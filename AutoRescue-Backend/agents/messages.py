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

class TelemetryValidationRequest(Model):
    """Request to validate vehicle telemetry."""

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


class TelemetryValidationMessage(Model):
    """Telemetry validation result."""

    valid: bool
    issues: list[str] = []
    normalized_telemetry: dict = {}


class SafetyRequest(Model):
    """Request to determine vehicle safety."""

    request_id: str
    vehicle_id: str
    diagnosis: DiagnosisSummary


class SafetyMessage(Model):
    """Safety determination result."""

    safe_to_drive: bool
    navigation_allowed: bool
    tow_required: bool
    risk_level: str


class MaintenanceRequest(Model):
    """Request to generate maintenance recommendation."""

    request_id: str
    vehicle_id: str
    diagnosis: DiagnosisSummary
    safety: SafetyMessage


class MaintenanceMessage(Model):
    """Maintenance recommendation."""

    component: str
    action: str
    urgency: str
    reason: str = ""


class NotificationRequest(Model):
    """Request to generate diagnostic notifications."""

    request_id: str
    vehicle_id: str
    telemetry_validation: TelemetryValidationMessage | None = None
    diagnosis: DiagnosisSummary | None = None
    safety: SafetyMessage | None = None
    maintenance: MaintenanceMessage | None = None


class NotificationMessage(Model):
    """User notification alert."""

    type: str
    severity: str
    title: str
    message: str
    recommendation: str = ""
    timestamp: str = ""


class ExplanationRequest(Model):
    """Request to generate AI explanation of vehicle state."""

    request_id: str
    vehicle_id: str
    diagnosis: DiagnosisSummary | None = None
    safety: SafetyMessage | None = None
    maintenance: MaintenanceMessage | None = None


class ExplanationMessage(Model):
    """AI explanation of vehicle state."""

    summary: str
    driver_guidance: str


class VerificationRequest(Model):
    """Request to verify consistency of all diagnostic outputs."""

    request_id: str
    vehicle_id: str
    telemetry_validation: TelemetryValidationMessage | None = None
    diagnosis: DiagnosisSummary | None = None
    safety: SafetyMessage | None = None
    maintenance: MaintenanceMessage | None = None


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


# ===== PHASE 10: NEW 10 AGENT MESSAGES (Agents 11-20) =====

class VehicleProfileRequest(Model):
    """Request for vehicle profile information."""
    request_id: str
    vehicle_id: str


class VehicleProfileResponse(Model):
    """Vehicle profile with powertrain and specifications."""
    request_id: str
    vehicle_id: str
    manufacturer: str | None = None
    model: str | None = None
    year: int | None = None
    vehicle_type: str = "UNKNOWN"  # CAR, SUV, TRUCK, etc.
    powertrain: str = "UNKNOWN"  # ICE, EV, HYBRID, UNKNOWN
    fuel_type: str | None = None  # PETROL, DIESEL, etc.
    battery_type: str | None = None  # 12V, 48V, TRACTION_PACK, etc.
    tyre_specification: str | None = None
    odometer_km: float | None = None
    last_service_km: float | None = None
    service_interval_km: float | None = None
    profile_found: bool = False


class BatteryHealthRequest(Model):
    """Request battery health evaluation."""
    request_id: str
    vehicle_id: str
    battery_voltage: float
    powertrain: str  # Context from vehicle profile


class BatteryHealthResponse(Model):
    """Battery health assessment."""
    request_id: str
    vehicle_id: str
    status: str  # NORMAL, WEAK, CRITICAL, UNKNOWN
    battery_voltage: float
    action: str
    reason: str


class TyreHealthRequest(Model):
    """Request tyre pressure analysis."""
    request_id: str
    vehicle_id: str
    front_left_tyre_psi: float
    front_right_tyre_psi: float
    rear_left_tyre_psi: float
    rear_right_tyre_psi: float


class TyreHealthResponse(Model):
    """Tyre health assessment."""
    request_id: str
    vehicle_id: str
    status: str  # NORMAL, WARNING, CRITICAL
    affected_tyres: list[str] = []
    minimum_psi: float
    action: str
    reason: str


class EngineHealthRequest(Model):
    """Request engine health evaluation."""
    request_id: str
    vehicle_id: str
    engine_temperature: float
    coolant_level: float


class EngineHealthResponse(Model):
    """Engine health assessment."""
    request_id: str
    vehicle_id: str
    status: str  # NORMAL, WARNING, CRITICAL
    engine_temperature: float
    coolant_risk: str  # NONE, LOW, CRITICAL
    action: str
    reason: str


class BreakdownClassificationRequest(Model):
    """Request breakdown category classification."""
    request_id: str
    vehicle_id: str
    selected_rescue_category: str | None = None  # User's explicit choice if any
    diagnosis: str | None = None
    vehicle_profile: dict | None = None
    safety_context: dict | None = None


class BreakdownClassificationResponse(Model):
    """Classified breakdown category."""
    request_id: str
    vehicle_id: str
    category: str  # FLAT_TYRE, BATTERY_ISSUE, ENGINE_BREAKDOWN, ACCIDENT, FUEL_NEEDED, EV_CHARGING, OTHER
    subtype: str | None = None
    confidence: float = 1.0
    reason: str


class PassengerSafetyRequest(Model):
    """Request passenger safety assessment."""
    request_id: str
    vehicle_id: str
    accident_flag: bool = False
    passenger_injury: bool = False
    available_context: dict | None = None


class PassengerSafetyResponse(Model):
    """Passenger safety assessment."""
    request_id: str
    vehicle_id: str
    medical_priority: str  # NONE, MEDIUM, HIGH
    hospital_search_required: bool = False
    vehicle_service_priority: bool = True
    guidance: str


class NearbyAssistanceRequest(Model):
    """Request nearby assistance places."""
    request_id: str
    vehicle_id: str
    category: str  # EV_CHARGING, BATTERY_SERVICE, FUEL_STATION, HOSPITAL, VEHICLE_REPAIR
    latitude: float
    longitude: float
    max_results: int = 10


class NearbyAssistanceResponse(Model):
    """Nearby assistance places."""
    request_id: str
    vehicle_id: str
    category: str
    places: list[dict] = []  # Places data from nearby service
    count: int = 0
    fallback: bool = False  # True if using fallback data


class ServiceRankingRequest(Model):
    """Request service place ranking."""
    request_id: str
    vehicle_id: str
    places: list[dict]
    assistance_category: str
    vehicle_context: dict | None = None


class ServiceRankingResponse(Model):
    """Ranked service places."""
    request_id: str
    vehicle_id: str
    ranked_places: list[dict] = []
    ranking_reason: str


class IncidentMemoryRequest(Model):
    """Request incident memory operation."""
    request_id: str
    vehicle_id: str
    operation: str  # STORE_INCIDENT, GET_RECENT, GET_REPEATED
    incident_data: dict | None = None
    limit: int = 10


class IncidentMemoryResponse(Model):
    """Incident memory data."""
    request_id: str
    vehicle_id: str
    operation: str
    incidents: list[dict] = []
    repeated_faults: list[dict] = []
    success: bool = True


class AgentHealthRequest(Model):
    """Request agent health status."""
    request_id: str


class AgentHealthResponse(Model):
    """Agent health status."""
    request_id: str
    total_agents: int = 20
    online: int = 0
    agents: list[dict] = []  # [{"name": "...", "status": "ONLINE|OFFLINE|TIMEOUT"}]
    timestamp: str | None = None
