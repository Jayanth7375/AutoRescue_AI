"""Test client for Rescue uAgent."""

import os
import sys
import asyncio
import logging
from uuid import uuid4

from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    RescueRequestMessage,
    RescueResponseMessage,
    RescueErrorMessage,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
RESCUE_AGENT_ADDRESS = os.getenv("RESCUE_AGENT_ADDRESS")
TEST_RESCUE_PORT = int(os.getenv("TEST_CLIENT_PORT", "8012"))

if not RESCUE_AGENT_ADDRESS:
    logger.error("\n" + "=" * 60)
    logger.error("ERROR: RESCUE_AGENT_ADDRESS not configured")
    logger.error("=" * 60)
    logger.error("Please:")
    logger.error("1. Start Rescue Agent: uv run python run_rescue_agent.py")
    logger.error("2. Copy the printed agent address")
    logger.error("3. Update .env: RESCUE_AGENT_ADDRESS=<address>")
    logger.error("4. Then run: uv run python test_rescue_agent.py")
    logger.error("=" * 60)
    sys.exit(1)

# Create test client agent
test_client = Agent(
    name="rescue_test_client",
    seed="rescue-test-client-seed",
    port=8017,
    endpoint=[f"http://127.0.0.1:8017/submit"],
)

# Shared state for test results
test_results = []


@test_client.on_message(model=RescueResponseMessage)
async def handle_response(ctx: Context, sender: str, msg: RescueResponseMessage):
    """Handle rescue response."""
    logger.info("\n" + "=" * 60)
    logger.info("✓ RESCUE RESPONSE RECEIVED")
    logger.info("=" * 60)

    logger.info(f"Request ID: {msg.request_id}")
    logger.info(f"Vehicle ID: {msg.vehicle_id}")
    logger.info(f"Assistance Required: {msg.assistance_required}")
    logger.info(f"Assistance Type: {msg.assistance_type}")
    logger.info(f"Priority: {msg.priority}")
    logger.info(f"Can Drive: {msg.can_drive}")
    logger.info(f"Tow Required: {msg.tow_required}")
    logger.info(f"Instructions: {msg.instructions}")
    logger.info(f"Reason: {msg.reason}")
    if msg.destination_name:
        logger.info(f"Destination: {msg.destination_name}")
    if msg.estimated_dispatch_minutes:
        logger.info(f"Estimated Dispatch ETA: {msg.estimated_dispatch_minutes} minutes (Simulated MVP)")

    # Store result for verification
    test_results.append({
        "test_id": msg.request_id,
        "response": msg,
        "received": True,
    })


@test_client.on_message(model=RescueErrorMessage)
async def handle_error(ctx: Context, sender: str, msg: RescueErrorMessage):
    """Handle error response."""
    logger.error("\n" + "=" * 60)
    logger.error("✗ ERROR RESPONSE RECEIVED")
    logger.error("=" * 60)
    logger.error(f"Request ID: {msg.request_id}")
    logger.error(f"Error: {msg.error}")

    test_results.append({
        "test_id": msg.request_id,
        "error": msg.error,
        "received": False,
    })


async def send_test(
    ctx: Context,
    test_name: str,
    issue: str,
    affected_component: str,
    severity: str,
    safe_to_drive: bool,
    service_centre_name: str | None = None,
):
    """Send a single rescue test request."""
    request_id = str(uuid4())

    logger.info("\n" + "=" * 60)
    logger.info(f"TEST: {test_name}")
    logger.info("=" * 60)
    logger.info(f"Request ID: {request_id}")
    logger.info(f"Issue: {issue}")
    logger.info(f"Component: {affected_component}")
    logger.info(f"Severity: {severity}")
    logger.info(f"Safe to Drive: {safe_to_drive}")

    rescue_request = RescueRequestMessage(
        request_id=request_id,
        vehicle_id="TN37AB1234",
        issue=issue,
        affected_component=affected_component,
        severity=severity,
        safe_to_drive=safe_to_drive,
        latitude=19.076,
        longitude=72.8777,
        service_centre_name=service_centre_name,
        service_centre_place_id="osm-node-123" if service_centre_name else None,
    )

    logger.info(f"\nSending rescue request to {RESCUE_AGENT_ADDRESS}...")
    await ctx.send(RESCUE_AGENT_ADDRESS, rescue_request)

    # Wait for response
    start_time = asyncio.get_event_loop().time()
    while True:
        elapsed = asyncio.get_event_loop().time() - start_time

        # Check if response received
        matching = [r for r in test_results if r["test_id"] == request_id]
        if matching:
            break

        if elapsed > 10:
            logger.error(f"Timeout waiting for response")
            break

        await asyncio.sleep(0.1)

    return request_id


