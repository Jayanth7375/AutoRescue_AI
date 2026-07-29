"""Pydantic models for AutoRescue API (HTTP gateway)."""

from pydantic import BaseModel, Field


class AutoRescueApiRequest(BaseModel):
    """HTTP request model for AutoRescue diagnostic check."""

    vehicle_id: str = Field(..., description="Unique vehicle identifier")
    engine_temperature: float = Field(..., ge=-50, le=150, description="Engine temperature in Celsius")
    battery_voltage: float = Field(..., gt=0, le=20, description="Battery voltage in volts")
    front_left_tyre_psi: float = Field(..., ge=0, le=60, description="Front left tyre pressure in PSI")
    front_right_tyre_psi: float = Field(..., ge=0, le=60, description="Front right tyre pressure in PSI")
    rear_left_tyre_psi: float = Field(..., ge=0, le=60, description="Rear left tyre pressure in PSI")
    rear_right_tyre_psi: float = Field(..., ge=0, le=60, description="Rear right tyre pressure in PSI")
    coolant_level: float = Field(..., ge=0, le=100, description="Coolant level as percentage")
    latitude: float = Field(..., ge=-90, le=90, description="GPS latitude")
    longitude: float = Field(..., ge=-180, le=180, description="GPS longitude")


class DiagnosisApiResponse(BaseModel):
    """Diagnosis information in API response."""

    issue: str
    affected_component: str
    severity: str
    safe_to_drive: bool
    recommendation: str


class ServiceCentreApiResponse(BaseModel):
    """Service centre information in API response."""

    place_id: str
    name: str
    address: str
    latitude: float
    longitude: float
    rating: float | None = None
    review_count: int | None = None
    is_open: bool | None = None
    distance_km: float
    priority_score: float
    recommendation_reason: str


class RescueApiResponse(BaseModel):
    """Rescue recommendation in API response."""

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


class AutoRescueApiResponse(BaseModel):
    """Unified HTTP response from AutoRescue gateway."""

    request_id: str
    vehicle_id: str
    status: str
    diagnosis: DiagnosisApiResponse
    service_centres: list[ServiceCentreApiResponse]
    navigation_allowed: bool
    rescue: RescueApiResponse | None = None
    message: str


class AutoRescueErrorResponse(BaseModel):
    """Error response from AutoRescue gateway."""

    detail: str
    request_id: str | None = None
    stage: str | None = None
