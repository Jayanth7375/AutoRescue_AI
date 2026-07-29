# Phase 6 Gateway — Testing Guide

## Pre-Test Verification

### Step 1: Verify Imports ✓
```bash
uv run python -c "import main; print('MAIN IMPORT OK')"
```

**Expected:**
```
MAIN IMPORT OK
```

### Step 2: Verify Dependencies
```bash
uv sync
```

**Expected:**
```
Resolved 56 packages in 2ms
Checked 55 packages in 10ms
```

### Step 3: Clean Old Processes
**Windows PowerShell:**
```powershell
Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*uvicorn*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
```

**Linux/macOS:**
```bash
pkill -f "uvicorn\|python.*run_.*agent\|python.*main.py"
sleep 3
```

---

## Automated Testing (Recommended)

### Start All Services
**Windows PowerShell:**
```powershell
cd AutoRescue-Backend
.\run_all_agents.ps1
```

**Linux/macOS:**
```bash
cd AutoRescue-Backend
chmod +x run_phase6_test.sh
./run_phase6_test.sh
```

**Expected output:**
```
==========================================
      AutoRescue AI Backend Startup
==========================================

Starting Diagnostic Agent :8011...
Diagnostic Agent health check passed.

Starting Service Agent :8013...
Service Agent health check passed.

Starting Rescue Agent :8015...
Rescue Agent health check passed.

Starting Orchestrator Agent :8018...
Orchestrator Agent health check passed.

Starting FastAPI Gateway :8000...
FastAPI Gateway health check passed.

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

Next run:
  uv run python test_gateway.py
```

### Run Gateway Tests (New Terminal)
```bash
uv run python test_gateway.py
```

**Expected output:**
```
============================================================
FastAPI Gateway Test Suite
============================================================
Gateway URL: http://127.0.0.1:8000

Waiting for gateway to be ready...
OK Gateway is ready

============================================================
SCENARIO: Healthy Vehicle (No Service/Rescue)
============================================================
HTTP Status: 200
Status: HEALTHY
Diagnosis Severity: NORMAL
Service Centres: 0
Navigation Allowed: True
OK Status matches expected: HEALTHY

============================================================
SCENARIO: Tyre Warning (Service Recommended)
============================================================
HTTP Status: 200
Status: SERVICE_RECOMMENDED
Diagnosis Severity: WARNING
Service Centres: 5
Navigation Allowed: True
OK Status matches expected: SERVICE_RECOMMENDED

============================================================
SCENARIO: Engine Overheating (Assistance Required)
============================================================
HTTP Status: 200
Status: ASSISTANCE_REQUIRED
Diagnosis Severity: CRITICAL
Service Centres: 5
Navigation Allowed: False
Rescue Type: TOW
Tow Required: True
OK Status matches expected: ASSISTANCE_REQUIRED

============================================================
TEST RESULTS
============================================================
OK PASS: Healthy Vehicle
OK PASS: Tyre Warning
OK PASS: Engine Overheating

============================================================
OK ALL GATEWAY TESTS PASSED (3/3)
==============================================================
HTTP gateway successfully routes to Orchestrator
```

**If all tests pass:** ✅ Gateway is working!

---

## Manual Testing

If automated testing doesn't work, test manually.

### Terminal Setup

**Terminal 1: Diagnostic Agent**
```bash
uv run python run_diagnostic_agent.py
```

Wait for:
```
INFO:     Started server process [...]
INFO:     Uvicorn running on http://127.0.0.1:8011 (Press CTRL+C to quit)
```

**Terminal 2: Service Agent**
```bash
uv run python run_service_agent.py
```

Wait for:
```
INFO:     Started server process [...]
INFO:     Uvicorn running on http://127.0.0.1:8013 (Press CTRL+C to quit)
```

**Terminal 3: Rescue Agent**
```bash
uv run python run_rescue_agent.py
```

Wait for:
```
INFO:     Started server process [...]
INFO:     Uvicorn running on http://127.0.0.1:8015 (Press CTRL+C to quit)
```

**Terminal 4: Orchestrator Agent**
```bash
uv run python run_orchestrator_agent.py
```

Wait for:
```
INFO:     Started server process [...]
INFO:     Uvicorn running on http://127.0.0.1:8018 (Press CTRL+C to quit)
```

**Terminal 5: FastAPI Gateway**
```bash
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

Wait for:
```
INFO:     Started server process [...]
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Verify Endpoints

**Terminal 6: Test health endpoints**

```bash
# Test gateway health
curl -s http://127.0.0.1:8000/health | python -m json.tool

# Test endpoint exists
curl -s http://127.0.0.1:8000/openapi.json | python -c "import sys,json; print('\n'.join(json.load(sys.stdin)['paths'].keys()))"
```

**Expected:**
```json
{
    "status": "ok",
    "service": "AutoRescue AI Backend"
}

/
/health
/diagnose
/api/autorescue/check
```

### Test Gateway Endpoint

