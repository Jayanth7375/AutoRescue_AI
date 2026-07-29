"""Orchestrator Agent - coordinates Diagnostic, Service, and Rescue agents."""

import os
import logging

from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    AutoRescueRequestMessage,
    AutoRescueResponseMessage,
    AutoRescueErrorMessage,
    VehicleTelemetryMessage,
    DiagnosticResponseMessage,
    DiagnosticErrorMessage,
    ServiceRequestMessage,
    ServiceResponseMessage,
    ServiceErrorMessage,
    RescueRequestMessage,
    RescueResponseMessage,
    RescueErrorMessage,
    DiagnosisSummary,
    RescueSummary,
)
from models.autorescue_api import ServiceCentreApiResponse
from orchestration.workflow_store import get_workflow_store

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
ORCHESTRATOR_AGENT_SEED = os.getenv("ORCHESTRATOR_AGENT_SEED", "autorescue-orchestrator-agent-development-seed")
ORCHESTRATOR_AGENT_PORT = int(os.getenv("ORCHESTRATOR_AGENT_PORT", "8018"))

# Load specialist agent addresses
DIAGNOSTIC_AGENT_ADDRESS = os.getenv("DIAGNOSTIC_AGENT_ADDRESS")
SERVICE_AGENT_ADDRESS = os.getenv("SERVICE_AGENT_ADDRESS")
RESCUE_AGENT_ADDRESS = os.getenv("RESCUE_AGENT_ADDRESS")

# Create Orchestrator Agent
orchestrator_uagent = Agent(
    name="autorescue_orchestrator_agent",
    seed=ORCHESTRATOR_AGENT_SEED,
    port=ORCHESTRATOR_AGENT_PORT,
    endpoint=[f"http://127.0.0.1:{ORCHESTRATOR_AGENT_PORT}/submit"],
)

# Get workflow store
workflow_store = get_workflow_store()


# REMOVED: @on_message handler for AutoRescueRequestMessage
# Use @on_query handler below instead for proper synchronous request-response
# Reason: uAgents cannot have both @on_message and @on_query for the same message type
#         This was causing the same request to be processed twice


# ============================================================================
# ASYNCHRONOUS WORKFLOW HANDLERS
# ============================================================================
# These handlers are for internal agent-to-agent async communication ONLY.
# They are NOT the entry point for FastAPI gateway calls.
# The @on_query handler above is the synchronous entry point.
# ============================================================================

@orchestrator_uagent.on_message(model=DiagnosticResponseMessage)
async def handle_diagnostic_response(ctx: Context, sender: str, msg: DiagnosticResponseMessage):
    """Handle Diagnostic Agent response and route accordingly.

    NOTE: This handler is for asynchronous workflows only.
    For synchronous FastAPI calls, use the @on_query handler above.
    """
    try:
        request_id = msg.request_id
        logger.info(f"[ORCHESTRATOR] {request_id} ← DIAGNOSTIC RESPONSE HANDLER CALLED: severity={msg.severity}")

        workflow = workflow_store.get_workflow(request_id)
        if not workflow:
            logger.error(f"[ORCHESTRATOR] {request_id} Workflow NOT FOUND")
            return

        logger.info(f"[ORCHESTRATOR] {request_id} Workflow found, saving response...")
        # Save diagnostic response
        workflow_store.save_diagnostic_response(request_id, {
            "issue": msg.issue,
            "affected_component": msg.affected_component,
            "severity": msg.severity,
            "safe_to_drive": msg.safe_to_drive,
            "recommendation": msg.recommendation,
        })
        logger.info(f"[ORCHESTRATOR] {request_id} ✓ Diagnostic response SAVED")

        # Check severity
        if msg.severity == "NORMAL":
            logger.info(f"[ORCHESTRATOR] {request_id}: HEALTHY vehicle, no further action")
            response = AutoRescueResponseMessage(
                request_id=request_id,
                vehicle_id=msg.vehicle_id,
                status="HEALTHY",
                diagnosis=DiagnosisSummary(
                    issue=msg.issue,
                    affected_component=msg.affected_component,
                    severity=msg.severity,
                    safe_to_drive=msg.safe_to_drive,
                    recommendation=msg.recommendation,
                ),
                service_centres=[],
                navigation_allowed=True,
                rescue=None,
                message="Vehicle systems are operating within normal ranges.",
            )

            logger.info(f"[ORCHESTRATOR] {request_id} → CLIENT: HEALTHY")
            await ctx.send(workflow.original_sender, response)
            workflow_store.delete_workflow(request_id)
            return

        # Route to Service Agent if problem exists
        if not SERVICE_AGENT_ADDRESS:
            raise ValueError("SERVICE_AGENT_ADDRESS not configured")

        logger.info(f"[ORCHESTRATOR] {request_id} → SERVICE")
        workflow_store.update_stage(request_id, "SERVICE")

        service_msg = ServiceRequestMessage(
            request_id=request_id,
            vehicle_id=msg.vehicle_id,
            issue=msg.issue,
            affected_component=msg.affected_component,
            severity=msg.severity,
            safe_to_drive=msg.safe_to_drive,
            latitude=workflow.latitude,
            longitude=workflow.longitude,
        )

        await ctx.send(SERVICE_AGENT_ADDRESS, service_msg)

    except Exception as e:
        logger.error(f"[ORCHESTRATOR] Error handling diagnostic response: {str(e)}")


