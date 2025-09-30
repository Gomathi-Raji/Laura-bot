@echo off
title Laura-bot IoT Simulation Launcher

echo ========================================
echo    🤖 Laura-bot IoT Simulation
echo ========================================
echo.
echo Starting IoT simulation environment...
echo.

REM Change to project directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Install simulation requirements if needed
if exist "simulation\requirements.txt" (
    echo 📦 Installing simulation dependencies...
    pip install -r simulation\requirements.txt
    echo.
)

REM Launch the IoT simulation launcher
echo 🚀 Launching IoT Simulation Launcher...
python simulation\launcher.py

pause