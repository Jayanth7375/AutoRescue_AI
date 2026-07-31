"""Mock nearby places service for development."""

import os
import logging
import math
from typing import Optional
from pydantic import BaseModel

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Mock data for development - no real API key needed
USE_MOCK_DATA = True


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

    # Mock data for Coimbatore area
    MOCK_DATA = {
        "HOSPITAL": [
            PlaceModel(id="h1", name="Apollo Hospitals Coimbatore", address="Avinashi Rd, Coimbatore", latitude=11.0186, longitude=76.9629, distance_km=0.8, rating=4.5),
            PlaceModel(id="h2", name="Madras Medical College Hospital", address="Trichy Rd, Coimbatore", latitude=11.0412, longitude=76.9694, distance_km=1.2, rating=4.2),
            PlaceModel(id="h3", name="CMC Hospital", address="Govt Hospital Rd, Coimbatore", latitude=11.0268, longitude=76.9542, distance_km=0.5, rating=4.3),
            PlaceModel(id="h4", name="Sree Mookambika Hospital", address="Mettupalayam Rd, Coimbatore", latitude=11.0156, longitude=76.9512, distance_km=1.0, rating=4.1),
            PlaceModel(id="h5", name="PSG Hospitals", address="Peelamedu, Coimbatore", latitude=11.0158, longitude=76.9892, distance_km=1.5, rating=4.6),
        ],
        "EV_CHARGING": [
            PlaceModel(id="ev1", name="Tesla Supercharger - Forum", address="Cosmo City Mall, Coimbatore", latitude=11.0219, longitude=76.9563, distance_km=0.3, rating=4.7),
            PlaceModel(id="ev2", name="Okaya EV Charging Station", address="Race Course Rd, Coimbatore", latitude=11.0284, longitude=76.9612, distance_km=0.7, rating=4.4),
            PlaceModel(id="ev3", name="Chargeup EV Station", address="Oppanakara St, Coimbatore", latitude=11.0156, longitude=76.9489, distance_km=1.1, rating=4.2),
            PlaceModel(id="ev4", name="E-Verse Charging Hub", address="Avinashi Rd, Coimbatore", latitude=11.0195, longitude=76.9631, distance_km=0.6, rating=4.3),
            PlaceModel(id="ev5", name="Blue Smart Charging Station", address="Mettupalayam, Coimbatore", latitude=11.0289, longitude=76.9745, distance_km=1.3, rating=4.1),
        ],
        "BATTERY_SERVICE": [
            PlaceModel(id="b1", name="Amaron Battery Service Center", address="Gandhipuram, Coimbatore", latitude=11.0189, longitude=76.9687, distance_km=0.4, rating=4.3),
            PlaceModel(id="b2", name="Exide Car Battery Shop", address="Big Bazaar Rd, Coimbatore", latitude=11.0245, longitude=76.9512, distance_km=0.8, rating=4.1),
            PlaceModel(id="b3", name="Luminous Power Centre", address="Brookefields, Coimbatore", latitude=11.0312, longitude=76.9856, distance_km=1.2, rating=4.2),
            PlaceModel(id="b4", name="Autocare Battery Service", address="Kavundampalayam, Coimbatore", latitude=11.0421, longitude=76.9834, distance_km=1.6, rating=3.9),
            PlaceModel(id="b5", name="Okaya Auto Service", address="Peelamedu, Coimbatore", latitude=11.0158, longitude=76.9892, distance_km=1.4, rating=4.0),
        ],
        "FUEL_STATION": [
            PlaceModel(id="f1", name="IOCL Petrol Pump - Gandhipuram", address="Gandhipuram Main Rd, Coimbatore", latitude=11.0189, longitude=76.9687, distance_km=0.4, rating=4.2),
            PlaceModel(id="f2", name="BPCL Fuel Station - Race Course", address="Race Course Rd, Coimbatore", latitude=11.0284, longitude=76.9612, distance_km=0.7, rating=4.1),
            PlaceModel(id="f3", name="Shell Petrol Pump", address="Avinashi Rd, Coimbatore", latitude=11.0195, longitude=76.9631, distance_km=0.6, rating=4.3),
            PlaceModel(id="f4", name="HP Fuel Station - Brookefields", address="Brookefields, Coimbatore", latitude=11.0312, longitude=76.9856, distance_km=1.2, rating=4.0),
            PlaceModel(id="f5", name="IOCL Petrol Pump - Mettupalayam", address="Mettupalayam Rd, Coimbatore", latitude=11.0289, longitude=76.9745, distance_km=1.3, rating=3.9),
        ],
    }

    @staticmethod
    async def search_nearby_places(
        latitude: float,
        longitude: float,
        category: str,
        max_results: int = 10,
        initial_radius_m: int = 10000,
    ) -> NearbyPlacesModel:
        """
        Search for nearby places (using mock data for development).

        Args:
            latitude: User latitude
            longitude: User longitude
            category: Place category (EV_CHARGING, BATTERY_SERVICE, FUEL_STATION, HOSPITAL)
            max_results: Maximum results to return (default 10)
            initial_radius_m: Initial search radius in meters (default 10km)

        Returns:
            NearbyPlacesModel with search results
        """
        if category not in NearbyPlacesService.SUPPORTED_CATEGORIES:
            logger.error(f"Unsupported category: {category}")
            raise ValueError(f"Unsupported category: {category}")

        logger.info(f"[RESCUE-MOCK] Searching nearby {category} at {latitude},{longitude}")

        # Return mock data for the category
        mock_places = NearbyPlacesService.MOCK_DATA.get(category, [])

        # Sort by distance from requested location
        sorted_places = sorted(
            mock_places,
            key=lambda p: NearbyPlacesService._haversine_distance(latitude, longitude, p.latitude, p.longitude)
        )

        # Update distances based on actual request location
        result_places = []
        for place in sorted_places[:max_results]:
            updated_distance = NearbyPlacesService._haversine_distance(
                latitude, longitude, place.latitude, place.longitude
            )
            result_places.append(PlaceModel(
                id=place.id,
                name=place.name,
                address=place.address,
                latitude=place.latitude,
                longitude=place.longitude,
                distance_km=round(updated_distance, 1),
                rating=place.rating,
            ))

        logger.info(f"[RESCUE-MOCK] Returning {len(result_places)} places for {category}")
        return NearbyPlacesModel(
            category=category,
            count=len(result_places),
            places=result_places
        )

