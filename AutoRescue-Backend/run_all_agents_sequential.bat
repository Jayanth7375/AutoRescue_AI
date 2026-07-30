@echo off
REM AutoRescue AI - Run All Agents Sequentially (For CI/Testing)
REM This version runs agents in sequence instead of parallel windows
REM Useful for CI/CD pipelines and non-interactive environments

setlocal enabledelayedexpansion

echo.
echo ====================================================================
echo   AutoRescue AI - Sequential Agent Startup (CI Mode)
echo ====================================================================
echo.

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

if not exist ".env" (
    echo [ERROR] .env file not found
    exit /b 1
)

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed
    exit /b 1
)

echo [INFO] Starting AutoRescue AI System (Sequential Mode)
echo [INFO] Each agent will start in sequence
echo.

REM Note: To truly run in parallel in CI, you would need to:
REM 1. Use ProcessHacker or similar
REM 2. Use background jobs in PowerShell
REM 3. Use a third-party process manager like pm2

echo Starting FastAPI Backend...
python main.py &
set FASTAPI_PID=!ERRORLEVEL!
timeout /t 3

echo Starting Orchestrator Agent...
python agents/orchestrator_uagent_phase9.py &

echo Starting Telemetry Agent...
python agents/telemetry_uagent.py &

echo Starting Safety Agent...
python agents/safety_uagent.py &

echo Starting Maintenance Agent...
python agents/maintenance_uagent.py &

echo Starting Notification Agent...
python agents/notification_uagent.py &

echo Starting Explanation Agent...
python agents/explanation_uagent.py &

echo Starting Verification Agent...
python agents/verification_uagent.py &

echo Starting Diagnostic Agent (Legacy)...
python agents/diagnostic_uagent.py &

echo Starting Service Agent (Legacy)...
python agents/service_uagent.py &

echo Starting Rescue Agent (Legacy)...
python agents/rescue_uagent.py &

echo.
echo ====================================================================
echo   All agents started in background
echo ====================================================================
echo.
echo To stop all services, use: taskkill /F /IM python.exe
echo Note: This will stop ALL Python processes on the system
echo.
