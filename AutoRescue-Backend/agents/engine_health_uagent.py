"""Engine Health Agent - Specialized engine evaluation."""

import os
import logging
from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    EngineHealthRequest,
    EngineHealthResponse,
)

load_dotenv()
logger = logging.getLogger(__name__)

AGENT_SEED = os.getenv("ENGINE_HEALTH_AGENT_SEED", "autorescue-engine-health-seed")
AGENT_PORT = int(os.getenv("ENGINE_HEALTH_AGENT_PORT", "8029"))

agent = Agent(
    name="autorescue_engine_health_agent",
    seed=AGENT_SEED,
    port=AGENT_PORT,
    endpoint=[f"http://127.0.0.1:{AGENT_PORT}/submit"],
)


@agent.on_query(model=EngineHealthRequest, replies={EngineHealthResponse})
async def handle_engine_query(ctx: Context, sender: str, msg: EngineHealthRequest):
    """Evaluate engine health."""
    try:
        logger.info(f"[ENGINE-HEALTH] Request {msg.request_id}")

        status = "NORMAL"
        coolant_risk = "NONE"
        action = "Continue monitoring"
        reason = "Engine temperature within normal range"

        # Engine temperature checks
        if msg.engine_temperature > 120:
            status = "CRITICAL"
            action = "STOP vehicle immediately. Switch off engine and allow cooling"
            reason = f"Engine temperature {msg.engine_temperature}°C is critically high"
            coolant_risk = "CRITICAL"
        elif msg.engine_temperature > 110:
            status = "WARNING"
            action = "Reduce load and monitor temperature"
            reason = f"Engine temperature {msg.engine_temperature}°C is elevated"
            coolant_risk = "LOW"
        elif msg.engine_temperature < 80:
            status = "NORMAL"
            reason = f"Engine temperature {msg.engine_temperature}°C is within normal startup/cold range"

        # Coolant level checks
        if msg.coolant_level < 30:
            status = "CRITICAL"
            coolant_risk = "CRITICAL"
            action = "STOP vehicle and refill coolant immediately"
            reason = f"Coolant level {msg.coolant_level}% is critically low"
        elif msg.coolant_level < 50:
            if status != "CRITICAL":
                status = "WARNING"
            coolant_risk = "LOW"
            action = "Refill coolant at next service"
            reason = f"Coolant level {msg.coolant_level}% is below recommended"

        response = EngineHealthResponse(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            status=status,
            engine_temperature=msg.engine_temperature,
            coolant_risk=coolant_risk,
            action=action,
            reason=reason,
        )

        logger.info(f"[ENGINE-HEALTH] Response: {status}")
        await ctx.send(sender, response)

    except Exception as e:
        logger.error(f"[ENGINE-HEALTH] Error: {str(e)}")
        response = EngineHealthResponse(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            status="UNKNOWN",
            engine_temperature=msg.engine_temperature,
            coolant_risk="UNKNOWN",
            action="Error in engine health assessment",
            reason=str(e),
        )
        await ctx.send(sender, response)


@agent.on_event("startup")
async def startup(ctx: Context):
    logger.info("=" * 60)
    logger.info("Engine Health Agent started")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)


if __name__ == "__main__":
    agent.run()
