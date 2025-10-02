@echo off
echo ============================================
echo Archaeological Rover Simulation - Setup
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Python is not installed.
    echo.
    echo Please install Python 3.8 or later from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo + Found Python %PYTHON_VERSION%

REM Check if version is 3.8 or later (simplified check)
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo X Python 3.8 or later is required.
    echo Please upgrade Python from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo.
echo Creating virtual environment...
python -m venv rover_env

if %errorlevel% neq 0 (
    echo X Failed to create virtual environment.
    echo Please make sure Python is properly installed.
    echo.
    pause
    exit /b 1
)

echo + Virtual environment created
echo.
echo Activating virtual environment...

REM Activate virtual environment
call rover_env\Scripts\activate.bat

if %errorlevel% neq 0 (
    echo X Failed to activate virtual environment.
    echo.
    pause
    exit /b 1
)

echo + Virtual environment activated
echo.
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo X Failed to install dependencies.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo + Setup complete!
echo ============================================
echo.
echo To run the game:
echo   1. Activate the virtual environment:
echo      rover_env\Scripts\activate
echo.
echo   2. Run the game:
echo      python main.py
echo.
echo To deactivate the virtual environment later:
echo      deactivate
echo.
pause
