import httpx
import asyncio
import json

async def test():
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "http://127.0.0.1:8000/api/autorescue/check",
                json={
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
            )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

asyncio.run(test())
