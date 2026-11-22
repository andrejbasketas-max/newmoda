@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title GLAVONJA AI STUDIO - Update
echo Updating GLAVONJA AI STUDIO safely.
echo Your projects, outputs, settings, style, references and database are NOT touched.
if not exist ".venv\Scripts\python.exe" ( echo Run install.bat first. & pause & exit /b 1 )
set "VPY=%~dp0.venv\Scripts\python.exe"
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmmss"') do set "STAMP=%%I"
set "BK=backups\%STAMP%"
echo [1/4] Backup to %BK% ...
mkdir "%BK%" 2>nul
if exist config\settings.json copy /y config\settings.json "%BK%\" >nul
if exist config\style.json copy /y config\style.json "%BK%\" >nul
if exist database\glavonja.db copy /y database\glavonja.db "%BK%\" >nul
if exist database\asset_license.json copy /y database\asset_license.json "%BK%\" >nul
echo [2/4] Getting the new version ...
where git >nul 2>nul
if errorlevel 1 (
  echo   git not found - if you downloaded a ZIP, extract the new version over this folder
  echo   ^(your data folders are kept^), then run update.bat again.
) else (
  git pull --ff-only || echo   git pull failed - your files were not changed.
)
echo [3/4] Updating packages ...
"%VPY%" -m pip install --disable-pip-version-check -q -r requirements.txt
"%VPY%" -m pip install --disable-pip-version-check -q -r requirements-optional.txt >nul 2>nul
echo [4/4] Self-test ...
"%VPY%" glavonja.py selftest
pause
