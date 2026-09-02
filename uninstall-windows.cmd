@echo off
setlocal
cd /d "%~dp0"
echo MZP351HV00TR SD-card uninstaller
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0uninstall-offline.ps1" %*
if errorlevel 1 (
  echo.
  echo Uninstall failed. Review the message above.
) else (
  echo.
  echo Uninstall finished. Safely eject the SD card.
)
echo.
pause
