# Debug Trace: Run Vehicle Check Flow

## Logging Added

Comprehensive debug logging has been added at each step of the call chain:

```
1 BUTTON CLICKED          ← DiagnoseScreen button onClick
2 VIEWMODEL CALLED        ← DiagnosticsViewModel.runVehicleCheck() entry
3 REQUESTING LOCATION     ← LocationViewModel access attempt
4 LOCATION RECEIVED       ← GPS coordinates obtained
5 CALLING REPOSITORY      ← AutoRescueRepository invoked
6 CALLING FASTAPI         ← Retrofit POST request
6A BASE_URL               ← Backend URL verification
6B CALLING RETROFIT       ← Network call begins
7 RESPONSE RECEIVED       ← Backend response received
8 UI STATE UPDATED        ← ViewModel state updated, UI will re-render
```

Additional error logs will show if:
- Location is null/unavailable
- Network connection fails
- HTTP errors occur
- Unexpected exceptions

---

## Step-by-Step Testing

### Prerequisites

1. **Backend Running**
   ```powershell
   cd C:\Users\Jayanth\Downloads\AutoRescueAI\AutoRescue-Backend
   .\run_all_agents.ps1
   ```
   Should show:
   ```
   READY: FastAPI Gateway :8000
   ```

2. **Phone/Emulator**
   - USB debugging enabled
   - Connected via ADB

3. **ADB Reverse Configured**
   ```powershell
   adb devices  # Verify connection
   adb reverse tcp:8000 tcp:8000  # Forward port
   ```

4. **APK Built**
   - New APK from this session with debug logs

---

### Installation

```powershell
cd "C:\Users\Jayanth\Downloads\AutoRescueAI\AutoRescue-Mobile"

# Uninstall old version (if needed)
adb uninstall com.example

# Install new APK with debug logs
adb install -r "app\build\outputs\apk\debug\app-debug.apk"

# Wait for installation to complete
```

---

### Clear Logs

**Important:** Clear existing logs before testing so you only see output from this test run.

```powershell
adb logcat -c
```

---

### Run the Test

1. **Launch the app on phone**
   ```powershell
   adb shell am start -n com.example/.MainActivity
   ```

2. **Navigate to Diagnose screen** (if not already there)

3. **Tap "Run Vehicle Check" button**
   - Should see loading animation
   - Progress text: "Initializing...", "Fetching telemetry...", "Getting GPS...", "Connecting to backend..."

4. **Wait 5-10 seconds**

5. **Open a new PowerShell window and run:**
   ```powershell
   & "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" logcat -d | Select-String "AutoRescueDebug"
   ```

---

### Reading the Output

The logcat output will show a sequence like:

**Expected Success Flow:**
```
I  1 BUTTON CLICKED - DiagnoseScreen
I  2 VIEWMODEL CALLED - DiagnosticsViewModel.runVehicleCheck()
I  Getting demo telemetry...
I  Telemetry: engine=98.0°C, battery=12.5V
I  3 REQUESTING LOCATION from LocationViewModel
I  4 LOCATION RECEIVED lat=11.1234 lon=76.5678
I  5 CALLING REPOSITORY
I  6 REPOSITORY CALLED - building request
I  6A BASE URL = http://127.0.0.1:8000/
I  6B CALLING RETROFIT POST /api/autorescue/check
I  7 RESPONSE RECEIVED status=HEALTHY
I  8 UI STATE UPDATED with backend response
```

---

### Failure Scenarios

#### Scenario A: Button Not Triggering ViewModel

**Log Output:**
```
I  1 BUTTON CLICKED - DiagnoseScreen
(nothing after this)
```

**Diagnosis:** 
- Button is not calling `diagnosticsViewModel.runVehicleCheck()`
- May be calling old local method instead
- Check DiagnoseScreen button onClick handler

**Fix:**
- Verify button has `onClick = { diagnosticsViewModel.runVehicleCheck() }`

---

#### Scenario B: ViewModel Called but No Location

