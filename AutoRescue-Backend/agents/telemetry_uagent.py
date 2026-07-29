"""Telemetry Agent - Validates and normalizes vehicle sensor data."""

import os
import logging
from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    TelemetryValidationRequest,
    TelemetryValidationMessage,
)

load_dotenv()
logger = logging.getLogger(__name__)

TELEMETRY_AGENT_SEED = os.getenv("TELEMETRY_AGENT_SEED", "autorescue-telemetry-agent-seed")
TELEMETRY_AGENT_PORT = int(os.getenv("TELEMETRY_AGENT_PORT", "8020"))

agent = Agent(
    name="autorescue_telemetry_agent",
    seed=TELEMETRY_AGENT_SEED,
    port=TELEMETRY_AGENT_PORT,
    endpoint=[f"http://127.0.0.1:{TELEMETRY_AGENT_PORT}/submit"],
)

@agent.on_query(
    model=TelemetryValidationRequest,
    replies={TelemetryValidationMessage},
)
async def handle_telemetry_query(ctx: Context, sender: str, msg: TelemetryValidationRequest):
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

    response = TelemetryValidationMessage(
        valid=len(issues) == 0,
        issues=issues,
        normalized_telemetry=normalized
    )

    logger.info(f"[TELEMETRY] {msg.request_id} → Sending validation result to {sender}")
    await ctx.send(sender, response)


@agent.on_event("startup")
async def startup(ctx: Context):
    """Log startup."""
    logger.info("=" * 60)
    logger.info("Telemetry Agent started")
    logger.info(f"Agent Name: {ctx.agent.name}")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)


if __name__ == "__main__":
    agent.run()
