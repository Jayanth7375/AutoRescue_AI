package com.example.ui.screens

import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.LocationOn
import androidx.compose.material.icons.outlined.Phone
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import com.example.model.HealthStatus
import com.example.ui.components.AutoRescueHeader
import com.example.ui.components.NearbyServiceCentresCard
import com.example.ui.components.StatusBadge
import com.example.ui.theme.*
import com.example.utils.openServiceCentreInMaps
import com.example.utils.openTowDialer
import com.example.viewmodel.DiagnosticsViewModel
import com.example.viewmodel.LocationViewModel
import com.example.viewmodel.VehicleViewModel
import java.util.Locale

import androidx.lifecycle.viewmodel.compose.viewModel

@Composable
fun RescueScreen(
    vehicleViewModel: VehicleViewModel,
    diagnosticsViewModel: DiagnosticsViewModel,
    locationViewModel: LocationViewModel = viewModel(),
    onNavigateToNotifications: () -> Unit,
    onNavigateToProfile: () -> Unit
) {
    val rescueOptions by vehicleViewModel.rescueOptions.collectAsState()
    val selectedOption by vehicleViewModel.selectedRescueOption.collectAsState()
    val notifications by vehicleViewModel.notifications.collectAsState()
    val locationState by vehicleViewModel.locationState.collectAsState()
    val locationUiState by locationViewModel.uiState.collectAsState()
    val serviceCentresState by vehicleViewModel.serviceCentresState.collectAsState()

    // Backend diagnostic state
    val backendDiagnosticState by diagnosticsViewModel.diagnosticState.collectAsState()
    val backendResponse = backendDiagnosticState.backendResponse
    val backendStatus = backendResponse?.status
    val backendRescue = backendResponse?.rescue
    val navigationAllowed = backendResponse?.navigationAllowed ?: true

    val context = LocalContext.current

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val fineGranted = permissions[android.Manifest.permission.ACCESS_FINE_LOCATION] ?: false
        val coarseGranted = permissions[android.Manifest.permission.ACCESS_COARSE_LOCATION] ?: false
        if (fineGranted || coarseGranted) {
            locationViewModel.fetchLocation(context)
            vehicleViewModel.fetchLocation(context)
        } else {
            locationViewModel.onPermissionDenied()
            vehicleViewModel.setLocationPermissionDenied()
        }
    }

    LaunchedEffect(Unit) {
        val fineGranted = ContextCompat.checkSelfPermission(
            context,
            android.Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED
        val coarseGranted = ContextCompat.checkSelfPermission(
            context,
            android.Manifest.permission.ACCESS_COARSE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED

        if (fineGranted || coarseGranted) {
            locationViewModel.fetchLocation(context)
            vehicleViewModel.fetchLocation(context)
        } else {
            permissionLauncher.launch(
                arrayOf(
                    android.Manifest.permission.ACCESS_FINE_LOCATION,
                    android.Manifest.permission.ACCESS_COARSE_LOCATION
                )
            )
        }
    }

    Scaffold(
        topBar = {
            AutoRescueHeader(
                title = "Roadside Assistance",
                hasUnreadNotifications = notifications.any { !it.isRead },
                onNotificationClick = onNavigateToNotifications,
                onProfileClick = onNavigateToProfile
            )
        },
        containerColor = BackgroundLight
    ) { innerPadding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(horizontal = 20.dp),
            verticalArrangement = Arrangement.spacedBy(20.dp),
            contentPadding = PaddingValues(top = 12.dp, bottom = 28.dp)
        ) {
            // Location Banner Card
            item {
                Card(
                    shape = RoundedCornerShape(20.dp),
                    colors = CardDefaults.cardColors(containerColor = PrimaryDark),
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable {
                            val fineGranted = ContextCompat.checkSelfPermission(
                                context,
                                android.Manifest.permission.ACCESS_FINE_LOCATION
                            ) == PackageManager.PERMISSION_GRANTED
                            val coarseGranted = ContextCompat.checkSelfPermission(
                                context,
                                android.Manifest.permission.ACCESS_COARSE_LOCATION
                            ) == PackageManager.PERMISSION_GRANTED

                            if (fineGranted || coarseGranted) {
                                locationViewModel.fetchLocation(context)
                                vehicleViewModel.fetchLocation(context)
                            } else {
                                permissionLauncher.launch(
                                    arrayOf(
                                        android.Manifest.permission.ACCESS_FINE_LOCATION,
                                        android.Manifest.permission.ACCESS_COARSE_LOCATION
                                    )
                                )
                            }
                        }
                ) {
                    Column(
                        modifier = Modifier.padding(18.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                Icon(
                                    imageVector = Icons.Outlined.LocationOn,
                                    contentDescription = "Location",
                                    tint = HealthyGreen,
                                    modifier = Modifier.size(20.dp)
                                )
                                Text(
                                    text = "CURRENT VEHICLE LOCATION",
                                    color = HealthyGreen,
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }

                            if (locationUiState.isLoading) {
                                CircularProgressIndicator(
                                    modifier = Modifier.size(16.dp),
                                    color = HealthyGreen,
                                    strokeWidth = 2.dp
                                )
                            } else if (locationUiState.permissionDenied || locationUiState.isLocationUnavailable) {
                                Icon(
                                    imageVector = Icons.Default.Refresh,
                                    contentDescription = "Retry Location",
                                    tint = HealthyGreen,
                                    modifier = Modifier.size(18.dp)
                                )
                            }
                        }

                        val locationText = when {
                            locationUiState.isLoading -> "Acquiring GPS Location..."
                            locationUiState.permissionDenied -> "Location Permission Denied"
                            locationUiState.isLocationUnavailable -> "GPS Location Unavailable"
                            !locationUiState.address.isNullOrEmpty() -> locationUiState.address!!
                            locationUiState.latitude != null && locationUiState.longitude != null ->
                                String.format(Locale.US, "Lat: %.4f°, Long: %.4f°", locationUiState.latitude, locationUiState.longitude)
                            else -> "Current Location"
                        }

                        Text(
                            text = locationText,
                            style = MaterialTheme.typography.titleMedium,
                            color = CardSurfaceLight,
                            fontWeight = FontWeight.Bold
                        )

                        val subtext = when {
                            locationUiState.isLoading -> "Retrieving fresh location via FusedLocationProviderClient..."
                            locationUiState.permissionDenied -> "Tap card to grant location permission"
                            locationUiState.isLocationUnavailable -> "Unable to acquire location lock. Tap card to retry."
                            locationUiState.latitude != null && locationUiState.longitude != null -> {
                                val latFormatted = String.format(Locale.US, "%.4f", locationUiState.latitude)
                                val lngFormatted = String.format(Locale.US, "%.4f", locationUiState.longitude)
                                val latDir = if (locationUiState.latitude!! >= 0) "N" else "S"
                                val lngDir = if (locationUiState.longitude!! >= 0) "E" else "W"
                                "GPS Signal Lock: High Precision (Lat: $latFormatted° $latDir, Long: $lngFormatted° $lngDir)"
                            }
                            else -> "GPS Signal Lock: High Precision"
                        }

                        Text(
                            text = subtext,
                            fontSize = 12.sp,
                            color = Color.White.copy(alpha = 0.7f)
                        )
                    }
                }
            }

            // Assistance Options Selection
            item {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text(
                        text = "Select Rescue Category",
                        style = MaterialTheme.typography.titleMedium,
                        color = CharcoalText,
                        fontWeight = FontWeight.Bold
                    )

                    // Grid of 6 options
                    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        rescueOptions.chunked(2).forEach { rowOptions ->
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(10.dp)
                            ) {
                                rowOptions.forEach { option ->
                                    val isSelected = selectedOption == option.title
                                    val (bgColor, borderColor, textColor) = if (isSelected) {
                                        Triple(PrimaryDark, HealthyGreen, CardSurfaceLight)
                                    } else {
                                        Triple(CardSurfaceLight, CardBorderLight, CharcoalText)
                                    }

                                    Card(
                                        shape = RoundedCornerShape(16.dp),
                                        colors = CardDefaults.cardColors(containerColor = bgColor),
                                        border = androidx.compose.foundation.BorderStroke(
                                            if (isSelected) 2.dp else 1.dp,
                                            borderColor
                                        ),
                                        modifier = Modifier
                                            .weight(1f)
                                            .clickable { vehicleViewModel.selectRescueOption(option.title) }
                                            .testTag("rescue_option_${option.title}")
                                    ) {
                                        Column(
                                            modifier = Modifier.padding(14.dp),
                                            verticalArrangement = Arrangement.spacedBy(8.dp)
                                        ) {
                                            Row(
                                                modifier = Modifier.fillMaxWidth(),
                                                horizontalArrangement = Arrangement.SpaceBetween,
                                                verticalAlignment = Alignment.CenterVertically
                                            ) {
                                                Icon(
                                                    imageVector = when (option.title) {
                                                        "Flat Tyre" -> Icons.Default.TireRepair
                                                        "Battery Issue" -> Icons.Default.BatteryAlert
                                                        "Engine Breakdown" -> Icons.Default.Build
                                                        "Accident" -> Icons.Default.Warning
                                                        "Fuel Needed" -> Icons.Default.LocalGasStation
                                                        else -> Icons.Default.HelpOutline
                                                    },
                                                    contentDescription = null,
                                                    tint = if (isSelected) HealthyGreen else PrimaryDark,
                                                    modifier = Modifier.size(24.dp)
                                                )

                                                if (isSelected) {
                                                    Icon(
                                                        imageVector = Icons.Default.CheckCircle,
                                                        contentDescription = "Selected",
                                                        tint = HealthyGreen,
                                                        modifier = Modifier.size(18.dp)
                                                    )
                                                }
                                            }

                                            Text(
                                                text = option.title,
                                                fontWeight = FontWeight.Bold,
                                                fontSize = 14.sp,
                                                color = textColor
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // Helpful Info Section (instead of "Request Assistance" button which now shows backend recommendation)
            item {
                Card(
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = BackgroundLight),
                    border = androidx.compose.foundation.BorderStroke(1.dp, CardBorderLight),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier.padding(14.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = "About Assistance",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            color = CharcoalMuted
                        )
                        Text(
                            text = "Run a vehicle check to receive personalized assistance recommendations based on your vehicle's condition.",
                            fontSize = 11.sp,
                            color = CharcoalMuted,
                            lineHeight = 16.sp
                        )
                    }
                }
            }

            // Nearby Service Centres (from Backend, not Google Places)
            if (!backendResponse?.serviceCentres.isNullOrEmpty()) {
                item {
                    Column(
                        modifier = Modifier.fillMaxWidth(),
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
                                        .clip(RoundedCornerShape(8.dp))
                                        .background(PrimaryDark),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.Storefront,
                                        contentDescription = "Service Centres",
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
                                    Text(
                                        text = "From OpenStreetMap",
                                        fontSize = 11.sp,
                                        color = CharcoalMuted
                                    )
                                }
                            }
                        }

                        // Service centres list from backend
                        Text(
                            text = "Found ${backendResponse?.serviceCentres?.size ?: 0} automotive centres",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = HealthyGreenDark
                        )

                        backendResponse?.serviceCentres?.forEachIndexed { index, centre ->
                            Card(
                                shape = RoundedCornerShape(16.dp),
                                colors = CardDefaults.cardColors(containerColor = CardSurfaceLight),
                                border = androidx.compose.foundation.BorderStroke(1.dp, CardBorderLight),
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Column(
                                    modifier = Modifier.padding(16.dp),
                                    verticalArrangement = Arrangement.spacedBy(10.dp)
                                ) {
                                    Row(
                                        modifier = Modifier.fillMaxWidth(),
                                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Box(
                                            modifier = Modifier
                                                .size(26.dp)
                                                .clip(CircleShape)
                                                .background(PrimaryDark),
                                            contentAlignment = Alignment.Center
                                        ) {
                                            Text(
                                                text = "#${index + 1}",
                                                color = HealthyGreen,
                                                fontWeight = FontWeight.Bold,
                                                fontSize = 11.sp
                                            )
                                        }

                                        Text(
                                            text = centre.name,
                                            style = MaterialTheme.typography.titleMedium,
                                            fontWeight = FontWeight.Bold,
                                            color = CharcoalText,
                                            modifier = Modifier.weight(1f)
                                        )
                                    }

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
                                            color = CharcoalMuted
                                        )
                                    }

                                    Text(
                                        text = "Distance: ${String.format("%.1f", centre.distanceKm)} km",
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.SemiBold,
                                        color = PrimaryDark
                                    )

                                    // Navigate button
                                    Button(
                                        onClick = {
                                            openServiceCentreInMaps(
                                                context,
                                                centre.latitude,
                                                centre.longitude,
                                                centre.name
                                            )
                                        },
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .height(40.dp),
                                        colors = ButtonDefaults.buttonColors(
                                            containerColor = PrimaryDark
                                        ),
                                        shape = RoundedCornerShape(10.dp)
                                    ) {
                                        Row(
                                            verticalAlignment = Alignment.CenterVertically,
                                            horizontalArrangement = Arrangement.spacedBy(6.dp)
                                        ) {
                                            Icon(
                                                imageVector = Icons.Outlined.LocationOn,
                                                contentDescription = "Navigate",
                                                tint = HealthyGreen,
                                                modifier = Modifier.size(18.dp)
                                            )
                                            Text(
                                                text = if (navigationAllowed) "Navigate" else "View Location",
                                                fontSize = 12.sp,
                                                fontWeight = FontWeight.Bold,
                                                color = HealthyGreen
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // Backend Assistance Recommendation (replaces mock dispatch)
            when (backendStatus) {
                "ASSISTANCE_REQUIRED" -> {
                    if (backendRescue != null) {
                        item {
                            Card(
                                shape = RoundedCornerShape(20.dp),
                                colors = CardDefaults.cardColors(containerColor = CardSurfaceLight),
                                border = androidx.compose.foundation.BorderStroke(1.5.dp, CriticalRedDark),
                                elevation = CardDefaults.cardElevation(defaultElevation = 6.dp),
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .testTag("backend_assistance_card")
                            ) {
                                Column(
                                    modifier = Modifier.padding(20.dp),
                                    verticalArrangement = Arrangement.spacedBy(14.dp)
                                ) {
                                    // Assistance Type & Priority
                                    Row(
                                        modifier = Modifier.fillMaxWidth(),
                                        horizontalArrangement = Arrangement.SpaceBetween,
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Column {
                                            Text(
                                                text = "Recommended Assistance",
                                                style = MaterialTheme.typography.titleMedium,
                                                color = CharcoalText,
                                                fontWeight = FontWeight.Bold
                                            )
                                            Text(
                                                text = backendRescue.assistanceType ?: "General Roadside Assistance",
                                                fontSize = 14.sp,
                                                color = CriticalRedDark,
                                                fontWeight = FontWeight.Bold
                                            )
                                        }

                                        StatusBadge(
                                            status = HealthStatus.CRITICAL,
                                            text = backendRescue.priority ?: "HIGH"
                                        )
                                    }

                                    HorizontalDivider(color = CardBorderLight)

                                    // Safe to Drive Warning
                                    if (backendResponse?.diagnosis?.safeToDrive == false) {
                                        Row(
                                            modifier = Modifier
                                                .fillMaxWidth()
                                                .clip(RoundedCornerShape(12.dp))
                                                .background(CriticalRedBg)
                                                .padding(12.dp),
                                            verticalAlignment = Alignment.CenterVertically,
                                            horizontalArrangement = Arrangement.spacedBy(10.dp)
                                        ) {
                                            Icon(
                                                imageVector = Icons.Default.Warning,
                                                contentDescription = "Safety Warning",
                                                tint = CriticalRedDark,
                                                modifier = Modifier.size(20.dp)
                                            )
                                            Text(
                                                text = "NOT SAFE TO DRIVE",
                                                fontSize = 13.sp,
                                                fontWeight = FontWeight.Bold,
                                                color = CriticalRedDark
                                            )
                                        }
                                    }

                                    // Reason
                                    if (!backendRescue.reason.isNullOrBlank()) {
                                        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                                            Text(
                                                text = "Reason",
                                                fontSize = 11.sp,
                                                fontWeight = FontWeight.Bold,
                                                color = CharcoalMuted
                                            )
                                            Text(
                                                text = backendRescue.reason,
                                                fontSize = 13.sp,
                                                color = CharcoalText
                                            )
                                        }
                                    }

                                    // ETA (with Demo Label)
                                    if (backendRescue.estimatedDispatchMinutes != null) {
                                        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                                            Text(
                                                text = "Estimated Assistance Time",
                                                fontSize = 11.sp,
                                                fontWeight = FontWeight.Bold,
                                                color = CharcoalMuted
                                            )
                                            Row(
                                                verticalAlignment = Alignment.CenterVertically,
                                                horizontalArrangement = Arrangement.spacedBy(6.dp)
                                            ) {
                                                Text(
                                                    text = "${backendRescue.estimatedDispatchMinutes} mins",
                                                    fontSize = 18.sp,
                                                    fontWeight = FontWeight.Bold,
                                                    color = PrimaryDark
                                                )
                                                Text(
                                                    text = "Demo estimate",
                                                    fontSize = 10.sp,
                                                    fontWeight = FontWeight.Bold,
                                                    color = WarningAmberDark
                                                )
                                            }
                                        }
                                    }

                                    // Tow Required
                                    if (backendRescue.towRequired) {
                                        Row(
                                            modifier = Modifier
                                                .fillMaxWidth()
                                                .clip(RoundedCornerShape(10.dp))
                                                .background(BackgroundLight)
                                                .padding(10.dp),
                                            verticalAlignment = Alignment.CenterVertically,
                                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                                        ) {
                                            Icon(
                                                imageVector = Icons.Default.DirectionsCar,
                                                contentDescription = "Tow Required",
                                                tint = PrimaryDark,
                                                modifier = Modifier.size(18.dp)
                                            )
                                            Text(
                                                text = "Towing Required",
                                                fontSize = 13.sp,
                                                fontWeight = FontWeight.Bold,
                                                color = PrimaryDark
                                            )
                                        }
                                    }

                                    // Instructions
                                    if (!backendRescue.instructions.isNullOrBlank()) {
                                        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                                            Text(
                                                text = "Instructions",
                                                fontSize = 11.sp,
                                                fontWeight = FontWeight.Bold,
                                                color = CharcoalMuted
                                            )
                                            Text(
                                                text = backendRescue.instructions,
                                                fontSize = 12.sp,
                                                color = CharcoalText
                                            )
                                        }
                                    }
                                }
                            }
                        }

                        // Tow Service Call Button for Critical scenarios
                        if (backendRescue.towRequired) {
                            item {
                                Button(
                                    onClick = { openTowDialer(context) },
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .height(54.dp),
                                    colors = ButtonDefaults.buttonColors(
                                        containerColor = CriticalRedDark
                                    ),
                                    shape = RoundedCornerShape(14.dp)
                                ) {
                                    Row(
                                        verticalAlignment = Alignment.CenterVertically,
                                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                                    ) {
                                        Icon(
                                            imageVector = Icons.Outlined.Phone,
                                            contentDescription = "Call Tow Service",
                                            tint = Color.White,
                                            modifier = Modifier.size(22.dp)
                                        )
                                        Column {
                                            Text(
                                                text = "Call Tow Service",
                                                fontSize = 14.sp,
                                                fontWeight = FontWeight.Bold,
                                                color = Color.White
                                            )
                                            Text(
                                                text = "7867896369",
                                                fontSize = 11.sp,
                                                color = Color.White.copy(alpha = 0.8f)
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                "SERVICE_RECOMMENDED" -> {
                    item {
                        Card(
                            shape = RoundedCornerShape(20.dp),
                            colors = CardDefaults.cardColors(containerColor = WarningAmberBg),
                            border = androidx.compose.foundation.BorderStroke(1.5.dp, WarningAmberDark),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Column(
                                modifier = Modifier.padding(16.dp),
                                verticalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                Text(
                                    text = "Service Inspection Recommended",
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = WarningAmberDark
                                )
                                Text(
                                    text = "Roadside assistance is not currently required. Visit a service centre for inspection.",
                                    fontSize = 12.sp,
                                    color = WarningAmberDark.copy(alpha = 0.8f)
                                )
                            }
                        }
                    }
                }

                "HEALTHY" -> {
                    item {
                        Card(
                            shape = RoundedCornerShape(20.dp),
                            colors = CardDefaults.cardColors(containerColor = HealthyGreenBg),
                            border = androidx.compose.foundation.BorderStroke(1.5.dp, HealthyGreenDark),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Column(
                                modifier = Modifier.padding(16.dp),
                                verticalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                Text(
                                    text = "No Assistance Required",
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = HealthyGreenDark
                                )
                                Text(
                                    text = "Your vehicle is currently healthy and safe to drive.",
                                    fontSize = 12.sp,
                                    color = HealthyGreenDark.copy(alpha = 0.8f)
                                )
                            }
                        }
                    }
                }

                else -> {
                    item {
                        Card(
                            shape = RoundedCornerShape(20.dp),
                            colors = CardDefaults.cardColors(containerColor = CardBorderLight),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Column(
                                modifier = Modifier.padding(16.dp),
                                verticalArrangement = Arrangement.spacedBy(8.dp),
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Text(
                                    text = "No Check Yet",
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = CharcoalText
                                )
                                Text(
                                    text = "Run a vehicle check to receive assistance recommendations.",
                                    fontSize = 12.sp,
                                    color = CharcoalMuted,
                                    modifier = Modifier.padding(horizontal = 8.dp)
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}
