# Phase 7B Inspection Report — Old Mock UI & Implementation Plan

## 1. Mock Content Location Summary

### 1.1 Fake Rescue Data Location
**File:** `app/src/main/java/com/example/model/VehicleModels.kt`  
**Lines:** 45–55

**RescueRequestStatus data class with hardcoded defaults:**
- `providerName: String = "AutoRescue Swift Patrol #402"`
- `statusMessage: String = "Rescue Unit Dispatched!"`
- `estimatedArrival: String = "14 mins"`
- `driverName: String = "Ramesh Kumar"`
- `driverPhone: String = "+91 98765 01234"`
- `location: String = "Coimbatore, Tamil Nadu"`

### 1.2 Rescue Status Update Location
**File:** `app/src/main/java/com/example/viewmodel/VehicleViewModel.kt`  
**Lines:** 274–284 (requestAssistance method)

**Hardcoded values set when user requests assistance:**
- `statusMessage = "Rescue Unit Dispatched!"`
- `estimatedArrival = "14 mins"`

### 1.3 Fake Rescue UI Display
**File:** `app/src/main/java/com/example/ui/screens/RescueScreen.kt`  
**Lines:** 365–512 (Mock Assistance Status Card)

**Components shown:**
- `rescueStatus.statusMessage` → displays "Rescue Unit Dispatched!"
- `rescueStatus.providerName` → displays "AutoRescue Swift Patrol #402"
- `rescueStatus.estimatedArrival` → displays "14 mins"
- `rescueStatus.driverName` → displays "Ramesh Kumar"
- `StatusBadge` with "EN ROUTE"
- "Assigned Technician" label
- "Estimated Arrival" label with "14 mins"

### 1.4 Places API Key Missing Error
**File:** `app/src/main/java/com/example/repository/PlacesServiceRepository.kt`  
**Lines:** 59–72 (getNearbyServiceCentres method)

**Error message returned:**
```
"Places API key is missing or not configured. Set PLACES_API_KEY in AI Studio secrets."
```

**Display location:** `app/src/main/java/com/example/ui/components/NearbyServiceCentresCard.kt`  
**Lines:** 191–277 (Error state handling)

**When Places API key check fails:**
- Error type: `ServiceCentreErrorType.PlacesKeyMissing`
- Error title: "Places API Key Missing"
- Error message: The text from PlacesServiceRepository
- Button label: "Retry Key Check"

### 1.5 Google Places Attribution
**File:** `app/src/main/java/com/example/ui/components/NearbyServiceCentresCard.kt`  
**Lines:** 345–365

**Attribution footer shown in success state:**
```kotlin
Text("Search results provided by Google Places")
```

---

## 2. Current Architecture Issues

### 2.1 ViewModels Not Sharing Backend Response
- **DiagnosticsViewModel** has new backend integration but stores response only locally
- **VehicleViewModel** still uses old mock data and DiagnosticEngine
- **RescueScreen** depends on VehicleViewModel.rescueStatus (all mock)
- **HomeScreen** depends on VehicleViewModel.vehicleInfo (hardcoded)
- **DiagnoseScreen** depends on VehicleViewModel.componentHealthList (local calculation, not backend)

### 2.2 Places Dependency Still Required for AutoRescue Flow
- NearbyServiceCentresCard requires PLACES_API_KEY even when backend provides service centres
- Backend response includes serviceCentres array from OSM/Overpass
- Android still calls PlacesServiceRepository instead of using backend response
- Error card appears blocking the AutoRescue workflow

### 2.3 Fake Rescue Still Displayed
- RescueScreen shows "Rescue Unit Dispatched" immediately after user selects option
- No real dispatch system exists
- ETA is hardcoded "14 mins"
- Technician name is hardcoded "Ramesh Kumar"
- Service option is not sent to backend

---

## 3. Required Changes

### 3.1 DiagnosticsViewModel Updates
**Goal:** Make backend response accessible to all screens

**Changes needed:**
1. Keep existing DiagnosticsViewModel structure (already complete from Phase 7)
2. Extend DiagnosticsState to expose full response
3. Provide DiagnosticsViewModel to other screens via shared ViewModel injection
4. Ensure latest result persists when navigating between screens

### 3.2 RescueScreen Rewrite
**Goal:** Remove fake dispatch, show backend recommendation or empty state

**Current:** Shows fake "Rescue Unit Dispatched!" card after user selects option  
**New:** Display backend rescue recommendation from DiagnosticsViewModel.diagnosticState.backendResponse.rescue

**States:**
- No check performed: "No vehicle check result available"
- HEALTHY status: "No roadside assistance required"
- SERVICE_RECOMMENDED: "Service inspection recommended" (no rescue)
- ASSISTANCE_REQUIRED: Show backend rescue data or empty state

**Remove:**
- Manual "Request Assistance" button behavior that sets hardcoded statusMessage
- Fake "Rescue Unit Dispatched!" card (lines 365–512)
- Fake ETA display
- Fake technician name display
- rescueStatus.isRequested state propagation

**Keep:**
- Manual rescue category selection (6 options)
- Location card
- Service centres card
- Cancel/Retry functionality (but as state cleanup, not provider cancellation)

