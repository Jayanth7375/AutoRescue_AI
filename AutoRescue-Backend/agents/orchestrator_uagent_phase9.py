"""Phase 10B Production Orchestrator - Full 20-Agent Real Coordination."""

import os
import logging
import asyncio
from datetime import datetime
from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    AutoRescueRequestMessage,
    AutoRescueResponseMessageExtended,
    AgentTraceEntry,
    DiagnosisSummary,
    RescueSummary,
    VehicleProfileRequest,
    VehicleProfileResponse,
    BatteryHealthRequest,
    BatteryHealthResponse,
    TyreHealthRequest,
    TyreHealthResponse,
    EngineHealthRequest,
    EngineHealthResponse,
    BreakdownClassificationRequest,
    BreakdownClassificationResponse,
    PassengerSafetyRequest,
    PassengerSafetyResponse,
    NearbyAssistanceRequest,
    NearbyAssistanceResponse,
    ServiceRankingRequest,
    ServiceRankingResponse,
    IncidentMemoryRequest,
    IncidentMemoryResponse,
)

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

# ===== ALL 20 AGENT ADDRESSES =====
# Original 10
DIAGNOSTIC_ADDR = os.getenv("DIAGNOSTIC_AGENT_ADDRESS")
SERVICE_ADDR = os.getenv("SERVICE_AGENT_ADDRESS")
RESCUE_ADDR = os.getenv("RESCUE_AGENT_ADDRESS")
TELEMETRY_ADDR = os.getenv("TELEMETRY_AGENT_ADDRESS")
SAFETY_ADDR = os.getenv("SAFETY_AGENT_ADDRESS")
MAINTENANCE_ADDR = os.getenv("MAINTENANCE_AGENT_ADDRESS")
NOTIFICATION_ADDR = os.getenv("NOTIFICATION_AGENT_ADDRESS")
EXPLANATION_ADDR = os.getenv("EXPLANATION_AGENT_ADDRESS")
VERIFICATION_ADDR = os.getenv("VERIFICATION_AGENT_ADDRESS")

# New 10 (Phase 10)
VEHICLE_PROFILE_ADDR = os.getenv("VEHICLE_PROFILE_AGENT_ADDRESS")
BATTERY_HEALTH_ADDR = os.getenv("BATTERY_HEALTH_AGENT_ADDRESS")
TYRE_HEALTH_ADDR = os.getenv("TYRE_HEALTH_AGENT_ADDRESS")
ENGINE_HEALTH_ADDR = os.getenv("ENGINE_HEALTH_AGENT_ADDRESS")
BREAKDOWN_CLASS_ADDR = os.getenv("BREAKDOWN_CLASSIFICATION_AGENT_ADDRESS")
PASSENGER_SAFETY_ADDR = os.getenv("PASSENGER_SAFETY_AGENT_ADDRESS")
NEARBY_ASSIST_ADDR = os.getenv("NEARBY_ASSISTANCE_AGENT_ADDRESS")
SERVICE_RANKING_ADDR = os.getenv("SERVICE_RANKING_AGENT_ADDRESS")
INCIDENT_MEMORY_ADDR = os.getenv("INCIDENT_MEMORY_AGENT_ADDRESS")


@agent.on_query(
    model=AutoRescueRequestMessage,
    replies={AutoRescueResponseMessageExtended},
)
async def handle_autorescue_query(ctx: Context, sender: str, msg: AutoRescueRequestMessage):
    """Handle incoming AutoRescue orchestration request from FastAPI."""
    logger.info(f"[ORCH-20] {msg.request_id} ← RECEIVED from FastAPI")

    try:
        orchestrator = Orchestrator20Agent(ctx)
        response = await orchestrator.orchestrate(msg)
        logger.info(f"[ORCH-20] {msg.request_id} → SENDING response: {response.status}")
        await ctx.send(sender, response)
    except Exception as e:
        logger.error(f"[ORCH-20] {msg.request_id} ✗ FAILED: {type(e).__name__}: {e}", exc_info=True)
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


