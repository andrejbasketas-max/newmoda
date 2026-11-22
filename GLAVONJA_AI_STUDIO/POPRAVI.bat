@echo off
setlocal
cd /d "%~dp0"
title GLAVONJA AI STUDIO - popravka
echo Popravka: instaliram pakete koji fale. Sacekaj 1-3 minuta...
echo.
if not exist ".venv\Scripts\python.exe" (
  echo Nema .venv - pokreni prvo install.bat
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
".venv\Scripts\python.exe" -c "import PIL, numpy, espeakng_loader; print('OK - svi paketi rade')"
if errorlevel 1 (
  echo.
  echo GRESKA - slikaj ovaj prozor ^(Windows+Shift+S^) i posalji ga.
  pause
  exit /b 1
)
echo.
echo Gotovo. Sada pokrecem studio...
call "%~dp0start.bat"
