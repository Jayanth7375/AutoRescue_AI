package com.example.repository

import android.content.Context
import android.location.Location
import android.util.Log
import com.example.BuildConfig
import com.example.engine.ServiceCentreRanker
import com.example.model.HealthStatus
import com.example.model.ServiceCentre
import com.google.android.gms.maps.model.LatLng
import com.google.android.libraries.places.api.Places
import com.google.android.libraries.places.api.model.CircularBounds
import com.google.android.libraries.places.api.model.Place
import com.google.android.libraries.places.api.net.PlacesClient
import com.google.android.libraries.places.api.net.SearchNearbyRequest
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.tasks.await
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException
import java.net.UnknownHostException
import java.util.concurrent.TimeUnit

sealed class ServiceCentreErrorType {
    object PermissionDenied : ServiceCentreErrorType()
    object GpsUnavailable : ServiceCentreErrorType()
    object PlacesKeyMissing : ServiceCentreErrorType()
    object PlacesRequestFailed : ServiceCentreErrorType()
    object InvalidPlaceType : ServiceCentreErrorType()
    object ZeroResults : ServiceCentreErrorType()
    object LocationFailure : ServiceCentreErrorType()
    object NetworkUnavailable : ServiceCentreErrorType()
    data class Custom(val message: String) : ServiceCentreErrorType()
}

sealed class ServiceCentresResult {
    data class Success(val serviceCentres: List<ServiceCentre>) : ServiceCentresResult()
    data class Error(val errorType: ServiceCentreErrorType, val message: String) : ServiceCentresResult()
}

class PlacesServiceRepository(private val context: Context) {

    private val okHttpClient = OkHttpClient.Builder()
        .connectTimeout(12, TimeUnit.SECONDS)
        .readTimeout(12, TimeUnit.SECONDS)
        .build()

    suspend fun getNearbyServiceCentres(
        latitude: Double,
        longitude: Double,
        radiusMeters: Double = 10000.0,
        issueType: String? = null,
        severity: HealthStatus? = null
    ): ServiceCentresResult = withContext(Dispatchers.IO) {
        val apiKey = try {
            BuildConfig.PLACES_API_KEY.trim()
        } catch (e: Exception) {
            ""
        }

        val isKeyLoaded = apiKey.isNotBlank() && apiKey != "PLACES_API_KEY_DEFAULT_VALUE"
        Log.d("PlacesService", "Places API key loaded: $isKeyLoaded")

        if (!isKeyLoaded) {
            return@withContext ServiceCentresResult.Error(
                ServiceCentreErrorType.PlacesKeyMissing,
                "Places API key is missing or not configured. Set PLACES_API_KEY in AI Studio secrets."
            )
        }

        var rawCentres: List<ServiceCentre> = emptyList()
        var lastException: Exception? = null

        // Try Places SDK first
        try {
            if (!Places.isInitialized()) {
                try {
                    Places.initializeWithNewPlacesApiEnabled(context.applicationContext, apiKey)
                } catch (e: Throwable) {
                    Places.initialize(context.applicationContext, apiKey)
                }
            }
            val placesClient = Places.createClient(context.applicationContext)
            rawCentres = searchViaPlacesSdk(placesClient, latitude, longitude, radiusMeters)
        } catch (e: Exception) {
            lastException = e
            Log.e("PlacesService", "Places SDK search failed: ${e.message}", e)
        }

        // Fallback to HTTP REST API if SDK returns empty or errors
        if (rawCentres.isEmpty()) {
            try {
                rawCentres = searchViaHttpApi(apiKey, latitude, longitude, radiusMeters)
            } catch (e: UnknownHostException) {
                return@withContext ServiceCentresResult.Error(
                    ServiceCentreErrorType.NetworkUnavailable,
                    "Network unavailable. Please check your internet connection."
                )
            } catch (e: IOException) {
                return@withContext ServiceCentresResult.Error(
                    ServiceCentreErrorType.NetworkUnavailable,
                    "Network connection failed when reaching Google Places."
                )
            } catch (e: Exception) {
                if (lastException == null) lastException = e
                Log.e("PlacesService", "Places HTTP REST API search failed: ${e.message}", e)
            }
        }

        if (rawCentres.isNotEmpty()) {
            val rankedResults = ServiceCentreRanker.rank(
                centres = rawCentres,
                issueType = issueType,
                severity = severity
            )
            return@withContext ServiceCentresResult.Success(rankedResults)
        }

        if (lastException != null) {
            val errMsg = lastException.localizedMessage ?: "API call error"
            val isInvalidType = errMsg.contains("9012") ||
                    errMsg.contains("Unsupported type", ignoreCase = true) ||
                    errMsg.contains("INVALID_ARGUMENT", ignoreCase = true)

            if (isInvalidType) {
                Log.e("PlacesService", "Google Places unsupported type error: $errMsg", lastException)
            }

            val errorType = if (isInvalidType) {
                ServiceCentreErrorType.InvalidPlaceType
            } else {
                ServiceCentreErrorType.PlacesRequestFailed
            }

            return@withContext ServiceCentresResult.Error(
                errorType,
                "Google Places request failed: $errMsg"
            )
        }

        return@withContext ServiceCentresResult.Error(
            ServiceCentreErrorType.ZeroResults,
            "No automotive service centres found within ${radiusMeters.toInt()} meters."
        )
    }

