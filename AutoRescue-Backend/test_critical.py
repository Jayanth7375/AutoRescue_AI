import httpx, asyncio

async def test():
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post("http://127.0.0.1:8000/api/autorescue/check",
            json={"vehicle_id": "TN37AB5678", "engine_temperature": 122, "battery_voltage": 12.7,
                  "front_left_tyre_psi": 32, "front_right_tyre_psi": 32, "rear_left_tyre_psi": 31,
                  "rear_right_tyre_psi": 31, "coolant_level": 75, "latitude": 11.0168, "longitude": 76.9558})
        
        print(f"HTTP {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"\n? CRITICAL TEST RESULT")
            print(f"  Status: {data.get('status')}")
            print(f"  Severity: {data.get('diagnosis', {}).get('severity')}")
            print(f"  Safe to drive: {data.get('diagnosis', {}).get('safe_to_drive')}")
            print(f"  Assistance type: {data.get('rescue', {}).get('assistance_type') if data.get('rescue') else 'N/A'}")
        else:
            print(f"Error: {response.text[:200]}")

asyncio.run(test())
