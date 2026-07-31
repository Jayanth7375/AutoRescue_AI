"""Diagnostic uAgent for vehicle safety assessment."""

import os
import logging
from typing import Optional

from uagents import Agent, Context
from dotenv import load_dotenv

from models.telemetry import VehicleTelemetry
from tools.diagnostic_rules import diagnose_vehicle
from agents.messages import (
    VehicleTelemetryMessage,
    DiagnosticResponseMessage,
    DiagnosticErrorMessage,
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration from environment
DIAGNOSTIC_AGENT_SEED = os.getenv("DIAGNOSTIC_AGENT_SEED", "autorescue-diagnostic-agent-development-seed")
DIAGNOSTIC_AGENT_PORT = int(os.getenv("DIAGNOSTIC_AGENT_PORT", "8001"))

# Create the Diagnostic uAgent with proper endpoints
diagnostic_uagent = Agent(
    name="autorescue_diagnostic_agent",
    seed=DIAGNOSTIC_AGENT_SEED,
    port=DIAGNOSTIC_AGENT_PORT,
    endpoint=[f"http://127.0.0.1:{DIAGNOSTIC_AGENT_PORT}/submit"],
)


@diagnostic_uagent.on_query(
    model=VehicleTelemetryMessage,
    replies={DiagnosticResponseMessage, DiagnosticErrorMessage},
)
async def handle_telemetry_query(ctx: Context, sender: str, msg: VehicleTelemetryMessage):
    """Process incoming telemetry data and send diagnostic response."""
    try:
        logger.info(f"Received telemetry request {msg.request_id} from {sender} for vehicle {msg.vehicle_id}")

        # Convert uAgent message to Pydantic model
        telemetry = VehicleTelemetry(
            vehicle_id=msg.vehicle_id,
            engine_temperature=msg.engine_temperature,
            battery_voltage=msg.battery_voltage,
            front_left_tyre_psi=msg.front_left_tyre_psi,
            front_right_tyre_psi=msg.front_right_tyre_psi,
            rear_left_tyre_psi=msg.rear_left_tyre_psi,
            rear_right_tyre_psi=msg.rear_right_tyre_psi,
            coolant_level=msg.coolant_level,
        )

        # Run diagnostic analysis using existing rule engine
        result = diagnose_vehicle(telemetry)

        if result is None:
            logger.error(f"Diagnostic analysis returned None for request {msg.request_id}")
            error_response = DiagnosticErrorMessage(
                request_id=msg.request_id,
                vehicle_id=msg.vehicle_id,
                error="Diagnostic analysis returned no result",
            )
            await ctx.send(sender, error_response)
            return

        # Convert result to response message
        try:
            response = DiagnosticResponseMessage(
                request_id=msg.request_id,
                vehicle_id=msg.vehicle_id,
                issue=result.issue,
                affected_component=result.affected_component,
                severity=result.severity.value if hasattr(result.severity, 'value') else str(result.severity),
                safe_to_drive=result.safe_to_drive,
                recommendation=result.recommendation,
            )

            logger.info(f"Sending response for request {msg.request_id}: {result.severity}")
            await ctx.send(sender, response)
        except Exception as e:
            logger.error(f"Error converting diagnostic result: {str(e)}")
            error_response = DiagnosticErrorMessage(
                request_id=msg.request_id,
                vehicle_id=msg.vehicle_id,
                error=f"Failed to convert diagnostic result: {str(e)}",
            )
            await ctx.send(sender, error_response)

    except Exception as e:
        logger.error(f"Error processing telemetry request {msg.request_id}: {str(e)}")
        error_response = DiagnosticErrorMessage(
            request_id=msg.request_id,
            vehicle_id=getattr(msg, "vehicle_id", None),
            error=f"Diagnostic analysis failed: {str(e)}",
        )
        await ctx.send(sender, error_response)


@diagnostic_uagent.on_event("startup")
async def startup(ctx: Context):
    """Log agent startup information."""
    logger.info("=" * 60)
    logger.info("Diagnostic Agent started")
    logger.info(f"Agent Name: {ctx.agent.name}")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)


if __name__ == "__main__":
    diagnostic_uagent.run()
