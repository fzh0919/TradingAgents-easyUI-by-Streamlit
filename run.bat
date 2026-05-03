@echo off
cd /d "%~dp0"
start http://localhost:8501
start /min "" D:\Python\python.exe -m streamlit run "%~dp0app.py" --server.enableCORS=false --server.enableXsrfProtection=false --browser.gatherUsageStats=false --server.headless=true
exit
