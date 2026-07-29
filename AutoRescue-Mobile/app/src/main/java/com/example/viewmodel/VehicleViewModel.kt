package com.example.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.engine.DiagnosticEngine
import com.example.model.*
import com.example.repository.TelemetryRepository
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class DiagnosticUiState(
    val isScanning: Boolean = false,
    val scanProgress: Float = 0f,
    val scanStepMessage: String = "Initializing OBD-II diagnostics...",
    val result: DiagnosticResult? = null
)

typealias DiagnosticState = DiagnosticUiState

data class DeviceLocationState(
    val isLoading: Boolean = false,
    val permissionGranted: Boolean = false,
    val permissionDenied: Boolean = false,
    val isLocationUnavailable: Boolean = false,
    val latitude: Double? = null,
    val longitude: Double? = null,
    val accuracy: Float? = null,
    val locationAddress: String? = null,
    val isSimulatedLocation: Boolean = false,
    val errorMessage: String? = null
)

data class ServiceCentresUiState(
    val isLoading: Boolean = false,
    val serviceCentres: List<com.example.model.ServiceCentre> = emptyList(),
    val errorType: com.example.repository.ServiceCentreErrorType? = null,
    val errorMessage: String? = null,
    val lastFetchedLat: Double? = null,
    val lastFetchedLng: Double? = null
)

