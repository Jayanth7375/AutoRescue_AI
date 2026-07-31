package com.example.utils

import android.content.Context
import android.content.Intent
import android.net.Uri

/**
 * Open Google Maps with service centre coordinates.
 * Prefers Google Maps app, falls back to web search.
 */
fun openServiceCentreInMaps(
    context: Context,
    latitude: Double,
    longitude: Double,
    name: String
) {
    val geoUri = Uri.parse(
        "geo:$latitude,$longitude?q=$latitude,$longitude(${Uri.encode(name)})"
    )

    val mapsIntent = Intent(Intent.ACTION_VIEW, geoUri).apply {
        setPackage("com.google.android.apps.maps")
    }

    try {
        context.startActivity(mapsIntent)
    } catch (e: Exception) {
        // Fall back to web-based maps
        val fallbackUri = Uri.parse(
            "https://www.google.com/maps/search/?api=1&query=$latitude,$longitude"
        )
        val fallbackIntent = Intent(Intent.ACTION_VIEW, fallbackUri)
        context.startActivity(fallbackIntent)
    }
}

/**
 * Open phone dialer with tow service number pre-filled.
 * Uses ACTION_DIAL which does not require CALL_PHONE permission.
 */
fun openTowDialer(context: Context) {
    val dialIntent = Intent(
        Intent.ACTION_DIAL,
        Uri.parse("tel:7867896369")
    )
    context.startActivity(dialIntent)
}
