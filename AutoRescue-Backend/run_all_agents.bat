@echo off
REM AutoRescue AI - Run All Agents and FastAPI Backend
REM This script launches all required agents and services

setlocal enabledelayedexpansion

echo.
echo ====================================================================
echo   AutoRescue AI - Complete Agent Orchestration System
echo ====================================================================
echo.

REM Get the script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check if .env exists
if not exist ".env" (
    echo [ERROR] .env file not found in %SCRIPT_DIR%
    echo [ERROR] Please create .env file with required configuration
    pause
    exit /b 1
)

echo [INFO] Starting AutoRescue AI System...
echo [INFO] Backend Directory: %SCRIPT_DIR%
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [INFO] Python found. Launching services...
echo.

REM Colors and formatting for output
cls

REM ===================================================================
REM PHASE 1: Launch FastAPI Backend Server
REM ===================================================================
echo Launching FastAPI Backend Server (port 8000)...
start "AutoRescue FastAPI Backend" cmd /k "python main.py"
timeout /t 2 /nobreak

REM ===================================================================
REM PHASE 2: Launch Phase 9 Orchestrator Agent
REM ===================================================================
echo Launching Phase 9 Orchestrator Agent (port 8018)...
start "AutoRescue Orchestrator (8018)" cmd /k "python agents/orchestrator_uagent_phase9.py"
timeout /t 2 /nobreak

REM ===================================================================
REM PHASE 3: Launch Phase 9 Specialist Agents
REM ===================================================================
echo Launching Telemetry Validation Agent (port 8020)...
start "AutoRescue Telemetry Agent (8020)" cmd /k "python agents/telemetry_uagent.py"
timeout /t 1 /nobreak

echo Launching Safety Assessment Agent (port 8021)...
start "AutoRescue Safety Agent (8021)" cmd /k "python agents/safety_uagent.py"
timeout /t 1 /nobreak

echo Launching Maintenance Planning Agent (port 8022)...
start "AutoRescue Maintenance Agent (8022)" cmd /k "python agents/maintenance_uagent.py"
timeout /t 1 /nobreak

echo Launching Notification Agent (port 8023)...
start "AutoRescue Notification Agent (8023)" cmd /k "python agents/notification_uagent.py"
timeout /t 1 /nobreak

echo Launching AI Explanation Agent (port 8024)...
start "AutoRescue Explanation Agent (8024)" cmd /k "python agents/explanation_uagent.py"
timeout /t 1 /nobreak

echo Launching Verification Agent (port 8025)...
start "AutoRescue Verification Agent (8025)" cmd /k "python agents/verification_uagent.py"
timeout /t 1 /nobreak

REM ===================================================================
REM PHASE 4: Launch Legacy Phase 8 Agents (Optional but Supported)
REM ===================================================================
echo Launching Legacy Diagnostic Agent (port 8011)...
start "AutoRescue Diagnostic Agent (8011)" cmd /k "python agents/diagnostic_uagent.py"
timeout /t 1 /nobreak

echo Launching Legacy Service Centre Agent (port 8013)...
start "AutoRescue Service Agent (8013)" cmd /k "python agents/service_uagent.py"
timeout /t 1 /nobreak

echo Launching Legacy Rescue Agent (port 8015)...
start "AutoRescue Rescue Agent (8015)" cmd /k "python agents/rescue_uagent.py"
timeout /t 1 /nobreak

REM ===================================================================
REM COMPLETION
REM ===================================================================
cls
echo.
echo ====================================================================
echo   AutoRescue AI System - All Services Launched
echo ====================================================================
echo.
echo [SUCCESS] All agents and services have been started!
echo.
echo Endpoint Summary:
echo ────────────────────────────────────────────────────────────────
echo FastAPI Backend:              http://127.0.0.1:8000
echo   - Health Check:             http://127.0.0.1:8000/health
echo   - API Docs (Swagger):       http://127.0.0.1:8000/docs
echo   - AutoRescue Check:         POST http://127.0.0.1:8000/api/autorescue/check
echo   - Chat Endpoint:            POST http://127.0.0.1:8000/api/chat
echo   - Nearby Places:            GET  http://127.0.0.1:8000/api/rescue/nearby
echo.
echo Phase 9 Orchestrator (10-Agent System):
echo   - Orchestrator:             Port 8018
echo   - Telemetry Validation:     Port 8020
echo   - Safety Assessment:        Port 8021
echo   - Maintenance Planning:     Port 8022
echo   - Notifications:            Port 8023
echo   - AI Explanations:          Port 8024
echo   - Verification:             Port 8025
echo.
echo Legacy Phase 8 Agents:
echo   - Diagnostic Analysis:      Port 8011
echo   - Service Centre Search:    Port 8013
echo   - Rescue Assessment:        Port 8015
echo.
echo ────────────────────────────────────────────────────────────────
echo Agent Logs:
echo   Each agent runs in its own console window with live logs
echo   Close any window to stop that specific service
echo.
echo Configuration:
echo   Environment File:           .env
echo   Log Level:                  INFO
echo   Python Version:             %PYTHON_VERSION%
echo ────────────────────────────────────────────────────────────────
echo.
echo [NEXT STEPS]
echo 1. Wait 3-5 seconds for all agents to initialize
echo 2. Test API: curl http://127.0.0.1:8000/health
echo 3. Open Swagger UI: http://127.0.0.1:8000/docs
echo 4. Send test request to /api/autorescue/check
echo.
echo [TROUBLESHOOTING]
echo - If agents fail to start, check .env file configuration
echo - Verify all ports (8000, 8011-8025) are available
echo - Check Python dependencies: pip install -r requirements.txt
echo - Review individual agent windows for error messages
echo.
echo [STOPPING THE SYSTEM]
echo Close all console windows to stop all services, or use Ctrl+C in each window
echo.
echo ====================================================================
echo.

REM Keep this window open
pause