@orchestrator_uagent.on_message(model=ServiceResponseMessage)
async def handle_service_response(ctx: Context, sender: str, msg: ServiceResponseMessage):
    """Handle Service Agent response and route to Rescue if needed."""
    try:
        request_id = msg.request_id
        logger.info(f"[ORCHESTRATOR] {request_id} ← SERVICE: {len(msg.centres)} centres")

        workflow = workflow_store.get_workflow(request_id)
        if not workflow:
            logger.error(f"[ORCHESTRATOR] Workflow {request_id} not found")
            return

        # Save service response
        workflow_store.save_service_response(request_id, {
            "centres": [c.dict() for c in msg.centres],
            "navigation_allowed": msg.navigation_allowed,
            "tow_recommended": msg.tow_recommended,
        })

        diagnosis = workflow.diagnostic_response

        # If safe to drive, return now
        if diagnosis["safe_to_drive"]:
            logger.info(f"[ORCHESTRATOR] {request_id}: Safe to drive, returning service results")

            response = AutoRescueResponseMessage(
                request_id=request_id,
                vehicle_id=msg.vehicle_id,
                status="SERVICE_RECOMMENDED",
                diagnosis=DiagnosisSummary(**diagnosis),
                service_centres=msg.centres,
                navigation_allowed=True,
                rescue=None,
                message="Vehicle requires attention. Nearby service centres have been ranked for you.",
            )

            logger.info(f"[ORCHESTRATOR] {request_id} → CLIENT: SERVICE_RECOMMENDED")
            await ctx.send(workflow.original_sender, response)
            workflow_store.delete_workflow(request_id)
            return

        # Not safe - route to Rescue Agent
        if not RESCUE_AGENT_ADDRESS:
            raise ValueError("RESCUE_AGENT_ADDRESS not configured")

        logger.info(f"[ORCHESTRATOR] {request_id} → RESCUE")
        workflow_store.update_stage(request_id, "RESCUE")

        # Use top service centre as tow destination if available
        tow_destination = None
        if msg.centres:
            top_centre = msg.centres[0]
            tow_destination = {
                "service_centre_name": top_centre.name,
                "service_centre_place_id": top_centre.place_id,
                "service_centre_latitude": top_centre.latitude,
                "service_centre_longitude": top_centre.longitude,
            }

        rescue_msg = RescueRequestMessage(
            request_id=request_id,
            vehicle_id=msg.vehicle_id,
            issue=diagnosis["issue"],
            affected_component=diagnosis["affected_component"],
            severity=diagnosis["severity"],
            safe_to_drive=diagnosis["safe_to_drive"],
            latitude=workflow.latitude,
            longitude=workflow.longitude,
            **(tow_destination or {}),
        )

        await ctx.send(RESCUE_AGENT_ADDRESS, rescue_msg)

    except Exception as e:
        logger.error(f"[ORCHESTRATOR] Error handling service response: {str(e)}")


