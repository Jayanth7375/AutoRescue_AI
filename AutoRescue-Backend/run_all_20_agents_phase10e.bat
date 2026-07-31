@echo off
REM AutoRescue AI - Phase 10E: Run All 20 Agents (Smart Port Checking)
REM Checks port availability BEFORE launching to prevent Errno 10048

setlocal enabledelayedexpansion

echo.
echo ====================================================================
echo   AutoRescue AI - PHASE 10E: 20-Agent System (Port-Aware)
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
echo [INFO] Checking port availability before launch...
echo.

REM ===== FASTAPI BACKEND =====
echo [1/21] Checking FastAPI (port 8000)...
netstat -an | find ":8000 " >nul 2>&1
if !errorlevel!==0 (
    echo [SKIP] FastAPI Backend already running on port 8000
) else (
    echo [START] FastAPI Backend (port 8000)
    start "FastAPI Backend (8000)" cmd /k "cd /d "%SCRIPT_DIR%" && set PYTHONPATH=. && uv run python main.py"
    timeout /t 2 /nobreak
)

REM ===== PHASE 9 ORCHESTRATOR =====
echo [2/21] Checking Orchestrator (port 8018)...
netstat -an | find ":8018 " >nul 2>&1
if !errorlevel!==0 (
    echo [SKIP] Orchestrator already running on port 8018
) else (
    echo [START] Orchestrator (port 8018)
    start "Orchestrator (8018)" cmd /k "cd /d "%SCRIPT_DIR%" && set PYTHONPATH=. && uv run python agents/orchestrator_uagent_phase9.py"
    timeout /t 2 /nobreak
)

REM ===== ORIGINAL 10 AGENTS =====
echo [3/21] Checking Diagnostic Agent (port 8011)...
netstat -an | find ":8011 " >nul 2>&1
if !errorlevel!==0 (
    echo [SKIP] Diagnostic already running on port 8011
) else (
    echo [START] Diagnostic Agent (port 8011)
    start "Diagnostic (8011)" cmd /k "cd /d "%SCRIPT_DIR%" && set PYTHONPATH=. && uv run python agents/diagnostic_uagent.py"
    timeout /t 1 /nobreak
)

echo [4/21] Checking Service Agent (port 8013)...
netstat -an | find ":8013 " >nul 2>&1
if !errorlevel!==0 (
    echo [SKIP] Service already running on port 8013
) else (
    echo [START] Service Agent (port 8013)
    start "Service (8013)" cmd /k "cd /d "%SCRIPT_DIR%" && set PYTHONPATH=. && uv run python agents/service_uagent.py"
    timeout /t 1 /nobreak
)

echo [5/21] Checking Rescue Agent (port 8015)...
netstat -an | find ":8015 " >nul 2>&1
if !errorlevel!==0 (
    echo [SKIP] Rescue already running on port 8015
) else (
    echo [START] Rescue Agent (port 8015)
    start "Rescue (8015)" cmd /k "cd /d "%SCRIPT_DIR%" && set PYTHONPATH=. && uv run python agents/rescue_uagent.py"
    timeout /t 1 /nobreak
)

echo [6/21] Checking Telemetry Agent (port 8020)...
netstat -an | find ":8020 " >nul 2>&1
if !errorlevel!==0 (
    echo [SKIP] Telemetry already running on port 8020
) else (
    echo [START] Telemetry Agent (port 8020)
    start "Telemetry (8020)" cmd /k "cd /d "%SCRIPT_DIR%" && set PYTHONPATH=. && uv run python agents/telemetry_uagent.py"
    timeout /t 1 /nobreak
)

echo [7/21] Checking Safety Agent (port 8021)...
netstat -an | find ":8021 " >nul 2>&1
if !errorlevel!==0 (
    echo [SKIP] Safety already running on port 8021
) else (
    echo [START] Safety Agent (port 8021)
    start "Safety (8021)" cmd /k "cd /d "%SCRIPT_DIR%" && set PYTHONPATH=. && uv run python agents/safety_uagent.py"
    timeout /t 1 /nobreak
)

echo [8/21] Checking Maintenance Agent (port 8022)...
netstat -an | find ":8022 " >nul 2>&1
if !errorlevel!==0 (
    echo [SKIP] Maintenance already running on port 8022
) else (
    echo [START] Maintenance Agent (port 8022)
    start "Maintenance (8022)" cmd /k "cd /d "%SCRIPT_DIR%" && set PYTHONPATH=. && uv run python agents/maintenance_uagent.py"
    timeout /t 1 /nobreak
)

echo [9/21] Checking Notification Agent (port 8023)...
netstat -an | find ":8023 " >nul 2>&1
if !errorlevel!==0 (
    echo [SKIP] Notification already running on port 8023
) else (
    echo [START] Notification Agent (port 8023)
    start "Notification (8023)" cmd /k "cd /d "%SCRIPT_DIR%" && set PYTHONPATH=. && uv run python agents/notification_uagent.py"
    timeout /t 1 /nobreak
)

echo [10/21] Checking Explanation Agent (port 8024)...
netstat -an | find ":8024 " >nul 2>&1
if !errorlevel!==0 (
    echo [SKIP] Explanation already running on port 8024
) else (
    echo [START] Explanation Agent (port 8024)
    start "Explanation (8024)" cmd /k "cd /d "%SCRIPT_DIR%" && set PYTHONPATH=. && uv run python agents/explanation_uagent.py"
    timeout /t 1 /nobreak
)

echo [11/21] Checking Verification Agent (port 8025)...
netstat -an | find ":8025 " >nul 2>&1
if !errorlevel!==0 (
    echo [SKIP] Verification already running on port 8025
) else (
    echo [START] Verification Agent (port 8025)
    start "Verification (8025)" cmd /k "cd /d "%SCRIPT_DIR%" && set PYTHONPATH=. && uv run python agents/verification_uagent.py"
    timeout /t 1 /nobreak
)

