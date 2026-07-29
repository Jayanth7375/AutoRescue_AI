"""Test client for Service uAgent."""

import os
import sys
import asyncio
import logging
from uuid import uuid4

from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    ServiceRequestMessage,
    ServiceResponseMessage,
    ServiceErrorMessage,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
SERVICE_AGENT_ADDRESS = os.getenv("SERVICE_AGENT_ADDRESS")
TEST_SERVICE_LATITUDE = float(os.getenv("TEST_SERVICE_LATITUDE", "19.0760"))
TEST_SERVICE_LONGITUDE = float(os.getenv("TEST_SERVICE_LONGITUDE", "72.8777"))

if not SERVICE_AGENT_ADDRESS:
    logger.error("\n" + "=" * 60)
    logger.error("ERROR: SERVICE_AGENT_ADDRESS not configured")
    logger.error("=" * 60)
    logger.error("Please:")
    logger.error("1. Start Service Agent: uv run python run_service_agent.py")
    logger.error("2. Copy the printed agent address")
    logger.error("3. Update .env: SERVICE_AGENT_ADDRESS=<address>")
    logger.error("4. Then run: uv run python test_service_agent.py")
    logger.error("=" * 60)
    sys.exit(1)

# Create test client agent
TEST_CLIENT_PORT = int(os.getenv("TEST_CLIENT_PORT", "8012"))

test_client = Agent(
    name="service_test_client",
    seed="service-test-client-seed",
    port=8014,
    endpoint=[f"http://127.0.0.1:8014/submit"],
)

# Shared state
test_result = {
    "response_received": False,
    "error_received": False,
    "data": None,
    "done": False,
}


@test_client.on_message(model=ServiceResponseMessage)
async def handle_response(ctx: Context, sender: str, msg: ServiceResponseMessage):
    """Handle service response."""
    logger.info("\n" + "=" * 60)
    logger.info("✓ RESPONSE RECEIVED FROM SERVICE AGENT")
    logger.info("=" * 60)
    logger.info(f"From: {sender}")
    logger.info(f"Request ID: {msg.request_id}")
    logger.info(f"Vehicle ID: {msg.vehicle_id}")
    logger.info(f"Issue: {msg.issue}")
    logger.info(f"Severity: {msg.severity}")
    logger.info(f"Navigation Allowed: {msg.navigation_allowed}")
    logger.info(f"Tow Recommended: {msg.tow_recommended}")
    logger.info(f"Service Centres Found: {len(msg.centres)}")

    if msg.centres:
        logger.info("\n" + "-" * 60)
        logger.info("TOP SERVICE CENTRES (Ranked)")
        logger.info("-" * 60)

        for i, centre in enumerate(msg.centres[:5], 1):
            logger.info(f"\n{i}. {centre.name}")
            logger.info(f"   Address: {centre.address}")
            logger.info(f"   Distance: {centre.distance_km} km")
            logger.info(f"   Priority Score: {centre.priority_score}/100")
            logger.info(f"   Rating: {centre.rating} ({centre.review_count} reviews)" if centre.rating else "   Rating: Not available")
            logger.info(f"   Open: {'Yes' if centre.is_open else 'No' if centre.is_open is not None else 'Unknown'}")
            logger.info(f"   Reason: {centre.recommendation_reason}")

    test_result["response_received"] = True
    test_result["data"] = msg
    test_result["done"] = True

    # Verify test expectations
    verify_response(msg)


@test_client.on_message(model=ServiceErrorMessage)
async def handle_error(ctx: Context, sender: str, msg: ServiceErrorMessage):
    """Handle error response."""
    logger.error("\n" + "=" * 60)
    logger.error("✗ ERROR RESPONSE RECEIVED")
    logger.error("=" * 60)
    logger.error(f"From: {sender}")
    logger.error(f"Error: {msg.error}")

    test_result["error_received"] = True
    test_result["data"] = msg
    test_result["done"] = True


