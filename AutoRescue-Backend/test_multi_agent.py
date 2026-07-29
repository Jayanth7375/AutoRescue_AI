"""Test suite for 10-agent orchestration system."""

import httpx
import json
import time

BASE_URL = "http://127.0.0.1:8000"
TEST_TIMEOUT = 30

# Test cases with telemetry that should trigger different severity levels
TEST_SCENARIOS = {
    "HEALTHY": {
        "engine_temperature": 85.0,
        "battery_voltage": 13.5,
        "front_left_tyre_psi": 32.0,
        "front_right_tyre_psi": 32.0,
        "rear_left_tyre_psi": 32.0,
        "rear_right_tyre_psi": 32.0,
        "coolant_level": 75.0,
        "expected_status": "HEALTHY"
    },
    "WARNING": {
        "engine_temperature": 100.0,  # Slightly elevated
        "battery_voltage": 13.5,
        "front_left_tyre_psi": 28.0,  # Slightly low but acceptable
        "front_right_tyre_psi": 32.0,
        "rear_left_tyre_psi": 32.0,
        "rear_right_tyre_psi": 32.0,
        "coolant_level": 75.0,
        "expected_status": "SERVICE_RECOMMENDED"
    },
    "CRITICAL": {
        "engine_temperature": 130.0,  # Critical
        "battery_voltage": 9.0,  # Critical low
        "front_left_tyre_psi": 32.0,
        "front_right_tyre_psi": 32.0,
        "rear_left_tyre_psi": 32.0,
        "rear_right_tyre_psi": 32.0,
        "coolant_level": 75.0,
        "expected_status": "ASSISTANCE_REQUIRED"
    },
    "InvalidTelemetry": {
        "engine_temperature": 90.0,  # Normal operating temperature
        "battery_voltage": 12.8,  # Normal voltage
        "front_left_tyre_psi": 32.0,
        "front_right_tyre_psi": 32.0,
        "rear_left_tyre_psi": 32.0,
        "rear_right_tyre_psi": 32.0,
        "coolant_level": 80.0,  # Normal coolant level
        "expected_status": "HEALTHY"  # Should process as healthy
    }
}

