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
    DiagnosisSummary,
)

# Get addresses from .env
TELEMETRY_ADDR = os.getenv("TELEMETRY_AGENT_ADDRESS")
SAFETY_ADDR = os.getenv("SAFETY_AGENT_ADDRESS")

print("\n" + "=" * 70)
print("Agent Message Smoke Test (Async)")
print("=" * 70)

async def test_telemetry():
    """Test Telemetry agent directly (async)."""
    print("\n[TEST] Telemetry Agent")
    print("-" * 70)

    if not TELEMETRY_ADDR:
        print("✗ SKIP - TELEMETRY_AGENT_ADDRESS not configured")
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
            print(f"  Response is tuple, extracting [1]")
            resp = resp[1]

        print(f"  Valid: {resp.valid}")
        print("  ✓ PASS")
        return True

    except Exception as e:
        print(f"  ✗ FAIL - {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_safety():
    """Test Safety agent directly (async)."""
    print("\n[TEST] Safety Agent")
    print("-" * 70)

    if not SAFETY_ADDR:
        print("✗ SKIP - SAFETY_AGENT_ADDRESS not configured")
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
            print(f"  Response is tuple, extracting [1]")
            resp = resp[1]

        print(f"  Safe to drive: {resp.safe_to_drive}")
        print(f"  Navigation allowed: {resp.navigation_allowed}")
        print(f"  Tow required: {resp.tow_required}")
        print(f"  Risk level: {resp.risk_level}")
        print("  ✓ PASS")
        return True

    except Exception as e:
        print(f"  ✗ FAIL - {type(e).__name__}: {e}")
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

    # Summary
    print("\n" + "=" * 70)
    print("Results:")
    passed = sum(1 for _, p in results if p)
    print(f"  {passed}/{len(results)} PASS")
    for name, result in results:
        status = "✓" if result else "✗"
        print(f"  {status} {name}")
    print("=" * 70 + "\n")

    return passed == len(results)

if __name__ == "__main__":
    # FIXED: Use asyncio.run() to run main async function
    success = asyncio.run(main())
    exit(0 if success else 1)
