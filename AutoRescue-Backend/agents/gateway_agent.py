"""Gateway Agent - bridges FastAPI HTTP calls to Orchestrator uAgent synchronously."""

import os
import logging

from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    AutoRescueRequestMessage,
    AutoRescueResponseMessageExtended,
    AutoRescueErrorMessage,
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
GATEWAY_AGENT_SEED = os.getenv("GATEWAY_AGENT_SEED", "autorescue-gateway-agent-development-seed")
GATEWAY_AGENT_PORT = int(os.getenv("GATEWAY_AGENT_PORT", "8019"))
ORCHESTRATOR_AGENT_ADDRESS = os.getenv("ORCHESTRATOR_AGENT_ADDRESS")

# Create Gateway Agent
gateway_uagent = Agent(
    name="autorescue_gateway_agent",
    seed=GATEWAY_AGENT_SEED,
    port=GATEWAY_AGENT_PORT,
    endpoint=[f"http://127.0.0.1:{GATEWAY_AGENT_PORT}/submit"],
)


async def call_orchestrator(
    ctx: Context,
    request: AutoRescueRequestMessage,
) -> AutoRescueResponseMessageExtended | AutoRescueErrorMessage:
    """
    Synchronously call the Orchestrator using send_and_receive.

    This is used by FastAPI to get a synchronous response from the Orchestrator.
    """
    if not ORCHESTRATOR_AGENT_ADDRESS:
        raise ValueError("ORCHESTRATOR_AGENT_ADDRESS not configured")

    logger.info(f"[GATEWAY] {request.request_id} calling Orchestrator")

    try:
        # Use send_and_receive to synchronously wait for response
        result = await ctx.send_and_receive(
            destination=ORCHESTRATOR_AGENT_ADDRESS,
            message=request,
            timeout=120,
        )

        logger.info(f"[GATEWAY] {request.request_id} ← ORCHESTRATOR: {type(result).__name__}")

        # Unpack tuple response (response, status) if needed
        if isinstance(result, tuple):
            response, status = result
            logger.info(f"[GATEWAY] UNPACKED: response={type(response).__name__}, status={type(status).__name__}")
        else:
            response = result

        if isinstance(response, AutoRescueResponseMessageExtended):
            logger.info(f"[GATEWAY] {request.request_id} got AutoRescueResponseMessageExtended: {response.status}")
            return response

        elif isinstance(response, AutoRescueErrorMessage):
            logger.error(f"[GATEWAY] {request.request_id} got AutoRescueErrorMessage: {response.error}")
            return response

        else:
            logger.error(
                f"[GATEWAY] {request.request_id}: Unexpected response type {type(response).__name__}"
            )
            raise ValueError(f"Unexpected response type: {type(response).__name__}")

    except Exception as e:
        logger.error(f"[GATEWAY] {request.request_id} call failed: {str(e)}", exc_info=True)
        raise


@gateway_uagent.on_event("startup")
async def startup(ctx: Context):
    """Validate configuration and log startup."""
    logger.info("=" * 60)
    logger.info("Gateway Agent started")
    logger.info(f"Agent Name: {ctx.agent.name}")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)

    if ORCHESTRATOR_AGENT_ADDRESS:
        logger.info(f"✓ Orchestrator configured: {ORCHESTRATOR_AGENT_ADDRESS[:30]}...")
    else:
        logger.error("⚠ ORCHESTRATOR_AGENT_ADDRESS not configured")


if __name__ == "__main__":
    gateway_uagent.run()
