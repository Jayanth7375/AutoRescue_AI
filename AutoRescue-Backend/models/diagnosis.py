from enum import Enum
from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    """Severity levels for diagnostic findings."""

    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class DiagnosticResult(BaseModel):
    """Result of vehicle diagnostic analysis."""

    issue: str = Field(..., description="Description of the issue or condition found")
    affected_component: str = Field(..., description="Component affected by the issue")
    severity: SeverityLevel = Field(..., description="Severity level of the issue")
    safe_to_drive: bool = Field(..., description="Whether it is safe to drive the vehicle")
    recommendation: str = Field(..., description="Recommended action to take")
