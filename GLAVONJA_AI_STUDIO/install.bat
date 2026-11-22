@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title GLAVONJA AI STUDIO - Install
echo ============================================================
echo   GLAVONJA AI STUDIO - installation (no admin rights needed)
echo ============================================================
echo.
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
  echo   Python 3.12 64-bit was not found.
  echo   Install it for free from https://www.python.org/downloads/windows/
  echo   ^(tick "Add python.exe to PATH"^), then double-click install.bat again.
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
"%VPY%" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 ( echo   ERROR: package installation failed - check your internet connection. & pause & exit /b 1 )
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
echo ============================================================
echo   Done. Start the studio with start.bat
echo   Next: open Settings and paste your Gemini API key,
echo         open Style and upload screenshots of your channel.
echo ============================================================
pause
