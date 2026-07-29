"""Maintenance Agent - Generates maintenance recommendations."""

import logging
from uagents import Agent, Context, Model

logger = logging.getLogger(__name__)

class MaintenanceRequest(Model):
    """Request for maintenance recommendations."""
    request_id: str
    vehicle_id: str
    severity: str
    affected_component: str
    issue: str

class MaintenanceResponse(Model):
    """Maintenance recommendation response."""
    request_id: str
    vehicle_id: str
    component: str
    action: str
    urgency: str
    reason: str

agent = Agent(name="maintenance", port=8022, seed="maintenance_seed_9012")

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

@agent.on_message(model=MaintenanceRequest)
async def handle_maintenance(ctx: Context, sender: str, msg: MaintenanceRequest):
    """Generate maintenance recommendation based on severity."""

    component_key = msg.affected_component.lower()
    rules = MAINTENANCE_RULES.get(component_key, {})
    action_data = rules.get(msg.severity, {"action": "Schedule service", "urgency": "SOON"})

    response = MaintenanceResponse(
        request_id=msg.request_id,
        vehicle_id=msg.vehicle_id,
        component=msg.affected_component,
        action=action_data["action"],
        urgency=action_data["urgency"],
        reason=msg.issue
    )

    await ctx.send(sender, response)

if __name__ == "__main__":
    agent.run()
