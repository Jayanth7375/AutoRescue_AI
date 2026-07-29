from uagents.communication import send_sync_message
from agents.messages import AutoRescueRequestMessage, AutoRescueResponseMessage
import os
from dotenv import load_dotenv

load_dotenv()
ORCHESTRATOR = os.getenv("ORCHESTRATOR_AGENT_ADDRESS")

msg = AutoRescueRequestMessage(
    request_id="direct-test-123",
    vehicle_id="TN37AB1234",
    engine_temperature=95.0,
    battery_voltage=12.7,
    front_left_tyre_psi=32.0,
    front_right_tyre_psi=32.0,
    rear_left_tyre_psi=31.0,
    rear_right_tyre_psi=31.0,
    coolant_level=75.0,
    latitude=19.076,
    longitude=72.8777,
)

print(f"Sending to: {ORCHESTRATOR}")
print(f"Message type: {type(msg).__name__}")

result = send_sync_message(
    destination=ORCHESTRATOR,
    message=msg,
    response_type=AutoRescueResponseMessage,
    timeout=15,
)

print(f"\nResult type: {type(result).__name__}")
print(f"Result: {repr(result)[:500]}")

if hasattr(result, '__dict__'):
    print(f"Result dict: {result.__dict__}")
