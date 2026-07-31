@echo off
REM AutoRescue AI - Phase 10: Run All 20 Agents
REM 10 Original Agents + 10 New Agents + FastAPI Backend

setlocal enabledelayedexpansion

echo.
echo ====================================================================
echo   AutoRescue AI - PHASE 10: 20-Agent System
echo ====================================================================
echo.

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

set PYTHONPATH=%SCRIPT_DIR%;%PYTHONPATH%

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
echo [INFO] Starting all 20 agents + FastAPI backend...
echo.

REM ===== FASTAPI BACKEND =====
echo [1/21] Starting FastAPI Backend (port 8000)...
start "FastAPI Backend (8000)" cmd /k "cd /d "%SCRIPT_DIR%" && python main.py"
timeout /t 2 /nobreak

REM ===== PHASE 9 ORCHESTRATOR =====
echo [2/21] Starting Orchestrator (port 8018)...
start "Orchestrator (8018)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/orchestrator_uagent_phase9.py"
timeout /t 2 /nobreak

REM ===== ORIGINAL 10 AGENTS =====
echo [3/21] Starting Diagnostic Agent (port 8011)...
start "Diagnostic (8011)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/diagnostic_uagent.py"
timeout /t 1 /nobreak

echo [4/21] Starting Service Agent (port 8013)...
start "Service (8013)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/service_uagent.py"
timeout /t 1 /nobreak

echo [5/21] Starting Rescue Agent (port 8015)...
start "Rescue (8015)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/rescue_uagent.py"
timeout /t 1 /nobreak

echo [6/21] Starting Telemetry Agent (port 8020)...
start "Telemetry (8020)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/telemetry_uagent.py"
timeout /t 1 /nobreak

echo [7/21] Starting Safety Agent (port 8021)...
start "Safety (8021)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/safety_uagent.py"
timeout /t 1 /nobreak

echo [8/21] Starting Maintenance Agent (port 8022)...
start "Maintenance (8022)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/maintenance_uagent.py"
timeout /t 1 /nobreak

echo [9/21] Starting Notification Agent (port 8023)...
start "Notification (8023)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/notification_uagent.py"
timeout /t 1 /nobreak

echo [10/21] Starting Explanation Agent (port 8024)...
start "Explanation (8024)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/explanation_uagent.py"
timeout /t 1 /nobreak

echo [11/21] Starting Verification Agent (port 8025)...
start "Verification (8025)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/verification_uagent.py"
timeout /t 1 /nobreak

REM ===== NEW 10 AGENTS (PHASE 10) =====
echo [12/21] Starting Vehicle Profile Agent (port 8026)...
start "Vehicle Profile (8026)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/vehicle_profile_uagent.py"
timeout /t 1 /nobreak

echo [13/21] Starting Battery Health Agent (port 8027)...
start "Battery Health (8027)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/battery_health_uagent.py"
timeout /t 1 /nobreak

echo [14/21] Starting Tyre Health Agent (port 8028)...
start "Tyre Health (8028)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/tyre_health_uagent.py"
timeout /t 1 /nobreak

echo [15/21] Starting Engine Health Agent (port 8029)...
start "Engine Health (8029)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/engine_health_uagent.py"
timeout /t 1 /nobreak

echo [16/21] Starting Breakdown Classification Agent (port 8030)...
start "Breakdown Class (8030)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/breakdown_classification_uagent.py"
timeout /t 1 /nobreak

echo [17/21] Starting Passenger Safety Agent (port 8031)...
start "Passenger Safety (8031)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/passenger_safety_uagent.py"
timeout /t 1 /nobreak

echo [18/21] Starting Nearby Assistance Agent (port 8032)...
start "Nearby Assist (8032)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/nearby_assistance_uagent.py"
timeout /t 1 /nobreak

echo [19/21] Starting Service Ranking Agent (port 8033)...
start "Service Ranking (8033)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/service_ranking_uagent.py"
timeout /t 1 /nobreak

echo [20/21] Starting Incident Memory Agent (port 8034)...
start "Incident Memory (8034)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/incident_memory_uagent.py"
timeout /t 1 /nobreak

echo [21/21] Starting Agent Health Monitor (port 8035)...
start "Agent Health (8035)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/agent_health_monitor_uagent.py"
timeout /t 1 /nobreak

cls
echo.
echo ====================================================================
echo   AutoRescue AI - PHASE 10: All 20 Agents + FastAPI Running
echo ====================================================================
echo.
echo [SUCCESS] All 21 services started (20 agents + 1 FastAPI backend)
echo.
echo === FastAPI Backend ===
echo   API:                        http://127.0.0.1:8000
echo   Health:                     http://127.0.0.1:8000/health
echo   Docs:                       http://127.0.0.1:8000/docs
echo.
echo === Original 10 Agents ===
echo   Orchestrator                8018
echo   Diagnostic                  8011
echo   Service                     8013
echo   Rescue                      8015
echo   Telemetry                   8020
echo   Safety                      8021
echo   Maintenance                 8022
echo   Notification                8023
echo   Explanation                 8024
echo   Verification                8025
echo.
echo === New 10 Agents (Phase 10) ===
echo   Vehicle Profile             8026
echo   Battery Health              8027
echo   Tyre Health                 8028
echo   Engine Health               8029
echo   Breakdown Classification    8030
echo   Passenger Safety            8031
echo   Nearby Assistance           8032
echo   Service Ranking             8033
echo   Incident Memory             8034
echo   Agent Health Monitor        8035
echo.
echo === Quick Test ===
echo   curl http://127.0.0.1:8000/health
echo   check_services.bat
echo.
echo ====================================================================
echo.

pause
