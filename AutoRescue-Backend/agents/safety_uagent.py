"""Safety Agent - Determines authoritative safety flags."""

import os
import logging
from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    SafetyRequest,
    SafetyMessage,
    DiagnosisSummary,
)

load_dotenv()
logger = logging.getLogger(__name__)

SAFETY_AGENT_SEED = os.getenv("SAFETY_AGENT_SEED", "autorescue-safety-agent-seed")
SAFETY_AGENT_PORT = int(os.getenv("SAFETY_AGENT_PORT", "8021"))

agent = Agent(
    name="autorescue_safety_agent",
    seed=SAFETY_AGENT_SEED,
    port=SAFETY_AGENT_PORT,
    endpoint=[f"http://127.0.0.1:{SAFETY_AGENT_PORT}/submit"],
)

@agent.on_message(model=SafetyRequest)
async def handle_safety(ctx: Context, sender: str, msg: SafetyRequest):
    """Determine safety flags based on severity."""

    if msg.severity == "CRITICAL":
        response = SafetyMessage(
            safe_to_drive=False,
            navigation_allowed=False,
            tow_required=True,
            risk_level="HIGH"
        )
    elif msg.severity == "WARNING":
        response = SafetyMessage(
            safe_to_drive=True,
            navigation_allowed=True,
            tow_required=False,
            risk_level="MEDIUM"
        )
    else:  # NORMAL
        response = SafetyMessage(
            safe_to_drive=True,
            navigation_allowed=True,
            tow_required=False,
            risk_level="LOW"
        )

    logger.info(f"[SAFETY] {msg.request_id} → {msg.severity}={response.risk_level}")
    await ctx.send(sender, response)


@agent.on_event("startup")
async def startup(ctx: Context):
    """Log startup."""
    logger.info("=" * 60)
    logger.info("Safety Agent started")
    logger.info(f"Agent Name: {ctx.agent.name}")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)


if __name__ == "__main__":
    agent.run()
