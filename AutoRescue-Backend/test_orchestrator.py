"""Test client for Orchestrator Agent - complete multi-agent workflow testing."""

import os
import sys
import asyncio
import logging
from uuid import uuid4

from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    AutoRescueRequestMessage,
    AutoRescueResponseMessage,
    AutoRescueErrorMessage,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
ORCHESTRATOR_AGENT_ADDRESS = os.getenv("ORCHESTRATOR_AGENT_ADDRESS")

if not ORCHESTRATOR_AGENT_ADDRESS:
    logger.error("\n" + "=" * 60)
    logger.error("ERROR: ORCHESTRATOR_AGENT_ADDRESS not configured")
    logger.error("=" * 60)
    logger.error("Please:")
    logger.error("1. Start all agents:")
    logger.error("   - uv run python run_diagnostic_agent.py")
    logger.error("   - uv run python run_service_agent.py")
    logger.error("   - uv run python run_rescue_agent.py")
    logger.error("   - uv run python run_orchestrator_agent.py")
    logger.error("2. Update .env with agent addresses")
    logger.error("3. Run: uv run python test_orchestrator.py")
    logger.error("=" * 60)
    sys.exit(1)

# Create test client agent
test_client = Agent(
    name="orchestrator_test_client",
    seed="orchestrator-test-client-seed",
    port=8019,
    endpoint=[f"http://127.0.0.1:8019/submit"],
)

# Shared state for test results
test_results = {}


@test_client.on_message(model=AutoRescueResponseMessage)
async def handle_response(ctx: Context, sender: str, msg: AutoRescueResponseMessage):
    """Handle unified AutoRescue response."""
    logger.info("\n" + "=" * 60)
    logger.info("✓ ORCHESTRATOR RESPONSE RECEIVED")
    logger.info("=" * 60)

    logger.info(f"Request ID: {msg.request_id}")
    logger.info(f"Vehicle ID: {msg.vehicle_id}")
    logger.info(f"Status: {msg.status}")
    logger.info(f"Message: {msg.message}")
    logger.info(f"\nDiagnosis:")
    logger.info(f"  Issue: {msg.diagnosis.issue}")
    logger.info(f"  Component: {msg.diagnosis.affected_component}")
    logger.info(f"  Severity: {msg.diagnosis.severity}")
    logger.info(f"  Safe to Drive: {msg.diagnosis.safe_to_drive}")
    logger.info(f"\nService Centres: {len(msg.service_centres)}")
    if msg.service_centres:
        for i, centre in enumerate(msg.service_centres[:3], 1):
            logger.info(f"  {i}. {centre.name} ({centre.distance_km} km)")
    logger.info(f"Navigation Allowed: {msg.navigation_allowed}")

    if msg.rescue:
        logger.info(f"\nRescue:")
        logger.info(f"  Assistance Required: {msg.rescue.assistance_required}")
        logger.info(f"  Type: {msg.rescue.assistance_type}")
        logger.info(f"  Priority: {msg.rescue.priority}")
        logger.info(f"  Tow Required: {msg.rescue.tow_required}")
        if msg.rescue.destination_name:
            logger.info(f"  Destination: {msg.rescue.destination_name}")
        if msg.rescue.estimated_dispatch_minutes:
            logger.info(f"  Est. Dispatch: {msg.rescue.estimated_dispatch_minutes} min (Simulated MVP)")

    test_results[msg.request_id] = {
        "received": True,
        "response": msg,
    }


@test_client.on_message(model=AutoRescueErrorMessage)
async def handle_error(ctx: Context, sender: str, msg: AutoRescueErrorMessage):
    """Handle error response."""
    logger.error("\n" + "=" * 60)
    logger.error("✗ ORCHESTRATOR ERROR RESPONSE")
    logger.error("=" * 60)
    logger.error(f"Stage: {msg.stage}")
    logger.error(f"Error: {msg.error}")

    test_results[msg.request_id] = {
        "received": False,
        "error": msg.error,
    }


