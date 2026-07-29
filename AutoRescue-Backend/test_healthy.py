import httpx, asyncio, json

async def test():
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post("http://127.0.0.1:8000/api/autorescue/check",
            json={"vehicle_id": "TN37AB1234", "engine_temperature": 95, "battery_voltage": 12.7,
                  "front_left_tyre_psi": 32, "front_right_tyre_psi": 32, "rear_left_tyre_psi": 31,
                  "rear_right_tyre_psi": 31, "coolant_level": 75, "latitude": 11.0168, "longitude": 76.9558})
    
    print(f"HTTP {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"\n??? HEALTHY TEST PASSED ???")
        print(f"  Status: {data.get('status')}")
        print(f"  Severity: {data.get('diagnosis', {}).get('severity')}")
        print(f"  Safe to drive: {data.get('diagnosis', {}).get('safe_to_drive')}")
    else:
        print(f"Error: {response.text[:200]}")

asyncio.run(test())
