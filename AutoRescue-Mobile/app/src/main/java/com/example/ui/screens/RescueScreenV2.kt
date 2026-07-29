package com.example.ui.screens

import android.content.pm.PackageManager
import android.util.Log
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.draw.clip
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.model.RescueOption
import com.example.ui.components.AccidentInjuryDialog
import com.example.ui.components.AutoRescueHeader
import com.example.ui.components.BatteryAssistanceSheet
import com.example.ui.components.NearbyServiceCentresCard
import com.example.ui.theme.*
import com.example.utils.openServiceCentreInMaps
import com.example.utils.openTowDialer
import com.example.viewmodel.DiagnosticsViewModel
import com.example.viewmodel.LocationViewModel
import com.example.viewmodel.RescueViewModel
import com.example.viewmodel.VehicleViewModel

@Composable
fun RescueScreen(
    vehicleViewModel: VehicleViewModel,
    diagnosticsViewModel: DiagnosticsViewModel,
    rescueViewModel: RescueViewModel = viewModel(),
    locationViewModel: LocationViewModel = viewModel(),
    onNavigateToNotifications: () -> Unit,
    onNavigateToProfile: () -> Unit
) {
    val context = LocalContext.current
    val rescueState by rescueViewModel.rescueState.collectAsState()
    val rescueOptions by vehicleViewModel.rescueOptions.collectAsState()
    val notifications by vehicleViewModel.notifications.collectAsState()
    val locationUiState by locationViewModel.uiState.collectAsState()
    val backendResponse = diagnosticsViewModel.diagnosticState.collectAsState().value.backendResponse

    var showBatterySheet by remember { mutableStateOf(false) }
    var showAccidentDialog by remember { mutableStateOf(false) }

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val fineGranted = permissions[android.Manifest.permission.ACCESS_FINE_LOCATION] ?: false
        val coarseGranted = permissions[android.Manifest.permission.ACCESS_COARSE_LOCATION] ?: false
        if (fineGranted || coarseGranted) {
            locationViewModel.fetchLocation(context)
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
        } else {
            permissionLauncher.launch(
                arrayOf(
                    android.Manifest.permission.ACCESS_FINE_LOCATION,
                    android.Manifest.permission.ACCESS_COARSE_LOCATION
                )
            )
        }
    }

    // Dialog states
    if (showBatterySheet) {
        BatteryAssistanceSheet(
            onEvChargingSelected = {
                rescueViewModel.selectBatteryAssistanceType("EV_CHARGING")
                showBatterySheet = false
            },
            onVehicleBatterySelected = {
                rescueViewModel.selectBatteryAssistanceType("VEHICLE_BATTERY_ISSUE")
                showBatterySheet = false
            },
            onDismiss = { showBatterySheet = false }
        )
    }

    if (showAccidentDialog) {
        AccidentInjuryDialog(
            onYesSelected = {
                rescueViewModel.selectAccidentInjuryResponse(true)
                showAccidentDialog = false
            },
            onNoSelected = {
                rescueViewModel.selectAccidentInjuryResponse(false)
                showAccidentDialog = false
            },
            onDismiss = { showAccidentDialog = false }
        )
    }

    // Render based on current flow
    when (rescueState.currentFlow) {
        "CATEGORY_SELECTION" -> {
            RescueCategorySelectionScreen(
                rescueOptions = rescueOptions,
                notifications = notifications,
                onCategorySelected = { category ->
                    when (category.title) {
                        "Battery Issue" -> {
                            rescueViewModel.selectRescueCategory("BATTERY_ISSUE")
                            showBatterySheet = true
                        }
                        "Accident" -> {
                            rescueViewModel.selectRescueCategory("ACCIDENT")
                            showAccidentDialog = true
                        }
                        "Fuel Needed" -> {
                            rescueViewModel.selectRescueCategory("FUEL_NEEDED")
                            rescueViewModel.selectBatteryAssistanceType("FUEL_STATION")
                        }
                        "Flat Tyre" -> {
                            rescueViewModel.selectRescueCategory("FLAT_TYRE")
                        }
                        "Engine Breakdown" -> {
                            rescueViewModel.selectRescueCategory("ENGINE_BREAKDOWN")
                        }
                        else -> {
                            rescueViewModel.selectRescueCategory("OTHER")
                        }
                    }
                },
                onNotificationClick = onNavigateToNotifications,
                onProfileClick = onNavigateToProfile
            )
        }

        "BATTERY_SELECTION" -> {
            // Battery assistance sheet is shown above
        }

        "ACCIDENT_CHECK" -> {
            // Accident dialog is shown above
        }

        "NEARBY_PLACES" -> {
            val latitude = locationUiState.latitude
            val longitude = locationUiState.longitude

            if (latitude == 0.0 && longitude == 0.0) {
                LocationPermissionNeededScreen(onBackClick = {
                    rescueViewModel.goBackToSelection()
                })
            } else {
                // Trigger search on first compose
                if (latitude != 0.0 && longitude != 0.0) {
                    LaunchedEffect(rescueState.placesCategory) {
                        rescueViewModel.searchNearbyPlaces(latitude, longitude, context)
                    }
                }

                NearbyPlacesScreen(
                    title = rescueViewModel.getTitleForCategory(),
                    places = rescueState.nearbyPlaces,
                    isLoading = rescueState.isLoadingPlaces,
                    error = rescueState.placesError,
                    placesCategory = rescueState.placesCategory,
                    onBackClick = {
                        if (rescueState.selectedRescueCategory == "BATTERY_ISSUE") {
                            rescueViewModel.goBackToBatterySelection()
                        } else {
                            rescueViewModel.goBackToSelection()
                        }
                    }
                )
            }
        }

        "RESULT" -> {
            // Existing rescue result screen
            RescueResultScreen(
                backendResponse = backendResponse,
                onBackClick = { rescueViewModel.resetFlow() },
                onNotificationClick = onNavigateToNotifications,
                onProfileClick = onNavigateToProfile
            )
        }
    }
}

