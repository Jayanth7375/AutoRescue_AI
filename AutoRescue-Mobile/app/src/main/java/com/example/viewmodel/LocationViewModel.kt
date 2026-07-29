package com.example.viewmodel

import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.repository.LocationData
import com.example.repository.LocationRepository
import com.example.repository.LocationResult
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class LocationUiState(
    val isLoading: Boolean = false,
    val permissionGranted: Boolean = false,
    val permissionDenied: Boolean = false,
    val isLocationUnavailable: Boolean = false,
    val latitude: Double? = null,
    val longitude: Double? = null,
    val accuracy: Float? = null,
    val address: String? = null,
    val isSimulatedLocation: Boolean = false,
    val errorMessage: String? = null
)

class LocationViewModel(
    private val locationRepositoryProvider: ((Context) -> LocationRepository)? = null
) : ViewModel() {

    private val _uiState = MutableStateFlow(LocationUiState())
    val uiState: StateFlow<LocationUiState> = _uiState.asStateFlow()

    val latitude: StateFlow<Double?> = _uiState
        .map { it.latitude }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = null
        )

    val longitude: StateFlow<Double?> = _uiState
        .map { it.longitude }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = null
        )

    fun fetchLocation(context: Context) {
        _uiState.update {
            it.copy(
                isLoading = true,
                permissionGranted = true,
                permissionDenied = false,
                isLocationUnavailable = false,
                errorMessage = null
            )
        }

        viewModelScope.launch {
            val repository = locationRepositoryProvider?.invoke(context)
                ?: LocationRepository(context.applicationContext)

            when (val result = repository.getCurrentLocation()) {
                is LocationResult.Success -> {
                    val data = result.locationData
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            latitude = data.latitude,
                            longitude = data.longitude,
                            accuracy = data.accuracy,
                            address = data.locationName,
                            isSimulatedLocation = data.isSimulatedLocation,
                            permissionGranted = true,
                            permissionDenied = false,
                            isLocationUnavailable = false,
                            errorMessage = null
                        )
                    }
                }
                is LocationResult.LocationUnavailable -> {
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            isLocationUnavailable = true,
                            permissionGranted = true,
                            permissionDenied = false,
                            errorMessage = "GPS location unavailable"
                        )
                    }
                }
                is LocationResult.Error -> {
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            isLocationUnavailable = true,
                            permissionGranted = true,
                            permissionDenied = false,
                            errorMessage = result.message
                        )
                    }
                }
            }
        }
    }

    fun onPermissionDenied() {
        _uiState.update {
            it.copy(
                isLoading = false,
                permissionGranted = false,
                permissionDenied = true,
                isLocationUnavailable = false,
                errorMessage = "Location permission denied"
            )
        }
    }
}
