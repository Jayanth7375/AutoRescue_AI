import os
import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from dotenv import load_dotenv
from uagents.communication import send_sync_message
from uagents_core.types import MsgStatus

from models import VehicleTelemetry, DiagnosticResult
from models.autorescue_api import (
    AutoRescueApiRequest,
    AutoRescueApiResponse,
    DiagnosisApiResponse,
    RescueApiResponse,
    ServiceCentreApiResponse,
)
from agents import diagnostic_agent
from agents.messages import (
    AutoRescueRequestMessage,
    AutoRescueResponseMessage,
    AutoRescueErrorMessage,
)
from services.chat_service import ChatRequest, ChatResponse, chat_with_autorescue

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ORCHESTRATOR_AGENT_ADDRESS = os.getenv("ORCHESTRATOR_AGENT_ADDRESS")

app = FastAPI(
    title="AutoRescue AI Backend",
    description="Vehicle diagnostic and safety assessment API",
    version="0.1.0",
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "AutoRescue AI Backend is running"}


@app.get("/health")
async def health():
    """Service health status endpoint."""
    return {
        "status": "ok",
        "service": "AutoRescue AI Backend",
    }


@app.post("/diagnose", response_model=DiagnosticResult)
async def diagnose(telemetry: VehicleTelemetry) -> DiagnosticResult:
    """
    Perform vehicle diagnostic analysis.

    Accepts vehicle telemetry data and returns a structured diagnostic result
    containing the most critical issue found and safety recommendations.

    Args:
        telemetry: Vehicle telemetry data containing engine, battery, tyre, and coolant information

    Returns:
        DiagnosticResult with issue details, severity, and recommendations
    """
    try:
        result = diagnostic_agent.run(telemetry)
        return result
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diagnostic analysis failed: {str(e)}")


