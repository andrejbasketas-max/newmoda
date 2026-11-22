@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title GLAVONJA AI STUDIO - Install
echo ============================================================
echo   GLAVONJA AI STUDIO - installation (no admin rights needed)
echo ============================================================
echo.
echo GLAVONJA install %DATE% %TIME% > install_log.txt
echo [1/9] Checking Windows...
ver | find "10." >nul || ver | find "11." >nul || echo   WARNING: tested for Windows 10/11 only.
ver

echo [2/9] Looking for Python 3.10-3.13 (64-bit)...
set "PY="
for %%V in (3.12 3.13 3.11 3.10) do (
  if not defined PY (
    py -%%V -c "import sys; assert sys.maxsize > 2**32" >nul 2>nul && set "PY=py -%%V"
  )
)
if not defined PY (
  python -c "import sys; assert (3,10) <= sys.version_info[:2] <= (3,13) and sys.maxsize > 2**32" >nul 2>nul && set "PY=python"
)
if not defined PY (
  echo.
  echo   Python 3.12 is NOT installed. It is free and needed by the studio.
  set /p PYI="  Install Python 3.12 automatically now? [Y/n] "
  if /i not "!PYI!"=="n" (
    where winget >nul 2>nul && (
      winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
    ) || (
      echo   Automatic install is not available on this PC.
    )
  )
  if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY="%LOCALAPPDATA%\Programs\Python\Python312\python.exe""
)
if not defined PY (
  echo.
  echo   Please install Python 3.12 from the page that opens now:
  echo   choose "Windows installer (64-bit)", tick "Add python.exe to PATH", click Install Now.
  echo   Then double-click install.bat again.
  start "" "https://www.python.org/downloads/release/python-3129/"
  echo.
  pause
  exit /b 1
)
echo   using: %PY%

echo [3/9] Creating virtual environment .venv ...
if not exist ".venv\Scripts\python.exe" (
  %PY% -m venv .venv
  if errorlevel 1 ( echo   ERROR: could not create .venv & pause & exit /b 1 )
)
set "VPY=%~dp0.venv\Scripts\python.exe"

echo [4/9] Installing Python packages ...
"%VPY%" -m pip install --disable-pip-version-check -q --upgrade pip
echo   please wait 1-3 minutes ... (details in install_log.txt)
"%VPY%" -m pip install --disable-pip-version-check -r requirements.txt >> install_log.txt 2>&1
if errorlevel 1 (
  echo   ERROR: package installation failed. Last lines of install_log.txt:
  powershell -NoProfile -Command "Get-Content install_log.txt -Tail 15"
  pause
  exit /b 1
)
echo   optional Piper voice engine (better fallback voice):
"%VPY%" -m pip install --disable-pip-version-check -q -r requirements-optional.txt || echo   Piper not installed - espeak-ng fallback will be used.

echo [5/9] Inspecting hardware (saved to docs\hardware_report.json) ...
"%VPY%" scripts\install_helper.py hardware

echo [6/9] FFmpeg (free, downloaded into tools\ffmpeg) ...
"%VPY%" scripts\install_helper.py ffmpeg

echo [7/9] Optional Piper voice models (asks first, ~65 MB each) ...
"%VPY%" scripts\install_helper.py models

echo [8/9] Creating folders, database and reference library ...
"%VPY%" glavonja.py style test

echo [9/9] Self-test ...
"%VPY%" glavonja.py selftest
echo.
set /p AP="Turn on the daily AUTOPILOT (Windows Task Scheduler, no Claude usage)? [Y/n] "
if /i not "%AP%"=="n" call "%~dp0autopilot_install.bat"
echo ============================================================
echo   Done. Start the studio with start.bat
echo   Next: open Settings and paste your Gemini API key,
echo         open Style and upload screenshots of your channel.
echo ============================================================
pause
