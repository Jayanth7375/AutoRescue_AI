"""Verification Agent - Final consistency checker for vehicle diagnosis."""

import os
import logging
from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    VerificationRequest,
    VerificationMessage,
)

load_dotenv()
logger = logging.getLogger(__name__)

VERIFICATION_AGENT_SEED = os.getenv("VERIFICATION_AGENT_SEED", "autorescue-verification-agent-seed")
VERIFICATION_AGENT_PORT = int(os.getenv("VERIFICATION_AGENT_PORT", "8025"))

agent = Agent(
    name="autorescue_verification_agent",
    seed=VERIFICATION_AGENT_SEED,
    port=VERIFICATION_AGENT_PORT,
    endpoint=[f"http://127.0.0.1:{VERIFICATION_AGENT_PORT}/submit"],
)

@agent.on_query(
    model=VerificationRequest,
    replies={VerificationMessage},
)
async def handle_verification_query(ctx: Context, sender: str, msg: VerificationRequest):
    """Verify consistency of all diagnostic outputs."""

    issues = []
    corrections = []

    # Check diagnosis exists
    if not msg.diagnosis:
        issues.append("No diagnosis available for verification")

    # Check safety exists
    if not msg.safety:
        issues.append("No safety data available for verification")

    # Safety-first consistency checks
    if msg.diagnosis and msg.safety:
        severity = msg.diagnosis.severity

        if severity == "CRITICAL":
            if msg.safety.safe_to_drive:
                issues.append("CRITICAL severity but safe_to_drive=true")
                corrections.append("Should be safe_to_drive=false")

            if msg.safety.navigation_allowed:
                issues.append("CRITICAL severity but navigation_allowed=true")
                corrections.append("Should be navigation_allowed=false")

            if not msg.safety.tow_required:
                issues.append("CRITICAL severity but tow_required=false")
                corrections.append("Should be tow_required=true")

        elif severity == "WARNING":
            # Warnings typically allow driving
            if not msg.safety.safe_to_drive:
                issues.append("WARNING severity but safe_to_drive=false")
                corrections.append("WARNING should allow driving in most cases")

        elif severity == "NORMAL":
            if not msg.safety.safe_to_drive:
                issues.append("NORMAL severity but safe_to_drive=false")
                corrections.append("NORMAL should have safe_to_drive=true")

        # Check maintenance urgency matches severity
        if msg.maintenance:
            if severity == "CRITICAL" and msg.maintenance.urgency != "IMMEDIATE":
                issues.append(f"CRITICAL diagnosis but maintenance urgency={msg.maintenance.urgency}")
                corrections.append("CRITICAL should have urgency=IMMEDIATE")

            elif severity == "WARNING" and msg.maintenance.urgency == "ROUTINE":
                issues.append(f"WARNING diagnosis but maintenance urgency=ROUTINE")
                corrections.append("WARNING should have urgency=SOON or IMMEDIATE")

    response = VerificationMessage(
        verified=len(issues) == 0,
        issues=issues,
        corrections=corrections
    )

    logger.info(f"[VERIFICATION] {msg.request_id} → verified={response.verified}, issues={len(issues)}")
    await ctx.send(sender, response)


@agent.on_event("startup")
async def startup(ctx: Context):
    """Log startup."""
    logger.info("=" * 60)
    logger.info("Verification Agent started")
    logger.info(f"Agent Name: {ctx.agent.name}")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)


if __name__ == "__main__":
    agent.run()
