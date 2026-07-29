package com.example.model

enum class HealthStatus {
    HEALTHY,
    WARNING,
    CRITICAL
}

data class VehicleInfo(
    val name: String = "Tata Nexon",
    val registrationNumber: String = "TN 37 AB 1234",
    val fuelType: String = "Petrol",
    val modelYear: String = "2024",
    val odometer: String = "12,480 km",
    val overallHealthPercentage: Int = 87,
    val statusText: String = "HEALTHY"
)

data class ComponentHealth(
    val id: String,
    val name: String,
    val percentage: Int,
    val status: HealthStatus,
    val statusText: String,
    val detailsText: String = ""
)

data class DiagnosticResult(
    val issue: String = "Front-left tyre pressure low",
    val severity: HealthStatus = HealthStatus.WARNING,
    val severityLabel: String = "Warning",
    val safeToDrive: Boolean = true,
    val safeToDriveText: String = "Yes, short distance only",
    val recommendation: String = "Check tyre pressure before your next long drive.",
    val affectedComponent: String = "Tyre Pressure",
    val telemetry: VehicleTelemetry? = null
)

data class RescueOption(
    val id: String,
    val title: String,
    val description: String = ""
)

data class RescueRequestStatus(
    val isRequested: Boolean = false,
    val id: String = "REQ-84920",
    val optionTitle: String = "Flat Tyre",
    val providerName: String = "AutoRescue Swift Patrol #402",
    val statusMessage: String = "Rescue Unit Dispatched!",
    val estimatedArrival: String = "14 mins",
    val location: String = "Coimbatore, Tamil Nadu",
    val driverName: String = "Ramesh Kumar",
    val driverPhone: String = "+91 98765 01234"
)

data class AlertItem(
    val id: String,
    val title: String,
    val message: String,
    val timestamp: String,
    val severity: HealthStatus,
    val isCriticalInstruction: Boolean = false,
    val isRead: Boolean = false
)

data class UserProfile(
    val name: String = "Alex Morgan",
    val email: String = "alex.morgan@autorescue.ai",
    val phone: String = "+91 98765 43210",
    val emergencyContact: String = "Priya Morgan (+91 98765 99999)",
    val address: String = "Race Course Road, Coimbatore, Tamil Nadu"
)