REM ===== NEW 10 AGENTS (PHASE 10) =====
echo [12/21] Checking Vehicle Profile Agent (port 8026)...
netstat -an | find ":8026 " >nul 2>&1
if !errorlevel!==0 (
    echo [SKIP] Vehicle Profile already running on port 8026
) else (
    echo [START] Vehicle Profile Agent (port 8026)
    start "Vehicle Profile (8026)" cmd /k "cd /d "%SCRIPT_DIR%" && set PYTHONPATH=. && uv run python agents/vehicle_profile_uagent.py"
    timeout /t 1 /nobreak
)

echo [13/21] Checking Battery Health Agent (port 8027)...
netstat -an | find ":8027 " >nul 2>&1
if !errorlevel!==0 (
    echo [SKIP] Battery Health already running on port 8027
) else (
    echo [START] Battery Health Agent (port 8027)
    start "Battery Health (8027)" cmd /k "cd /d "%SCRIPT_DIR%" && set PYTHONPATH=. && uv run python agents/battery_health_uagent.py"
    timeout /t 1 /nobreak
)

echo [14/21] Checking Tyre Health Agent (port 8028)...
netstat -an | find ":8028 " >nul 2>&1
if !errorlevel!==0 (
    echo [SKIP] Tyre Health already running on port 8028
) else (
    echo [START] Tyre Health Agent (port 8028)
    start "Tyre Health (8028)" cmd /k "cd /d "%SCRIPT_DIR%" && set PYTHONPATH=. && uv run python agents/tyre_health_uagent.py"
    timeout /t 1 /nobreak
)

echo [15/21] Checking Engine Health Agent (port 8029)...
netstat -an | find ":8029 " >nul 2>&1
if !errorlevel!==0 (
    echo [SKIP] Engine Health already running on port 8029
) else (
    echo [START] Engine Health Agent (port 8029)
    start "Engine Health (8029)" cmd /k "cd /d "%SCRIPT_DIR%" && set PYTHONPATH=. && uv run python agents/engine_health_uagent.py"
    timeout /t 1 /nobreak
)

echo [16/21] Checking Breakdown Classification Agent (port 8030)...
netstat -an | find ":8030 " >nul 2>&1
if !errorlevel!==0 (
    echo [SKIP] Breakdown Classification already running on port 8030
) else (
    echo [START] Breakdown Classification Agent (port 8030)
    start "Breakdown Class (8030)" cmd /k "cd /d "%SCRIPT_DIR%" && set PYTHONPATH=. && uv run python agents/breakdown_classification_uagent.py"
    timeout /t 1 /nobreak
)

echo [17/21] Checking Passenger Safety Agent (port 8031)...
netstat -an | find ":8031 " >nul 2>&1
if !errorlevel!==0 (
    echo [SKIP] Passenger Safety already running on port 8031
) else (
    echo [START] Passenger Safety Agent (port 8031)
    start "Passenger Safety (8031)" cmd /k "cd /d "%SCRIPT_DIR%" && set PYTHONPATH=. && uv run python agents/passenger_safety_uagent.py"
    timeout /t 1 /nobreak
)

echo [18/21] Checking Nearby Assistance Agent (port 8032)...
netstat -an | find ":8032 " >nul 2>&1
if !errorlevel!==0 (
    echo [SKIP] Nearby Assistance already running on port 8032
) else (
    echo [START] Nearby Assistance Agent (port 8032)
    start "Nearby Assist (8032)" cmd /k "cd /d "%SCRIPT_DIR%" && set PYTHONPATH=. && uv run python agents/nearby_assistance_uagent.py"
    timeout /t 1 /nobreak
)

echo [19/21] Checking Service Ranking Agent (port 8033)...
netstat -an | find ":8033 " >nul 2>&1
if !errorlevel!==0 (
    echo [SKIP] Service Ranking already running on port 8033
) else (
    echo [START] Service Ranking Agent (port 8033)
    start "Service Ranking (8033)" cmd /k "cd /d "%SCRIPT_DIR%" && set PYTHONPATH=. && uv run python agents/service_ranking_uagent.py"
    timeout /t 1 /nobreak
)

echo [20/21] Checking Incident Memory Agent (port 8034)...
netstat -an | find ":8034 " >nul 2>&1
if !errorlevel!==0 (
    echo [SKIP] Incident Memory already running on port 8034
) else (
    echo [START] Incident Memory Agent (port 8034)
    start "Incident Memory (8034)" cmd /k "cd /d "%SCRIPT_DIR%" && set PYTHONPATH=. && uv run python agents/incident_memory_uagent.py"
    timeout /t 1 /nobreak
)

echo [21/21] Checking Agent Health Monitor (port 8035)...
netstat -an | find ":8035 " >nul 2>&1
if !errorlevel!==0 (
    echo [SKIP] Agent Health Monitor already running on port 8035
) else (
    echo [START] Agent Health Monitor (port 8035)
    start "Agent Health (8035)" cmd /k "cd /d "%SCRIPT_DIR%" && set PYTHONPATH=. && uv run python agents/agent_health_monitor_uagent.py"
    timeout /t 1 /nobreak
)

cls
echo.
echo ====================================================================
echo   AutoRescue AI - All 20 Agents Processing Complete
echo ====================================================================
echo.
echo [SUCCESS] All 21 services configured (20 agents + 1 FastAPI)
echo.
echo IMPORTANT:
echo - Wait 10-15 seconds for all agents to initialize
echo - Each service is running in its own window
echo - Check status with: check_services.bat
echo - Run tests with: uv run python test_20_agents.py
echo.
echo ====================================================================
echo.

pause
