@echo off
REM AutoRescue AI - Run Only Orchestrator and Core Agents
REM Minimal setup for development and testing

setlocal enabledelayedexpansion

echo.
echo ====================================================================
echo   AutoRescue AI - Orchestrator + Core Agents (Dev Mode)
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
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

cls
echo [INFO] Starting minimal AutoRescue configuration...
echo.

REM FastAPI Backend
echo Starting FastAPI Backend (port 8000)...
start "AutoRescue FastAPI Backend" cmd /k "python main.py"
timeout /t 2 /nobreak

REM Orchestrator
echo Starting Orchestrator (port 8018)...
start "AutoRescue Orchestrator" cmd /k "python agents/orchestrator_uagent_phase9.py"
timeout /t 2 /nobreak

REM Phase 9 Specialist Agents
echo Starting Telemetry Agent (port 8020)...
start "Telemetry Agent" cmd /k "python agents/telemetry_uagent.py"
timeout /t 1 /nobreak

echo Starting Safety Agent (port 8021)...
start "Safety Agent" cmd /k "python agents/safety_uagent.py"
timeout /t 1 /nobreak

echo Starting Maintenance Agent (port 8022)...
start "Maintenance Agent" cmd /k "python agents/maintenance_uagent.py"
timeout /t 1 /nobreak

echo Starting Notification Agent (port 8023)...
start "Notification Agent" cmd /k "python agents/notification_uagent.py"
timeout /t 1 /nobreak

echo Starting Explanation Agent (port 8024)...
start "Explanation Agent" cmd /k "python agents/explanation_uagent.py"
timeout /t 1 /nobreak

echo Starting Verification Agent (port 8025)...
start "Verification Agent" cmd /k "python agents/verification_uagent.py"
timeout /t 1 /nobreak

cls
echo.
echo ====================================================================
echo   AutoRescue AI - Orchestrator Mode Started
echo ====================================================================
echo.
echo [SUCCESS] FastAPI + Phase 9 Orchestrator system running
echo.
echo Active Services:
echo   FastAPI:        http://127.0.0.1:8000
echo   Orchestrator:   Port 8018
echo   Telemetry:      Port 8020
echo   Safety:         Port 8021
echo   Maintenance:    Port 8022
echo   Notification:   Port 8023
echo   Explanation:    Port 8024
echo   Verification:   Port 8025
echo.
echo Test the system:
echo   curl http://127.0.0.1:8000/health
echo   Open http://127.0.0.1:8000/docs
echo.
echo ====================================================================
echo.

pause
