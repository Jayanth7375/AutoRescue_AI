# Phase 6 Synchronous Gateway — Test Execution Plan

## Current Status

✅ **Orchestrator:** Added `@on_query` handler with `orchestrate_sync()` function  
✅ **FastAPI Gateway:** Updated to use `send_sync_message()` API  
✅ **Test Suite:** Created `test_orchestrator_sync.py` for direct sync testing  
✅ **Error Handling:** Proper type detection and logging  

## Pre-Test Checklist

- [ ] All Python files saved
- [ ] No syntax errors
- [ ] All agents buildable (no import errors)
- [ ] .env file has all AGENT_ADDRESS variables set

**Verify:**
```powershell
uv run python -c "import main; print('MAIN IMPORT OK')"
uv run python -c "from agents.orchestrator_uagent import orchestrator_uagent; print('ORCHESTRATOR IMPORT OK')"
```

---

## Test Execution (Step-by-Step)

### Step 1: Start All Services

**Clean up old processes first:**
```powershell
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 5
```

**Start all services:**
```powershell
cd AutoRescue-Backend
.\run_all_agents.ps1
```

**Expected output (wait for all "READY" messages):**
```
Pre-startup: Cleaning up any existing processes...
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
  uv run python test_orchestrator_sync.py

Press Ctrl+C to stop all services
```

**If any service shows "FAILED":**
- Check spawned PowerShell windows for error messages
- Look for "ERROR" or "Traceback" lines
- Common issues:
  - Import errors (missing modules)
  - Port already in use (run cleanup again)
  - Missing .env variables

---

### Step 2: Test Orchestrator Synchronous Path (NEW)

**Open NEW PowerShell terminal (do NOT close the services terminal):**

```powershell
cd AutoRescue-Backend
uv run python test_orchestrator_sync.py
```

**Expected output:**
```
============================================================
Orchestrator Synchronous Query Test Suite
============================================================
Orchestrator Address: agent1qwrumduc7wqzwqkc6zt30pqem5j76gyttf36as7ggqzsqy5zeh67s9d08mz

============================================================
SCENARIO: Healthy Vehicle (No Service/Rescue)
============================================================
Sending synchronous query to agent1qwrum...
Request ID: 550e8400-...
Response type: AutoRescueResponseMessage
Status: HEALTHY
Diagnosis Severity: NORMAL
Safe to Drive: True
Service Centres: 0
Navigation Allowed: True
OK Status matches expected: HEALTHY

============================================================
SCENARIO: Tyre Warning (Service Recommended)
============================================================
Sending synchronous query to agent1qwrum...
Request ID: 550e8401-...
Response type: AutoRescueResponseMessage
Status: SERVICE_RECOMMENDED
Diagnosis Severity: WARNING
Safe to Drive: True
Service Centres: 5
Navigation Allowed: True
OK Status matches expected: SERVICE_RECOMMENDED

============================================================
SCENARIO: Engine Overheating (Assistance Required)
============================================================
Sending synchronous query to agent1qwrum...
Request ID: 550e8402-...
Response type: AutoRescueResponseMessage
Status: ASSISTANCE_REQUIRED
Diagnosis Severity: CRITICAL
Safe to Drive: False
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
OK ALL ORCHESTRATOR SYNC TESTS PASSED (3/3)
============================================================
Synchronous query handler is working correctly
```

**If test FAILS:**
- Check Orchestrator logs in spawned terminal for errors
- Look for `[ORCHESTRATOR QUERY]` messages
- Common issues:
  - `ctx.send_and_receive()` timeouts (agent not responding)
  - Type mismatches in response handling
  - Missing specialist agents

---

### Step 3: Test FastAPI Gateway (HTTP)

**Same PowerShell terminal (or new one):**

```powershell
cd AutoRescue-Backend
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

**If test FAILS:**
- Check FastAPI logs in spawned terminal
- Look for `[GATEWAY]` messages
- Check response type being logged
- HTTP errors indicate communication or conversion issue

---

### Step 4: Regression Test — Async Orchestrator (Phase 5)

**Verify existing async path still works:**

```powershell
cd AutoRescue-Backend
uv run python test_orchestrator.py
```

**Expected output:**
```
============================================================
Orchestrator Multi-Agent Test Suite
============================================================
Orchestrator Address: agent1qwrumduc7wqzwqkc6zt30pqem5j76gyttf36as7ggqzsqy5zeh67s9d08mz

