"""Standalone Overpass API diagnostic test - no uAgents."""

import os
import logging
import httpx

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

OVERPASS_API_URL = os.getenv("OVERPASS_API_URL", "https://overpass-api.de/api/interpreter")

# Test coordinates (Mumbai area)
LATITUDE = 19.076
LONGITUDE = 72.8777

# Simplified query - search only for car_repair shops (smaller result set)
QUERY = f"""[out:json][timeout:60];
(
  node["shop"="car_repair"](around:10000,{LATITUDE},{LONGITUDE});
  way["shop"="car_repair"](around:10000,{LATITUDE},{LONGITUDE});
);
out center;"""

# Alternative query with tyres (if first fails)
QUERY_WITH_TYRES = f"""[out:json][timeout:60];
(
  node["shop"="car_repair"](around:10000,{LATITUDE},{LONGITUDE});
  way["shop"="car_repair"](around:10000,{LATITUDE},{LONGITUDE});
  node["shop"="tyres"](around:10000,{LATITUDE},{LONGITUDE});
  way["shop"="tyres"](around:10000,{LATITUDE},{LONGITUDE});
);
out center;"""


def test_overpass():
    """Test Overpass API connection and query validity."""
    logger.info("=" * 60)
    logger.info("Overpass API Diagnostic Test")
    logger.info("=" * 60)
    logger.info(f"API URL: {OVERPASS_API_URL}")
    logger.info(f"Location: {LATITUDE}, {LONGITUDE}")

    logger.debug("Generated Overpass query:")
    logger.debug(QUERY)

    try:
        logger.info("\nAttempt 1: Simplified query (car_repair only)")
        logger.info("Sending POST request to Overpass API...")
        logger.info("Using data={'data': query} format")

        headers = {
            "User-Agent": "AutoRescueAI/0.1",
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                OVERPASS_API_URL,
                data={"data": QUERY},
                headers=headers,
            )

        # If first query times out or fails, try with tyres
        if response.status_code == 504:
            logger.warning("Server timeout on first query, trying with more specific tags...")
            logger.info("Attempt 2: Car repair + tyres query")
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    OVERPASS_API_URL,
                    data={"data": QUERY_WITH_TYRES},
                    headers=headers,
                )

        logger.info(f"\nOverpass HTTP Status: {response.status_code}")

        # Check for errors
        if response.status_code == 400:
            logger.error("\n" + "=" * 60)
            logger.error("✗ HTTP 400 Bad Request")
            logger.error("=" * 60)
            logger.error("The Overpass server rejected the query.")
            logger.error("\nResponse body:")
            logger.error(response.text[:1000])
            logger.error("\nQuery that was sent:")
            logger.error(QUERY)
            return False

        if response.status_code != 200:
            logger.error(f"\n✗ Unexpected status code: {response.status_code}")
            logger.error(f"Response: {response.text[:500]}")
            return False

        # Parse response
        data = response.json()

        elements = data.get("elements", [])
        logger.info(f"\n✓ HTTP 200 OK")
        logger.info(f"Elements Found: {len(elements)}")

        if not elements:
            logger.warning("No service centres found in this area")
            return True

        # Show first 5 elements
        logger.info("\nFirst 5 Service Centres:")
        logger.info("-" * 60)

        for i, elem in enumerate(elements[:5], 1):
            elem_type = elem.get("type")
            elem_id = elem.get("id")
            name = elem.get("tags", {}).get("name", "Unknown")

            if elem_type == "node":
                lat = elem.get("lat")
                lon = elem.get("lon")
            else:
                center = elem.get("center", {})
                lat = center.get("lat")
                lon = center.get("lon")

            logger.info(f"\n{i}. {name}")
            logger.info(f"   Type: {elem_type} (ID: {elem_id})")
            logger.info(f"   Location: {lat}, {lon}")
            logger.info(f"   Tags: {elem.get('tags', {})}")

        logger.info("\n" + "=" * 60)
        logger.info("✓ DIAGNOSTIC TEST PASSED")
        logger.info("=" * 60)
        logger.info(f"Overpass API is working correctly")
        logger.info(f"Found {len(elements)} total elements")
        logger.info(f"Ready to integrate with Service Agent")

        return True

    except httpx.TimeoutException as e:
        logger.error(f"\n✗ Timeout: {str(e)}")
        logger.error("Overpass API took too long to respond")
        return False

    except httpx.ConnectError as e:
        logger.error(f"\n✗ Connection error: {str(e)}")
        logger.error("Cannot reach Overpass API")
        logger.error(f"Check URL: {OVERPASS_API_URL}")
        return False

    except httpx.HTTPError as e:
        logger.error(f"\n✗ HTTP error: {str(e)}")
        return False

    except ValueError as e:
        logger.error(f"\n✗ Invalid JSON response: {str(e)}")
        return False

    except Exception as e:
        logger.error(f"\n✗ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_overpass()
    exit(0 if success else 1)
