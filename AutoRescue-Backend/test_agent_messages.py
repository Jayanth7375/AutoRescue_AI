#!/usr/bin/env python3
"""Smoke test for direct uAgent message communication (no FastAPI)."""

import asyncio
import logging
from uagents.communication import send_sync_message
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.WARNING)  # Reduce noise

# Import shared models
from agents.messages import (
    TelemetryValidationRequest,
    TelemetryValidationMessage,
    SafetyRequest,
    SafetyMessage,
    MaintenanceRequest,
    MaintenanceMessage,
    NotificationRequest,
    NotificationMessage,
    ExplanationRequest,
    ExplanationMessage,
    VerificationRequest,
    VerificationMessage,
    DiagnosisSummary,
    ServiceResponseMessage,
    RescueResponseMessage,
)

# Get addresses from .env
TELEMETRY_ADDR = os.getenv("TELEMETRY_AGENT_ADDRESS")
SAFETY_ADDR = os.getenv("SAFETY_AGENT_ADDRESS")
MAINTENANCE_ADDR = os.getenv("MAINTENANCE_AGENT_ADDRESS")
NOTIFICATION_ADDR = os.getenv("NOTIFICATION_AGENT_ADDRESS")
EXPLANATION_ADDR = os.getenv("EXPLANATION_AGENT_ADDRESS")
VERIFICATION_ADDR = os.getenv("VERIFICATION_AGENT_ADDRESS")
SERVICE_ADDR = os.getenv("SERVICE_AGENT_ADDRESS")
RESCUE_ADDR = os.getenv("RESCUE_AGENT_ADDRESS")

print("\n" + "=" * 70)
print("Agent Message Smoke Test (Async)")
print("=" * 70)

