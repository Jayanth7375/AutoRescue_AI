package com.example.model

data class VehicleTelemetry(
    val engineTemperatureC: Double,
    val batteryVoltageV: Double,
    val tyrePressurePsi: Double,
    val coolantLevelPercent: Double,
    val timestamp: Long = System.currentTimeMillis()
)
