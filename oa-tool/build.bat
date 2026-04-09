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

echo [1/5] Checking files...
if not exist "%PYTHON%" (
    echo ERROR: .venv\Scripts\python.exe not found >> "%LOG%"
    echo ERROR: .venv not found. Run: python3.12 -m venv .venv
    pause & exit /b 1
)
echo       OK

echo [2/5] Cleaning old build...
if exist "%ROOT%dist\OASIS" (
    taskkill /f /im OASIS.exe >nul 2>&1
    timeout /t 1 /nobreak >nul
    rmdir /s /q "%ROOT%dist\OASIS"
    if exist "%ROOT%dist\OASIS" (
        echo WARNING: dist\OASIS could not be fully removed - retrying...
        timeout /t 2 /nobreak >nul
        rmdir /s /q "%ROOT%dist\OASIS"
    )
)
if exist "%ROOT%build\OASIS" rmdir /s /q "%ROOT%build\OASIS"
echo       Done

echo [3/5] Running PyInstaller... (5-10 minutes, please wait)
echo.

"%PYINSTALLER%" --clean --noconfirm --name OASIS --noconsole --add-data "%ROOT%web\static;web/static" --add-data "%ROOT%prompts;prompts" --add-data "%ROOT%config.yaml;." --hidden-import anthropic --hidden-import openai --hidden-import google.generativeai --hidden-import multipart --hidden-import uvicorn.logging --hidden-import uvicorn.loops --hidden-import uvicorn.loops.auto --hidden-import uvicorn.protocols --hidden-import uvicorn.protocols.http --hidden-import uvicorn.protocols.http.auto --hidden-import uvicorn.lifespan --hidden-import uvicorn.lifespan.on --hidden-import web.app --hidden-import oa_parser --hidden-import session --hidden-import llm_client --hidden-import report_generator --hidden-import sample_manager --hidden-import handlers --hidden-import handlers.prior_art_handler --hidden-import handlers.clarity_handler --hidden-import handlers.unity_handler --hidden-import handlers.default_handler --hidden-import handlers.base_handler --hidden-import fitz --hidden-import fitz._fitz --collect-binaries pymupdf --collect-all winrt "%ROOT%launcher.py"

if not exist "%ROOT%dist\OASIS\OASIS.exe" (
    echo.
    echo ========================================
    echo  FAILED - PyInstaller did not produce exe
    echo ========================================
    pause & exit /b 1
)

echo.
echo [4/5] Copying data files to _internal\ ...
set INTERNAL=%ROOT%dist\OASIS\_internal

if not exist "%INTERNAL%\web\static" mkdir "%INTERNAL%\web\static"
copy /y "%ROOT%web\static\*" "%INTERNAL%\web\static\" >> "%LOG%" 2>&1

if not exist "%INTERNAL%\prompts" mkdir "%INTERNAL%\prompts"
copy /y "%ROOT%prompts\*" "%INTERNAL%\prompts\" >> "%LOG%" 2>&1

copy /y "%ROOT%config.yaml" "%INTERNAL%\" >> "%LOG%" 2>&1

echo       Done

echo [5/5] Checking result...
echo       Build completed: %date% %time% >> "%LOG%"
echo       web\static contents: >> "%LOG%"
dir "%INTERNAL%\web\static" >> "%LOG%" 2>&1
echo       prompts contents: >> "%LOG%"
dir "%INTERNAL%\prompts" >> "%LOG%" 2>&1

if exist "%INTERNAL%\web\static\index.html" (
    echo.
    echo ========================================
    echo  SUCCESS: dist\OASIS\OASIS.exe
    echo ========================================
    echo  Log saved to: build_log.txt
) else (
    echo.
    echo ========================================
    echo  WARNING: exe built but web\static\index.html missing!
    echo  Check build_log.txt
    echo ========================================
)

echo.
pause
