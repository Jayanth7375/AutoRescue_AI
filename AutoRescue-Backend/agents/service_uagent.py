"""Service uAgent for finding and ranking nearby service centres."""

import os
import logging
from uuid import uuid4

from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    ServiceRequestMessage,
    ServiceCentreMessage,
    ServiceResponseMessage,
    ServiceErrorMessage,
)
from tools.places_tool import nearby_search, PlacesToolError
from tools.distance import haversine_distance
from tools.service_ranker import rank_service_centres, get_top_centres

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration from environment
SERVICE_AGENT_SEED = os.getenv("SERVICE_AGENT_SEED", "autorescue-service-agent-development-seed")
SERVICE_AGENT_PORT = int(os.getenv("SERVICE_AGENT_PORT", "8003"))

# Create the Service uAgent
service_uagent = Agent(
    name="autorescue_service_agent",
    seed=SERVICE_AGENT_SEED,
    port=SERVICE_AGENT_PORT,
    endpoint=[f"http://127.0.0.1:{SERVICE_AGENT_PORT}/submit"],
)


@service_uagent.on_message(model=ServiceRequestMessage)
async def handle_service_request(ctx: Context, sender: str, msg: ServiceRequestMessage):
    """
    Process service request and find nearby service centres.

    Flow:
    1. Validate request
    2. Query Google Places API
    3. Calculate distances
    4. Rank results
    5. Send response with top centres
    """
    try:
        logger.info(
            f"Received service request {msg.request_id} from {sender} for vehicle {msg.vehicle_id}"
        )
        logger.info(
            f"  Issue: {msg.issue} ({msg.affected_component}, {msg.severity})"
        )
        logger.info(f"  Location: {msg.latitude}, {msg.longitude}")

        # Load mock Coimbatore service centres (no external API calls)
        logger.info("[SERVICE] Loading mock Coimbatore service dataset...")
        candidates = nearby_search(
            latitude=msg.latitude,
            longitude=msg.longitude,
            issue=msg.issue,
            affected_component=msg.affected_component,
        )

        if not candidates:
            logger.warning(f"No mock service centres available")
            error_response = ServiceErrorMessage(
                request_id=msg.request_id,
                vehicle_id=msg.vehicle_id,
                error="No mock service centres available in dataset",
            )
            await ctx.send(sender, error_response)
            return

        logger.info(f"[SERVICE] Found {len(candidates)} mock Coimbatore centres")
        logger.info(f"[SERVICE] Calculating distances from user location...")

        # Calculate distances for each candidate
        for centre in candidates:
            centre["distance_km"] = haversine_distance(
                msg.latitude,
                msg.longitude,
                centre["latitude"],
                centre["longitude"],
            )

        # Rank service centres
        logger.info("Ranking service centres...")
        ranked = rank_service_centres(
            candidates=candidates,
            user_latitude=msg.latitude,
            user_longitude=msg.longitude,
            affected_component=msg.affected_component,
            severity=msg.severity,
        )

        # Get top 10
        top_centres = get_top_centres(ranked, limit=10)

        # Log nearest centre
        if top_centres:
            nearest = top_centres[0]
            logger.info(f"[SERVICE] Nearest centre: {nearest['name']} ({nearest['distance_km']} km)")

        # Convert to ServiceCentreMessage format
        centre_messages = [
            ServiceCentreMessage(
                place_id=centre["place_id"],
                name=centre["name"],
                address=centre["address"],
                latitude=centre["latitude"],
                longitude=centre["longitude"],
                rating=centre.get("rating"),
                review_count=centre.get("review_count"),
                is_open=centre.get("is_open"),
                distance_km=centre["distance_km"],
                priority_score=centre["priority_score"],
                recommendation_reason=centre["recommendation_reason"],
            )
            for centre in top_centres
        ]

        # Determine navigation and tow requirements based on safety
        navigation_allowed = msg.safe_to_drive
        tow_recommended = not msg.safe_to_drive

        logger.info(f"Sending response with {len(centre_messages)} centres")
        logger.info(f"  Navigation allowed: {navigation_allowed}")
        logger.info(f"  Tow recommended: {tow_recommended}")

        response = ServiceResponseMessage(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            issue=msg.issue,
            severity=msg.severity,
            navigation_allowed=navigation_allowed,
            tow_recommended=tow_recommended,
            centres=centre_messages,
        )

        await ctx.send(sender, response)

    except PlacesToolError as e:
        logger.error(f"Places API error: {str(e)}")
        error_response = ServiceErrorMessage(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            error=f"Service discovery failed: {str(e)}",
        )
        await ctx.send(sender, error_response)

    except Exception as e:
        logger.error(f"Error processing service request {msg.request_id}: {str(e)}", exc_info=True)
        error_response = ServiceErrorMessage(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            error=f"Service discovery error: {str(e)}",
        )
        await ctx.send(sender, error_response)


@service_uagent.on_event("startup")
async def startup(ctx: Context):
    """Log agent startup information."""
    logger.info("=" * 60)
    logger.info("Service Agent started")
    logger.info(f"Agent Name: {ctx.agent.name}")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)


if __name__ == "__main__":
    service_uagent.run()
