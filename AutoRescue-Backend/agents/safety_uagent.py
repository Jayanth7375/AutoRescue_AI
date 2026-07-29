"""Safety Agent - Determines authoritative safety flags."""

import logging
from uagents import Agent, Context, Model

logger = logging.getLogger(__name__)

class SafetyRequest(Model):
    """Request to determine safety flags."""
    request_id: str
    vehicle_id: str
    severity: str
    issue: str

class SafetyResponse(Model):
    """Response with safety-critical flags."""
    request_id: str
    vehicle_id: str
    safe_to_drive: bool
    navigation_allowed: bool
    tow_required: bool
    risk_level: str

agent = Agent(name="safety", port=8021, seed="safety_seed_5678")

@agent.on_message(model=SafetyRequest)
async def handle_safety(ctx: Context, sender: str, msg: SafetyRequest):
    """Determine safety flags based on severity."""

    if msg.severity == "CRITICAL":
        response = SafetyResponse(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            safe_to_drive=False,
            navigation_allowed=False,
            tow_required=True,
            risk_level="HIGH"
        )
    elif msg.severity == "WARNING":
        response = SafetyResponse(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            safe_to_drive=True,
            navigation_allowed=True,
            tow_required=False,
            risk_level="MEDIUM"
        )
    else:  # NORMAL
        response = SafetyResponse(
            request_id=msg.request_id,
            vehicle_id=msg.vehicle_id,
            safe_to_drive=True,
            navigation_allowed=True,
            tow_required=False,
            risk_level="LOW"
        )

    await ctx.send(sender, response)

if __name__ == "__main__":
    agent.run()
