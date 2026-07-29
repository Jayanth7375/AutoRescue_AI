# Phase 7: Android ↔ Backend Integration Plan

## Existing Architecture (Discovered)

### Project Structure
- **Package:** com.example
- **Build System:** Gradle with Kotlin DSL
- **UI Framework:** Jetpack Compose + Material 3
- **Networking:** Retrofit + OkHttp + Moshi (already configured)
- **Coroutines:** kotlinx.coroutines
- **Location:** Play Services Location

### Current Screens
- HomeScreen
- DiagnoseScreen
- RescueScreen
- VehicleScreen
- NotificationsScreen
- ProfileScreen

### Current Components
- **DiagnosticEngine:** Local diagnostic rules (to be bypassed)
- **TelemetryRepository:** Demo telemetry provider (to be extended)
- **LocationRepository:** GPS location handling (to be reused)
- **LocationViewModel:** Location state management (to be reused)
- **DiagnosticsViewModel:** Local diagnosis state (to be updated)
- **VehicleViewModel:** Overall vehicle state

### Existing Models
- VehicleTelemetry (simplified - single tyre pressure, not 4 individual tyres)
- DiagnosticResult
- ServiceCentre
- HealthStatus enum

## Phase 7 Implementation Steps

### Step 1: Add Internet Permission
**File:** AndroidManifest.xml
- Add: `<uses-permission android:name="android.permission.INTERNET" />`

### Step 2: Create Backend DTOs
**New File:** network/AutoRescueApi.kt
- AutoRescueCheckRequest (maps to backend JSON)
- AutoRescueCheckResponse (maps from backend JSON)
- Nested DTOs: DiagnosisDto, ServiceCentreDto, RescueDto

**Key Mapping:**
```
VehicleTelemetry (Android - simplified)
→ AutoRescueCheckRequest (backend - detailed tyres)

Individual tyres in request:
- front_left_tyre_psi
- front_right_tyre_psi
- rear_left_tyre_psi
- rear_right_tyre_psi
```

### Step 3: Create Retrofit API Interface
**New File:** network/AutoRescueService.kt
- POST /api/autorescue/check endpoint
- Async suspend function
- Exception handling

### Step 4: Configure Backend Base URL
**New File:** network/NetworkConfig.kt
- DEBUG: http://127.0.0.1:8000/ (with ADB reverse)
- or LAN: http://<LAPTOP_IP>:8000/
- Uses BuildConfig.DEBUG

### Step 5: Create Network Client
**File:** network/NetworkClient.kt or extend existing
- OkHttp with timeouts (10s connect, 120s read, 130s total)
- Logging interceptor for DEBUG
- Moshi JSON converter

### Step 6: Create AutoRescueRepository
**New File:** repository/AutoRescueRepository.kt
- Calls Retrofit service
- Handles errors: connection refused, timeout, 4xx, 5xx
- Returns Result<T> wrapper
- NO silent exception swallowing

### Step 7: Create Telemetry Models for Backend
**Update/New File:** model/BackendTelemetry.kt or extend VehicleTelemetry
- Expand to 4 individual tyre pressures
- Provide default values from VehicleTelemetry

### Step 8: Update DiagnosticsViewModel
**File:** viewmodel/DiagnosticsViewModel.kt
- Replace DiagnosticEngine call with backend call
- Inject AutoRescueRepository
- Add error states
- Map backend response to UI state
- Adapt progress messages

### Step 9: Handle Backend Response Status
**Logic in ViewModel:**
- `status == "HEALTHY"` → show green UI
- `status == "SERVICE_RECOMMENDED"` → show warning + service centres
- `status == "ASSISTANCE_REQUIRED"` → show critical + rescue

### Step 10: Create Debug Telemetry Modes
**New File:** network/DebugTelemetryProvider.kt
- Mode: HEALTHY (all normal)
- Mode: WARNING (tyre low or similar)
- Mode: CRITICAL (engine hot)
- Accessible in DEBUG builds

### Step 11: Update DiagnoseScreen
- Display backend diagnosis (already mostly compatible)
- Show service centres from backend response
- Handle navigation_allowed flag for Maps
- Show rescue details when status is ASSISTANCE_REQUIRED

### Step 12: Update HomeScreen
- Show status from latest backend check result
- Persist check result in ViewModel state

