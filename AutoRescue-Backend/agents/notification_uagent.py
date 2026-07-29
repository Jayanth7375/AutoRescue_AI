"""Notification Agent - Generates alerts from current vehicle state."""

import logging
from datetime import datetime
from uagents import Agent, Context, Model

logger = logging.getLogger(__name__)

class NotificationRequest(Model):
    """Request to generate notifications."""
    request_id: str
    vehicle_id: str
    severity: str
    affected_component: str
    issue: str
    recommendation: str

class Notification(Model):
    """Single notification alert."""
    type: str
    severity: str
    title: str
    message: str
    recommendation: str
    timestamp: str

class NotificationResponse(Model):
    """Response with generated notifications."""
    request_id: str
    vehicle_id: str
    notifications: list[Notification]

agent = Agent(name="notification", port=8023, seed="notification_seed_3456")

COMPONENT_TYPES = {
    "tyre": "TYRE",
    "battery": "BATTERY",
    "engine": "ENGINE",
    "coolant": "COOLANT",
}

@agent.on_message(model=NotificationRequest)
async def handle_notification(ctx: Context, sender: str, msg: NotificationRequest):
    """Generate notifications from vehicle state."""

    notifications = []

    component_type = COMPONENT_TYPES.get(msg.affected_component.lower(), "VEHICLE")
    timestamp = datetime.utcnow().isoformat() + "Z"

    # Generate title based on component and severity
    if msg.severity == "CRITICAL":
        title = f"Critical {msg.affected_component} Issue"
    elif msg.severity == "WARNING":
        title = f"{msg.affected_component} Warning"
    else:
        title = f"{msg.affected_component} Status"

    notification = Notification(
        type=component_type,
        severity=msg.severity,
        title=title,
        message=msg.issue,
        recommendation=msg.recommendation,
        timestamp=timestamp
    )

    notifications.append(notification)

    response = NotificationResponse(
        request_id=msg.request_id,
        vehicle_id=msg.vehicle_id,
        notifications=notifications
    )

    await ctx.send(sender, response)

if __name__ == "__main__":
    agent.run()
