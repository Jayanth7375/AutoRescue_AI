# AutoRescue AI — Phase 6: FastAPI Gateway ✓ Complete

## Overview

Phase 6 exposes the Orchestrator uAgent through an HTTP API gateway, enabling the Android app to communicate with the multi-agent AutoRescue system via standard REST endpoints.

**Architecture:**
```
Mobile App (HTTP)
       ↓
FastAPI Gateway (main.py:8000)
       ↓
Orchestrator uAgent (orchestrator_uagent.py:8018)
       ↓
  ┌────┬────┬────┐
  ↓    ↓    ↓    ↓
 Diag  Svc  Resc  Retry
```

---

## Files Implemented / Modified

### 1. `models/autorescue_api.py` — HTTP API Models

**New Pydantic models for external HTTP communication:**

- **`AutoRescueApiRequest`** — Input payload from mobile app
  - `vehicle_id`, `engine_temperature`, `battery_voltage`
  - `front_left_tyre_psi`, `front_right_tyre_psi`, `rear_left_tyre_psi`, `rear_right_tyre_psi`
  - `coolant_level`, `latitude`, `longitude`
  - Full validation: temperature ±50 to ±150°C, voltage 0-20V, PSI 0-60, coolant 0-100%, lat/lon boundaries

- **`DiagnosisApiResponse`** — Diagnosis section of response
  - `issue`, `affected_component`, `severity`, `safe_to_drive`, `recommendation`

- **`ServiceCentreApiResponse`** — Individual service centre in response
  - `place_id`, `name`, `address`, `latitude`, `longitude`
  - `rating`, `review_count`, `is_open`, `distance_km`, `priority_score`, `recommendation_reason`

- **`RescueApiResponse`** — Roadside assistance details (if ASSISTANCE_REQUIRED)
  - `assistance_required`, `assistance_type`, `priority`, `can_drive`, `tow_required`
  - `instructions`, `reason`, `destination_name`, `destination_place_id`, `estimated_dispatch_minutes`

- **`AutoRescueApiResponse`** — Unified response payload
  - `request_id`, `vehicle_id`, `status` (HEALTHY, SERVICE_RECOMMENDED, ASSISTANCE_REQUIRED)
  - `diagnosis`, `service_centres`, `navigation_allowed`, `rescue`, `message`

- **`AutoRescueErrorResponse`** — Error payload
  - `detail`, `request_id`, `stage`

### 2. `main.py` — FastAPI Gateway

**New POST endpoint:** `POST /api/autorescue/check`

**Implementation:**
1. Accepts `AutoRescueApiRequest` (JSON)
2. Generates unique `request_id` (UUID)
3. Constructs `AutoRescueRequestMessage` for Orchestrator
4. **Calls Orchestrator via uAgents query protocol** (`await query(ORCHESTRATOR_AGENT_ADDRESS, message, timeout=120)`)
5. Decodes response and handles:
   - `AutoRescueResponseMessage` → Convert to `AutoRescueApiResponse` (200 OK)
   - `AutoRescueErrorMessage` → HTTP 500 with error detail
   - Timeout → HTTP 504 Gateway Timeout
   - Connection error → HTTP 503 Service Unavailable
   - Validation error → HTTP 422 Unprocessable Entity
6. Returns unified JSON response

**Key Design Decisions:**
- ✓ Gateway is **stateless** — no database, no caching (Orchestrator handles state)
- ✓ FastAPI is **only HTTP translation** — all logic stays in Orchestrator
- ✓ Uses `from uagents.query import query` for inter-agent communication
- ✓ Proper error handling with HTTP status codes
- ✓ Logging with `[GATEWAY]` prefix for request tracking

### 3. `test_gateway.py` — HTTP Integration Tests

**Test Scenarios:**
1. **Healthy Vehicle (TN37AB1234)** — No issues
   - Expected status: `HEALTHY`
   - No rescue, no service needed

2. **Tyre Warning (TN37AB1234)** — Front-left PSI 28 (warning threshold)
   - Expected status: `SERVICE_RECOMMENDED`
   - Service centres returned, no rescue

3. **Engine Overheating (TN37AB1234)** — Engine temp 122°C (critical)
   - Expected status: `ASSISTANCE_REQUIRED`
   - Service centres + rescue assistance (tow/cooling)

**Features:**
- Async HTTP client (httpx) with 120s timeout
- Waits for gateway health check before testing
- Validates response structure and severity levels
- Detailed logging for debugging

---

## How It Works

### HTTP Request Flow

```json
POST /api/autorescue/check
Content-Type: application/json

{
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
}
```

### Response (Healthy Vehicle)

