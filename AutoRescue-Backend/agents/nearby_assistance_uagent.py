"""Nearby Assistance Agent - Find nearby assistance places."""

import os
import logging
from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    NearbyAssistanceRequest,
    NearbyAssistanceResponse,
)

load_dotenv()
logger = logging.getLogger(__name__)

AGENT_SEED = os.getenv("NEARBY_ASSISTANCE_AGENT_SEED", "autorescue-nearby-assist-seed")
AGENT_PORT = int(os.getenv("NEARBY_ASSISTANCE_AGENT_PORT", "8032"))

agent = Agent(
    name="autorescue_nearby_assistance_agent",
    seed=AGENT_SEED,
    port=AGENT_PORT,
    endpoint=[f"http://127.0.0.1:{AGENT_PORT}/submit"],
)


@agent.on_query(model=NearbyAssistanceRequest, replies={NearbyAssistanceResponse})
async def handle_nearby(ctx: Context, sender: str, msg: NearbyAssistanceRequest):
    """Find nearby assistance places."""
    try:
        logger.info(f"[NEARBY-ASSIST] Request {msg.request_id} category={msg.category}")

        # In production, integrate with NearbyPlacesService
        # For now, return placeholder data indicating places should be fetched

        response = NearbyAssistanceResponse(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            category=msg.category,
            places=[],
            count=0,
            fallback=True,
        )

        logger.info(f"[NEARBY-ASSIST] Response: fallback mode (no real API)")
        await ctx.send(sender, response)

    except Exception as e:
        logger.error(f"[NEARBY-ASSIST] Error: {str(e)}")
        response = NearbyAssistanceResponse(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            category=msg.category,
            places=[],
            count=0,
            fallback=True,
        )
        await ctx.send(sender, response)


@agent.on_event("startup")
async def startup(ctx: Context):
    logger.info("=" * 60)
    logger.info("Nearby Assistance Agent started")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)


if __name__ == "__main__":
    agent.run()
