package com.example.repository

import android.util.Log
import com.example.model.VehicleTelemetry
import com.example.network.AutoRescueCheckRequest
import com.example.network.AutoRescueCheckResponse
import com.example.network.NetworkConfig

class AutoRescueRepository(
    private val autoRescueApi: com.example.network.AutoRescueApi = NetworkConfig.autoRescueApi
) {

    suspend fun runVehicleCheck(
        telemetry: VehicleTelemetry,
        latitude: Double,
        longitude: Double,
        vehicleId: String = "TN38CP7375" // Default demo vehicle
    ): Result<AutoRescueCheckResponse> {
        return try {
            Log.d("AutoRescueDebug", "6 REPOSITORY CALLED - building request")
            Log.d("AutoRescueRepository", "Starting vehicle check for $vehicleId")

            val request = AutoRescueCheckRequest(
                vehicleId = vehicleId,
                engineTemperature = telemetry.engineTemperatureC,
                batteryVoltage = telemetry.batteryVoltageV,
                // Expand single tyre pressure to all 4 wheels
                // In a real implementation, these would come from separate sensors
                frontLeftTyrePsi = telemetry.tyrePressurePsi,
                frontRightTyrePsi = telemetry.tyrePressurePsi,
                rearLeftTyrePsi = telemetry.tyrePressurePsi,
                rearRightTyrePsi = telemetry.tyrePressurePsi,
                coolantLevel = telemetry.coolantLevelPercent,
                latitude = latitude,
                longitude = longitude
            )

            Log.d(
                "AutoRescueDebug",
                """
                REQUEST:
                engine=${request.engineTemperature}°C
                battery=${request.batteryVoltage}V
                FL=${request.frontLeftTyrePsi} PSI
                FR=${request.frontRightTyrePsi} PSI
                RL=${request.rearLeftTyrePsi} PSI
                RR=${request.rearRightTyrePsi} PSI
                coolant=${request.coolantLevel}%
                lat=${request.latitude}
                lon=${request.longitude}
                """.trimIndent()
            )

            Log.d("AutoRescueDebug", "6A BASE URL = ${NetworkConfig.BASE_URL}")
            Log.d("AutoRescueDebug", "6B CALLING RETROFIT POST /api/autorescue/check")
            Log.d("AutoRescueRepository", "Sending request: $request")

            val response = autoRescueApi.runVehicleCheck(request)

            Log.d(
                "AutoRescueDebug",
                """
                BACKEND RESULT:
                status=${response.status}
                severity=${response.diagnosis.severity}
                safeToDrive=${response.diagnosis.safeToDrive}
                navigationAllowed=${response.navigationAllowed}
                issue=${response.diagnosis.issue}
                serviceCentresCount=${response.serviceCentres.size}
                rescueRequired=${response.rescue?.assistanceRequired}
                """.trimIndent()
            )
            Log.d("AutoRescueRepository", "Received response: status=${response.status}")

            Result.success(response)

        } catch (e: java.net.ConnectException) {
            Log.e("AutoRescueDebug", "NETWORK ERROR: Connection refused - ${e.message}")
            Log.e("AutoRescueRepository", "Connection refused: ${e.message}")
            Result.failure(Exception("Unable to connect to AutoRescue AI. Check that the backend is running."))

        } catch (e: java.net.SocketTimeoutException) {
            Log.e("AutoRescueDebug", "NETWORK ERROR: Request timeout - ${e.message}")
            Log.e("AutoRescueRepository", "Request timeout: ${e.message}")
            Result.failure(Exception("Vehicle check is taking longer than expected. Please retry."))

        } catch (e: retrofit2.HttpException) {
            Log.e("AutoRescueDebug", "HTTP ERROR ${e.code()}: ${e.message}")
            Log.e("AutoRescueRepository", "HTTP error ${e.code()}: ${e.message}")
            val errorMsg = when (e.code()) {
                400 -> "Invalid request data"
                422 -> "Invalid vehicle telemetry. Please check the entered sensor values."
                500 -> "Backend server error"
                503 -> "AutoRescue service is temporarily unavailable"
                else -> "HTTP error ${e.code()}"
            }
            Result.failure(Exception(errorMsg))

        } catch (e: Exception) {
            Log.e("AutoRescueDebug", "UNEXPECTED ERROR: ${e.javaClass.simpleName} - ${e.message}")
            Log.e("AutoRescueRepository", "Unexpected error: ${e.message}", e)
            Result.failure(Exception("An unexpected error occurred: ${e.message}"))
        }
    }
}
