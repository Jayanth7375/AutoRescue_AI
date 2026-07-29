package com.example.viewmodel

import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import android.util.Log
import com.example.model.NearbyPlace
import com.example.model.NearbyPlacesResponse
import com.example.repository.LocationRepository
import com.example.repository.NearbyPlacesRepository
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class RescueState(
    // Category selection
    val selectedRescueCategory: String? = null, // FLAT_TYRE, BATTERY_ISSUE, ENGINE_BREAKDOWN, ACCIDENT, FUEL_NEEDED, OTHER

    // Battery flow state
    val batteryAssistanceType: String? = null, // EV_CHARGING or VEHICLE_BATTERY_ISSUE

    // Accident flow state
    val passengerInjury: Boolean? = null, // true=YES, false=NO, null=not answered

    // Nearby places state
    val nearbyPlaces: List<NearbyPlace> = emptyList(),
    val isLoadingPlaces: Boolean = false,
    val placesError: String? = null,
    val placesCategory: String? = null,

    // Navigation state
    val currentFlow: String = "CATEGORY_SELECTION", // CATEGORY_SELECTION, BATTERY_SELECTION, ACCIDENT_CHECK, NEARBY_PLACES, RESULT
)

class RescueViewModel(
    private val locationRepository: LocationRepository = LocationRepository(),
    private val nearbyPlacesRepository: NearbyPlacesRepository = NearbyPlacesRepository()
) : ViewModel() {

    private val _rescueState = MutableStateFlow(RescueState())
    val rescueState: StateFlow<RescueState> = _rescueState.asStateFlow()

    fun selectRescueCategory(category: String) {
        Log.d("RescueViewModel", "Selected category: $category")
        _rescueState.update {
            when (category) {
                "BATTERY_ISSUE" -> {
                    it.copy(
                        selectedRescueCategory = category,
                        currentFlow = "BATTERY_SELECTION"
                    )
                }
                "ACCIDENT" -> {
                    it.copy(
                        selectedRescueCategory = category,
                        currentFlow = "ACCIDENT_CHECK"
                    )
                }
                else -> {
                    it.copy(
                        selectedRescueCategory = category,
                        currentFlow = "NEARBY_PLACES"
                    )
                }
            }
        }
    }

    fun selectBatteryAssistanceType(type: String) {
        Log.d("RescueViewModel", "Selected battery assistance: $type")
        _rescueState.update {
            it.copy(
                batteryAssistanceType = type,
                currentFlow = "NEARBY_PLACES",
                placesCategory = if (type == "EV_CHARGING") "EV_CHARGING" else "BATTERY_SERVICE"
            )
        }
    }

    fun selectAccidentInjuryResponse(hasInjury: Boolean) {
        Log.d("RescueViewModel", "Accident injury response: $hasInjury")
        _rescueState.update {
            it.copy(
                passengerInjury = hasInjury,
                currentFlow = if (hasInjury) {
                    "NEARBY_PLACES"
                } else {
                    "RESULT" // Continue with existing accident flow
                },
                placesCategory = if (hasInjury) "HOSPITAL" else null
            )
        }
    }

    fun searchNearbyPlaces(
        latitude: Double,
        longitude: Double,
        context: Context
    ) {
        val placesCategory = _rescueState.value.placesCategory ?: return

        Log.d("RescueViewModel", "Searching nearby places: $placesCategory at $latitude, $longitude")

        viewModelScope.launch {
            _rescueState.update { it.copy(isLoadingPlaces = true, placesError = null) }
            delay(500) // Show loading briefly

            val result = when (placesCategory) {
                "EV_CHARGING" -> nearbyPlacesRepository.getEvChargingStations(latitude, longitude)
                "BATTERY_SERVICE" -> nearbyPlacesRepository.getBatteryServices(latitude, longitude)
                "FUEL_STATION" -> nearbyPlacesRepository.getFuelStations(latitude, longitude)
                "HOSPITAL" -> nearbyPlacesRepository.getHospitals(latitude, longitude)
                else -> {
                    _rescueState.update {
                        it.copy(
                            isLoadingPlaces = false,
                            placesError = "Unknown category"
                        )
                    }
                    return@launch
                }
            }

            result.onSuccess { response ->
                Log.d("RescueViewModel", "Found ${response.count} places for $placesCategory")
                _rescueState.update {
                    it.copy(
                        nearbyPlaces = response.places,
                        isLoadingPlaces = false,
                        placesError = if (response.places.isEmpty()) {
                            getEmptyStateMessage(placesCategory)
                        } else null,
                        currentFlow = "NEARBY_PLACES"
                    )
                }
            }

            result.onFailure { error ->
                Log.e("RescueViewModel", "Error searching places: ${error.message}", error)
                val errorMessage = when (error) {
                    is retrofit2.HttpException -> when (error.code()) {
                        400 -> "Invalid location or category"
                        422 -> "Invalid coordinates"
                        503 -> "Service temporarily unavailable"
                        else -> "Error searching nearby places (${error.code()})"
                    }
                    else -> error.message ?: "Unknown error occurred"
                }
                _rescueState.update {
                    it.copy(
                        isLoadingPlaces = false,
                        placesError = errorMessage,
                        nearbyPlaces = emptyList()
                    )
                }
            }
        }
    }

    fun resetFlow() {
        Log.d("RescueViewModel", "Resetting rescue flow")
        _rescueState.update {
            RescueState()
        }
    }

    fun goBackToSelection() {
        Log.d("RescueViewModel", "Going back to category selection")
        _rescueState.update {
            it.copy(
                currentFlow = "CATEGORY_SELECTION",
                batteryAssistanceType = null,
                passengerInjury = null,
                nearbyPlaces = emptyList(),
                placesError = null
            )
        }
    }

    fun goBackToBatterySelection() {
        Log.d("RescueViewModel", "Going back to battery selection")
        _rescueState.update {
            it.copy(
                currentFlow = "BATTERY_SELECTION",
                batteryAssistanceType = null,
                nearbyPlaces = emptyList(),
                placesError = null
            )
        }
    }

    private fun getEmptyStateMessage(category: String): String {
        return when (category) {
            "EV_CHARGING" -> "No EV charging stations were found within the current search area."
            "BATTERY_SERVICE" -> "No nearby vehicle repair services were found."
            "FUEL_STATION" -> "No fuel stations were found within the current search area."
            "HOSPITAL" -> "No hospitals were found within the current search area."
            else -> "No results found in this area."
        }
    }

    fun getTitleForCategory(): String {
        return when (_rescueState.value.placesCategory) {
            "EV_CHARGING" -> "Nearby EV Charging Stations"
            "BATTERY_SERVICE" -> "Nearby Battery Assistance"
            "FUEL_STATION" -> "Nearby Fuel Stations"
            "HOSPITAL" -> "Nearby Hospitals"
            else -> "Nearby Results"
        }
    }

    fun getLoadingMessageForCategory(): String {
        return when (_rescueState.value.placesCategory) {
            "EV_CHARGING" -> "Finding nearby EV charging stations..."
            "BATTERY_SERVICE" -> "Finding nearby battery services..."
            "FUEL_STATION" -> "Finding nearby fuel stations..."
            "HOSPITAL" -> "Finding nearby hospitals..."
            else -> "Searching nearby places..."
        }
    }
}
