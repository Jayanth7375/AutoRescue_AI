"""Test client agent for testing Diagnostic uAgent communication."""

import os
import logging
import asyncio
from typing import Optional
from uuid import uuid4

from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    VehicleTelemetryMessage,
    DiagnosticResponseMessage,
    DiagnosticErrorMessage,
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration from environment
DIAGNOSTIC_AGENT_ADDRESS = os.getenv("DIAGNOSTIC_AGENT_ADDRESS")
TEST_CLIENT_PORT = int(os.getenv("TEST_CLIENT_PORT", "8002"))

# Create the Test Client Agent with proper endpoints
test_client = Agent(
    name="autorescue_test_client",
    seed="autorescue-test-client-development-seed",
    port=TEST_CLIENT_PORT,
    endpoint=[f"http://127.0.0.1:{TEST_CLIENT_PORT}/submit"],
)

# Shared state for test results
test_state = {
    "response_received": False,
    "response_data": None,
    "error_received": False,
    "error_data": None,
    "test_complete": False,
}


@test_client.on_message(model=DiagnosticResponseMessage)
async def handle_diagnostic_response(ctx: Context, sender: str, msg: DiagnosticResponseMessage):
    """Handle diagnostic response from Diagnostic Agent."""
    logger.info(f"Received diagnostic response from {sender}")
    logger.info(f"  Request ID: {msg.request_id}")
    logger.info(f"  Vehicle ID: {msg.vehicle_id}")
    logger.info(f"  Issue: {msg.issue}")
    logger.info(f"  Severity: {msg.severity}")
    logger.info(f"  Safe to Drive: {msg.safe_to_drive}")
    logger.info(f"  Affected Component: {msg.affected_component}")

    test_state["response_received"] = True
    test_state["response_data"] = msg
    test_state["test_complete"] = True


@test_client.on_message(model=DiagnosticErrorMessage)
async def handle_diagnostic_error(ctx: Context, sender: str, msg: DiagnosticErrorMessage):
    """Handle error response from Diagnostic Agent."""
    logger.error(f"Received error response from {sender}")
    logger.error(f"  Request ID: {msg.request_id}")
    logger.error(f"  Vehicle ID: {msg.vehicle_id}")
    logger.error(f"  Error: {msg.error}")

    test_state["error_received"] = True
    test_state["error_data"] = msg
    test_state["test_complete"] = True