async def test_telemetry():
    """Test Telemetry agent directly (async)."""
    print("\n[TEST] Telemetry Agent")
    print("-" * 70)

    if not TELEMETRY_ADDR:
        print("X SKIP - TELEMETRY_AGENT_ADDRESS not configured")
        return False

    try:
        req = TelemetryValidationRequest(
            request_id="test-001",
            vehicle_id="TEST-VEH",
            engine_temperature=95.0,
            battery_voltage=12.7,
            front_left_tyre_psi=32.0,
            front_right_tyre_psi=32.0,
            rear_left_tyre_psi=32.0,
            rear_right_tyre_psi=32.0,
            coolant_level=75.0,
            latitude=19.076,
            longitude=72.8777,
        )

        print(f"  Destination: {TELEMETRY_ADDR[:40]}...")
        print(f"  Request model: TelemetryValidationRequest")
        print(f"  Awaiting response...")

        # FIXED: Now properly awaiting async function
        resp = await send_sync_message(
            destination=TELEMETRY_ADDR,
            message=req,
            response_type=TelemetryValidationMessage,
            timeout=5,
        )

        print(f"  Response type: {type(resp).__name__}")
        if isinstance(resp, tuple):
            print(f"  Response is tuple, extracting [0]")
            resp = resp[0]

        print(f"  Valid: {resp.valid}")
        print("  OK PASS")
        return True

    except Exception as e:
        print(f"  X FAIL - {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_safety():
    """Test Safety agent directly (async)."""
    print("\n[TEST] Safety Agent")
    print("-" * 70)

    if not SAFETY_ADDR:
        print("X SKIP - SAFETY_AGENT_ADDRESS not configured")
        return False

    try:
        diagnosis = DiagnosisSummary(
            issue="Test issue",
            affected_component="engine",
            severity="WARNING",
            safe_to_drive=True,
            recommendation="Test recommendation",
        )

        req = SafetyRequest(
            request_id="test-002",
            vehicle_id="TEST-VEH",
            diagnosis=diagnosis,
        )

        print(f"  Destination: {SAFETY_ADDR[:40]}...")
        print(f"  Request model: SafetyRequest (severity=WARNING)")
        print(f"  Awaiting response...")

        # FIXED: Now properly awaiting async function
        resp = await send_sync_message(
            destination=SAFETY_ADDR,
            message=req,
            response_type=SafetyMessage,
            timeout=5,
        )

        print(f"  Response type: {type(resp).__name__}")
        if isinstance(resp, tuple):
            print(f"  Response is tuple, extracting [0]")
            resp = resp[0]

        print(f"  Safe to drive: {resp.safe_to_drive}")
        print(f"  Navigation allowed: {resp.navigation_allowed}")
        print(f"  Tow required: {resp.tow_required}")
        print(f"  Risk level: {resp.risk_level}")
        print("  OK PASS")
        return True

    except Exception as e:
        print(f"  X FAIL - {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_maintenance():
    """Test Maintenance agent directly (async)."""
    print("\n[TEST] Maintenance Agent")
    print("-" * 70)

    if not MAINTENANCE_ADDR:
        print("X SKIP - MAINTENANCE_AGENT_ADDRESS not configured")
        return False

    try:
        diagnosis = DiagnosisSummary(
            issue="Low tyre pressure",
            affected_component="tyre",
            severity="WARNING",
            safe_to_drive=True,
            recommendation="Check tyre pressure",
        )

        # Create corresponding safety object for WARNING scenario
        safety = SafetyMessage(
            safe_to_drive=True,
            navigation_allowed=True,
            tow_required=False,
            risk_level="MEDIUM",
        )

        req = MaintenanceRequest(
            request_id="test-003",
            vehicle_id="TEST-VEH",
            diagnosis=diagnosis,
            safety=safety,
        )

        print(f"  Destination: {MAINTENANCE_ADDR[:40]}...")
        print(f"  Request model: MaintenanceRequest (severity=WARNING)")
        print(f"  Awaiting response...")

        resp = await send_sync_message(
            destination=MAINTENANCE_ADDR,
            message=req,
            response_type=MaintenanceMessage,
            timeout=5,
        )

        print(f"  Response type: {type(resp).__name__}")
        if isinstance(resp, tuple):
            print(f"  Response is tuple, extracting [0]")
            resp = resp[0]

        print(f"  Component: {resp.component}")
        print(f"  Urgency: {resp.urgency}")
        print(f"  Action: {resp.action[:50]}...")
        print("  OK PASS")
        return True

    except Exception as e:
        print(f"  X FAIL - {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_notification():
    """Test Notification agent directly (async)."""
    print("\n[TEST] Notification Agent")
    print("-" * 70)

    if not NOTIFICATION_ADDR:
        print("X SKIP - NOTIFICATION_AGENT_ADDRESS not configured")
        return False

    try:
        diagnosis = DiagnosisSummary(
            issue="Low tyre pressure",
            affected_component="tyre",
            severity="WARNING",
            safe_to_drive=True,
            recommendation="Check tyre pressure",
        )

        req = NotificationRequest(
            request_id="test-004",
            vehicle_id="TEST-VEH",
            diagnosis=diagnosis,
        )

        print(f"  Destination: {NOTIFICATION_ADDR[:40]}...")
        print(f"  Request model: NotificationRequest (severity=WARNING)")
        print(f"  Awaiting response...")

        resp = await send_sync_message(
            destination=NOTIFICATION_ADDR,
            message=req,
            response_type=NotificationMessage,
            timeout=5,
        )

        print(f"  Response type: {type(resp).__name__}")
        if isinstance(resp, tuple):
            print(f"  Response is tuple, extracting [0]")
            resp = resp[0]

        print(f"  Type: {resp.type}")
        print(f"  Severity: {resp.severity}")
        print(f"  Title: {resp.title}")
        print("  OK PASS")
        return True

    except Exception as e:
        print(f"  X FAIL - {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_explanation():
    """Test Explanation agent directly (async)."""
    print("\n[TEST] Explanation Agent")
    print("-" * 70)

    if not EXPLANATION_ADDR:
        print("X SKIP - EXPLANATION_AGENT_ADDRESS not configured")
        return False

    try:
        diagnosis = DiagnosisSummary(
            issue="Low tyre pressure",
            affected_component="tyre",
            severity="WARNING",
            safe_to_drive=True,
            recommendation="Check tyre pressure",
        )

        req = ExplanationRequest(
            request_id="test-005",
            vehicle_id="TEST-VEH",
            diagnosis=diagnosis,
        )

        print(f"  Destination: {EXPLANATION_ADDR[:40]}...")
        print(f"  Request model: ExplanationRequest")
        print(f"  Awaiting response...")

        resp = await send_sync_message(
            destination=EXPLANATION_ADDR,
            message=req,
            response_type=ExplanationMessage,
            timeout=5,
        )

        print(f"  Response type: {type(resp).__name__}")
        if isinstance(resp, tuple):
            print(f"  Response is tuple, extracting [0]")
            resp = resp[0]

        print(f"  Summary: {resp.summary[:50]}...")
        print(f"  Guidance: {resp.driver_guidance[:50]}...")
        # Check if using LLM or fallback
        groq_key = os.getenv("GROQ_API_KEY", "").strip()
        mode = "COMPLETED" if groq_key else "FALLBACK"
        print(f"  LLM Mode: {mode}")
        print("  OK PASS")
        return True

    except Exception as e:
        print(f"  X FAIL - {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_verification():
    """Test Verification agent directly (async)."""
    print("\n[TEST] Verification Agent")
    print("-" * 70)

    if not VERIFICATION_ADDR:
        print("X SKIP - VERIFICATION_AGENT_ADDRESS not configured")
        return False

    try:
        diagnosis = DiagnosisSummary(
            issue="Low tyre pressure",
            affected_component="tyre",
            severity="WARNING",
            safe_to_drive=True,
            recommendation="Check tyre pressure",
        )

        # Create consistent WARNING scenario
        safety = SafetyMessage(
            safe_to_drive=True,
            navigation_allowed=True,
            tow_required=False,
            risk_level="MEDIUM",
        )

        maintenance = MaintenanceMessage(
            component="tyre",
            action="Inspect and inflate affected tyre",
            urgency="SOON",
            reason="Low tyre pressure detected",
        )

        req = VerificationRequest(
            request_id="test-006",
            vehicle_id="TEST-VEH",
            diagnosis=diagnosis,
            safety=safety,
            maintenance=maintenance,
        )

        print(f"  Destination: {VERIFICATION_ADDR[:40]}...")
        print(f"  Request model: VerificationRequest")
        print(f"  Awaiting response...")

        resp = await send_sync_message(
            destination=VERIFICATION_ADDR,
            message=req,
            response_type=VerificationMessage,
            timeout=5,
        )

        print(f"  Response type: {type(resp).__name__}")
        if isinstance(resp, tuple):
            print(f"  Response is tuple, extracting [0]")
            resp = resp[0]

        print(f"  Verified: {resp.verified}")
        print(f"  Issues: {len(resp.issues)}")
        print("  OK PASS")
        return True

    except Exception as e:
        print(f"  X FAIL - {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_diagnostic():
    """Test Diagnostic function directly (synchronous, not a uAgent)."""
    print("\n[TEST] Diagnostic Function (Local)")
    print("-" * 70)

    try:
        from models.telemetry import VehicleTelemetry
        from tools.diagnostic_rules import diagnose_vehicle

        # Test HEALTHY
        telemetry = VehicleTelemetry(
            vehicle_id="TEST-HEALTHY",
            engine_temperature=95.0,
            battery_voltage=12.7,
            front_left_tyre_psi=32.0,
            front_right_tyre_psi=32.0,
            rear_left_tyre_psi=32.0,
            rear_right_tyre_psi=32.0,
            coolant_level=75.0,
        )

        result = diagnose_vehicle(telemetry)
        print(f"  HEALTHY input -> severity={result.severity.value}")
        if result.severity.value != "NORMAL":
            print(f"  X FAIL - Expected NORMAL, got {result.severity.value}")
            return False

        # Test WARNING
        telemetry.front_left_tyre_psi = 28.0
        result = diagnose_vehicle(telemetry)
        print(f"  WARNING input -> severity={result.severity.value}")
        if result.severity.value != "WARNING":
            print(f"  X FAIL - Expected WARNING, got {result.severity.value}")
            return False

        # Test CRITICAL
        telemetry.engine_temperature = 122.0
        result = diagnose_vehicle(telemetry)
        print(f"  CRITICAL input -> severity={result.severity.value}")
        if result.severity.value != "CRITICAL":
            print(f"  X FAIL - Expected CRITICAL, got {result.severity.value}")
            return False

        print("  PASS")
        return True

    except Exception as e:
        print(f"  X FAIL - {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_service():
    """Test Service agent directly (async)."""
    print("\n[TEST] Service Agent")
    print("-" * 70)

    SERVICE_ADDR = os.getenv("SERVICE_AGENT_ADDRESS")
    if not SERVICE_ADDR:
        print("X SKIP - SERVICE_AGENT_ADDRESS not configured")
        return False

    try:
        from agents.messages import ServiceRequestMessage

        req = ServiceRequestMessage(
            request_id="test-007",
            vehicle_id="TEST-VEH",
            issue="Low tyre pressure",
            affected_component="tyre",
            severity="WARNING",
            safe_to_drive=True,
            latitude=19.076,
            longitude=72.8777,
        )

        print(f"  Destination: {SERVICE_ADDR[:40]}...")
        print(f"  Request model: ServiceRequestMessage (WARNING severity)")
        print(f"  Awaiting response...")

        resp = await send_sync_message(
            destination=SERVICE_ADDR,
            message=req,
            response_type=ServiceResponseMessage,
            timeout=10,
        )

        print(f"  Response type: {type(resp).__name__}")
        if isinstance(resp, tuple):
            print(f"  Response is tuple, extracting [0]")
            resp = resp[0]

        print(f"  Service centres: {len(resp.centres)}")
        print(f"  Navigation allowed: {resp.navigation_allowed}")
        print(f"  Tow recommended: {resp.tow_recommended}")
        print("  OK PASS")
        return True

    except Exception as e:
        print(f"  X FAIL - {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_rescue():
    """Test Rescue agent directly (async)."""
    print("\n[TEST] Rescue Agent")
    print("-" * 70)

    RESCUE_ADDR = os.getenv("RESCUE_AGENT_ADDRESS")
    if not RESCUE_ADDR:
        print("X SKIP - RESCUE_AGENT_ADDRESS not configured")
        return False

    try:
        from agents.messages import RescueRequestMessage

        req = RescueRequestMessage(
            request_id="test-008",
            vehicle_id="TEST-VEH",
            issue="Engine overheating",
            affected_component="engine",
            severity="CRITICAL",
            safe_to_drive=False,
            latitude=19.076,
            longitude=72.8777,
        )

        print(f"  Destination: {RESCUE_ADDR[:40]}...")
        print(f"  Request model: RescueRequestMessage (CRITICAL severity)")
        print(f"  Awaiting response...")

        resp = await send_sync_message(
            destination=RESCUE_ADDR,
            message=req,
            response_type=RescueResponseMessage,
            timeout=10,
        )

        print(f"  Response type: {type(resp).__name__}")
        if isinstance(resp, tuple):
            print(f"  Response is tuple, extracting [0]")
            resp = resp[0]

        print(f"  Assistance required: {resp.assistance_required}")
        print(f"  Tow required: {resp.tow_required}")
        print(f"  Can drive: {resp.can_drive}")
        print(f"  Priority: {resp.priority}")
        print("  OK PASS")
        return True

    except Exception as e:
        print(f"  X FAIL - {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests in a single async context."""
    results = []

    # Run tests sequentially in one event loop
    telemetry_result = await test_telemetry()
    results.append(("Telemetry", telemetry_result))

    safety_result = await test_safety()
    results.append(("Safety", safety_result))

    maintenance_result = await test_maintenance()
    results.append(("Maintenance", maintenance_result))

    notification_result = await test_notification()
    results.append(("Notification", notification_result))

    explanation_result = await test_explanation()
    results.append(("Explanation", explanation_result))

    verification_result = await test_verification()
    results.append(("Verification", verification_result))

    service_result = await test_service()
    results.append(("Service", service_result))

    rescue_result = await test_rescue()
    results.append(("Rescue", rescue_result))

    # Summary
    print("\n" + "=" * 70)
    print("Results:")
    passed = sum(1 for _, p in results if p)
    print(f"  {passed}/{len(results)} PASS")
    for name, result in results:
        status = "OK" if result else "X"
        print(f"  {status} {name}")
    print("=" * 70 + "\n")

    return passed == len(results)

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Specialist Agent Communication Tests (11 total)")
    print("=" * 70)

    # Test Diagnostic first (synchronous local function)
    diagnostic_result = test_diagnostic()

    # Then test the async agents
    success = asyncio.run(main())

    # If either failed, report failure
    exit(0 if (diagnostic_result and success) else 1)
