@echo off
echo Starting Laura-bot Personal Learning Assistant...

REM Disable Streamlit telemetry and analytics
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
set STREAMLIT_GLOBAL_DEVELOPMENT_MODE=false
set STREAMLIT_CLIENT_TOOLBAR_MODE=minimal
set STREAMLIT_SERVER_ENABLE_CORS=false
set STREAMLIT_SERVER_ENABLE_WEBSOCKET_COMPRESSION=false

REM Set working directory
cd /d "C:\Users\Admin\Documents\Laura-bot"

REM Start the application
echo Launching Streamlit application...
python -m streamlit run app_ui.py --server.port 8505 --server.headless true --browser.gatherUsageStats false

pause