@echo off
echo Running API tests...
echo.

REM Check if Python is available
python --version 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements-test.txt

echo.
echo Starting tests...
python test_api.py

echo.
echo Test completed!
pause