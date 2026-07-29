"""Test Orchestrator synchronous query handler - direct uAgent communication."""

import os
import asyncio
import logging
from uuid import uuid4

from uagents.communication import send_sync_message
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

ORCHESTRATOR_AGENT_ADDRESS = os.getenv("ORCHESTRATOR_AGENT_ADDRESS")

if not ORCHESTRATOR_AGENT_ADDRESS:
    logger.error("ERROR: ORCHESTRATOR_AGENT_ADDRESS not configured in .env")
    exit(1)


async def test_scenario(name: str, payload: dict, expected_status: str) -> bool:
    """Test a single scenario."""
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"SCENARIO: {name}")
    logger.info("=" * 60)

    try:
        request_id = str(uuid4())

        msg = AutoRescueRequestMessage(
            request_id=request_id,
            vehicle_id=payload["vehicle_id"],
            engine_temperature=payload["engine_temperature"],
            battery_voltage=payload["battery_voltage"],
            front_left_tyre_psi=payload["front_left_tyre_psi"],
            front_right_tyre_psi=payload["front_right_tyre_psi"],
            rear_left_tyre_psi=payload["rear_left_tyre_psi"],
            rear_right_tyre_psi=payload["rear_right_tyre_psi"],
            coolant_level=payload["coolant_level"],
            latitude=payload["latitude"],
            longitude=payload["longitude"],
        )

        logger.info(f"Sending synchronous query to {ORCHESTRATOR_AGENT_ADDRESS[:30]}...")
        logger.info(f"Request ID: {request_id}")

        result = await send_sync_message(
            destination=ORCHESTRATOR_AGENT_ADDRESS,
            message=msg,
            response_type=AutoRescueResponseMessage,
            timeout=120,
        )

        logger.info(f"Response type: {type(result).__name__}")

        if isinstance(result, AutoRescueResponseMessage):
            logger.info(f"Status: {result.status}")
            logger.info(f"Diagnosis Severity: {result.diagnosis.severity}")
            logger.info(f"Safe to Drive: {result.diagnosis.safe_to_drive}")
            logger.info(f"Service Centres: {len(result.service_centres)}")
            logger.info(f"Navigation Allowed: {result.navigation_allowed}")

            if result.rescue:
                logger.info(f"Rescue Type: {result.rescue.assistance_type}")
                logger.info(f"Tow Required: {result.rescue.tow_required}")

            # Check expected status
            if result.status == expected_status:
                logger.info(f"OK Status matches expected: {expected_status}")
                return True
            else:
                logger.error(f"FAIL Expected {expected_status}, got {result.status}")
                return False

        elif isinstance(result, AutoRescueErrorMessage):
            logger.error(f"FAIL Orchestrator error: {result.error}")
            return False

        else:
            logger.error(f"FAIL Unexpected response type: {type(result).__name__}")
            return False

    except Exception as e:
        logger.error(f"FAIL Exception: {str(e)}", exc_info=True)
        return False


async def run_tests():
    """Run all test scenarios."""
    logger.info("=" * 60)
    logger.info("Orchestrator Synchronous Query Test Suite")
    logger.info("=" * 60)
    logger.info(f"Orchestrator Address: {ORCHESTRATOR_AGENT_ADDRESS}")
    logger.info("")

    # Test 1: Healthy Vehicle
    test1_pass = await test_scenario(
        "Healthy Vehicle (No Service/Rescue)",
        {
            "vehicle_id": "TN37AB1234",
            "engine_temperature": 95,
            "battery_voltage": 12.7,
            "front_left_tyre_psi": 32,
            "front_right_tyre_psi": 32,
            "rear_left_tyre_psi": 31,
            "rear_right_tyre_psi": 31,
            "coolant_level": 75,
            "latitude": 19.076,
            "longitude": 72.8777,
        },
        "HEALTHY",
    )

    # Test 2: Tyre Warning
    test2_pass = await test_scenario(
        "Tyre Warning (Service Recommended)",
        {
            "vehicle_id": "TN37AB1234",
            "engine_temperature": 95,
            "battery_voltage": 12.7,
            "front_left_tyre_psi": 28,
            "front_right_tyre_psi": 32,
            "rear_left_tyre_psi": 31,
            "rear_right_tyre_psi": 31,
            "coolant_level": 75,
            "latitude": 19.076,
            "longitude": 72.8777,
        },
        "SERVICE_RECOMMENDED",
    )

    # Test 3: Engine Overheating
    test3_pass = await test_scenario(
        "Engine Overheating (Assistance Required)",
        {
            "vehicle_id": "TN37AB1234",
            "engine_temperature": 122,
            "battery_voltage": 12.7,
            "front_left_tyre_psi": 32,
            "front_right_tyre_psi": 32,
            "rear_left_tyre_psi": 31,
            "rear_right_tyre_psi": 31,
            "coolant_level": 75,
            "latitude": 19.076,
            "longitude": 72.8777,
        },
        "ASSISTANCE_REQUIRED",
    )

    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("TEST RESULTS")
    logger.info("=" * 60)

    tests = [
        ("Healthy Vehicle", test1_pass),
        ("Tyre Warning", test2_pass),
        ("Engine Overheating", test3_pass),
    ]

    passed = sum(1 for _, p in tests if p)
    total = len(tests)

    for name, result in tests:
        status = "OK PASS" if result else "FAIL"
        logger.info(f"{status}: {name}")

    logger.info("")
    logger.info("=" * 60)
    if passed == total:
        logger.info(f"OK ALL ORCHESTRATOR SYNC TESTS PASSED ({passed}/{total})")
        logger.info("=" * 60)
        logger.info("Synchronous query handler is working correctly")
        return 0
    else:
        logger.error(f"FAIL SOME TESTS FAILED ({passed} passed, {total - passed} failed)")
        logger.error("=" * 60)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_tests())
    exit(exit_code)