@test_client.on_event("startup")
async def startup(ctx: Context):
    """Send telemetry message to Diagnostic Agent on startup."""
    if not DIAGNOSTIC_AGENT_ADDRESS:
        logger.error("DIAGNOSTIC_AGENT_ADDRESS not set in environment!")
        logger.error("Please start the Diagnostic Agent first and set DIAGNOSTIC_AGENT_ADDRESS")
        return

    logger.info("=" * 60)
    logger.info("Test Client Agent started")
    logger.info(f"Agent Name: {ctx.agent.name}")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)

    logger.info(f"Connecting to Diagnostic Agent at: {DIAGNOSTIC_AGENT_ADDRESS}")

    # Create test telemetry with engine overheating (should trigger CRITICAL)
    request_id = str(uuid4())
    test_telemetry = VehicleTelemetryMessage(
        request_id=request_id,
        vehicle_id="TN37AB1234",
        engine_temperature=122,  # CRITICAL - should trigger engine overheating
        battery_voltage=12.7,
        front_left_tyre_psi=32,
        front_right_tyre_psi=32,
        rear_left_tyre_psi=31,
        rear_right_tyre_psi=31,
        coolant_level=75,
    )

    logger.info("\n" + "=" * 60)
    logger.info("TEST: Sending vehicle telemetry to Diagnostic Agent")
    logger.info("=" * 60)
    logger.info(f"Request ID: {request_id}")
    logger.info(f"Vehicle ID: {test_telemetry.vehicle_id}")
    logger.info(f"Engine Temperature: {test_telemetry.engine_temperature}°C (CRITICAL threshold)")
    logger.info(f"Battery Voltage: {test_telemetry.battery_voltage}V")
    logger.info(f"Coolant Level: {test_telemetry.coolant_level}%")
    logger.info(f"Tyre Pressures: FL={test_telemetry.front_left_tyre_psi}, FR={test_telemetry.front_right_tyre_psi}, RL={test_telemetry.rear_left_tyre_psi}, RR={test_telemetry.rear_right_tyre_psi} PSI")

    # Send the message
    await ctx.send(DIAGNOSTIC_AGENT_ADDRESS, test_telemetry)

    logger.info(f"Message sent. Waiting for response...")

    # Wait for response with timeout
    timeout = 10
    start_time = asyncio.get_event_loop().time()

    while not test_state["test_complete"]:
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed > timeout:
            logger.error(f"Timeout waiting for response after {timeout} seconds")
            logger.error("Make sure the Diagnostic Agent is running at the configured address")
            break
        await asyncio.sleep(0.1)

    # Display results
    if test_state["response_received"]:
        logger.info("\n" + "=" * 60)
        logger.info("RESPONSE RECEIVED")
        logger.info("=" * 60)

        msg = test_state["response_data"]
        logger.info(f"Issue: {msg.issue}")
        logger.info(f"Severity: {msg.severity}")
        logger.info(f"Safe to Drive: {msg.safe_to_drive}")
        logger.info(f"Recommendation: {msg.recommendation}")

        # Verify the response
        expected_severity = "CRITICAL"
        expected_safe_to_drive = False
        expected_issue_substring = "Engine overheating"

        is_correct_severity = msg.severity == expected_severity
        is_correct_safety = msg.safe_to_drive == expected_safe_to_drive
        is_correct_issue = expected_issue_substring in msg.issue

        if is_correct_severity and is_correct_safety and is_correct_issue:
            logger.info("\n" + "=" * 60)
            logger.info("✓ TEST PASSED")
            logger.info("=" * 60)
            logger.info(f"✓ Severity is {expected_severity}")
            logger.info(f"✓ Safe to Drive is {expected_safe_to_drive}")
            logger.info(f"✓ Issue contains '{expected_issue_substring}'")
        else:
            logger.error("\n" + "=" * 60)
            logger.error("✗ TEST FAILED")
            logger.error("=" * 60)
            if not is_correct_severity:
                logger.error(f"✗ Expected severity {expected_severity}, got {msg.severity}")
            if not is_correct_safety:
                logger.error(f"✗ Expected safe_to_drive {expected_safe_to_drive}, got {msg.safe_to_drive}")
            if not is_correct_issue:
                logger.error(f"✗ Expected issue to contain '{expected_issue_substring}', got '{msg.issue}'")

    elif test_state["error_received"]:
        logger.info("\n" + "=" * 60)
        logger.error("✗ TEST FAILED - Error Response")
        logger.info("=" * 60)
        msg = test_state["error_data"]
        logger.error(f"Error: {msg.error}")

    else:
        logger.error("\n" + "=" * 60)
        logger.error("✗ TEST FAILED - No Response Received")
        logger.error("=" * 60)


if __name__ == "__main__":
    if not DIAGNOSTIC_AGENT_ADDRESS:
        logger.error("\n" + "=" * 60)
        logger.error("ERROR: DIAGNOSTIC_AGENT_ADDRESS not configured")
        logger.error("=" * 60)
        logger.error("To run the test client:")
        logger.error("1. Start the Diagnostic Agent: uv run python run_diagnostic_agent.py")
        logger.error("2. Copy the printed agent address")
        logger.error("3. Set it in .env: DIAGNOSTIC_AGENT_ADDRESS=agent1...")
        logger.error("4. Run this test: uv run python tests/agent_client.py")
        logger.error("=" * 60)
        exit(1)

    test_client.run()
