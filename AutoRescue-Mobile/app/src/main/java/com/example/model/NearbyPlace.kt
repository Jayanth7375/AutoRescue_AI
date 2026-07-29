package com.example.model

import com.squareup.moshi.Json

data class NearbyPlace(
    @Json(name = "id")
    val id: String,

    @Json(name = "name")
    val name: String,

    @Json(name = "address")
    val address: String,

    @Json(name = "latitude")
    val latitude: Double,

    @Json(name = "longitude")
    val longitude: Double,

    @Json(name = "distance_km")
    val distanceKm: Double,

    @Json(name = "rating")
    val rating: Double? = null
)

data class NearbyPlacesResponse(
    @Json(name = "category")
    val category: String,

    @Json(name = "count")
    val count: Int,

    @Json(name = "places")
    val places: List<NearbyPlace>
)
