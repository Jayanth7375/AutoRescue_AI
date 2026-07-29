"""Notification Agent - Generates alerts from current vehicle state."""

import os
import logging
from datetime import datetime
from uagents import Agent, Context
from dotenv import load_dotenv

from agents.messages import (
    NotificationRequest,
    NotificationMessage,
)

load_dotenv()
logger = logging.getLogger(__name__)

NOTIFICATION_AGENT_SEED = os.getenv("NOTIFICATION_AGENT_SEED", "autorescue-notification-agent-seed")
NOTIFICATION_AGENT_PORT = int(os.getenv("NOTIFICATION_AGENT_PORT", "8023"))

agent = Agent(
    name="autorescue_notification_agent",
    seed=NOTIFICATION_AGENT_SEED,
    port=NOTIFICATION_AGENT_PORT,
    endpoint=[f"http://127.0.0.1:{NOTIFICATION_AGENT_PORT}/submit"],
)

COMPONENT_TYPES = {
    "tyre": "TYRE",
    "battery": "BATTERY",
    "engine": "ENGINE",
    "coolant": "COOLANT",
}

@agent.on_query(
    model=NotificationRequest,
    replies={NotificationMessage},
)
async def handle_notification_query(ctx: Context, sender: str, msg: NotificationRequest):
    """Generate current diagnostic notifications."""

    timestamp = datetime.utcnow().isoformat() + "Z"

    # Generate notification from diagnosis if available
    if msg.diagnosis:
        component_type = COMPONENT_TYPES.get(msg.diagnosis.affected_component.lower(), "VEHICLE")

        if msg.diagnosis.severity == "CRITICAL":
            title = f"Critical {msg.diagnosis.affected_component} Issue"
        elif msg.diagnosis.severity == "WARNING":
            title = f"{msg.diagnosis.affected_component} Warning"
        else:
            title = f"{msg.diagnosis.affected_component} Status"

        notification = NotificationMessage(
            type=component_type,
            severity=msg.diagnosis.severity,
            title=title,
            message=msg.diagnosis.issue,
            recommendation=msg.diagnosis.recommendation,
            timestamp=timestamp
        )

        logger.info(f"[NOTIFICATION] {msg.request_id} → Generated: {notification.title}")
        await ctx.send(sender, notification)
    else:
        # No diagnosis available, send neutral notification
        notification = NotificationMessage(
            type="VEHICLE",
            severity="NORMAL",
            title="Vehicle Status Normal",
            message="No issues detected.",
            recommendation="Continue normal operation.",
            timestamp=timestamp
        )
        logger.info(f"[NOTIFICATION] {msg.request_id} → Vehicle normal")
        await ctx.send(sender, notification)


@agent.on_event("startup")
async def startup(ctx: Context):
    """Log startup."""
    logger.info("=" * 60)
    logger.info("Notification Agent started")
    logger.info(f"Agent Name: {ctx.agent.name}")
    logger.info(f"Agent Address: {ctx.agent.address}")
    logger.info("=" * 60)


if __name__ == "__main__":
    agent.run()