@orchestrator_uagent.on_message(model=RescueResponseMessage)
async def handle_rescue_response(ctx: Context, sender: str, msg: RescueResponseMessage):
    """Handle Rescue Agent response and return unified result."""
    try:
        request_id = msg.request_id
        logger.info(f"[ORCHESTRATOR] {request_id} ← RESCUE: {msg.assistance_type}")

        workflow = workflow_store.get_workflow(request_id)
        if not workflow:
            logger.error(f"[ORCHESTRATOR] Workflow {request_id} not found")
            return

        # Save rescue response
        workflow_store.save_rescue_response(request_id, {
            "assistance_required": msg.assistance_required,
            "assistance_type": msg.assistance_type,
            "priority": msg.priority,
            "can_drive": msg.can_drive,
            "tow_required": msg.tow_required,
            "instructions": msg.instructions,
            "reason": msg.reason,
            "destination_name": msg.destination_name,
            "destination_place_id": msg.destination_place_id,
            "estimated_dispatch_minutes": msg.estimated_dispatch_minutes,
        })

        diagnosis = workflow.diagnostic_response
        service_response = workflow.service_response or {}

        # Build unified response
        response = AutoRescueResponseMessage(
            request_id=request_id,
            vehicle_id=msg.vehicle_id,
            status="ASSISTANCE_REQUIRED",
            diagnosis=DiagnosisSummary(**diagnosis),
            service_centres=service_response.get("centres", []),
            navigation_allowed=False,
            rescue=RescueSummary(
                assistance_required=msg.assistance_required,
                assistance_type=msg.assistance_type,
                priority=msg.priority,
                can_drive=msg.can_drive,
                tow_required=msg.tow_required,
                instructions=msg.instructions,
                reason=msg.reason,
                destination_name=msg.destination_name,
                destination_place_id=msg.destination_place_id,
                estimated_dispatch_minutes=msg.estimated_dispatch_minutes,
            ),
            message="Vehicle is not safe to drive. Roadside assistance is recommended.",
        )

        logger.info(f"[ORCHESTRATOR] {request_id} → CLIENT: ASSISTANCE_REQUIRED")
        await ctx.send(workflow.original_sender, response)
        workflow_store.delete_workflow(request_id)

    except Exception as e:
        logger.error(f"[ORCHESTRATOR] Error handling rescue response: {str(e)}")


@orchestrator_uagent.on_message(model=DiagnosticErrorMessage)
async def handle_diagnostic_error(ctx: Context, sender: str, msg: DiagnosticErrorMessage):
    """Handle Diagnostic Agent error."""
    try:
        workflow = workflow_store.get_workflow(msg.request_id)
        if not workflow:
            return

        logger.error(f"[ORCHESTRATOR] {msg.request_id} ← DIAGNOSTIC ERROR: {msg.error}")

        error = AutoRescueErrorMessage(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            stage="DIAGNOSTIC",
            error=msg.error,
        )

        await ctx.send(workflow.original_sender, error)
        workflow_store.delete_workflow(msg.request_id)

    except Exception as e:
        logger.error(f"[ORCHESTRATOR] Error handling diagnostic error: {str(e)}")


@orchestrator_uagent.on_message(model=ServiceErrorMessage)
async def handle_service_error(ctx: Context, sender: str, msg: ServiceErrorMessage):
    """Handle Service Agent error."""
    try:
        workflow = workflow_store.get_workflow(msg.request_id)
        if not workflow:
            return

        logger.warning(f"[ORCHESTRATOR] {msg.request_id} ← SERVICE ERROR: {msg.error}")

        diagnosis = workflow.diagnostic_response
        if diagnosis and not diagnosis["safe_to_drive"]:
            # Still need rescue even if service discovery failed
            if RESCUE_AGENT_ADDRESS:
                logger.info(f"[ORCHESTRATOR] {msg.request_id} → RESCUE (service unavailable)")
                workflow_store.update_stage(msg.request_id, "RESCUE")

                rescue_msg = RescueRequestMessage(
                    request_id=msg.request_id,
                    vehicle_id=workflow.vehicle_id,
                    issue=diagnosis["issue"],
                    affected_component=diagnosis["affected_component"],
                    severity=diagnosis["severity"],
                    safe_to_drive=diagnosis["safe_to_drive"],
                    latitude=workflow.latitude,
                    longitude=workflow.longitude,
                )

                await ctx.send(RESCUE_AGENT_ADDRESS, rescue_msg)
                return

        # Service failed but vehicle is safe
        response = AutoRescueResponseMessage(
            request_id=msg.request_id,
            vehicle_id=workflow.vehicle_id,
            status="SERVICE_RECOMMENDED",
            diagnosis=DiagnosisSummary(**diagnosis),
            service_centres=[],
            navigation_allowed=True,
            rescue=None,
            message="Vehicle requires attention, but no nearby service centres were found.",
        )

        await ctx.send(workflow.original_sender, response)
        workflow_store.delete_workflow(msg.request_id)

    except Exception as e:
        logger.error(f"[ORCHESTRATOR] Error handling service error: {str(e)}")


