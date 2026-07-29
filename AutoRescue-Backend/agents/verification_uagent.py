"""Verification Agent - Final consistency checker for vehicle diagnosis."""

import logging
from uagents import Agent, Context, Model

logger = logging.getLogger(__name__)

class VerificationRequest(Model):
    """Request for verification."""
    request_id: str
    vehicle_id: str
    severity: str
    safe_to_drive: bool
    navigation_allowed: bool
    tow_required: bool

class VerificationResponse(Model):
    """Verification response."""
    request_id: str
    vehicle_id: str
    verified: bool
    issues: list[str]
    final_status: str

agent = Agent(name="verification", port=8025, seed="verification_seed_2468")

@agent.on_message(model=VerificationRequest)
async def handle_verification(ctx: Context, sender: str, msg: VerificationRequest):
    """Verify consistency of diagnosis and safety flags."""

    issues = []
    final_status = msg.severity

    # Safety-first consistency checks
    if msg.severity == "CRITICAL":
        if msg.safe_to_drive:
            issues.append("CRITICAL severity but safe_to_drive=true (should be false)")
            msg.safe_to_drive = False
            final_status = "CRITICAL_CORRECTED"

        if msg.navigation_allowed:
            issues.append("CRITICAL severity but navigation_allowed=true (should be false)")
            msg.navigation_allowed = False
            final_status = "CRITICAL_CORRECTED"

        if not msg.tow_required:
            issues.append("CRITICAL severity but tow_required=false (should be true)")
            msg.tow_required = True
            final_status = "CRITICAL_CORRECTED"

    elif msg.severity == "WARNING":
        # Warnings typically allow driving unless contradicted
        if not msg.safe_to_drive and msg.severity == "WARNING":
            issues.append("WARNING severity but safe_to_drive=false (inconsistent)")

    elif msg.severity == "NORMAL":
        if not msg.safe_to_drive:
            issues.append("NORMAL severity but safe_to_drive=false (inconsistent)")
            msg.severity = "WARNING"
            final_status = "HEALTHY_CORRECTED"

    response = VerificationResponse(
        request_id=msg.request_id,
        vehicle_id=msg.vehicle_id,
        verified=len(issues) == 0,
        issues=issues,
        final_status=final_status
    )

    await ctx.send(sender, response)

if __name__ == "__main__":
    agent.run()