**Log Output:**
```
I  1 BUTTON CLICKED - DiagnoseScreen
I  2 VIEWMODEL CALLED - DiagnosticsViewModel.runVehicleCheck()
I  Getting demo telemetry...
I  Telemetry: engine=98.0°C, battery=12.5V
I  3 REQUESTING LOCATION from LocationViewModel
I  Using fallback coordinates - LocationViewModel may not have provided real GPS
(no "4 LOCATION RECEIVED")
```

**Diagnosis:**
- LocationViewModel is not providing real GPS
- Using fallback coordinates (11.0168, 76.9558)

**Solutions:**
1. Ensure location permission is granted on phone
2. Enable GPS on device
3. Ensure location services are enabled
4. May need to wait for GPS lock (can take 10-30 seconds)

**Note:** Fallback coordinates are still valid for backend testing; the backend will work, just with demo coordinates instead of real GPS.

---

#### Scenario C: Repository Called but Network Fails

**Log Output:**
```
I  1 BUTTON CLICKED - DiagnoseScreen
I  2 VIEWMODEL CALLED - DiagnosticsViewModel.runVehicleCheck()
I  Getting demo telemetry...
I  Telemetry: engine=98.0°C, battery=12.5V
I  3 REQUESTING LOCATION from LocationViewModel
I  4 LOCATION RECEIVED lat=11.1234 lon=76.5678
I  5 CALLING REPOSITORY
I  6 REPOSITORY CALLED - building request
I  6A BASE URL = http://127.0.0.1:8000/
I  6B CALLING RETROFIT POST /api/autorescue/check
E  NETWORK ERROR: Connection refused - Connection refused
```

**Diagnosis:**
- Backend is NOT running or not accessible
- ADB reverse may not be configured

**Solutions:**
1. Verify backend is running:
   ```powershell
   cd AutoRescue-Backend
   .\run_all_agents.ps1
   # Wait for "READY: FastAPI Gateway :8000"
   ```

2. Verify ADB reverse:
   ```powershell
   adb reverse --list  # Should show: tcp:8000 tcp:8000
   
   # If not, re-run:
   adb reverse tcp:8000 tcp:8000
   ```

3. Test connection from phone:
   ```powershell
   adb shell ping 127.0.0.1  # May fail on some devices (expected)
   # The reverse tunnel should still work for app traffic
   ```

---

#### Scenario D: HTTP Error from Backend

**Log Output:**
```
I  1 BUTTON CLICKED - DiagnoseScreen
I  2 VIEWMODEL CALLED - DiagnosticsViewModel.runVehicleCheck()
I  Getting demo telemetry...
I  Telemetry: engine=98.0°C, battery=12.5V
I  3 REQUESTING LOCATION from LocationViewModel
I  4 LOCATION RECEIVED lat=11.1234 lon=76.5678
I  5 CALLING REPOSITORY
I  6 REPOSITORY CALLED - building request
I  6A BASE URL = http://127.0.0.1:8000/
I  6B CALLING RETROFIT POST /api/autorescue/check
E  HTTP ERROR 400: Bad Request
E  BACKEND ERROR: Invalid request data
```

**Diagnosis:**
- Backend received the request but rejected it
- Request format is incorrect
- Field mapping issue between Android DTOs and backend schema

**Solutions:**
1. Check backend logs for detailed error
2. Verify AutoRescueCheckRequest fields match backend expectations
3. Verify @Json annotations in AutoRescueApi.kt match field names

---

#### Scenario E: Response Received but UI Doesn't Update

**Log Output:**
```
I  1 BUTTON CLICKED - DiagnoseScreen
I  2 VIEWMODEL CALLED - DiagnosticsViewModel.runVehicleCheck()
I  Getting demo telemetry...
I  Telemetry: engine=98.0°C, battery=12.5V
I  3 REQUESTING LOCATION from LocationViewModel
I  4 LOCATION RECEIVED lat=11.1234 lon=76.5678
I  5 CALLING REPOSITORY
I  6 REPOSITORY CALLED - building request
I  6A BASE URL = http://127.0.0.1:8000/
I  6B CALLING RETROFIT POST /api/autorescue/check
I  7 RESPONSE RECEIVED status=HEALTHY
I  8 UI STATE UPDATED with backend response
(but UI still shows loading animation or blank)
```

