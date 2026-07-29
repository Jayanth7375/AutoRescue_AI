"""Test AutoRescue AI chatbot API."""

import asyncio
import logging
import httpx

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

GATEWAY_URL = "http://127.0.0.1:8000"


async def test_chat(name: str, message: str, context: dict) -> bool:
    """Test a single chat scenario."""
    logger.info("\n" + "=" * 60)
    logger.info(f"CHAT TEST: {name}")
    logger.info("=" * 60)
    logger.info(f"Message: {message}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{GATEWAY_URL}/api/chat",
                json={
                    "message": message,
                    "vehicle_id": "TN37AB1234",
                    "context": context,
                },
            )

        logger.info(f"HTTP Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            reply = data.get('reply', '')
            actions = data.get('suggested_actions', [])

            logger.info(f"Reply: {reply[:200]}...")
            if actions:
                logger.info(f"Suggested Actions: {actions}")

            # Verify response has required fields
            if reply:
                logger.info("✓ Chat response successful")
                return True
            else:
                logger.error("✗ Reply field is empty")
                return False
        else:
            logger.error(f"✗ Error: {response.text[:200]}")
            return False

    except Exception as e:
        logger.error(f"✗ Exception: {str(e)}", exc_info=True)
        return False


async def run_tests():
    """Run all chat tests."""
    logger.info("=" * 60)
    logger.info("AutoRescue AI Chatbot Test Suite")
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

    # Test 1: General question
    test1_pass = await test_chat(
        "General Question",
        "Hello",
        {}
    )

    # Test 2: Warning context
    test2_pass = await test_chat(
        "Warning Context (Tyre Pressure)",
        "Can I drive my vehicle?",
        {
            "status": "SERVICE_RECOMMENDED",
            "diagnosis": {
                "issue": "Front left tyre pressure low",
                "affected_component": "front_left_tyre",
                "severity": "WARNING",
                "safe_to_drive": True,
                "recommendation": "Inflate tyre to recommended pressure.",
            },
            "navigation_allowed": True,
            "rescue": {"tow_required": False}
        }
    )

    # Test 3: Critical context
    test3_pass = await test_chat(
        "Critical Context (Engine Overheating)",
        "Can I continue driving?",
        {
            "status": "ASSISTANCE_REQUIRED",
            "diagnosis": {
                "issue": "Engine overheating",
                "affected_component": "Engine",
                "severity": "CRITICAL",
                "safe_to_drive": False,
                "recommendation": "Stop the vehicle safely.",
            },
            "navigation_allowed": False,
            "rescue": {
                "assistance_required": True,
                "assistance_type": "TOW",
                "tow_required": True,
            }
        }
    )

    # Test 4: No context (no vehicle check yet)
    test4_pass = await test_chat(
        "No Vehicle Check Yet",
        "What should I know about my vehicle?",
        {}
    )

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST RESULTS")
    logger.info("=" * 60)

    tests = [
        ("General Question", test1_pass),
        ("Warning Context", test2_pass),
        ("Critical Context", test3_pass),
        ("No Context", test4_pass),
    ]

    passed = sum(1 for _, p in tests if p)
    total = len(tests)

    for name, result in tests:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {name}")

    logger.info("\n" + "=" * 60)
    if passed == total:
        logger.info(f"✓ ALL CHAT TESTS PASSED ({passed}/{total})")
        logger.info("=" * 60)
    else:
        logger.error(f"✗ SOME TESTS FAILED ({passed} passed, {total - passed} failed)")
        logger.error("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_tests())