class Orchestrator20Agent:
    """Full 20-agent orchestrator with conditional routing."""

    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.trace = []

    async def call_agent(self, agent_name: str, address: str, request, expected_type, timeout=10):
        """Helper to call an agent and handle response."""
        if not address:
            logger.warning(f"[{agent_name}] No address configured")
            return None

        try:
            logger.info(f"[{agent_name}] Sending request to {address[:40]}...")
            response = await self.ctx.send_and_receive(
                destination=address,
                message=request,
                response_type=expected_type,
                timeout=timeout,
            )

            if isinstance(response, tuple):
                response, status = response

            if response is None:
                logger.warning(f"[{agent_name}] Received None response")
                self.trace.append(AgentTraceEntry(
                    agent=agent_name,
                    status="FALLBACK",
                    summary="No response received"
                ))
                return None

            logger.info(f"[{agent_name}] Response OK")
            self.trace.append(AgentTraceEntry(
                agent=agent_name,
                status="COMPLETED",
                summary=f"Success"
            ))
            return response

        except asyncio.TimeoutError:
            logger.error(f"[{agent_name}] Timeout")
            self.trace.append(AgentTraceEntry(
                agent=agent_name,
                status="FAILED",
                summary="Agent timeout"
            ))
            return None
        except Exception as e:
            logger.error(f"[{agent_name}] Error: {str(e)}")
            self.trace.append(AgentTraceEntry(
                agent=agent_name,
                status="FAILED",
                summary=str(e)[:50]
            ))
            return None

    def skip_agent(self, agent_name: str, reason: str = "Not applicable"):
        """Mark agent as skipped."""
        self.trace.append(AgentTraceEntry(
            agent=agent_name,
            status="SKIPPED",
            summary=reason
        ))

    async def orchestrate(self, request: AutoRescueRequestMessage) -> AutoRescueResponseMessageExtended:
        """Execute 20-agent workflow with conditional routing."""
        request_id = request.request_id
        vehicle_id = request.vehicle_id

        logger.info(f"[ORCH-20] {request_id} Starting 20-agent orchestration for {vehicle_id}")

        # ===== PHASE 1: CONTEXT =====
        logger.info(f"[ORCH-20] {request_id} PHASE 1: Getting vehicle context")
        self.trace.append(AgentTraceEntry(agent="Orchestrator", status="COMPLETED", summary="Starting 20-agent workflow"))

        # Vehicle Profile
        vehicle_profile = None
        if VEHICLE_PROFILE_ADDR:
            vp_req = VehicleProfileRequest(request_id=request_id, vehicle_id=vehicle_id)
            vehicle_profile = await self.call_agent(
                "Vehicle Profile Agent",
                VEHICLE_PROFILE_ADDR,
                vp_req,
                VehicleProfileResponse,
                timeout=5
            )
        else:
            self.skip_agent("Vehicle Profile Agent", "Not configured")

        powertrain = vehicle_profile.powertrain if vehicle_profile else "UNKNOWN"

        # ===== PHASE 2: VALIDATION =====
        logger.info(f"[ORCH-20] {request_id} PHASE 2: Telemetry validation")

        # Call Telemetry Agent
        from agents.messages import VehicleTelemetryMessage, TelemetryValidationMessage
        telemetry_msg = VehicleTelemetryMessage(
            request_id=request_id,
            vehicle_id=vehicle_id,
            engine_temperature=request.engine_temperature,
            battery_voltage=request.battery_voltage,
            front_left_tyre_psi=request.front_left_tyre_psi,
            front_right_tyre_psi=request.front_right_tyre_psi,
            rear_left_tyre_psi=request.rear_left_tyre_psi,
            rear_right_tyre_psi=request.rear_right_tyre_psi,
            coolant_level=request.coolant_level,
        )

        telemetry_valid = True
        telemetry_resp = None
        if TELEMETRY_ADDR:
            telemetry_resp = await self.call_agent(
                "Telemetry Agent",
                TELEMETRY_ADDR,
                telemetry_msg,
                TelemetryValidationMessage,
                timeout=5
            )
            if telemetry_resp and not telemetry_resp.valid:
                telemetry_valid = False
        else:
            self.skip_agent("Telemetry Agent", "Not configured")

        # ===== PHASE 3: DIAGNOSIS =====
        logger.info(f"[ORCH-20] {request_id} PHASE 3: Vehicle diagnosis")

        diagnosis = None
        if DIAGNOSTIC_ADDR:
            from agents.messages import DiagnosticResponseMessage
            diagnosis = await self.call_agent(
                "Diagnostic Agent",
                DIAGNOSTIC_ADDR,
                telemetry_msg,
                DiagnosticResponseMessage
            )
        else:
            self.skip_agent("Diagnostic Agent", "Not configured")

        # ===== PHASE 4: SPECIALISTS (Conditional + Parallel) =====
        logger.info(f"[ORCH-20] {request_id} PHASE 4: Running specialist health agents")

        specialist_tasks = []

        # Battery Health (if battery data exists)
        if BATTERY_HEALTH_ADDR and request.battery_voltage:
            battery_req = BatteryHealthRequest(
                request_id=request_id,
                vehicle_id=vehicle_id,
                battery_voltage=request.battery_voltage,
                powertrain=powertrain
            )
            specialist_tasks.append(
                self.call_agent("Battery Health Agent", BATTERY_HEALTH_ADDR, battery_req, BatteryHealthResponse)
            )
        else:
            self.skip_agent("Battery Health Agent", "No battery data or not configured")

        # Tyre Health (if tyre data exists)
        if TYRE_HEALTH_ADDR and request.front_left_tyre_psi:
            tyre_req = TyreHealthRequest(
                request_id=request_id,
                vehicle_id=vehicle_id,
                front_left_tyre_psi=request.front_left_tyre_psi,
                front_right_tyre_psi=request.front_right_tyre_psi,
                rear_left_tyre_psi=request.rear_left_tyre_psi,
                rear_right_tyre_psi=request.rear_right_tyre_psi,
            )
            specialist_tasks.append(
                self.call_agent("Tyre Health Agent", TYRE_HEALTH_ADDR, tyre_req, TyreHealthResponse)
            )
        else:
            self.skip_agent("Tyre Health Agent", "No tyre data or not configured")

        # Engine Health (if engine data exists)
        if ENGINE_HEALTH_ADDR and request.engine_temperature:
            engine_req = EngineHealthRequest(
                request_id=request_id,
                vehicle_id=vehicle_id,
                engine_temperature=request.engine_temperature,
                coolant_level=request.coolant_level,
            )
            specialist_tasks.append(
                self.call_agent("Engine Health Agent", ENGINE_HEALTH_ADDR, engine_req, EngineHealthResponse)
            )
        else:
            self.skip_agent("Engine Health Agent", "No engine data or not configured")

        # Run specialists concurrently if any
        specialist_results = []
        if specialist_tasks:
            specialist_results = await asyncio.gather(*specialist_tasks, return_exceptions=True)

        # ===== PHASE 5: BREAKDOWN CLASSIFICATION =====
        logger.info(f"[ORCH-20] {request_id} PHASE 5: Breakdown classification")

        breakdown = None
        if BREAKDOWN_CLASS_ADDR:
            breakdown_req = BreakdownClassificationRequest(
                request_id=request_id,
                vehicle_id=vehicle_id,
                diagnosis=diagnosis.issue if diagnosis else None,
            )
            breakdown = await self.call_agent(
                "Breakdown Classification Agent",
                BREAKDOWN_CLASS_ADDR,
                breakdown_req,
                BreakdownClassificationResponse
            )
        else:
            self.skip_agent("Breakdown Classification Agent", "Not configured")

        # ===== PHASE 6: PASSENGER SAFETY (Accident handling) =====
        logger.info(f"[ORCH-20] {request_id} PHASE 6: Passenger safety check")

        passenger_safety = None
        if PASSENGER_SAFETY_ADDR and breakdown and "ACCIDENT" in breakdown.category:
            safety_req = PassengerSafetyRequest(
                request_id=request_id,
                vehicle_id=vehicle_id,
                accident_flag=True,
                passenger_injury=False,  # Default
            )
            passenger_safety = await self.call_agent(
                "Passenger Safety Agent",
                PASSENGER_SAFETY_ADDR,
                safety_req,
                PassengerSafetyResponse
            )
        else:
            self.skip_agent("Passenger Safety Agent", "No accident scenario")

        # ===== PHASE 7: SAFETY AGENT =====
        logger.info(f"[ORCH-20] {request_id} PHASE 7: Safety assessment")

        from agents.messages import SafetyRequest, SafetyMessage

        # Build DiagnosisSummary for Safety Agent
        if diagnosis:
            diagnosis_summary = DiagnosisSummary(
                issue=diagnosis.issue,
                affected_component=diagnosis.affected_component,
                severity=diagnosis.severity,
                safe_to_drive=diagnosis.safe_to_drive,
                recommendation=diagnosis.recommendation,
            )
        else:
            diagnosis_summary = DiagnosisSummary(
                issue="Unknown",
                affected_component="vehicle",
                severity="UNKNOWN",
                safe_to_drive=True,
                recommendation="Unable to determine vehicle status",
            )

        safety_req = SafetyRequest(
            request_id=request_id,
            vehicle_id=vehicle_id,
            diagnosis=diagnosis_summary,
        )

        safety_resp = None
        if SAFETY_ADDR:
            safety_resp = await self.call_agent(
                "Safety Agent",
                SAFETY_ADDR,
                safety_req,
                SafetyMessage
            )
        else:
            self.skip_agent("Safety Agent", "Not configured")

        # ===== PHASE 8: MAINTENANCE =====
        logger.info(f"[ORCH-20] {request_id} PHASE 8: Maintenance planning")

        maintenance = None
        if MAINTENANCE_ADDR and diagnosis and diagnosis_summary:
            from agents.messages import MaintenanceRequest, MaintenanceMessage
            maint_req = MaintenanceRequest(
                request_id=request_id,
                vehicle_id=vehicle_id,
                diagnosis=diagnosis_summary,
                safety=safety_resp if safety_resp else SafetyMessage(
                    request_id=request_id,
                    vehicle_id=vehicle_id,
                    safe_to_drive=True,
                    navigation_allowed=True,
                    tow_required=False,
                    risk_level="NORMAL",
                ),
            )
            maintenance = await self.call_agent(
                "Maintenance Agent",
                MAINTENANCE_ADDR,
                maint_req,
                MaintenanceMessage
            )
        else:
            self.skip_agent("Maintenance Agent", "Not applicable")

        # ===== PHASE 9: RESCUE (Conditional) =====
        logger.info(f"[ORCH-20] {request_id} PHASE 9: Rescue decision")

        rescue_needed = (
            (diagnosis and diagnosis.severity in ["CRITICAL", "WARNING"]) or
            (safety_resp and safety_resp.tow_required)
        )

        rescue_response = None
        if RESCUE_ADDR and rescue_needed:
            from agents.messages import RescueRequestMessage
            rescue_req = RescueRequestMessage(
                request_id=request_id,
                vehicle_id=vehicle_id,
                issue=diagnosis.issue if diagnosis else "Unknown",
                affected_component=diagnosis.affected_component if diagnosis else "vehicle",
                severity=diagnosis.severity if diagnosis else "UNKNOWN",
                safe_to_drive=diagnosis.safe_to_drive if diagnosis else False,
                latitude=request.latitude,
                longitude=request.longitude,
            )
            from agents.messages import RescueResponseMessage
            rescue_response = await self.call_agent(
                "Rescue Agent",
                RESCUE_ADDR,
                rescue_req,
                RescueResponseMessage
            )
        else:
            self.skip_agent("Rescue Agent", "No rescue needed")

        # ===== PHASE 10: NEARBY ASSISTANCE (If rescue) =====
        logger.info(f"[ORCH-20] {request_id} PHASE 10: Nearby assistance")

        nearby_results = []
        if NEARBY_ASSIST_ADDR and rescue_response and rescue_response.assistance_required:
            assist_category = "VEHICLE_REPAIR"  # Default
            if breakdown:
                assist_category = breakdown.category

            nearby_req = NearbyAssistanceRequest(
                request_id=request_id,
                vehicle_id=vehicle_id,
                category=assist_category,
                latitude=request.latitude,
                longitude=request.longitude,
                max_results=5,
            )
            nearby = await self.call_agent(
                "Nearby Assistance Agent",
                NEARBY_ASSIST_ADDR,
                nearby_req,
                NearbyAssistanceResponse
            )
            if nearby:
                nearby_results = nearby.places
        else:
            self.skip_agent("Nearby Assistance Agent", "No rescue assistance needed")

        # ===== PHASE 11: SERVICE RANKING (If nearby results) =====
        logger.info(f"[ORCH-20] {request_id} PHASE 11: Service ranking")

        ranked_places = nearby_results
        if SERVICE_RANKING_ADDR and nearby_results:
            ranking_req = ServiceRankingRequest(
                request_id=request_id,
                vehicle_id=vehicle_id,
                places=nearby_results,
                assistance_category=breakdown.category if breakdown else "VEHICLE_REPAIR",
            )
            ranked = await self.call_agent(
                "Service Ranking Agent",
                SERVICE_RANKING_ADDR,
                ranking_req,
                ServiceRankingResponse
            )
            if ranked:
                ranked_places = ranked.ranked_places
        else:
            self.skip_agent("Service Ranking Agent", "No places to rank")

        # ===== PHASE 12: NOTIFICATIONS =====
        logger.info(f"[ORCH-20] {request_id} PHASE 12: Notifications")

        if NOTIFICATION_ADDR and (diagnosis and diagnosis.severity in ["CRITICAL", "WARNING"]):
            from agents.messages import NotificationRequest, NotificationMessage
            notif_req = NotificationRequest(
                request_id=request_id,
                vehicle_id=vehicle_id,
                issue=diagnosis.issue if diagnosis else "Unknown",
                severity=diagnosis.severity if diagnosis else "UNKNOWN",
            )
            await self.call_agent(
                "Notification Agent",
                NOTIFICATION_ADDR,
                notif_req,
                NotificationMessage
            )
        else:
            self.skip_agent("Notification Agent", "No critical issues")

        # ===== PHASE 13: EXPLANATION =====
        logger.info(f"[ORCH-20] {request_id} PHASE 13: Explanation")

        explanation = None
        if EXPLANATION_ADDR:
            from agents.messages import ExplanationRequest, ExplanationMessage
            exp_req = ExplanationRequest(
                request_id=request_id,
                vehicle_id=vehicle_id,
                issue=diagnosis.issue if diagnosis else "Vehicle OK",
            )
            explanation = await self.call_agent(
                "Explanation Agent",
                EXPLANATION_ADDR,
                exp_req,
                ExplanationMessage
            )
        else:
            self.skip_agent("Explanation Agent", "Not configured")

        # ===== PHASE 14: INCIDENT MEMORY (Store meaningful incidents) =====
        logger.info(f"[ORCH-20] {request_id} PHASE 14: Incident memory")

        if INCIDENT_MEMORY_ADDR and diagnosis and diagnosis.severity in ["CRITICAL", "WARNING"]:
            incident_req = IncidentMemoryRequest(
                request_id=request_id,
                vehicle_id=vehicle_id,
                operation="STORE_INCIDENT",
                incident_data={
                    "issue": diagnosis.issue,
                    "severity": diagnosis.severity,
                    "affected_component": diagnosis.affected_component,
                    "safe_to_drive": diagnosis.safe_to_drive,
                }
            )
            await self.call_agent(
                "Incident Memory Agent",
                INCIDENT_MEMORY_ADDR,
                incident_req,
                IncidentMemoryResponse
            )
        else:
            self.skip_agent("Incident Memory Agent", "No significant incident")

        # ===== PHASE 15: VERIFICATION (Final) =====
        logger.info(f"[ORCH-20] {request_id} PHASE 15: Final verification")

        if VERIFICATION_ADDR:
            from agents.messages import VerificationRequest, VerificationMessage
            verif_req = VerificationRequest(
                request_id=request_id,
                vehicle_id=vehicle_id,
                telemetry_validation=telemetry_resp,
                diagnosis=diagnosis_summary,
                safety=safety_resp,
                maintenance=maintenance,
            )
            verification = await self.call_agent(
                "Verification Agent",
                VERIFICATION_ADDR,
                verif_req,
                VerificationMessage
            )
        else:
            self.skip_agent("Verification Agent", "Not configured")

        # Skip remaining agents not explicitly called
        self.skip_agent("Service Agent", "Integrated into Rescue workflow")
        self.skip_agent("Agent Health Monitor", "On-demand only")

        # ===== BUILD FINAL RESPONSE =====
        logger.info(f"[ORCH-20] {request_id} Building final response")

        status = "HEALTHY"
        if diagnosis:
            if diagnosis.severity == "CRITICAL":
                status = "ASSISTANCE_REQUIRED"
            elif diagnosis.severity == "WARNING":
                status = "SERVICE_RECOMMENDED"

        navigation_allowed = (
            (safety_resp.navigation_allowed if safety_resp else True) and
            (not rescue_response or not rescue_response.assistance_required)
        )

        rescue_summary = None
        if rescue_response and rescue_response.assistance_required:
            rescue_summary = RescueSummary(
                assistance_required=True,
                assistance_type=rescue_response.assistance_type,
                priority=rescue_response.priority,
                can_drive=rescue_response.can_drive,
                tow_required=rescue_response.tow_required,
                instructions=rescue_response.instructions,
                reason=rescue_response.reason,
            )
            navigation_allowed = False

        from models.autorescue_api import ServiceCentreApiResponse
        service_centres = [
            ServiceCentreApiResponse(
                place_id=p.get("place_id", ""),
                name=p.get("name", ""),
                address=p.get("address", ""),
                latitude=p.get("latitude", 0),
                longitude=p.get("longitude", 0),
                rating=p.get("rating"),
                review_count=p.get("review_count"),
                is_open=p.get("is_open"),
                distance_km=p.get("distance_km", 0),
                priority_score=p.get("priority_score", 0),
                recommendation_reason=p.get("recommendation_reason", ""),
            )
            for p in ranked_places
        ] if ranked_places else []

        final_response = AutoRescueResponseMessageExtended(
            request_id=request_id,
            vehicle_id=vehicle_id,
            status=status,
            diagnosis=DiagnosisSummary(
                issue=diagnosis.issue if diagnosis else "No issues detected",
                affected_component=diagnosis.affected_component if diagnosis else "vehicle",
                severity=diagnosis.severity if diagnosis else "NORMAL",
                safe_to_drive=diagnosis.safe_to_drive if diagnosis else True,
                recommendation=diagnosis.recommendation if diagnosis else "Continue normal driving",
            ),
            service_centres=service_centres,
            navigation_allowed=navigation_allowed,
            rescue=rescue_summary,
            message=rescue_response.instructions if rescue_response else "Vehicle operating normally",
            agent_trace=self.trace,
        )

        logger.info(f"[ORCH-20] {request_id} ✓ Complete: {status}")
        return final_response


@agent.on_event("startup")
async def startup(ctx: Context):
    """Log startup information."""
    logger.info("=" * 60)
    logger.info("Phase 10B: 20-Agent Orchestrator started")
    logger.info(f"Agent Name: {ctx.agent.name}")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info(f"Port: {ORCHESTRATOR_AGENT_PORT}")
    logger.info("=" * 60)


if __name__ == "__main__":
    agent.run()
