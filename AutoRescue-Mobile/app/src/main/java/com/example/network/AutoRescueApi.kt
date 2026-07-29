package com.example.network

import com.example.model.ChatRequest
import com.example.model.ChatResponse
import com.squareup.moshi.Json
import retrofit2.http.Body
import retrofit2.http.POST

// ===== REQUEST DTOS =====

data class AutoRescueCheckRequest(
    @Json(name = "vehicle_id")
    val vehicleId: String,

    @Json(name = "engine_temperature")
    val engineTemperature: Double,

    @Json(name = "battery_voltage")
    val batteryVoltage: Double,

    @Json(name = "front_left_tyre_psi")
    val frontLeftTyrePsi: Double,

    @Json(name = "front_right_tyre_psi")
    val frontRightTyrePsi: Double,

    @Json(name = "rear_left_tyre_psi")
    val rearLeftTyrePsi: Double,

    @Json(name = "rear_right_tyre_psi")
    val rearRightTyrePsi: Double,

    @Json(name = "coolant_level")
    val coolantLevel: Double,

    @Json(name = "latitude")
    val latitude: Double,

    @Json(name = "longitude")
    val longitude: Double
)

// ===== RESPONSE DTOS =====

data class AutoRescueCheckResponse(
    @Json(name = "request_id")
    val requestId: String,

    @Json(name = "vehicle_id")
    val vehicleId: String,

    @Json(name = "status")
    val status: String, // HEALTHY, SERVICE_RECOMMENDED, ASSISTANCE_REQUIRED

    @Json(name = "diagnosis")
    val diagnosis: DiagnosisDto,

    @Json(name = "service_centres")
    val serviceCentres: List<ServiceCentreDto> = emptyList(),

    @Json(name = "navigation_allowed")
    val navigationAllowed: Boolean,

    @Json(name = "rescue")
    val rescue: RescueDto? = null,

    @Json(name = "message")
    val message: String
)

data class DiagnosisDto(
    @Json(name = "issue")
    val issue: String,

    @Json(name = "affected_component")
    val affectedComponent: String,

    @Json(name = "severity")
    val severity: String, // NORMAL, WARNING, CRITICAL

    @Json(name = "safe_to_drive")
    val safeToDrive: Boolean,

    @Json(name = "recommendation")
    val recommendation: String
)

data class ServiceCentreDto(
    @Json(name = "place_id")
    val placeId: String,

    @Json(name = "name")
    val name: String,

    @Json(name = "address")
    val address: String,

    @Json(name = "latitude")
    val latitude: Double,

    @Json(name = "longitude")
    val longitude: Double,

    @Json(name = "rating")
    val rating: Double? = null,

    @Json(name = "review_count")
    val reviewCount: Int? = null,

    @Json(name = "is_open")
    val isOpen: Boolean? = null,

    @Json(name = "distance_km")
    val distanceKm: Double,

    @Json(name = "priority_score")
    val priorityScore: Double,

    @Json(name = "recommendation_reason")
    val recommendationReason: String
)

data class RescueDto(
    @Json(name = "assistance_required")
    val assistanceRequired: Boolean,

    @Json(name = "assistance_type")
    val assistanceType: String,

    @Json(name = "priority")
    val priority: String, // LOW, MEDIUM, HIGH, CRITICAL

    @Json(name = "can_drive")
    val canDrive: Boolean,

    @Json(name = "tow_required")
    val towRequired: Boolean,

    @Json(name = "instructions")
    val instructions: String,

    @Json(name = "reason")
    val reason: String,

    @Json(name = "destination_name")
    val destinationName: String? = null,

    @Json(name = "destination_place_id")
    val destinationPlaceId: String? = null,

    @Json(name = "estimated_dispatch_minutes")
    val estimatedDispatchMinutes: Int? = null
)

// ===== RETROFIT INTERFACE =====

interface AutoRescueApi {

    @POST("api/autorescue/check")
    suspend fun runVehicleCheck(
        @Body request: AutoRescueCheckRequest
    ): AutoRescueCheckResponse

    @POST("api/chat")
    suspend fun sendChatMessage(
        @Body request: ChatRequest
    ): ChatResponse
}
