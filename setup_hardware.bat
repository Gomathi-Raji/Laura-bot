@echo off
echo ========================================
echo        LAURA-BOT HARDWARE SETUP
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Check if hardware directory exists
if not exist "hardware" (
    echo ERROR: Hardware directory not found
    echo Please run this script from the Laura-bot root directory
    pause
    exit /b 1
)

echo Checking hardware setup...
echo.

REM Install hardware requirements
echo Installing hardware dependencies...
pip install -r hardware_requirements.txt
echo.

REM Run hardware setup
echo Running hardware configuration...
python hardware\setup_hardware.py

echo.
echo ========================================
echo Hardware setup complete!
echo.
echo Next steps:
echo 1. Run 'python laura_bot_server.py' to start the server
echo 2. Open http://localhost:5555/hardware to control your robot
echo 3. Check the hardware status on the dashboard
echo ========================================

pause