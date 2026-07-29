package com.example.repository

import android.annotation.SuppressLint
import android.content.Context
import android.location.Geocoder
import android.location.Location
import android.os.Build
import com.google.android.gms.location.CurrentLocationRequest
import com.google.android.gms.location.FusedLocationProviderClient
import com.google.android.gms.location.LocationServices
import com.google.android.gms.location.Priority
import com.google.android.gms.tasks.CancellationTokenSource
import kotlinx.coroutines.suspendCancellableCoroutine
import java.util.Locale
import kotlin.coroutines.resume

data class LocationData(
    val latitude: Double,
    val longitude: Double,
    val accuracy: Float?,
    val locationName: String,
    val isSimulatedLocation: Boolean
)

sealed class LocationResult {
    data class Success(val locationData: LocationData) : LocationResult()
    data class Error(val message: String) : LocationResult()
    object LocationUnavailable : LocationResult()
}

class LocationRepository(private val context: Context) {

    private val fusedLocationClient: FusedLocationProviderClient =
        LocationServices.getFusedLocationProviderClient(context)

    fun isEmulator(): Boolean {
        return (Build.FINGERPRINT.startsWith("generic")
                || Build.FINGERPRINT.startsWith("unknown")
                || Build.MODEL.contains("google_sdk")
                || Build.MODEL.contains("Emulator")
                || Build.MODEL.contains("Android SDK built for x86")
                || Build.MANUFACTURER.contains("Genymotion")
                || (Build.BRAND.startsWith("generic") && Build.DEVICE.startsWith("generic"))
                || "google_sdk" == Build.PRODUCT
                || Build.HARDWARE.contains("goldfish")
                || Build.HARDWARE.contains("ranchu"))
    }

    @SuppressLint("MissingPermission")
    suspend fun getCurrentLocation(): LocationResult = suspendCancellableCoroutine { continuation ->
        val cancellationTokenSource = CancellationTokenSource()

        val currentLocationRequest = CurrentLocationRequest.Builder()
            .setPriority(Priority.PRIORITY_HIGH_ACCURACY)
            .setDurationMillis(10000)
            .build()

        fusedLocationClient.getCurrentLocation(currentLocationRequest, cancellationTokenSource.token)
            .addOnSuccessListener { location: Location? ->
                if (location != null) {
                    val isSimulated = isEmulator() || (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && location.isMock) || location.isFromMockProvider
                    val name = getAddressFromLocation(context, location.latitude, location.longitude)
                    val data = LocationData(
                        latitude = location.latitude,
                        longitude = location.longitude,
                        accuracy = if (location.hasAccuracy()) location.accuracy else null,
                        locationName = name,
                        isSimulatedLocation = isSimulated
                    )
                    if (continuation.isActive) continuation.resume(LocationResult.Success(data))
                } else {
                    // Try lastLocation as fallback
                    fusedLocationClient.lastLocation
                        .addOnSuccessListener { lastLoc: Location? ->
                            if (lastLoc != null) {
                                val isSimulated = isEmulator() || (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && lastLoc.isMock) || lastLoc.isFromMockProvider
                                val name = getAddressFromLocation(context, lastLoc.latitude, lastLoc.longitude)
                                val data = LocationData(
                                    latitude = lastLoc.latitude,
                                    longitude = lastLoc.longitude,
                                    accuracy = if (lastLoc.hasAccuracy()) lastLoc.accuracy else null,
                                    locationName = name,
                                    isSimulatedLocation = isSimulated
                                )
                                if (continuation.isActive) continuation.resume(LocationResult.Success(data))
                            } else {
                                if (continuation.isActive) continuation.resume(LocationResult.LocationUnavailable)
                            }
                        }
                        .addOnFailureListener {
                            if (continuation.isActive) continuation.resume(LocationResult.LocationUnavailable)
                        }
                }
            }
            .addOnFailureListener { exception ->
                // Fallback to lastLocation
                fusedLocationClient.lastLocation
                    .addOnSuccessListener { lastLoc: Location? ->
                        if (lastLoc != null) {
                            val isSimulated = isEmulator() || (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && lastLoc.isMock) || lastLoc.isFromMockProvider
                            val name = getAddressFromLocation(context, lastLoc.latitude, lastLoc.longitude)
                            val data = LocationData(
                                latitude = lastLoc.latitude,
                                longitude = lastLoc.longitude,
                                accuracy = if (lastLoc.hasAccuracy()) lastLoc.accuracy else null,
                                locationName = name,
                                isSimulatedLocation = isSimulated
                            )
                            if (continuation.isActive) continuation.resume(LocationResult.Success(data))
                        } else {
                            if (continuation.isActive) continuation.resume(LocationResult.Error(exception.localizedMessage ?: "Failed to get location"))
                        }
                    }
                    .addOnFailureListener {
                        if (continuation.isActive) continuation.resume(LocationResult.Error(exception.localizedMessage ?: "Failed to get location"))
                    }
            }

        continuation.invokeOnCancellation {
            cancellationTokenSource.cancel()
        }
    }

    @Suppress("DEPRECATION")
    private fun getAddressFromLocation(context: Context, lat: Double, lng: Double): String {
        return try {
            val geocoder = Geocoder(context, Locale.getDefault())
            val addresses = geocoder.getFromLocation(lat, lng, 1)
            if (!addresses.isNullOrEmpty()) {
                val address = addresses[0]
                val locality = address.locality ?: address.subAdminArea ?: address.subLocality
                val adminArea = address.adminArea
                val country = address.countryName
                when {
                    !locality.isNullOrEmpty() && !adminArea.isNullOrEmpty() -> "$locality, $adminArea"
                    !locality.isNullOrEmpty() -> locality
                    !adminArea.isNullOrEmpty() -> adminArea
                    !country.isNullOrEmpty() -> country
                    else -> address.getAddressLine(0) ?: String.format(Locale.US, "Lat: %.4f°, Long: %.4f°", lat, lng)
                }
            } else {
                String.format(Locale.US, "Lat: %.4f°, Long: %.4f°", lat, lng)
            }
        } catch (e: Exception) {
            String.format(Locale.US, "Lat: %.4f°, Long: %.4f°", lat, lng)
        }
    }
}

