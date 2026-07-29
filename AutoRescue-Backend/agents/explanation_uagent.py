"""Explanation Agent - Generates user-friendly explanations using LLM."""

import logging
import os
import httpx
from uagents import Agent, Context, Model

logger = logging.getLogger(__name__)

class ExplanationRequest(Model):
    """Request for explanation."""
    request_id: str
    vehicle_id: str
    severity: str
    issue: str
    safe_to_drive: bool
    recommendation: str

class ExplanationResponse(Model):
    """Explanation response."""
    request_id: str
    vehicle_id: str
    summary: str
    driver_guidance: str

agent = Agent(name="explanation", port=8024, seed="explanation_seed_7890")

FALLBACK_EXPLANATIONS = {
    "HEALTHY": {
        "summary": "Your vehicle is operating normally.",
        "guidance": "No immediate action required. Continue normal driving.",
    },
    "WARNING": {
        "summary": "Your vehicle has a minor issue that should be addressed soon.",
        "guidance": "The vehicle is currently safe to drive, but schedule a service appointment soon.",
    },
    "CRITICAL": {
        "summary": "Your vehicle has a critical issue and is not safe to drive.",
        "guidance": "Stop the vehicle in a safe location immediately. Do not continue driving. Contact roadside assistance.",
    },
}

async def get_llm_explanation(issue: str, recommendation: str, safe_to_drive: bool) -> tuple[str, str]:
    """Get LLM explanation, fallback to deterministic if LLM fails."""
    try:
        # Try to call the Groq LLM service
        prompt = f"""Generate a brief, user-friendly explanation for a vehicle owner.
Issue: {issue}
Recommendation: {recommendation}
Safe to drive: {safe_to_drive}

Provide in JSON format:
{{"summary": "...", "guidance": "..."}}
"""

        async with httpx.AsyncClient(timeout=5) as client:
            # Attempt to call LLM backend (this would be your Groq endpoint)
            response = await client.post(
                "http://127.0.0.1:8000/api/explain",
                json={"prompt": prompt}
            )
            if response.status_code == 200:
                import json
                data = response.json()
                return data.get("summary", ""), data.get("guidance", "")
    except Exception as e:
        logger.warning(f"LLM explanation failed, using fallback: {e}")

    # Fallback to deterministic explanation
    return "", ""

@agent.on_message(model=ExplanationRequest)
async def handle_explanation(ctx: Context, sender: str, msg: ExplanationRequest):
    """Generate explanation with LLM fallback."""

    summary, guidance = await get_llm_explanation(msg.issue, msg.recommendation, msg.safe_to_drive)

    # Use fallback if LLM didn't provide response
    if not summary or not guidance:
        severity_key = msg.severity if msg.severity in FALLBACK_EXPLANATIONS else "WARNING"
        fallback = FALLBACK_EXPLANATIONS[severity_key]
        summary = fallback["summary"] if not summary else summary
        guidance = fallback["guidance"] if not guidance else guidance

        # Enhance with actual issue if possible
        if msg.issue:
            summary = f"{msg.issue}. {fallback['summary']}"

        if not msg.safe_to_drive and "stop" not in guidance.lower():
            guidance = "Do not continue driving. " + guidance

    response = ExplanationResponse(
        request_id=msg.request_id,
        vehicle_id=msg.vehicle_id,
        summary=summary,
        driver_guidance=guidance
    )

    await ctx.send(sender, response)

if __name__ == "__main__":
    agent.run()
