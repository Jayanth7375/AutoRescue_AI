package com.example.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.slideInVertically
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.DirectionsCar
import androidx.compose.material.icons.filled.MedicalServices
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.R
import com.example.model.HealthStatus
import com.example.ui.components.AutoRescueHeader
import com.example.ui.components.HealthProgressBar
import com.example.ui.components.NearbyServiceCentresCard
import com.example.ui.components.StatusBadge
import com.example.ui.theme.*
import com.example.viewmodel.DiagnosticsViewModel
import com.example.viewmodel.VehicleViewModel

@Composable
fun HomeScreen(
    vehicleViewModel: VehicleViewModel,
    diagnosticsViewModel: DiagnosticsViewModel,
    onNavigateToDiagnose: () -> Unit,
    onNavigateToRescue: () -> Unit,
    onNavigateToNotifications: () -> Unit,
    onNavigateToProfile: () -> Unit
) {
    val vehicleInfo by vehicleViewModel.vehicleInfo.collectAsState()
    val components by vehicleViewModel.componentHealthList.collectAsState()
    val notifications by vehicleViewModel.notifications.collectAsState()
    val locationState by vehicleViewModel.locationState.collectAsState()
    val serviceCentresState by vehicleViewModel.serviceCentresState.collectAsState()
    val diagnosticState by diagnosticsViewModel.diagnosticState.collectAsState()

    val hasUnreadNotifs = notifications.any { !it.isRead }

    val backendResponse = diagnosticState.backendResponse
    val latestStatus = backendResponse?.status ?: "UNKNOWN"
    val latestDiagnosis = backendResponse?.diagnosis

    Scaffold(
        topBar = {
            AutoRescueHeader(
                title = "AutoRescue AI",
                hasUnreadNotifications = hasUnreadNotifs,
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
            // Greeting Banner with Backend Status
            item {
                Column {
                    Text(
                        text = "Good Morning",
                        style = MaterialTheme.typography.displayMedium,
                        color = CharcoalText,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        val (statusMessage, statusColor) = when (latestStatus) {
                            "HEALTHY" -> "Your vehicle is healthy and safe to drive." to HealthyGreen
                            "SERVICE_RECOMMENDED" -> "Attention required: Service inspection recommended." to WarningAmberDark
                            "ASSISTANCE_REQUIRED" -> "Critical issue: NOT SAFE TO DRIVE — Assistance recommended." to CriticalRedDark
                            else -> "Run a vehicle check to assess health status." to CharcoalMuted
                        }

                        Box(
                            modifier = Modifier
                                .size(10.dp)
                                .clip(CircleShape)
                                .background(statusColor)
                        )
                        Text(
                            text = statusMessage,
                            style = MaterialTheme.typography.bodyLarge,
                            color = CharcoalMuted
                        )
                    }
                }
            }

            // Vehicle Hero Card
            item {
                Card(
                    shape = RoundedCornerShape(24.dp),
                    colors = CardDefaults.cardColors(containerColor = PrimaryDark),
                    elevation = CardDefaults.cardElevation(defaultElevation = 6.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier.padding(20.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.Top
                        ) {
                            Column {
                                Surface(
                                    color = Color.White.copy(alpha = 0.12f),
                                    shape = RoundedCornerShape(12.dp)
                                ) {
                                    Text(
                                        text = "PRIMARY VEHICLE",
                                        color = HealthyGreen,
                                        fontSize = 11.sp,
                                        fontWeight = FontWeight.Bold,
                                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp)
                                    )
                                }
                                Spacer(modifier = Modifier.height(8.dp))
                                Text(
                                    text = vehicleInfo.name,
                                    style = MaterialTheme.typography.titleLarge,
                                    color = CardSurfaceLight,
                                    fontWeight = FontWeight.Bold
                                )
                                Text(
                                    text = vehicleInfo.registrationNumber,
                                    style = MaterialTheme.typography.bodyLarge,
                                    color = Color.White.copy(alpha = 0.7f),
                                    fontWeight = FontWeight.Medium
                                )
                            }

                            // Vehicle Health Percentage Ring (from backend if available)
                            Column(
                                horizontalAlignment = Alignment.End
                            ) {
                                val healthPercentage = if (latestStatus == "HEALTHY") 90
                                                     else if (latestStatus == "SERVICE_RECOMMENDED") 50
                                                     else if (latestStatus == "ASSISTANCE_REQUIRED") 20
                                                     else vehicleInfo.overallHealthPercentage

                                val healthStatus = when (latestStatus) {
                                    "HEALTHY" -> HealthStatus.HEALTHY
                                    "SERVICE_RECOMMENDED" -> HealthStatus.WARNING
                                    "ASSISTANCE_REQUIRED" -> HealthStatus.CRITICAL
                                    else -> HealthStatus.HEALTHY
                                }

                                val statusText = when (latestStatus) {
                                    "HEALTHY" -> "HEALTHY"
                                    "SERVICE_RECOMMENDED" -> "ATTENTION"
                                    "ASSISTANCE_REQUIRED" -> "CRITICAL"
                                    else -> vehicleInfo.statusText
                                }

                                Text(
                                    text = "$healthPercentage%",
                                    fontSize = 32.sp,
                                    fontWeight = FontWeight.ExtraBold,
                                    color = when (healthStatus) {
                                        HealthStatus.HEALTHY -> HealthyGreen
                                        HealthStatus.WARNING -> WarningAmberDark
                                        HealthStatus.CRITICAL -> CriticalRedDark
                                    }
                                )
                                StatusBadge(
                                    status = healthStatus,
                                    text = statusText
                                )
                            }
                        }

                        Spacer(modifier = Modifier.height(16.dp))

                        // Vehicle Hero Image
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(130.dp)
                                .clip(RoundedCornerShape(16.dp))
                                .background(CharcoalSurface)
                        ) {
                            Image(
                                painter = painterResource(id = R.drawable.img_nexon_vehicle),
                                contentDescription = "Tata Nexon Vehicle",
                                contentScale = ContentScale.Crop,
                                modifier = Modifier.fillMaxSize()
                            )
                        }
                    }
                }
            }

            // Quick Actions Section
            item {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text(
                        text = "Quick Actions",
                        style = MaterialTheme.typography.titleMedium,
                        color = CharcoalText,
                        fontWeight = FontWeight.Bold
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        // Action 1: Run Vehicle Check
                        Button(
                            onClick = onNavigateToDiagnose,
                            colors = ButtonDefaults.buttonColors(
                                containerColor = PrimaryDark,
                                contentColor = CardSurfaceLight
                            ),
                            shape = RoundedCornerShape(16.dp),
                            contentPadding = PaddingValues(vertical = 14.dp, horizontal = 16.dp),
                            modifier = Modifier
                                .weight(1f)
                                .testTag("quick_run_vehicle_check_button")
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.Center
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Build,
                                    contentDescription = null,
                                    tint = HealthyGreen,
                                    modifier = Modifier.size(18.dp)
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = "Run Vehicle Check",
                                    fontSize = 13.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }

                        // Action 2: Request Assistance
                        Button(
                            onClick = onNavigateToRescue,
                            colors = ButtonDefaults.buttonColors(
                                containerColor = HealthyGreen,
                                contentColor = PrimaryDark
                            ),
                            shape = RoundedCornerShape(16.dp),
                            contentPadding = PaddingValues(vertical = 14.dp, horizontal = 16.dp),
                            modifier = Modifier
                                .weight(1f)
                                .testTag("quick_request_assistance_button")
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.Center
                            ) {
                                Icon(
                                    imageVector = Icons.Default.MedicalServices,
                                    contentDescription = null,
                                    tint = PrimaryDark,
                                    modifier = Modifier.size(18.dp)
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = "Request Assistance",
                                    fontSize = 13.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                    }
                }
            }

            // Vehicle Status Cards
            item {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "Vehicle Status",
                            style = MaterialTheme.typography.titleMedium,
                            color = CharcoalText,
                            fontWeight = FontWeight.Bold
                        )

                        Text(
                            text = "4 System Sensors",
                            fontSize = 12.sp,
                            color = CharcoalMuted
                        )
                    }

                    Card(
                        shape = RoundedCornerShape(20.dp),
                        colors = CardDefaults.cardColors(containerColor = CardSurfaceLight),
                        border = androidx.compose.foundation.BorderStroke(1.dp, CardBorderLight),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(
                            modifier = Modifier.padding(16.dp),
                            verticalArrangement = Arrangement.spacedBy(14.dp)
                        ) {
                            components.take(4).forEach { comp ->
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Row(
                                        verticalAlignment = Alignment.CenterVertically,
                                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                                    ) {
                                        Box(
                                            modifier = Modifier
                                                .size(10.dp)
                                                .clip(CircleShape)
                                                .background(
                                                    when (comp.status) {
                                                        HealthStatus.HEALTHY -> HealthyGreen
                                                        HealthStatus.WARNING -> WarningAmber
                                                        HealthStatus.CRITICAL -> CriticalRed
                                                    }
                                                )
                                        )
                                        Text(
                                            text = comp.name,
                                            fontWeight = FontWeight.SemiBold,
                                            fontSize = 15.sp,
                                            color = CharcoalText
                                        )
                                    }

                                    StatusBadge(
                                        status = comp.status,
                                        text = comp.statusText
                                    )
                                }

                                if (comp != components.take(4).last()) {
                                    HorizontalDivider(color = CardBorderLight.copy(alpha = 0.6f))
                                }
                            }
                        }
                    }
                }
            }

            // Nearby Service Centres
            item {
                val context = androidx.compose.ui.platform.LocalContext.current
                NearbyServiceCentresCard(
                    serviceCentresState = serviceCentresState,
                    locationState = locationState,
                    isSafeToDrive = latestDiagnosis?.safeToDrive ?: true,
                    onRequestTow = {
                        vehicleViewModel.selectRescueOption("Other")
                        onNavigateToRescue()
                    },
                    onRefreshClick = {
                        val lat = locationState.latitude
                        val lng = locationState.longitude
                        if (lat != null && lng != null) {
                            vehicleViewModel.fetchNearbyServiceCentres(context, lat, lng)
                        } else {
                            vehicleViewModel.fetchLocation(context)
                        }
                    }
                )
            }

            // Recent Alert Card
            item {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text(
                        text = "Recent Alert",
                        style = MaterialTheme.typography.titleMedium,
                        color = CharcoalText,
                        fontWeight = FontWeight.Bold
                    )

                    Card(
                        shape = RoundedCornerShape(20.dp),
                        colors = CardDefaults.cardColors(containerColor = WarningAmberBg),
                        border = androidx.compose.foundation.BorderStroke(1.dp, WarningAmber.copy(alpha = 0.4f)),
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { onNavigateToNotifications() }
                            .testTag("recent_alert_card")
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(14.dp)
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(44.dp)
                                    .clip(RoundedCornerShape(12.dp))
                                    .background(WarningAmber.copy(alpha = 0.2f)),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Warning,
                                    contentDescription = "Alert",
                                    tint = WarningAmberDark,
                                    modifier = Modifier.size(24.dp)
                                )
                            }

                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = "Front-left tyre pressure is low",
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 15.sp,
                                    color = WarningAmberDark
                                )
                                Spacer(modifier = Modifier.height(2.dp))
                                Text(
                                    text = "Today, 10:32 AM",
                                    fontSize = 12.sp,
                                    color = WarningAmberDark.copy(alpha = 0.8f)
                                )
                            }

                            Icon(
                                imageVector = Icons.AutoMirrored.Filled.ArrowForward,
                                contentDescription = "View",
                                tint = WarningAmberDark,
                                modifier = Modifier.size(18.dp)
                            )
                        }
                    }
                }
            }
        }
    }
}
