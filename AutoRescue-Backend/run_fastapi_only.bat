@echo off
REM AutoRescue AI - Run FastAPI Backend Only
REM Useful for testing API without running all agents

setlocal enabledelayedexpansion

echo.
echo ====================================================================
echo   AutoRescue AI - FastAPI Backend Only
echo ====================================================================
echo.

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

if not exist ".env" (
    echo [ERROR] .env file not found
    pause
    exit /b 1
)

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed
    pause
    exit /b 1
)

cls
echo [INFO] Starting FastAPI backend server...
echo.

REM Run FastAPI
echo Starting FastAPI on http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo.
python main.py

pause
