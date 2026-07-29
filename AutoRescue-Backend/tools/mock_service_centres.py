"""Mock service centre dataset for Coimbatore - Demo/Hackathon version."""

# 10 demo service centres around Coimbatore
# These are MOCK locations for the AutoRescue hackathon prototype
# Do NOT represent these as verified real automotive service businesses
MOCK_SERVICE_CENTRES = [
    {
        "place_id": "mock_CBE001",
        "name": "AutoRescue Central Service Hub",
        "address": "Coimbatore Central, Coimbatore",
        "latitude": 11.0168,
        "longitude": 76.9558,
        "rating": 4.5,
        "review_count": 128,
        "is_open": True,
    },
    {
        "place_id": "mock_CBE002",
        "name": "AutoRescue Gandhipuram Garage",
        "address": "Gandhipuram, Coimbatore",
        "latitude": 11.0185,
        "longitude": 76.9674,
        "rating": 4.3,
        "review_count": 95,
        "is_open": True,
    },
    {
        "place_id": "mock_CBE003",
        "name": "AutoRescue Peelamedu Auto Care",
        "address": "Peelamedu, Coimbatore",
        "latitude": 11.0260,
        "longitude": 77.0210,
        "rating": 4.7,
        "review_count": 156,
        "is_open": True,
    },
    {
        "place_id": "mock_CBE004",
        "name": "AutoRescue RS Puram Service Point",
        "address": "RS Puram, Coimbatore",
        "latitude": 11.0065,
        "longitude": 76.9500,
        "rating": 4.1,
        "review_count": 72,
        "is_open": True,
    },
    {
        "place_id": "mock_CBE005",
        "name": "AutoRescue Saibaba Colony Garage",
        "address": "Saibaba Colony, Coimbatore",
        "latitude": 11.0265,
        "longitude": 76.9435,
        "rating": 4.4,
        "review_count": 104,
        "is_open": False,  # Closed for demo variety
    },
    {
        "place_id": "mock_CBE006",
        "name": "AutoRescue Singanallur Service Hub",
        "address": "Singanallur, Coimbatore",
        "latitude": 11.0005,
        "longitude": 77.0290,
        "rating": 4.6,
        "review_count": 142,
        "is_open": True,
    },
    {
        "place_id": "mock_CBE007",
        "name": "AutoRescue Ukkadam Auto Care",
        "address": "Ukkadam, Coimbatore",
        "latitude": 10.9905,
        "longitude": 76.9620,
        "rating": 4.2,
        "review_count": 81,
        "is_open": True,
    },
    {
        "place_id": "mock_CBE008",
        "name": "AutoRescue Kuniyamuthur Garage",
        "address": "Kuniyamuthur, Coimbatore",
        "latitude": 10.9645,
        "longitude": 76.9545,
        "rating": 4.4,
        "review_count": 98,
        "is_open": True,
    },
    {
        "place_id": "mock_CBE009",
        "name": "AutoRescue Saravanampatti Service Point",
        "address": "Saravanampatti, Coimbatore",
        "latitude": 11.0790,
        "longitude": 76.9990,
        "rating": 4.5,
        "review_count": 111,
        "is_open": True,
    },
    {
        "place_id": "mock_CBE010",
        "name": "AutoRescue Podanur Auto Care",
        "address": "Podanur, Coimbatore",
        "latitude": 10.9630,
        "longitude": 76.9885,
        "rating": 4.3,
        "review_count": 87,
        "is_open": True,
    },
]


def get_mock_service_centres() -> list[dict]:
    """
    Return the mock service centres dataset.

    Returns:
        List of 10 mock service centre dictionaries
    """
    return MOCK_SERVICE_CENTRES.copy()
