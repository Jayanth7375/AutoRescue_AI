package com.example.model

data class ServiceCentre(
    val id: String,
    val name: String,
    val address: String,
    val latitude: Double,
    val longitude: Double,
    val rating: Double? = null,
    val reviewCount: Int? = null,
    val isOpen: Boolean? = null,
    val distanceKm: Double = 0.0,
    val placeTypes: List<String> = emptyList(),
    val priorityScore: Double = 0.0,
    val matchReason: String = "",
    val isRecommended: Boolean = false,
    val phoneNumber: String? = null,
    val websiteUri: String? = null,
    val attributions: String? = null
)
