package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.BatteryAlert
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.TireRepair
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.HealthStatus
import com.example.model.AlertItem
import com.example.ui.components.StatusBadge
import com.example.ui.theme.*
import com.example.viewmodel.DiagnosticsViewModel
import com.example.viewmodel.VehicleViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NotificationsScreen(
    vehicleViewModel: VehicleViewModel,
    diagnosticsViewModel: DiagnosticsViewModel? = null,
    onNavigateBack: () -> Unit
) {
    // Get latest backend response
    val diagnosticState by diagnosticsViewModel?.diagnosticState?.collectAsState() ?: androidx.compose.runtime.mutableStateOf(null)
    val backendResponse = diagnosticState?.backendResponse

    // Convert backend notifications to AlertItem format
    val backendNotifications = backendResponse?.notifications?.map { backendNotif ->
        AlertItem(
            id = "${backendNotif.type}-${backendNotif.severity}-${System.currentTimeMillis()}",
            title = backendNotif.title,
            message = backendNotif.message,
            timestamp = backendNotif.timestamp.ifEmpty { "Just now" },
            severity = when (backendNotif.severity.uppercase()) {
                "CRITICAL", "HIGH" -> HealthStatus.CRITICAL
                "MEDIUM", "WARNING" -> HealthStatus.WARNING
                else -> HealthStatus.HEALTHY
            },
            isCriticalInstruction = backendNotif.severity.uppercase() == "CRITICAL",
            isRead = false
        )
    } ?: emptyList()

    // Use backend notifications if available, otherwise fall back to static notifications
    val notifications by if (backendNotifications.isNotEmpty()) {
        androidx.compose.runtime.mutableStateOf(backendNotifications)
    } else {
        vehicleViewModel.notifications.collectAsState()
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        text = "Notifications & Alerts",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onBackground
                    )
                },
                navigationIcon = {
                    IconButton(
                        onClick = onNavigateBack,
                        modifier = Modifier.testTag("notifications_back_button")
                    ) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back",
                            tint = MaterialTheme.colorScheme.onBackground
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.background)
            )
        },
        containerColor = MaterialTheme.colorScheme.background
    ) { innerPadding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(horizontal = 20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
            contentPadding = PaddingValues(top = 12.dp, bottom = 28.dp)
        ) {
            notifications.forEach { item ->
                item {
                    val isCritical = item.isCriticalInstruction
                    val cardBg = when {
                        isCritical -> CriticalRedBg
                        item.severity == HealthStatus.WARNING -> WarningAmberBg
                        else -> CardSurfaceLight
                    }
                    val borderColor = when {
                        isCritical -> CriticalRed
                        item.severity == HealthStatus.WARNING -> WarningAmber.copy(alpha = 0.5f)
                        else -> CardBorderLight
                    }

                    Card(
                        shape = RoundedCornerShape(20.dp),
                        colors = CardDefaults.cardColors(containerColor = cardBg),
                        border = androidx.compose.foundation.BorderStroke(1.5.dp, borderColor),
                        elevation = CardDefaults.cardElevation(defaultElevation = if (isCritical) 6.dp else 2.dp),
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable {
                                // Only mark as read if from VehicleViewModel (has markNotificationRead)
                                if (backendNotifications.isEmpty()) {
                                    vehicleViewModel.markNotificationRead(item.id)
                                }
                            }
                            .testTag("notification_card_${item.id}")
                    ) {
                        Column(
                            modifier = Modifier.padding(18.dp),
                            verticalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                                ) {
                                    Box(
                                        modifier = Modifier
                                            .size(40.dp)
                                            .clip(RoundedCornerShape(12.dp))
                                            .background(
                                                when {
                                                    isCritical -> CriticalRed.copy(alpha = 0.2f)
                                                    item.severity == HealthStatus.WARNING -> WarningAmber.copy(alpha = 0.2f)
                                                    else -> HealthyGreenBg
                                                }
                                            ),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        Icon(
                                            imageVector = when (item.title) {
                                                "Critical Engine Alert" -> Icons.Default.Warning
                                                "Low Tyre Pressure" -> Icons.Default.TireRepair
                                                "Battery Health Update" -> Icons.Default.BatteryAlert
                                                else -> Icons.Default.Notifications
                                            },
                                            contentDescription = null,
                                            tint = when {
                                                isCritical -> CriticalRedDark
                                                item.severity == HealthStatus.WARNING -> WarningAmberDark
                                                else -> HealthyGreenDark
                                            },
                                            modifier = Modifier.size(22.dp)
                                        )
                                    }

                                    Column {
                                        Text(
                                            text = item.title,
                                            fontWeight = FontWeight.Bold,
                                            fontSize = 16.sp,
                                            color = if (isCritical) CriticalRedDark else CharcoalText
                                        )
                                        Text(
                                            text = item.timestamp,
                                            fontSize = 12.sp,
                                            color = CharcoalMuted
                                        )
                                    }
                                }

                                if (!item.isRead) {
                                    Box(
                                        modifier = Modifier
                                            .size(10.dp)
                                            .clip(CircleShape)
                                            .background(CriticalRed)
                                    )
                                }
                            }

                            Text(
                                text = item.message,
                                fontSize = 14.sp,
                                color = CharcoalText,
                                lineHeight = 20.sp
                            )

                            // Critical Banner instruction if required
                            if (isCritical) {
                                Surface(
                                    color = CriticalRedDark,
                                    shape = RoundedCornerShape(14.dp),
                                    modifier = Modifier.fillMaxWidth()
                                ) {
                                    Column(
                                        modifier = Modifier.padding(16.dp),
                                        horizontalAlignment = Alignment.CenterHorizontally,
                                        verticalArrangement = Arrangement.spacedBy(6.dp)
                                    ) {
                                        Text(
                                            text = "NOT SAFE TO DRIVE",
                                            color = CardSurfaceLight,
                                            fontWeight = FontWeight.ExtraBold,
                                            fontSize = 16.sp,
                                            letterSpacing = 0.5.sp,
                                            textAlign = TextAlign.Center
                                        )
                                        Text(
                                            text = "Stop the vehicle safely and switch off the engine.",
                                            color = CardSurfaceLight.copy(alpha = 0.9f),
                                            fontWeight = FontWeight.Bold,
                                            fontSize = 13.sp,
                                            textAlign = TextAlign.Center
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