@app.post("/api/autorescue/check", response_model=AutoRescueApiResponse)
async def autorescue_check(request: AutoRescueApiRequest):
    """
    Complete AutoRescue diagnostic and assistance check via Orchestrator.

    This endpoint:
    1. Routes request to Orchestrator uAgent synchronously
    2. Orchestrator coordinates Diagnostic, Service, and Rescue agents
    3. Returns unified response with diagnosis, service centres, and rescue recommendations

    Args:
        request: Vehicle telemetry and location data

    Returns:
        Unified AutoRescue response with diagnosis, services, and rescue info
    """
    try:
        if not ORCHESTRATOR_AGENT_ADDRESS:
            logger.error("ORCHESTRATOR_AGENT_ADDRESS not configured")
            raise HTTPException(
                status_code=503,
                detail="AutoRescue orchestration service is not configured",
            )

        request_id = str(uuid4())
        logger.info(f"[GATEWAY] Request {request_id} received")

        # Build message for Orchestrator
        orchestrator_msg = AutoRescueRequestMessage(
            request_id=request_id,
            vehicle_id=request.vehicle_id,
            engine_temperature=request.engine_temperature,
            battery_voltage=request.battery_voltage,
            front_left_tyre_psi=request.front_left_tyre_psi,
            front_right_tyre_psi=request.front_right_tyre_psi,
            rear_left_tyre_psi=request.rear_left_tyre_psi,
            rear_right_tyre_psi=request.rear_right_tyre_psi,
            coolant_level=request.coolant_level,
            latitude=request.latitude,
            longitude=request.longitude,
        )

        logger.info(f"[GATEWAY] {request_id} → ORCHESTRATOR")

        # Send synchronous message to Orchestrator
        result = await send_sync_message(
            destination=ORCHESTRATOR_AGENT_ADDRESS,
            message=orchestrator_msg,
            response_type=AutoRescueResponseMessage,
            timeout=120,
        )

        logger.info(f"[GATEWAY] {request_id} ← ORCHESTRATOR (type={type(result).__name__})")
        logger.debug(f"[GATEWAY] {request_id} result value: {repr(result)[:500]}")

        # Handle response based on type
        if isinstance(result, AutoRescueResponseMessage):
            # Success: convert to API response
            service_centres = [
                ServiceCentreApiResponse(
                    place_id=centre.place_id,
                    name=centre.name,
                    address=centre.address,
                    latitude=centre.latitude,
                    longitude=centre.longitude,
                    rating=centre.rating,
                    review_count=centre.review_count,
                    is_open=centre.is_open,
                    distance_km=centre.distance_km,
                    priority_score=centre.priority_score,
                    recommendation_reason=centre.recommendation_reason,
                )
                for centre in result.service_centres
            ]

            # Convert rescue if present
            rescue = None
            if result.rescue:
                rescue = RescueApiResponse(
                    assistance_required=result.rescue.assistance_required,
                    assistance_type=result.rescue.assistance_type,
                    priority=result.rescue.priority,
                    can_drive=result.rescue.can_drive,
                    tow_required=result.rescue.tow_required,
                    instructions=result.rescue.instructions,
                    reason=result.rescue.reason,
                    destination_name=result.rescue.destination_name,
                    destination_place_id=result.rescue.destination_place_id,
                    estimated_dispatch_minutes=result.rescue.estimated_dispatch_minutes,
                )

            # Build API response
            api_response = AutoRescueApiResponse(
                request_id=result.request_id,
                vehicle_id=result.vehicle_id,
                status=result.status,
                diagnosis=DiagnosisApiResponse(
                    issue=result.diagnosis.issue,
                    affected_component=result.diagnosis.affected_component,
                    severity=result.diagnosis.severity,
                    safe_to_drive=result.diagnosis.safe_to_drive,
                    recommendation=result.diagnosis.recommendation,
                ),
                service_centres=service_centres,
                navigation_allowed=result.navigation_allowed,
                rescue=rescue,
                message=result.message,
            )

            logger.info(f"[GATEWAY] {request_id} → CLIENT: {result.status}")
            return api_response

        elif isinstance(result, AutoRescueErrorMessage):
            # Error response from Orchestrator
            logger.error(f"[GATEWAY] {request_id}: Orchestrator error - {result.error}")
            raise HTTPException(
                status_code=500,
                detail=result.error,
            )

        elif isinstance(result, MsgStatus):
            # Communication failure
            logger.error(f"[GATEWAY] {request_id}: Communication failed - {result.detail}")
            raise HTTPException(
                status_code=503,
                detail="AutoRescue orchestration service is unavailable",
            )

        else:
            # Unexpected response type
            logger.error(
                f"[GATEWAY] {request_id}: Unexpected response type={type(result).__name__}",
            )
            logger.error(f"[GATEWAY] {request_id}: Response value: {repr(result)[:500]}")

            # If it's a dict or JSON-like, try to convert to AutoRescueResponseMessage
            if isinstance(result, dict):
                logger.info(f"[GATEWAY] {request_id}: Attempting to parse dict as AutoRescueResponseMessage")
                try:
                    response = AutoRescueResponseMessage(**result)
                    logger.info(f"[GATEWAY] {request_id} → CLIENT: {result.get('status', 'unknown')}")
                    api_response = AutoRescueApiResponse(
                        request_id=response.request_id,
                        vehicle_id=response.vehicle_id,
                        status=response.status,
                        diagnosis=DiagnosisApiResponse(
                            issue=response.diagnosis.issue,
                            affected_component=response.diagnosis.affected_component,
                            severity=response.diagnosis.severity,
                            safe_to_drive=response.diagnosis.safe_to_drive,
                            recommendation=response.diagnosis.recommendation,
                        ),
                        service_centres=[
                            ServiceCentreApiResponse(
                                place_id=centre.place_id,
                                name=centre.name,
                                address=centre.address,
                                latitude=centre.latitude,
                                longitude=centre.longitude,
                                rating=centre.rating,
                                review_count=centre.review_count,
                                is_open=centre.is_open,
                                distance_km=centre.distance_km,
                                priority_score=centre.priority_score,
                                recommendation_reason=centre.recommendation_reason,
                            )
                            for centre in response.service_centres
                        ],
                        navigation_allowed=response.navigation_allowed,
                        rescue=RescueApiResponse(
                            assistance_required=response.rescue.assistance_required,
                            assistance_type=response.rescue.assistance_type,
                            priority=response.rescue.priority,
                            can_drive=response.rescue.can_drive,
                            tow_required=response.rescue.tow_required,
                            instructions=response.rescue.instructions,
                            reason=response.rescue.reason,
                            destination_name=response.rescue.destination_name,
                            destination_place_id=response.rescue.destination_place_id,
                            estimated_dispatch_minutes=response.rescue.estimated_dispatch_minutes,
                        ) if response.rescue else None,
                        message=response.message,
                    )
                    return api_response
                except Exception as e:
                    logger.error(f"[GATEWAY] {request_id}: Failed to parse dict: {e}")

            raise HTTPException(
                status_code=500,
                detail=f"Invalid response from AutoRescue orchestration: {type(result).__name__}",
            )

    except ValidationError as e:
        logger.error(f"[GATEWAY] Validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"[GATEWAY] Unexpected error: {str(e)}", exc_info=True)
        logger.error(f"[GATEWAY] Error type: {type(e).__name__}")
        logger.error(f"[GATEWAY] Error details: {repr(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"AutoRescue service error: {str(e)[:200]}",
        )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with AutoRescue AI chatbot.

    The chatbot receives the latest vehicle diagnostic context and provides
    context-aware responses based on the vehicle's condition. Safety flags
    (safe_to_drive, navigation_allowed, tow_required) are authoritative.

    Args:
        request: Chat message with vehicle context

    Returns:
        ChatResponse with reply and optional suggested actions
    """
    logger.info(f"[CHAT] {request.vehicle_id}: {request.message[:50]}...")
    return await chat_with_autorescue(request)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
