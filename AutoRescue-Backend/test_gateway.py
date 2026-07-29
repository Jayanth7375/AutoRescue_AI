"""Test FastAPI gateway integration with Orchestrator Agent."""

import asyncio
import logging
import httpx

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

GATEWAY_URL = "http://127.0.0.1:8000"


async def test_scenario(name: str, payload: dict, expected_status: str) -> bool:
    """Test a single scenario."""
    logger.info("\n" + "=" * 60)
    logger.info(f"SCENARIO: {name}")
    logger.info("=" * 60)

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{GATEWAY_URL}/api/autorescue/check",
                json=payload,
            )

        logger.info(f"HTTP Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"Status: {data.get('status')}")
            logger.info(f"Diagnosis Severity: {data.get('diagnosis', {}).get('severity')}")
            logger.info(f"Service Centres: {len(data.get('service_centres', []))}")
            logger.info(f"Navigation Allowed: {data.get('navigation_allowed')}")

            if data.get('rescue'):
                logger.info(f"Rescue Type: {data['rescue'].get('assistance_type')}")
                logger.info(f"Tow Required: {data['rescue'].get('tow_required')}")

            # Check expected status
            if data.get('status') == expected_status:
                logger.info(f"✓ Status matches expected: {expected_status}")
                return True
            else:
                logger.error(f"✗ Expected {expected_status}, got {data.get('status')}")
                return False

        else:
            error = response.json()
            logger.error(f"Error: {error.get('detail', 'Unknown error')}")
            return False

    except Exception as e:
        logger.error(f"Exception: {str(e)}", exc_info=True)
        return False


async def run_tests():
    """Run all test scenarios."""
    logger.info("=" * 60)
    logger.info("FastAPI Gateway Test Suite")
    logger.info("=" * 60)
    logger.info(f"Gateway URL: {GATEWAY_URL}")

    # Wait for gateway to be ready
    logger.info("\nWaiting for gateway to be ready...")
    for attempt in range(10):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{GATEWAY_URL}/health", timeout=2.0)
                if response.status_code == 200:
                    logger.info("✓ Gateway is ready")
                    break
        except:
            if attempt < 9:
                await asyncio.sleep(1)
                continue
            else:
                logger.error("✗ Gateway not responding")
                return

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
    logger.info("\n" + "=" * 60)
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
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {name}")

    logger.info("\n" + "=" * 60)
    if passed == total:
        logger.info(f"✓ ALL GATEWAY TESTS PASSED ({passed}/{total})")
        logger.info("=" * 60)
        logger.info("HTTP gateway successfully routes to Orchestrator and returns unified responses")
    else:
        logger.error(f"✗ SOME TESTS FAILED ({passed} passed, {total - passed} failed)")
        logger.error("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_tests())
