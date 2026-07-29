"""uAgent message models for vehicle diagnostics."""

from uagents import Model


class VehicleTelemetryMessage(Model):
    """Request message containing vehicle telemetry data for diagnosis."""

    request_id: str
    vehicle_id: str
    engine_temperature: float
    battery_voltage: float
    front_left_tyre_psi: float
    front_right_tyre_psi: float
    rear_left_tyre_psi: float
    rear_right_tyre_psi: float
    coolant_level: float


class DiagnosticResponseMessage(Model):
    """Response message containing diagnostic analysis results."""

    request_id: str
    vehicle_id: str
    issue: str
    affected_component: str
    severity: str
    safe_to_drive: bool
    recommendation: str


class DiagnosticErrorMessage(Model):
    """Error response message for failed diagnostic requests."""

    request_id: str
    vehicle_id: str | None
    error: str


class ServiceRequestMessage(Model):
    """Request message for service centre discovery."""

    request_id: str
    vehicle_id: str
    issue: str
    affected_component: str
    severity: str
    safe_to_drive: bool
    latitude: float
    longitude: float


class ServiceCentreMessage(Model):
    """Information about a service centre candidate."""

    place_id: str
    name: str
    address: str
    latitude: float
    longitude: float
    rating: float | None
    review_count: int | None
    is_open: bool | None
    distance_km: float
    priority_score: float
    recommendation_reason: str


class ServiceResponseMessage(Model):
    """Response message with ranked service centres."""

    request_id: str
    vehicle_id: str
    issue: str
    severity: str
    navigation_allowed: bool
    tow_recommended: bool
    centres: list[ServiceCentreMessage]


class ServiceErrorMessage(Model):
    """Error response message for failed service requests."""

    request_id: str
    vehicle_id: str | None
    error: str


class RescueRequestMessage(Model):
    """Request message for roadside assistance determination."""

    request_id: str
    vehicle_id: str
    issue: str
    affected_component: str
    severity: str
    safe_to_drive: bool
    latitude: float
    longitude: float
    service_centre_name: str | None = None
    service_centre_place_id: str | None = None
    service_centre_latitude: float | None = None
    service_centre_longitude: float | None = None


class RescueResponseMessage(Model):
    """Response message with roadside assistance requirements."""

    request_id: str
    vehicle_id: str
    assistance_required: bool
    assistance_type: str
    priority: str
    can_drive: bool
    tow_required: bool
    instructions: str
    reason: str
    destination_name: str | None = None
    destination_place_id: str | None = None
    estimated_dispatch_minutes: int | None = None


class RescueErrorMessage(Model):
    """Error response message for failed rescue requests."""

    request_id: str
    vehicle_id: str | None
    error: str


class AutoRescueRequestMessage(Model):
    """Complete request to Orchestrator Agent with all vehicle telemetry."""

    request_id: str
    vehicle_id: str
    engine_temperature: float
    battery_voltage: float
    front_left_tyre_psi: float
    front_right_tyre_psi: float
    rear_left_tyre_psi: float
    rear_right_tyre_psi: float
    coolant_level: float
    latitude: float
    longitude: float


class DiagnosisSummary(Model):
    """Summary of diagnostic results."""

    issue: str
    affected_component: str
    severity: str
    safe_to_drive: bool
    recommendation: str


class RescueSummary(Model):
    """Summary of rescue recommendations."""

    assistance_required: bool
    assistance_type: str
    priority: str
    can_drive: bool
    tow_required: bool
    instructions: str
    reason: str
    destination_name: str | None = None
    destination_place_id: str | None = None
    estimated_dispatch_minutes: int | None = None


class AutoRescueResponseMessage(Model):
    """Unified response from Orchestrator containing all relevant information."""

    request_id: str
    vehicle_id: str
    status: str
    diagnosis: DiagnosisSummary
    service_centres: list[ServiceCentreMessage]
    navigation_allowed: bool
    rescue: RescueSummary | None = None
    message: str


class AutoRescueErrorMessage(Model):
    """Error response from Orchestrator."""

    request_id: str
    vehicle_id: str | None
    stage: str
    error: str


# Extended 10-Agent Response Models

class TelemetryValidationMessage(Model):
    """Telemetry validation result."""

    valid: bool
    issues: list[str] = []
    normalized_telemetry: dict = {}


class SafetyMessage(Model):
    """Safety determination result."""

    safe_to_drive: bool
    navigation_allowed: bool
    tow_required: bool
    risk_level: str


class MaintenanceMessage(Model):
    """Maintenance recommendation."""

    component: str
    action: str
    urgency: str
    reason: str = ""


class NotificationMessage(Model):
    """User notification alert."""

    type: str
    severity: str
    title: str
    message: str
    recommendation: str = ""
    timestamp: str = ""


class ExplanationMessage(Model):
    """AI explanation of vehicle state."""

    summary: str
    driver_guidance: str


class VerificationMessage(Model):
    """Verification/consistency check result."""

    verified: bool
    issues: list[str] = []
    corrections: list[str] = []


class AgentTraceEntry(Model):
    """Agent execution trace entry."""

    agent: str
    status: str  # COMPLETED, SKIPPED, FALLBACK, FAILED
    summary: str


class AutoRescueResponseMessageExtended(Model):
    """Extended unified response from Orchestrator with full 10-agent results."""

    request_id: str
    vehicle_id: str
    status: str
    diagnosis: DiagnosisSummary
    service_centres: list[ServiceCentreMessage]
    navigation_allowed: bool
    rescue: RescueSummary | None = None
    message: str

    # New optional 10-agent fields
    telemetry_validation: TelemetryValidationMessage | None = None
    safety: SafetyMessage | None = None
    maintenance: MaintenanceMessage | None = None
    notifications: list[NotificationMessage] = []
    explanation: ExplanationMessage | None = None
    verification: VerificationMessage | None = None
    agent_trace: list[AgentTraceEntry] = []
