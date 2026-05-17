@echo off
:: FXION-ONYX Q8 Augmented Boot — Windows Startup Launcher
title FXION-ONYX Q8 Boot
cd /d "C:\Users\Cristan\OneDrive\Desktop\FXION-ONYX-FINAL"

:: Try python from PATH, then common install locations
where python >nul 2>&1
if %errorlevel%==0 (
    python launch.py q8
) else if exist "C:\Python310\python.exe" (
    "C:\Python310\python.exe" launch.py q8
) else if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" launch.py q8
) else (
    echo [ERROR] Python not found. Install Python 3.10+ and add to PATH.
)

echo.
echo [FXION-ONYX] Boot complete. This window will close in 5 seconds.
timeout /t 5 >nul