@orchestrator_uagent.on_message(model=RescueErrorMessage)
async def handle_rescue_error(ctx: Context, sender: str, msg: RescueErrorMessage):
    """Handle Rescue Agent error."""
    try:
        workflow = workflow_store.get_workflow(msg.request_id)
        if not workflow:
            return

        logger.error(f"[ORCHESTRATOR] {msg.request_id} ← RESCUE ERROR: {msg.error}")

        diagnosis = workflow.diagnostic_response
        service_response = workflow.service_response or {}

        response = AutoRescueResponseMessage(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            status="ASSISTANCE_REQUIRED",
            diagnosis=DiagnosisSummary(**diagnosis),
            service_centres=service_response.get("centres", []),
            navigation_allowed=False,
            rescue=None,
            message="Vehicle requires assistance. Please contact emergency services if needed.",
        )

        await ctx.send(workflow.original_sender, response)
        workflow_store.delete_workflow(msg.request_id)

    except Exception as e:
        logger.error(f"[ORCHESTRATOR] Error handling rescue error: {str(e)}")


async def orchestrate_sync(
    ctx: Context,
    request: AutoRescueRequestMessage,
) -> AutoRescueResponseMessage:
    """
    Orchestrate multi-agent workflow for AutoRescue request.

    Calls Diagnostic Agent (synchronously via rules engine) to get severity,
    then routes to Service and Rescue agents as needed.
    """
    from models.telemetry import VehicleTelemetry
    from tools.diagnostic_rules import diagnose_vehicle
    from tools.places_tool import nearby_search
    from tools.distance import haversine_distance
    from tools.service_ranker import rank_service_centres, get_top_centres

    request_id = request.request_id
    logger.info(f"[ORCH-SYNC] {request_id} START")
    logger.info(f"[ORCH-SYNC] {request_id} Telemetry: engine={request.engine_temperature}, front_left_tyre={request.front_left_tyre_psi}, battery={request.battery_voltage}, coolant={request.coolant_level}")

    try:
        # Step 1: Call diagnostic rules engine directly
        telemetry = VehicleTelemetry(
            vehicle_id=request.vehicle_id,
            engine_temperature=request.engine_temperature,
            battery_voltage=request.battery_voltage,
            front_left_tyre_psi=request.front_left_tyre_psi,
            front_right_tyre_psi=request.front_right_tyre_psi,
            rear_left_tyre_psi=request.rear_left_tyre_psi,
            rear_right_tyre_psi=request.rear_right_tyre_psi,
            coolant_level=request.coolant_level,
        )

        diagnostic_result = diagnose_vehicle(telemetry)
        logger.info(f"[ORCH-SYNC] {request_id} Diagnostic severity: {diagnostic_result.severity.value}")

        # Convert severity enum to string
        severity_str = diagnostic_result.severity.value

        # If NORMAL: Return HEALTHY immediately
        if severity_str == "NORMAL":
            logger.info(f"[ORCH-SYNC] {request_id} Vehicle is HEALTHY")
            return AutoRescueResponseMessage(
                request_id=request_id,
                vehicle_id=request.vehicle_id,
                status="HEALTHY",
                diagnosis=DiagnosisSummary(
                    issue=diagnostic_result.issue,
                    affected_component=diagnostic_result.affected_component,
                    severity=severity_str,
                    safe_to_drive=diagnostic_result.safe_to_drive,
                    recommendation=diagnostic_result.recommendation,
                ),
                service_centres=[],
                navigation_allowed=True,
                rescue=None,
                message="Vehicle systems are operating within normal ranges.",
            )

        # If WARNING: Get service centres and return SERVICE_RECOMMENDED
        if severity_str == "WARNING":
            logger.info(f"[ORCH-SYNC] {request_id} Service required for {diagnostic_result.affected_component}")

            # Get service centres
            centres = nearby_search(
                latitude=request.latitude,
                longitude=request.longitude,
                issue=diagnostic_result.issue,
                affected_component=diagnostic_result.affected_component,
            )
            logger.info(f"[ORCH-SYNC] {request_id} Found {len(centres)} service centres")

            # Calculate distances and rank
            for centre in centres:
                centre["distance_km"] = haversine_distance(
                    request.latitude, request.longitude,
                    centre["latitude"], centre["longitude"],
                )

            ranked = rank_service_centres(
                candidates=centres,
                user_latitude=request.latitude,
                user_longitude=request.longitude,
                affected_component=diagnostic_result.affected_component,
                severity=severity_str,
            )

            top_centres = get_top_centres(ranked, limit=10)
            logger.info(f"[ORCH-SYNC] {request_id} Ranked to {len(top_centres)} top centres")

            # Convert to ServiceCentreApiResponse format
            centre_responses = [
                ServiceCentreApiResponse(
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

            return AutoRescueResponseMessage(
                request_id=request_id,
                vehicle_id=request.vehicle_id,
                status="SERVICE_RECOMMENDED",
                diagnosis=DiagnosisSummary(
                    issue=diagnostic_result.issue,
                    affected_component=diagnostic_result.affected_component,
                    severity=severity_str,
                    safe_to_drive=diagnostic_result.safe_to_drive,
                    recommendation=diagnostic_result.recommendation,
                ),
                service_centres=centre_responses,
                navigation_allowed=True,
                rescue=None,
                message=f"Vehicle requires service. {len(top_centres)} service centres nearby.",
            )

        # If CRITICAL: Get service centres and rescue assistance
        if severity_str == "CRITICAL":
            logger.info(f"[ORCH-SYNC] {request_id} Critical issue: {diagnostic_result.issue}")

            # Get service centres for CRITICAL too
            centres = nearby_search(
                latitude=request.latitude,
                longitude=request.longitude,
                issue=diagnostic_result.issue,
                affected_component=diagnostic_result.affected_component,
            )
            logger.info(f"[ORCH-SYNC] {request_id} Found {len(centres)} service centres for critical")

            # Calculate distances and rank
            for centre in centres:
                centre["distance_km"] = haversine_distance(
                    request.latitude, request.longitude,
                    centre["latitude"], centre["longitude"],
                )

            ranked = rank_service_centres(
                candidates=centres,
                user_latitude=request.latitude,
                user_longitude=request.longitude,
                affected_component=diagnostic_result.affected_component,
                severity=severity_str,
            )

            top_centres = get_top_centres(ranked, limit=10)
            logger.info(f"[ORCH-SYNC] {request_id} Critical scenario: {len(top_centres)} centres available")

            # Convert to response format
            centre_responses = [
                ServiceCentreApiResponse(
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

            # Select nearest centre as destination
            destination_centre = top_centres[0] if top_centres else None

            return AutoRescueResponseMessage(
                request_id=request_id,
                vehicle_id=request.vehicle_id,
                status="ASSISTANCE_REQUIRED",
                diagnosis=DiagnosisSummary(
                    issue=diagnostic_result.issue,
                    affected_component=diagnostic_result.affected_component,
                    severity=severity_str,
                    safe_to_drive=diagnostic_result.safe_to_drive,
                    recommendation=diagnostic_result.recommendation,
                ),
                service_centres=centre_responses,
                navigation_allowed=False,
                rescue=RescueSummary(
                    assistance_required=True,
                    assistance_type="TOW",
                    priority="HIGH",
                    can_drive=False,
                    tow_required=True,
                    instructions="Stop vehicle safely. Roadside assistance has been arranged.",
                    reason=diagnostic_result.issue,
                    destination_name=destination_centre["name"] if destination_centre else "Nearest service",
                    destination_place_id=destination_centre["place_id"] if destination_centre else "",
                    estimated_dispatch_minutes=15,
                ),
                message="Critical vehicle issue detected. Roadside assistance is dispatched.",
            )

        # Step 1: Send to Diagnostic Agent
        if not DIAGNOSTIC_AGENT_ADDRESS:
            raise ValueError("DIAGNOSTIC_AGENT_ADDRESS not configured")

        logger.info(f"[ORCH-SYNC] {request_id} → DIAGNOSTIC")
        workflow_store.update_stage(request_id, "DIAGNOSTIC")

        telemetry_msg = VehicleTelemetryMessage(
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

        logger.info(f"[ORCH-SYNC] {request_id} Sending to Diagnostic: {DIAGNOSTIC_AGENT_ADDRESS[:30]}...")
        await ctx.send(DIAGNOSTIC_AGENT_ADDRESS, telemetry_msg)

        # Wait for diagnostic response
        start_diag = time.time()
        poll_count = 0
        while True:
            workflow = workflow_store.get_workflow(request_id)
            if not workflow:
                raise ValueError(f"Workflow {request_id} expired")

            poll_count += 1
            if poll_count % 20 == 0:  # Log every 1 second (20 * 50ms)
                elapsed = time.time() - start_diag
                logger.info(f"[ORCH-SYNC] {request_id} Still waiting for DIAGNOSTIC... elapsed={elapsed:.1f}s")

            if workflow.diagnostic_response:
                elapsed_diag = time.time() - start_diag
                logger.info(f"[ORCH-SYNC] {request_id} ✓ DIAGNOSTIC RESPONSE received after {elapsed_diag:.2f}s")
                break

            if (time.time() - start_diag) > workflow.diagnostic_timeout:
                logger.error(f"[ORCH-SYNC] {request_id} DIAGNOSTIC TIMEOUT after {workflow.diagnostic_timeout}s")
                raise TimeoutError(f"Diagnostic timeout after {workflow.diagnostic_timeout}s")

            await asyncio.sleep(0.05)  # Poll every 50ms

        diagnosis_reply = workflow.diagnostic_response
        logger.info(f"[ORCH-SYNC] {request_id} ← DIAGNOSTIC: {diagnosis_reply.get('severity')}")

        # Step 2: Check if healthy
        if diagnosis_reply.get('severity') == "NORMAL":
            logger.info(f"[ORCH-SYNC] {request_id} BUILDING FINAL RESPONSE (HEALTHY)")
            logger.info(f"[ORCH-SYNC] {request_id}: Vehicle is HEALTHY, diagnosis_reply={diagnosis_reply}")

            response = AutoRescueResponseMessage(
                request_id=request_id,
                vehicle_id=request.vehicle_id,
                status="HEALTHY",
                diagnosis=DiagnosisSummary(
                    issue=diagnosis_reply.get('issue'),
                    affected_component=diagnosis_reply.get('affected_component'),
                    severity=diagnosis_reply.get('severity'),
                    safe_to_drive=diagnosis_reply.get('safe_to_drive'),
                    recommendation=diagnosis_reply.get('recommendation'),
                ),
                service_centres=[],
                navigation_allowed=True,
                rescue=None,
                message="Vehicle systems are operating within normal ranges.",
            )
            logger.info(f"[ORCH-SYNC] {request_id} ✓ AutoRescueResponseMessage created successfully")
            logger.info(f"[ORCH-SYNC] {request_id} Response status={response.status}, diagnosis={response.diagnosis}")
            return response

        # Step 3: Service Agent
        if not SERVICE_AGENT_ADDRESS:
            raise ValueError("SERVICE_AGENT_ADDRESS not configured")

        logger.info(f"[ORCH-SYNC] {request_id} BEFORE SERVICE")
        logger.info(f"[ORCH-SYNC] {request_id} Service destination={SERVICE_AGENT_ADDRESS[:30]}...")

        service_msg = ServiceRequestMessage(
            request_id=request_id,
            vehicle_id=request.vehicle_id,
            issue=diagnosis_reply.issue,
            affected_component=diagnosis_reply.affected_component,
            severity=diagnosis_reply.severity,
            safe_to_drive=diagnosis_reply.safe_to_drive,
            latitude=request.latitude,
            longitude=request.longitude,
        )

        start_svc = time.time()
        try:
            service_reply = await ctx.send_and_receive(
                destination=SERVICE_AGENT_ADDRESS,
                message=service_msg,
                response_type=ServiceResponseMessage,
                timeout=90,
            )
            elapsed_svc = time.time() - start_svc
            logger.info(f"[ORCH-SYNC] {request_id} AFTER SERVICE type={type(service_reply).__name__} elapsed={elapsed_svc:.2f}s")
        except Exception as exc:
            logger.exception(f"[ORCH-SYNC] {request_id} SERVICE FAILED: {type(exc).__name__}: {exc}")
            raise

        # Unpack tuple response if needed (sender, message)
        if isinstance(service_reply, tuple) and len(service_reply) == 2:
            service_reply = service_reply[1]

        if not isinstance(service_reply, ServiceResponseMessage):
            logger.warning(f"[ORCHESTRATOR SYNC] {request_id}: Service Agent response type {type(service_reply)}")
            service_centres = []
        else:
            logger.info(f"[ORCHESTRATOR SYNC] {request_id} ← SERVICE: {len(service_reply.centres)} centres")
            service_centres = service_reply.centres

        # Step 4: Check if safe to drive
        if diagnosis_reply.safe_to_drive:
            logger.info(f"[ORCH-SYNC] {request_id} BUILDING FINAL RESPONSE (SERVICE_RECOMMENDED)")
            logger.info(f"[ORCHESTRATOR SYNC] {request_id}: Safe to drive, returning SERVICE_RECOMMENDED")
            return AutoRescueResponseMessage(
                request_id=request_id,
                vehicle_id=request.vehicle_id,
                status="SERVICE_RECOMMENDED",
                diagnosis=DiagnosisSummary(
                    issue=diagnosis_reply.issue,
                    affected_component=diagnosis_reply.affected_component,
                    severity=diagnosis_reply.severity,
                    safe_to_drive=diagnosis_reply.safe_to_drive,
                    recommendation=diagnosis_reply.recommendation,
                ),
                service_centres=service_centres,
                navigation_allowed=True,
                rescue=None,
                message="Vehicle requires attention. Nearby service centres have been ranked for you.",
            )

        # Step 5: Rescue Agent (unsafe to drive)
        if not RESCUE_AGENT_ADDRESS:
            raise ValueError("RESCUE_AGENT_ADDRESS not configured")

        logger.info(f"[ORCH-SYNC] {request_id} BEFORE RESCUE")
        logger.info(f"[ORCH-SYNC] {request_id} Rescue destination={RESCUE_AGENT_ADDRESS[:30]}...")

        # Use top service centre as destination if available
        tow_destination = {}
        if service_centres:
            top_centre = service_centres[0]
            tow_destination = {
                "service_centre_name": top_centre.name,
                "service_centre_place_id": top_centre.place_id,
                "service_centre_latitude": top_centre.latitude,
                "service_centre_longitude": top_centre.longitude,
            }

        rescue_msg = RescueRequestMessage(
            request_id=request_id,
            vehicle_id=request.vehicle_id,
            issue=diagnosis_reply.issue,
            affected_component=diagnosis_reply.affected_component,
            severity=diagnosis_reply.severity,
            safe_to_drive=diagnosis_reply.safe_to_drive,
            latitude=request.latitude,
            longitude=request.longitude,
            **tow_destination,
        )

        start_rsc = time.time()
        try:
            rescue_reply = await ctx.send_and_receive(
                destination=RESCUE_AGENT_ADDRESS,
                message=rescue_msg,
                response_type=RescueResponseMessage,
                timeout=15,
            )
            elapsed_rsc = time.time() - start_rsc
            logger.info(f"[ORCH-SYNC] {request_id} AFTER RESCUE type={type(rescue_reply).__name__} elapsed={elapsed_rsc:.2f}s")
        except Exception as exc:
            logger.exception(f"[ORCH-SYNC] {request_id} RESCUE FAILED: {type(exc).__name__}: {exc}")
            raise

        # Unpack tuple response if needed (sender, message)
        if isinstance(rescue_reply, tuple) and len(rescue_reply) == 2:
            rescue_reply = rescue_reply[1]

        if not isinstance(rescue_reply, RescueResponseMessage):
            logger.error(f"[ORCHESTRATOR SYNC] {request_id}: Expected RescueResponseMessage, got {type(rescue_reply)}")
            raise ValueError(f"Invalid rescue response type: {type(rescue_reply)}")

        logger.info(f"[ORCHESTRATOR SYNC] {request_id} ← RESCUE: {rescue_reply.assistance_type}")

        logger.info(f"[ORCH-SYNC] {request_id} BUILDING FINAL RESPONSE (ASSISTANCE_REQUIRED)")
        # Step 6: Build and return final response
        return AutoRescueResponseMessage(
            request_id=request_id,
            vehicle_id=request.vehicle_id,
            status="ASSISTANCE_REQUIRED",
            diagnosis=DiagnosisSummary(
                issue=diagnosis_reply.issue,
                affected_component=diagnosis_reply.affected_component,
                severity=diagnosis_reply.severity,
                safe_to_drive=diagnosis_reply.safe_to_drive,
                recommendation=diagnosis_reply.recommendation,
            ),
            service_centres=service_centres,
            navigation_allowed=False,
            rescue=RescueSummary(
                assistance_required=rescue_reply.assistance_required,
                assistance_type=rescue_reply.assistance_type,
                priority=rescue_reply.priority,
                can_drive=rescue_reply.can_drive,
                tow_required=rescue_reply.tow_required,
                instructions=rescue_reply.instructions,
                reason=rescue_reply.reason,
                destination_name=rescue_reply.destination_name,
                destination_place_id=rescue_reply.destination_place_id,
                estimated_dispatch_minutes=rescue_reply.estimated_dispatch_minutes,
            ),
            message="Vehicle is not safe to drive. Roadside assistance is recommended.",
        )

    except Exception as e:
        logger.error(f"[ORCHESTRATOR SYNC] {request_id}: Orchestration failed: {str(e)}", exc_info=True)
        raise


@orchestrator_uagent.on_query(
    model=AutoRescueRequestMessage,
    replies={AutoRescueResponseMessage, AutoRescueErrorMessage},
)
async def handle_autorescue_query(
    ctx: Context,
    sender: str,
    msg: AutoRescueRequestMessage,
):
    """
    Query handler for synchronous request-response with external callers.

    This is the PRIMARY entry point for AutoRescue requests via send_sync_message().
    The @on_query decorator automatically handles the request-response protocol.

    Critical: The response MUST be sent via await ctx.send(sender, response)
    and must be one of the declared reply types.
    """
    try:
        logger.info(f"[ORCHESTRATOR QUERY] *** HANDLER CALLED ***")
        logger.info(f"[ORCHESTRATOR QUERY] {msg.request_id} received from {sender}")

        # Run complete orchestration and get response
        logger.info(f"[ORCHESTRATOR QUERY] {msg.request_id} calling orchestrate_sync...")
        response = await orchestrate_sync(ctx, msg)
        logger.info(f"[ORCHESTRATOR QUERY] {msg.request_id} orchestrate_sync returned successfully")

        # Verify response is correct type
        if not isinstance(response, AutoRescueResponseMessage):
            logger.error(
                f"[ORCHESTRATOR QUERY] {msg.request_id}: Response is {type(response).__name__}, not AutoRescueResponseMessage"
            )
            raise TypeError(f"orchestrate_sync returned {type(response).__name__}")

        logger.info(
            f"[ORCHESTRATOR QUERY] {msg.request_id} → QUERY CALLER {sender}: {response.status}"
        )

        # Log the exact response before sending
        logger.info(f"[ORCHESTRATOR] FINAL REPLY TYPE = {type(response).__name__}")
        payload = (
            response.model_dump()
            if hasattr(response, "model_dump")
            else response.dict()
            if hasattr(response, "dict")
            else response
        )
        logger.info(f"[ORCHESTRATOR] FINAL REPLY PAYLOAD keys = {list(payload.keys()) if isinstance(payload, dict) else 'not-a-dict'}")
        logger.info(f"[ORCHESTRATOR] FINAL REPLY PAYLOAD status = {payload.get('status') if isinstance(payload, dict) else 'N/A'}")

        # Send query response - @on_query automatically handles the protocol
        await ctx.send(sender, response)
        logger.info(f"[ORCHESTRATOR QUERY] {msg.request_id} query response sent successfully")

    except Exception as exc:
        logger.error(
            f"[ORCHESTRATOR QUERY] {msg.request_id} failed: {str(exc)}", exc_info=True
        )

        # Send error reply
        error = AutoRescueErrorMessage(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id if hasattr(msg, 'vehicle_id') else "unknown",
            stage="ORCHESTRATOR",
            error=str(exc),
        )

        logger.info(
            f"[ORCHESTRATOR QUERY] {msg.request_id} error reply sent: {str(exc)[:80]}"
        )

        logger.info(f"[ORCHESTRATOR] SENDING ERROR MODEL: {type(error).__name__}")
        logger.info(f"[ORCHESTRATOR] ERROR REASON: {str(exc)[:200]}")

        await ctx.send(sender, error)


@orchestrator_uagent.on_event("startup")
async def startup(ctx: Context):
    """Validate configuration and log startup."""
    logger.info("=" * 60)
    logger.info("Orchestrator Agent started")
    logger.info(f"Agent Name: {ctx.agent.name}")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)

    # Validate specialist addresses
    if not DIAGNOSTIC_AGENT_ADDRESS:
        logger.error("⚠ DIAGNOSTIC_AGENT_ADDRESS not configured")
    if not SERVICE_AGENT_ADDRESS:
        logger.error("⚠ SERVICE_AGENT_ADDRESS not configured")
    if not RESCUE_AGENT_ADDRESS:
        logger.error("⚠ RESCUE_AGENT_ADDRESS not configured")

    if DIAGNOSTIC_AGENT_ADDRESS and SERVICE_AGENT_ADDRESS and RESCUE_AGENT_ADDRESS:
        logger.info("✓ All specialist agents configured")
        logger.info(f"  Diagnostic: {DIAGNOSTIC_AGENT_ADDRESS[:30]}...")
        logger.info(f"  Service: {SERVICE_AGENT_ADDRESS[:30]}...")
        logger.info(f"  Rescue: {RESCUE_AGENT_ADDRESS[:30]}...")


if __name__ == "__main__":
    orchestrator_uagent.run()
