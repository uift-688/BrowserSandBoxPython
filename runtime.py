from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from code import InteractiveConsole
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import queue
import sys
import threading
import re
import base64

code = """<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Sandbox Runtime</title>
  <script src="https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js"></script>
</head>
<body>
  <script>
    let pyodide;

    async function main() {
      pyodide = await loadPyodide();
    }
  </script>
</body>
</html>
"""

# ChromeDriverのパスを指定してブラウザを起動
option = Options()
option.set_capability("goog:loggingPrefs", {"browser": "ALL"})
option.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)

print('Loading...')

driver.get(f"data:text/html;base64,{base64.b64encode(code.encode()).decode()}")

# JavaScriptでPyodideの準備を待つ処理（WASM環境に依存）
driver.execute_async_script("""
    var callback = arguments[arguments.length - 1];
    main().then(() => {
        callback('WASM initialized');
    }).catch(callback);
""")

class Console(InteractiveConsole):
    def runsource(self, source, filename="<input>", symbol="single"):
        # WASM環境でPythonコードを非同期実行するためのコード修正
        match = re.fullmatch(r"loadPackage\(\"(.*)\"\)", source)
        if match:
            package = match.group(1)
            script = f"""
        var callback = arguments[arguments.length - 1];
        pyodide.loadPackage("{package}").then(() => {{
            callback("Complete!");
        }}).catch(callback);
        """
            run_queue.put_nowait([driver.execute_async_script, script])
            result = response_queue.get() or ""
            if "__error_address" in result:
                print(result["type"])
                return
            elif result == "":
                return
            print(result)
            return
        script = f"""
        var callback = arguments[arguments.length - 1];
        pyodide.runPythonAsync(\"{source.replace('\"', '\\\"')}\").then((value) => {{
            callback(value);
        }}).catch(callback);
        """
        run_queue.put_nowait([driver.execute_async_script, script])
        result = response_queue.get() or ""
        if "__error_address" in dict(result):
            print(result["type"])
            return
        elif not result or result == "None" or result == "":
            return
        print(result)
    def input(self, prompt = ""):
        try:
            result = input(prompt)
            if result == "exit()":
                run_queue.put_nowait(KeyboardInterrupt)
                sys.exit(0)
            return result
        except EOFError:
            run_queue.put_nowait(KeyboardInterrupt)
            sys.exit(0)
        except KeyboardInterrupt:
            run_queue.put_nowait(KeyboardInterrupt)
            sys.exit(0)

try:
    console = Console()
    run_queue = queue.Queue()
    response_queue = queue.Queue()
    th = threading.Thread(target=console.interact, args=("Python WASM (Chrome/WASM) on chrome",))
    th.daemon = True
    th.start()
    while th.is_alive():
        try:
            script = run_queue.get(timeout=1)
            if script == KeyboardInterrupt:
                break
            result = script[0](*script[1:])
            for entry in driver.get_log("browser"):
                match = re.fullmatch(r"https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.asm.js\s\d+\:\d+\s\"(.*)\"", entry["message"])
                if match:
                    print(match.group(1))
            response_queue.put_nowait(result)
        except queue.Empty:
            for entry in driver.get_log("browser"):
                match = re.fullmatch(r"https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.asm.js\s\d+\:\d+\s\"(.*)\"", entry["message"])
                if match:
                    print(match.group(1))
finally:
    driver.quit()
