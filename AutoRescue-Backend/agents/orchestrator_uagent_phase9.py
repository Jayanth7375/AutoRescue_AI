"""Phase 9 Production Orchestrator - Real 10-Agent Coordination."""

import os
import logging
from datetime import datetime
from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    AutoRescueRequestMessage,
    TelemetryValidationRequest,
    TelemetryValidationMessage,
    SafetyRequest,
    SafetyMessage,
    MaintenanceRequest,
    MaintenanceMessage,
    NotificationRequest,
    NotificationMessage,
    ExplanationRequest,
    ExplanationMessage,
    VerificationRequest,
    VerificationMessage,
    AgentTraceEntry,
    AutoRescueResponseMessageExtended,
    DiagnosisSummary,
    RescueSummary,
    ServiceResponseMessage,
    RescueResponseMessage,
)
from tools.diagnostic_rules import diagnose_vehicle
from models.telemetry import VehicleTelemetry

load_dotenv()
logger = logging.getLogger(__name__)

ORCHESTRATOR_AGENT_SEED = os.getenv("ORCHESTRATOR_AGENT_SEED", "autorescue-orchestrator-seed-phase9")
ORCHESTRATOR_AGENT_PORT = int(os.getenv("ORCHESTRATOR_AGENT_PORT", "8018"))

agent = Agent(
    name="autorescue_orchestrator_phase9",
    seed=ORCHESTRATOR_AGENT_SEED,
    port=ORCHESTRATOR_AGENT_PORT,
    endpoint=[f"http://127.0.0.1:{ORCHESTRATOR_AGENT_PORT}/submit"],
)

# Agent addresses (MUST be configured via environment variables)
TELEMETRY_ADDR = os.getenv("TELEMETRY_AGENT_ADDRESS")
SAFETY_ADDR = os.getenv("SAFETY_AGENT_ADDRESS")
MAINTENANCE_ADDR = os.getenv("MAINTENANCE_AGENT_ADDRESS")
SERVICE_ADDR = os.getenv("SERVICE_AGENT_ADDRESS")
RESCUE_ADDR = os.getenv("RESCUE_AGENT_ADDRESS")
NOTIFICATION_ADDR = os.getenv("NOTIFICATION_AGENT_ADDRESS")
EXPLANATION_ADDR = os.getenv("EXPLANATION_AGENT_ADDRESS")
VERIFICATION_ADDR = os.getenv("VERIFICATION_AGENT_ADDRESS")


@agent.on_query(
    model=AutoRescueRequestMessage,
    replies={AutoRescueResponseMessageExtended},
)
async def handle_autorescue_query(ctx: Context, sender: str, msg: AutoRescueRequestMessage):
    """Handle incoming AutoRescue orchestration request from FastAPI (synchronous query pattern)."""
    logger.info(f"[ORCH] {msg.request_id} ← RECEIVED query from {sender[:30]}...")

    try:
        # Create orchestrator instance and execute workflow
        orchestrator = Orchestrator10Agent(ctx)
        response = await orchestrator.orchestrate(msg)

        logger.info(f"[ORCH] {msg.request_id} → SENDING response: {response.status}")
        await ctx.send(sender, response)
    except Exception as e:
        logger.error(f"[ORCH] {msg.request_id} ✗ FAILED: {type(e).__name__}: {e}", exc_info=True)
        error_response = AutoRescueResponseMessageExtended(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            status="ERROR",
            diagnosis=DiagnosisSummary(
                issue="Orchestration failed",
                affected_component="UNKNOWN",
                severity="UNKNOWN",
                safe_to_drive=False,
                recommendation="Please try again",
            ),
            service_centres=[],
            navigation_allowed=False,
            message=f"Orchestration error: {str(e)[:100]}",
            agent_trace=[
                AgentTraceEntry(
                    agent="Orchestrator",
                    status="FAILED",
                    summary=f"Error: {str(e)[:50]}"
                )
            ],
        )
        await ctx.send(sender, error_response)