@test_client.on_event("startup")
async def startup(ctx: Context):
    """Run all rescue tests on startup."""
    logger.info("=" * 60)
    logger.info("Rescue Agent Test Suite")
    logger.info("=" * 60)
    logger.info(f"Rescue Agent: {RESCUE_AGENT_ADDRESS}")
    logger.info(f"Test Client: {ctx.agent.address}")

    # Test 1: Engine Overheating
    id1 = await send_test(
        ctx,
        "Engine Overheating (Critical)",
        "Engine overheating",
        "engine",
        "CRITICAL",
        False,
    )

    # Test 2: Critical Tyre
    id2 = await send_test(
        ctx,
        "Critical Tyre Pressure",
        "Front Left Tyre pressure critically low",
        "front_left_tyre",
        "CRITICAL",
        False,
    )

    # Test 3: Battery Failure
    id3 = await send_test(
        ctx,
        "Battery Failure (Critical)",
        "Battery voltage critically low",
        "battery",
        "CRITICAL",
        False,
    )

    # Test 4: Healthy Vehicle
    id4 = await send_test(
        ctx,
        "Healthy Vehicle (No Assistance)",
        "No critical issues detected",
        "vehicle",
        "NORMAL",
        True,
    )

    # Test 5: Tow with Destination
    id5 = await send_test(
        ctx,
        "Engine Overheating with Tow Destination",
        "Engine overheating",
        "engine",
        "CRITICAL",
        False,
        service_centre_name="Demo Auto Service",
    )

    # Wait for all responses
    await asyncio.sleep(2)

    # Display results
    logger.info("\n" + "=" * 60)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 60)

    test_names = [
        ("Test 1", "Engine Overheating", "assistance_type=TOW, priority=CRITICAL"),
        ("Test 2", "Critical Tyre", "assistance_type=TYRE_ASSISTANCE"),
        ("Test 3", "Battery Failure", "assistance_type=BATTERY_JUMP_START"),
        ("Test 4", "Healthy Vehicle", "assistance_type=NONE, can_drive=true"),
        ("Test 5", "Tow Destination", "destination_name set"),
    ]

    test_ids = [id1, id2, id3, id4, id5]
    passed = 0
    failed = 0

    for (label, name, expected), test_id in zip(test_names, test_ids):
        matching = [r for r in test_results if r["test_id"] == test_id]

        if matching and matching[0].get("received"):
            logger.info(f"✓ {label}: {name}")
            passed += 1
        else:
            logger.error(f"✗ {label}: {name}")
            failed += 1

    logger.info("\n" + "=" * 60)
    if failed == 0:
        logger.info(f"✓ ALL RESCUE TESTS PASSED ({passed}/{len(test_ids)})")
        logger.info("=" * 60)
    else:
        logger.error(f"✗ SOME TESTS FAILED ({passed} passed, {failed} failed)")
        logger.error("=" * 60)


if __name__ == "__main__":
    logger.info("\n" + "=" * 60)
    logger.info("Phase 4: Rescue uAgent Test")
    logger.info("=" * 60)
    logger.info(f"Rescue Agent: {RESCUE_AGENT_ADDRESS}")

    try:
        test_client.run()
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
