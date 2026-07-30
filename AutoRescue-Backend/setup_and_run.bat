@echo off
REM AutoRescue AI - Setup Dependencies and Run System

setlocal enabledelayedexpansion

echo.
echo ====================================================================
echo   AutoRescue AI - Dependency Setup and System Start
echo ====================================================================
echo.

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Set Python path
set PYTHONPATH=%SCRIPT_DIR%;%PYTHONPATH%

echo [INFO] Current Directory: %SCRIPT_DIR%
echo [INFO] Python Path: %PYTHONPATH%
echo.

REM Check Python installation
echo [STEP 1] Checking Python installation...
python --version
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)
echo [OK] Python found
echo.

REM Check .env file
echo [STEP 2] Checking configuration (.env)...
if not exist ".env" (
    echo [ERROR] .env file not found
    echo [INFO] Please ensure .env file exists in the current directory
    pause
    exit /b 1
)
echo [OK] .env file found
echo.

REM Install dependencies
echo [STEP 3] Installing/Upgrading dependencies...
echo [INFO] This may take 1-2 minutes on first run...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo [ERROR] Failed to upgrade pip
    pause
    exit /b 1
)
echo.

echo [INFO] Installing required packages from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo [WARNING] Some packages may have failed to install
    echo [INFO] Attempting to continue anyway...
)
echo [OK] Dependencies installed
echo.

REM Verify imports
echo [STEP 4] Verifying Python modules...
python -c "import fastapi; print('[OK] FastAPI')"
python -c "import uvicorn; print('[OK] Uvicorn')"
python -c "import uagents; print('[OK] uAgents')"
python -c "import dotenv; print('[OK] python-dotenv')"
python -c "import pydantic; print('[OK] Pydantic')"

echo.
echo ====================================================================
echo   Setup Complete - Starting System
echo ====================================================================
echo.

REM Start the system
echo [INFO] Launching AutoRescue AI services...
echo.

start "AutoRescue FastAPI Backend" cmd /k "cd /d "%SCRIPT_DIR%" && python main.py"
timeout /t 2 /nobreak

start "AutoRescue Orchestrator" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/orchestrator_uagent_phase9.py"
timeout /t 2 /nobreak

start "Telemetry Agent" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/telemetry_uagent.py"
timeout /t 1 /nobreak

start "Safety Agent" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/safety_uagent.py"
timeout /t 1 /nobreak

start "Maintenance Agent" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/maintenance_uagent.py"
timeout /t 1 /nobreak

start "Notification Agent" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/notification_uagent.py"
timeout /t 1 /nobreak

start "Explanation Agent" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/explanation_uagent.py"
timeout /t 1 /nobreak

start "Verification Agent" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/verification_uagent.py"
timeout /t 1 /nobreak

cls
echo.
echo ====================================================================
echo   AutoRescue AI System - Ready
echo ====================================================================
echo.
echo [SUCCESS] All services have been started!
echo.
echo Services Running:
echo   FastAPI Backend:        http://127.0.0.1:8000
echo   API Docs (Swagger):     http://127.0.0.1:8000/docs
echo   Orchestrator:           Port 8018
echo   Telemetry:              Port 8020
echo   Safety:                 Port 8021
echo   Maintenance:            Port 8022
echo   Notification:           Port 8023
echo   Explanation:            Port 8024
echo   Verification:           Port 8025
echo.
echo Quick Test:
echo   curl http://127.0.0.1:8000/health
echo.
echo ====================================================================
echo.

pause
