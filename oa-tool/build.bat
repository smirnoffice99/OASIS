@echo off
set ROOT=%~dp0
set LOG=%ROOT%build_log.txt
set PYTHON=%ROOT%.venv\Scripts\python.exe
set PYINSTALLER=%ROOT%.venv\Scripts\pyinstaller.exe

echo Build started: %date% %time% > "%LOG%"

echo ========================================
echo  OASIS Build
echo ========================================
echo.

echo [1/4] Checking files...
if not exist "%PYTHON%" (
    echo ERROR: .venv\Scripts\python.exe not found >> "%LOG%"
    echo ERROR: .venv not found. Run: python3.12 -m venv .venv
    pause & exit /b 1
)
echo       OK

echo [2/4] Cleaning old build...
if exist "%ROOT%dist\OASIS" rmdir /s /q "%ROOT%dist\OASIS"
if exist "%ROOT%build\OASIS" rmdir /s /q "%ROOT%build\OASIS"
echo       Done

echo [3/4] Running PyInstaller... (5-10 minutes, please wait)
echo.

"%PYINSTALLER%" --clean --noconfirm --name OASIS --noconsole --add-data "%ROOT%web\static;web/static" --add-data "%ROOT%prompts;prompts" --add-data "%ROOT%config.yaml;." --hidden-import anthropic --hidden-import openai --hidden-import google.generativeai --hidden-import multipart --hidden-import uvicorn.logging --hidden-import uvicorn.loops --hidden-import uvicorn.loops.auto --hidden-import uvicorn.protocols --hidden-import uvicorn.protocols.http --hidden-import uvicorn.protocols.http.auto --hidden-import uvicorn.lifespan --hidden-import uvicorn.lifespan.on --hidden-import web.app --hidden-import oa_parser --hidden-import session --hidden-import llm_client --hidden-import report_generator --hidden-import sample_manager --hidden-import handlers --hidden-import handlers.prior_art_handler --hidden-import handlers.clarity_handler --hidden-import handlers.unity_handler --hidden-import handlers.default_handler --hidden-import handlers.base_handler --hidden-import fitz --hidden-import fitz._fitz --collect-binaries pymupdf "%ROOT%launcher.py"

echo.
echo [4/4] Checking result...

if exist "%ROOT%dist\OASIS\OASIS.exe" (
    echo       web\static included: >> "%LOG%"
    dir "%ROOT%dist\OASIS\_internal\web\static" >> "%LOG%" 2>&1
    echo.
    echo ========================================
    echo  SUCCESS: dist\OASIS\OASIS.exe
    echo ========================================
    echo  Log saved to: build_log.txt
) else (
    echo.
    echo ========================================
    echo  FAILED - See build_log.txt for details
    echo ========================================
    echo.
    echo Last 20 lines of log:
    powershell -command "Get-Content '%LOG%' | Select-Object -Last 20"
)

echo.
pause
