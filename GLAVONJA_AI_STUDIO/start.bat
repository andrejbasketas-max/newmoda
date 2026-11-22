@echo off
setlocal
cd /d "%~dp0"
title GLAVONJA AI STUDIO
if not exist ".venv\Scripts\python.exe" (
  echo GLAVONJA AI STUDIO is not installed yet. Double-click install.bat first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -c "import PIL, numpy, espeakng_loader" >nul 2>nul
if errorlevel 1 (
  echo Some packages are missing - installing them now, please wait 1-3 minutes ...
  ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
  ".venv\Scripts\python.exe" -c "import PIL, numpy, espeakng_loader" >nul 2>nul
  if errorlevel 1 (
    echo.
    echo ERROR: packages could not be installed. Take a screenshot of this window and send it.
    pause
    exit /b 1
  )
)
echo Starting GLAVONJA AI STUDIO ... the dashboard opens in your browser.
echo Keep this window open while you work. Close it to stop the studio.
".venv\Scripts\python.exe" glavonja.py dashboard
if errorlevel 1 pause
