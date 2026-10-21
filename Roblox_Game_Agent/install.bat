@echo off
setlocal
cd /d "%~dp0"
py -3 -m pip install --upgrade pip
py -3 -m pip install -r requirements.txt
if errorlevel 1 (
  echo Install failed. Make sure Python 3.10+ is installed and added to PATH.
  pause
  exit /b 1
)
echo Install complete. Double-click run.bat to start.
pause
