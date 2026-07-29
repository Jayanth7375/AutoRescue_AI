#!/usr/bin/env python3
"""Test script for AutoRescue AI Backend API."""

import json
import time
import subprocess
import requests

BASE_URL = "http://127.0.0.1:8000"


def test_health():
    """Test health endpoint."""
    print("\n=== Testing /health endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_diagnose_healthy():
    """Test healthy vehicle scenario."""
    print("\n=== Test 1: Healthy Vehicle ===")
    payload = {
        "vehicle_id": "TN37AB1234",
        "engine_temperature": 95,
        "battery_voltage": 12.7,
        "front_left_tyre_psi": 32,
        "front_right_tyre_psi": 32,
        "rear_left_tyre_psi": 31,
        "rear_right_tyre_psi": 31,
        "coolant_level": 75,
    }
    try:
        response = requests.post(f"{BASE_URL}/diagnose", json=payload, timeout=5)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        assert result["severity"] == "NORMAL", "Expected NORMAL severity"
        assert result["safe_to_drive"] == True, "Expected safe to drive"
        print("✓ Test passed")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_diagnose_engine_overheating():
    """Test engine overheating scenario."""
    print("\n=== Test 2: Engine Overheating ===")
    payload = {
        "vehicle_id": "TN37AB1234",
        "engine_temperature": 122,
        "battery_voltage": 12.6,
        "front_left_tyre_psi": 32,
        "front_right_tyre_psi": 32,
        "rear_left_tyre_psi": 31,
        "rear_right_tyre_psi": 31,
        "coolant_level": 70,
    }
    try:
        response = requests.post(f"{BASE_URL}/diagnose", json=payload, timeout=5)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        assert result["severity"] == "CRITICAL", "Expected CRITICAL severity"
        assert result["safe_to_drive"] == False, "Expected unsafe to drive"
        assert "Engine overheating" in result["issue"], "Expected engine overheating issue"
        print("✓ Test passed")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_diagnose_critical_tyre():
    """Test critical tyre scenario."""
    print("\n=== Test 3: Critical Tyre Pressure ===")
    payload = {
        "vehicle_id": "TN37AB1234",
        "engine_temperature": 95,
        "battery_voltage": 12.6,
        "front_left_tyre_psi": 20,
        "front_right_tyre_psi": 32,
        "rear_left_tyre_psi": 31,
        "rear_right_tyre_psi": 31,
        "coolant_level": 70,
    }
    try:
        response = requests.post(f"{BASE_URL}/diagnose", json=payload, timeout=5)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        assert result["severity"] == "CRITICAL", "Expected CRITICAL severity"
        assert result["safe_to_drive"] == False, "Expected unsafe to drive"
        print("✓ Test passed")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_diagnose_critical_coolant():
    """Test critical coolant scenario."""
    print("\n=== Test 4: Critical Coolant Level ===")
    payload = {
        "vehicle_id": "TN37AB1234",
        "engine_temperature": 95,
        "battery_voltage": 12.6,
        "front_left_tyre_psi": 32,
        "front_right_tyre_psi": 32,
        "rear_left_tyre_psi": 31,
        "rear_right_tyre_psi": 31,
        "coolant_level": 20,
    }
    try:
        response = requests.post(f"{BASE_URL}/diagnose", json=payload, timeout=5)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        assert result["severity"] == "CRITICAL", "Expected CRITICAL severity"
        assert result["safe_to_drive"] == False, "Expected unsafe to drive"
        print("✓ Test passed")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Starting AutoRescue AI Backend Tests")
    print("=" * 50)

    # Start the server
    print("Starting server...")
    proc = subprocess.Popen(
        ["uv", "run", "uvicorn", "main:app", "--reload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to start
    time.sleep(4)

    try:
        # Run tests
        results = []
        results.append(("Health", test_health()))
        results.append(("Healthy Vehicle", test_diagnose_healthy()))
        results.append(("Engine Overheating", test_diagnose_engine_overheating()))
        results.append(("Critical Tyre", test_diagnose_critical_tyre()))
        results.append(("Critical Coolant", test_diagnose_critical_coolant()))

        # Summary
        print("\n" + "=" * 50)
        print("Test Summary")
        print("=" * 50)
        for name, passed in results:
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status}: {name}")

        total = len(results)
        passed = sum(1 for _, p in results if p)
        print(f"\nTotal: {passed}/{total} tests passed")

        return 0 if passed == total else 1

    finally:
        # Stop the server
        print("\nStopping server...")
        proc.terminate()
        proc.wait(timeout=5)


if __name__ == "__main__":
    import sys
    sys.exit(main())
