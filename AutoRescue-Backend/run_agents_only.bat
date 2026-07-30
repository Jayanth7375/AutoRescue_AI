@echo off
REM AutoRescue AI - Run All Agents Only (No FastAPI)
REM Useful for standalone agent testing and development

setlocal enabledelayedexpansion

echo.
echo ====================================================================
echo   AutoRescue AI - All Agents (No FastAPI Backend)
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
echo [INFO] Launching all agents without FastAPI backend...
echo.

REM Phase 9 Orchestrator
echo Starting Orchestrator (port 8018)...
start "Orchestrator (8018)" cmd /k "python agents/orchestrator_uagent_phase9.py"
timeout /t 2 /nobreak

REM Phase 9 Specialist Agents
echo Starting Telemetry Agent (port 8020)...
start "Telemetry (8020)" cmd /k "python agents/telemetry_uagent.py"
timeout /t 1 /nobreak

echo Starting Safety Agent (port 8021)...
start "Safety (8021)" cmd /k "python agents/safety_uagent.py"
timeout /t 1 /nobreak

echo Starting Maintenance Agent (port 8022)...
start "Maintenance (8022)" cmd /k "python agents/maintenance_uagent.py"
timeout /t 1 /nobreak

echo Starting Notification Agent (port 8023)...
start "Notification (8023)" cmd /k "python agents/notification_uagent.py"
timeout /t 1 /nobreak

echo Starting Explanation Agent (port 8024)...
start "Explanation (8024)" cmd /k "python agents/explanation_uagent.py"
timeout /t 1 /nobreak

echo Starting Verification Agent (port 8025)...
start "Verification (8025)" cmd /k "python agents/verification_uagent.py"
timeout /t 1 /nobreak

REM Legacy Agents
echo Starting Diagnostic Agent (port 8011)...
start "Diagnostic (8011)" cmd /k "python agents/diagnostic_uagent.py"
timeout /t 1 /nobreak

echo Starting Service Agent (port 8013)...
start "Service (8013)" cmd /k "python agents/service_uagent.py"
timeout /t 1 /nobreak

echo Starting Rescue Agent (port 8015)...
start "Rescue (8015)" cmd /k "python agents/rescue_uagent.py"
timeout /t 1 /nobreak

cls
echo.
echo ====================================================================
echo   AutoRescue AI - All Agents Running (No Backend)
echo ====================================================================
echo.
echo [SUCCESS] All 10 agents are running!
echo.
echo Active Agent Ports:
echo   Phase 9 Orchestrator:  8018
echo   Telemetry:             8020
echo   Safety:                8021
echo   Maintenance:           8022
echo   Notification:          8023
echo   Explanation:           8024
echo   Verification:          8025
echo   (Legacy)
echo   Diagnostic:            8011
echo   Service:               8013
echo   Rescue:                8015
echo.
echo Note: FastAPI backend is NOT running. Use agents directly or
echo       start FastAPI separately with: python main.py
echo.
echo ====================================================================
echo.

pause
