"""Comprehensive integration tests for 20-agent orchestration system."""

import pytest
import asyncio
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://127.0.0.1:8000"
HEALTH_ENDPOINT = f"{BASE_URL}/health"
AUTORESCUE_ENDPOINT = f"{BASE_URL}/api/autorescue/check"

# Test vehicle data sets
NORMAL_VEHICLE = {
    "vehicle_id": "TEST-NORMAL-001",
    "engine_temperature": 95,
    "battery_voltage": 12.6,
    "front_left_tyre_psi": 32,
    "front_right_tyre_psi": 32,
    "rear_left_tyre_psi": 30,
    "rear_right_tyre_psi": 30,
    "coolant_level": 85,
    "latitude": 40.7128,
    "longitude": -74.0060,
}

TYRE_WARNING_VEHICLE = {
    "vehicle_id": "TEST-TYRE-WARNING-001",
    "engine_temperature": 95,
    "battery_voltage": 12.6,
    "front_left_tyre_psi": 28,  # Below 30 = warning
    "front_right_tyre_psi": 32,
    "rear_left_tyre_psi": 29,
    "rear_right_tyre_psi": 30,
    "coolant_level": 85,
    "latitude": 40.7128,
    "longitude": -74.0060,
}

ENGINE_CRITICAL_VEHICLE = {
    "vehicle_id": "TEST-ENGINE-CRIT-001",
    "engine_temperature": 125,  # Critical
    "battery_voltage": 12.6,
    "front_left_tyre_psi": 32,
    "front_right_tyre_psi": 32,
    "rear_left_tyre_psi": 30,
    "rear_right_tyre_psi": 30,
    "coolant_level": 20,  # Low
    "latitude": 40.7128,
    "longitude": -74.0060,
}

BATTERY_ISSUE_VEHICLE = {
    "vehicle_id": "TEST-BATTERY-001",
    "engine_temperature": 95,
    "battery_voltage": 11.2,  # Critical low
    "front_left_tyre_psi": 32,
    "front_right_tyre_psi": 32,
    "rear_left_tyre_psi": 30,
    "rear_right_tyre_psi": 30,
    "coolant_level": 85,
    "latitude": 40.7128,
    "longitude": -74.0060,
}

INVALID_TELEMETRY_VEHICLE = {
    "vehicle_id": "TEST-INVALID-001",
    "engine_temperature": 200,  # Unrealistic
    "battery_voltage": 0,  # Invalid
    "front_left_tyre_psi": -5,  # Impossible
    "front_right_tyre_psi": 32,
    "rear_left_tyre_psi": 30,
    "rear_right_tyre_psi": 30,
    "coolant_level": -10,  # Invalid
    "latitude": 40.7128,
    "longitude": -74.0060,
}


@pytest.fixture
def http_client():
    """Create HTTP client for tests."""
    return httpx.Client(timeout=30.0)


def test_01_health_check(http_client):
    """Test 1: Verify FastAPI is running."""
    try:
        response = http_client.get(HEALTH_ENDPOINT, timeout=5.0)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["status"] == "ok", f"Expected status=ok, got {data.get('status')}"
        logger.info("✓ Test 1: Health check PASSED")
    except Exception as e:
        logger.error(f"✗ Test 1 FAILED: {str(e)}")
        raise


def test_02_normal_vehicle_check(http_client):
    """Test 2: Normal vehicle - should return HEALTHY."""
    response = http_client.post(AUTORESCUE_ENDPOINT, json=NORMAL_VEHICLE)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()

    # Check response structure
    assert "status" in data, "Missing 'status' field"
    assert "diagnosis" in data, "Missing 'diagnosis' field"
    assert "agent_trace" in data, "Missing 'agent_trace' field"

    # For normal vehicle
    assert data["status"] == "HEALTHY", f"Expected HEALTHY, got {data['status']}"
    assert data["diagnosis"]["severity"] in ["NORMAL", "WARNING"], f"Unexpected severity: {data['diagnosis']['severity']}"
    assert data["navigation_allowed"] == True, f"Expected navigation_allowed=true, got {data['navigation_allowed']}"

    # Check trace exists and has entries
    trace = data["agent_trace"]
    assert len(trace) > 5, f"Expected trace with 5+ entries, got {len(trace)}"

    # Verify key agents were called or skipped appropriately
    agent_statuses = {entry["agent"]: entry["status"] for entry in trace}

    # Orchestrator must not be FAILED
    orch_status = agent_statuses.get("Orchestrator", "UNKNOWN")
    assert orch_status != "FAILED", f"Orchestrator FAILED: {[e for e in trace if e['agent'] == 'Orchestrator']}"

    # Must have completed key agents
    assert "Diagnostic Agent" in agent_statuses, "Missing Diagnostic Agent in trace"
    assert "Safety Agent" in agent_statuses, "Missing Safety Agent in trace"
    assert "Verification Agent" in agent_statuses, "Missing Verification Agent in trace"

    # Check statuses are valid
    for entry in trace:
        assert entry["status"] in ["COMPLETED", "SKIPPED", "FAILED", "FALLBACK"], f"Invalid status: {entry['status']}"

    logger.info("✓ Test 2: Normal vehicle check PASSED")
    logger.info(f"  Status: {data['status']}, Trace entries: {len(trace)}")


