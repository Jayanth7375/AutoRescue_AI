# How to Start AutoRescue AI Backend Services

## Quick Start

### Step 1: Clean Up Old Processes
**Windows PowerShell (Admin):**
```powershell
$ports = @(8000, 8011, 8013, 8015, 8018)
foreach ($port in $ports) {
    $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($conn) {
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}
Start-Sleep -Seconds 3
```

### Step 2: Start All Services
**Windows PowerShell:**
```powershell
cd AutoRescue-Backend
.\run_all_agents_fixed.ps1
```

Expected output:
```
==========================================
      AutoRescue AI Backend Startup
==========================================

Pre-startup: Cleaning up any existing processes...
Waiting 3 seconds for ports to release...

Starting Diagnostic Agent :8011...
  Process started (PID: 12345)
  Health checking on port 8011...
    Attempt 1/20...
    Attempt 2/20...
Diagnostic Agent health check PASSED

[Similar for Service, Rescue, Orchestrator agents...]

Waiting 5 seconds for agents to fully initialize...

Starting FastAPI Gateway :8000...
  Process started (PID: 12356)
  Health checking on port 8000...
FastAPI Gateway health check PASSED

==========================================
 AutoRescue AI services have been started
==========================================

Services:
  FastAPI Gateway     : http://127.0.0.1:8000
  Swagger UI          : http://127.0.0.1:8000/docs
  Diagnostic Agent    : port 8011
  Service Agent       : port 8013
  Rescue Agent        : port 8015
  Orchestrator Agent  : port 8018

Next step:
  uv run python test_gateway.py

Press Ctrl+C to stop all services
```

### Step 3: Test Gateway (New Terminal)
```powershell
cd AutoRescue-Backend
uv run python test_gateway.py
```

Expected output:
```
ALL GATEWAY TESTS PASSED (3/3)
✓ PASS: Healthy Vehicle
✓ PASS: Tyre Warning
✓ PASS: Engine Overheating
```

---

## Troubleshooting

### Issue: "FAILED: Diagnostic Agent :8011 did not respond to health check"

**Root Cause:** Port still in use from previous run

**Solution 1 - Manual port cleanup:**
```powershell
# Find what's using the port
Get-NetTCPConnection -LocalPort 8011 -State Listen

# Kill the process
Stop-Process -Id <PID> -Force

# Wait and retry
Start-Sleep -Seconds 3
.\run_all_agents_fixed.ps1
```

**Solution 2 - Nuclear option (kill all Python processes):**
```powershell
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force
Get-Process | Where-Object {$_.ProcessName -like "*uvicorn*"} | Stop-Process -Force
Start-Sleep -Seconds 5
.\run_all_agents_fixed.ps1
```

### Issue: Agent window closes immediately

**Cause:** Script or import error in agent

**Solution:** Run agent directly in terminal to see error
```powershell
cd AutoRescue-Backend
uv run python run_diagnostic_agent.py
# Will show actual error message
```

### Issue: Gateway gives "HTTP 503 Service Unavailable"

**Cause:** Orchestrator not running or ORCHESTRATOR_AGENT_ADDRESS not set

**Check:**
1. All 5 services running? Check spawned PowerShell windows
2. Check `.env` has `ORCHESTRATOR_AGENT_ADDRESS` set
3. Verify agent logs in each PowerShell window

### Issue: "Port already in use" error

**Check which process is using it:**
```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen
Get-NetTCPConnection -LocalPort 8011 -State Listen
Get-NetTCPConnection -LocalPort 8013 -State Listen
Get-NetTCPConnection -LocalPort 8015 -State Listen
Get-NetTCPConnection -LocalPort 8018 -State Listen
```

**Kill the process:**
```powershell
Stop-Process -Id <PID> -Force
```

---

## What the Fixed Script Does

✅ **Pre-startup cleanup:**
- Finds any existing processes using ports 8000, 8011, 8013, 8015, 8018
- Kills them gracefully
- Waits 3 seconds for ports to release

✅ **Sequential startup:**
- Starts each agent one at a time
- Waits 3 seconds for the process to launch
- Performs health check on HTTP /health endpoint
- Retries up to 20 times with 1-second intervals (20 seconds max)
- If health check passes, moves to next service
- If health check fails, stops and reports the error

✅ **Better error messages:**
- Shows PID of each launched process
- Reports health check progress
- Explains how to troubleshoot on failure
- Clear success message with next steps

---

## Manual Testing (If Script Fails)

Open 5 separate PowerShell windows and run:

**Terminal 1:**
```powershell
cd AutoRescue-Backend
uv run python run_diagnostic_agent.py
```

**Terminal 2:**
```powershell
cd AutoRescue-Backend
uv run python run_service_agent.py
```

**Terminal 3:**
```powershell
cd AutoRescue-Backend
uv run python run_rescue_agent.py
```

**Terminal 4:**
```powershell
cd AutoRescue-Backend
uv run python run_orchestrator_agent.py
```

**Terminal 5:**
```powershell
cd AutoRescue-Backend
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

**Terminal 6:**
```powershell
cd AutoRescue-Backend
uv run python test_gateway.py
```

Each terminal should show:
- Diagnostic Agent: `Uvicorn running on http://0.0.0.0:8011`
- Service Agent: `Uvicorn running on http://0.0.0.0:8013`
- Rescue Agent: `Uvicorn running on http://0.0.0.0:8015`
- Orchestrator: `Uvicorn running on http://0.0.0.0:8018`
- FastAPI Gateway: `Uvicorn running on http://0.0.0.0:8000`
- Test output: `ALL GATEWAY TESTS PASSED (3/3)`

---

## Key Changes in Fixed Script

1. **Pre-startup port cleanup** - Kills any zombie processes before starting
2. **Longer waits** - 3 seconds after spawn, 5 seconds between agent stages
3. **Better logging** - Shows PID, attempts, timeouts
4. **Improved retry logic** - 20 retries with 1-second intervals (instead of 10 retries)
5. **Better error messages** - Troubleshooting hints when services fail to start
6. **String formatting** - Fixed PowerShell syntax issues

---

## Next Steps

1. Run `.\run_all_agents_fixed.ps1`
2. Once all services show health checks PASSED
3. Open new terminal and run `uv run python test_gateway.py`
4. Verify ALL GATEWAY TESTS PASSED (3/3)
5. Android app can now integrate with `http://server:8000/api/autorescue/check`

---

## Quick Health Check

If services are already running, verify they're working:

```powershell
# Check each service
curl http://127.0.0.1:8011/health  # Diagnostic Agent
curl http://127.0.0.1:8013/health  # Service Agent
curl http://127.0.0.1:8015/health  # Rescue Agent
curl http://127.0.0.1:8018/health  # Orchestrator Agent
curl http://127.0.0.1:8000/health  # FastAPI Gateway

# All should return: {"status":"ok",...}
```

---

## Getting Help

1. Check agent logs in spawned PowerShell windows
2. Look for "ERROR" or "Traceback" lines
3. Note the full error message
4. Check `.env` configuration
5. Try manual startup in separate terminals for clearer error output
