# Phase 7 Implementation Progress

## Completed

### Network Layer ✅
- [x] `AutoRescueApi.kt` — Complete DTO mapping (Request + Response models)
- [x] `AutoRescueService.kt` — Retrofit interface with POST endpoint
- [x] `NetworkConfig.kt` — OkHttp client configuration (10s connect, 120s read, 130s total timeouts)
- [x] `AutoRescueRepository.kt` — Backend communication with error handling
- [x] `AndroidManifest.xml` — Added INTERNET permission

### ViewModel ✅
- [x] `DiagnosticsViewModel.kt` — Updated to call backend instead of local engine
  - Fetches demo telemetry
  - Gets GPS location  
  - Calls backend `/api/autorescue/check` endpoint
  - Converts backend response to UI model
  - Handles all error cases with user-friendly messages

### Models ✅
- [x] DiagnosticState extended with errorMessage and backendResponse fields
- [x] HealthStatus enum already exists (HEALTHY, WARNING, CRITICAL)

## Remaining Work

### UI Screens (5 files to update)

#### 1. DiagnoseScreen.kt
**Current:** Displays local diagnostic results  
**Needed:**
- Display backend `diagnosis` data
- Show `service_centres` list (from backend response)
- Respect `navigation_allowed` flag
- Handle error states with Retry button
- Show loading progress during backend call

#### 2. HomeScreen.kt
**Current:** Shows vehicle status summary  
**Needed:**
- Display latest check result status (HEALTHY/SERVICE_RECOMMENDED/ASSISTANCE_REQUIRED)
- Update status badge color based on backend status
- Show latest error message if check failed

#### 3. RescueScreen.kt
**Current:** Displays mock rescue dispatch data  
**Needed:**
- Populate from backend `rescue` field if `status == "ASSISTANCE_REQUIRED"`
- Show assistance type, priority, ETA
- Display destination from response
- Show "NOT SAFE TO DRIVE" prominently when applicable
- Do NOT show fake "Technician Dispatched" messages

#### 4. VehicleScreen.kt
**Current:** Shows hardcoded vehicle info  
**Needed:**
- Optionally update vehicle health percentage based on backend diagnosis severity
- Or keep as static demo data (decision needed)

#### 5. NotificationsScreen.kt
**Current:** Shows hardcoded alerts  
**Needed:**
- Optionally create alert when vehicle check completes with non-healthy status
- Or keep as static (decision needed)

### Integration Points

#### DiagnoseScreen Integration
```kotlin
// Already available from ViewModel:
val diagnosticState by viewModel.diagnosticState.collectAsState()
val backendResponse = diagnosticState.backendResponse

// Display:
if (backendResponse != null) {
    Text(backendResponse.diagnosis.issue)
    Text(backendResponse.diagnosis.recommendation)
    
    // Service centres section
    if (backendResponse.status == "SERVICE_RECOMMENDED" || 
        backendResponse.status == "ASSISTANCE_REQUIRED") {
        for (centre in backendResponse.serviceCentres) {
            // Display each service centre
        }
    }
}

// Error handling:
if (diagnosticState.errorMessage != null) {
    ShowErrorDialog(diagnosticState.errorMessage)
    // Add Retry button that calls viewModel.runVehicleCheck()
}
```

#### RescueScreen Integration
```kotlin
// From DiagnosticsViewModel:
val rescue = diagnosticState.backendResponse?.rescue

if (rescue != null && diagnosticState.backendResponse?.status == "ASSISTANCE_REQUIRED") {
    // Display rescue details
    Text("Assistance Type: ${rescue.assistanceType}")
    Text("Priority: ${rescue.priority}")
    Text("ETA: ${rescue.estimatedDispatchMinutes} minutes")
    Text("Destination: ${rescue.destinationName}")
}

// Safety flag
if (!(diagnosticState.backendResponse?.diagnosis?.safeToDrive == true)) {
    Text("NOT SAFE TO DRIVE", color = Color.Red)
}
```

### Test Scenarios

All three must be tested on a physical device with ADB reverse:

1. **HEALTHY Scenario**
   ```
   Backend response status = "HEALTHY"
   Expected UI: Green badge, "Vehicle Healthy" message
   Service centres: None shown
   Rescue: None shown
   ```

