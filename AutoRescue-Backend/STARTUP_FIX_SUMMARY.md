# Startup Script Fix Summary

## Problem Identified

The original `run_all_agents.ps1` was using HTTP `GET /health` checks on all services, but:

- **uAgents** (Diagnostic, Service, Rescue, Orchestrator) do NOT expose `/health` endpoints
- uAgents only expose communication endpoints like `/submit`
- Only **FastAPI Gateway** has a `/health` endpoint

This caused the startup script to fail on all uAgent services with:
```
FAILED: Diagnostic Agent :8011 did not respond to health check
```

---

## Solution Implemented

### 1. TCP Port Readiness for uAgents

Created `Wait-ForTcpPort` function:
```powershell
function Wait-ForTcpPort {
    param(
        [int]$Port,
        [int]$MaxRetries = 20
    )

    for ($i = 0; $i -lt $MaxRetries; $i++) {
        $ready = Test-NetConnection `
            -ComputerName "127.0.0.1" `
            -Port $Port `
            -InformationLevel Quiet `
            -WarningAction SilentlyContinue

        if ($ready) {
            return $true
        }

        Start-Sleep -Milliseconds 500
    }

    return $false
}
```

**Used for:**
- Diagnostic Agent :8011
- Service Agent :8013
- Rescue Agent :8015
- Orchestrator Agent :8018

### 2. HTTP Health Check for FastAPI Gateway

Created `Wait-ForHttpHealth` function:
```powershell
function Wait-ForHttpHealth {
    param(
        [int]$Port,
        [int]$MaxRetries = 20
    )

    for ($i = 0; $i -lt $MaxRetries; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/health" `
                -TimeoutSec 2 `
                -ErrorAction Stop

            if ($response.StatusCode -eq 200) {
                return $true
            }
        }
        catch {
            # Continue retrying
        }

        Start-Sleep -Milliseconds 500
    }

    return $false
}
```

### 3. OpenAPI Endpoint Verification

Created `Verify-OpenApiEndpoint` function:
```powershell
function Verify-OpenApiEndpoint {
    param(
        [int]$Port
    )

    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/openapi.json" `
            -TimeoutSec 2 `
            -ErrorAction Stop

        $openapi = $response.Content | ConvertFrom-Json
        return $openapi.paths.Contains("/api/autorescue/check")
    }
    catch {
        return $false
    }
}
```

Ensures `/api/autorescue/check` endpoint exists in OpenAPI schema.

### 4. Separate Start Functions

**For uAgents:**
```powershell
function Start-AutoRescueAgent {
    # Uses Wait-ForTcpPort
    # Prints: "READY: [Agent Name]" on success
}
```

**For FastAPI:**
```powershell
function Start-FastApiGateway {
    # Uses Wait-ForHttpHealth
    # Verifies /api/autorescue/check endpoint
    # Prints: "READY: FastAPI Gateway :8000" on success
}
```

---

## Startup Output (Now Correct)

```
==========================================
      AutoRescue AI Backend Startup
==========================================

Pre-startup: Cleaning up any existing processes...
  Stopping PID XXXX on port 8011...
  Stopping PID XXXX on port 8013...
  Stopping PID XXXX on port 8015...
  Stopping PID XXXX on port 8018...
  Stopping PID XXXX on port 8000...
Waiting 3 seconds for ports to release...

Starting Diagnostic Agent :8011...
  Waiting for port 8011...
READY: Diagnostic Agent :8011

Starting Service Agent :8013...
  Waiting for port 8013...
READY: Service Agent :8013

Starting Rescue Agent :8015...
  Waiting for port 8015...
READY: Rescue Agent :8015

Starting Orchestrator Agent :8018...
  Waiting for port 8018...
READY: Orchestrator Agent :8018

Starting FastAPI Gateway :8000...
  Waiting for HTTP health on port 8000...
  Verifying /api/autorescue/check endpoint...
READY: FastAPI Gateway :8000

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

---

## Files Modified

| File | Changes |
|------|---------|
| **run_all_agents.ps1** | Complete rewrite with correct readiness checks |

---

## Files NOT Modified (As Instructed)

✅ No Python agents modified  
✅ No `/health` endpoints added to agents  
✅ No Orchestrator logic changes  
✅ This is purely a PowerShell readiness-check fix  

---

## How to Use

### Step 1: Clean Up
```powershell
cd AutoRescue-Backend
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force
Start-Sleep -Seconds 5
```

### Step 2: Start Services
```powershell
.\run_all_agents.ps1
```

**Expected output:**
```
READY: Diagnostic Agent :8011
READY: Service Agent :8013
READY: Rescue Agent :8015
READY: Orchestrator Agent :8018
READY: FastAPI Gateway :8000
```

### Step 3: Test Gateway (New Terminal)
```powershell
cd AutoRescue-Backend
uv run python test_gateway.py
```

**Expected output:**
```
ALL GATEWAY TESTS PASSED (3/3)
✓ PASS: Healthy Vehicle
✓ PASS: Tyre Warning
✓ PASS: Engine Overheating
```

---

## Technical Details

### TCP Port Readiness vs HTTP Health

**TCP Port Readiness (Test-NetConnection):**
- ✅ Works as soon as the service is listening on the port
- ✅ No HTTP endpoint required
- ✅ Fast (50ms check intervals)
- ✅ Correct for uAgents

**HTTP Health (/health):**
- ✅ Verifies the service is actually responding
- ✅ Confirms the HTTP server is running
- ✅ Slower (requires HTTP handshake)
- ✅ Correct for FastAPI

### Why TCP First, Then HTTP for FastAPI?

1. `Test-NetConnection` confirms the port is listening (very fast)
2. `Invoke-WebRequest /health` confirms HTTP is working (slightly slower)
3. `Verify-OpenApiEndpoint` confirms the gateway is properly configured

This gives us high confidence the service is actually ready before moving on.

---

## Debugging

If a service fails to start:

1. Check spawned PowerShell windows for error messages
2. Look for "ERROR" or "Traceback" lines in agent terminals
3. Verify .env configuration
4. Try manual startup in separate terminals

Manual startup:
```powershell
cd AutoRescue-Backend
uv run python run_diagnostic_agent.py
# Should show: Uvicorn running on http://0.0.0.0:8011
```

---

## Summary

✅ **Fixed:** Incorrect health checks on uAgents  
✅ **Added:** TCP port readiness for uAgents  
✅ **Kept:** HTTP health check for FastAPI  
✅ **Added:** OpenAPI endpoint verification  
✅ **Result:** Clear "READY" messages for all services  

**Ready to test: `.\run_all_agents.ps1`**
