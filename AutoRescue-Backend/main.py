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
    AutoRescueApiResponseExtended,
    DiagnosisApiResponse,
    RescueApiResponse,
    ServiceCentreApiResponse,
    TelemetryValidationApiResponse,
    SafetyApiResponse,
    MaintenanceApiResponse,
    NotificationApiResponse,
    ExplanationApiResponse,
    VerificationApiResponse,
    AgentTraceEntryApiResponse,
)
from agents import diagnostic_agent
from agents.messages import (
    AutoRescueRequestMessage,
    AutoRescueResponseMessage,
    AutoRescueResponseMessageExtended,
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
    Phase 9 AutoRescue diagnostic check - Real 10-Agent Orchestration.

    Coordinates all 10 agents:
    - Telemetry Validation
    - Diagnostic Analysis
    - Safety Determination
    - Maintenance Recommendation
    - Service Centre Search (conditional)
    - Rescue Assessment (conditional)
    - Notifications
    - AI Explanation
    - Verification
    - Orchestrator Coordination
    """
    try:
        from agents.messages import (
            AutoRescueRequestMessage,
            AutoRescueResponseMessageExtended,
            DiagnosisSummary,
            RescueSummary,
        )

        request_id = str(uuid4())
        logger.info(f"[GATEWAY-P9] Request {request_id} received")

        # Get orchestrator agent address
        orch_addr = os.getenv("ORCHESTRATOR_AGENT_ADDRESS")
        if not orch_addr:
            raise ValueError("ORCHESTRATOR_AGENT_ADDRESS not configured")

        # Build orchestrator request
        orch_request = AutoRescueRequestMessage(
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

        logger.info(f"[GATEWAY-P9] {request_id} → ORCHESTRATOR (10-agent)")
        try:
            result = await send_sync_message(
                destination=orch_addr,
                message=orch_request,
                response_type=AutoRescueResponseMessageExtended,
                timeout=60,
            )
        except Exception as e:
            logger.error(f"[GATEWAY-P9] {request_id}: Orchestrator communication error: {e}")
            raise HTTPException(
                status_code=503,
                detail="AutoRescue orchestration service temporarily unavailable. Please try again."
            )

        if not isinstance(result, AutoRescueResponseMessageExtended):
            logger.error(f"[GATEWAY-P9] {request_id}: Orchestrator returned {type(result).__name__ if result else 'None'}")
            raise HTTPException(
                status_code=503,
                detail="Orchestrator service returned invalid response."
            )

        logger.info(f"[GATEWAY-P9] {request_id} ← ORCHESTRATOR: {result.status}")

        # Map status string
        status = "HEALTHY" if result.status == "HEALTHY" else (
            "SERVICE_RECOMMENDED" if result.status == "WARNING" else (
                "ASSISTANCE_REQUIRED" if result.status == "CRITICAL" else "ERROR"
            )
        )
        navigation_allowed = result.navigation_allowed
        service_centres = result.service_centres
        rescue = None

        if result.rescue:
            rescue = RescueSummary(
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
            navigation_allowed = False
            message = result.rescue.instructions
        else:
            message = result.message

        # Build internal response message for compatibility
        result_msg = AutoRescueResponseMessage(
            request_id=result.request_id,
            vehicle_id=result.vehicle_id,
            status=status,
            diagnosis=result.diagnosis,
            service_centres=service_centres,
            navigation_allowed=navigation_allowed,
            rescue=rescue,
            message=message,
        )

        logger.info(f"[GATEWAY-P9] {request_id} → CLIENT: {status}")

        # Convert internal response to API response
        service_centres_api = [
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
            for centre in service_centres
        ]

        rescue_api = None
        if rescue:
            rescue_api = RescueApiResponse(
                assistance_required=rescue.assistance_required,
                assistance_type=rescue.assistance_type,
                priority=rescue.priority,
                can_drive=rescue.can_drive,
                tow_required=rescue.tow_required,
                instructions=rescue.instructions,
                reason=rescue.reason,
                destination_name=rescue.destination_name,
                destination_place_id=rescue.destination_place_id,
                estimated_dispatch_minutes=rescue.estimated_dispatch_minutes,
            )

        api_response = AutoRescueApiResponse(
            request_id=result_msg.request_id,
            vehicle_id=result_msg.vehicle_id,
            status=status,
            diagnosis=DiagnosisApiResponse(
                issue=result_msg.diagnosis.issue,
                affected_component=result_msg.diagnosis.affected_component,
                severity=result_msg.diagnosis.severity,
                safe_to_drive=result_msg.diagnosis.safe_to_drive,
                recommendation=result_msg.diagnosis.recommendation,
            ),
            service_centres=service_centres_api,
            navigation_allowed=navigation_allowed,
            rescue=rescue_api,
            message=message,
        )

        return api_response

    except ValidationError as e:
        logger.error(f"[GATEWAY] Validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"[GATEWAY] Unexpected error: {str(e)}", exc_info=True)
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
