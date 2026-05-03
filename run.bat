@echo off
cd /d "%~dp0"

:: Check if streamlit is available in the current Python environment
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo =======================================================
    echo [ERROR] Streamlit is not installed or not found.
    echo.
    echo If you are using a virtual environment (like Conda or venv),
    echo please make sure you run this script from an activated terminal:
    echo    conda activate tradingagents
    echo    run.bat
    echo =======================================================
    pause
    exit /b 1
)

start http://localhost:8501
start /min "" python -m streamlit run "%~dp0app.py" --server.enableCORS=false --server.enableXsrfProtection=false --browser.gatherUsageStats=false --server.headless=true
exit
