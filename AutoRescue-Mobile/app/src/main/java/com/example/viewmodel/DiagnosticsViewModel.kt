package com.example.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import android.util.Log
import com.example.model.DiagnosticResult
import com.example.model.HealthStatus
import com.example.model.VehicleTelemetry
import com.example.network.AutoRescueCheckResponse
import com.example.repository.AutoRescueRepository
import com.example.repository.TelemetryRepository
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class DiagnosticsState(
    val isScanning: Boolean = false,
    val scanProgress: Float = 0f,
    val scanStepMessage: String = "",
    val result: DiagnosticResult? = null,
    val errorMessage: String? = null,
    val backendResponse: AutoRescueCheckResponse? = null
)

class DiagnosticsViewModel(
    private val telemetryRepository: TelemetryRepository = TelemetryRepository(),
    private val autoRescueRepository: AutoRescueRepository = AutoRescueRepository(),
    private val locationViewModel: LocationViewModel? = null
) : ViewModel() {

    private val _diagnosticState = MutableStateFlow(DiagnosticsState())
    val diagnosticState: StateFlow<DiagnosticsState> = _diagnosticState.asStateFlow()

    private val _latestTelemetry = MutableStateFlow<VehicleTelemetry?>(null)
    val latestTelemetry: StateFlow<VehicleTelemetry?> = _latestTelemetry.asStateFlow()

    fun runVehicleCheck() {
        Log.d("AutoRescueDebug", "2 VIEWMODEL CALLED - DiagnosticsViewModel.runVehicleCheck()")
        viewModelScope.launch {
            _diagnosticState.update {
                it.copy(
                    isScanning = true,
                    scanProgress = 0.15f,
                    scanStepMessage = "Initializing OBD-II Interface...",
                    result = null,
                    errorMessage = null
                )
            }
            delay(500)

            _diagnosticState.update {
                it.copy(
                    scanProgress = 0.35f,
                    scanStepMessage = "Fetching real-time vehicle telemetry..."
                )
            }

            // 1. Fetch telemetry (demo values)
            Log.d("AutoRescueDebug", "Getting demo telemetry...")
            val telemetry = telemetryRepository.getLatestTelemetry()
            _latestTelemetry.value = telemetry
            Log.d("AutoRescueDebug", "Telemetry: engine=${telemetry.engineTemperatureC}°C, battery=${telemetry.batteryVoltageV}V")

            _diagnosticState.update {
                it.copy(
                    scanProgress = 0.55f,
                    scanStepMessage = "Getting GPS location..."
                )
            }

            // 2. Get GPS location (real coordinates)
            Log.d("AutoRescueDebug", "3 REQUESTING LOCATION from LocationViewModel")
            val latitude = locationViewModel?.uiState?.value?.latitude ?: 11.0168
            val longitude = locationViewModel?.uiState?.value?.longitude ?: 76.9558

            if (latitude == 11.0168 && longitude == 76.9558) {
                Log.w("AutoRescueDebug", "Using fallback coordinates - LocationViewModel may not have provided real GPS")
            } else {
                Log.d("AutoRescueDebug", "4 LOCATION RECEIVED lat=$latitude lon=$longitude")
            }

            _diagnosticState.update {
                it.copy(
                    scanProgress = 0.75f,
                    scanStepMessage = "Connecting to AutoRescue AI backend..."
                )
            }

            // 3. Call backend API
            Log.d("AutoRescueDebug", "5 CALLING REPOSITORY")
            val result = autoRescueRepository.runVehicleCheck(
                telemetry = telemetry,
                latitude = latitude,
                longitude = longitude
            )

            result.onSuccess { backendResponse ->
                Log.d("AutoRescueDebug", "7 BACKEND RESPONSE status=${backendResponse.status}")
                // Convert backend response to UI model
                val uiResult = convertBackendResponseToUiModel(backendResponse)

                _diagnosticState.update {
                    it.copy(
                        scanProgress = 1.0f,
                        scanStepMessage = "Vehicle Check Complete",
                        isScanning = false,
                        result = uiResult,
                        errorMessage = null,
                        backendResponse = backendResponse
                    )
                }
                Log.d("AutoRescueDebug", "8 UI STATE UPDATED with backend response")
            }

            result.onFailure { error ->
                Log.e("AutoRescueDebug", "BACKEND ERROR: ${error.message}", error)
                _diagnosticState.update {
                    it.copy(
                        scanProgress = 0f,
                        isScanning = false,
                        errorMessage = error.message ?: "Unknown error occurred",
                        result = null
                    )
                }
            }
        }
    }

    private fun convertBackendResponseToUiModel(
        response: AutoRescueCheckResponse
    ): DiagnosticResult {
        val severity = when (response.diagnosis.severity) {
            "CRITICAL" -> HealthStatus.CRITICAL
            "WARNING" -> HealthStatus.WARNING
            else -> HealthStatus.HEALTHY
        }

        return DiagnosticResult(
            issue = response.diagnosis.issue,
            severity = severity,
            severityLabel = response.diagnosis.severity,
            safeToDrive = response.diagnosis.safeToDrive,
            safeToDriveText = if (response.diagnosis.safeToDrive) "Yes, safe to drive" else "No - Unsafe to drive",
            recommendation = response.diagnosis.recommendation,
            affectedComponent = response.diagnosis.affectedComponent
        )
    }
}