### Step 13: Verify AndroidManifest
- INTERNET permission ✓
- ACCESS_FINE_LOCATION ✓
- ACCESS_COARSE_LOCATION ✓
- POST_NOTIFICATIONS (already there)

### Step 14: Build & Test
- `gradlew assembleDebug`
- Fix all compile errors
- Test on physical device with ADB reverse

## Files to Create

1. `network/AutoRescueApi.kt` — DTOs for backend communication
2. `network/AutoRescueService.kt` — Retrofit API interface
3. `network/NetworkConfig.kt` — Backend URL configuration
4. `network/NetworkClient.kt` or update existing — OkHttp client
5. `repository/AutoRescueRepository.kt` — Backend communication wrapper
6. `network/DebugTelemetryProvider.kt` — Demo scenarios

## Files to Modify

1. `AndroidManifest.xml` — Add INTERNET permission
2. `viewmodel/DiagnosticsViewModel.kt` — Use backend, not local engine
3. `ui/screens/DiagnoseScreen.kt` — Display backend data
4. `model/VehicleTelemetry.kt` — Optionally expand to 4 tyres
5. `build.gradle.kts` — Optionally adjust timeouts

## Files NOT to Modify

- MainActivity
- Navigation structure
- UI theme colors
- Compose Material 3 setup
- LocationViewModel
- LocationRepository
- ServiceCentreRanker (if not directly integrated)
- DiagnosticEngine (not called anymore, can stay)

## Testing Scenarios

### Test 1: HEALTHY
- Backend: All metrics normal
- Expected: Green UI, "Vehicle Healthy" message
- Android flow: GPS → telemetry → POST → response → UI

### Test 2: SERVICE_RECOMMENDED (Tyre Warning)
- Backend: Tyre pressure warning
- Expected: Yellow UI, service centres shown
- Android flow: Same, but with centres displayed

### Test 3: ASSISTANCE_REQUIRED (Engine Critical)
- Backend: Engine overheating, safe_to_drive=false
- Expected: Red UI, "NOT SAFE TO DRIVE", rescue shown
- Android flow: Same, plus NOT SAFE TO DRIVE indicator

## Backend Contract Confirmation

POST http://127.0.0.1:8000/api/autorescue/check

**Request JSON:**
```json
{
  "vehicle_id": "TN37AB1234",
  "engine_temperature": 95,
  "battery_voltage": 12.7,
  "front_left_tyre_psi": 32,
  "front_right_tyre_psi": 32,
  "rear_left_tyre_psi": 31,
  "rear_right_tyre_psi": 31,
  "coolant_level": 75,
  "latitude": 11.0168,
  "longitude": 76.9558
}
```

**Response JSON:**
```json
{
  "request_id": "...",
  "vehicle_id": "...",
  "status": "HEALTHY|SERVICE_RECOMMENDED|ASSISTANCE_REQUIRED",
  "diagnosis": {...},
  "service_centres": [...],
  "navigation_allowed": true|false,
  "rescue": null|{...},
  "message": "..."
}
```

## Key Design Decisions

1. **Reuse existing LocationViewModel** — Don't create another GPS implementation
2. **Reuse existing Retrofit/OkHttp** — Already configured
3. **Extend TelemetryRepository or create new** — Keep demo data provider
4. **DEBUG build support for ADB reverse** — Easy localhost testing
5. **Keep UI screens mostly unchanged** — Just update data binding
6. **No database persistence yet** — In-memory ViewModel state
7. **No vehicle telemetry from OBD-II yet** — Demo values still used
8. **Navigation_allowed flag controls UI** — Safety-first design

## Success Criteria

- [ ] Android builds without errors
- [ ] HEALTHY scenario returns green UI
- [ ] WARNING scenario shows service centres from OSM
- [ ] CRITICAL scenario shows NOT SAFE TO DRIVE + rescue
- [ ] GPS provides real latitude/longitude
- [ ] Backend URL configurable per BUILD type
- [ ] All existing features still work
- [ ] No crashes, proper error handling
- [ ] Timeouts handled gracefully

## Deliverable

A fully functional Android app that:
1. Collects telemetry (demo) + GPS (real)
2. POSTs to backend /api/autorescue/check
3. Displays unified backend response
4. Handles all three status types correctly
5. Respects navigation_allowed flag
6. Builds without errors on DEBUG