```json
HTTP 200 OK

{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "vehicle_id": "TN37AB1234",
  "status": "HEALTHY",
  "diagnosis": {
    "issue": "No issues detected",
    "affected_component": "NONE",
    "severity": "NORMAL",
    "safe_to_drive": true,
    "recommendation": "Vehicle is in good condition. Continue monitoring."
  },
  "service_centres": [],
  "navigation_allowed": true,
  "rescue": null,
  "message": "Your vehicle is healthy. No service or assistance required."
}
```

### Response (Critical Engine)

```json
HTTP 200 OK

{
  "request_id": "550e8400-e29b-41d4-a716-446655440001",
  "vehicle_id": "TN37AB1234",
  "status": "ASSISTANCE_REQUIRED",
  "diagnosis": {
    "issue": "Engine overheating",
    "affected_component": "ENGINE",
    "severity": "CRITICAL",
    "safe_to_drive": false,
    "recommendation": "Stop immediately. Do not continue driving. Engine cooling system failure suspected."
  },
  "service_centres": [
    {
      "place_id": "osm:node:1234567",
      "name": "Mumbai Auto Cooling Center",
      "address": "Bandra, Mumbai",
      "latitude": 19.0596,
      "longitude": 72.8295,
      "rating": 4.5,
      "review_count": 120,
      "is_open": true,
      "distance_km": 8.3,
      "priority_score": 87.2,
      "recommendation_reason": "Specialized cooling system service with excellent rating"
    }
  ],
  "navigation_allowed": false,
  "rescue": {
    "assistance_required": true,
    "assistance_type": "TOW",
    "priority": "CRITICAL",
    "can_drive": false,
    "tow_required": true,
    "instructions": "CRITICAL: Stop immediately. Engine overheating detected. Tow truck is being dispatched.",
    "reason": "Engine temperature critically high with unsafe_to_drive flag. Vehicle should not be driven.",
    "destination_name": "Mumbai Auto Cooling Center",
    "destination_place_id": "osm:node:1234567",
    "estimated_dispatch_minutes": 10
  },
  "message": "CRITICAL: Engine overheating. Tow assistance and cooling system service required. Help is on the way."
}
```

### Error Response (Service Unavailable)

```json
HTTP 503 Service Unavailable

{
  "detail": "AutoRescue orchestration service is unavailable"
}
```

---

## Architecture: Gateway ↔ Orchestrator Communication

### uAgents Query Protocol

The gateway does **not** directly call Diagnostic/Service/Rescue agents.

```python
# In main.py
response = await query(
    destination=ORCHESTRATOR_AGENT_ADDRESS,  # From .env
    message=orchestrator_msg,                 # AutoRescueRequestMessage
    timeout=120                               # 2 minutes
)
```

### Message Flow

1. **Gateway sends:** `AutoRescueRequestMessage`
   - Contains: request_id, vehicle_id, telemetry, coordinates
   
2. **Orchestrator receives:** `AutoRescueRequestMessage`
   - Routes to Diagnostic Agent
   
3. **Orchestrator processes:**
   - Diagnostic → DiagnosticResponseMessage
   - If NORMAL → returns immediately
   - Else → Service Agent → ServiceResponseMessage
   - If safe_to_drive=false → Rescue Agent → RescueResponseMessage
   
4. **Orchestrator sends back:** `AutoRescueResponseMessage`
   - Contains: complete diagnosis, centres, rescue info, status
   
5. **Gateway converts:** `AutoRescueResponseMessage` → `AutoRescueApiResponse`
   - JSON serialization with full type safety

---

## Testing

### Option 1: Automated Test (Recommended)

**Windows PowerShell:**
```powershell
# Start all services in one command
.\run_all_agents.ps1

# In another terminal, run tests (after services are ready):
python test_gateway.py
```

**Linux/macOS:**
```bash
# Make scripts executable
chmod +x run_phase6_test.sh

# Run complete test suite
./run_phase6_test.sh
```

### Option 2: Manual Testing

**Terminal 1 - Diagnostic Agent:**
```bash
python run_diagnostic_agent.py
```

**Terminal 2 - Service Agent:**
```bash
python run_service_agent.py
```

**Terminal 3 - Rescue Agent:**
```bash
python run_rescue_agent.py
```

**Terminal 4 - Orchestrator:**
```bash
python run_orchestrator_agent.py
```

**Terminal 5 - FastAPI Gateway:**
```bash
python main.py
# or
uvicorn main:app --host 127.0.0.1 --port 8000
```

**Terminal 6 - Run Tests:**
```bash
python test_gateway.py
```

### Option 3: Manual HTTP Testing (cURL)

```bash
# Healthy vehicle test
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
  }'

# Engine overheating test
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
  }'
```

---

## Integration with Android App

### Endpoint
```
POST http://<server-ip>:8000/api/autorescue/check
```

