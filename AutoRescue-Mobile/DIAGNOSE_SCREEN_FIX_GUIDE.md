# Diagnose Screen — Missing UI Fix Guide

## Issue

On physical phone, tapping "Diagnose" tab shows only location detection, with NO:
- Run Vehicle Check button
- Vehicle telemetry section
- Demo scenario selector
- Backend loading state
- Diagnosis result

## Root Cause Investigation

### Step 1: Verify You're On DiagnoseScreen

**NEW DEBUG LABEL ADDED:**

After updating the APK, the header should show:

```
Vehicle Diagnostics — DEBUG: DiagnoseScreen Active
✓ This is DiagnoseScreen
```

If you see this after tapping Diagnose:
- ✅ You're on the correct screen
- UI layout issue (missing content below location)
- Issue is NOT navigation

If you DON'T see this:
- ❌ Navigation is broken OR
- ❌ Wrong screen is being shown
- Navigation issue (check routing)

---

### Step 2: What Each Tab Should Show

| Tab | Expected Screen | Expected Content |
|-----|---|---|
| Home | HomeScreen | Vehicle card, health %, quick actions |
| **Diagnose** | **DiagnoseScreen** | **✓ This is DiagnoseScreen**, Component Health, **RUN VEHICLE CHECK**, Results |
| Rescue | RescueScreen | Location card, rescue options, assistance status |
| Vehicle | VehicleScreen | Vehicle details, component list |

---

## Installation & Testing

### 1. Install New APK with Debug Label

```powershell
cd "C:\Users\Jayanth\Downloads\AutoRescueAI\AutoRescue-Mobile"

# Uninstall old version
adb uninstall com.example

# Install new version
adb install -r "app\build\outputs\apk\debug\app-debug.apk"
```

### 2. Launch App

```powershell
adb shell am start -n com.example/.MainActivity
```

### 3. Tap "Diagnose" Tab

Observe what's displayed on the phone screen.

---

## Diagnosis Table

### Case A: You See "✓ This is DiagnoseScreen"

**Diagnosis:** ✅ Navigation works, DiagnoseScreen IS displaying

**Next Steps:**
1. Scroll up on the screen
2. Are there items above the location card?
3. Can you scroll down?
4. Is there a "Run Vehicle Check" button below?

**If Yes (content exists but scrolled):**
- Layout is fine, user just needs to scroll
- Content IS there, just not visible without scrolling

**If No (truly blank):**
- Check for LaunchedEffect that might be hiding content
- Check for Modifier.fillMaxSize() that might be consuming space

---

### Case B: You DON'T See "✓ This is DiagnoseScreen"

**Diagnosis:** ❌ Navigation broken OR wrong screen rendering

**Possible Causes:**

1. **Diagnose tab is navigating to wrong screen**
   - Check: Screen.Diagnose.route value
   - Check: NavHost routing for "diagnose"

2. **Bottom navigation is broken**
   - Check: AutoRescueBottomBar implementation
   - Check: onNavigateToRoute callback

3. **Diagnose tab doesn't exist**
   - Check: bottomNavScreens list in Screen.kt
   - Check: Diagnose route definition

**Fix Steps:**
- Verify Screen.Diagnose in Screen.kt:
  ```kotlin
  object Diagnose : Screen("diagnose", "Diagnose", ...)
  ```
- Verify NavHost in AutoRescueNavGraph.kt:
  ```kotlin
  composable(Screen.Diagnose.route) {
      DiagnoseScreen(...)
  }
  ```
- Verify bottomNavScreens includes Diagnose

---

## What Should Be Visible (Actual Layout)

After you tap Diagnose and the APK updates, here's the expected hierarchy:

```
[AutoRescueHeader]
  Vehicle Diagnostics — DEBUG: DiagnoseScreen Active

[LazyColumn Content - scrollable]
  ✓ This is DiagnoseScreen (debug label)
  
  [Header Description Card]
    Real-Time Health Metrics
    OBD-II live telemetry from 18 vehicle sensors.
  
  [Component Health Scores Card]
    Engine      94%  ✓ HEALTHY
    Battery     88%  ✓ HEALTHY
    Tyres       72%  ⚠ WARNING
    Coolant     91%  ✓ HEALTHY
    Brakes      95%  ✓ HEALTHY
  
  [Run Vehicle Check Button]
    ✓ "Run Vehicle Check" (large button)
  
  [Loading Animation - if checking]
    (shows progress bar with message)
  
  [Results Card - if check completed]
    Diagnostic Summary
    Issue Detected
    Affected Component
    etc.
```

---

## Scroll Test

The entire screen is in a **LazyColumn** which means it MUST be scrollable:

1. Tap "Diagnose"
2. Try to scroll UP with finger
3. Try to scroll DOWN with finger

If nothing scrolls, that's a layout issue (height constraint problem).

---

## If Still Seeing Only Location (Case B)

This likely means you're on the **RescueScreen**, not DiagnoseScreen.

RescueScreen shows:
- Location card at top ("Acquiring GPS Location...")
- Rescue options
- Service centres

**But NOT:**
- Run Vehicle Check button
- Component Health Scores

If this is what you see, the issue is:
- Diagnose tab is not connected to DiagnoseScreen
- Diagnose route is pointing to wrong composable
- Navigation is using old route definition

**Fix:**
1. Check AutoRescueNavGraph.kt line 120-127
2. Verify `composable(Screen.Diagnose.route)` calls `DiagnoseScreen(...)`
3. Check Screen.kt — Diagnose route must be "diagnose"

---

## Build & Reinstall Steps

```powershell
# 1. Clean build
cd "C:\Users\Jayanth\Downloads\AutoRescueAI\AutoRescue-Mobile"
.\gradlew.bat clean

# 2. Build fresh APK
.\gradlew.bat assembleDebug

# 3. Expected output
# BUILD SUCCESSFUL

# 4. Uninstall old version
adb uninstall com.example

# 5. Install new APK
adb install -r "app\build\outputs\apk\debug\app-debug.apk"

# 6. Launch
adb shell am start -n com.example/.MainActivity

# 7. Wait for app to fully load (~3 seconds)

# 8. Tap Diagnose tab

# 9. Report what you see
```

---

## Report Format

After installing and testing, report EXACTLY what you see:

```
DIAGNOSE TAB SHOWS:
[ ] Debug label "✓ This is DiagnoseScreen" visible
[ ] Header card with "Real-Time Health Metrics"
[ ] Component Health Scores card
[ ] "Run Vehicle Check" button
[ ] Scrollable (can swipe up/down)
[ ] Only location card visible
[ ] Other: ___________

After scrolling DOWN:
[ ] Run Vehicle Check button appears
[ ] More content below
[ ] Nothing - hits bottom immediately
[ ] Can't scroll

DEBUG LABEL TEXT:
If visible, what exact text do you see in the header?
(copy/paste the exact text from the header)
```

---

## Quick Checklist

After installing the updated APK:

- [ ] Tap Diagnose tab
- [ ] Look for "✓ This is DiagnoseScreen" debug label
- [ ] If visible: scroll through the page
- [ ] If not visible: try other tabs to confirm navigation works
- [ ] Report findings above

---

## Summary

The new APK includes:

1. **Debug label** at top of DiagnoseScreen
2. **Continued debug logging** in run Vehicle Check flow
3. **Same UI structure** as before (LazyColumn with items)

If you see the debug label → navigation and screen ARE working  
If you DON'T see it → navigation/routing issue

Let me know what you observe!
