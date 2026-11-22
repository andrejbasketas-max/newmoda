@echo off
setlocal
cd /d "%~dp0"
title GLAVONJA AI STUDIO
if not exist ".venv\Scripts\python.exe" (
  echo GLAVONJA AI STUDIO is not installed yet. Double-click install.bat first.
  pause
  exit /b 1
)
echo Starting GLAVONJA AI STUDIO ... the dashboard opens in your browser.
echo Keep this window open while you work. Close it to stop the studio.
".venv\Scripts\python.exe" glavonja.py dashboard
if errorlevel 1 pause
