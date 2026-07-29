from pydantic import BaseModel, Field


class VehicleTelemetry(BaseModel):
    """Vehicle telemetry data for diagnostic analysis."""

    vehicle_id: str = Field(..., description="Unique vehicle identifier")
    engine_temperature: float = Field(..., ge=0, description="Engine temperature in Celsius")
    battery_voltage: float = Field(..., gt=0, description="Battery voltage in volts")
    front_left_tyre_psi: float = Field(..., ge=0, description="Front left tyre pressure in PSI")
    front_right_tyre_psi: float = Field(..., ge=0, description="Front right tyre pressure in PSI")
    rear_left_tyre_psi: float = Field(..., ge=0, description="Rear left tyre pressure in PSI")
    rear_right_tyre_psi: float = Field(..., ge=0, description="Rear right tyre pressure in PSI")
    coolant_level: float = Field(..., ge=0, le=100, description="Coolant level as percentage (0-100)")