def test_03_tyre_warning(http_client):
    """Test 3: Tyre warning - should route to Tyre Health."""
    response = http_client.post(AUTORESCUE_ENDPOINT, json=TYRE_WARNING_VEHICLE)
    assert response.status_code == 200
    data = response.json()

    # Should get a warning
    assert data["diagnosis"]["severity"] in ["WARNING", "CRITICAL"]

    # Check Tyre Health was called
    agent_names = [a["agent"] for a in data["agent_trace"]]
    assert "Tyre Health Agent" in agent_names

    logger.info("✓ Test 3: Tyre warning PASSED")


def test_04_engine_critical(http_client):
    """Test 4: Engine critical - should require rescue."""
    response = http_client.post(AUTORESCUE_ENDPOINT, json=ENGINE_CRITICAL_VEHICLE)
    assert response.status_code == 200
    data = response.json()

    # Should get critical diagnosis
    assert data["diagnosis"]["severity"] == "CRITICAL"
    assert data["diagnosis"]["safe_to_drive"] == False

    # Navigation not allowed
    assert data["navigation_allowed"] == False

    # Check Engine Health was called
    agent_names = [a["agent"] for a in data["agent_trace"]]
    assert "Engine Health Agent" in agent_names

    logger.info("✓ Test 4: Engine critical PASSED")


def test_05_battery_issue(http_client):
    """Test 5: Battery issue - should route battery specialist."""
    response = http_client.post(AUTORESCUE_ENDPOINT, json=BATTERY_ISSUE_VEHICLE)
    assert response.status_code == 200
    data = response.json()

    # Should identify battery issue
    assert "battery" in data["diagnosis"]["affected_component"].lower() or data["diagnosis"]["severity"] in ["CRITICAL", "WARNING"]

    # Battery Health should be called
    agent_names = [a["agent"] for a in data["agent_trace"]]
    assert "Battery Health Agent" in agent_names

    logger.info("✓ Test 5: Battery issue PASSED")


def test_06_invalid_telemetry(http_client):
    """Test 6: Invalid telemetry - should handle gracefully."""
    response = http_client.post(AUTORESCUE_ENDPOINT, json=INVALID_TELEMETRY_VEHICLE)

    # Should not crash
    assert response.status_code == 200 or response.status_code == 422

    if response.status_code == 200:
        data = response.json()
        # Should have some response
        assert "diagnosis" in data or "error" in str(data)

    logger.info("✓ Test 6: Invalid telemetry handled")


def test_07_agent_trace_completeness(http_client):
    """Test 7: Verify agent trace is complete and realistic."""
    response = http_client.post(AUTORESCUE_ENDPOINT, json=NORMAL_VEHICLE)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()

    trace = data["agent_trace"]

    # Must have realistic trace (not just one FAILED entry)
    assert len(trace) >= 8, f"Expected 8+ trace entries for normal check, got {len(trace)}"

    # Orchestrator must not be FAILED
    orchestrator_entry = next((e for e in trace if "Orchestrator" in e["agent"]), None)
    assert orchestrator_entry, "Missing Orchestrator in trace"
    assert orchestrator_entry["status"] != "FAILED", f"Orchestrator FAILED: {orchestrator_entry}"

    # Count by status
    completed = sum(1 for e in trace if e["status"] == "COMPLETED")
    failed = sum(1 for e in trace if e["status"] == "FAILED")

    assert completed >= 5, f"Expected 5+ COMPLETED, got {completed}"
    assert failed == 0, f"Expected 0 FAILED entries, got {failed}"

    # Each trace entry must have required fields
    for entry in trace:
        assert "agent" in entry, f"Missing 'agent' in trace entry: {entry}"
        assert "status" in entry, f"Missing 'status' in trace entry: {entry}"
        assert "summary" in entry, f"Missing 'summary' in trace entry: {entry}"
        assert entry["status"] in ["COMPLETED", "SKIPPED", "FAILED", "FALLBACK"], f"Invalid status: {entry['status']}"

    logger.info(f"✓ Test 7: Agent trace completeness PASSED ({len(trace)} entries, {completed} completed, {failed} failed)")
    logger.info("  Trace entries:")
    for entry in trace:
        logger.info(f"    - {entry['agent']}: {entry['status']} ({entry['summary']})")


