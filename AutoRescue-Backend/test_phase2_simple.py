"""Simple Phase 2 uAgent test - run this after starting the Diagnostic Agent."""

import os
import sys
import asyncio
import logging
from uuid import uuid4

from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    VehicleTelemetryMessage,
    DiagnosticResponseMessage,
    DiagnosticErrorMessage,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration from environment
DIAGNOSTIC_AGENT_ADDRESS = os.getenv("DIAGNOSTIC_AGENT_ADDRESS")
TEST_CLIENT_PORT = int(os.getenv("TEST_CLIENT_PORT", "8002"))

if not DIAGNOSTIC_AGENT_ADDRESS:
    logger.error("\n" + "=" * 60)
    logger.error("ERROR: DIAGNOSTIC_AGENT_ADDRESS not set")
    logger.error("=" * 60)
    logger.error("Please:")
    logger.error("1. Start Diagnostic Agent: uv run python run_diagnostic_agent.py")
    logger.error("2. Copy the printed agent address")
    logger.error("3. Update .env file: DIAGNOSTIC_AGENT_ADDRESS=<address>")
    logger.error("4. Then run: uv run python test_phase2_simple.py")
    logger.error("=" * 60)
    sys.exit(1)

# Create test client agent with proper endpoints
test_client = Agent(
    name="autorescue_test_client",
    seed="autorescue-test-client-simple-seed",
    port=TEST_CLIENT_PORT,
    endpoint=[f"http://127.0.0.1:{TEST_CLIENT_PORT}/submit"],
)

# Shared state
test_result = {
    "response_received": False,
    "error_received": False,
    "data": None,
    "done": False,
}


@test_client.on_message(model=DiagnosticResponseMessage)
async def handle_response(ctx: Context, sender: str, msg: DiagnosticResponseMessage):
    """Handle diagnostic response."""
    logger.info("\n" + "=" * 60)
    logger.info("✓ RESPONSE RECEIVED")
    logger.info("=" * 60)
    logger.info(f"From: {sender}")
    logger.info(f"Request ID: {msg.request_id}")
    logger.info(f"Vehicle ID: {msg.vehicle_id}")
    logger.info(f"Issue: {msg.issue}")
    logger.info(f"Severity: {msg.severity}")
    logger.info(f"Safe to Drive: {msg.safe_to_drive}")
    logger.info(f"Affected Component: {msg.affected_component}")
    logger.info(f"Recommendation: {msg.recommendation}")

    test_result["response_received"] = True
    test_result["data"] = msg
    test_result["done"] = True

    # Verify the response
    if (msg.severity == "CRITICAL" and
        msg.safe_to_drive is False and
        "Engine overheating" in msg.issue):
        logger.info("\n" + "=" * 60)
        logger.info("✓ TEST PASSED - Correct diagnosis")
        logger.info("=" * 60)
    else:
        logger.error("\n" + "=" * 60)
        logger.error("✗ TEST FAILED - Unexpected response")
        logger.error("=" * 60)


@test_client.on_message(model=DiagnosticErrorMessage)
async def handle_error(ctx: Context, sender: str, msg: DiagnosticErrorMessage):
    """Handle error response."""
    logger.error("\n" + "=" * 60)
    logger.error("✗ ERROR RESPONSE RECEIVED")
    logger.error("=" * 60)
    logger.error(f"From: {sender}")
    logger.error(f"Error: {msg.error}")

    test_result["error_received"] = True
    test_result["data"] = msg
    test_result["done"] = True


@test_client.on_event("startup")
async def startup(ctx: Context):
    """Send test message on startup."""
    logger.info("=" * 60)
    logger.info("Test Client Agent started")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)

    logger.info(f"\nSending telemetry to: {DIAGNOSTIC_AGENT_ADDRESS}")

    # Create test telemetry
    request_id = str(uuid4())
    telemetry = VehicleTelemetryMessage(
        request_id=request_id,
        vehicle_id="TN37AB1234",
        engine_temperature=122,  # CRITICAL - engine overheating
        battery_voltage=12.7,
        front_left_tyre_psi=32,
        front_right_tyre_psi=32,
        rear_left_tyre_psi=31,
        rear_right_tyre_psi=31,
        coolant_level=75,
    )

    logger.info("\n" + "=" * 60)
    logger.info("TEST SCENARIO")
    logger.info("=" * 60)
    logger.info(f"Request ID: {request_id}")
    logger.info(f"Vehicle ID: {telemetry.vehicle_id}")
    logger.info(f"Engine Temperature: {telemetry.engine_temperature}°C")
    logger.info(f"Battery Voltage: {telemetry.battery_voltage}V")
    logger.info(f"Coolant Level: {telemetry.coolant_level}%")
    logger.info(f"Tyre Pressures: FL={telemetry.front_left_tyre_psi}, FR={telemetry.front_right_tyre_psi}, RL={telemetry.rear_left_tyre_psi}, RR={telemetry.rear_right_tyre_psi} PSI")
    logger.info("\nExpected Result:")
    logger.info("  Severity: CRITICAL")
    logger.info("  Issue: Engine overheating")
    logger.info("  Safe to Drive: False")

    logger.info("\nSending request...")
    await ctx.send(DIAGNOSTIC_AGENT_ADDRESS, telemetry)

    # Wait for response
    logger.info("Waiting for response...")
    start_time = asyncio.get_event_loop().time()

    while not test_result["done"]:
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed > 15:
            logger.error("\nTimeout! No response received within 15 seconds.")
            logger.error("Make sure the Diagnostic Agent is running at the configured address.")
            test_result["done"] = True
            break
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    logger.info("\n" + "=" * 60)
    logger.info("Phase 2: uAgent Communication Test")
    logger.info("=" * 60)
    logger.info(f"Diagnostic Agent: {DIAGNOSTIC_AGENT_ADDRESS}")

    try:
        test_client.run()
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
