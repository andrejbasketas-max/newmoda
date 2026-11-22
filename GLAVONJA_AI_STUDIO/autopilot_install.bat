@echo off
setlocal
cd /d "%~dp0"
title GLAVONJA AI STUDIO - Autopilot setup
if not exist ".venv\Scripts\pythonw.exe" ( echo Run install.bat first. & pause & exit /b 1 )
echo Registers two Windows scheduled tasks for YOUR user (no admin rights, no Claude usage):
echo   1) "GLAVONJA Autopilot"  - every 30 minutes: daily ideas, FLOW_INBOX import, resume, notifications
echo   2) "GLAVONJA Studio"     - opens the studio dashboard when you log in to Windows
echo.
set "PYW=%~dp0.venv\Scripts\pythonw.exe"
set "APP=%~dp0glavonja.py"
schtasks /Create /F /SC MINUTE /MO 30 /TN "GLAVONJA Autopilot" /TR "\"%PYW%\" \"%APP%\" autopilot"
if errorlevel 1 ( echo ERROR creating the autopilot task. & pause & exit /b 1 )
schtasks /Create /F /SC ONLOGON /TN "GLAVONJA Studio" /TR "\"%PYW%\" \"%APP%\" dashboard"
if errorlevel 1 echo Could not create the logon task (optional) - use start.bat instead.
echo.
echo Done. Remove it any time with autopilot_uninstall.bat
pause
