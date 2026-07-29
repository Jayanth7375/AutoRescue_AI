package com.example.repository

import com.example.model.VehicleTelemetry
import kotlinx.coroutines.delay

class TelemetryRepository {

    private var scanCount = 0

    suspend fun getLatestTelemetry(): VehicleTelemetry {
        // Simulate hardware sensor readings from OBD-II port
        delay(400)
        scanCount++

        return when (scanCount % 4) {
            1 -> VehicleTelemetry(
                engineTemperatureC = 108.0, // Warning range (106-115)
                batteryVoltageV = 12.6,    // Normal range (>=12.4)
                tyrePressurePsi = 32.0,    // Normal range (>=30)
                coolantLevelPercent = 82.0 // Normal range (>=50)
            )
            2 -> VehicleTelemetry(
                engineTemperatureC = 95.0,  // Normal range (<=105)
                batteryVoltageV = 11.8,     // Critical range (<12.0)
                tyrePressurePsi = 31.5,     // Normal range (>=30)
                coolantLevelPercent = 75.0  // Normal range (>=50)
            )
            3 -> VehicleTelemetry(
                engineTemperatureC = 92.0,  // Normal range (<=105)
                batteryVoltageV = 12.5,     // Normal range (>=12.4)
                tyrePressurePsi = 27.5,     // Warning range (25-29.9)
                coolantLevelPercent = 42.0  // Warning range (30-49)
            )
            0 -> VehicleTelemetry(
                engineTemperatureC = 94.0,  // Normal range (<=105)
                batteryVoltageV = 12.7,     // Normal range (>=12.4)
                tyrePressurePsi = 33.0,     // Normal range (>=30)
                coolantLevelPercent = 88.0  // Normal range (>=50)
            )
            else -> VehicleTelemetry(
                engineTemperatureC = 96.0,
                batteryVoltageV = 12.5,
                tyrePressurePsi = 32.0,
                coolantLevelPercent = 85.0
            )
        }
    }
}