============================================================
SCENARIO: Healthy Vehicle
============================================================
...
OK PASS: Healthy Vehicle

============================================================
SCENARIO: Tyre Warning
============================================================
...
OK PASS: Tyre Warning

============================================================
SCENARIO: Engine Overheating
============================================================
...
OK PASS: Engine Overheating

============================================================
TEST RESULTS
============================================================
OK PASS: Healthy Vehicle
OK PASS: Tyre Warning
OK PASS: Engine Overheating

OK ALL ORCHESTRATOR TESTS PASSED (3/3)
============================================================
```

**If fails:** The async message handlers were modified - check orchestrator_uagent.py

---

### Step 5: Regression Test — Phase 1 API (Diagnostic Endpoint)

**Verify Phase 1 endpoint still works:**

```powershell
cd AutoRescue-Backend
uv run python test_api.py
```

**Expected output:**
```
Starting AutoRescue AI Backend Tests
==================================================
Starting server...

===== Test 1: Healthy Vehicle =====
Status: 200
OK Test passed

===== Test 2: Engine Overheating =====
Status: 200
OK Test passed

===== Test 3: Critical Tyre Pressure =====
Status: 200
OK Test passed

===== Test 4: Critical Coolant Level =====
Status: 200
OK Test passed

===== Test 5: Health Endpoint =====
Status: 200
OK Test passed

==================================================
Test Summary
==================================================
OK PASS: Health
OK PASS: Healthy Vehicle
OK PASS: Engine Overheating
OK PASS: Critical Tyre
OK PASS: Critical Coolant

Total: 5/5 tests passed
```

**If fails:** Phase 1 code was accidentally modified - check main.py /diagnose endpoint

---

## Test Summary Table

| Test | Command | Expected | If Fails |
|------|---------|----------|----------|
| **Sync Orchestrator** | `python test_orchestrator_sync.py` | 3/3 PASS | Check Orchestrator logs |
| **HTTP Gateway** | `python test_gateway.py` | 3/3 PASS | Check FastAPI + Orchestrator logs |
| **Async Orchestrator (Regression)** | `python test_orchestrator.py` | 3/3 PASS | Check async message handlers |
| **Phase 1 API (Regression)** | `python test_api.py` | 5/5 PASS | Check /diagnose endpoint |

---

## Success Criteria

✅ **PASS:** All 4 test suites show "3/3 PASS" or "5/5 PASS"  
✅ **PASS:** No "FAILED" messages in test output  
✅ **PASS:** No "HTTP 500" errors  
✅ **PASS:** No "Invalid response type" errors  
✅ **PASS:** Async orchestrator still works (Phase 5)  
✅ **PASS:** Phase 1 diagnostic endpoint still works  

---

## Troubleshooting Quick Reference

### "Test passed but gateway failed"
- Orchestrator sync works, but FastAPI integration broke
- Check: FastAPI response conversion logic in main.py
- Check: send_sync_message() call has response_type=AutoRescueResponseMessage

### "All sync tests fail with connection error"
- Orchestrator query handler not responding
- Check: @on_query decorator is present
- Check: orchestrate_sync() function exists
- Check: ctx.send_and_receive() calls have correct addresses

### "HTTP 500 'Invalid response type'"
- FastAPI got unexpected response from send_sync_message()
- Check: logger output shows type(result)
- Common cause: send_sync_message() returning MsgStatus (communication failed)

### "Service centres empty for warning scenario"
- Service Agent not returning results
- Check: Service Agent running and healthy
- Check: Overpass API accessible
- Check: Service agent logs for errors

---

## After All Tests Pass

1. ✅ Phase 6 gateway is complete
2. ✅ Synchronous query path works
3. ✅ Asynchronous path still works (backward compatibility)
4. ✅ All regression tests pass
5. **Ready for:** Android app integration

---

## Run All Tests Quickly

```powershell
# Terminal 1 (keep running)
.\run_all_agents.ps1

# Terminal 2 (run in order)
uv run python test_orchestrator_sync.py
uv run python test_gateway.py
uv run python test_orchestrator.py
uv run python test_api.py

# Check results:
# - test_orchestrator_sync.py → 3/3
# - test_gateway.py → 3/3
# - test_orchestrator.py → 3/3
# - test_api.py → 5/5
```

**If all show PASS: Phase 6 is complete and fully operational.**
