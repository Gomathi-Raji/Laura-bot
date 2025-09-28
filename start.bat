@echo off
echo ====================================================
echo        ZARA VOICE ASSISTANT - SETUP & RUN
echo ====================================================

echo.
echo 🔧 Installing/Upgrading dependencies...
pip install -r requirements.txt
pip install googletrans

echo.
echo ✅ Dependencies installed successfully!

echo.
echo 🚀 Starting Zara Voice Assistant Launcher...
python launcher.py

echo.
echo 👋 Thanks for using Zara Voice Assistant!
pause
