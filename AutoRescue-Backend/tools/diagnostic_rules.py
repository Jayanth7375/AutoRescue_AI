from models.telemetry import VehicleTelemetry
from models.diagnosis import DiagnosticResult, SeverityLevel


def diagnose_vehicle(data: VehicleTelemetry) -> DiagnosticResult:
    """
    Deterministic diagnostic rule engine for vehicle safety assessment.

    Evaluates vehicle telemetry against predefined safety thresholds and returns
    the most severe issue found, prioritized by safety impact.
    """
    issues = []

    # Check engine temperature
    if data.engine_temperature > 115:
        issues.append(
            DiagnosticResult(
                issue="Engine overheating",
                affected_component="engine",
                severity=SeverityLevel.CRITICAL,
                safe_to_drive=False,
                recommendation="Stop the vehicle safely and switch off the engine. Allow it to cool before proceeding.",
            )
        )
    elif data.engine_temperature > 105:
        issues.append(
            DiagnosticResult(
                issue="Engine temperature elevated",
                affected_component="engine",
                severity=SeverityLevel.WARNING,
                safe_to_drive=True,
                recommendation="Monitor engine temperature. Reduce load and ensure cooling system is functioning properly.",
            )
        )

    # Check coolant level
    if data.coolant_level < 30:
        issues.append(
            DiagnosticResult(
                issue="Coolant level critically low",
                affected_component="cooling_system",
                severity=SeverityLevel.CRITICAL,
                safe_to_drive=False,
                recommendation="Stop the vehicle and refill coolant immediately. Check for leaks in the cooling system.",
            )
        )
    elif data.coolant_level < 50:
        issues.append(
            DiagnosticResult(
                issue="Coolant level low",
                affected_component="cooling_system",
                severity=SeverityLevel.WARNING,
                safe_to_drive=True,
                recommendation="Refill coolant at the earliest opportunity. Monitor engine temperature.",
            )
        )

    # Check battery voltage
    if data.battery_voltage < 12.0:
        issues.append(
            DiagnosticResult(
                issue="Battery voltage critically low",
                affected_component="battery",
                severity=SeverityLevel.CRITICAL,
                safe_to_drive=True,
                recommendation="Battery may fail to start or power vehicle systems reliably. Inspect the battery and charging system immediately.",
            )
        )
    elif data.battery_voltage < 12.4:
        issues.append(
            DiagnosticResult(
                issue="Battery voltage low",
                affected_component="battery",
                severity=SeverityLevel.WARNING,
                safe_to_drive=True,
                recommendation="Have battery and charging system inspected. Battery may not provide reliable power.",
            )
        )

    # Check tyre pressures
    tyres = [
        ("front_left_tyre", data.front_left_tyre_psi),
        ("front_right_tyre", data.front_right_tyre_psi),
        ("rear_left_tyre", data.rear_left_tyre_psi),
        ("rear_right_tyre", data.rear_right_tyre_psi),
    ]

    for tyre_name, pressure in tyres:
        if pressure < 25:
            issues.append(
                DiagnosticResult(
                    issue=f"{tyre_name.replace('_', ' ').title()} pressure critically low",
                    affected_component=tyre_name,
                    severity=SeverityLevel.CRITICAL,
                    safe_to_drive=False,
                    recommendation="Stop safely and inspect or inflate the tyre before continuing.",
                )
            )
        elif pressure < 30:
            issues.append(
                DiagnosticResult(
                    issue=f"{tyre_name.replace('_', ' ').title()} pressure low",
                    affected_component=tyre_name,
                    severity=SeverityLevel.WARNING,
                    safe_to_drive=True,
                    recommendation="Inflate tyre to recommended pressure. Check for punctures or slow leaks.",
                )
            )

    # Return most severe issue, prioritizing by severity and safety impact
    if issues:
        critical_issues = [i for i in issues if i.severity == SeverityLevel.CRITICAL]
        if critical_issues:
            # Prioritize critical issues by safety impact
            priority_order = ["engine", "cooling_system", "battery"]
            for component in priority_order:
                for issue in critical_issues:
                    if issue.affected_component == component:
                        return issue
            # For critical tyre issues, return the first one
            if critical_issues:
                return critical_issues[0]

        # Return first warning if no critical issues
        warning_issues = [i for i in issues if i.severity == SeverityLevel.WARNING]
        if warning_issues:
            return warning_issues[0]

    # No issues found
    return DiagnosticResult(
        issue="No critical issues detected",
        affected_component="vehicle",
        severity=SeverityLevel.NORMAL,
        safe_to_drive=True,
        recommendation="Vehicle systems appear to be within normal ranges.",
    )
