@echo off
REM Lexpresso Server Startup Script
REM This script starts the Lexpresso server on port 80

echo ====================================
echo Starting Lexpresso Server...
echo ====================================
echo.

REM Change to the script's directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.6 or higher
    pause
    exit /b 1
)

REM Start the server
echo Starting server on port 80...
echo Press Ctrl+C to stop the server
echo.
python server.py

REM If server stops, pause so we can see any error messages
pause