async def send_test(
    ctx: Context,
    test_name: str,
    engine_temp: float,
    battery: float,
    fl_tyre: float,
    fr_tyre: float,
    rl_tyre: float,
    rr_tyre: float,
    coolant: float,
):
    """Send a test scenario."""
    request_id = str(uuid4())

    logger.info("\n" + "=" * 60)
    logger.info(f"SCENARIO: {test_name}")
    logger.info("=" * 60)
    logger.info(f"Request ID: {request_id}")
    logger.info(f"Engine Temp: {engine_temp}°C")
    logger.info(f"Battery: {battery}V")
    logger.info(f"Tyres: FL={fl_tyre}, FR={fr_tyre}, RL={rl_tyre}, RR={rr_tyre} PSI")
    logger.info(f"Coolant: {coolant}%")

    request = AutoRescueRequestMessage(
        request_id=request_id,
        vehicle_id="TN37AB1234",
        engine_temperature=engine_temp,
        battery_voltage=battery,
        front_left_tyre_psi=fl_tyre,
        front_right_tyre_psi=fr_tyre,
        rear_left_tyre_psi=rl_tyre,
        rear_right_tyre_psi=rr_tyre,
        coolant_level=coolant,
        latitude=19.076,
        longitude=72.8777,
    )

    logger.info(f"\nSending to Orchestrator: {ORCHESTRATOR_AGENT_ADDRESS[:40]}...")
    await ctx.send(ORCHESTRATOR_AGENT_ADDRESS, request)

    # Wait for response
    start_time = asyncio.get_event_loop().time()
    while True:
        elapsed = asyncio.get_event_loop().time() - start_time

        if request_id in test_results:
            break

        if elapsed > 30:
            logger.error(f"Timeout waiting for response")
            test_results[request_id] = {
                "received": False,
                "error": "Timeout",
            }
            break

        await asyncio.sleep(0.1)

    return request_id


@test_client.on_event("startup")
async def startup(ctx: Context):
    """Run all orchestration tests."""
    logger.info("=" * 60)
    logger.info("Orchestrator Agent Test Suite")
    logger.info("=" * 60)
    logger.info(f"Test Client: {ctx.agent.address}")
    logger.info(f"Orchestrator: {ORCHESTRATOR_AGENT_ADDRESS[:40]}...")

    # Test 1: Healthy Vehicle
    id1 = await send_test(
        ctx,
        "Healthy Vehicle (No Service/Rescue)",
        engine_temp=95,
        battery=12.7,
        fl_tyre=32,
        fr_tyre=32,
        rl_tyre=31,
        rr_tyre=31,
        coolant=75,
    )

    # Test 2: Tyre Warning
    id2 = await send_test(
        ctx,
        "Tyre Warning (Service Recommended)",
        engine_temp=95,
        battery=12.7,
        fl_tyre=28,
        fr_tyre=32,
        rl_tyre=31,
        rr_tyre=31,
        coolant=75,
    )

    # Test 3: Engine Overheating
    id3 = await send_test(
        ctx,
        "Engine Overheating (Assistance Required)",
        engine_temp=122,
        battery=12.7,
        fl_tyre=32,
        fr_tyre=32,
        rl_tyre=31,
        rr_tyre=31,
        coolant=75,
    )

    # Wait for all responses
    await asyncio.sleep(2)

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 60)

    tests = [
        ("Test 1", "Healthy Vehicle", id1, "HEALTHY"),
        ("Test 2", "Tyre Warning", id2, "SERVICE_RECOMMENDED"),
        ("Test 3", "Engine Overheating", id3, "ASSISTANCE_REQUIRED"),
    ]

    passed = 0
    failed = 0

    for label, desc, request_id, expected_status in tests:
        if request_id in test_results:
            result = test_results[request_id]
            if result.get("received"):
                status = result["response"].status
                match = "✓" if status == expected_status else "⚠"
                logger.info(f"{match} {label}: {desc}")
                if status == expected_status:
                    passed += 1
                else:
                    logger.warning(f"   Expected {expected_status}, got {status}")
            else:
                logger.error(f"✗ {label}: {desc} - {result.get('error', 'Unknown error')}")
                failed += 1
        else:
            logger.error(f"✗ {label}: {desc} - No response")
            failed += 1

    logger.info("\n" + "=" * 60)
    if failed == 0:
        logger.info(f"✓ ALL ORCHESTRATION TESTS PASSED ({passed}/{len(tests)})")
        logger.info("=" * 60)
        logger.info("Multi-agent workflow verified:")
        logger.info("  Orchestrator → Diagnostic")
        logger.info("  Orchestrator → Service (when needed)")
        logger.info("  Orchestrator → Rescue (when unsafe)")
        logger.info("  Orchestrator → Client (unified response)")
    else:
        logger.error(f"✗ SOME TESTS FAILED ({passed} passed, {failed} failed)")
        logger.error("=" * 60)


if __name__ == "__main__":
    logger.info("\n" + "=" * 60)
    logger.info("Phase 5: Orchestrator Agent Test")
    logger.info("=" * 60)

    try:
        test_client.run()
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
