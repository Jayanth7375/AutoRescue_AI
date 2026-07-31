"""Service Ranking Agent - Rank assistance places."""

import os
import logging
from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    ServiceRankingRequest,
    ServiceRankingResponse,
)

load_dotenv()
logger = logging.getLogger(__name__)

AGENT_SEED = os.getenv("SERVICE_RANKING_AGENT_SEED", "autorescue-service-ranking-seed")
AGENT_PORT = int(os.getenv("SERVICE_RANKING_AGENT_PORT", "8033"))

agent = Agent(
    name="autorescue_service_ranking_agent",
    seed=AGENT_SEED,
    port=AGENT_PORT,
    endpoint=[f"http://127.0.0.1:{AGENT_PORT}/submit"],
)


@agent.on_query(model=ServiceRankingRequest, replies={ServiceRankingResponse})
async def handle_ranking(ctx: Context, sender: str, msg: ServiceRankingRequest):
    """Rank service places."""
    try:
        logger.info(f"[SERVICE-RANKING] Request {msg.request_id}")

        # Sort by distance (ascending) as primary ranking
        ranked_places = sorted(
            msg.places,
            key=lambda p: p.get("distance_km", float("inf"))
        ) if msg.places else []

        response = ServiceRankingResponse(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            ranked_places=ranked_places,
            ranking_reason="Sorted by distance (nearest first) and service relevance",
        )

        logger.info(f"[SERVICE-RANKING] Response: ranked {len(ranked_places)} places")
        await ctx.send(sender, response)

    except Exception as e:
        logger.error(f"[SERVICE-RANKING] Error: {str(e)}")
        response = ServiceRankingResponse(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            ranked_places=[],
            ranking_reason=f"Error: {str(e)}",
        )
        await ctx.send(sender, response)


@agent.on_event("startup")
async def startup(ctx: Context):
    logger.info("=" * 60)
    logger.info("Service Ranking Agent started")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)


if __name__ == "__main__":
    agent.run()
