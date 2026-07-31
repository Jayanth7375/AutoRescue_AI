"""Breakdown Classification Agent - Classify rescue scenarios."""

import os
import logging
from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    BreakdownClassificationRequest,
    BreakdownClassificationResponse,
)

load_dotenv()
logger = logging.getLogger(__name__)

AGENT_SEED = os.getenv("BREAKDOWN_CLASSIFICATION_AGENT_SEED", "autorescue-breakdown-class-seed")
AGENT_PORT = int(os.getenv("BREAKDOWN_CLASSIFICATION_AGENT_PORT", "8030"))

agent = Agent(
    name="autorescue_breakdown_classification_agent",
    seed=AGENT_SEED,
    port=AGENT_PORT,
    endpoint=[f"http://127.0.0.1:{AGENT_PORT}/submit"],
)


@agent.on_query(model=BreakdownClassificationRequest, replies={BreakdownClassificationResponse})
async def handle_classification(ctx: Context, sender: str, msg: BreakdownClassificationRequest):
    """Classify breakdown scenario."""
    try:
        logger.info(f"[BREAKDOWN-CLASS] Request {msg.request_id}")

        # If user explicitly selected, respect it
        if msg.selected_rescue_category:
            category = msg.selected_rescue_category
            reason = f"User selected: {category}"
            confidence = 1.0
        else:
            category = "OTHER"
            reason = "No explicit selection provided"
            confidence = 0.5

        response = BreakdownClassificationResponse(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            category=category,
            confidence=confidence,
            reason=reason,
        )

        logger.info(f"[BREAKDOWN-CLASS] Response: {category}")
        await ctx.send(sender, response)

    except Exception as e:
        logger.error(f"[BREAKDOWN-CLASS] Error: {str(e)}")
        response = BreakdownClassificationResponse(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            category="OTHER",
            confidence=0.0,
            reason=str(e),
        )
        await ctx.send(sender, response)


@agent.on_event("startup")
async def startup(ctx: Context):
    logger.info("=" * 60)
    logger.info("Breakdown Classification Agent started")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)


if __name__ == "__main__":
    agent.run()
