"""Maintenance Agent - Generates maintenance recommendations."""

import os
import logging
from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    MaintenanceRequest,
    MaintenanceMessage,
)

load_dotenv()
logger = logging.getLogger(__name__)

MAINTENANCE_AGENT_SEED = os.getenv("MAINTENANCE_AGENT_SEED", "autorescue-maintenance-agent-seed")
MAINTENANCE_AGENT_PORT = int(os.getenv("MAINTENANCE_AGENT_PORT", "8022"))

agent = Agent(
    name="autorescue_maintenance_agent",
    seed=MAINTENANCE_AGENT_SEED,
    port=MAINTENANCE_AGENT_PORT,
    endpoint=[f"http://127.0.0.1:{MAINTENANCE_AGENT_PORT}/submit"],
)

MAINTENANCE_RULES = {
    "tyre": {
        "NORMAL": {"action": "Monitor tyre pressure", "urgency": "ROUTINE"},
        "WARNING": {"action": "Inspect and inflate affected tyre", "urgency": "SOON"},
        "CRITICAL": {"action": "Stop vehicle - replace tyre immediately", "urgency": "IMMEDIATE"},
    },
    "battery": {
        "NORMAL": {"action": "Monitor battery health", "urgency": "ROUTINE"},
        "WARNING": {"action": "Check battery charging system", "urgency": "SOON"},
        "CRITICAL": {"action": "Stop and inspect battery/alternator", "urgency": "IMMEDIATE"},
    },
    "engine": {
        "NORMAL": {"action": "Monitor engine performance", "urgency": "ROUTINE"},
        "WARNING": {"action": "Inspect engine systems", "urgency": "SOON"},
        "CRITICAL": {"action": "Stop vehicle - engine inspection required", "urgency": "IMMEDIATE"},
    },
    "coolant": {
        "NORMAL": {"action": "Monitor coolant level", "urgency": "ROUTINE"},
        "WARNING": {"action": "Check coolant level and system", "urgency": "SOON"},
        "CRITICAL": {"action": "Stop vehicle - coolant system failure", "urgency": "IMMEDIATE"},
    },
}

@agent.on_query(
    model=MaintenanceRequest,
    replies={MaintenanceMessage},
)
async def handle_maintenance_query(ctx: Context, sender: str, msg: MaintenanceRequest):
    """Generate maintenance recommendation based on severity."""

    # Get component name
    component = msg.diagnosis.affected_component if msg.diagnosis else "UNKNOWN"
    component_key = component.lower()

    # Get severity (from diagnosis or direct)
    severity = msg.diagnosis.severity if msg.diagnosis else msg.severity

    # Lookup maintenance rule
    rules = MAINTENANCE_RULES.get(component_key, {})
    action_data = rules.get(severity, {"action": "Schedule service", "urgency": "SOON"})

    response = MaintenanceMessage(
        component=component,
        action=action_data["action"],
        urgency=action_data["urgency"],
        reason=msg.diagnosis.issue if msg.diagnosis else "Vehicle maintenance required"
    )

    logger.info(f"[MAINTENANCE] {msg.request_id} → {component} {response.urgency}")
    await ctx.send(sender, response)


@agent.on_event("startup")
async def startup(ctx: Context):
    """Log startup."""
    logger.info("=" * 60)
    logger.info("Maintenance Agent started")
    logger.info(f"Agent Name: {ctx.agent.name}")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)


if __name__ == "__main__":
    agent.run()
