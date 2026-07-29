"""Rescue uAgent for determining roadside assistance requirements."""

import os
import logging

from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    RescueRequestMessage,
    RescueResponseMessage,
    RescueErrorMessage,
)
from tools.rescue_rules import determine_rescue_action

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration from environment
RESCUE_AGENT_SEED = os.getenv("RESCUE_AGENT_SEED", "autorescue-rescue-agent-development-seed")
RESCUE_AGENT_PORT = int(os.getenv("RESCUE_AGENT_PORT", "8015"))

# Create the Rescue uAgent
rescue_uagent = Agent(
    name="autorescue_rescue_agent",
    seed=RESCUE_AGENT_SEED,
    port=RESCUE_AGENT_PORT,
    endpoint=[f"http://127.0.0.1:{RESCUE_AGENT_PORT}/submit"],
)


@rescue_uagent.on_message(model=RescueRequestMessage)
async def handle_rescue_request(ctx: Context, sender: str, msg: RescueRequestMessage):
    """
    Process rescue request and determine assistance requirements.

    Flow:
    1. Validate request
    2. Apply rescue decision rules
    3. Send response with assistance details
    """
    try:
        logger.info(f"Received rescue request {msg.request_id} from {sender} for vehicle {msg.vehicle_id}")
        logger.info(f"  Issue: {msg.issue}")
        logger.info(f"  Component: {msg.affected_component}")
        logger.info(f"  Severity: {msg.severity}")
        logger.info(f"  Safe to Drive: {msg.safe_to_drive}")

        # Apply rescue decision rules
        logger.info("Applying rescue decision rules...")
        rescue_decision = determine_rescue_action(
            issue=msg.issue,
            affected_component=msg.affected_component,
            severity=msg.severity,
            safe_to_drive=msg.safe_to_drive,
            service_centre_name=msg.service_centre_name,
            service_centre_place_id=msg.service_centre_place_id,
        )

        # Create response message
        response = RescueResponseMessage(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            assistance_required=rescue_decision["assistance_required"],
            assistance_type=rescue_decision["assistance_type"],
            priority=rescue_decision["priority"],
            can_drive=rescue_decision["can_drive"],
            tow_required=rescue_decision["tow_required"],
            instructions=rescue_decision["instructions"],
            reason=rescue_decision["reason"],
            destination_name=rescue_decision.get("destination_name"),
            destination_place_id=rescue_decision.get("destination_place_id"),
            estimated_dispatch_minutes=rescue_decision.get("estimated_dispatch_minutes"),
        )

        logger.info(f"Sending rescue response for request {msg.request_id}")
        logger.info(f"  Assistance Type: {response.assistance_type}")
        logger.info(f"  Priority: {response.priority}")
        logger.info(f"  Tow Required: {response.tow_required}")

        await ctx.send(sender, response)

    except Exception as e:
        logger.error(f"Error processing rescue request {msg.request_id}: {str(e)}", exc_info=True)
        error_response = RescueErrorMessage(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            error=f"Rescue decision failed: {str(e)}",
        )
        await ctx.send(sender, error_response)


@rescue_uagent.on_event("startup")
async def startup(ctx: Context):
    """Log agent startup information."""
    logger.info("=" * 60)
    logger.info("Rescue Agent started")
    logger.info(f"Agent Name: {ctx.agent.name}")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)


if __name__ == "__main__":
    rescue_uagent.run()
