@echo off
title Laura-bot Flask Web Application
echo.
echo ================================================
echo 🤖 LAURA-BOT WEB APPLICATION
echo ================================================
echo.
echo Starting Laura-bot server...
echo.

cd /d "C:\Users\Admin\Documents\Laura-bot"

echo Checking Python...
python --version
echo.

echo Starting Flask server...
echo URL: http://localhost:5555
echo.
echo ✨ Laura-bot will open in your browser!
echo 🛑 Press Ctrl+C to stop the server
echo.

REM Try to start the server
C:\Users\Admin\Documents\Laura-bot\.venv\Scripts\python.exe quick_start.py

echo.
echo Server stopped.
pause