### 3.3 HomeScreen Updates
**Goal:** Show latest backend vehicle check status

**Current:** Hardcoded "Your vehicle is currently healthy"  
**New:** Derive from DiagnosticsViewModel.diagnosticState.backendResponse.status

**Mappings:**
- No check: Show default/neutral state
- HEALTHY: "Vehicle Healthy" with green badge
- SERVICE_RECOMMENDED: "Attention Required" with yellow badge
- ASSISTANCE_REQUIRED: "Critical Issue — NOT SAFE TO DRIVE" with red badge

### 3.4 DiagnoseScreen Updates
**Goal:** Display backend service centres instead of Places results

**Current:** Uses VehicleViewModel.serviceCentresState (comes from Places)  
**New:** Use DiagnosticsViewModel.diagnosticState.backendResponse.serviceCentres

**Behavior:**
- Show backend service centres list if status is SERVICE_RECOMMENDED or ASSISTANCE_REQUIRED
- Do NOT call PlacesServiceRepository
- Do NOT show "Places API Key Missing" error
- Use backend centre data: name, address, distance_km, priority_score, recommendation_reason
- Respect navigationAllowed flag from backend

### 3.5 Remove Places Requirement from AutoRescue Flow
**Goal:** Backend service centres used instead of Google Places

**Changes:**
- Do NOT modify PlacesServiceRepository (leave for other features)
- Do NOT ask for PLACES_API_KEY for AutoRescue flow
- NearbyServiceCentresCard used only for Places-backed searches (optional feature)
- New component OR modified usage for backend service centres

**Option A (Recommended):** Create separate ServiceCentresDisplay component for backend results  
**Option B:** Extend NearbyServiceCentresCard to accept backend centre list

### 3.6 Navigation & State Persistence
**Goal:** All screens access same latest result without re-calling backend

**Implementation:**
- DiagnosticsViewModel scoped to activity or navigation graph
- All screens injected with same ViewModel instance
- Navigation between screens preserves result
- Result persists until next "Run Vehicle Check" button tap

---

## 4. Existing Code to Preserve

✅ DiagnosticsViewModel (already implements backend call)  
✅ AutoRescueRepository (already handles network)  
✅ AutoRescueCheckResponse DTOs (already complete)  
✅ NetworkConfig (already configured with timeouts)  
✅ TelemetryRepository (demo telemetry)  
✅ LocationViewModel (real GPS)  
✅ Component health list display logic (reusable)  
✅ Manual rescue category selection UI  
✅ Location card display  
✅ Profile/Notifications navigation  

---

## 5. Files to Modify

| File | Changes | Priority |
|------|---------|----------|
| DiagnosticsViewModel | Extend state exposure | HIGH |
| RescueScreen | Remove fake dispatch, use backend | HIGH |
| HomeScreen | Use latest backend status | HIGH |
| DiagnoseScreen | Use backend service centres | HIGH |
| VehicleViewModel | Keep for non-backend vehicle info | MEDIUM |
| NearbyServiceCentresCard | Optional: add backend centre support | LOW |
| MainActivity/NavHost | Ensure ViewModel sharing | HIGH |

---

## 6. New Files to Create (Optional)

- ServiceCentresDisplay.kt (if separate component needed for backend centres)
- DebugScenarioSelector.kt (if DEBUG test mode added)

---

## 7. Testing Scenarios

After implementation, test with real phone:

1. **HEALTHY Check**
   - Home shows "Vehicle Healthy"
   - Diagnose shows no issues
   - Rescue shows empty/no assistance needed

2. **SERVICE_RECOMMENDED Check**
   - Home shows "Attention Required"
   - Diagnose shows issue + backend service centres (OSM results)
   - NO "Places API Key Missing" error
   - Rescue shows empty state

3. **ASSISTANCE_REQUIRED Check**
   - Home shows "Critical — NOT SAFE TO DRIVE"
   - Diagnose shows issue + service centres + safety warning
   - Rescue shows backend rescue recommendation (type, priority, ETA with "Demo estimate" label)
   - NO fake "Rescue Unit Dispatched" card
   - NO fake technician name

---

## 8. Success Criteria

- ✅ Build passes: `.\gradlew.bat assembleDebug`
- ✅ No "Places API Key Missing" in AutoRescue flow
- ✅ No "Rescue Unit Dispatched!" without real provider
- ✅ No "Ramesh Kumar" or fake technician names
- ✅ No hardcoded "14 mins" presented as real
- ✅ Backend response used for all decisions
- ✅ Service centres from backend (OSM), not Places
- ✅ Real GPS used in all checks
- ✅ Demo telemetry labeled as such
- ✅ All three scenarios work on physical device
- ✅ Navigation between screens preserves result

---

## 9. Implementation Order

1. Update MainActivity/NavHost for ViewModel sharing
2. Extend DiagnosticsViewModel state if needed
3. Update RescueScreen (remove fake dispatch)
4. Update HomeScreen (use backend status)
5. Update DiagnoseScreen (use backend centres)
6. Add DEBUG scenario selector (optional)
7. Build and test