**Diagnosis:**
- Backend response received and state updated
- UI not responding to state changes
- Likely issue with Compose recomposition

**Solutions:**
1. Check if DiagnoseScreen subscribed to correct StateFlow
2. Verify `by diagnosticsViewModel.diagnosticState.collectAsState()`
3. May need to manually trigger recomposition
4. Try closing and re-opening the app

---

### Complete Logcat Capture

To capture the full session for analysis:

```powershell
# Clear logs
adb logcat -c

# Tap the button, wait 10 seconds

# Capture all logs
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" logcat -d > C:\Users\Jayanth\Downloads\AutoRescueDebug.log

# View the file
notepad C:\Users\Jayanth\Downloads\AutoRescueDebug.log

# Filter by AutoRescueDebug tags only
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" logcat -d -s "AutoRescueDebug" > C:\Users\Jayanth\Downloads\AutoRescueDebug-Filtered.log
```

---

### Expected Happy Path (All Green)

If everything works:

1. ✅ Button clicks (log 1)
2. ✅ ViewModel starts (log 2)
3. ✅ Telemetry fetched
4. ✅ Location obtained (log 3-4)
5. ✅ Repository called (log 5)
6. ✅ Base URL verified (log 6A)
7. ✅ Retrofit request sent (log 6B)
8. ✅ Backend responds (log 7)
9. ✅ UI state updated (log 8)
10. ✅ DiagnoseScreen shows result
11. ✅ HomeScreen updates to latest status
12. ✅ RescueScreen shows backend recommendation

---

## Critical Checks

### 1. Backend Endpoint

The APK is trying to reach:
```
POST http://127.0.0.1:8000/api/autorescue/check
```

Verify backend is listening:
```powershell
# From laptop terminal where backend runs
# Should show active connections to 8000
netstat -ano | findstr :8000

# Or check backend logs for "POST /api/autorescue/check"
```

### 2. ADB Reverse

The phone CANNOT directly access laptop IP. It must use the reverse tunnel:
```powershell
adb reverse tcp:8000 tcp:8000

# Verify it's active
adb reverse --list
```

### 3. Request Format

The Android DTO must serialize correctly:
```kotlin
AutoRescueCheckRequest(
    vehicleId = "TN37AB1234",
    engineTemperature = 98.0,
    batteryVoltage = 12.5,
    frontLeftTyrePsi = 32.0,
    frontRightTyrePsi = 32.0,
    rearLeftTyrePsi = 32.0,
    rearRightTyrePsi = 32.0,
    coolantLevel = 75.0,
    latitude = 11.1234,
    longitude = 76.5678
)
```

Should send JSON matching backend schema exactly.

---

## After Debugging

Once you've traced where it stops and fixed the issue:

1. Remove debug logs (optional, they don't hurt in debug builds)
2. Rebuild: `.\gradlew.bat assembleDebug`
3. Reinstall: `adb install -r app-debug.apk`
4. Test again

If the flow completes to log 8 but UI doesn't update, the issue is in the Compose layer (separate from networking).

---

## Contact Points

**If logs show:**
- ❌ Stops at "1 BUTTON CLICKED" → Check DiagnoseScreen button handler
- ❌ Stops at "2 VIEWMODEL CALLED" → Check ViewModel runVehicleCheck method
- ❌ Stops at "3 REQUESTING LOCATION" → Check LocationViewModel injection
- ❌ Stops at "5 CALLING REPOSITORY" → Check AutoRescueRepository injection
- ❌ Stops at "6B CALLING RETROFIT" → Check NetworkConfig/Retrofit setup
- ❌ Stops before "7 RESPONSE RECEIVED" → Check network/backend availability
- ✅ Gets to "8 UI STATE UPDATED" → Network works, UI issue

---

## Quick Summary

Run these commands in order:

```powershell
# 1. Clear logs
adb logcat -c

# 2. Tap "Run Vehicle Check" button on phone (once)

# 3. Wait 10 seconds

# 4. View debug output
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" logcat -d | Select-String "AutoRescueDebug"

# 5. Look for what's MISSING from the sequence
# (compares to expected sequence above)
```

That's it. The logs will tell us exactly where it stops.