class Orchestrator10Agent:
    """Orchestrates the 10-agent workflow with truthful traces."""

    def __init__(self, ctx: Context):
        """Initialize with uAgent context."""
        self.ctx = ctx

    async def orchestrate(self, request: AutoRescueRequestMessage) -> AutoRescueResponseMessageExtended:
        """Execute the complete 10-agent workflow sequentially."""
        request_id = request.request_id
        vehicle_id = request.vehicle_id
        trace = []

        # Initialize result containers
        validation = None
        diagnosis = None
        safety = None
        maintenance = None
        service_response = None
        rescue_response = None
        notifications = []
        explanation = None
        verification = None

        try:
            # 1. TELEMETRY VALIDATION
            logger.info(f"[ORCH] {request_id} → Stage 1: Telemetry Validation")
            try:
                telemetry_req = TelemetryValidationRequest(
                    request_id=request_id,
                    vehicle_id=vehicle_id,
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

                telemetry_resp = await self.ctx.send_and_receive(
                    destination=TELEMETRY_ADDR,
                    message=telemetry_req,
                    response_type=TelemetryValidationMessage,
                    timeout=10,
                )

                if isinstance(telemetry_resp, tuple):
                    telemetry_resp = telemetry_resp[1]

                validation = telemetry_resp
                trace.append(AgentTraceEntry(
                    agent="Telemetry Agent",
                    status="COMPLETED",
                    summary=f"Validated (valid={validation.valid})"
                ))
                logger.info(f"[ORCH] {request_id} ✓ Telemetry: valid={validation.valid}")

            except Exception as e:
                logger.warning(f"[ORCH] {request_id} Telemetry failed (fallback): {e}")
                trace.append(AgentTraceEntry(
                    agent="Telemetry Agent",
                    status="FALLBACK",
                    summary=f"Validation skipped: {str(e)[:50]}"
                ))

            # 2. DIAGNOSTIC AGENT
            logger.info(f"[ORCH] {request_id} → Stage 2: Diagnostic Analysis")
            try:
                telemetry = VehicleTelemetry(
                    vehicle_id=vehicle_id,
                    engine_temperature=request.engine_temperature,
                    battery_voltage=request.battery_voltage,
                    front_left_tyre_psi=request.front_left_tyre_psi,
                    front_right_tyre_psi=request.front_right_tyre_psi,
                    rear_left_tyre_psi=request.rear_left_tyre_psi,
                    rear_right_tyre_psi=request.rear_right_tyre_psi,
                    coolant_level=request.coolant_level,
                )

                diagnostic_result = diagnose_vehicle(telemetry)
                severity_str = diagnostic_result.severity.value

                diagnosis = DiagnosisSummary(
                    issue=diagnostic_result.issue,
                    affected_component=diagnostic_result.affected_component,
                    severity=severity_str,
                    safe_to_drive=diagnostic_result.safe_to_drive,
                    recommendation=diagnostic_result.recommendation,
                )

                trace.append(AgentTraceEntry(
                    agent="Diagnostic Agent",
                    status="COMPLETED",
                    summary=f"{severity_str}: {diagnostic_result.issue[:40]}"
                ))
                logger.info(f"[ORCH] {request_id} ✓ Diagnostic: {severity_str}")

            except Exception as e:
                logger.error(f"[ORCH] {request_id} Diagnostic failed: {e}")
                trace.append(AgentTraceEntry(
                    agent="Diagnostic Agent",
                    status="FAILED",
                    summary=f"Error: {str(e)[:50]}"
                ))
                return self._error_response(request_id, vehicle_id, trace, "Diagnostic failed")

            # 3. SAFETY DETERMINATION
            logger.info(f"[ORCH] {request_id} → Stage 3: Safety Determination")
            try:
                safety_req = SafetyRequest(
                    request_id=request_id,
                    vehicle_id=vehicle_id,
                    diagnosis=diagnosis,
                )

                safety_resp = await self.ctx.send_and_receive(
                    destination=SAFETY_ADDR,
                    message=safety_req,
                    response_type=SafetyMessage,
                    timeout=10,
                )

                if isinstance(safety_resp, tuple):
                    safety_resp = safety_resp[1]

                safety = safety_resp
                trace.append(AgentTraceEntry(
                    agent="Safety Agent",
                    status="COMPLETED",
                    summary=f"safe={safety.safe_to_drive}, risk={safety.risk_level}"
                ))
                logger.info(f"[ORCH] {request_id} ✓ Safety: safe_to_drive={safety.safe_to_drive}")

            except Exception as e:
                logger.warning(f"[ORCH] {request_id} Safety failed (fallback): {e}")
                trace.append(AgentTraceEntry(
                    agent="Safety Agent",
                    status="FALLBACK",
                    summary=f"Using diagnostic defaults"
                ))
                # Fallback: derive from diagnosis
                safety = SafetyMessage(
                    safe_to_drive=diagnosis.safe_to_drive,
                    navigation_allowed=diagnosis.severity != "CRITICAL",
                    tow_required=diagnosis.severity == "CRITICAL",
                    risk_level="HIGH" if diagnosis.severity == "CRITICAL" else (
                        "MEDIUM" if diagnosis.severity == "WARNING" else "LOW"
                    ),
                )

            # 4. MAINTENANCE RECOMMENDATION
            logger.info(f"[ORCH] {request_id} → Stage 4: Maintenance Recommendation")
            try:
                maint_req = MaintenanceRequest(
                    request_id=request_id,
                    vehicle_id=vehicle_id,
                    diagnosis=diagnosis,
                    safety=safety,
                )

                maint_resp = await self.ctx.send_and_receive(
                    destination=MAINTENANCE_ADDR,
                    message=maint_req,
                    response_type=MaintenanceMessage,
                    timeout=10,
                )

                if isinstance(maint_resp, tuple):
                    maint_resp = maint_resp[1]

                maintenance = maint_resp
                trace.append(AgentTraceEntry(
                    agent="Maintenance Agent",
                    status="COMPLETED",
                    summary=f"{maintenance.component}: {maintenance.urgency}"
                ))
                logger.info(f"[ORCH] {request_id} ✓ Maintenance: {maintenance.component} {maintenance.urgency}")

            except Exception as e:
                logger.warning(f"[ORCH] {request_id} Maintenance failed (fallback): {e}")
                trace.append(AgentTraceEntry(
                    agent="Maintenance Agent",
                    status="FALLBACK",
                    summary=f"Fallback recommendation"
                ))

            # 5. SERVICE CENTRE SEARCH (Conditional: if not NORMAL severity)
            logger.info(f"[ORCH] {request_id} → Stage 5: Service Centre Search")
            if diagnosis.severity != "NORMAL":
                try:
                    from agents.messages import ServiceRequestMessage
                    service_req = ServiceRequestMessage(
                        request_id=request_id,
                        vehicle_id=vehicle_id,
                        issue=diagnosis.issue,
                        affected_component=diagnosis.affected_component,
                        severity=diagnosis.severity,
                        safe_to_drive=safety.safe_to_drive,
                        latitude=request.latitude,
                        longitude=request.longitude,
                    )

                    service_resp = await self.ctx.send_and_receive(
                        destination=SERVICE_ADDR,
                        message=service_req,
                        response_type=ServiceResponseMessage,
                        timeout=15,
                    )

                    if isinstance(service_resp, tuple):
                        service_resp = service_resp[1]

                    service_response = service_resp
                    trace.append(AgentTraceEntry(
                        agent="Service Agent",
                        status="COMPLETED",
                        summary=f"Found {len(service_response.centres)} service centres"
                    ))
                    logger.info(f"[ORCH] {request_id} ✓ Service: {len(service_response.centres)} centres")

                except Exception as e:
                    logger.warning(f"[ORCH] {request_id} Service failed (fallback): {e}")
                    trace.append(AgentTraceEntry(
                        agent="Service Agent",
                        status="FALLBACK",
                        summary=f"Service search unavailable"
                    ))
            else:
                trace.append(AgentTraceEntry(
                    agent="Service Agent",
                    status="SKIPPED",
                    summary="NORMAL severity - no service needed"
                ))
                logger.info(f"[ORCH] {request_id} - Service: skipped (NORMAL)")

            # 6. RESCUE ASSESSMENT (Conditional: if CRITICAL or tow required)
            logger.info(f"[ORCH] {request_id} → Stage 6: Rescue Assessment")
            if diagnosis.severity == "CRITICAL" or safety.tow_required:
                try:
                    from agents.messages import RescueRequestMessage
                    rescue_req = RescueRequestMessage(
                        request_id=request_id,
                        vehicle_id=vehicle_id,
                        issue=diagnosis.issue,
                        affected_component=diagnosis.affected_component,
                        severity=diagnosis.severity,
                        safe_to_drive=safety.safe_to_drive,
                        latitude=request.latitude,
                        longitude=request.longitude,
                    )

                    # Add service centre info if available
                    if service_response and service_response.centres:
                        top_centre = service_response.centres[0]
                        rescue_req.service_centre_name = top_centre.name
                        rescue_req.service_centre_place_id = top_centre.place_id
                        rescue_req.service_centre_latitude = top_centre.latitude
                        rescue_req.service_centre_longitude = top_centre.longitude

                    rescue_resp = await self.ctx.send_and_receive(
                        destination=RESCUE_ADDR,
                        message=rescue_req,
                        response_type=RescueResponseMessage,
                        timeout=15,
                    )

                    if isinstance(rescue_resp, tuple):
                        rescue_resp = rescue_resp[1]

                    rescue_response = rescue_resp
                    trace.append(AgentTraceEntry(
                        agent="Rescue Agent",
                        status="COMPLETED",
                        summary=f"Assistance: {rescue_response.assistance_type}"
                    ))
                    logger.info(f"[ORCH] {request_id} ✓ Rescue: {rescue_response.assistance_type}")

                except Exception as e:
                    logger.warning(f"[ORCH] {request_id} Rescue failed (fallback): {e}")
                    trace.append(AgentTraceEntry(
                        agent="Rescue Agent",
                        status="FALLBACK",
                        summary=f"Rescue unavailable"
                    ))
            else:
                trace.append(AgentTraceEntry(
                    agent="Rescue Agent",
                    status="SKIPPED",
                    summary="Not CRITICAL - no rescue needed"
                ))
                logger.info(f"[ORCH] {request_id} - Rescue: skipped")

            # 7. NOTIFICATIONS
            logger.info(f"[ORCH] {request_id} → Stage 7: Notifications")
            try:
                notif_req = NotificationRequest(
                    request_id=request_id,
                    vehicle_id=vehicle_id,
                    diagnosis=diagnosis,
                    safety=safety,
                    maintenance=maintenance,
                )

                notif_resp = await self.ctx.send_and_receive(
                    destination=NOTIFICATION_ADDR,
                    message=notif_req,
                    response_type=NotificationMessage,
                    timeout=10,
                )

                if isinstance(notif_resp, tuple):
                    notif_resp = notif_resp[1]

                notifications = [notif_resp] if notif_resp else []
                trace.append(AgentTraceEntry(
                    agent="Notification Agent",
                    status="COMPLETED",
                    summary=f"Generated {len(notifications)} notification(s)"
                ))
                logger.info(f"[ORCH] {request_id} ✓ Notifications: {len(notifications)}")

            except Exception as e:
                logger.warning(f"[ORCH] {request_id} Notification failed (fallback): {e}")
                trace.append(AgentTraceEntry(
                    agent="Notification Agent",
                    status="FALLBACK",
                    summary=f"Notification skipped"
                ))

            # 8. EXPLANATION
            logger.info(f"[ORCH] {request_id} → Stage 8: AI Explanation")
            try:
                explain_req = ExplanationRequest(
                    request_id=request_id,
                    vehicle_id=vehicle_id,
                    diagnosis=diagnosis,
                    safety=safety,
                    maintenance=maintenance,
                )

                explain_resp = await self.ctx.send_and_receive(
                    destination=EXPLANATION_ADDR,
                    message=explain_req,
                    response_type=ExplanationMessage,
                    timeout=15,
                )

                if isinstance(explain_resp, tuple):
                    explain_resp = explain_resp[1]

                explanation = explain_resp
                trace.append(AgentTraceEntry(
                    agent="Explanation Agent",
                    status="COMPLETED",
                    summary=f"Generated explanation ({len(explanation.summary)} chars)"
                ))
                logger.info(f"[ORCH] {request_id} ✓ Explanation generated")

            except Exception as e:
                logger.warning(f"[ORCH] {request_id} Explanation failed (fallback): {e}")
                trace.append(AgentTraceEntry(
                    agent="Explanation Agent",
                    status="FALLBACK",
                    summary=f"Using deterministic explanation"
                ))

            # 9. VERIFICATION
            logger.info(f"[ORCH] {request_id} → Stage 9: Verification")
            try:
                verify_req = VerificationRequest(
                    request_id=request_id,
                    vehicle_id=vehicle_id,
                    diagnosis=diagnosis,
                    safety=safety,
                    maintenance=maintenance,
                )

                verify_resp = await self.ctx.send_and_receive(
                    destination=VERIFICATION_ADDR,
                    message=verify_req,
                    response_type=VerificationMessage,
                    timeout=10,
                )

                if isinstance(verify_resp, tuple):
                    verify_resp = verify_resp[1]

                verification = verify_resp
                trace.append(AgentTraceEntry(
                    agent="Verification Agent",
                    status="COMPLETED",
                    summary=f"verified={verification.verified}, issues={len(verification.issues)}"
                ))
                logger.info(f"[ORCH] {request_id} ✓ Verification: verified={verification.verified}")

            except Exception as e:
                logger.warning(f"[ORCH] {request_id} Verification failed (fallback): {e}")
                trace.append(AgentTraceEntry(
                    agent="Verification Agent",
                    status="FALLBACK",
                    summary=f"Verification skipped"
                ))

            # 10. BUILD FINAL RESPONSE
            logger.info(f"[ORCH] {request_id} → Stage 10: Building Final Response")

            # Determine final status
            final_status = "HEALTHY"
            if diagnosis.severity == "CRITICAL":
                final_status = "CRITICAL"
            elif diagnosis.severity == "WARNING":
                final_status = "WARNING"

            # Build rescue summary if we have a rescue response
            rescue_summary = None
            if rescue_response:
                rescue_summary = RescueSummary(
                    assistance_required=rescue_response.assistance_required,
                    assistance_type=rescue_response.assistance_type,
                    priority=rescue_response.priority,
                    can_drive=rescue_response.can_drive,
                    tow_required=rescue_response.tow_required,
                    instructions=rescue_response.instructions,
                    reason=rescue_response.reason,
                    destination_name=rescue_response.destination_name,
                    destination_place_id=rescue_response.destination_place_id,
                    estimated_dispatch_minutes=rescue_response.estimated_dispatch_minutes,
                )

            # Build service centres list
            service_centres = []
            if service_response:
                service_centres = service_response.centres

            # Build final message
            final_message = f"{diagnosis.issue}. {diagnosis.recommendation}"

            response = AutoRescueResponseMessageExtended(
                request_id=request_id,
                vehicle_id=vehicle_id,
                status=final_status,
                diagnosis=diagnosis,
                service_centres=service_centres,
                navigation_allowed=safety.navigation_allowed,
                rescue=rescue_summary,
                message=final_message,
                telemetry_validation=validation,
                safety=safety,
                maintenance=maintenance,
                notifications=notifications,
                explanation=explanation,
                verification=verification,
                agent_trace=trace,
            )

            trace.append(AgentTraceEntry(
                agent="Orchestrator",
                status="COMPLETED",
                summary=f"Complete workflow: {final_status}"
            ))

            logger.info(f"[ORCH] {request_id} ✓✓✓ Orchestration complete: {final_status}")
            return response

        except Exception as e:
            logger.error(f"[ORCH] {request_id} Orchestration failed: {e}")
            return self._error_response(request_id, vehicle_id, trace, f"Orchestration failed: {str(e)}")

    def _error_response(self, request_id: str, vehicle_id: str | None, trace: list, error_msg: str):
        """Generate error response."""
        trace.append(AgentTraceEntry(
            agent="Orchestrator",
            status="FAILED",
            summary=error_msg[:50]
        ))

        # Return minimal response structure
        return AutoRescueResponseMessageExtended(
            request_id=request_id,
            vehicle_id=vehicle_id or "UNKNOWN",
            status="ERROR",
            diagnosis=DiagnosisSummary(
                issue="Diagnostic failed",
                affected_component="UNKNOWN",
                severity="UNKNOWN",
                safe_to_drive=False,
                recommendation="Please try again",
            ),
            service_centres=[],
            navigation_allowed=False,
            message=error_msg,
            agent_trace=trace,
        )


@agent.on_event("startup")
async def startup(ctx: Context):
    """Log startup and validate configuration."""
    logger.info("=" * 60)
    logger.info("Orchestrator Phase 9 Agent started")
    logger.info(f"Agent Name: {ctx.agent.name}")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)

    # Validate all required agent addresses are configured
    required_addrs = {
        "TELEMETRY": TELEMETRY_ADDR,
        "SAFETY": SAFETY_ADDR,
        "MAINTENANCE": MAINTENANCE_ADDR,
        "SERVICE": SERVICE_ADDR,
        "RESCUE": RESCUE_ADDR,
        "NOTIFICATION": NOTIFICATION_ADDR,
        "EXPLANATION": EXPLANATION_ADDR,
        "VERIFICATION": VERIFICATION_ADDR,
    }

    missing = [name for name, addr in required_addrs.items() if not addr]
    if missing:
        logger.error(f"⚠ Missing agent addresses: {', '.join(missing)}")
        logger.error("Configure via environment variables (see .env file)")
    else:
        logger.info("✓ All 8 agent addresses configured:")
        for name, addr in required_addrs.items():
            logger.info(f"  {name:15} {addr[:40]}...")
    logger.info("=" * 60)


if __name__ == "__main__":
    agent.run()
