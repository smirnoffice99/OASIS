@echo off
echo OASIS Web App Starting...
echo.
echo Open browser: http://localhost:8000
echo Press Ctrl+C to stop
echo.
cd /d %~dp0
.venv\Scripts\python.exe -m uvicorn web.app:app --reload --port 8000