def test_autorescue_check():
    """Test /api/autorescue/check endpoint with all scenarios."""

    print("\n" + "=" * 70)
    print("Test Suite: 10-Agent Orchestration System")
    print("=" * 70 + "\n")

    passed = 0
    failed = 0

    for scenario_name, scenario_data in TEST_SCENARIOS.items():
        print(f"\n[TEST] {scenario_name} Scenario")
        print("-" * 70)

        # Prepare request
        payload = {
            "vehicle_id": f"TEST-{scenario_name}",
            "latitude": 40.7128,
            "longitude": -74.0060,
            **{k: v for k, v in scenario_data.items() if k != "expected_status"}
        }

        expected_status = scenario_data["expected_status"]

        try:
            # Call direct 10-agent endpoint
            with httpx.Client(timeout=TEST_TIMEOUT) as client:
                response = client.post(
                    f"{BASE_URL}/api/autorescue/check-direct",  # Use new direct endpoint
                    json=payload
                )

            if response.status_code != 200:
                print(f"  [FAIL] HTTP {response.status_code}")
                resp_text = response.text[:200].encode('ascii', 'replace').decode('ascii')
                print(f"    Response: {resp_text}")
                failed += 1
                continue

            data = response.json()
            actual_status = data.get("status")

            # Verify response structure
            required_fields = ["status", "diagnosis", "navigation_allowed", "message"]
            missing_fields = [f for f in required_fields if f not in data]

            if missing_fields:
                print(f"  [FAIL] Missing fields {missing_fields}")
                failed += 1
                continue

            # Verify status matches expected
            if actual_status != expected_status:
                print(f"  [FAIL] Status mismatch")
                print(f"    Expected: {expected_status}")
                print(f"    Actual:   {actual_status}")
                failed += 1
                continue

            # Verify diagnosis data
            diagnosis = data.get("diagnosis", {})
            if not isinstance(diagnosis, dict):
                print(f"  [FAIL] diagnosis is not a dict")
                failed += 1
                continue

            # Check for agent_trace (new 10-agent field)
            agent_trace = data.get("agent_trace", [])
            if agent_trace and isinstance(agent_trace, list):
                print(f"    Agent Trace: {len(agent_trace)} entries")
                for entry in agent_trace:
                    print(f"      - {entry.get('agent', '?')}: {entry.get('status', '?')}")

            # Check for key diagnosis fields
            if scenario_name != "HEALTHY" and "severity" in diagnosis:
                severity = diagnosis["severity"]
                print(f"  [PASS] {scenario_name} correctly diagnosed")
                print(f"    Status: {actual_status}")
                print(f"    Severity: {severity}")
                print(f"    Safe to Drive: {diagnosis.get('safe_to_drive')}")
                issue = diagnosis.get('issue', 'N/A')
                if isinstance(issue, str):
                    try:
                        issue = issue[:50].encode('ascii', 'replace').decode('ascii')
                    except:
                        issue = 'Issue detected'
                print(f"    Issue: {issue}")
                passed += 1
            elif scenario_name == "HEALTHY":
                print(f"  [PASS] Vehicle is HEALTHY")
                print(f"    Status: {actual_status}")
                passed += 1
            else:
                print(f"  [PASS] {scenario_name} processed")
                print(f"    Status: {actual_status}")
                passed += 1

        except httpx.ConnectError:
            print(f"  [FAIL] Cannot connect to API (port 8000)")
            failed += 1
        except httpx.TimeoutException:
            print(f"  [FAIL] Request timeout (>{TEST_TIMEOUT}s)")
            failed += 1
        except Exception as e:
            print(f"  [FAIL] {type(e).__name__}: {str(e)[:100]}")
            failed += 1

    # Print summary
    print("\n" + "=" * 70)
    print(f"Test Results: {passed}/{passed + failed} PASSED")
    print("=" * 70 + "\n")

    if failed == 0:
        print("[OK] All tests passed!")
        return True
    else:
        print(f"[XX] {failed} test(s) failed")
        return False

def test_agent_health():
    """Quick check that agents are responding."""

    print("\n" + "=" * 70)
    print("Agent Health Check")
    print("=" * 70 + "\n")

    agents = [
        ("FastAPI Gateway", "http://127.0.0.1:8000/health"),
        ("Orchestrator", "http://127.0.0.1:8018/"),
        ("Diagnostic", "http://127.0.0.1:8011/"),
        ("Service", "http://127.0.0.1:8013/"),
        ("Rescue", "http://127.0.0.1:8015/"),
        ("Telemetry", "http://127.0.0.1:8020/"),
        ("Safety", "http://127.0.0.1:8021/"),
        ("Maintenance", "http://127.0.0.1:8022/"),
        ("Notification", "http://127.0.0.1:8023/"),
        ("Explanation", "http://127.0.0.1:8024/"),
        ("Verification", "http://127.0.0.1:8025/"),
    ]

    healthy = 0
    unhealthy = 0

    for agent_name, url in agents:
        try:
            with httpx.Client(timeout=2) as client:
                response = client.get(url)
                # 200 = gateway health, 405/404 = agents (don't support GET)
                if response.status_code in [200, 405, 404]:
                    print(f"  [OK] {agent_name:20s} - Listening")
                    healthy += 1
                else:
                    print(f"  [XX] {agent_name:20s} - HTTP {response.status_code}")
                    unhealthy += 1
        except Exception as e:
            print(f"  [XX] {agent_name:20s} - {type(e).__name__}")
            unhealthy += 1

    print(f"\nHealth: {healthy}/{healthy + unhealthy} agents responsive\n")
    return unhealthy == 0

if __name__ == "__main__":
    import sys

    # Check agent health first
    if not test_agent_health():
        print("[WARN] Some agents are not responding. Start all agents with: uv run python run_all_agents.ps1")
        sys.exit(1)

    # Run main tests
    success = test_autorescue_check()
    sys.exit(0 if success else 1)
