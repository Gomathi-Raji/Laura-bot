@echo off
echo ============================================================
echo                    LAURA-BOT STARTUP
echo              Hardware-Ready Educational Assistant
echo ============================================================
echo.

REM Store start time
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set starttime=%datetime:~8,2%:%datetime:~10,2%:%datetime:~12,2%

echo [%starttime%] Starting Laura-bot with hardware integration...
echo.

REM Check Python installation
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo        Please install Python 3.8+ from https://python.org
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VER=%%i
echo [OK] %PYTHON_VER% found
echo.

REM Check if we're in the correct directory
if not exist "laura_bot_server.py" (
    echo [ERROR] laura_bot_server.py not found
    echo        Please run this script from the Laura-bot directory
    echo.
    pause
    exit /b 1
)

echo [INFO] Checking required files...
if exist "laura_bot_server.py" echo [OK] Flask server found
if exist "templates\" echo [OK] Templates directory found
if exist "static\" echo [OK] Static files directory found
if exist "hardware\" echo [OK] Hardware directory found
echo.

REM Check and install basic requirements
echo [INFO] Checking basic requirements...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [WARN] Flask not found, installing basic requirements...
    pip install flask flask-socketio
    echo.
)

REM Check hardware requirements
echo [INFO] Checking hardware integration...
if exist "hardware_requirements.txt" (
    echo [INFO] Hardware requirements file found
    
    REM Ask user if they want hardware features
    set /p ENABLE_HW="Enable hardware features? (y/n) [y]: "
    if "%ENABLE_HW%"=="" set ENABLE_HW=y
    
    if /i "%ENABLE_HW%"=="y" (
        echo [INFO] Installing hardware dependencies...
        pip install -r hardware_requirements.txt
        echo.
        
        echo [INFO] Running hardware detection...
        python -c "
import sys
import os
sys.path.append('hardware')
try:
    from real_hardware_controller import get_hardware_controller
    controller = get_hardware_controller()
    print('[OK] Hardware controller initialized')
    if controller.is_connected:
        print('[OK] Hardware components detected')
    else:
        print('[WARN] No hardware connected - simulation mode enabled')
except Exception as e:
    print(f'[WARN] Hardware initialization failed: {e}')
    print('[INFO] Running in simulation mode')
" 2>nul
        echo.
    ) else (
        echo [INFO] Hardware features disabled by user
        echo.
    )
) else (
    echo [WARN] Hardware requirements file not found
    echo [INFO] Hardware features will be simulated
    echo.
)

REM Display startup information
echo ============================================================
echo                     STARTUP INFORMATION
echo ============================================================
echo.
echo Server Configuration:
echo   - URL: http://localhost:5555
echo   - Environment: Development
echo   - Debug Mode: Enabled
echo.
echo Available Features:
echo   [Dashboard]  http://localhost:5555/
echo   [Learning]   http://localhost:5555/learn
echo   [Quiz]       http://localhost:5555/quiz
echo   [Progress]   http://localhost:5555/progress
echo   [Hardware]   http://localhost:5555/hardware
echo.
echo Hardware Status:
if /i "%ENABLE_HW%"=="y" (
    echo   [Real Hardware] Connection will be attempted
    echo   [Simulation]   Fallback mode available
) else (
    echo   [Simulation]   Hardware features simulated
    echo   [Real Hardware] Disabled
)
echo.
echo Controls:
echo   - Press Ctrl+C to stop the server
echo   - Server will auto-open in browser
echo   - Hardware control available via web interface
echo.
echo ============================================================
echo.

REM Start the server
echo [INFO] Starting Laura-bot Flask server...
echo.

REM Set environment variables
set FLASK_ENV=development
set PYTHONPATH=%CD%

REM Start the server with error handling
python laura_bot_server.py
set SERVER_EXIT_CODE=%ERRORLEVEL%

echo.
echo ============================================================

if %SERVER_EXIT_CODE% EQU 0 (
    echo [INFO] Laura-bot server stopped normally
) else (
    echo [ERROR] Laura-bot server stopped with error code: %SERVER_EXIT_CODE%
    echo.
    echo Common solutions:
    echo   - Check if port 5555 is already in use
    echo   - Verify all dependencies are installed
    echo   - Check for Python errors in the output above
    echo   - Try running: pip install -r requirements.txt
)

echo.
echo Thank you for using Laura-bot! 🤖
echo ============================================================

pause