def test_08_response_model_validity(http_client):
    """Test 8: Response follows AutoRescueApiResponseExtended model."""
    response = http_client.post(AUTORESCUE_ENDPOINT, json=NORMAL_VEHICLE)
    assert response.status_code == 200
    data = response.json()

    # Required fields
    assert "request_id" in data
    assert "vehicle_id" in data
    assert "status" in data
    assert "diagnosis" in data
    assert "navigation_allowed" in data
    assert "agent_trace" in data

    # Diagnosis fields
    diag = data["diagnosis"]
    assert "issue" in diag
    assert "affected_component" in diag
    assert "severity" in diag
    assert "safe_to_drive" in diag

    logger.info("✓ Test 8: Response model validity PASSED")


def test_09_concurrent_specialists(http_client):
    """Test 9: Multiple specialists execute for complex scenario."""
    response = http_client.post(AUTORESCUE_ENDPOINT, json=ENGINE_CRITICAL_VEHICLE)
    assert response.status_code == 200
    data = response.json()

    # Should call multiple specialists
    agents_called = [
        entry["agent"] for entry in data["agent_trace"]
        if entry["status"] == "COMPLETED"
    ]

    # For critical engine, multiple agents should execute
    assert len(agents_called) >= 3  # Orchestrator + Diagnostic + at least Safety/Engine

    logger.info(f"✓ Test 9: Multiple specialists executed ({len(agents_called)} agents)")


def test_10_safety_never_weaken(http_client):
    """Test 10: Safety never weakened by other agents."""
    response = http_client.post(AUTORESCUE_ENDPOINT, json=ENGINE_CRITICAL_VEHICLE)
    assert response.status_code == 200
    data = response.json()

    # If diagnosis is CRITICAL, safety must reflect this
    diagnosis_critical = data["diagnosis"]["severity"] == "CRITICAL"
    safe_to_drive = data["diagnosis"]["safe_to_drive"]

    if diagnosis_critical:
        # Cannot have critical diagnosis but safe to drive for engine/safety issues
        if data["diagnosis"]["affected_component"] in ["engine", "cooling_system"]:
            assert safe_to_drive == False

    logger.info("✓ Test 10: Safety constraints maintained")


# Run all tests
if __name__ == "__main__":
    print("\n" + "="*60)
    print("AutoRescue AI - 20-Agent Integration Test Suite")
    print("="*60 + "\n")

    client = httpx.Client(timeout=30.0)

    tests = [
        ("Health Check", test_01_health_check),
        ("Normal Vehicle", test_02_normal_vehicle_check),
        ("Tyre Warning", test_03_tyre_warning),
        ("Engine Critical", test_04_engine_critical),
        ("Battery Issue", test_05_battery_issue),
        ("Invalid Telemetry", test_06_invalid_telemetry),
        ("Trace Completeness", test_07_agent_trace_completeness),
        ("Response Validity", test_08_response_model_validity),
        ("Concurrent Specialists", test_09_concurrent_specialists),
        ("Safety Constraints", test_10_safety_never_weaken),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func(client)
            passed += 1
        except Exception as e:
            logger.error(f"✗ Test Failed: {name} - {str(e)}")
            failed += 1

    client.close()

    print("\n" + "="*60)
    print(f"Results: {passed} PASSED, {failed} FAILED")
    print("="*60 + "\n")

    if failed == 0:
        print("✓ ALL TESTS PASSED!")
    else:
        print(f"✗ {failed} test(s) failed")