@Composable
private fun RescueCategorySelectionScreen(
    rescueOptions: List<RescueOption>,
    notifications: List<com.example.model.AlertItem>,
    onCategorySelected: (RescueOption) -> Unit,
    onNotificationClick: () -> Unit,
    onProfileClick: () -> Unit
) {
    Scaffold(
        topBar = {
            AutoRescueHeader(
                title = "Roadside Assistance",
                hasUnreadNotifications = notifications.any { !it.isRead },
                onNotificationClick = onNotificationClick,
                onProfileClick = onProfileClick
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
            item {
                Card(
                    shape = RoundedCornerShape(20.dp),
                    colors = CardDefaults.cardColors(containerColor = PrimaryDark),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(18.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(48.dp)
                                .clip(RoundedCornerShape(14.dp))
                                .background(HealthyGreen.copy(alpha = 0.2f)),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.LocalShipping,
                                contentDescription = null,
                                tint = HealthyGreen,
                                modifier = Modifier.size(26.dp)
                            )
                        }

                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "Roadside Assistance",
                                style = MaterialTheme.typography.titleMedium,
                                color = MaterialTheme.colorScheme.onPrimary,
                                fontWeight = FontWeight.Bold
                            )
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(
                                text = "Select assistance type",
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.7f)
                            )
                        }
                    }
                }
            }

            item {
                LazyVerticalGrid(
                    columns = GridCells.Fixed(2),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                    modifier = Modifier
                        .fillMaxWidth()
                        .wrapContentHeight()
                ) {
                    items(rescueOptions) { option ->
                        RescueCategoryCard(
                            option = option,
                            onClick = { onCategorySelected(option) }
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun ServiceCentreItem(
    name: String,
    address: String,
    distance: Double,
    rating: Double?,
    onClick: () -> Unit
) {
    Card(
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        border = androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Text(
                    text = name,
                    fontWeight = FontWeight.Bold,
                    fontSize = 13.sp,
                    modifier = Modifier.weight(1f)
                )
                if (rating != null) {
                    Text(
                        text = "★ $rating",
                        fontSize = 11.sp,
                        color = WarningAmber
                    )
                }
            }
            Text(
                text = address,
                fontSize = 11.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = String.format("%.1f km", distance),
                fontSize = 11.sp,
                color = HealthyGreen,
                fontWeight = FontWeight.SemiBold
            )
        }
    }
}

@Composable
private fun RescueCategoryCard(
    option: RescueOption,
    onClick: () -> Unit
) {
    val (bgColor, iconColor) = when (option.title) {
        "Battery Issue" -> WarningAmberBg to WarningAmber
        "Accident" -> CriticalRedBg to CriticalRed
        "Fuel Needed" -> HealthyGreenBg to HealthyGreen
        else -> CardSurfaceLight to PrimaryDark
    }

    val icon = when (option.title) {
        "Flat Tyre" -> Icons.Default.TireRepair
        "Battery Issue" -> Icons.Default.BatteryAlert
        "Engine Breakdown" -> Icons.Default.Build
        "Accident" -> Icons.Default.Warning
        "Fuel Needed" -> Icons.Default.LocalGasStation
        else -> Icons.Default.Info
    }

    Card(
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = bgColor),
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .height(140.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, iconColor.copy(alpha = 0.3f))
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Box(
                modifier = Modifier
                    .size(44.dp)
                    .background(iconColor.copy(alpha = 0.2f), RoundedCornerShape(10.dp)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = iconColor,
                    modifier = Modifier.size(24.dp)
                )
            }

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = option.title,
                fontWeight = FontWeight.Bold,
                fontSize = 13.sp,
                color = MaterialTheme.colorScheme.onSurface,
                textAlign = androidx.compose.ui.text.style.TextAlign.Center
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun LocationPermissionNeededScreen(onBackClick: () -> Unit) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Location Required") },
                navigationIcon = {
                    IconButton(onClick = onBackClick) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Icon(
                imageVector = Icons.Default.LocationOff,
                contentDescription = null,
                tint = WarningAmber,
                modifier = Modifier.size(64.dp)
            )

            Spacer(modifier = Modifier.height(20.dp))

            Text(
                text = "Location Access Needed",
                fontWeight = FontWeight.Bold,
                fontSize = 18.sp
            )

            Spacer(modifier = Modifier.height(12.dp))

            Text(
                text = "Location access is needed to find nearby assistance.",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = androidx.compose.ui.text.style.TextAlign.Center
            )
        }
    }
}

@Composable
private fun RescueResultScreen(
    backendResponse: com.example.network.AutoRescueCheckResponse?,
    onBackClick: () -> Unit,
    onNotificationClick: () -> Unit,
    onProfileClick: () -> Unit
) {
    val notifications by remember { mutableStateOf(emptyList<com.example.model.AlertItem>()) }

    Scaffold(
        topBar = {
            AutoRescueHeader(
                title = "Rescue Information",
                hasUnreadNotifications = notifications.any { !it.isRead },
                onNotificationClick = onNotificationClick,
                onProfileClick = onProfileClick
            )
        }
    ) { innerPadding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(horizontal = 20.dp),
            contentPadding = PaddingValues(top = 12.dp, bottom = 28.dp)
        ) {
            item {
                Button(
                    onClick = onBackClick,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(44.dp)
                ) {
                    Text("Back to Categories")
                }
            }

            if (backendResponse?.rescue != null) {
                item {
                    Card(
                        shape = RoundedCornerShape(16.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(
                            modifier = Modifier.padding(16.dp),
                            verticalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            Text(
                                text = "Rescue Information",
                                fontWeight = FontWeight.Bold,
                                fontSize = 16.sp
                            )
                            Text(
                                text = "Assistance Type: ${backendResponse.rescue.assistanceType}",
                                fontSize = 14.sp
                            )
                            Text(
                                text = "Priority: ${backendResponse.rescue.priority}",
                                fontSize = 14.sp
                            )
                            Text(
                                text = backendResponse.rescue.instructions,
                                fontSize = 13.sp,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )

                            if (backendResponse.rescue.towRequired) {
                                Button(
                                    onClick = { openTowDialer(context) },
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .height(44.dp)
                                ) {
                                    Text("Call Tow Service")
                                }
                            }
                        }
                    }
                }
            }

            if (backendResponse?.serviceCentres?.isNotEmpty() == true) {
                item {
                    Text(
                        "Available Service Centres",
                        fontWeight = FontWeight.Bold,
                        fontSize = 16.sp,
                        modifier = Modifier.padding(top = 12.dp)
                    )
                    LazyColumn(
                        verticalArrangement = Arrangement.spacedBy(12.dp),
                        modifier = Modifier.padding(top = 12.dp)
                    ) {
                        items(backendResponse.serviceCentres) { centre ->
                            ServiceCentreItem(
                                name = centre.name,
                                address = centre.address,
                                distance = centre.distanceKm,
                                rating = centre.rating,
                                onClick = {
                                    openServiceCentreInMaps(context, centre.latitude, centre.longitude, centre.name)
                                }
                            )
                        }
                    }
                }
            }
        }
    }
}
