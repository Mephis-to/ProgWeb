@echo off
setlocal

cd /d "%~dp0"
call environment.bat

set "PYTHON_BIN=%Directory_PythonEnv%\Scripts\python.exe"

if not exist "%PYTHON_BIN%" (
    echo Python environment not found at %Directory_PythonEnv%.
    echo Run setup-Env.bat first.
    pause
    exit /b 1
)

start "" "%PYTHON_BIN%" -m flask --app Server run --port %Port% --host=127.0.0.1

timeout 3

start http://localhost:%Port%/
