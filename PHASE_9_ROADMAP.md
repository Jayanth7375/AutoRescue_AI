# Phase 9 — Real 10-Agent Orchestration

## Current Status
- ✓ Git checkpoint created (4-agent stable state)
- ✓ Root cause identified: Message model mismatch causing FALLBACK
- ✓ Unified request models added to agents/messages.py
- ✓ Telemetry Agent updated to use shared models
- ✓ Safety Agent updated to use shared models + startup logging
- ✓ Maintenance Agent updated to use shared models
- ✓ Notification Agent updated to use shared models
- ✓ Explanation Agent updated to use shared models + LLM fallback
- ✓ Verification Agent updated to use shared models + consistency checks
- ✓ New orchestrator_uagent_phase9.py implemented with real 10-agent workflow
- ✓ FastAPI endpoint wired to use orchestrator_uagent_phase9
- ✓ All 10 run_*_agent.py scripts created
- ✓ run_all_agents.ps1 updated to start all 10 agents + FastAPI
- ⏳ Tests need validation against real traces
- ⏳ Android needs extended models + UI components

---

## Implementation Plan

### PHASE 9A — Backend (Real 10-Agent Coordination)

#### Stage 1: Fix Agent Message Models (4 files remaining)
- [x] Maintenance Agent: Update to use MaintenanceRequest/MaintenanceMessage
- [x] Notification Agent: Update to use NotificationRequest/NotificationMessage  
- [x] Explanation Agent: Update to use ExplanationRequest/ExplanationMessage
- [x] Verification Agent: Update to use VerificationRequest/VerificationMessage

**Status**: ✓ COMPLETE - All 6 new agents use shared models with environment config
**Details**: 
  - All agents import from agents.messages
  - All have AGENT_SEED and AGENT_PORT env vars with defaults
  - All have @on_event("startup") logging
  - Explanation Agent has Groq LLM fallback
  - Verification Agent checks for contradictions
**Commit**: "Phase 9 Step 1: Unify all 6 new agent message models"

#### Stage 2: Implement True 10-Agent Orchestrator
- [x] Create new orchestrator_uagent_phase9.py with proper flow
- [x] Implement sequential workflow:
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
- [x] Real message passing: use ctx.send_and_receive() for each agent
- [x] Proper error handling: catch failures, mark as FALLBACK, continue
- [x] Real agent traces: only mark COMPLETED if agent actually responded
- [x] Conditional execution: skip Service/Rescue based on severity
- [x] Merge results: Safety overrides Diagnosis, Verification is final

**Key Logic:**
```
Telemetry → VALIDATES → continues
       → FAILS → return error

Diagnostic → severity={NORMAL, WARNING, CRITICAL}

Safety → (NORMAL=safe) / (WARNING=safe) / (CRITICAL=unsafe)

Maintenance → urgency={ROUTINE, SOON, IMMEDIATE}

Service → IF severity != NORMAL (SKIPPED if NORMAL)

Rescue → IF CRITICAL or tow_required (SKIPPED otherwise)

Notifications → from all previous results

Explanation → LLM with fallback to deterministic

Verification → reconcile contradictions
```

**Status**: ✓ COMPLETE - orchestrator_uagent_phase9.py fully implemented
**Details**:
  - Class Orchestrator10Agent with async orchestrate() method
  - Uses Orchestrator class pattern for internal coordination
  - Environment-based agent address configuration with defaults
  - Comprehensive error handling and trace logging
  - Conditional Service/Rescue execution
  - Truthful agent traces (COMPLETED/SKIPPED/FALLBACK/FAILED)
**Commit**: "Phase 9 Step 2: Implement real 10-agent orchestrator"

#### Stage 3: Update FastAPI Endpoint
- [x] Modify /api/autorescue/check to call new orchestrator
- [x] Return extended response with all 10 agent results
- [x] Include agent_trace with COMPLETED/SKIPPED/FALLBACK/FAILED
- [x] Maintain backward compatibility with existing Android fields

**Status**: ✓ COMPLETE - FastAPI endpoint wired to orchestrator_uagent_phase9
**Details**:
  - /api/autorescue/check now calls ORCHESTRATOR_AGENT_ADDRESS
  - Uses send_sync_message() with 60-second timeout
  - Returns AutoRescueApiResponse with all legacy fields intact
  - Extended response includes telemetry_validation, safety, maintenance, etc. (optional)
  - Agent traces included in response
  - Proper error handling with 503 service unavailable
**Commit**: "Phase 9 Step 3: Wire FastAPI to 10-agent orchestrator"

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
None - Backend Phase 9A infrastructure complete!

## Next Steps (Immediate)
1. ✓ Stage 1-3 COMPLETE: Agents, Orchestrator, FastAPI wired
2. Stage 4: Validate tests (test_gateway.py 3/3, test_multi_agent.py 4/4)
3. Stages 5-7: Android integration (once tests pass)

## Critical Path to Go Live
1. Start all 10 agents + FastAPI using updated run_all_agents.ps1
2. Run test suite to verify all agents communicate correctly
3. Check for FALLBACK status (should only appear on genuine LLM failures)
4. Validate agent traces show truthful COMPLETED/SKIPPED/FALLBACK/FAILED

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