def verify_response(msg: ServiceResponseMessage):
    """Verify response meets expectations."""
    logger.info("\n" + "=" * 60)
    logger.info("VERIFICATION")
    logger.info("=" * 60)

    checks = []

    # Check 1: Has centres
    if msg.centres:
        logger.info("✓ Service centres returned")
        checks.append(True)
    else:
        logger.error("✗ No service centres in response")
        checks.append(False)

    # Check 2: Centres are sorted by priority score
    if msg.centres:
        scores = [c.priority_score for c in msg.centres]
        is_sorted = all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1))
        if is_sorted:
            logger.info("✓ Centres sorted by priority score (descending)")
            checks.append(True)
        else:
            logger.error("✗ Centres not properly sorted")
            checks.append(False)

    # Check 3: All centres have required fields
    if msg.centres:
        all_have_fields = all(
            hasattr(c, 'name') and
            hasattr(c, 'distance_km') and
            hasattr(c, 'priority_score') and
            hasattr(c, 'recommendation_reason')
            for c in msg.centres
        )
        if all_have_fields:
            logger.info("✓ All centres have required fields")
            checks.append(True)
        else:
            logger.error("✗ Some centres missing required fields")
            checks.append(False)

    # Check 4: Navigation/tow logic
    if msg.navigation_allowed and msg.tow_recommended:
        logger.error("✗ Contradiction: navigation_allowed=true but tow_recommended=true")
        checks.append(False)
    else:
        logger.info("✓ Navigation/tow logic consistent")
        checks.append(True)

    # Overall result
    if all(checks):
        logger.info("\n" + "=" * 60)
        logger.info("✓ ALL VERIFICATION CHECKS PASSED")
        logger.info("=" * 60)
    else:
        logger.error("\n" + "=" * 60)
        logger.error("✗ SOME VERIFICATION CHECKS FAILED")
        logger.error("=" * 60)


@test_client.on_event("startup")
async def startup(ctx: Context):
    """Send service request on startup."""
    logger.info("=" * 60)
    logger.info("Service Test Client started")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)

    logger.info(f"Service Agent: {SERVICE_AGENT_ADDRESS}")

    # Test Scenario 1: Tyre issue (WARNING, safe to drive)
    request_id = str(uuid4())
    service_request = ServiceRequestMessage(
        request_id=request_id,
        vehicle_id="TN37AB1234",
        issue="Front Left Tyre pressure low",
        affected_component="front_left_tyre",
        severity="WARNING",
        safe_to_drive=True,
        latitude=TEST_SERVICE_LATITUDE,
        longitude=TEST_SERVICE_LONGITUDE,
    )

    logger.info("\n" + "=" * 60)
    logger.info("TEST SCENARIO 1")
    logger.info("=" * 60)
    logger.info(f"Request ID: {request_id}")
    logger.info(f"Vehicle ID: {service_request.vehicle_id}")
    logger.info(f"Issue: {service_request.issue}")
    logger.info(f"Affected Component: {service_request.affected_component}")
    logger.info(f"Severity: {service_request.severity}")
    logger.info(f"Safe to Drive: {service_request.safe_to_drive}")
    logger.info(f"Location: {service_request.latitude}, {service_request.longitude}")
    logger.info("\nExpected Behaviour:")
    logger.info("  - Service centres returned")
    logger.info("  - Sorted by priority score")
    logger.info("  - navigation_allowed = true")
    logger.info("  - tow_recommended = false")

    logger.info("\nSending request...")
    await ctx.send(SERVICE_AGENT_ADDRESS, service_request)

    # Wait for response
    logger.info("Waiting for response...")
    start_time = asyncio.get_event_loop().time()

    while not test_result["done"]:
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed > 30:
            logger.error("Timeout waiting for response after 30 seconds")
            logger.error("Make sure the Service Agent is running at the configured address")
            test_result["done"] = True
            break
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    logger.info("\n" + "=" * 60)
    logger.info("Phase 3: Service uAgent Test")
    logger.info("=" * 60)
    logger.info(f"Service Agent: {SERVICE_AGENT_ADDRESS}")
    logger.info(f"Test Location: {TEST_SERVICE_LATITUDE}, {TEST_SERVICE_LONGITUDE}")

    try:
        test_client.run()
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
