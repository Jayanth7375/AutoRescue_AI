# Phase 9 — Real 10-Agent Orchestration

## Current Status
- ✓ Git checkpoint created (4-agent stable state)
- ✓ Root cause identified: Message model mismatch causing FALLBACK
- ✓ Unified request models added to agents/messages.py
- ✓ Telemetry Agent updated to use shared models
- ⏳ 4 more agent files need model fixes
- ⏳ New 10-agent Orchestrator needs implementation
- ⏳ FastAPI endpoint needs real orchestrator integration
- ⏳ Tests need validation against real traces
- ⏳ Android needs extended models + UI components

---

## Implementation Plan

### PHASE 9A — Backend (Real 10-Agent Coordination)

#### Stage 1: Fix Agent Message Models (4 files remaining)
- [ ] Maintenance Agent: Update to use MaintenanceRequest/MaintenanceMessage
- [ ] Notification Agent: Update to use NotificationRequest/NotificationMessage  
- [ ] Explanation Agent: Update to use ExplanationRequest/ExplanationMessage
- [ ] Verification Agent: Update to use VerificationRequest/VerificationMessage

**Status**: Message model unification started
**Blocker**: Need to complete agent file updates
**Next Commit**: "Phase 9 Step 2: Unify all agent message models"

#### Stage 2: Implement True 10-Agent Orchestrator
- [ ] Create new orchestrator_uagent_phase9.py with proper flow
- [ ] Implement sequential workflow:
  1. Telemetry validation
  2. Diagnostic analysis
  3. Safety determination
  4. Maintenance recommendation
  5. Service search (conditional: WARNING+)
  6. Rescue assessment (conditional: CRITICAL)
  7. Notifications generation
  8. AI explanations
  9. Verification checks
  10. Orchestrator coordination
- [ ] Real message passing: use ctx.send_and_receive() for each agent
- [ ] Proper error handling: catch failures, mark as FALLBACK, continue
- [ ] Real agent traces: only mark COMPLETED if agent actually responded
- [ ] Conditional execution: skip Service/Rescue based on severity
- [ ] Merge results: Safety overrides Diagnosis, Verification is final

**Key Logic:**
```
Telemetry → VALIDATES → continues
       → FAILS → return error

Diagnostic → severity={NORMAL, WARNING, CRITICAL}

Safety → (NORMAL=safe) / (WARNING=safe) / (CRITICAL=unsafe)

Maintenance → urgency={ROUTINE, SOON, IMMEDIATE}

Service → IF severity != NORMAL

Rescue → IF CRITICAL or tow_required

Notifications → from all previous results

Explanation → LLM with fallback to deterministic

Verification → reconcile contradictions
```

**Status**: Design ready, implementation pending
**Blocker**: Waiting for Stage 1 completion
**Next Commit**: "Phase 9 Step 3: Implement real 10-agent orchestration"

#### Stage 3: Update FastAPI Endpoint
- [ ] Modify /api/autorescue/check to call new orchestrator
- [ ] Return extended response with all 10 agent results
- [ ] Include agent_trace with COMPLETED/SKIPPED/FALLBACK/FAILED
- [ ] Maintain backward compatibility with existing Android fields

**Status**: Ready to implement after Stage 2
**Next Commit**: "Phase 9 Step 4: Wire FastAPI to 10-agent orchestrator"

#### Stage 4: Test Validation
- [ ] test_gateway.py: 3/3 PASS (HEALTHY, WARNING, CRITICAL)
- [ ] test_multi_agent.py: 4/4 PASS with real traces
- [ ] Verify NO agents show FALLBACK (except Explanation if LLM fails)

**Status**: Tests will be validated after Stage 3
**Expected**: All COMPLETED traces for healthy integration

---

### PHASE 9B — Android (Extended Response Display)

#### Stage 5: Extend Android Models
- [ ] Add TelemetryValidationDTO
- [ ] Add SafetyResultDTO
- [ ] Add MaintenanceResultDTO
- [ ] Add AutoRescueNotificationDTO
- [ ] Add ExplanationResultDTO
- [ ] Add VerificationResultDTO
- [ ] Add AgentTraceEntryDTO
- [ ] Update AutoRescueResponseDTO with new optional fields

**Status**: Pending backend Phase 9A completion

#### Stage 6: Update UI Components
- [ ] DiagnoseScreen: Add Safety + Maintenance + Verification display
- [ ] Create AgentActivityCard: Show all 10 agents with status icons
- [ ] HomeScreen: Display condensed safety summary
- [ ] NotificationsScreen: Use backend notifications
- [ ] Add visual status indicators: ✓ COMPLETED / - SKIPPED / ⚠ FALLBACK / ✗ FAILED

**Status**: Design ready, implementation pending backend completion

#### Stage 7: Build & Test Android
- [ ] ./gradlew.bat clean assembleDebug
- [ ] Manual test: Healthy vehicle
- [ ] Manual test: Warning (tyre)
- [ ] Manual test: Critical (engine)
- [ ] Verify dark/light theme compatibility

**Status**: Pending Stages 5-6 completion

---

## Success Criteria

### Backend (Phase 9A)
✓ test_gateway.py: 3/3 PASS
✓ test_chat.py: 4/4 PASS  
✓ test_multi_agent.py: 4/4 PASS
✓ No agents show FALLBACK (except Explanation if LLM unavailable)
✓ Agent traces show COMPLETED for real communication
✓ /api/autorescue/check works end-to-end

### Android (Phase 9B)
✓ Android build: BUILD SUCCESSFUL
✓ APK path: app/build/outputs/apk/debug/app-debug.apk
✓ All 3 scenarios (Healthy/Warning/Critical) work
✓ Agent Activity UI displays properly
✓ Themes compatible

---

## Current Blockers
1. 4 agent files still use local message models
2. orchestrator_10agent.py needs to be made production-ready
3. FastAPI endpoint still uses 4-agent direct orchestration

## Next Steps
1. Complete Stage 1: Update remaining 4 agent files
2. Proceed to Stage 2: Build real orchestrator
3. Stage 3-4: Wire to FastAPI and validate tests
4. Stages 5-7: Android integration

---

## Time Estimate
- Stage 1 (Agents): ~30 mins
- Stage 2 (Orchestrator): ~60 mins  
- Stage 3-4 (Endpoint + Tests): ~45 mins
- **Backend Total: ~2 hours**
- Stage 5-7 (Android): ~60 mins
- **Total Phase 9: ~3 hours**

---

## Notes
- No rushing: Quality over speed
- Real agent communication: No faking traces
- Backward compatibility: Don't break existing Android
- Documentation: Update CLAUDE.md with final architecture
- Git: Commit after each major stage for rollback safety
