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

@agent.on_query(
    model=SafetyRequest,
    replies={SafetyMessage},
)
async def handle_safety_query(ctx: Context, sender: str, msg: SafetyRequest):
    """Determine safety flags based on diagnosis severity (query/response pattern)."""

    # Extract severity from diagnosis
    severity = msg.diagnosis.severity if msg.diagnosis else "NORMAL"

    if severity == "CRITICAL":
        response = SafetyMessage(
            safe_to_drive=False,
            navigation_allowed=False,
            tow_required=True,
            risk_level="HIGH"
        )
    elif severity == "WARNING":
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

    logger.info(f"[SAFETY] {msg.request_id} → {severity}={response.risk_level}")

    # Debug logging
    try:
        payload = response.model_dump()
    except AttributeError:
        payload = response.dict()
    logger.info(f"[SAFETY] OUTGOING TYPE: {type(response).__name__}")
    logger.info(f"[SAFETY] OUTGOING PAYLOAD: {payload}")

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
