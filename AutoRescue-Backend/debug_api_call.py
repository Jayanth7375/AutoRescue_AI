"""Debug script to test API call and capture full orchestrator response."""

import httpx
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

BASE_URL = "http://127.0.0.1:8000"

# Simple normal vehicle request
payload = {
    "vehicle_id": "TEST-NORMAL",
    "engine_temperature": 90,
    "battery_voltage": 12.7,
    "front_left_tyre_psi": 32,
    "front_right_tyre_psi": 32,
    "rear_left_tyre_psi": 31,
    "rear_right_tyre_psi": 31,
    "coolant_level": 80,
    "latitude": 11.0168,
    "longitude": 76.9558
}

print("="*70)
print("Testing Normal Vehicle Request")
print("="*70)
print("")
print("Payload:")
print(json.dumps(payload, indent=2))
print("")

try:
    print("Calling POST /api/autorescue/check...")
    response = httpx.post(
        f"{BASE_URL}/api/autorescue/check",
        json=payload,
        timeout=30
    )

    print(f"Status Code: {response.status_code}")
    print("")

    data = response.json()

    print("Response:")
    print(json.dumps(data, indent=2))
    print("")

    print("Analysis:")
    print(f"  Status: {data.get('status')}")
    print(f"  Diagnosis Severity: {data.get('diagnosis', {}).get('severity')}")
    print(f"  Trace Entries: {len(data.get('agent_trace', []))}")
    print("")

    if data.get('agent_trace'):
        print("Trace Details:")
        for idx, entry in enumerate(data.get('agent_trace', []), 1):
            print(f"  {idx}. {entry.get('agent')}: {entry.get('status')} - {entry.get('summary')}")

except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
