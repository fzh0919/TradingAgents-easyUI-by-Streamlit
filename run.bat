@echo off
cd /d "%~dp0"
start http://localhost:8501
start /min "" py -3 -m streamlit run "%~dp0app.py" --server.enableCORS=false --server.enableXsrfProtection=false --browser.gatherUsageStats=false --server.headless=true
exit