    private suspend fun searchViaPlacesSdk(
        placesClient: PlacesClient,
        userLat: Double,
        userLng: Double,
        radiusMeters: Double
    ): List<ServiceCentre> {
        val placeFields = listOf(
            Place.Field.ID,
            Place.Field.NAME,
            Place.Field.ADDRESS,
            Place.Field.LAT_LNG,
            Place.Field.RATING,
            Place.Field.USER_RATINGS_TOTAL,
            Place.Field.CURRENT_OPENING_HOURS,
            Place.Field.TYPES,
            Place.Field.PHONE_NUMBER,
            Place.Field.WEBSITE_URI
        )

        val center = LatLng(userLat, userLng)
        val bounds = CircularBounds.newInstance(center, radiusMeters)

        val searchNearbyRequest = SearchNearbyRequest.builder(
            bounds,
            placeFields
        )
            .setIncludedTypes(listOf("car_repair", "tire_shop", "car_dealer"))
            .setMaxResultCount(10)
            .build()

        val response = placesClient.searchNearby(searchNearbyRequest).await()
        val places = response.places

        return places.mapNotNull { place ->
            val placeId = place.id ?: return@mapNotNull null
            val name = place.name ?: "Automotive Service Centre"
            val address = place.address ?: "Nearby Location"
            val latLng = place.latLng
            val lat = latLng?.latitude ?: userLat
            val lng = latLng?.longitude ?: userLng

            val distanceKm = calculateDistanceKm(userLat, userLng, lat, lng)
            val rating = place.rating
            val reviewCount = place.userRatingsTotal
            val isOpen = place.isOpen
            val types = place.types?.map { it.name } ?: listOf("car_repair")
            val phone = place.phoneNumber
            val website = place.websiteUri?.toString()

            ServiceCentre(
                id = placeId,
                name = name,
                address = address,
                latitude = lat,
                longitude = lng,
                rating = rating,
                reviewCount = reviewCount,
                isOpen = isOpen,
                distanceKm = distanceKm,
                placeTypes = types,
                phoneNumber = phone,
                websiteUri = website
            )
        }
    }

