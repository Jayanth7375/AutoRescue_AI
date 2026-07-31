"""Chat service for AutoRescue AI chatbot."""

import logging
import os
from typing import Optional

from pydantic import BaseModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    vehicle_id: str
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    reply: str
    suggested_actions: list[str] = []


class VehicleContext(BaseModel):
    """Vehicle diagnostic context for chatbot."""
    status: str = "UNKNOWN"
    severity: str = "NORMAL"
    safe_to_drive: bool = True
    navigation_allowed: bool = True
    issue: str = ""
    affected_component: str = ""
    recommendation: str = ""
    tow_required: bool = False
    assistance_type: str = ""


def get_system_prompt(vehicle_context: VehicleContext) -> str:
    """Generate system prompt with vehicle context."""
    return f"""You are AutoRescue AI, an automotive assistance chatbot for the AutoRescue platform.

Current Vehicle Status:
- Status: {vehicle_context.status}
- Severity: {vehicle_context.severity}
- Issue: {vehicle_context.issue or 'None detected'}
- Affected Component: {vehicle_context.affected_component or 'N/A'}
- Safe to Drive: {vehicle_context.safe_to_drive}
- Navigation Allowed: {vehicle_context.navigation_allowed}
- Tow Required: {vehicle_context.tow_required}

SAFETY RULES (AUTHORITATIVE):
1. If safe_to_drive=False: Tell the user NOT to drive. Recommend stopping safely.
2. If navigation_allowed=False: Do NOT encourage driving, recommend viewing location only.
3. If tow_required=True: Recommend contacting tow service at 9843398325.

RESTRICTIONS:
- Never claim a tow vehicle has been dispatched unless actual dispatch exists.
- Never claim a technician has been assigned.
- Service centres may be DEMO data - do not represent as verified real businesses.
- Do not diagnose unrelated medical or legal issues.
- Keep responses concise and practical.

Answer user questions about their vehicle's current status, what the diagnostics mean, and what they should do.
Provide context-aware advice based on their vehicle's condition."""


async def chat_with_autorescue(request: ChatRequest) -> ChatResponse:
    """Process a chat message and return a response."""
    try:
        # Extract API key from environment
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            logger.error("[CHAT] GROQ_API_KEY not configured - cannot initialize chatbot")
            return ChatResponse(
                reply="AutoRescue Assistant is temporarily unavailable. Your vehicle diagnosis is still available on the Diagnose screen."
            )

        # Build vehicle context from request
        context_data = request.context or {}
        vehicle_context = VehicleContext(
            status=context_data.get("status", "UNKNOWN"),
            severity=context_data.get("diagnosis", {}).get("severity", "NORMAL"),
            safe_to_drive=context_data.get("diagnosis", {}).get("safe_to_drive", True),
            navigation_allowed=context_data.get("navigation_allowed", True),
            issue=context_data.get("diagnosis", {}).get("issue", ""),
            affected_component=context_data.get("diagnosis", {}).get("affected_component", ""),
            recommendation=context_data.get("diagnosis", {}).get("recommendation", ""),
            tow_required=context_data.get("rescue", {}).get("tow_required", False),
            assistance_type=context_data.get("rescue", {}).get("assistance_type", ""),
        )

        # Initialize Groq LLM
        model = os.getenv("CHATBOT_MODEL", "llama-3.1-8b-instant")
        temperature = float(os.getenv("CHATBOT_TEMPERATURE", "0.7"))
        max_tokens = int(os.getenv("CHATBOT_MAX_TOKENS", "500"))

        logger.info(f"[CHAT] Initializing ChatGroq with model={model}, temp={temperature}, tokens={max_tokens}")

        llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Build messages
        system_prompt = get_system_prompt(vehicle_context)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=request.message),
        ]

        # Get response
        response = llm.invoke(messages)
        reply = response.content

        logger.info(f"[CHAT] {request.vehicle_id}: User asked '{request.message[:50]}...' → replied")

        # Suggest actions based on context
        suggested_actions = []
        if vehicle_context.tow_required:
            suggested_actions.append("Call Tow Service")
        if not vehicle_context.safe_to_drive and len(vehicle_context.issue) > 0:
            suggested_actions.append("View Diagnosis Details")
        if len(vehicle_context.issue) > 0:
            suggested_actions.append("View nearest service centre")

        return ChatResponse(reply=reply, suggested_actions=suggested_actions)

    except Exception as e:
        logger.exception(f"[CHAT] Chatbot generation failed - Exception: {type(e).__name__}: {str(e)}")
        return ChatResponse(
            reply="AutoRescue Assistant is temporarily unavailable. Your vehicle diagnosis is still available on the Diagnose screen."
        )
