package com.example.ui.components

import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.Directions
import androidx.compose.material.icons.outlined.Info
import androidx.compose.material.icons.outlined.Language
import androidx.compose.material.icons.outlined.LocationOn
import androidx.compose.material.icons.outlined.Phone
import androidx.compose.material.icons.outlined.Star
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.ServiceCentre
import com.example.ui.theme.*
import com.example.viewmodel.DeviceLocationState
import com.example.viewmodel.ServiceCentresUiState
import java.util.Locale

@Composable
fun NearbyServiceCentresCard(
    serviceCentresState: ServiceCentresUiState,
    locationState: DeviceLocationState,
    onRefreshClick: () -> Unit,
    modifier: Modifier = Modifier,
    isSafeToDrive: Boolean = true,
    onRequestTow: () -> Unit = {}
) {
    val context = LocalContext.current
    var safetyDialogCentre by remember { mutableStateOf<ServiceCentre?>(null) }
    var viewCentreDialogCentre by remember { mutableStateOf<ServiceCentre?>(null) }

    fun handleDirectionsClick(centre: ServiceCentre) {
        if (isSafeToDrive) {
            launchDirections(context, centre)
        } else {
            safetyDialogCentre = centre
        }
    }

    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(14.dp)
    ) {
        // Section Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Box(
                    modifier = Modifier
                        .size(36.dp)
                        .clip(CircleShape)
                        .background(PrimaryDark),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.Storefront,
                        contentDescription = "Nearby Service Centres",
                        tint = HealthyGreen,
                        modifier = Modifier.size(20.dp)
                    )
                }

                Column {
                    Text(
                        text = "Nearby Service Centres",
                        style = MaterialTheme.typography.titleMedium,
                        color = CharcoalText,
                        fontWeight = FontWeight.Bold
                    )
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        Text(
                            text = if (locationState.locationAddress != null) {
                                "Around ${locationState.locationAddress}"
                            } else {
                                "Automotive repair & service hubs"
                            },
                            fontSize = 11.sp,
                            color = CharcoalMuted,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                            modifier = Modifier.weight(1f, fill = false)
                        )

                        if (locationState.isSimulatedLocation) {
                            Box(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(4.dp))
                                    .background(WarningAmberBg)
                                    .border(1.dp, WarningAmberDark.copy(alpha = 0.5f), RoundedCornerShape(4.dp))
                                    .padding(horizontal = 5.dp, vertical = 2.dp)
                            ) {
                                Text(
                                    text = "Simulated location",
                                    fontSize = 9.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = WarningAmberDark
                                )
                            }
                        }
                    }
                }
            }

            IconButton(
                onClick = onRefreshClick,
                modifier = Modifier
                    .size(36.dp)
                    .clip(CircleShape)
                    .background(CardBorderLight)
                    .testTag("refresh_service_centres_button")
            ) {
                Icon(
                    imageVector = Icons.Default.Refresh,
                    contentDescription = "Refresh",
                    tint = PrimaryDark,
                    modifier = Modifier.size(18.dp)
                )
            }
        }

        // State switcher: Loading / Error / Empty / Success
        when {
            serviceCentresState.isLoading -> {
                // Loading State
                Card(
                    shape = RoundedCornerShape(18.dp),
                    colors = CardDefaults.cardColors(containerColor = CardSurfaceLight),
                    border = androidx.compose.foundation.BorderStroke(1.dp, CardBorderLight),
                    modifier = Modifier
                        .fillMaxWidth()
                        .testTag("service_centres_loading_card")
                ) {
                    Row(
                        modifier = Modifier
                            .padding(20.dp)
                            .fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        CircularProgressIndicator(
                            color = PrimaryDark,
                            strokeWidth = 3.dp,
                            modifier = Modifier.size(28.dp)
                        )
                        Column {
                            Text(
                                text = "Searching Nearby Businesses...",
                                fontWeight = FontWeight.Bold,
                                fontSize = 14.sp,
                                color = CharcoalText
                            )
                            Text(
                                text = "Querying Google Places SDK around your location",
                                fontSize = 12.sp,
                                color = CharcoalMuted
                            )
                        }
                    }
                }
            }

            serviceCentresState.errorMessage != null || serviceCentresState.errorType != null -> {
                val errorType = serviceCentresState.errorType
                val errorTitle = when (errorType) {
                    is com.example.repository.ServiceCentreErrorType.PermissionDenied -> "Location Permission Denied"
                    is com.example.repository.ServiceCentreErrorType.GpsUnavailable -> "GPS Location Unavailable"
                    is com.example.repository.ServiceCentreErrorType.PlacesKeyMissing -> "Places API Key Missing"
                    is com.example.repository.ServiceCentreErrorType.PlacesRequestFailed -> "Places API Request Failed"
                    is com.example.repository.ServiceCentreErrorType.InvalidPlaceType -> "Invalid Place Type Filter"
                    is com.example.repository.ServiceCentreErrorType.ZeroResults -> "No Service Centres Found"
                    is com.example.repository.ServiceCentreErrorType.LocationFailure -> "Location Acquisition Failed"
                    is com.example.repository.ServiceCentreErrorType.NetworkUnavailable -> "Network Unavailable"
                    else -> "Unable to Fetch Service Centres"
                }

                val errorIcon = when (errorType) {
                    is com.example.repository.ServiceCentreErrorType.PermissionDenied -> Icons.Default.LocationOff
                    is com.example.repository.ServiceCentreErrorType.GpsUnavailable -> Icons.Default.GpsOff
                    is com.example.repository.ServiceCentreErrorType.PlacesKeyMissing -> Icons.Default.KeyOff
                    is com.example.repository.ServiceCentreErrorType.PlacesRequestFailed -> Icons.Default.CloudOff
                    is com.example.repository.ServiceCentreErrorType.InvalidPlaceType -> Icons.Default.FilterListOff
                    is com.example.repository.ServiceCentreErrorType.ZeroResults -> Icons.Default.SearchOff
                    is com.example.repository.ServiceCentreErrorType.LocationFailure -> Icons.Default.LocationDisabled
                    is com.example.repository.ServiceCentreErrorType.NetworkUnavailable -> Icons.Default.WifiOff
                    else -> Icons.Default.ErrorOutline
                }

                val buttonLabel = when (errorType) {
                    is com.example.repository.ServiceCentreErrorType.PermissionDenied -> "Retry Location Permission"
                    is com.example.repository.ServiceCentreErrorType.GpsUnavailable -> "Retry Location"
                    is com.example.repository.ServiceCentreErrorType.PlacesKeyMissing -> "Retry Key Check"
                    is com.example.repository.ServiceCentreErrorType.NetworkUnavailable -> "Retry Connection"
                    else -> "Retry Search"
                }

                Card(
                    shape = RoundedCornerShape(18.dp),
                    colors = CardDefaults.cardColors(containerColor = WarningAmberBg),
                    border = androidx.compose.foundation.BorderStroke(1.dp, WarningAmberDark.copy(alpha = 0.4f)),
                    modifier = Modifier
                        .fillMaxWidth()
                        .testTag("service_centres_error_card")
                ) {
                    Column(
                        modifier = Modifier.padding(18.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Icon(
                                imageVector = errorIcon,
                                contentDescription = "Error Icon",
                                tint = WarningAmberDark,
                                modifier = Modifier.size(20.dp)
                            )
                            Text(
                                text = errorTitle,
                                fontWeight = FontWeight.Bold,
                                color = WarningAmberDark,
                                fontSize = 14.sp
                            )
                        }

                        Text(
                            text = serviceCentresState.errorMessage ?: "An error occurred while fetching nearby automotive service centres.",
                            fontSize = 12.sp,
                            color = CharcoalText.copy(alpha = 0.85f)
                        )

                        Button(
                            onClick = onRefreshClick,
                            colors = ButtonDefaults.buttonColors(containerColor = WarningAmberDark),
                            shape = RoundedCornerShape(10.dp),
                            contentPadding = PaddingValues(horizontal = 14.dp, vertical = 8.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Refresh,
                                contentDescription = null,
                                modifier = Modifier.size(14.dp)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(text = buttonLabel, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }

            serviceCentresState.serviceCentres.isEmpty() -> {
                // Empty State
                Card(
                    shape = RoundedCornerShape(18.dp),
                    colors = CardDefaults.cardColors(containerColor = CardSurfaceLight),
                    border = androidx.compose.foundation.BorderStroke(1.dp, CardBorderLight),
                    modifier = Modifier
                        .fillMaxWidth()
                        .testTag("service_centres_empty_card")
                ) {
                    Column(
                        modifier = Modifier
                            .padding(24.dp)
                            .fillMaxWidth(),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.SearchOff,
                            contentDescription = "Empty",
                            tint = CharcoalMuted,
                            modifier = Modifier.size(36.dp)
                        )
                        Text(
                            text = "No Service Centres Found",
                            fontWeight = FontWeight.Bold,
                            fontSize = 15.sp,
                            color = CharcoalText
                        )
                        Text(
                            text = "No automotive repair or service businesses were found in your immediate search radius.",
                            fontSize = 12.sp,
                            color = CharcoalMuted,
                            modifier = Modifier.padding(horizontal = 12.dp)
                        )
                        Button(
                            onClick = onRefreshClick,
                            colors = ButtonDefaults.buttonColors(containerColor = PrimaryDark),
                            shape = RoundedCornerShape(12.dp),
                            contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp)
                        ) {
                            Text(text = "Refresh Location & Search", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }

            else -> {
                // Success State: Top 10 Service Centres sorted by priorityScore descending
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text(
                        text = "Found ${serviceCentresState.serviceCentres.size} relevant automotive centres (sorted by priority)",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = HealthyGreenDark
                    )

                    serviceCentresState.serviceCentres.forEachIndexed { index, centre ->
                        ServiceCentreItemCard(
                            index = index + 1,
                            centre = centre,
                            onDirectionsClick = { handleDirectionsClick(centre) },
                            onViewCentreClick = { viewCentreDialogCentre = centre }
                        )
                    }

                    // Google Places Attribution
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(top = 4.dp, bottom = 4.dp),
                        horizontalArrangement = Arrangement.Center,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Outlined.Info,
                            contentDescription = "Google Places Attribution",
                            tint = CharcoalMuted,
                            modifier = Modifier.size(13.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = "Search results provided by Google Places",
                            fontSize = 11.sp,
                            color = CharcoalMuted
                        )
                    }
                }
            }
        }
    }

    // Safety Warning Dialog for unsafe-to-drive vehicles
    if (safetyDialogCentre != null) {
        val centre = safetyDialogCentre!!
        AlertDialog(
            onDismissRequest = { safetyDialogCentre = null },
            icon = {
                Box(
                    modifier = Modifier
                        .size(44.dp)
                        .clip(CircleShape)
                        .background(CriticalRedBg),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.Warning,
                        contentDescription = "Warning",
                        tint = CriticalRedDark,
                        modifier = Modifier.size(24.dp)
                    )
                }
            },
            title = {
                Text(
                    text = "Your vehicle is not safe to drive.",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    color = CharcoalText
                )
            },
            text = {
                Text(
                    text = "Request roadside assistance instead of driving to the service centre.",
                    fontSize = 13.sp,
                    color = CharcoalMuted
                )
            },
            confirmButton = {
                Button(
                    onClick = {
                        safetyDialogCentre = null
                        onRequestTow()
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = CriticalRedDark, contentColor = Color.White),
                    shape = RoundedCornerShape(10.dp)
                ) {
                    Text("Request Tow", fontWeight = FontWeight.Bold, fontSize = 13.sp)
                }
            },
            dismissButton = {
                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    OutlinedButton(
                        onClick = {
                            val target = safetyDialogCentre
                            safetyDialogCentre = null
                            viewCentreDialogCentre = target
                        },
                        shape = RoundedCornerShape(10.dp)
                    ) {
                        Text("View Centre", fontWeight = FontWeight.Bold, fontSize = 12.sp)
                    }
                    TextButton(
                        onClick = { safetyDialogCentre = null }
                    ) {
                        Text("Cancel", color = CharcoalMuted, fontSize = 12.sp)
                    }
                }
            },
            containerColor = CardSurfaceLight,
            shape = RoundedCornerShape(20.dp)
        )
    }

    // View Centre Details Dialog
    if (viewCentreDialogCentre != null) {
        val centre = viewCentreDialogCentre!!
        ViewCentreDetailDialog(
            centre = centre,
            onDismiss = { viewCentreDialogCentre = null },
            onDirectionsClick = {
                viewCentreDialogCentre = null
                handleDirectionsClick(centre)
            }
        )
    }
}

@Composable
fun ServiceCentreItemCard(
    index: Int,
    centre: ServiceCentre,
    onDirectionsClick: () -> Unit,
    onViewCentreClick: () -> Unit
) {
    val context = LocalContext.current

    Card(
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = CardSurfaceLight),
        border = androidx.compose.foundation.BorderStroke(
            width = if (centre.isRecommended) 2.dp else 1.dp,
            color = if (centre.isRecommended) HealthyGreenDark else CardBorderLight
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = if (centre.isRecommended) 4.dp else 2.dp),
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onViewCentreClick() }
            .testTag("service_centre_item_$index")
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            // Row 1: Index badge, Name, Recommended tag & Priority Score
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Row(
                    modifier = Modifier.weight(1f),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .size(26.dp)
                            .clip(CircleShape)
                            .background(if (centre.isRecommended) HealthyGreenDark else PrimaryDark),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "#$index",
                            color = if (centre.isRecommended) Color.White else HealthyGreen,
                            fontWeight = FontWeight.Bold,
                            fontSize = 11.sp
                        )
                    }

                    Text(
                        text = centre.name,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = CharcoalText,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                        modifier = Modifier.weight(1f, fill = false)
                    )

                    if (centre.isRecommended) {
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(6.dp))
                                .background(PrimaryDark)
                                .padding(horizontal = 7.dp, vertical = 3.dp)
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(3.dp)
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Verified,
                                    contentDescription = "Recommended",
                                    tint = HealthyGreen,
                                    modifier = Modifier.size(11.dp)
                                )
                                Text(
                                    text = "Recommended",
                                    fontSize = 10.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = HealthyGreen
                                )
                            }
                        }
                    }
                }

                Spacer(modifier = Modifier.width(6.dp))

                // Priority score tag (formatted e.g. 91/100)
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(8.dp))
                        .background(if (centre.isRecommended) HealthyGreenBg else CardBorderLight.copy(alpha = 0.5f))
                        .padding(horizontal = 8.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = "${centre.priorityScore.toInt()}/100",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        color = if (centre.isRecommended) HealthyGreenDark else PrimaryDark
                    )
                }
            }

            // Recommendation reason string (e.g. Open now • 1.8 km • 4.6 stars • Relevant for tyre repair)
            if (centre.matchReason.isNotBlank()) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(8.dp))
                        .background(if (centre.isRecommended) HealthyGreenBg else BackgroundLight)
                        .border(
                            1.dp,
                            if (centre.isRecommended) HealthyGreenDark.copy(alpha = 0.3f) else CardBorderLight,
                            RoundedCornerShape(8.dp)
                        )
                        .padding(horizontal = 10.dp, vertical = 6.dp)
                ) {
                    Text(
                        text = centre.matchReason,
                        fontSize = 11.sp,
                        fontWeight = if (centre.isRecommended) FontWeight.Bold else FontWeight.Medium,
                        color = if (centre.isRecommended) HealthyGreenDark else CharcoalText
                    )
                }
            }

            // Address with pin icon
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                Icon(
                    imageVector = Icons.Outlined.LocationOn,
                    contentDescription = null,
                    tint = CharcoalMuted,
                    modifier = Modifier.size(16.dp)
                )
                Text(
                    text = centre.address,
                    fontSize = 12.sp,
                    color = CharcoalMuted,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
            }

            HorizontalDivider(color = CardBorderLight.copy(alpha = 0.6f))

            // Rating, Review count, Distance, Open/Closed Badge
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(10.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Rating & Reviews
                    if (centre.rating != null) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(3.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Star,
                                contentDescription = "Rating",
                                tint = Color(0xFFFFB800),
                                modifier = Modifier.size(16.dp)
                            )
                            Text(
                                text = "${centre.rating}",
                                fontWeight = FontWeight.Bold,
                                fontSize = 13.sp,
                                color = CharcoalText
                            )
                            if (centre.reviewCount != null) {
                                Text(
                                    text = "(${centre.reviewCount} reviews)",
                                    fontSize = 11.sp,
                                    color = CharcoalMuted
                                )
                            }
                        }
                    }

                    // Distance
                    Text(
                        text = "${String.format(Locale.US, "%.1f", centre.distanceKm)} km away",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = PrimaryDark
                    )
                }

                // Opening State
                if (centre.isOpen != null) {
                    val isOpen = centre.isOpen
                    val (statusBg, statusFg, statusText) = if (isOpen) {
                        Triple(HealthyGreenBg, HealthyGreenDark, "Open Now")
                    } else {
                        Triple(Color(0xFFFFEBEE), CriticalRedDark, "Closed")
                    }

                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(6.dp))
                            .background(statusBg)
                            .padding(horizontal = 8.dp, vertical = 3.dp)
                    ) {
                        Text(
                            text = statusText,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            color = statusFg
                        )
                    }
                }
            }

            // Action Row: Call Button (if phone exists) & Directions Button
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // View Details link / Place types
                Text(
                    text = "View Details",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = PrimaryDark,
                    modifier = Modifier
                        .clickable { onViewCentreClick() }
                        .padding(vertical = 4.dp)
                )

                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // CALL BUTTON: Shown ONLY if Places result provides a phone number
                    if (!centre.phoneNumber.isNullOrBlank()) {
                        OutlinedButton(
                            onClick = {
                                val dialIntent = Intent(Intent.ACTION_DIAL, Uri.parse("tel:${centre.phoneNumber}"))
                                try {
                                    context.startActivity(dialIntent)
                                } catch (e: Exception) {
                                    e.printStackTrace()
                                }
                            },
                            shape = RoundedCornerShape(10.dp),
                            border = androidx.compose.foundation.BorderStroke(1.dp, PrimaryDark),
                            contentPadding = PaddingValues(horizontal = 10.dp, vertical = 6.dp),
                            modifier = Modifier.height(34.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Outlined.Phone,
                                contentDescription = "Call",
                                tint = PrimaryDark,
                                modifier = Modifier.size(13.dp)
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(
                                text = "Call",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = PrimaryDark
                            )
                        }
                    }

                    // DIRECTIONS BUTTON
                    Button(
                        onClick = onDirectionsClick,
                        colors = ButtonDefaults.buttonColors(
                            containerColor = PrimaryDark,
                            contentColor = HealthyGreen
                        ),
                        shape = RoundedCornerShape(10.dp),
                        contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp),
                        modifier = Modifier.height(34.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Outlined.Directions,
                            contentDescription = "Navigate",
                            tint = HealthyGreen,
                            modifier = Modifier.size(14.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = "Directions",
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun ViewCentreDetailDialog(
    centre: ServiceCentre,
    onDismiss: () -> Unit,
    onDirectionsClick: () -> Unit
) {
    val context = LocalContext.current

    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        text = centre.name,
                        fontSize = 17.sp,
                        fontWeight = FontWeight.Bold,
                        color = CharcoalText,
                        modifier = Modifier.weight(1f)
                    )
                    if (centre.isRecommended) {
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(6.dp))
                                .background(HealthyGreenBg)
                                .border(1.dp, HealthyGreenDark.copy(alpha = 0.4f), RoundedCornerShape(6.dp))
                                .padding(horizontal = 6.dp, vertical = 2.dp)
                        ) {
                            Text(
                                text = "Recommended",
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold,
                                color = HealthyGreenDark
                            )
                        }
                    }
                }
            }
        },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                // Address
                Row(
                    verticalAlignment = Alignment.Top,
                    horizontalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    Icon(
                        imageVector = Icons.Outlined.LocationOn,
                        contentDescription = "Address",
                        tint = CharcoalMuted,
                        modifier = Modifier.size(16.dp)
                    )
                    Text(
                        text = centre.address,
                        fontSize = 13.sp,
                        color = CharcoalText
                    )
                }

                HorizontalDivider(color = CardBorderLight)

                // Rating & Review Count
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Star,
                            contentDescription = "Rating",
                            tint = Color(0xFFFFB800),
                            modifier = Modifier.size(16.dp)
                        )
                        Text(
                            text = if (centre.rating != null) "${centre.rating} ★" else "Rating N/A",
                            fontWeight = FontWeight.Bold,
                            fontSize = 13.sp,
                            color = CharcoalText
                        )
                        if (centre.reviewCount != null) {
                            Text(
                                text = "(${centre.reviewCount} reviews)",
                                fontSize = 12.sp,
                                color = CharcoalMuted
                            )
                        }
                    }

                    Text(
                        text = "${String.format(Locale.US, "%.1f", centre.distanceKm)} km away",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                        color = PrimaryDark
                    )
                }

                // Opening state
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    val isOpen = centre.isOpen
                    val statusText = when (isOpen) {
                        true -> "Open Now"
                        false -> "Closed"
                        null -> "Opening Hours Not Provided"
                    }
                    val statusColor = when (isOpen) {
                        true -> HealthyGreenDark
                        false -> CriticalRedDark
                        null -> CharcoalMuted
                    }

                    Text(
                        text = "Status: $statusText",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = statusColor
                    )
                }

                // Priority Score & Reason
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(8.dp))
                        .background(BackgroundLight)
                        .padding(10.dp)
                ) {
                    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Text(
                            text = "Priority Score: ${centre.priorityScore.toInt()}/100",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            color = PrimaryDark
                        )
                        if (centre.matchReason.isNotBlank()) {
                            Text(
                                text = centre.matchReason,
                                fontSize = 11.sp,
                                color = CharcoalMuted
                            )
                        }
                    }
                }

                // Phone Action (if available)
                if (!centre.phoneNumber.isNullOrBlank()) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Outlined.Phone,
                                contentDescription = "Phone",
                                tint = PrimaryDark,
                                modifier = Modifier.size(16.dp)
                            )
                            Text(
                                text = centre.phoneNumber,
                                fontSize = 13.sp,
                                fontWeight = FontWeight.Medium,
                                color = CharcoalText
                            )
                        }

                        Button(
                            onClick = {
                                val intent = Intent(Intent.ACTION_DIAL, Uri.parse("tel:${centre.phoneNumber}"))
                                try { context.startActivity(intent) } catch (e: Exception) { e.printStackTrace() }
                            },
                            shape = RoundedCornerShape(8.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = PrimaryDark),
                            contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp),
                            modifier = Modifier.height(32.dp)
                        ) {
                            Text("Call", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }

                // Website Action (if available)
                if (!centre.websiteUri.isNullOrBlank()) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(6.dp),
                            modifier = Modifier.weight(1f)
                        ) {
                            Icon(
                                imageVector = Icons.Outlined.Language,
                                contentDescription = "Website",
                                tint = PrimaryDark,
                                modifier = Modifier.size(16.dp)
                            )
                            Text(
                                text = centre.websiteUri,
                                fontSize = 12.sp,
                                color = PrimaryDark,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis
                            )
                        }

                        OutlinedButton(
                            onClick = {
                                val intent = Intent(Intent.ACTION_VIEW, Uri.parse(centre.websiteUri))
                                try { context.startActivity(intent) } catch (e: Exception) { e.printStackTrace() }
                            },
                            shape = RoundedCornerShape(8.dp),
                            contentPadding = PaddingValues(horizontal = 10.dp, vertical = 6.dp),
                            modifier = Modifier.height(32.dp)
                        ) {
                            Text("Visit", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }

                if (!centre.attributions.isNullOrBlank()) {
                    Text(
                        text = "Attribution: ${centre.attributions}",
                        fontSize = 10.sp,
                        color = CharcoalMuted
                    )
                }
            }
        },
        confirmButton = {
            Button(
                onClick = onDirectionsClick,
                colors = ButtonDefaults.buttonColors(containerColor = PrimaryDark, contentColor = HealthyGreen),
                shape = RoundedCornerShape(10.dp)
            ) {
                Icon(
                    imageVector = Icons.Outlined.Directions,
                    contentDescription = null,
                    modifier = Modifier.size(14.dp)
                )
                Spacer(modifier = Modifier.width(4.dp))
                Text("Directions", fontWeight = FontWeight.Bold, fontSize = 12.sp)
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Close", color = CharcoalMuted, fontSize = 12.sp)
            }
        },
        containerColor = CardSurfaceLight,
        shape = RoundedCornerShape(20.dp)
    )
}

private fun launchDirections(context: Context, centre: ServiceCentre) {
    val placeIdParam = if (centre.id.startsWith("centre_") || centre.id.startsWith("place_")) "" else "&destination_place_id=${centre.id}"
    val uriStr = "https://www.google.com/maps/dir/?api=1&destination=${centre.latitude},${centre.longitude}$placeIdParam"
    val uri = Uri.parse(uriStr)
    val mapIntent = Intent(Intent.ACTION_VIEW, uri).apply {
        setPackage("com.google.android.apps.maps")
    }
    try {
        context.startActivity(mapIntent)
    } catch (e: Exception) {
        val fallbackIntent = Intent(Intent.ACTION_VIEW, uri)
        try {
            context.startActivity(fallbackIntent)
        } catch (ex: Exception) {
            ex.printStackTrace()
        }
    }
}
