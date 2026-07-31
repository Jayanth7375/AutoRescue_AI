@echo off
REM AutoRescue AI - Complete 20-Agent Service Status Checker

setlocal enabledelayedexpansion

echo.
echo ====================================================================
echo   AutoRescue AI - 20-Agent System Status Check
echo ====================================================================
echo.

set OK=[OK]
set FAIL=[FAIL]

set ONLINE=0
set OFFLINE=0

REM FastAPI
echo Checking FastAPI Backend (port 8000)...
netstat -an | find ":8000" >nul 2>&1
if !errorlevel!==0 (
    echo !OK! FastAPI Backend (8000)
    set /a ONLINE=!ONLINE!+1
) else (
    echo !FAIL! FastAPI Backend (8000) NOT RUNNING
    set /a OFFLINE=!OFFLINE!+1
)

echo.
echo Checking Original 10 Agents:
echo.

REM Original agents
for %%A in (
    "8011:Diagnostic"
    "8013:Service"
    "8015:Rescue"
    "8018:Orchestrator"
    "8020:Telemetry"
    "8021:Safety"
    "8022:Maintenance"
    "8023:Notification"
    "8024:Explanation"
    "8025:Verification"
) do (
    for /f "tokens=1,2 delims=:" %%B in ("%%A") do (
        netstat -an | find ":%%B" >nul 2>&1
        if !errorlevel!==0 (
            echo !OK! %%C (%%B)
            set /a ONLINE=!ONLINE!+1
        ) else (
            echo !FAIL! %%C (%%B) NOT RUNNING
            set /a OFFLINE=!OFFLINE!+1
        )
    )
)

echo.
echo Checking New 10 Agents (Phase 10):
echo.

REM New agents
for %%A in (
    "8026:Vehicle Profile"
    "8027:Battery Health"
    "8028:Tyre Health"
    "8029:Engine Health"
    "8030:Breakdown Classification"
    "8031:Passenger Safety"
    "8032:Nearby Assistance"
    "8033:Service Ranking"
    "8034:Incident Memory"
    "8035:Agent Health Monitor"
) do (
    for /f "tokens=1,2 delims=:" %%B in ("%%A") do (
        netstat -an | find ":%%B" >nul 2>&1
        if !errorlevel!==0 (
            echo !OK! %%C (%%B)
            set /a ONLINE=!ONLINE!+1
        ) else (
            echo !FAIL! %%C (%%B) NOT RUNNING
            set /a OFFLINE=!OFFLINE!+1
        )
    )
)

echo.
echo Checking FastAPI Health Endpoint...
curl -s http://127.0.0.1:8000/health >nul 2>&1
if !errorlevel!==0 (
    echo !OK! FastAPI health endpoint responding
) else (
    echo !FAIL! FastAPI health endpoint not responding
)

echo.
echo ====================================================================
echo   Service Status Summary
echo ====================================================================
echo.
echo ONLINE:  !ONLINE!/21
echo OFFLINE: !OFFLINE!/21
echo.

if !OFFLINE!==0 (
    echo [SUCCESS] All 21 services ONLINE - System ready
) else (
    echo [WARNING] !OFFLINE! service(s) offline - Check logs
)

echo.
echo To start services, run:
echo   .\run_all_20_agents.bat
echo.
echo To run integration tests, run:
echo   uv run python test_20_agents.py
echo.

pause
