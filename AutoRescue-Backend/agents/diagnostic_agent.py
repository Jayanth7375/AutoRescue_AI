from models.telemetry import VehicleTelemetry
from models.diagnosis import DiagnosticResult
from tools import diagnose_vehicle


class DiagnosticAgent:
    """
    Simple diagnostic agent wrapper for vehicle safety assessment.

    This agent encapsulates the diagnostic logic and will serve as a placeholder
    for future integration with Agentverse agents or more sophisticated AI-driven
    diagnostics.
    """

    def run(self, telemetry: VehicleTelemetry) -> DiagnosticResult:
        """
        Run diagnostic analysis on provided vehicle telemetry data.

        Args:
            telemetry: Vehicle telemetry data to analyze

        Returns:
            DiagnosticResult containing the diagnostic findings
        """
        return diagnose_vehicle(telemetry)


# Global instance for use throughout the application
diagnostic_agent = DiagnosticAgent()
