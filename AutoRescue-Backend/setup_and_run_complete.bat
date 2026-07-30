@echo off
REM AutoRescue AI - Complete Setup with ALL Agents (Phase 9 + Phase 8)

setlocal enabledelayedexpansion

echo.
echo ====================================================================
echo   AutoRescue AI - Complete Setup with All Agents
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
    pause
    exit /b 1
)
echo [OK] .env file found
echo.

REM Install dependencies
echo [STEP 3] Installing/Upgrading dependencies...
echo [INFO] This may take 1-2 minutes on first run...
echo.

echo [INFO] Installing packages with --user flag (uv-compatible)...
pip install --user --upgrade pip setuptools wheel >nul 2>&1

echo [INFO] Installing required packages...
pip install --user -r requirements.txt >nul 2>&1

echo [OK] Dependency installation complete
echo.

echo ====================================================================
echo   Starting All AutoRescue AI Services
echo ====================================================================
echo.

REM Start FastAPI Backend
echo [1/11] Starting FastAPI Backend (port 8000)...
start "AutoRescue FastAPI Backend" cmd /k "cd /d "%SCRIPT_DIR%" && python main.py"
timeout /t 2 /nobreak

REM ===== PHASE 9 ORCHESTRATION SYSTEM =====
echo [2/11] Starting Phase 9 Orchestrator (port 8018)...
start "Orchestrator (8018)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/orchestrator_uagent_phase9.py"
timeout /t 2 /nobreak

echo [3/11] Starting Telemetry Validation Agent (port 8020)...
start "Telemetry (8020)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/telemetry_uagent.py"
timeout /t 1 /nobreak

echo [4/11] Starting Safety Assessment Agent (port 8021)...
start "Safety (8021)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/safety_uagent.py"
timeout /t 1 /nobreak

echo [5/11] Starting Maintenance Planning Agent (port 8022)...
start "Maintenance (8022)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/maintenance_uagent.py"
timeout /t 1 /nobreak

echo [6/11] Starting Notification Agent (port 8023)...
start "Notification (8023)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/notification_uagent.py"
timeout /t 1 /nobreak

echo [7/11] Starting AI Explanation Agent (port 8024)...
start "Explanation (8024)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/explanation_uagent.py"
timeout /t 1 /nobreak

echo [8/11] Starting Verification Agent (port 8025)...
start "Verification (8025)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/verification_uagent.py"
timeout /t 1 /nobreak

REM ===== LEGACY PHASE 8 AGENTS =====
echo [9/11] Starting Diagnostic Agent (port 8011) - LEGACY...
start "Diagnostic (8011)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/diagnostic_uagent.py"
timeout /t 1 /nobreak

echo [10/11] Starting Service Centre Agent (port 8013) - LEGACY...
start "Service (8013)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/service_uagent.py"
timeout /t 1 /nobreak

echo [11/11] Starting Rescue Agent (port 8015) - LEGACY...
start "Rescue (8015)" cmd /k "cd /d "%SCRIPT_DIR%" && python agents/rescue_uagent.py"
timeout /t 1 /nobreak

cls
echo.
echo ====================================================================
echo   AutoRescue AI - Complete System Running
echo ====================================================================
echo.
echo [SUCCESS] All 11 services have been started!
echo.
echo === FastAPI Backend ===
echo   REST API:               http://127.0.0.1:8000
echo   Health Check:           http://127.0.0.1:8000/health
echo   Swagger UI (API Docs):  http://127.0.0.1:8000/docs
echo   ReDoc:                  http://127.0.0.1:8000/redoc
echo.
echo === Phase 9 Orchestration System (10-Agent Coordination) ===
echo   Orchestrator:           Port 8018  (Coordinator)
echo   Telemetry:              Port 8020  (Validation)
echo   Safety:                 Port 8021  (Assessment)
echo   Maintenance:            Port 8022  (Planning)
echo   Notification:           Port 8023  (Alerts)
echo   Explanation:            Port 8024  (AI Responses)
echo   Verification:           Port 8025  (Validation)
echo.
echo === Legacy Phase 8 Agents (Backward Compatibility) ===
echo   Diagnostic:             Port 8011  (Analysis)
echo   Service Centre:         Port 8013  (Search)
echo   Rescue:                 Port 8015  (Coordination)
echo.
echo ====================================================================
echo   Quick Test Commands
echo ====================================================================
echo.
echo Test FastAPI health:
echo   curl http://127.0.0.1:8000/health
echo.
echo Test complete diagnostic check:
echo   curl -X POST http://127.0.0.1:8000/api/autorescue/check ^
echo     -H "Content-Type: application/json" ^
echo     -d "{\"vehicle_id\":\"TEST-001\",\"engine_temperature\":95,\"battery_voltage\":12.5,\"front_left_tyre_psi\":32,\"front_right_tyre_psi\":32,\"rear_left_tyre_psi\":30,\"rear_right_tyre_psi\":30,\"coolant_level\":85,\"latitude\":40.7128,\"longitude\":-74.0060}"
echo.
echo Check service status in another terminal:
echo   check_services.bat
echo.
echo ====================================================================
echo   Console Windows
echo ====================================================================
echo.
echo You should see 11 console windows open with live logs:
echo   - 1 FastAPI window
echo   - 7 Phase 9 agent windows
echo   - 3 Legacy agent windows
echo.
echo If any window shows an error, check:
echo   1. .env file configuration
echo   2. All ports (8000-8025) are available
echo   3. Python dependencies are installed
echo.
echo To stop a specific service, close its window or press Ctrl+C
echo To stop everything, close all windows
echo.
echo ====================================================================
echo.
echo Press any key to close this setup window...
echo.

pause
