"""Passenger Safety Agent - Handle accident/injury context."""

import os
import logging
from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    PassengerSafetyRequest,
    PassengerSafetyResponse,
)

load_dotenv()
logger = logging.getLogger(__name__)

AGENT_SEED = os.getenv("PASSENGER_SAFETY_AGENT_SEED", "autorescue-passenger-safety-seed")
AGENT_PORT = int(os.getenv("PASSENGER_SAFETY_AGENT_PORT", "8031"))

agent = Agent(
    name="autorescue_passenger_safety_agent",
    seed=AGENT_SEED,
    port=AGENT_PORT,
    endpoint=[f"http://127.0.0.1:{AGENT_PORT}/submit"],
)


@agent.on_query(model=PassengerSafetyRequest, replies={PassengerSafetyResponse})
async def handle_safety(ctx: Context, sender: str, msg: PassengerSafetyRequest):
    """Assess passenger safety."""
    try:
        logger.info(f"[PASSENGER-SAFETY] Request {msg.request_id}")

        medical_priority = "NONE"
        hospital_required = False
        vehicle_priority = True
        guidance = "Vehicle appears safe"

        if msg.accident_flag:
            if msg.passenger_injury:
                medical_priority = "HIGH"
                hospital_required = True
                vehicle_priority = False
                guidance = "Medical assistance is PRIMARY priority. Contact emergency services."
            else:
                medical_priority = "MEDIUM"
                hospital_required = False
                vehicle_priority = True
                guidance = "No immediate injury detected. Vehicle assistance can proceed."

        response = PassengerSafetyResponse(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            medical_priority=medical_priority,
            hospital_search_required=hospital_required,
            vehicle_service_priority=vehicle_priority,
            guidance=guidance,
        )

        logger.info(f"[PASSENGER-SAFETY] Response: priority={medical_priority}")
        await ctx.send(sender, response)

    except Exception as e:
        logger.error(f"[PASSENGER-SAFETY] Error: {str(e)}")
        response = PassengerSafetyResponse(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            medical_priority="UNKNOWN",
            guidance=str(e),
        )
        await ctx.send(sender, response)


@agent.on_event("startup")
async def startup(ctx: Context):
    logger.info("=" * 60)
    logger.info("Passenger Safety Agent started")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)


if __name__ == "__main__":
    agent.run()
