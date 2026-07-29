"""Service centre ranking and scoring logic."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Scoring weights for OpenStreetMap (must sum to 100)
# Note: Google Places weights removed; OSM doesn't provide ratings
WEIGHT_DISTANCE = 40
WEIGHT_ISSUE_RELEVANCE = 30
WEIGHT_OPEN_STATUS = 20
WEIGHT_DATA_COMPLETENESS = 10


def calculate_issue_relevance_score(affected_component: str, osm_tags: dict) -> float:
    """
    Calculate relevance score based on issue type and OSM tags.

    Args:
        affected_component: The affected vehicle component
        osm_tags: OpenStreetMap tags for the business

    Returns:
        Score from 0-100
    """
    component_lower = affected_component.lower() if affected_component else ""
    shop = osm_tags.get("shop", "").lower()
    tags_str = " ".join(f"{k}={v}".lower() for k, v in osm_tags.items())

    # Tyre-related issues
    if "tyre" in component_lower or "tire" in component_lower:
        if shop == "tyres":
            return 100.0
        if osm_tags.get("service:vehicle:tyres") == "yes":
            return 95.0
        if shop == "car_repair":
            return 75.0
        return 40.0

    # Battery/electrical issues
    elif "battery" in component_lower or "electrical" in component_lower:
        if osm_tags.get("service:vehicle:electrical") == "yes":
            return 100.0
        if shop == "car_repair":
            return 80.0
        return 40.0

    # Engine, coolant, brake, transmission issues
    elif any(word in component_lower for word in ["engine", "coolant", "brake", "transmission"]):
        if shop == "car_repair":
            return 100.0
        if osm_tags.get("service:vehicle:car_repair") == "yes":
            return 95.0
        return 50.0

    # Default: any car-related shop
    if shop in ["car_repair", "car", "mechanic"]:
        return 70.0

    if "service:vehicle:" in tags_str:
        return 60.0

    return 30.0


def normalize_score(value: float, min_val: float, max_val: float, weight: int) -> float:
    """Normalize a score to 0-weight range."""
    if max_val <= min_val:
        return weight * 50 / 100  # Return half weight if can't normalize

    normalized = (value - min_val) / (max_val - min_val)
    return max(0, min(weight, normalized * weight))


def calculate_data_completeness_score(tags: dict) -> float:
    """
    Calculate score based on data completeness.

    Rewards presence of useful fields:
    - name, address, phone, website, opening_hours, service tags
    """
    score = 0
    max_score = 100

    # Check for important fields
    important_fields = [
        ("name", 30),
        ("address", 20),
        ("phone", 15),
        ("website", 15),
        ("opening_hours", 10),
    ]

    for field, points in important_fields:
        if field in tags or f"addr:{field}" in tags or f"contact:{field}" in tags:
            score += points

    # Check for service tags
    if any(k.startswith("service:vehicle:") for k in tags.keys()):
        score += 10

    return min(score, max_score)


def rank_service_centres(
    candidates: list[dict],
    user_latitude: float,
    user_longitude: float,
    affected_component: str,
    severity: str,
) -> list[dict]:
    """
    Rank service centres using multi-factor scoring (OpenStreetMap version).

    Args:
        candidates: List of service centre candidates from Overpass API
        user_latitude: User's latitude
        user_longitude: User's longitude
        affected_component: Vehicle component that needs service
        severity: Issue severity (NORMAL, WARNING, CRITICAL)

    Returns:
        Sorted list of candidates with priority_score and recommendation_reason
    """
    if not candidates:
        return []

    scored = []

    # Calculate distance scores
    min_distance = min(c.get("distance_km", float("inf")) for c in candidates if c.get("distance_km"))
    max_distance = max(c.get("distance_km", 0) for c in candidates if c.get("distance_km"))

    for centre in candidates:
        scores = {}

        # Distance score (lower is better) - 40%
        if centre.get("distance_km"):
            distance_normalized = 100 - normalize_score(
                centre["distance_km"], min_distance, max_distance, 100
            )
            scores["distance"] = normalize_score(distance_normalized, 0, 100, WEIGHT_DISTANCE)
        else:
            scores["distance"] = 0

        # Issue relevance score - 30%
        tags = centre.get("tags", {})
        relevance = calculate_issue_relevance_score(affected_component, tags)
        scores["relevance"] = normalize_score(relevance, 0, 100, WEIGHT_ISSUE_RELEVANCE)

        # Open status score - 20%
        is_open = centre.get("is_open")
        if is_open is True:
            scores["open"] = WEIGHT_OPEN_STATUS
        elif is_open is False:
            # For CRITICAL severity, heavily penalize closed businesses
            scores["open"] = WEIGHT_OPEN_STATUS * 0.2 if severity == "CRITICAL" else WEIGHT_OPEN_STATUS * 0.4
        else:
            # Unknown status (neutral)
            scores["open"] = WEIGHT_OPEN_STATUS * 0.7

        # Data completeness score - 10%
        completeness = calculate_data_completeness_score(tags)
        scores["data"] = normalize_score(completeness, 0, 100, WEIGHT_DATA_COMPLETENESS)

        total_score = sum(scores.values())

        # Generate recommendation reason
        reason_parts = []

        # Open status
        if is_open is True:
            reason_parts.append("Open now")
        elif is_open is False and severity == "CRITICAL":
            reason_parts.append("⚠ Closed")
        elif is_open is False:
            reason_parts.append("Currently closed")

        # Distance
        distance = centre.get("distance_km")
        if distance:
            reason_parts.append(f"{distance} km away")

        # Relevance
        if relevance >= 80:
            reason_parts.append(f"Relevant for {affected_component}")
        elif relevance >= 50:
            reason_parts.append("Automotive repair service")

        recommendation_reason = " • ".join(reason_parts)

        scored.append({
            **centre,
            "priority_score": round(total_score, 1),
            "recommendation_reason": recommendation_reason,
        })

    # Sort by priority score descending
    scored.sort(key=lambda x: x["priority_score"], reverse=True)

    return scored


def get_top_centres(ranked: list[dict], limit: int = 10) -> list[dict]:
    """Get top N ranked centres."""
    return ranked[:limit]
