"""Explanation Agent - Generates user-friendly explanations using LLM."""

import os
import logging
import httpx
from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    ExplanationRequest,
    ExplanationMessage,
)

load_dotenv()
logger = logging.getLogger(__name__)

EXPLANATION_AGENT_SEED = os.getenv("EXPLANATION_AGENT_SEED", "autorescue-explanation-agent-seed")
EXPLANATION_AGENT_PORT = int(os.getenv("EXPLANATION_AGENT_PORT", "8024"))

agent = Agent(
    name="autorescue_explanation_agent",
    seed=EXPLANATION_AGENT_SEED,
    port=EXPLANATION_AGENT_PORT,
    endpoint=[f"http://127.0.0.1:{EXPLANATION_AGENT_PORT}/submit"],
)

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

async def get_llm_explanation(diagnosis, safe_to_drive: bool) -> tuple[str, str]:
    """Get LLM explanation with Groq, fallback to deterministic if LLM fails."""
    try:
        if not diagnosis:
            return "", ""

        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            logger.warning("GROQ_API_KEY not configured, using fallback")
            return "", ""

        prompt = f"""Generate a brief, user-friendly explanation for a vehicle owner.
Issue: {diagnosis.issue}
Component: {diagnosis.affected_component}
Severity: {diagnosis.severity}
Recommendation: {diagnosis.recommendation}
Safe to drive: {safe_to_drive}

Respond in JSON format: {{"summary": "...", "guidance": "..."}}
Keep it concise and user-friendly."""

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {groq_api_key}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                }
            )
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                import json
                explanation = json.loads(content)
                return explanation.get("summary", ""), explanation.get("guidance", "")
    except Exception as e:
        logger.warning(f"LLM explanation failed: {e}, using fallback")

    return "", ""

@agent.on_message(model=ExplanationRequest)
async def handle_explanation(ctx: Context, sender: str, msg: ExplanationRequest):
    """Generate explanation with LLM fallback."""

    summary, guidance = await get_llm_explanation(
        msg.diagnosis if hasattr(msg, 'diagnosis') else None,
        msg.safety.safe_to_drive if hasattr(msg, 'safety') and msg.safety else True
    )

    # Use fallback if LLM didn't provide response
    if not summary or not guidance:
        severity = "HEALTHY"
        if hasattr(msg, 'diagnosis') and msg.diagnosis:
            severity = msg.diagnosis.severity if msg.diagnosis.severity in FALLBACK_EXPLANATIONS else "WARNING"

        fallback = FALLBACK_EXPLANATIONS.get(severity, FALLBACK_EXPLANATIONS["WARNING"])
        summary = fallback["summary"] if not summary else summary
        guidance = fallback["guidance"] if not guidance else guidance

        if hasattr(msg, 'diagnosis') and msg.diagnosis and msg.diagnosis.issue:
            summary = f"{msg.diagnosis.issue}. {fallback['summary']}"

        if hasattr(msg, 'safety') and msg.safety and not msg.safety.safe_to_drive and "stop" not in guidance.lower():
            guidance = "Do not continue driving. " + guidance

    response = ExplanationMessage(
        summary=summary,
        driver_guidance=guidance
    )

    logger.info(f"[EXPLANATION] {msg.request_id} → Generated explanation")
    await ctx.send(sender, response)


@agent.on_event("startup")
async def startup(ctx: Context):
    """Log startup."""
    logger.info("=" * 60)
    logger.info("Explanation Agent started")
    logger.info(f"Agent Name: {ctx.agent.name}")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)


if __name__ == "__main__":
    agent.run()
