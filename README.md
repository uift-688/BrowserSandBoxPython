# Pyodide-in-Chrome Python Runner

This project allows you to run Pyodide inside Chrome and control it via Selenium, effectively creating a remotely controllable Python interpreter in the browser.

## Overview

- Uses **Pyodide** to execute Python code within the browser (Chrome).
- Controlled via **Selenium WebDriver**.
- Designed to act as a headless or interactive Python interpreter through browser automation.
- Ideal for automation, testing, scripting, or remote execution of Python code.

## Usage

1. **Download and run the `runtime.exe` file** to launch a Pyodide-enabled browser window.
2. **Wait for the browser to fully load** — please note that this may take a few moments as the browser needs to initialize Pyodide.
3. **Control the Pyodide instance using Selenium** to send Python code and receive results.

The browser window will act as a Python interpreter that can be controlled programmatically through Selenium.

## License

This project uses a dual license model:

- The **source code** is licensed under the [Apache License 2.0](./LICENSE).
- The **compiled binary (`.exe`) builds** are distributed under the [GNU General Public License v3](./LICENSE-GPLv3.txt).

You are free to reuse, modify, and distribute the source code under the terms of Apache 2.0.  
If you use or redistribute the `.exe` binaries provided in releases, you must comply with the GPLv3 license.

