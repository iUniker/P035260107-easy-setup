@echo off
setlocal
cd /d "%~dp0"
echo MZP351HV00TR SD-card installer
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-offline.ps1" %*
if errorlevel 1 (
  echo.
  echo Installation failed. No display configuration was applied.
) else (
  echo.
  echo Installation finished. Safely eject the SD card.
)
echo.
pause
