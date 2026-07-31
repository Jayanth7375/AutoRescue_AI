"""Tyre Health Agent - Specialized tyre pressure analysis."""

import os
import logging
from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    TyreHealthRequest,
    TyreHealthResponse,
)

load_dotenv()
logger = logging.getLogger(__name__)

TYRE_HEALTH_AGENT_SEED = os.getenv("TYRE_HEALTH_AGENT_SEED", "autorescue-tyre-health-seed")
TYRE_HEALTH_AGENT_PORT = int(os.getenv("TYRE_HEALTH_AGENT_PORT", "8028"))

agent = Agent(
    name="autorescue_tyre_health_agent",
    seed=TYRE_HEALTH_AGENT_SEED,
    port=TYRE_HEALTH_AGENT_PORT,
    endpoint=[f"http://127.0.0.1:{TYRE_HEALTH_AGENT_PORT}/submit"],
)


@agent.on_query(
    model=TyreHealthRequest,
    replies={TyreHealthResponse},
)
async def handle_tyre_query(ctx: Context, sender: str, msg: TyreHealthRequest):
    """Analyze tyre health."""
    try:
        logger.info(f"[TYRE-HEALTH] Request {msg.request_id} for vehicle {msg.vehicle_id}")

        tyres = {
            "FRONT_LEFT": msg.front_left_tyre_psi,
            "FRONT_RIGHT": msg.front_right_tyre_psi,
            "REAR_LEFT": msg.rear_left_tyre_psi,
            "REAR_RIGHT": msg.rear_right_tyre_psi,
        }

        status = "NORMAL"
        affected_tyres = []
        minimum_psi = min(tyres.values())
        action = "Maintain current tyre pressure"
        reason = "All tyres are within recommended range"

        # Check for critical low pressure
        for tyre_name, pressure in tyres.items():
            if pressure < 25:
                status = "CRITICAL"
                affected_tyres.append(tyre_name)
                action = f"Stop safely and inspect or inflate {', '.join(affected_tyres)}"
                reason = f"One or more tyres critically low: {minimum_psi} PSI"

        # Check for warning level
        if status != "CRITICAL":
            for tyre_name, pressure in tyres.items():
                if pressure < 30:
                    status = "WARNING"
                    affected_tyres.append(tyre_name)
            if affected_tyres:
                action = f"Inflate {', '.join(affected_tyres)} to recommended pressure"
                reason = f"One or more tyres below recommended: {minimum_psi} PSI"

        response = TyreHealthResponse(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            status=status,
            affected_tyres=affected_tyres,
            minimum_psi=minimum_psi,
            action=action,
            reason=reason,
        )

        logger.info(f"[TYRE-HEALTH] Response: {status}")
        await ctx.send(sender, response)

    except Exception as e:
        logger.error(f"[TYRE-HEALTH] Error: {str(e)}")
        response = TyreHealthResponse(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            status="UNKNOWN",
            minimum_psi=0,
            action="Unable to assess tyre health",
            reason=str(e),
        )
        await ctx.send(sender, response)


@agent.on_event("startup")
async def startup(ctx: Context):
    """Log startup information."""
    logger.info("=" * 60)
    logger.info("Tyre Health Agent started")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)


if __name__ == "__main__":
    agent.run()