    private fun searchViaHttpApi(
        apiKey: String,
        userLat: Double,
        userLng: Double,
        radiusMeters: Double
    ): List<ServiceCentre> {
        val resultsList = mutableListOf<ServiceCentre>()

        // 1. Places API New v1 (searchNearby)
        try {
            val url = "https://places.googleapis.com/v1/places:searchNearby"
            val jsonBody = JSONObject().apply {
                put("includedTypes", org.json.JSONArray(listOf("car_repair", "tire_shop", "car_dealer")))
                put("maxResultCount", 10)
                put("locationRestriction", JSONObject().apply {
                    put("circle", JSONObject().apply {
                        put("center", JSONObject().apply {
                            put("latitude", userLat)
                            put("longitude", userLng)
                        })
                        put("radius", radiusMeters)
                    })
                })
            }

            val request = Request.Builder()
                .url(url)
                .addHeader("X-Goog-Api-Key", apiKey)
                .addHeader(
                    "X-Goog-FieldMask",
                    "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.currentOpeningHours,places.types,places.primaryType,places.nationalPhoneNumber,places.internationalPhoneNumber,places.websiteUri"
                )
                .post(jsonBody.toString().toRequestBody("application/json".toMediaType()))
                .build()

            val response = okHttpClient.newCall(request).execute()
            if (response.isSuccessful) {
                val respStr = response.body?.string() ?: ""
                val jsonResp = JSONObject(respStr)
                if (jsonResp.has("places")) {
                    val placesArray = jsonResp.getJSONArray("places")
                    for (i in 0 until placesArray.length()) {
                        val p = placesArray.getJSONObject(i)
                        val id = p.optString("id", "centre_$i")
                        val nameObj = p.optJSONObject("displayName")
                        val name = nameObj?.optString("text") ?: "Automotive Service"
                        val address = p.optString("formattedAddress", "Nearby")
                        val locObj = p.optJSONObject("location")
                        val lat = locObj?.optDouble("latitude") ?: userLat
                        val lng = locObj?.optDouble("longitude") ?: userLng
                        val rating = if (p.has("rating")) p.optDouble("rating") else null
                        val reviewCount = if (p.has("userRatingCount")) p.optInt("userRatingCount") else null

                        val isOpen = if (p.has("currentOpeningHours")) {
                            p.optJSONObject("currentOpeningHours")?.optBoolean("openNow")
                        } else null

                        val phone = when {
                            p.has("nationalPhoneNumber") -> p.optString("nationalPhoneNumber")
                            p.has("internationalPhoneNumber") -> p.optString("internationalPhoneNumber")
                            else -> null
                        }
                        val website = if (p.has("websiteUri")) p.optString("websiteUri") else null

                        val types = mutableListOf<String>()
                        if (p.has("types")) {
                            val typesArr = p.getJSONArray("types")
                            for (j in 0 until typesArr.length()) {
                                types.add(typesArr.getString(j))
                            }
                        }

                        val distanceKm = calculateDistanceKm(userLat, userLng, lat, lng)
                        val priorityScore = calculatePriorityScore(rating, reviewCount, isOpen, distanceKm)

                        resultsList.add(
                            ServiceCentre(
                                id = id,
                                name = name,
                                address = address,
                                latitude = lat,
                                longitude = lng,
                                rating = rating,
                                reviewCount = reviewCount,
                                isOpen = isOpen,
                                distanceKm = distanceKm,
                                placeTypes = types,
                                priorityScore = priorityScore,
                                phoneNumber = phone,
                                websiteUri = website
                            )
                        )
                    }
                }
            } else {
                val errBody = response.body?.string() ?: ""
                Log.e("PlacesService", "HTTP searchNearby error response (${response.code}): $errBody")
                if (errBody.contains("9012") || errBody.contains("Unsupported type", ignoreCase = true)) {
                    throw IOException("Places API error: 9012 Unsupported types in searchNearby request")
                }
            }
        } catch (e: Exception) {
            Log.e("PlacesService", "HTTP searchNearby exception: ${e.message}", e)
        }

        if (resultsList.isNotEmpty()) {
            return resultsList.sortedByDescending { it.priorityScore }.take(10)
        }

        // 2. Legacy fallback
        try {
            val legacyUrl = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=$userLat,$userLng&radius=${radiusMeters.toInt()}&type=car_repair&key=$apiKey"
            val request = Request.Builder().url(legacyUrl).get().build()
            val response = okHttpClient.newCall(request).execute()
            if (response.isSuccessful) {
                val respStr = response.body?.string() ?: ""
                val jsonResp = JSONObject(respStr)
                if (jsonResp.has("results")) {
                    val resultsArray = jsonResp.getJSONArray("results")
                    for (i in 0 until resultsArray.length()) {
                        val p = resultsArray.getJSONObject(i)
                        val id = p.optString("place_id", "place_$i")
                        val name = p.optString("name", "Service Centre")
                        val address = p.optString("vicinity", "Nearby Location")
                        val geometry = p.optJSONObject("geometry")
                        val location = geometry?.optJSONObject("location")
                        val lat = location?.optDouble("lat") ?: userLat
                        val lng = location?.optDouble("lng") ?: userLng
                        val rating = if (p.has("rating")) p.optDouble("rating") else null
                        val reviewCount = if (p.has("user_ratings_total")) p.optInt("user_ratings_total") else null
                        val isOpen = if (p.has("opening_hours")) {
                            p.optJSONObject("opening_hours")?.optBoolean("open_now")
                        } else null

                        val types = mutableListOf<String>()
                        if (p.has("types")) {
                            val typesArr = p.getJSONArray("types")
                            for (j in 0 until typesArr.length()) {
                                types.add(typesArr.getString(j))
                            }
                        }

                        val distanceKm = calculateDistanceKm(userLat, userLng, lat, lng)
                        val priorityScore = calculatePriorityScore(rating, reviewCount, isOpen, distanceKm)

                        resultsList.add(
                            ServiceCentre(
                                id = id,
                                name = name,
                                address = address,
                                latitude = lat,
                                longitude = lng,
                                rating = rating,
                                reviewCount = reviewCount,
                                isOpen = isOpen,
                                distanceKm = distanceKm,
                                placeTypes = types,
                                priorityScore = priorityScore
                            )
                        )
                    }
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }

        return resultsList.sortedByDescending { it.priorityScore }.take(10)
    }

    private fun calculateDistanceKm(
        startLat: Double,
        startLng: Double,
        endLat: Double,
        endLng: Double
    ): Double {
        val results = FloatArray(1)
        Location.distanceBetween(startLat, startLng, endLat, endLng, results)
        val meters = results[0]
        return (meters / 100.0).toInt() / 10.0 // Rounded to 1 decimal place
    }

    private fun calculatePriorityScore(
        rating: Double?,
        reviewCount: Int?,
        isOpen: Boolean?,
        distanceKm: Double
    ): Double {
        val r = rating ?: 3.8
        val openBonus = if (isOpen == true) 25.0 else 0.0
        val ratingPart = r * 12.0
        val reviewPart = ((reviewCount ?: 0) / 20.0).coerceAtMost(15.0)
        val distancePenalty = (distanceKm * 2.5).coerceAtMost(40.0)
        val total = ratingPart + openBonus + reviewPart - distancePenalty
        return ((total * 10).toInt() / 10.0).coerceAtLeast(0.0)
    }
}