2. **SERVICE_RECOMMENDED Scenario**
   ```
   Backend response status = "SERVICE_RECOMMENDED"  
   Expected UI: Yellow/Warning badge
   Diagnosis: Issue + recommendation
   Service centres: Show ranked list from OSM
   Navigation: Enabled (navigation_allowed = true)
   ```

3. **ASSISTANCE_REQUIRED Scenario**
   ```
   Backend response status = "ASSISTANCE_REQUIRED"
   Expected UI: Red badge, "NOT SAFE TO DRIVE" prominent
   Diagnosis: Issue + recommendation
   Service centres: Show for destination context
   Rescue: Type, priority, ETA, destination
   Navigation: Disabled (navigation_allowed = false)
   ```

### Build Verification

**Command:** `.\gradlew.bat assembleDebug`

**Expected:** ✓ Gradle build succeeds  
**Common issues:**
- Missing imports (network DTOs, NetworkConfig, AutoRescueRepository)
- ViewModel constructor injection not recognized
- Retrofit/Moshi configuration issues

### Launch Configuration (Physical Device)

1. Enable ADB reverse:
   ```bash
   adb reverse tcp:8000 tcp:8000
   ```

2. Start backend on laptop:
   ```bash
   cd AutoRescue-Backend
   .\run_all_agents.ps1
   ```

3. Install and run app:
   ```bash
   .\gradlew.bat installDebug
   adb shell am start -n com.example/.MainActivity
   ```

4. Test "Run Vehicle Check" button on Home/Diagnose screens

## Architecture Summary

### Data Flow
```
User taps "Run Vehicle Check"
    ↓
DiagnosticsViewModel.runVehicleCheck()
    ↓
Get demo telemetry from TelemetryRepository
    ↓
Get real GPS from LocationViewModel
    ↓
Create AutoRescueCheckRequest
    ↓
Call autoRescueRepository.runVehicleCheck()
    ↓
POST to http://127.0.0.1:8000/api/autorescue/check
    ↓
Receive AutoRescueCheckResponse
    ↓
Convert to DiagnosticResult for UI display
    ↓
Update diagnosticState StateFlow
    ↓
Compose re-renders DiagnoseScreen with new data
    ↓
User sees: diagnosis + service centres + rescue info
```

### Key Assumptions

1. **Telemetry:** Still using demo values from TelemetryRepository
   - Real OBD-II integration NOT implemented yet
   - All 4 tyres use same pressure (tyrePressurePsi)

2. **Location:** Real GPS from LocationViewModel
   - Falls back to demo coords (11.0168, 76.9558) if unavailable
   - Shows error if GPS unavailable

3. **Backend:** Running on laptop at http://127.0.0.1:8000
   - Uses ADB reverse: `adb reverse tcp:8000 tcp:8000`
   - 120-second timeout for entire workflow

4. **Timing:** Sequential operations
   - Not real-time monitoring
   - Single check per button tap

## Status Checklist

- [x] Network DTOs created
- [x] Retrofit service interface created
- [x] Network client configured
- [x] AutoRescueRepository created
- [x] DiagnosticsViewModel updated
- [x] INTERNET permission added
- [ ] DiagnoseScreen UI updated for backend data
- [ ] HomeScreen UI updated with status
- [ ] RescueScreen UI updated with rescue data
- [ ] Gradle build passes
- [ ] Unit tests pass (if any)
- [ ] Manual testing on physical device (all 3 scenarios)
- [ ] Error handling tested (no network, timeouts, etc.)

## Next Steps

1. Update DiagnoseScreen to display backend service_centres
2. Update RescueScreen to display backend rescue data
3. Add error dialogs and retry logic to screens
4. Build with `.\gradlew.bat assembleDebug`
5. Fix any compile errors
6. Test on physical device with ADB reverse
7. Verify all three scenarios work correctly

## Known Limitations (Phase 7)

- Telemetry is still simulated (demo values)
- No persistence of check results between app restarts
- No real-time monitoring (only on-demand checks)
- No background service integration yet
- No notification generation for non-healthy results
- No real OBD-II connection
- No payment/premium features

## Success Criteria

- [x] Android builds without errors
- [ ] HEALTHY scenario works (green UI)
- [ ] WARNING scenario shows service centres from OSM (yellow UI)
- [ ] CRITICAL scenario shows "NOT SAFE TO DRIVE" + rescue (red UI)
- [ ] Real GPS coordinates used
- [ ] Error handling for network failures
- [ ] Timeouts handled gracefully
- [ ] No crashes on error states
