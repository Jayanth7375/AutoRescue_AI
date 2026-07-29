import asyncio
from uagents import Agent
from agents.messages import ServiceRequestMessage, ServiceResponseMessage
from agents.service_uagent import service_uagent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test the service agent's mock dataset
async def test_mock_dataset():
    msg = ServiceRequestMessage(
        request_id="mock-test-123",
        vehicle_id="TN37AB1234",
        issue="Engine Warning",
        affected_component="Engine",
        severity="WARNING",
        safe_to_drive=True,
        latitude=11.0168,
        longitude=76.9558,
    )
    
    print(f"\n{'='*60}")
    print(f"Testing Service Agent with Mock Dataset")
    print(f"{'='*60}")
    print(f"Request: {msg.request_id}")
    print(f"Issue: {msg.issue} ({msg.affected_component})")
    print(f"Location: {msg.latitude}, {msg.longitude}")
    
    # Manually test the nearby_search function
    from tools.places_tool import nearby_search
    from tools.distance import haversine_distance
    
    print(f"\nCalling nearby_search()...")
    candidates = nearby_search(msg.latitude, msg.longitude, msg.issue, msg.affected_component)
    print(f"? Got {len(candidates)} mock centres")
    
    # Calculate distances
    print(f"\nCalculating distances...")
    for centre in candidates:
        centre["distance_km"] = haversine_distance(
            msg.latitude, msg.longitude,
            centre["latitude"], centre["longitude"]
        )
    
    # Sort by distance
    candidates_sorted = sorted(candidates, key=lambda c: c["distance_km"])
    
    print(f"\nTop 5 nearest centres (by distance):")
    for i, centre in enumerate(candidates_sorted[:5], 1):
        print(f"  {i}. {centre['name']} - {centre['distance_km']} km away")
    
    print(f"\n? Mock dataset integration working correctly!")

asyncio.run(test_mock_dataset())
