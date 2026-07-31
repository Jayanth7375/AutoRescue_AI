@echo off
REM AutoRescue AI - Phase 10D: Run All 20 Agents (Fixed Environment)
REM Uses uv run for all agents to ensure consistent Python environment

setlocal enabledelayedexpansion

echo.
echo ====================================================================
echo   AutoRescue AI - PHASE 10D: 20-Agent System (Fixed)
echo ====================================================================
echo.

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

if not exist ".env" (
    echo [ERROR] .env file not found
    pause
    exit /b 1
)

echo [INFO] Verifying uv environment...
uv run python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] uv or Python not available
    pause
    exit /b 1
)

cls
echo [INFO] Starting all 20 agents + FastAPI backend...
echo [INFO] Using: uv run python for all services
echo.

REM ===== FASTAPI BACKEND =====
echo [1/21] Starting FastAPI Backend (port 8000)...
start "FastAPI Backend (8000)" cmd /k "cd /d "%SCRIPT_DIR%" && set PYTHONPATH=. && uv run python main.py"
timeout /t 2 /nobreak

REM ===== PHASE 9 ORCHESTRATOR =====
echo [2/21] Starting Orchestrator (port 8018)...
start "Orchestrator (8018)" cmd /k "cd /d "%SCRIPT_DIR%" && set PYTHONPATH=. && uv run python agents/orchestrator_uagent_phase9.py"
timeout /t 2 /nobreak

REM ===== ORIGINAL 10 AGENTS =====
echo [3/21] Starting Diagnostic Agent (port 8011)...
start "Diagnostic (8011)" cmd /k "cd /d "%SCRIPT_DIR%" && uv run python agents/diagnostic_uagent.py"
timeout /t 1 /nobreak

echo [4/21] Starting Service Agent (port 8013)...
start "Service (8013)" cmd /k "cd /d "%SCRIPT_DIR%" && uv run python agents/service_uagent.py"
timeout /t 1 /nobreak

echo [5/21] Starting Rescue Agent (port 8015)...
start "Rescue (8015)" cmd /k "cd /d "%SCRIPT_DIR%" && uv run python agents/rescue_uagent.py"
timeout /t 1 /nobreak

echo [6/21] Starting Telemetry Agent (port 8020)...
start "Telemetry (8020)" cmd /k "cd /d "%SCRIPT_DIR%" && uv run python agents/telemetry_uagent.py"
timeout /t 1 /nobreak

echo [7/21] Starting Safety Agent (port 8021)...
start "Safety (8021)" cmd /k "cd /d "%SCRIPT_DIR%" && uv run python agents/safety_uagent.py"
timeout /t 1 /nobreak

echo [8/21] Starting Maintenance Agent (port 8022)...
start "Maintenance (8022)" cmd /k "cd /d "%SCRIPT_DIR%" && uv run python agents/maintenance_uagent.py"
timeout /t 1 /nobreak

echo [9/21] Starting Notification Agent (port 8023)...
start "Notification (8023)" cmd /k "cd /d "%SCRIPT_DIR%" && uv run python agents/notification_uagent.py"
timeout /t 1 /nobreak

echo [10/21] Starting Explanation Agent (port 8024)...
start "Explanation (8024)" cmd /k "cd /d "%SCRIPT_DIR%" && uv run python agents/explanation_uagent.py"
timeout /t 1 /nobreak

echo [11/21] Starting Verification Agent (port 8025)...
start "Verification (8025)" cmd /k "cd /d "%SCRIPT_DIR%" && uv run python agents/verification_uagent.py"
timeout /t 1 /nobreak

REM ===== NEW 10 AGENTS (PHASE 10) =====
echo [12/21] Starting Vehicle Profile Agent (port 8026)...
start "Vehicle Profile (8026)" cmd /k "cd /d "%SCRIPT_DIR%" && uv run python agents/vehicle_profile_uagent.py"
timeout /t 1 /nobreak

echo [13/21] Starting Battery Health Agent (port 8027)...
start "Battery Health (8027)" cmd /k "cd /d "%SCRIPT_DIR%" && uv run python agents/battery_health_uagent.py"
timeout /t 1 /nobreak

echo [14/21] Starting Tyre Health Agent (port 8028)...
start "Tyre Health (8028)" cmd /k "cd /d "%SCRIPT_DIR%" && uv run python agents/tyre_health_uagent.py"
timeout /t 1 /nobreak

echo [15/21] Starting Engine Health Agent (port 8029)...
start "Engine Health (8029)" cmd /k "cd /d "%SCRIPT_DIR%" && uv run python agents/engine_health_uagent.py"
timeout /t 1 /nobreak

echo [16/21] Starting Breakdown Classification Agent (port 8030)...
start "Breakdown Class (8030)" cmd /k "cd /d "%SCRIPT_DIR%" && uv run python agents/breakdown_classification_uagent.py"
timeout /t 1 /nobreak

echo [17/21] Starting Passenger Safety Agent (port 8031)...
start "Passenger Safety (8031)" cmd /k "cd /d "%SCRIPT_DIR%" && uv run python agents/passenger_safety_uagent.py"
timeout /t 1 /nobreak

echo [18/21] Starting Nearby Assistance Agent (port 8032)...
start "Nearby Assist (8032)" cmd /k "cd /d "%SCRIPT_DIR%" && uv run python agents/nearby_assistance_uagent.py"
timeout /t 1 /nobreak

echo [19/21] Starting Service Ranking Agent (port 8033)...
start "Service Ranking (8033)" cmd /k "cd /d "%SCRIPT_DIR%" && uv run python agents/service_ranking_uagent.py"
timeout /t 1 /nobreak

echo [20/21] Starting Incident Memory Agent (port 8034)...
start "Incident Memory (8034)" cmd /k "cd /d "%SCRIPT_DIR%" && uv run python agents/incident_memory_uagent.py"
timeout /t 1 /nobreak

echo [21/21] Starting Agent Health Monitor (port 8035)...
start "Agent Health (8035)" cmd /k "cd /d "%SCRIPT_DIR%" && uv run python agents/agent_health_monitor_uagent.py"
timeout /t 1 /nobreak

cls
echo.
echo ====================================================================
echo   AutoRescue AI - All 20 Agents Started
echo ====================================================================
echo.
echo [SUCCESS] All 21 services started (20 agents + 1 FastAPI)
echo.
echo IMPORTANT:
echo - Wait 10-15 seconds for all agents to initialize
echo - Each agent is running in its own window
echo - Check status with: check_services.bat
echo - Run tests with: uv run python test_20_agents.py
echo.
echo ====================================================================
echo.

pause
