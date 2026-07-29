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
    Direct 4-agent AutoRescue diagnostic check (stable demo mode).

    Gateway directly coordinates:
    - Diagnostic Agent (telemetry analysis)
    - Service Agent (service centre finder)
    - Rescue Agent (roadside assistance)
    """
    try:
        from agents.messages import (
            VehicleTelemetryMessage,
            DiagnosticResponseMessage,
            ServiceRequestMessage,
            ServiceResponseMessage,
            RescueRequestMessage,
            RescueResponseMessage,
            DiagnosisSummary,
            RescueSummary,
        )

        request_id = str(uuid4())
        logger.info(f"[GATEWAY-DEMO] Request {request_id} received")

        # Get agent addresses
        diag_addr = os.getenv("DIAGNOSTIC_AGENT_ADDRESS")
        svc_addr = os.getenv("SERVICE_AGENT_ADDRESS")
        resc_addr = os.getenv("RESCUE_AGENT_ADDRESS")

        if not diag_addr:
            raise ValueError("DIAGNOSTIC_AGENT_ADDRESS not configured")

        # Step 1: Call Diagnostic Agent
        logger.info(f"[GATEWAY-DEMO] {request_id} → DIAGNOSTIC")
        diag_msg = VehicleTelemetryMessage(
            request_id=request_id,
            vehicle_id=request.vehicle_id,
            engine_temperature=request.engine_temperature,
            battery_voltage=request.battery_voltage,
            front_left_tyre_psi=request.front_left_tyre_psi,
            front_right_tyre_psi=request.front_right_tyre_psi,
            rear_left_tyre_psi=request.rear_left_tyre_psi,
            rear_right_tyre_psi=request.rear_right_tyre_psi,
            coolant_level=request.coolant_level,
        )

        try:
            diag_result = await send_sync_message(
                destination=diag_addr,
                message=diag_msg,
                response_type=DiagnosticResponseMessage,
                timeout=30,
            )
        except Exception as e:
            logger.error(f"[GATEWAY-DEMO] {request_id}: Diagnostic communication error: {e}")
            diag_result = None

        if not isinstance(diag_result, DiagnosticResponseMessage):
            logger.error(f"[GATEWAY-DEMO] {request_id}: Diagnostic returned {type(diag_result).__name__ if diag_result else 'None'}")
            raise HTTPException(
                status_code=503,
                detail="Diagnostic service temporarily unavailable. Please try again."
            )

        logger.info(f"[GATEWAY-DEMO] {request_id} ← DIAGNOSTIC: {diag_result.severity}")

        # Initialize response data
        service_centres = []
        rescue = None
        status = "HEALTHY" if diag_result.severity == "NORMAL" else (
            "SERVICE_RECOMMENDED" if diag_result.severity == "WARNING" else "ASSISTANCE_REQUIRED"
        )
        message = "Vehicle systems are operating within normal ranges." if diag_result.severity == "NORMAL" else "Vehicle requires attention"
        navigation_allowed = diag_result.safe_to_drive

        # Step 2: Call Service Agent if needed
        if diag_result.severity != "NORMAL" and svc_addr:
            logger.info(f"[GATEWAY-DEMO] {request_id} → SERVICE")
            svc_msg = ServiceRequestMessage(
                request_id=request_id,
                vehicle_id=request.vehicle_id,
                issue=diag_result.issue,
                affected_component=diag_result.affected_component,
                severity=diag_result.severity,
                safe_to_drive=diag_result.safe_to_drive,
                latitude=request.latitude,
                longitude=request.longitude,
            )

            svc_result = await send_sync_message(
                destination=svc_addr,
                message=svc_msg,
                response_type=ServiceResponseMessage,
                timeout=30,
            )

            if isinstance(svc_result, ServiceResponseMessage):
                logger.info(f"[GATEWAY-DEMO] {request_id} ← SERVICE: {len(svc_result.centres)} centres")
                service_centres = svc_result.centres
                message = f"Found {len(svc_result.centres)} service centres nearby."

        # Step 3: Call Rescue Agent if CRITICAL
        if diag_result.severity == "CRITICAL" and resc_addr:
            logger.info(f"[GATEWAY-DEMO] {request_id} → RESCUE")
            resc_msg = RescueRequestMessage(
                request_id=request_id,
                vehicle_id=request.vehicle_id,
                issue=diag_result.issue,
                affected_component=diag_result.affected_component,
                severity=diag_result.severity,
                safe_to_drive=diag_result.safe_to_drive,
                latitude=request.latitude,
                longitude=request.longitude,
            )

            resc_result = await send_sync_message(
                destination=resc_addr,
                message=resc_msg,
                response_type=RescueResponseMessage,
                timeout=30,
            )

            if isinstance(resc_result, RescueResponseMessage):
                logger.info(f"[GATEWAY-DEMO] {request_id} ← RESCUE")
                rescue = RescueSummary(
                    assistance_required=resc_result.assistance_required,
                    assistance_type=resc_result.assistance_type,
                    priority=resc_result.priority,
                    can_drive=resc_result.can_drive,
                    tow_required=resc_result.tow_required,
                    instructions=resc_result.instructions,
                    reason=resc_result.reason,
                    destination_name=resc_result.destination_name,
                )
                navigation_allowed = False
                message = resc_result.instructions

        # Build internal response message
        result = AutoRescueResponseMessage(
            request_id=request_id,
            vehicle_id=request.vehicle_id,
            status=status,
            diagnosis=DiagnosisSummary(
                issue=diag_result.issue,
                affected_component=diag_result.affected_component,
                severity=diag_result.severity,
                safe_to_drive=diag_result.safe_to_drive,
                recommendation=diag_result.recommendation,
            ),
            service_centres=service_centres,
            navigation_allowed=navigation_allowed,
            rescue=rescue,
            message=message,
        )

        logger.info(f"[GATEWAY-DEMO] {request_id} → CLIENT: {status}")

        if isinstance(result, AutoRescueResponseMessage):
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
            logger.error(f"[GATEWAY] {request_id}: Orchestrator error - {result.error}")
            raise HTTPException(status_code=500, detail=result.error)

        elif isinstance(result, MsgStatus):
            logger.error(f"[GATEWAY] {request_id}: Communication failed - {result.detail}")
            raise HTTPException(
                status_code=503,
                detail="AutoRescue orchestration service is unavailable",
            )

        else:
            logger.error(f"[GATEWAY] {request_id}: Unexpected response type={type(result).__name__}")
            if isinstance(result, dict):
                try:
                    response = AutoRescueResponseMessage(**result)
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
                    logger.info(f"[GATEWAY] {request_id} → CLIENT: {response.status} (recovered)")
                    return api_response
                except Exception as e:
                    logger.error(f"[GATEWAY] {request_id}: Failed to parse dict: {e}")

            raise HTTPException(
                status_code=500,
                detail=f"Invalid response from orchestration: {type(result).__name__}",
            )

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
