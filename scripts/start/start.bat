@echo off
REM Auto-setup script for Audio Streaming Control Panel (Windows)
REM Handles venv creation, activation, and dependency installation automatically

setlocal enabledelayedexpansion

echo ==================================================
echo    Audio Streaming Control Panel - Auto Setup
echo ==================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3 and try again.
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Step 1: Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo [SETUP] Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
    echo.
) else (
    echo [OK] Virtual environment already exists
    echo.
)

REM Step 2: Activate virtual environment
echo [SETUP] Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Step 3: Check and install dependencies
echo [SETUP] Checking dependencies...

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found!
    echo Creating requirements.txt with necessary packages...
    (
        echo flask==3.0.0
        echo sounddevice==0.4.6
        echo websockets==12.0
        echo psutil==5.9.6
    ) > requirements.txt
    echo [OK] requirements.txt created
)

REM Check if packages are installed
set NEEDS_INSTALL=0

python -c "import flask" 2>nul || set NEEDS_INSTALL=1
python -c "import sounddevice" 2>nul || set NEEDS_INSTALL=1
python -c "import websockets" 2>nul || set NEEDS_INSTALL=1
python -c "import psutil" 2>nul || set NEEDS_INSTALL=1

if !NEEDS_INSTALL!==1 (
    echo [SETUP] Installing dependencies...
    python -m pip install --upgrade pip >nul 2>&1
    pip install -r requirements.txt
    echo [OK] Dependencies installed
) else (
    echo [OK] All dependencies already installed
)

echo.
echo ==================================================
echo    Starting Control Panel...
echo ==================================================
echo.

REM Step 4: Run launcher.py from src directory
python src\launcher.py

REM Deactivate venv when launcher exits
call venv\Scripts\deactivate.bat