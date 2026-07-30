@echo off
REM AutoRescue AI - Service Status Checker
REM Checks if all services are running and healthy

setlocal enabledelayedexpansion

echo.
echo ====================================================================
echo   AutoRescue AI - Service Status Check
echo ====================================================================
echo.

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Colors and status symbols
set OK=[OK]
set FAIL=[FAIL]
set WAIT=[WAIT]

echo Checking AutoRescue AI services...
echo.

REM Function to check if port is open
REM We'll use netstat to check active connections

echo Checking FastAPI Backend (port 8000)...
netstat -an | find ":8000" >nul 2>&1
if %errorlevel%==0 (
    echo %OK% FastAPI Backend is running on port 8000
) else (
    echo %FAIL% FastAPI Backend is NOT running
)

echo.
echo Checking Phase 9 Orchestrator System:
echo.

set AGENTS=^
    "8018:Orchestrator"^
    "8020:Telemetry"^
    "8021:Safety"^
    "8022:Maintenance"^
    "8023:Notification"^
    "8024:Explanation"^
    "8025:Verification"

for %%A in (%AGENTS%) do (
    for /f "tokens=1,2 delims=:" %%B in ("%%A") do (
        netstat -an | find ":%%B" >nul 2>&1
        if !errorlevel!==0 (
            echo %OK% %%C agent running on port %%B
        ) else (
            echo %FAIL% %%C agent NOT running on port %%B
        )
    )
)

echo.
echo Checking Legacy Agents:
echo.

set LEGACY_AGENTS=^
    "8011:Diagnostic"^
    "8013:Service"^
    "8015:Rescue"

for %%A in (%LEGACY_AGENTS%) do (
    for /f "tokens=1,2 delims=:" %%B in ("%%A") do (
        netstat -an | find ":%%B" >nul 2>&1
        if !errorlevel!==0 (
            echo %OK% %%C agent running on port %%B
        ) else (
            echo %FAIL% %%C agent NOT running on port %%B
        )
    )
)

echo.
echo Checking FastAPI Health Endpoint...
curl -s http://127.0.0.1:8000/health >nul 2>&1
if %errorlevel%==0 (
    echo %OK% FastAPI health endpoint is responding
) else (
    echo %FAIL% FastAPI health endpoint is not responding
)

echo.
echo ====================================================================
echo   Service Check Complete
echo ====================================================================
echo.
echo To start services, run one of:
echo   - run_all_agents.bat              (Start everything)
echo   - run_orchestrator_only.bat       (Start core services)
echo   - run_agents_only.bat             (Start agents only)
echo   - run_fastapi_only.bat            (Start FastAPI only)
echo.

pause
