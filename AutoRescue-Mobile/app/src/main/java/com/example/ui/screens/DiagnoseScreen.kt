package com.example.ui.screens

import androidx.compose.animation.*
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.CheckCircle
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
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import android.util.Log
import com.example.model.HealthStatus
import com.example.ui.components.AutoRescueHeader
import com.example.ui.components.HealthProgressBar
import com.example.ui.components.StatusBadge
import com.example.ui.theme.*
import com.example.viewmodel.DiagnosticsViewModel
import com.example.viewmodel.VehicleViewModel

@Composable
private fun TelemetryRow(label: String, value: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(8.dp))
            .background(BackgroundLight)
            .padding(10.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            fontSize = 12.sp,
            color = CharcoalMuted,
            fontWeight = FontWeight.Medium
        )
        Text(
            text = value,
            fontSize = 13.sp,
            color = CharcoalText,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
fun DiagnoseScreen(
    vehicleViewModel: VehicleViewModel,
    diagnosticsViewModel: DiagnosticsViewModel,
    onNavigateToNotifications: () -> Unit,
    onNavigateToProfile: () -> Unit
) {
    val context = androidx.compose.ui.platform.LocalContext.current
    val notifications by vehicleViewModel.notifications.collectAsState()
    val backendDiagnosticState by diagnosticsViewModel.diagnosticState.collectAsState()
    val latestTelemetry by diagnosticsViewModel.latestTelemetry.collectAsState()

    Scaffold(
        topBar = {
            AutoRescueHeader(
                title = "Vehicle Diagnostics — DEBUG: DiagnoseScreen Active",
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
            // Debug label
            item {
                Text(
                    text = "✓ This is DiagnoseScreen",
                    fontSize = 10.sp,
                    color = HealthyGreen,
                    modifier = Modifier.padding(vertical = 8.dp)
                )
            }

            // Header Description
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
                                imageVector = Icons.Default.Build,
                                contentDescription = null,
                                tint = HealthyGreen,
                                modifier = Modifier.size(26.dp)
                            )
                        }

                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "Real-Time Health Metrics",
                                style = MaterialTheme.typography.titleMedium,
                                color = CardSurfaceLight,
                                fontWeight = FontWeight.Bold
                            )
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(
                                text = "OBD-II live telemetry from 18 vehicle sensors.",
                                style = MaterialTheme.typography.bodyMedium,
                                color = Color.White.copy(alpha = 0.7f)
                            )
                        }
                    }
                }
            }

            // Vehicle Telemetry (Demo data being used for request)
            item {
                Card(
                    shape = RoundedCornerShape(20.dp),
                    colors = CardDefaults.cardColors(containerColor = CardSurfaceLight),
                    border = androidx.compose.foundation.BorderStroke(1.dp, CardBorderLight),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier.padding(20.dp),
                        verticalArrangement = Arrangement.spacedBy(14.dp)
                    ) {
                        Text(
                            text = "Vehicle Telemetry",
                            style = MaterialTheme.typography.titleMedium,
                            color = CharcoalText,
                            fontWeight = FontWeight.Bold
                        )

                        Text(
                            text = "Demo telemetry (real OBD-II not integrated)",
                            fontSize = 11.sp,
                            color = CharcoalMuted,
                            fontStyle = androidx.compose.ui.text.font.FontStyle.Italic
                        )

                        latestTelemetry?.let { telem ->
                            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                TelemetryRow("Engine Temperature", "${String.format(java.util.Locale.US, "%.1f", telem.engineTemperatureC)}°C")
                                TelemetryRow("Battery Voltage", "${String.format(java.util.Locale.US, "%.2f", telem.batteryVoltageV)}V")
                                TelemetryRow("Front Left Tyre", "${String.format(java.util.Locale.US, "%.1f", telem.tyrePressurePsi)} PSI")
                                TelemetryRow("Front Right Tyre", "${String.format(java.util.Locale.US, "%.1f", telem.tyrePressurePsi)} PSI")
                                TelemetryRow("Rear Left Tyre", "${String.format(java.util.Locale.US, "%.1f", telem.tyrePressurePsi)} PSI")
                                TelemetryRow("Rear Right Tyre", "${String.format(java.util.Locale.US, "%.1f", telem.tyrePressurePsi)} PSI")
                                TelemetryRow("Coolant Level", "${telem.coolantLevelPercent.toInt()}%")
                            }
                        } ?: run {
                            Text(
                                text = "No telemetry available. Tap Run Vehicle Check.",
                                fontSize = 12.sp,
                                color = CharcoalMuted
                            )
                        }
                    }
                }
            }

            // Run Vehicle Check Button
            item {
                Button(
                    onClick = {
                        Log.d("AutoRescueDebug", "1 BUTTON CLICKED - DiagnoseScreen")
                        diagnosticsViewModel.runVehicleCheck()
                    },
                    enabled = !backendDiagnosticState.isScanning,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = PrimaryDark,
                        contentColor = CardSurfaceLight,
                        disabledContainerColor = CharcoalSurface
                    ),
                    shape = RoundedCornerShape(16.dp),
                    contentPadding = PaddingValues(vertical = 16.dp),
                    modifier = Modifier
                        .fillMaxWidth()
                        .testTag("run_vehicle_check_button")
                ) {
                    if (backendDiagnosticState.isScanning) {
                        CircularProgressIndicator(
                            color = HealthyGreen,
                            strokeWidth = 2.5.dp,
                            modifier = Modifier.size(20.dp)
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(
                            text = "Scanning Telemetry...",
                            fontWeight = FontWeight.Bold,
                            fontSize = 15.sp
                        )
                    } else {
                        Icon(
                            imageVector = Icons.Default.Build,
                            contentDescription = null,
                            tint = HealthyGreen,
                            modifier = Modifier.size(20.dp)
                        )
                        Spacer(modifier = Modifier.width(10.dp))
                        Text(
                            text = "Run Vehicle Check",
                            fontWeight = FontWeight.Bold,
                            fontSize = 15.sp
                        )
                    }
                }
            }

            // Loading scanning animation overlay card
            if (backendDiagnosticState.isScanning) {
                item {
                    Card(
                        shape = RoundedCornerShape(20.dp),
                        colors = CardDefaults.cardColors(containerColor = PrimaryDark),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(
                            modifier = Modifier
                                .padding(20.dp)
                                .fillMaxWidth(),
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.spacedBy(14.dp)
                        ) {
                            Text(
                                text = backendDiagnosticState.scanStepMessage,
                                color = CardSurfaceLight,
                                fontWeight = FontWeight.Bold,
                                fontSize = 15.sp
                            )

                            LinearProgressIndicator(
                                progress = { backendDiagnosticState.scanProgress },
                                color = HealthyGreen,
                                trackColor = Color.White.copy(alpha = 0.15f),
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(8.dp)
                                    .clip(CircleShape)
                            )
                        }
                    }
                }
            }

            // Diagnostic Results Card (Displays backend result if available)
            backendDiagnosticState.result?.let { result ->
                item {
                    val borderTint = when (result.severity) {
                        HealthStatus.HEALTHY -> HealthyGreen
                        HealthStatus.WARNING -> WarningAmber
                        HealthStatus.CRITICAL -> CriticalRed
                    }
                    val bgTint = when (result.severity) {
                        HealthStatus.HEALTHY -> HealthyGreenBg
                        HealthStatus.WARNING -> WarningAmberBg
                        HealthStatus.CRITICAL -> CriticalRedBg
                    }
                    val iconTint = when (result.severity) {
                        HealthStatus.HEALTHY -> HealthyGreenDark
                        HealthStatus.WARNING -> WarningAmberDark
                        HealthStatus.CRITICAL -> CriticalRedDark
                    }

                    Card(
                        shape = RoundedCornerShape(20.dp),
                        colors = CardDefaults.cardColors(containerColor = CardSurfaceLight),
                        border = androidx.compose.foundation.BorderStroke(1.5.dp, borderTint.copy(alpha = 0.6f)),
                        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
                        modifier = Modifier
                            .fillMaxWidth()
                            .testTag("diagnostic_result_card")
                    ) {
                        Column(
                            modifier = Modifier.padding(20.dp),
                            verticalArrangement = Arrangement.spacedBy(14.dp)
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
                                            .size(36.dp)
                                            .clip(RoundedCornerShape(10.dp))
                                            .background(bgTint),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        Icon(
                                            imageVector = when (result.severity) {
                                                HealthStatus.HEALTHY -> Icons.Default.CheckCircle
                                                HealthStatus.WARNING -> Icons.Default.Warning
                                                HealthStatus.CRITICAL -> Icons.Default.Warning
                                            },
                                            contentDescription = null,
                                            tint = iconTint,
                                            modifier = Modifier.size(20.dp)
                                        )
                                    }
                                    Text(
                                        text = "Diagnostic Summary",
                                        style = MaterialTheme.typography.titleMedium,
                                        color = CharcoalText,
                                        fontWeight = FontWeight.Bold
                                    )
                                }

                                StatusBadge(
                                    status = result.severity,
                                    text = result.severityLabel
                                )
                            }

                            HorizontalDivider(color = CardBorderLight)

                            // Result Item 1: Issue
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Text(
                                    text = "Issue Detected:",
                                    fontWeight = FontWeight.SemiBold,
                                    fontSize = 14.sp,
                                    color = CharcoalMuted
                                )
                                Text(
                                    text = result.issue,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 14.sp,
                                    color = CharcoalText,
                                    modifier = Modifier.weight(1f, fill = false),
                                    textAlign = androidx.compose.ui.text.style.TextAlign.End
                                )
                            }

                            // Result Item 2: Affected Component
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Text(
                                    text = "Affected Component:",
                                    fontWeight = FontWeight.SemiBold,
                                    fontSize = 14.sp,
                                    color = CharcoalMuted
                                )
                                Text(
                                    text = result.affectedComponent,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 14.sp,
                                    color = CharcoalText
                                )
                            }

                            // Result Item 3: Severity
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Text(
                                    text = "Severity:",
                                    fontWeight = FontWeight.SemiBold,
                                    fontSize = 14.sp,
                                    color = CharcoalMuted
                                )
                                Text(
                                    text = result.severityLabel,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 14.sp,
                                    color = iconTint
                                )
                            }

                            // Result Item 4: Safe to drive
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Text(
                                    text = "Safe to drive:",
                                    fontWeight = FontWeight.SemiBold,
                                    fontSize = 14.sp,
                                    color = CharcoalMuted
                                )
                                Text(
                                    text = result.safeToDriveText,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 14.sp,
                                    color = if (result.safeToDrive) HealthyGreenDark else CriticalRedDark
                                )
                            }

                            // Result Item 5: Telemetry Snapshot if present
                            result.telemetry?.let { telem ->
                                Surface(
                                    color = CharcoalSurface,
                                    shape = RoundedCornerShape(12.dp),
                                    modifier = Modifier.fillMaxWidth()
                                ) {
                                    Column(
                                        modifier = Modifier.padding(12.dp),
                                        verticalArrangement = Arrangement.spacedBy(6.dp)
                                    ) {
                                        Text(
                                            text = "Evaluated OBD-II Telemetry",
                                            fontWeight = FontWeight.Bold,
                                            fontSize = 12.sp,
                                            color = HealthyGreen
                                        )
                                        Row(
                                            modifier = Modifier.fillMaxWidth(),
                                            horizontalArrangement = Arrangement.SpaceBetween
                                        ) {
                                            Text("Engine Temp: ${String.format(java.util.Locale.US, "%.1f", telem.engineTemperatureC)}°C", fontSize = 11.sp, color = CardSurfaceLight)
                                            Text("Battery: ${String.format(java.util.Locale.US, "%.2f", telem.batteryVoltageV)}V", fontSize = 11.sp, color = CardSurfaceLight)
                                        }
                                        Row(
                                            modifier = Modifier.fillMaxWidth(),
                                            horizontalArrangement = Arrangement.SpaceBetween
                                        ) {
                                            Text("Tyre PSI: ${String.format(java.util.Locale.US, "%.1f", telem.tyrePressurePsi)} PSI", fontSize = 11.sp, color = CardSurfaceLight)
                                            Text("Coolant: ${telem.coolantLevelPercent.toInt()}%", fontSize = 11.sp, color = CardSurfaceLight)
                                        }
                                    }
                                }
                            }

                            // Result Item 6: Recommendation
                            Surface(
                                color = BackgroundLight,
                                shape = RoundedCornerShape(12.dp)
                            ) {
                                Column(
                                    modifier = Modifier.padding(14.dp),
                                    verticalArrangement = Arrangement.spacedBy(4.dp)
                                ) {
                                    Text(
                                        text = "Recommendation:",
                                        fontWeight = FontWeight.Bold,
                                        fontSize = 13.sp,
                                        color = PrimaryDark
                                    )
                                    Text(
                                        text = result.recommendation,
                                        fontSize = 13.sp,
                                        color = CharcoalText
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
