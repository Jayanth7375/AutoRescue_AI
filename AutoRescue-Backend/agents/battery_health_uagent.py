"""Battery Health Agent - Specialized battery evaluation."""

import os
import logging
from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    BatteryHealthRequest,
    BatteryHealthResponse,
)

load_dotenv()
logger = logging.getLogger(__name__)

BATTERY_HEALTH_AGENT_SEED = os.getenv("BATTERY_HEALTH_AGENT_SEED", "autorescue-battery-health-seed")
BATTERY_HEALTH_AGENT_PORT = int(os.getenv("BATTERY_HEALTH_AGENT_PORT", "8027"))

agent = Agent(
    name="autorescue_battery_health_agent",
    seed=BATTERY_HEALTH_AGENT_SEED,
    port=BATTERY_HEALTH_AGENT_PORT,
    endpoint=[f"http://127.0.0.1:{BATTERY_HEALTH_AGENT_PORT}/submit"],
)


@agent.on_query(
    model=BatteryHealthRequest,
    replies={BatteryHealthResponse},
)
async def handle_battery_query(ctx: Context, sender: str, msg: BatteryHealthRequest):
    """Evaluate battery health."""
    try:
        logger.info(f"[BATTERY-HEALTH] Request {msg.request_id} for vehicle {msg.vehicle_id}")

        status = "NORMAL"
        action = "No action required"
        reason = f"Battery voltage {msg.battery_voltage}V is within normal range"

        # ICE vehicle rules (12V battery)
        if msg.powertrain == "ICE" or msg.powertrain == "UNKNOWN":
            if msg.battery_voltage < 11.5:
                status = "CRITICAL"
                action = "Charge battery immediately or seek assistance"
                reason = f"12V battery voltage {msg.battery_voltage}V is critically low"
            elif msg.battery_voltage < 12.0:
                status = "WEAK"
                action = "Charge battery at next opportunity"
                reason = f"12V battery voltage {msg.battery_voltage}V indicates weak charge"
            elif msg.battery_voltage > 14.5:
                status = "CRITICAL"
                action = "Check charging system for overcharge"
                reason = f"Battery voltage {msg.battery_voltage}V exceeds safe charging voltage"

        # EV vehicles - 12V signal doesn't represent traction battery
        elif msg.powertrain == "EV":
            status = "UNKNOWN"
            action = "12V auxiliary battery appears nominal; check traction battery via OEM system"
            reason = f"12V reading {msg.battery_voltage}V is auxiliary battery only. EV traction battery status unavailable."

        # HYBRID vehicles
        elif msg.powertrain == "HYBRID":
            if msg.battery_voltage < 12.0:
                status = "WEAK"
                action = "Check hybrid battery and 12V charging system"
                reason = f"12V auxiliary battery {msg.battery_voltage}V is low"

        response = BatteryHealthResponse(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            status=status,
            battery_voltage=msg.battery_voltage,
            action=action,
            reason=reason,
        )

        logger.info(f"[BATTERY-HEALTH] Response: {status}")
        await ctx.send(sender, response)

    except Exception as e:
        logger.error(f"[BATTERY-HEALTH] Error: {str(e)}")
        response = BatteryHealthResponse(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            status="UNKNOWN",
            battery_voltage=msg.battery_voltage,
            action="Unable to assess battery health",
            reason=str(e),
        )
        await ctx.send(sender, response)


@agent.on_event("startup")
async def startup(ctx: Context):
    """Log startup information."""
    logger.info("=" * 60)
    logger.info("Battery Health Agent started")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)


if __name__ == "__main__":
    agent.run()
