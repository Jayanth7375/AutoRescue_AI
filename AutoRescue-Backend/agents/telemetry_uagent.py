"""Telemetry Agent - Validates and normalizes vehicle sensor data."""

import logging
from uagents import Agent, Context, Model

logger = logging.getLogger(__name__)

class TelemetryValidationRequest(Model):
    """Request to validate telemetry data."""
    request_id: str
    vehicle_id: str
    engine_temperature: float
    battery_voltage: float
    front_left_tyre_psi: float
    front_right_tyre_psi: float
    rear_left_tyre_psi: float
    rear_right_tyre_psi: float
    coolant_level: float
    latitude: float
    longitude: float

class TelemetryValidationResponse(Model):
    """Response with validated telemetry data."""
    request_id: str
    vehicle_id: str
    valid: bool
    issues: list[str]
    normalized_telemetry: dict

agent = Agent(name="telemetry", port=8020, seed="telemetry_seed_1234")

@agent.on_message(model=TelemetryValidationRequest)
async def handle_telemetry(ctx: Context, sender: str, msg: TelemetryValidationRequest):
    """Validate and normalize telemetry data."""
    issues = []

    # Validation rules
    if not -50 <= msg.engine_temperature <= 150:
        issues.append(f"Engine temperature {msg.engine_temperature}°C out of range")

    if not 10 <= msg.battery_voltage <= 16:
        issues.append(f"Battery voltage {msg.battery_voltage}V out of range")

    for label, psi in [
        ("front_left", msg.front_left_tyre_psi),
        ("front_right", msg.front_right_tyre_psi),
        ("rear_left", msg.rear_left_tyre_psi),
        ("rear_right", msg.rear_right_tyre_psi),
    ]:
        if psi < 0 or psi > 50:
            issues.append(f"{label} tyre PSI {psi} invalid")

    if not 0 <= msg.coolant_level <= 100:
        issues.append(f"Coolant level {msg.coolant_level}% out of range")

    if not -90 <= msg.latitude <= 90:
        issues.append(f"Latitude {msg.latitude} invalid")

    if not -180 <= msg.longitude <= 180:
        issues.append(f"Longitude {msg.longitude} invalid")

    normalized = {
        "engine_temperature": msg.engine_temperature,
        "battery_voltage": msg.battery_voltage,
        "front_left_tyre_psi": msg.front_left_tyre_psi,
        "front_right_tyre_psi": msg.front_right_tyre_psi,
        "rear_left_tyre_psi": msg.rear_left_tyre_psi,
        "rear_right_tyre_psi": msg.rear_right_tyre_psi,
        "coolant_level": msg.coolant_level,
        "latitude": msg.latitude,
        "longitude": msg.longitude,
    }

    response = TelemetryValidationResponse(
        request_id=msg.request_id,
        vehicle_id=msg.vehicle_id,
        valid=len(issues) == 0,
        issues=issues,
        normalized_telemetry=normalized
    )

    await ctx.send(sender, response)

if __name__ == "__main__":
    agent.run()