**Scenario 1: Healthy Vehicle**
```bash
curl -X POST http://127.0.0.1:8000/api/autorescue/check \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "TN37AB1234",
    "engine_temperature": 95,
    "battery_voltage": 12.7,
    "front_left_tyre_psi": 32,
    "front_right_tyre_psi": 32,
    "rear_left_tyre_psi": 31,
    "rear_right_tyre_psi": 31,
    "coolant_level": 75,
    "latitude": 19.076,
    "longitude": 72.8777
  }' | python -m json.tool
```

**Expected:**
```json
{
  "request_id": "550e8400-...",
  "vehicle_id": "TN37AB1234",
  "status": "HEALTHY",
  "diagnosis": {
    "severity": "NORMAL",
    "safe_to_drive": true,
    "issue": "No issues detected",
    ...
  },
  "service_centres": [],
  "navigation_allowed": true,
  "rescue": null,
  ...
}
```

**Scenario 2: Tyre Warning**
```bash
curl -X POST http://127.0.0.1:8000/api/autorescue/check \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "TN37AB1234",
    "engine_temperature": 95,
    "battery_voltage": 12.7,
    "front_left_tyre_psi": 28,
    "front_right_tyre_psi": 32,
    "rear_left_tyre_psi": 31,
    "rear_right_tyre_psi": 31,
    "coolant_level": 75,
    "latitude": 19.076,
    "longitude": 72.8777
  }' | python -m json.tool
```

**Expected:**
```json
{
  "status": "SERVICE_RECOMMENDED",
  "diagnosis": {
    "severity": "WARNING",
    "safe_to_drive": true,
    "issue": "Tyre pressure low",
    ...
  },
  "service_centres": [...],
  "navigation_allowed": true,
  "rescue": null,
  ...
}
```

**Scenario 3: Engine Overheating**
```bash
curl -X POST http://127.0.0.1:8000/api/autorescue/check \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "TN37AB1234",
    "engine_temperature": 122,
    "battery_voltage": 12.7,
    "front_left_tyre_psi": 32,
    "front_right_tyre_psi": 32,
    "rear_left_tyre_psi": 31,
    "rear_right_tyre_psi": 31,
    "coolant_level": 75,
    "latitude": 19.076,
    "longitude": 72.8777
  }' | python -m json.tool
```

**Expected:**
```json
{
  "status": "ASSISTANCE_REQUIRED",
  "diagnosis": {
    "severity": "CRITICAL",
    "safe_to_drive": false,
    "issue": "Engine overheating",
    ...
  },
  "service_centres": [...],
  "navigation_allowed": false,
  "rescue": {
    "assistance_type": "TOW",
    "priority": "CRITICAL",
    "tow_required": true,
    "estimated_dispatch_minutes": 10,
    ...
  },
  ...
}
```

---

## Troubleshooting

### Issue: "Port 8000 already in use"
**Solution:**
```powershell
# Windows PowerShell
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force
Start-Sleep -Seconds 3
```

### Issue: "ModuleNotFoundError: No module named 'uagents'"
**Solution:**
```bash
uv sync
uv run python -c "import main; print('OK')"
```

### Issue: "No health check response from gateway"
**Solution:**
1. Verify FastAPI started: Check for "Uvicorn running on..." in terminal
2. Verify port isn't firewalled: `curl http://127.0.0.1:8000/` should work
3. Check logs for import errors
4. Verify .env has ORCHESTRATOR_AGENT_ADDRESS set

### Issue: "Orchestrator did not respond"
**Solution:**
1. Verify all 4 agents started (Diagnostic, Service, Rescue, Orchestrator)
2. Check .env has correct ORCHESTRATOR_AGENT_ADDRESS
3. Check Orchestrator logs for errors
4. Verify agents can reach each other (all on localhost)

### Issue: "Service centres returned: 0"
**Cause:** Overpass API rate limiting or no results  
**Solution:** Try different coordinates or wait a minute and retry

### Issue: "HTTP 422 Unprocessable Entity"
**Cause:** Invalid request data  
**Solution:** 
- Check field values are within bounds
- Engine: -50 to 150°C
- Battery: 0 to 20V
- Tyres: 0 to 60 PSI
- Coolant: 0 to 100%
- Latitude: -90 to 90
- Longitude: -180 to 180

---

## Success Criteria

✅ All tests pass 3/3  
✅ Gateway responds to all 3 scenarios  
✅ Statuses are correct (HEALTHY, SERVICE_RECOMMENDED, ASSISTANCE_REQUIRED)  
✅ Service centres returned when appropriate  
✅ Rescue details present for critical issues  
✅ Navigation allowed flag correct  

---

## Next Steps After Testing

1. ✅ **Verify gateway works** ← You are here
2. **Document response format** for Android app
3. **Test with Android app** using real telemetry
4. **Deploy to production server**
5. **Monitor logs** for issues

---

## Summary

**Phase 6 is fully functional and ready for integration.**

- ✅ All 5 agents start and respond
- ✅ Gateway routes requests through Orchestrator
- ✅ Responses are properly formatted JSON
- ✅ HTTP status codes are correct
- ✅ Timeouts are handled gracefully
- ✅ Error messages are clear

**Android app can now integrate with the backend.**
