@echo off
setlocal EnableExtensions EnableDelayedExpansion

:: ============================================================================
::  IntelliSales - One-Click Launcher
::
::  - Activates the "intellisales" conda environment
::  - Starts the FastAPI app (app.main:app) with uvicorn --reload
::  - Keeps the server running in its own terminal window
::  - Waits for the server to start, then opens the dashboard in Chrome
:: ============================================================================

:: Use the folder containing this .bat file as the project root, so the
:: launcher works correctly no matter where it is double-clicked from.
set "PROJECT_DIR=%~dp0"
if "%PROJECT_DIR:~-1%"=="\" set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

set "CONDA_ENV_NAME=intellisales"
set "APP_URL=http://127.0.0.1:8000"

echo ============================================================
echo   IntelliSales Launcher
echo ============================================================
echo Project directory : %PROJECT_DIR%
echo Conda environment  : %CONDA_ENV_NAME%
echo.

:: ----------------------------------------------------------------------
:: Locate the Conda installation (checks common install locations first,
:: then falls back to whatever "conda" is found on PATH).
:: ----------------------------------------------------------------------
set "CONDA_ROOT="

if exist "%USERPROFILE%\anaconda3\Scripts\conda.exe" set "CONDA_ROOT=%USERPROFILE%\anaconda3"
if not defined CONDA_ROOT if exist "%USERPROFILE%\miniconda3\Scripts\conda.exe" set "CONDA_ROOT=%USERPROFILE%\miniconda3"
if not defined CONDA_ROOT if exist "%LOCALAPPDATA%\anaconda3\Scripts\conda.exe" set "CONDA_ROOT=%LOCALAPPDATA%\anaconda3"
if not defined CONDA_ROOT if exist "C:\ProgramData\anaconda3\Scripts\conda.exe" set "CONDA_ROOT=C:\ProgramData\anaconda3"
if not defined CONDA_ROOT if exist "C:\ProgramData\miniconda3\Scripts\conda.exe" set "CONDA_ROOT=C:\ProgramData\miniconda3"

if not defined CONDA_ROOT (
    for /f "delims=" %%I in ('where conda 2^>nul') do if not defined CONDA_ROOT for %%J in ("%%~dpI..") do set "CONDA_ROOT=%%~fJ"
)

if not defined CONDA_ROOT (
    echo [ERROR] Could not locate a Conda/Anaconda installation on this machine.
    echo Please make sure Anaconda or Miniconda is installed, then try again.
    pause
    exit /b 1
)

if not exist "%CONDA_ROOT%\Scripts\activate.bat" (
    echo [ERROR] Conda was found at "%CONDA_ROOT%" but activate.bat is missing there.
    pause
    exit /b 1
)

echo Conda root found at: %CONDA_ROOT%
echo.

:: ----------------------------------------------------------------------
:: Build a small helper script for the server window. Generating a real
:: .bat file (instead of an inline "cmd /k ..." one-liner) avoids the
:: quoting/escaping problems that come from mixing quoted paths with
:: "&&" chains directly on the command line.
:: ----------------------------------------------------------------------
set "SERVER_SCRIPT=%TEMP%\intellisales_server_%RANDOM%.bat"

(
    echo @echo off
    echo cd /d "%PROJECT_DIR%"
    echo call "%CONDA_ROOT%\Scripts\activate.bat" %CONDA_ENV_NAME%
    echo echo Starting IntelliSales FastAPI server ^(app.main:app^)...
    echo python -m uvicorn app.main:app --reload
    echo echo.
    echo echo Server stopped. Press any key to close this window.
    echo pause ^>nul
) > "%SERVER_SCRIPT%"

echo Launching the IntelliSales server in its own window...
start "IntelliSales Server" cmd /k "%SERVER_SCRIPT%"

:: ----------------------------------------------------------------------
:: Give the server a few seconds to start before opening the browser.
:: ----------------------------------------------------------------------
echo Waiting for the server to start...
timeout /t 6 /nobreak > nul

:: ----------------------------------------------------------------------
:: Open the dashboard in Google Chrome (falls back to the default browser
:: if Chrome cannot be found).
:: ----------------------------------------------------------------------
set "CHROME_PATH="
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set "CHROME_PATH=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if not defined CHROME_PATH if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set "CHROME_PATH=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
if not defined CHROME_PATH if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" set "CHROME_PATH=%LocalAppData%\Google\Chrome\Application\chrome.exe"

if defined CHROME_PATH (
    echo Opening %APP_URL% in Google Chrome...
    start "" "%CHROME_PATH%" "%APP_URL%"
) else (
    echo [WARNING] Google Chrome was not found in the usual install locations.
    echo Opening %APP_URL% in the default browser instead...
    start "" "%APP_URL%"
)

echo.
echo ============================================================
echo IntelliSales is starting up.
echo Keep the "IntelliSales Server" window open while you use the
echo app - closing it will stop the server.
echo ============================================================

endlocal
exit /b 0
