"""Google Places API service for nearby place searches."""

import os
import logging
import math
from typing import Optional
from pydantic import BaseModel

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
PLACES_API_BASE_URL = "https://places.googleapis.com/v1"


class PlaceModel(BaseModel):
    """Nearby place result."""
    id: str
    name: str
    address: str
    latitude: float
    longitude: float
    distance_km: float
    rating: Optional[float] = None


class NearbyPlacesModel(BaseModel):
    """Nearby places search result."""
    category: str
    count: int
    places: list[PlaceModel]


class NearbyPlacesService:
    """Service for searching nearby places using Google Places API."""

    PLACE_TYPE_MAP = {
        "EV_CHARGING": "electric_vehicle_charging_station",
        "BATTERY_SERVICE": "car_repair",  # Fallback to car_repair for battery
        "FUEL_STATION": "gas_station",
        "HOSPITAL": "hospital",
    }

    SUPPORTED_CATEGORIES = list(PLACE_TYPE_MAP.keys())

    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in km."""
        R = 6371  # Earth radius in km
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @staticmethod
    async def search_nearby_places(
        latitude: float,
        longitude: float,
        category: str,
        max_results: int = 10,
        initial_radius_m: int = 10000,
    ) -> NearbyPlacesModel:
        """
        Search for nearby places using Google Places API (New).

        Args:
            latitude: User latitude
            longitude: User longitude
            category: Place category (EV_CHARGING, BATTERY_SERVICE, FUEL_STATION, HOSPITAL)
            max_results: Maximum results to return (default 10)
            initial_radius_m: Initial search radius in meters (default 10km)

        Returns:
            NearbyPlacesModel with search results
        """
        if not GOOGLE_PLACES_API_KEY:
            logger.error("GOOGLE_PLACES_API_KEY not configured")
            raise ValueError("Google Places API key not configured")

        if category not in NearbyPlacesService.SUPPORTED_CATEGORIES:
            logger.error(f"Unsupported category: {category}")
            raise ValueError(f"Unsupported category: {category}")

        place_type = NearbyPlacesService.PLACE_TYPE_MAP.get(category)
        if not place_type:
            raise ValueError(f"Cannot map category {category} to place type")

        try:
            # Try initial radius first
            places = await NearbyPlacesService._search_with_radius(
                latitude, longitude, place_type, max_results, initial_radius_m
            )

            # If fewer than 5 results and we started with 10km, expand to 25km
            if len(places) < 5 and initial_radius_m == 10000:
                logger.info(f"Expanding search radius for {category}")
                places = await NearbyPlacesService._search_with_radius(
                    latitude, longitude, place_type, max_results, 25000
                )

            # Sort by distance
            places.sort(key=lambda p: p.distance_km)

            return NearbyPlacesModel(
                category=category,
                count=len(places),
                places=places[:max_results]
            )

        except Exception as e:
            logger.error(f"Error searching nearby places: {e}")
            raise

    @staticmethod
    async def _search_with_radius(
        latitude: float,
        longitude: float,
        place_type: str,
        max_results: int,
        radius_m: int
    ) -> list[PlaceModel]:
        """Search nearby places with given radius."""
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
        }

        request_body = {
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                    "radius": radius_m,
                }
            },
            "includedTypes": [place_type],
            "maxResultCount": max_results,
            "rankPreference": "DISTANCE",
        }

        field_mask = "places.id,places.displayName,places.formattedAddress,places.location,places.rating"

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    f"{PLACES_API_BASE_URL}/places:searchNearby",
                    json=request_body,
                    headers=headers,
                    params={"fields": field_mask},
                )

                if response.status_code != 200:
                    logger.error(f"Places API error: {response.status_code} {response.text}")
                    return []

                data = response.json()
                places = []

                for place in data.get("places", []):
                    place_id = place.get("id", "")
                    name = place.get("displayName", {}).get("text", "Unknown")
                    address = place.get("formattedAddress", "")
                    location = place.get("location", {})
                    lat = location.get("latitude", 0)
                    lon = location.get("longitude", 0)
                    rating = place.get("rating")

                    # Calculate distance
                    distance_km = NearbyPlacesService._haversine_distance(
                        latitude, longitude, lat, lon
                    )

                    places.append(
                        PlaceModel(
                            id=place_id,
                            name=name,
                            address=address,
                            latitude=lat,
                            longitude=lon,
                            distance_km=round(distance_km, 1),
                            rating=rating,
                        )
                    )

                return places

            except httpx.TimeoutException:
                logger.error("Places API request timeout")
                return []
            except Exception as e:
                logger.error(f"Error calling Places API: {e}")
                return []
