"""Vehicle Profile Agent - Provides contextual vehicle information."""

import os
import logging
from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    VehicleProfileRequest,
    VehicleProfileResponse,
)

load_dotenv()
logger = logging.getLogger(__name__)

VEHICLE_PROFILE_AGENT_SEED = os.getenv("VEHICLE_PROFILE_AGENT_SEED", "autorescue-vehicle-profile-seed")
VEHICLE_PROFILE_AGENT_PORT = int(os.getenv("VEHICLE_PROFILE_AGENT_PORT", "8026"))

agent = Agent(
    name="autorescue_vehicle_profile_agent",
    seed=VEHICLE_PROFILE_AGENT_SEED,
    port=VEHICLE_PROFILE_AGENT_PORT,
    endpoint=[f"http://127.0.0.1:{VEHICLE_PROFILE_AGENT_PORT}/submit"],
)

# Local vehicle profile database (demo)
VEHICLE_PROFILES = {
    "TN37AB1234": {
        "manufacturer": "Tata",
        "model": "Nexon",
        "year": 2023,
        "vehicle_type": "SUV",
        "powertrain": "ICE",
        "fuel_type": "PETROL",
        "battery_type": "12V",
        "tyre_specification": "215/65 R16",
        "odometer_km": 45000,
        "last_service_km": 40000,
        "service_interval_km": 10000,
    },
    "EV-001": {
        "manufacturer": "Tesla",
        "model": "Model 3",
        "year": 2023,
        "vehicle_type": "CAR",
        "powertrain": "EV",
        "fuel_type": None,
        "battery_type": "TRACTION_PACK",
        "tyre_specification": "225/45 R18",
        "odometer_km": 20000,
        "last_service_km": 15000,
        "service_interval_km": 25000,
    },
}


@agent.on_query(
    model=VehicleProfileRequest,
    replies={VehicleProfileResponse},
)
async def handle_profile_query(ctx: Context, sender: str, msg: VehicleProfileRequest):
    """Retrieve vehicle profile information."""
    try:
        logger.info(f"[VEHICLE-PROFILE] Request {msg.request_id} from {sender[:30]}...")

        profile = VEHICLE_PROFILES.get(msg.vehicle_id, {})

        response = VehicleProfileResponse(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            manufacturer=profile.get("manufacturer"),
            model=profile.get("model"),
            year=profile.get("year"),
            vehicle_type=profile.get("vehicle_type", "UNKNOWN"),
            powertrain=profile.get("powertrain", "UNKNOWN"),
            fuel_type=profile.get("fuel_type"),
            battery_type=profile.get("battery_type"),
            tyre_specification=profile.get("tyre_specification"),
            odometer_km=profile.get("odometer_km"),
            last_service_km=profile.get("last_service_km"),
            service_interval_km=profile.get("service_interval_km"),
            profile_found=len(profile) > 0,
        )

        logger.info(f"[VEHICLE-PROFILE] Response: {response.powertrain}")
        await ctx.send(sender, response)

    except Exception as e:
        logger.error(f"[VEHICLE-PROFILE] Error: {str(e)}")
        response = VehicleProfileResponse(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            profile_found=False,
        )
        await ctx.send(sender, response)


@agent.on_event("startup")
async def startup(ctx: Context):
    """Log startup information."""
    logger.info("=" * 60)
    logger.info("Vehicle Profile Agent started")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)


if __name__ == "__main__":
    agent.run()
