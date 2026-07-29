"""10-Agent orchestration flow for AutoRescue."""

import logging
from datetime import datetime
from threading import Lock

logger = logging.getLogger(__name__)

# Response cache for gateway to retrieve extended responses
_response_cache = {}
_cache_lock = Lock()


def cache_extended_response(request_id: str, response):
    """Cache the extended response for retrieval by gateway."""
    with _cache_lock:
        _response_cache[request_id] = response
        # Auto-expire after 5 minutes
        import threading
        def expire():
            import time
            time.sleep(300)
            with _cache_lock:
                _response_cache.pop(request_id, None)
        threading.Thread(daemon=True, target=expire).start()


def get_extended_response(request_id: str):
    """Retrieve and remove the cached extended response."""
    with _cache_lock:
        return _response_cache.pop(request_id, None)

# Import response types ahead of time
from agents.messages import (
    ServiceResponseMessage,
    RescueResponseMessage,
)
from agents.notification_uagent import NotificationResponse
from agents.explanation_uagent import ExplanationResponse


class Agent10Orchestrator:
    """Orchestrates the 10-agent workflow synchronously."""

    def __init__(self, ctx, agent_addresses):
        """Initialize with uAgent context and agent addresses."""
        self.ctx = ctx
        self.telemetry_addr = agent_addresses.get("telemetry")
        self.diagnostic_addr = agent_addresses.get("diagnostic")
        self.safety_addr = agent_addresses.get("safety")
        self.maintenance_addr = agent_addresses.get("maintenance")
        self.service_addr = agent_addresses.get("service")
        self.rescue_addr = agent_addresses.get("rescue")
        self.notification_addr = agent_addresses.get("notification")
        self.explanation_addr = agent_addresses.get("explanation")
        self.verification_addr = agent_addresses.get("verification")
        self.trace = []

    async def orchestrate(self, request):
        """Execute the complete 10-agent workflow."""
        from agents.messages import (
            TelemetryValidationMessage,
            SafetyMessage,
            MaintenanceMessage,
            NotificationMessage,
            ExplanationMessage,
            VerificationMessage,
            AgentTraceEntry,
            AutoRescueResponseMessageExtended,
            DiagnosisSummary,
            RescueSummary,
        )
        from agents.telemetry_uagent import TelemetryValidationRequest, TelemetryValidationResponse
        from agents.safety_uagent import SafetyRequest, SafetyResponse
        from agents.maintenance_uagent import MaintenanceRequest, MaintenanceResponse
        from agents.notification_uagent import NotificationRequest
        from agents.explanation_uagent import ExplanationRequest
        from agents.verification_uagent import VerificationRequest, VerificationResponse

        request_id = request.request_id
        trace = []
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
            # 1. TELEMETRY AGENT
            logger.info(f"[10-Agent] {request_id} → Telemetry Agent")
            try:
                telemetry_req = TelemetryValidationRequest(
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

                telemetry_resp = await self.ctx.send_and_receive(
                    destination=self.telemetry_addr,
                    message=telemetry_req,
                    response_type=TelemetryValidationResponse,
                    timeout=10,
                )

                if isinstance(telemetry_resp, tuple):
                    telemetry_resp = telemetry_resp[1]

                validation = TelemetryValidationMessage(
                    valid=telemetry_resp.valid,
                    issues=telemetry_resp.issues,
                    normalized_telemetry=telemetry_resp.normalized_telemetry or {},
                )
                trace.append(AgentTraceEntry(agent="Telemetry Agent", status="COMPLETED", summary="Telemetry validated"))
                logger.info(f"[10-Agent] {request_id} ✓ Telemetry: valid={validation.valid}")

                if not validation.valid:
                    logger.warning(f"[10-Agent] {request_id} Invalid telemetry: {validation.issues}")

            except Exception as e:
                logger.warning(f"[10-Agent] {request_id} Telemetry Agent failed (continuing anyway): {e}")
                trace.append(AgentTraceEntry(agent="Telemetry Agent", status="FALLBACK", summary="Validation skipped"))
                # Don't fail - continue with diagnosis using raw telemetry

            # 2. DIAGNOSTIC AGENT
            logger.info(f"[10-Agent] {request_id} → Diagnostic Agent")
            try:
                from tools.diagnostic_rules import diagnose_vehicle
                from models.telemetry import VehicleTelemetry

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
                severity_str = diagnostic_result.severity.value

                diagnosis = {
                    "issue": diagnostic_result.issue,
                    "affected_component": diagnostic_result.affected_component,
                    "severity": severity_str,
                    "safe_to_drive": diagnostic_result.safe_to_drive,
                    "recommendation": diagnostic_result.recommendation,
                }

                trace.append(AgentTraceEntry(
                    agent="Diagnostic Agent",
                    status="COMPLETED",
                    summary=f"{severity_str}: {diagnostic_result.issue[:50]}"
                ))
                logger.info(f"[10-Agent] {request_id} ✓ Diagnostic: {severity_str}")

            except Exception as e:
                logger.error(f"[10-Agent] {request_id} Diagnostic Agent failed: {e}")
                trace.append(AgentTraceEntry(agent="Diagnostic Agent", status="FAILED", summary=str(e)[:100]))
                return self._error_response(request_id, request.vehicle_id, "Diagnosis failed")

            # 3. SAFETY AGENT
            logger.info(f"[10-Agent] {request_id} → Safety Agent")
            try:
                safety_req = SafetyRequest(
                    request_id=request_id,
                    vehicle_id=request.vehicle_id,
                    severity=diagnosis["severity"],
                    issue=diagnosis["issue"],
                )

                safety_resp = await self.ctx.send_and_receive(
                    destination=self.safety_addr,
                    message=safety_req,
                    response_type=SafetyResponse,
                    timeout=10,
                )

                if isinstance(safety_resp, tuple):
                    safety_resp = safety_resp[1]

                safety = SafetyMessage(
                    safe_to_drive=safety_resp.safe_to_drive,
                    navigation_allowed=safety_resp.navigation_allowed,
                    tow_required=safety_resp.tow_required,
                    risk_level=safety_resp.risk_level,
                )

                trace.append(AgentTraceEntry(
                    agent="Safety Agent",
                    status="COMPLETED",
                    summary=f"safe={safety.safe_to_drive}, nav={safety.navigation_allowed}"
                ))
                logger.info(f"[10-Agent] {request_id} ✓ Safety: safe_to_drive={safety.safe_to_drive}")

            except Exception as e:
                logger.warning(f"[10-Agent] {request_id} Safety Agent failed (using defaults): {e}")
                trace.append(AgentTraceEntry(agent="Safety Agent", status="FALLBACK", summary="Using defaults"))
                # Fallback: use diagnosis to determine safety
                safety = SafetyMessage(
                    safe_to_drive=diagnosis["safe_to_drive"],
                    navigation_allowed=diagnosis["severity"] != "CRITICAL",
                    tow_required=diagnosis["severity"] == "CRITICAL",
                    risk_level="MEDIUM" if diagnosis["severity"] == "WARNING" else ("HIGH" if diagnosis["severity"] == "CRITICAL" else "LOW"),
                )

            # 4. MAINTENANCE AGENT
            logger.info(f"[10-Agent] {request_id} → Maintenance Agent")
            try:
                maint_req = MaintenanceRequest(
                    request_id=request_id,
                    vehicle_id=request.vehicle_id,
                    severity=diagnosis["severity"],
                    affected_component=diagnosis["affected_component"],
                    issue=diagnosis["issue"],
                )

                maint_resp = await self.ctx.send_and_receive(
                    destination=self.maintenance_addr,
                    message=maint_req,
                    response_type=MaintenanceResponse,
                    timeout=10,
                )

                if isinstance(maint_resp, tuple):
                    maint_resp = maint_resp[1]

                maintenance = MaintenanceMessage(
                    component=maint_resp.component,
                    action=maint_resp.action,
                    urgency=maint_resp.urgency,
                    reason=maint_resp.reason,
                )

                trace.append(AgentTraceEntry(
                    agent="Maintenance Agent",
                    status="COMPLETED",
                    summary=f"{maintenance.component}: {maintenance.urgency}"
                ))
                logger.info(f"[10-Agent] {request_id} ✓ Maintenance: {maintenance.urgency}")

            except Exception as e:
                logger.error(f"[10-Agent] {request_id} Maintenance Agent failed: {e}")
                trace.append(AgentTraceEntry(agent="Maintenance Agent", status="FAILED", summary=str(e)[:100]))
                maintenance = MaintenanceMessage(component="Unknown", action="Contact service", urgency="ROUTINE")

            # 5. SERVICE AGENT (conditional: WARNING or CRITICAL)
            if diagnosis["severity"] in ["WARNING", "CRITICAL"]:
                logger.info(f"[10-Agent] {request_id} → Service Agent")
                try:
                    from agents.messages import ServiceRequestMessage
                    service_req = ServiceRequestMessage(
                        request_id=request_id,
                        vehicle_id=request.vehicle_id,
                        issue=diagnosis["issue"],
                        affected_component=diagnosis["affected_component"],
                        severity=diagnosis["severity"],
                        safe_to_drive=safety.safe_to_drive,
                        latitude=request.latitude,
                        longitude=request.longitude,
                    )

                    service_resp = await self.ctx.send_and_receive(
                        destination=self.service_addr,
                        message=service_req,
                        response_type=ServiceResponseMessage,
                        timeout=30,
                    )

                    if isinstance(service_resp, tuple):
                        service_resp = service_resp[1]

                    service_response = service_resp
                    trace.append(AgentTraceEntry(
                        agent="Service Agent",
                        status="COMPLETED",
                        summary=f"{len(service_resp.centres)} service centres found"
                    ))
                    logger.info(f"[10-Agent] {request_id} ✓ Service: {len(service_resp.centres)} centres")

                except Exception as e:
                    logger.warning(f"[10-Agent] {request_id} Service Agent failed: {e}")
                    trace.append(AgentTraceEntry(agent="Service Agent", status="FAILED", summary=str(e)[:100]))
                    service_response = None
            else:
                trace.append(AgentTraceEntry(agent="Service Agent", status="SKIPPED", summary="Not needed for HEALTHY"))

            # 6. RESCUE AGENT (conditional: CRITICAL or tow_required)
            if diagnosis["severity"] == "CRITICAL" or safety.tow_required:
                logger.info(f"[10-Agent] {request_id} → Rescue Agent")
                try:
                    from agents.messages import RescueRequestMessage
                    rescue_req = RescueRequestMessage(
                        request_id=request_id,
                        vehicle_id=request.vehicle_id,
                        issue=diagnosis["issue"],
                        affected_component=diagnosis["affected_component"],
                        severity=diagnosis["severity"],
                        safe_to_drive=safety.safe_to_drive,
                        latitude=request.latitude,
                        longitude=request.longitude,
                    )

                    rescue_resp = await self.ctx.send_and_receive(
                        destination=self.rescue_addr,
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
                        summary=f"{rescue_resp.assistance_type if rescue_resp.assistance_required else 'Not needed'}"
                    ))
                    logger.info(f"[10-Agent] {request_id} ✓ Rescue: {rescue_resp.assistance_type}")

                except Exception as e:
                    logger.warning(f"[10-Agent] {request_id} Rescue Agent failed: {e}")
                    trace.append(AgentTraceEntry(agent="Rescue Agent", status="FAILED", summary=str(e)[:100]))
                    rescue_response = None
            else:
                trace.append(AgentTraceEntry(agent="Rescue Agent", status="SKIPPED", summary="Not needed"))

            # 7. NOTIFICATION AGENT
            logger.info(f"[10-Agent] {request_id} → Notification Agent")
            try:
                notif_req = NotificationRequest(
                    request_id=request_id,
                    vehicle_id=request.vehicle_id,
                    severity=diagnosis["severity"],
                    affected_component=diagnosis["affected_component"],
                    issue=diagnosis["issue"],
                    recommendation=diagnosis["recommendation"],
                )

                notif_resp = await self.ctx.send_and_receive(
                    destination=self.notification_addr,
                    message=notif_req,
                    response_type=NotificationResponse,
                    timeout=10,
                )

                if isinstance(notif_resp, tuple):
                    notif_resp = notif_resp[1]

                for notif in notif_resp.notifications:
                    notifications.append(NotificationMessage(
                        type=notif.type,
                        severity=notif.severity,
                        title=notif.title,
                        message=notif.message,
                        recommendation=notif.recommendation,
                        timestamp=notif.timestamp,
                    ))

                trace.append(AgentTraceEntry(
                    agent="Notification Agent",
                    status="COMPLETED",
                    summary=f"{len(notifications)} notification(s)"
                ))
                logger.info(f"[10-Agent] {request_id} ✓ Notifications: {len(notifications)}")

            except Exception as e:
                logger.warning(f"[10-Agent] {request_id} Notification Agent failed: {e}")
                trace.append(AgentTraceEntry(agent="Notification Agent", status="FALLBACK", summary="Skipped"))

            # 8. EXPLANATION AGENT
            logger.info(f"[10-Agent] {request_id} → Explanation Agent")
            try:
                expl_req = ExplanationRequest(
                    request_id=request_id,
                    vehicle_id=request.vehicle_id,
                    severity=diagnosis["severity"],
                    issue=diagnosis["issue"],
                    safe_to_drive=safety.safe_to_drive,
                    recommendation=diagnosis["recommendation"],
                )

                expl_resp = await self.ctx.send_and_receive(
                    destination=self.explanation_addr,
                    message=expl_req,
                    response_type=ExplanationResponse,
                    timeout=15,
                )

                if isinstance(expl_resp, tuple):
                    expl_resp = expl_resp[1]

                explanation = ExplanationMessage(
                    summary=expl_resp.summary,
                    driver_guidance=expl_resp.driver_guidance,
                )

                trace.append(AgentTraceEntry(
                    agent="Explanation Agent",
                    status="COMPLETED",
                    summary="Explanation generated"
                ))
                logger.info(f"[10-Agent] {request_id} ✓ Explanation completed")

            except Exception as e:
                logger.warning(f"[10-Agent] {request_id} Explanation Agent failed: {e}")
                trace.append(AgentTraceEntry(agent="Explanation Agent", status="FALLBACK", summary="Using defaults"))
                explanation = ExplanationMessage(
                    summary=diagnosis["issue"],
                    driver_guidance="Please contact service for assistance." if diagnosis["severity"] == "WARNING" else "Do not continue driving. Seek assistance immediately."
                )

            # 9. VERIFICATION AGENT
            logger.info(f"[10-Agent] {request_id} → Verification Agent")
            try:
                verif_req = VerificationRequest(
                    request_id=request_id,
                    vehicle_id=request.vehicle_id,
                    severity=diagnosis["severity"],
                    safe_to_drive=safety.safe_to_drive,
                    navigation_allowed=safety.navigation_allowed,
                    tow_required=safety.tow_required,
                )

                verif_resp = await self.ctx.send_and_receive(
                    destination=self.verification_addr,
                    message=verif_req,
                    response_type=VerificationResponse,
                    timeout=10,
                )

                if isinstance(verif_resp, tuple):
                    verif_resp = verif_resp[1]

                verification = VerificationMessage(
                    verified=verif_resp.verified,
                    issues=verif_resp.issues,
                    corrections=verif_resp.corrections,
                )

                # Apply safety corrections from Verification Agent
                if verif_resp.corrections:
                    logger.warning(f"[10-Agent] {request_id} Verification applied corrections: {verif_resp.corrections}")
                    # Re-verify to ensure corrections are applied
                    if "safe_to_drive" in str(verif_resp.corrections):
                        safety.safe_to_drive = False
                    if "navigation" in str(verif_resp.corrections):
                        safety.navigation_allowed = False
                    if "tow" in str(verif_resp.corrections):
                        safety.tow_required = True

                trace.append(AgentTraceEntry(
                    agent="Verification Agent",
                    status="COMPLETED",
                    summary="Verified" if verification.verified else f"Issues found: {len(verification.issues)}"
                ))
                logger.info(f"[10-Agent] {request_id} ✓ Verification: verified={verification.verified}")

            except Exception as e:
                logger.error(f"[10-Agent] {request_id} Verification Agent failed: {e}")
                trace.append(AgentTraceEntry(agent="Verification Agent", status="FAILED", summary=str(e)[:100]))
                verification = VerificationMessage(verified=False, issues=[str(e)])

            # Build final response
            logger.info(f"[10-Agent] {request_id} Building final response")

            from agents.messages import AutoRescueResponseMessageExtended, ServiceCentreMessage

            status = self._determine_status(diagnosis["severity"], safety.safe_to_drive, rescue_response is not None)

            service_centres = []
            if service_response and hasattr(service_response, 'centres'):
                service_centres = service_response.centres

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
                    destination_name=getattr(rescue_response, 'destination_name', None),
                    destination_place_id=getattr(rescue_response, 'destination_place_id', None),
                    estimated_dispatch_minutes=getattr(rescue_response, 'estimated_dispatch_minutes', None),
                )

            response = AutoRescueResponseMessageExtended(
                request_id=request_id,
                vehicle_id=request.vehicle_id,
                status=status,
                diagnosis=DiagnosisSummary(**diagnosis),
                service_centres=service_centres,
                navigation_allowed=safety.navigation_allowed if safety else True,
                rescue=rescue_summary,
                message=self._generate_message(status, diagnosis),
                telemetry_validation=validation,
                safety=safety,
                maintenance=maintenance,
                notifications=notifications,
                explanation=explanation,
                verification=verification,
                agent_trace=trace,
            )

            logger.info(f"[10-Agent] {request_id} ✓ Complete: {status}")

            # Cache extended response for gateway retrieval
            cache_extended_response(request_id, response)

            return response

        except Exception as e:
            logger.error(f"[10-Agent] {request_id} Orchestration failed: {e}", exc_info=True)
            return self._error_response(request_id, request.vehicle_id, str(e))

    def _determine_status(self, severity, safe_to_drive, has_rescue):
        """Determine final status from severity and safety."""
        if severity == "NORMAL":
            return "HEALTHY"
        elif severity == "WARNING":
            return "SERVICE_RECOMMENDED"
        elif severity == "CRITICAL":
            return "ASSISTANCE_REQUIRED"
        return "HEALTHY"

    def _generate_message(self, status, diagnosis):
        """Generate user-facing message."""
        if status == "HEALTHY":
            return "Vehicle systems are operating within normal ranges."
        elif status == "SERVICE_RECOMMENDED":
            return f"Vehicle requires attention: {diagnosis['issue']}"
        elif status == "ASSISTANCE_REQUIRED":
            return "Vehicle is not safe to drive. Roadside assistance is recommended."
        return "Vehicle check complete."

    def _error_response(self, request_id, vehicle_id, error):
        """Create error response."""
        from agents.messages import AutoRescueErrorMessage
        return AutoRescueErrorMessage(
            request_id=request_id,
            vehicle_id=vehicle_id,
            stage="ORCHESTRATION",
            error=error,
        )
