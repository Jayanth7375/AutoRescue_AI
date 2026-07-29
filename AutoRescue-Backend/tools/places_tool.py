"""Mock service centre lookup tool - Returns deterministic local dataset for Coimbatore."""

import logging
from tools.mock_service_centres import get_mock_service_centres

logger = logging.getLogger(__name__)


class PlacesToolError(Exception):
    """Exception raised by places tool."""
    pass


# Mock-only implementation - no external API queries
# The dataset is deterministic Coimbatore demo data


def nearby_search(
    latitude: float,
    longitude: float,
    issue: str = "",
    affected_component: str = "",
) -> list[dict]:
    """
    Return mock service centres for Coimbatore area.

    NOTE: This function now returns DEMO/MOCK data for the AutoRescue hackathon.
    No external API calls (Overpass, Google Places, etc.) are made.

    The dataset contains 10 deterministic service centres around Coimbatore.
    All locations are demo mock data, not verified real businesses.

    Args:
        latitude: User latitude
        longitude: User longitude
        issue: Vehicle issue description (for context, ignored for mock)
        affected_component: Affected component (for context, ignored for mock)

    Returns:
        List of 10 mock service centre dictionaries (all Coimbatore)
    """
    logger.info(f"[SERVICE] Using Coimbatore mock service dataset")
    logger.info(f"[SERVICE] User location: lat={latitude}, lon={longitude}")
    logger.info(f"[SERVICE] Issue: {issue or 'Not specified'} ({affected_component or 'General'})")

    # Return all 10 mock Coimbatore centres
    # Distance calculation will be done by the service agent
    mock_centres = get_mock_service_centres()

    logger.info(f"[SERVICE] Loaded {len(mock_centres)} mock service centres from Coimbatore dataset")

    return mock_centres