class VehicleViewModel(
    private val telemetryRepository: TelemetryRepository = TelemetryRepository(),
    private val diagnosticEngine: DiagnosticEngine = DiagnosticEngine()
) : ViewModel() {

    private val _locationState = MutableStateFlow(DeviceLocationState())
    val locationState: StateFlow<DeviceLocationState> = _locationState.asStateFlow()

    private val _serviceCentresState = MutableStateFlow(ServiceCentresUiState())
    val serviceCentresState: StateFlow<ServiceCentresUiState> = _serviceCentresState.asStateFlow()

    private val _vehicleInfo = MutableStateFlow(VehicleInfo())
    val vehicleInfo: StateFlow<VehicleInfo> = _vehicleInfo.asStateFlow()

    private val _componentHealthList = MutableStateFlow(
        listOf(
            ComponentHealth("eng", "Engine", 94, HealthStatus.HEALTHY, "Normal", "Ignition timing, sensor & oil level nominal"),
            ComponentHealth("bat", "Battery", 88, HealthStatus.HEALTHY, "Good", "12.6V output, healthy charge cycle"),
            ComponentHealth("tyr", "Tyres", 72, HealthStatus.WARNING, "Warning", "Front-left tyre pressure at 28 PSI (Low)"),
            ComponentHealth("col", "Coolant", 91, HealthStatus.HEALTHY, "Normal", "Temperature 90°C, level optimal"),
            ComponentHealth("brk", "Brakes", 95, HealthStatus.HEALTHY, "Good", "Pads wear at 18%, hydraulic pressure stable")
        )
    )
    val componentHealthList: StateFlow<List<ComponentHealth>> = _componentHealthList.asStateFlow()

    private val _diagnosticState = MutableStateFlow(DiagnosticUiState())
    val diagnosticState: StateFlow<DiagnosticUiState> = _diagnosticState.asStateFlow()

    private val _rescueOptions = MutableStateFlow(
        listOf(
            RescueOption("1", "Flat Tyre", "Puncture or air replacement"),
            RescueOption("2", "Battery Issue", "Jumpstart or battery swap"),
            RescueOption("3", "Engine Breakdown", "Mechanical inspection or towing"),
            RescueOption("4", "Accident", "Emergency response & roadside support"),
            RescueOption("5", "Fuel Needed", "Emergency petrol delivery"),
            RescueOption("6", "Other", "General roadside query")
        )
    )
    val rescueOptions: StateFlow<List<RescueOption>> = _rescueOptions.asStateFlow()

    private val _selectedRescueOption = MutableStateFlow("Flat Tyre")
    val selectedRescueOption: StateFlow<String> = _selectedRescueOption.asStateFlow()

    private val _rescueStatus = MutableStateFlow(RescueRequestStatus())
    val rescueStatus: StateFlow<RescueRequestStatus> = _rescueStatus.asStateFlow()

    private val _notifications = MutableStateFlow(
        listOf(
            AlertItem(
                id = "notif_1",
                title = "Critical Engine Alert",
                message = "Critical oil pressure drop detected on Cylinder 2 telemetry.",
                timestamp = "Today, 08:15 AM",
                severity = HealthStatus.CRITICAL,
                isCriticalInstruction = true,
                isRead = false
            ),
            AlertItem(
                id = "notif_2",
                title = "Low Tyre Pressure",
                message = "Front-left tyre pressure dropped to 28 PSI (Recommended: 33 PSI).",
                timestamp = "Today, 10:32 AM",
                severity = HealthStatus.WARNING,
                isCriticalInstruction = false,
                isRead = false
            ),
            AlertItem(
                id = "notif_3",
                title = "Service Reminder",
                message = "Scheduled 15,000 km routine maintenance inspection due in 14 days.",
                timestamp = "Yesterday, 04:00 PM",
                severity = HealthStatus.HEALTHY,
                isCriticalInstruction = false,
                isRead = true
            ),
            AlertItem(
                id = "notif_4",
                title = "Battery Health Update",
                message = "Battery state of health is 88%. Terminal voltage normal at 12.6V.",
                timestamp = "Jul 25, 11:20 AM",
                severity = HealthStatus.HEALTHY,
                isCriticalInstruction = false,
                isRead = true
            )
        )
    )
    val notifications: StateFlow<List<AlertItem>> = _notifications.asStateFlow()

    private val _userProfile = MutableStateFlow(UserProfile())
    val userProfile: StateFlow<UserProfile> = _userProfile.asStateFlow()

    fun runVehicleCheck(context: android.content.Context? = null) {
        if (_diagnosticState.value.isScanning) return

        viewModelScope.launch {
            _diagnosticState.update {
                it.copy(
                    isScanning = true,
                    scanProgress = 0.15f,
                    scanStepMessage = "Connecting to OBD-II ECU Interface...",
                    result = null
                )
            }
            delay(400)

            _diagnosticState.update {
                it.copy(
                    scanProgress = 0.45f,
                    scanStepMessage = "Fetching real-time vehicle telemetry..."
                )
            }

            val telemetry = telemetryRepository.getLatestTelemetry()

            _diagnosticState.update {
                it.copy(
                    scanProgress = 0.75f,
                    scanStepMessage = "Evaluating telemetry against safety rules..."
                )
            }
            delay(400)

            val calculatedResult = diagnosticEngine.analyze(telemetry)

            context?.let { ctx ->
                com.example.service.VehicleMonitoringService.evaluateAndNotify(ctx.applicationContext, calculatedResult)
            }

            // Update component health list to reflect actual calculated telemetry
            _componentHealthList.update { list ->
                list.map { component ->
                    when (component.id) {
                        "eng" -> {
                            val temp = telemetry.engineTemperatureC
                            val status = when {
                                temp > 115.0 -> HealthStatus.CRITICAL
                                temp in 106.0..115.0 -> HealthStatus.WARNING
                                else -> HealthStatus.HEALTHY
                            }
                            val pct = when (status) {
                                HealthStatus.HEALTHY -> 95
                                HealthStatus.WARNING -> 70
                                HealthStatus.CRITICAL -> 30
                            }
                            component.copy(
                                percentage = pct,
                                status = status,
                                statusText = if (status == HealthStatus.HEALTHY) "Normal" else status.name,
                                detailsText = "Engine temp at ${String.format(java.util.Locale.US, "%.1f", temp)}°C"
                            )
                        }
                        "bat" -> {
                            val bat = telemetry.batteryVoltageV
                            val status = when {
                                bat < 12.0 -> HealthStatus.CRITICAL
                                bat in 12.0..12.39 -> HealthStatus.WARNING
                                else -> HealthStatus.HEALTHY
                            }
                            val pct = when (status) {
                                HealthStatus.HEALTHY -> 90
                                HealthStatus.WARNING -> 65
                                HealthStatus.CRITICAL -> 25
                            }
                            component.copy(
                                percentage = pct,
                                status = status,
                                statusText = if (status == HealthStatus.HEALTHY) "Good" else status.name,
                                detailsText = "Battery output at ${String.format(java.util.Locale.US, "%.2f", bat)}V"
                            )
                        }
                        "tyr" -> {
                            val psi = telemetry.tyrePressurePsi
                            val status = when {
                                psi < 25.0 -> HealthStatus.CRITICAL
                                psi in 25.0..29.9 -> HealthStatus.WARNING
                                else -> HealthStatus.HEALTHY
                            }
                            val pct = when (status) {
                                HealthStatus.HEALTHY -> 92
                                HealthStatus.WARNING -> 68
                                HealthStatus.CRITICAL -> 20
                            }
                            component.copy(
                                percentage = pct,
                                status = status,
                                statusText = if (status == HealthStatus.HEALTHY) "Good" else status.name,
                                detailsText = "Pressure at ${String.format(java.util.Locale.US, "%.1f", psi)} PSI"
                            )
                        }
                        "col" -> {
                            val coolant = telemetry.coolantLevelPercent
                            val status = when {
                                coolant < 30.0 -> HealthStatus.CRITICAL
                                coolant in 30.0..49.9 -> HealthStatus.WARNING
                                else -> HealthStatus.HEALTHY
                            }
                            val pct = when (status) {
                                HealthStatus.HEALTHY -> 90
                                HealthStatus.WARNING -> 60
                                HealthStatus.CRITICAL -> 20
                            }
                            component.copy(
                                percentage = pct,
                                status = status,
                                statusText = if (status == HealthStatus.HEALTHY) "Optimal" else status.name,
                                detailsText = "Coolant level at ${coolant.toInt()}%"
                            )
                        }
                        else -> component
                    }
                }
            }

            _diagnosticState.update {
                it.copy(
                    isScanning = false,
                    scanProgress = 1.0f,
                    scanStepMessage = "Vehicle Check Complete",
                    result = calculatedResult
                )
            }
        }
    }

    fun selectRescueOption(optionTitle: String) {
        _selectedRescueOption.value = optionTitle
    }

    fun requestAssistance() {
        viewModelScope.launch {
            _rescueStatus.update {
                it.copy(
                    isRequested = true,
                    optionTitle = _selectedRescueOption.value,
                    statusMessage = "Rescue Unit Dispatched!",
                    estimatedArrival = "14 mins"
                )
            }
        }
    }

    fun cancelAssistance() {
        _rescueStatus.update {
            it.copy(isRequested = false)
        }
    }

    fun markNotificationRead(id: String) {
        _notifications.update { list ->
            list.map { if (it.id == id) it.copy(isRead = true) else it }
        }
    }

    fun fetchLocation(context: android.content.Context) {
        _locationState.update {
            it.copy(
                isLoading = true,
                permissionGranted = true,
                permissionDenied = false,
                isLocationUnavailable = false,
                errorMessage = null
            )
        }
        viewModelScope.launch {
            val repository = com.example.repository.LocationRepository(context.applicationContext)
            when (val result = repository.getCurrentLocation()) {
                is com.example.repository.LocationResult.Success -> {
                    val data = result.locationData
                    _locationState.update {
                        it.copy(
                            isLoading = false,
                            latitude = data.latitude,
                            longitude = data.longitude,
                            accuracy = data.accuracy,
                            locationAddress = data.locationName,
                            isSimulatedLocation = data.isSimulatedLocation,
                            isLocationUnavailable = false,
                            permissionDenied = false
                        )
                    }
                    _rescueStatus.update {
                        it.copy(location = data.locationName)
                    }
                    fetchNearbyServiceCentres(context, data.latitude, data.longitude)
                }
                is com.example.repository.LocationResult.LocationUnavailable -> {
                    _locationState.update {
                        it.copy(
                            isLoading = false,
                            isLocationUnavailable = true
                        )
                    }
                    _serviceCentresState.update {
                        it.copy(
                            isLoading = false,
                            serviceCentres = emptyList(),
                            errorType = com.example.repository.ServiceCentreErrorType.GpsUnavailable,
                            errorMessage = "GPS unavailable. Please enable location services on your phone."
                        )
                    }
                    _rescueStatus.update {
                        it.copy(location = "GPS Unavailable")
                    }
                }
                is com.example.repository.LocationResult.Error -> {
                    _locationState.update {
                        it.copy(
                            isLoading = false,
                            isLocationUnavailable = true,
                            errorMessage = result.message
                        )
                    }
                    _serviceCentresState.update {
                        it.copy(
                            isLoading = false,
                            serviceCentres = emptyList(),
                            errorType = com.example.repository.ServiceCentreErrorType.GpsUnavailable,
                            errorMessage = result.message
                        )
                    }
                    _rescueStatus.update {
                        it.copy(location = "Location Error")
                    }
                }
            }
        }
    }

    fun setLocationPermissionDenied() {
        _locationState.update {
            it.copy(
                isLoading = false,
                permissionGranted = false,
                permissionDenied = true,
                isLocationUnavailable = false
            )
        }
        _serviceCentresState.update {
            it.copy(
                isLoading = false,
                serviceCentres = emptyList(),
                errorType = com.example.repository.ServiceCentreErrorType.PermissionDenied,
                errorMessage = "Location permission denied. Please grant FINE or COARSE location permission."
            )
        }
        _rescueStatus.update {
            it.copy(location = "Location Permission Denied")
        }
    }

    fun fetchNearbyServiceCentres(context: android.content.Context, lat: Double, lng: Double) {
        _serviceCentresState.update {
            it.copy(
                isLoading = true,
                errorType = null,
                errorMessage = null,
                lastFetchedLat = lat,
                lastFetchedLng = lng
            )
        }
        viewModelScope.launch {
            val (issueType, severity) = getActiveIssueContext()
            val repo = com.example.repository.PlacesServiceRepository(context.applicationContext)
            when (val result = repo.getNearbyServiceCentres(lat, lng, issueType = issueType, severity = severity)) {
                is com.example.repository.ServiceCentresResult.Success -> {
                    _serviceCentresState.update {
                        it.copy(
                            isLoading = false,
                            serviceCentres = result.serviceCentres,
                            errorType = null,
                            errorMessage = null
                        )
                    }
                }
                is com.example.repository.ServiceCentresResult.Error -> {
                    _serviceCentresState.update {
                        it.copy(
                            isLoading = false,
                            serviceCentres = emptyList(),
                            errorType = result.errorType,
                            errorMessage = result.message
                        )
                    }
                }
            }
        }
    }

    private fun getActiveIssueContext(): Pair<String, HealthStatus> {
        val diag = _diagnosticState.value.result
        if (diag != null) {
            return Pair(diag.issue, diag.severity)
        }

        val worstComponent = _componentHealthList.value
            .filter { it.status != HealthStatus.HEALTHY }
            .minByOrNull {
                when (it.status) {
                    HealthStatus.CRITICAL -> 0
                    HealthStatus.WARNING -> 1
                    HealthStatus.HEALTHY -> 2
                }
            }

        if (worstComponent != null) {
            return Pair(worstComponent.name, worstComponent.status)
        }

        val selectedRescue = _selectedRescueOption.value
        return Pair(selectedRescue, HealthStatus.WARNING)
    }

    fun isVehicleSafeToDrive(): Boolean {
        val diag = _diagnosticState.value.result
        if (diag != null) {
            return diag.safeToDrive
        }
        return !_componentHealthList.value.any { it.status == HealthStatus.CRITICAL }
    }
}