### Request Format (JSON)
```kotlin
// Android Kotlin example
val request = mapOf(
    "vehicle_id" to "TN37AB1234",
    "engine_temperature" to 95.0,
    "battery_voltage" to 12.7,
    "front_left_tyre_psi" to 32.0,
    "front_right_tyre_psi" to 32.0,
    "rear_left_tyre_psi" to 31.0,
    "rear_right_tyre_psi" to 31.0,
    "coolant_level" to 75.0,
    "latitude" to 19.076,
    "longitude" to 72.8777
)

val response = httpClient.post("http://<server>/api/autorescue/check") {
    contentType(ContentType.Application.Json)
    setBody(request)
}
```

### Response Parsing
```kotlin
data class AutoRescueResponse(
    val request_id: String,
    val vehicle_id: String,
    val status: String,  // HEALTHY, SERVICE_RECOMMENDED, ASSISTANCE_REQUIRED
    val diagnosis: Diagnosis,
    val service_centres: List<ServiceCentre>,
    val navigation_allowed: Boolean,
    val rescue: Rescue?,
    val message: String
)

// Parse navigation decisions
when (response.status) {
    "HEALTHY" -> showHealthyMessage()
    "SERVICE_RECOMMENDED" -> showServiceLocations(response.service_centres)
    "ASSISTANCE_REQUIRED" -> {
        if (response.rescue?.tow_required == true) {
            showTowDispatch(response.rescue.estimated_dispatch_minutes)
        }
    }
}

// Navigation flag
if (!response.navigation_allowed) {
    disableNavigation("Vehicle cannot be driven safely")
}
```

---

## Phase Progression

| Phase | Component | Status |
|-------|-----------|--------|
| 1 | FastAPI + Diagnostic Rules | ✓ Complete |
| 2 | Diagnostic uAgent | ✓ Complete |
| 3 | Service uAgent + OSM | ✓ Complete |
| 4 | Rescue uAgent | ✓ Complete |
| 5 | Orchestrator uAgent | ✓ Complete |
| 6 | **HTTP Gateway (FastAPI)** | ✓ **Complete** |

---

## Key Design Principles Maintained

✓ **No Database** — Gateway is stateless  
✓ **No LLM** — All logic is deterministic rules-based  
✓ **No Android Changes** — Pure backend implementation  
✓ **No Bypass** — Orchestrator remains the brain  
✓ **uAgent Query Protocol** — Standard inter-agent communication  
✓ **Type Safety** — Full Pydantic validation throughout  
✓ **Error Handling** — HTTP status codes reflect agent/orchestration state  
✓ **Logging** — Request tracking with correlation IDs  

---

## Files Created in Phase 6

1. **models/autorescue_api.py** — HTTP API models (81 lines)
2. **main.py** (updated) — POST /api/autorescue/check endpoint (248 lines)
3. **test_gateway.py** — Integration test suite (167 lines)
4. **run_all_agents.ps1** — Windows service orchestration (77 lines)
5. **run_phase6_test.sh** — Linux/macOS automated testing (91 lines)
6. **PHASE_6_COMPLETE.md** — This documentation

---

## Next Steps for Android Integration

1. **Point Android app to gateway:** `http://<backend-server>:8000/api/autorescue/check`
2. **Validate request format:** Match `AutoRescueApiRequest` schema
3. **Handle response status:** Use `status` field for UI routing
4. **Display results:**
   - `HEALTHY` → Show message
   - `SERVICE_RECOMMENDED` → Show centres with navigation
   - `ASSISTANCE_REQUIRED` → Show rescue details + centres
5. **Respect navigation_allowed flag** → Disable navigation if false

---

## Environment Configuration

Ensure `.env` has these variables set:

```env
ORCHESTRATOR_AGENT_ADDRESS=agent1qwrumduc7wqzwqkc6zt30pqem5j76gyttf36as7ggqzsqy5zeh67s9d08mz
ORCHESTRATOR_AGENT_PORT=8018
DIAGNOSTIC_AGENT_PORT=8011
SERVICE_AGENT_PORT=8013
RESCUE_AGENT_PORT=8015
OVERPASS_API_URL=https://overpass.openstreetmap.fr/api/interpreter
```

Gateway will auto-load these on startup.

---

## Summary

**Phase 6 is complete.** The FastAPI gateway successfully:
- ✓ Receives HTTP requests from Android app
- ✓ Routes to Orchestrator via uAgents query protocol
- ✓ Handles all response types (Diagnosis, Service, Rescue, Error)
- ✓ Converts agent messages to JSON API responses
- ✓ Provides proper HTTP status codes
- ✓ Logs request flow with correlation IDs
- ✓ Maintains stateless, deterministic architecture

**All 6 phases are now complete.** The AutoRescue AI backend is production-ready for integration with the Android mobile application.
