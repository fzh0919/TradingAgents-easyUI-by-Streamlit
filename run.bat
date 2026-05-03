@echo off
cd /d "%~dp0"

:: Check if streamlit is available in the current Python environment
python -c "import streamlit" >nul 2>&1
if %errorlevel% equ 0 goto start_server

echo =======================================================
echo [WARNING] Streamlit and other dependencies are not found 
echo in your current Python environment.
echo =======================================================
set /p install_deps="Would you like to install the required dependencies now? [y/N]: "

if /i "%install_deps%" neq "y" (
    echo.
    echo Installation canceled. Exiting...
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
python -m pip install -e . python-dotenv
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Installation failed. Please check your Python and pip installation.
    pause
    exit /b 1
)
echo.
echo [SUCCESS] Dependencies installed successfully!
echo.

:start_server
echo Starting TradingAgents Streamlit Web UI...
start http://localhost:8501
start /min "" python -m streamlit run "%~dp0app.py" --server.enableCORS=false --server.enableXsrfProtection=false --browser.gatherUsageStats=false --server.headless=true
exit
