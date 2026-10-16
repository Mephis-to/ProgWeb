@echo off
echo off

call environment.bat

setlocal enableextensions enabledelayedexpansion

echo ReCreating Python environment...
python -m venv %Directory_PythonEnv%

echo Updating pip...
%Directory_PythonEnv%\Scripts\python.exe -m pip install --upgrade pip

echo Installing Python/Flask modules...
%Directory_PythonEnv%\Scripts\pip install Flask Flask-Session Flask-Mail

pause
