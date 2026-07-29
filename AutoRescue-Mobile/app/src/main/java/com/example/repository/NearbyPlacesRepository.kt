package com.example.repository

import android.util.Log
import com.example.model.NearbyPlace
import com.example.model.NearbyPlacesResponse
import com.example.network.AutoRescueApi
import com.example.network.NetworkConfig

class NearbyPlacesRepository(
    private val api: AutoRescueApi = NetworkConfig.autoRescueApi
) {

    suspend fun getEvChargingStations(
        latitude: Double,
        longitude: Double,
        maxResults: Int = 10
    ): Result<NearbyPlacesResponse> {
        return try {
            Log.d("NearbyPlacesRepository", "Fetching EV charging stations at $latitude, $longitude")
            val response = api.getNearbyPlaces(
                category = "EV_CHARGING",
                latitude = latitude,
                longitude = longitude,
                maxResults = maxResults
            )
            Log.d("NearbyPlacesRepository", "Found ${response.count} EV charging stations")
            Result.success(response)
        } catch (e: Exception) {
            Log.e("NearbyPlacesRepository", "Error fetching EV charging stations: ${e.message}", e)
            Result.failure(e)
        }
    }

    suspend fun getBatteryServices(
        latitude: Double,
        longitude: Double,
        maxResults: Int = 10
    ): Result<NearbyPlacesResponse> {
        return try {
            Log.d("NearbyPlacesRepository", "Fetching battery services at $latitude, $longitude")
            val response = api.getNearbyPlaces(
                category = "BATTERY_SERVICE",
                latitude = latitude,
                longitude = longitude,
                maxResults = maxResults
            )
            Log.d("NearbyPlacesRepository", "Found ${response.count} battery services")
            Result.success(response)
        } catch (e: Exception) {
            Log.e("NearbyPlacesRepository", "Error fetching battery services: ${e.message}", e)
            Result.failure(e)
        }
    }

    suspend fun getFuelStations(
        latitude: Double,
        longitude: Double,
        maxResults: Int = 10
    ): Result<NearbyPlacesResponse> {
        return try {
            Log.d("NearbyPlacesRepository", "Fetching fuel stations at $latitude, $longitude")
            val response = api.getNearbyPlaces(
                category = "FUEL_STATION",
                latitude = latitude,
                longitude = longitude,
                maxResults = maxResults
            )
            Log.d("NearbyPlacesRepository", "Found ${response.count} fuel stations")
            Result.success(response)
        } catch (e: Exception) {
            Log.e("NearbyPlacesRepository", "Error fetching fuel stations: ${e.message}", e)
            Result.failure(e)
        }
    }

    suspend fun getHospitals(
        latitude: Double,
        longitude: Double,
        maxResults: Int = 10
    ): Result<NearbyPlacesResponse> {
        return try {
            Log.d("NearbyPlacesRepository", "Fetching hospitals at $latitude, $longitude")
            val response = api.getNearbyPlaces(
                category = "HOSPITAL",
                latitude = latitude,
                longitude = longitude,
                maxResults = maxResults
            )
            Log.d("NearbyPlacesRepository", "Found ${response.count} hospitals")
            Result.success(response)
        } catch (e: Exception) {
            Log.e("NearbyPlacesRepository", "Error fetching hospitals: ${e.message}", e)
            Result.failure(e)
        }
    }
}
