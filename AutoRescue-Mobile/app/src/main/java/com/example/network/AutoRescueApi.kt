package com.example.network

import com.example.model.ChatRequest
import com.example.model.ChatResponse
import com.example.model.NearbyPlace
import com.example.model.NearbyPlacesResponse
import com.squareup.moshi.Json
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Query

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
    val message: String,

    // Phase 9 Extended fields
    @Json(name = "telemetry_validation")
    val telemetryValidation: TelemetryValidationDto? = null,

    @Json(name = "safety")
    val safety: SafetyDto? = null,

    @Json(name = "maintenance")
    val maintenance: MaintenanceDto? = null,

    @Json(name = "notifications")
    val notifications: List<NotificationDto> = emptyList(),

    @Json(name = "explanation")
    val explanation: ExplanationDto? = null,

    @Json(name = "verification")
    val verification: VerificationDto? = null,

    @Json(name = "agent_trace")
    val agentTrace: List<AgentTraceEntryDto> = emptyList()
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

// ===== PHASE 9 EXTENDED DTOS =====

data class TelemetryValidationDto(
    @Json(name = "valid")
    val valid: Boolean = true,

    @Json(name = "issues")
    val issues: List<String> = emptyList(),

    @Json(name = "normalized_telemetry")
    val normalizedTelemetry: Map<String, Any> = emptyMap()
)

data class SafetyDto(
    @Json(name = "safe_to_drive")
    val safeToDrive: Boolean,

    @Json(name = "navigation_allowed")
    val navigationAllowed: Boolean,

    @Json(name = "tow_required")
    val towRequired: Boolean,

    @Json(name = "risk_level")
    val riskLevel: String // LOW, MEDIUM, HIGH
)

data class MaintenanceDto(
    @Json(name = "component")
    val component: String,

    @Json(name = "action")
    val action: String,

    @Json(name = "urgency")
    val urgency: String, // ROUTINE, SOON, IMMEDIATE

    @Json(name = "reason")
    val reason: String = ""
)

data class NotificationDto(
    @Json(name = "type")
    val type: String,

    @Json(name = "severity")
    val severity: String, // LOW, MEDIUM, HIGH, CRITICAL

    @Json(name = "title")
    val title: String,

    @Json(name = "message")
    val message: String,

    @Json(name = "recommendation")
    val recommendation: String = "",

    @Json(name = "timestamp")
    val timestamp: String = ""
)

data class ExplanationDto(
    @Json(name = "summary")
    val summary: String,

    @Json(name = "driver_guidance")
    val driverGuidance: String
)

data class VerificationDto(
    @Json(name = "verified")
    val verified: Boolean,

    @Json(name = "issues")
    val issues: List<String> = emptyList(),

    @Json(name = "corrections")
    val corrections: List<String> = emptyList()
)

data class AgentTraceEntryDto(
    @Json(name = "agent")
    val agent: String,

    @Json(name = "status")
    val status: String, // COMPLETED, SKIPPED, FALLBACK, FAILED

    @Json(name = "summary")
    val summary: String
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

    @GET("api/rescue/nearby")
    suspend fun getNearbyPlaces(
        @Query("category") category: String,
        @Query("latitude") latitude: Double,
        @Query("longitude") longitude: Double,
        @Query("max_results") maxResults: Int = 10
    ): NearbyPlacesResponse
}
