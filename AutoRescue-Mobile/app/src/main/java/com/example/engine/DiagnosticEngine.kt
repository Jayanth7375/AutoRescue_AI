package com.example.engine

import com.example.model.DiagnosticResult
import com.example.model.HealthStatus
import com.example.model.VehicleTelemetry
import java.util.Locale

class DiagnosticEngine {

    fun analyze(telemetry: VehicleTelemetry): DiagnosticResult {
        val detectedIssues = mutableListOf<ComponentEvaluation>()

        // 1. Engine Temperature
        val tempVal = telemetry.engineTemperatureC
        when {
            tempVal > 115.0 -> {
                detectedIssues.add(
                    ComponentEvaluation(
                        componentName = "Engine Temperature",
                        issueDescription = "Engine temperature critically high (${String.format(Locale.US, "%.1f", tempVal)}°C)",
                        severity = HealthStatus.CRITICAL,
                        recommendation = "Pull over immediately in a safe spot, turn off the engine, and allow it to cool down."
                    )
                )
            }
            tempVal in 106.0..115.0 -> {
                detectedIssues.add(
                    ComponentEvaluation(
                        componentName = "Engine Temperature",
                        issueDescription = "Engine temperature elevated (${String.format(Locale.US, "%.1f", tempVal)}°C)",
                        severity = HealthStatus.WARNING,
                        recommendation = "Monitor temperature gauge closely and check coolant radiator levels."
                    )
                )
            }
        }

        // 2. Battery Voltage
        val batVal = telemetry.batteryVoltageV
        when {
            batVal < 12.0 -> {
                detectedIssues.add(
                    ComponentEvaluation(
                        componentName = "Battery Voltage",
                        issueDescription = "Battery voltage critically low (${String.format(Locale.US, "%.2f", batVal)}V)",
                        severity = HealthStatus.CRITICAL,
                        recommendation = "Recharge or replace battery immediately to prevent sudden vehicle shutdown."
                    )
                )
            }
            batVal >= 12.0 && batVal <= 12.39 -> {
                detectedIssues.add(
                    ComponentEvaluation(
                        componentName = "Battery Voltage",
                        issueDescription = "Battery charge low (${String.format(Locale.US, "%.2f", batVal)}V)",
                        severity = HealthStatus.WARNING,
                        recommendation = "Drive for at least 20 minutes to allow the alternator to recharge the battery."
                    )
                )
            }
        }

        // 3. Tyre PSI
        val tyreVal = telemetry.tyrePressurePsi
        when {
            tyreVal < 25.0 -> {
                detectedIssues.add(
                    ComponentEvaluation(
                        componentName = "Tyre Pressure",
                        issueDescription = "Tyre pressure critically low (${String.format(Locale.US, "%.1f", tyreVal)} PSI)",
                        severity = HealthStatus.CRITICAL,
                        recommendation = "Inflate tyre to standard 33 PSI immediately or swap with spare tyre."
                    )
                )
            }
            tyreVal >= 25.0 && tyreVal <= 29.9 -> {
                detectedIssues.add(
                    ComponentEvaluation(
                        componentName = "Tyre Pressure",
                        issueDescription = "Tyre pressure below recommended (${String.format(Locale.US, "%.1f", tyreVal)} PSI)",
                        severity = HealthStatus.WARNING,
                        recommendation = "Refill tyre air pressure to standard 32-35 PSI at nearest station."
                    )
                )
            }
        }

        // 4. Coolant Level
        val coolantVal = telemetry.coolantLevelPercent
        when {
            coolantVal < 30.0 -> {
                detectedIssues.add(
                    ComponentEvaluation(
                        componentName = "Coolant Level",
                        issueDescription = "Coolant level critically low (${coolantVal.toInt()}%)",
                        severity = HealthStatus.CRITICAL,
                        recommendation = "Top up engine coolant reservoir immediately before driving to avoid overheating."
                    )
                )
            }
            coolantVal >= 30.0 && coolantVal <= 49.9 -> {
                detectedIssues.add(
                    ComponentEvaluation(
                        componentName = "Coolant Level",
                        issueDescription = "Coolant level low (${coolantVal.toInt()}%)",
                        severity = HealthStatus.WARNING,
                        recommendation = "Top up coolant reservoir at your earliest convenience."
                    )
                )
            }
        }

        if (detectedIssues.isEmpty()) {
            return DiagnosticResult(
                issue = "All Systems Nominal",
                severity = HealthStatus.HEALTHY,
                severityLabel = "Normal",
                safeToDrive = true,
                safeToDriveText = "Yes, safe to drive",
                recommendation = "Vehicle is in optimal working condition. Regular maintenance recommended.",
                affectedComponent = "None",
                telemetry = telemetry
            )
        }

        val hasCritical = detectedIssues.any { it.severity == HealthStatus.CRITICAL }
        val overallSeverity = if (hasCritical) HealthStatus.CRITICAL else HealthStatus.WARNING
        val isSafeToDrive = !hasCritical

        val primaryIssue = detectedIssues.firstOrNull { it.severity == HealthStatus.CRITICAL }
            ?: detectedIssues.first()

        val primaryIssueText = if (detectedIssues.size > 1) {
            "${primaryIssue.issueDescription} (+${detectedIssues.size - 1} other issue(s))"
        } else {
            primaryIssue.issueDescription
        }

        val componentsText = detectedIssues.joinToString(", ") { it.componentName }

        val severityLabel = when (overallSeverity) {
            HealthStatus.CRITICAL -> "Critical"
            HealthStatus.WARNING -> "Warning"
            HealthStatus.HEALTHY -> "Normal"
        }

        val safeToDriveText = if (isSafeToDrive) "Yes, with caution" else "No - Unsafe to drive"

        return DiagnosticResult(
            issue = primaryIssueText,
            severity = overallSeverity,
            severityLabel = severityLabel,
            safeToDrive = isSafeToDrive,
            safeToDriveText = safeToDriveText,
            recommendation = primaryIssue.recommendation,
            affectedComponent = componentsText,
            telemetry = telemetry
        )
    }

    private data class ComponentEvaluation(
        val componentName: String,
        val issueDescription: String,
        val severity: HealthStatus,
        val recommendation: String
    )
}
