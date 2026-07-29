"""Deterministic roadside rescue assistance decision engine."""

import logging

logger = logging.getLogger(__name__)


def determine_rescue_action(
    issue: str,
    affected_component: str,
    severity: str,
    safe_to_drive: bool,
    service_centre_name: str | None = None,
    service_centre_place_id: str | None = None,
) -> dict:
    """
    Determine what roadside assistance is required.

    Args:
        issue: Description of the vehicle issue
        affected_component: Affected component
        severity: Issue severity (NORMAL, WARNING, CRITICAL)
        safe_to_drive: Whether vehicle can be driven
        service_centre_name: Optional destination service centre name
        service_centre_place_id: Optional destination service centre ID

    Returns:
        Dictionary with assistance decision and instructions
    """
    assistance_required = False
    assistance_type = "NONE"
    priority = "LOW"
    can_drive = safe_to_drive
    tow_required = False
    instructions = ""
    reason = ""
    destination_name = None
    destination_place_id = None
    estimated_dispatch_minutes = None

    issue_lower = issue.lower() if issue else ""
    component_lower = affected_component.lower() if affected_component else ""

    logger.info(f"Determining rescue action for {affected_component} issue: {issue}")

    # Engine overheating
    if component_lower == "engine" and not safe_to_drive:
        assistance_required = True
        assistance_type = "TOW"
        priority = "CRITICAL"
        can_drive = False
        tow_required = True
        instructions = "Stop the vehicle safely, switch off the engine and do not continue driving."
        reason = "Engine overheating can cause severe engine damage if the vehicle continues operating."

    # Cooling system
    elif component_lower in ["coolant", "cooling_system"] and not safe_to_drive:
        assistance_required = True
        assistance_type = "COOLING_SYSTEM_ASSISTANCE"
        priority = "CRITICAL"
        can_drive = False
        tow_required = True
        instructions = "Stop the vehicle safely and allow the engine to cool. Do not open the cooling system while hot."
        reason = "Critical coolant loss can cause engine damage. Professional assistance is required."

    # Tyre problem
    elif ("tyre" in component_lower or "tire" in component_lower) and not safe_to_drive:
        assistance_required = True
        assistance_type = "TYRE_ASSISTANCE"
        priority = "HIGH"
        can_drive = False
        tow_required = False  # Roadside tyre assistance attempted first
        instructions = "Move to a safe location and await roadside tyre assistance."
        reason = "Critical tyre pressure or damage detected. Professional tyre inspection and repair needed."

    # Battery problem
    elif component_lower == "battery" and not safe_to_drive:
        assistance_required = True
        assistance_type = "BATTERY_JUMP_START"
        priority = "HIGH"
        can_drive = False
        tow_required = False
        instructions = "Avoid attempting to start the vehicle. Professional battery assistance will be provided."
        reason = "Battery condition may prevent the vehicle from starting reliably."

    # Accident/collision
    elif any(word in issue_lower for word in ["accident", "collision", "crash"]):
        assistance_required = True
        assistance_type = "ACCIDENT_EMERGENCY"
        priority = "CRITICAL"
        can_drive = False
        tow_required = True
        instructions = "Move to a safe location if possible and seek appropriate emergency assistance."
        reason = "Emergency roadside assistance required."

    # Fuel issue
    elif "fuel" in issue_lower or "out of fuel" in issue_lower:
        assistance_required = True
        assistance_type = "FUEL_ASSISTANCE"
        priority = "HIGH"
        can_drive = False
        tow_required = False
        instructions = "Remain in the vehicle and await fuel delivery assistance."
        reason = "Fuel shortage detected. Fuel delivery service will be dispatched."

    # Safe vehicle
    elif safe_to_drive and severity == "NORMAL":
        assistance_required = False
        assistance_type = "NONE"
        priority = "LOW"
        can_drive = True
        tow_required = False
        instructions = "Vehicle is safe to operate. Continue to nearest service centre if repairs are recommended."
        reason = "No urgent assistance required."

    # Default: warning level
    elif safe_to_drive and severity == "WARNING":
        assistance_required = False
        assistance_type = "NONE"
        priority = "MEDIUM"
        can_drive = True
        tow_required = False
        instructions = "Vehicle may be driven. Monitor condition closely and visit service centre soon."
        reason = "Issue detected but vehicle is currently safe to operate."

    # If towing is required, set destination
    if tow_required and service_centre_name:
        destination_name = service_centre_name
        destination_place_id = service_centre_place_id

    # Set estimated dispatch ETA (simulated for MVP)
    if assistance_required:
        if priority == "CRITICAL":
            estimated_dispatch_minutes = 10
        elif priority == "HIGH":
            estimated_dispatch_minutes = 15
        elif priority == "MEDIUM":
            estimated_dispatch_minutes = 25

    logger.info(
        f"Rescue decision: {assistance_type} ({priority}) - "
        f"assistance_required={assistance_required}, "
        f"can_drive={can_drive}, tow_required={tow_required}"
    )

    return {
        "assistance_required": assistance_required,
        "assistance_type": assistance_type,
        "priority": priority,
        "can_drive": can_drive,
        "tow_required": tow_required,
        "instructions": instructions,
        "reason": reason,
        "destination_name": destination_name,
        "destination_place_id": destination_place_id,
        "estimated_dispatch_minutes": estimated_dispatch_minutes,
    }
