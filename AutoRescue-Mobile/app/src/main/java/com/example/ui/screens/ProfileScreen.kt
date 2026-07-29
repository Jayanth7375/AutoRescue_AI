package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.ArrowForwardIos
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.ui.theme.*
import com.example.viewmodel.VehicleViewModel
import com.example.viewmodel.ThemeViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    viewModel: VehicleViewModel,
    themeViewModel: ThemeViewModel = viewModel(),
    onNavigateBack: () -> Unit
) {
    val userProfile by viewModel.userProfile.collectAsState()
    val vehicleInfo by viewModel.vehicleInfo.collectAsState()
    val currentThemeMode by themeViewModel.themeMode.collectAsState()

    var showInfoDialog by remember { mutableStateOf<String?>(null) }
    var showThemeDialog by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        text = "User Profile & Settings",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        color = CharcoalText
                    )
                },
                navigationIcon = {
                    IconButton(
                        onClick = onNavigateBack,
                        modifier = Modifier.testTag("profile_back_button")
                    ) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back",
                            tint = CharcoalText
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = BackgroundLight)
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
            // User Header Card
            item {
                Card(
                    shape = RoundedCornerShape(24.dp),
                    colors = CardDefaults.cardColors(containerColor = PrimaryDark),
                    elevation = CardDefaults.cardElevation(defaultElevation = 6.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(20.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(64.dp)
                                .clip(CircleShape)
                                .background(CharcoalSurface)
                                .border(2.dp, HealthyGreen, CircleShape),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.Person,
                                contentDescription = "Profile Avatar",
                                tint = CardSurfaceLight,
                                modifier = Modifier.size(36.dp)
                            )
                        }

                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = userProfile.name,
                                style = MaterialTheme.typography.titleLarge,
                                color = CardSurfaceLight,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                text = userProfile.email,
                                fontSize = 13.sp,
                                color = Color.White.copy(alpha = 0.7f)
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            Surface(
                                color = HealthyGreen.copy(alpha = 0.2f),
                                shape = RoundedCornerShape(8.dp)
                            ) {
                                Text(
                                    text = "Connected: ${vehicleInfo.name} (${vehicleInfo.registrationNumber})",
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = HealthyGreen,
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp)
                                )
                            }
                        }
                    }
                }
            }

            // Profile Sections List
            item {
                Card(
                    shape = RoundedCornerShape(20.dp),
                    colors = CardDefaults.cardColors(containerColor = CardSurfaceLight),
                    border = androidx.compose.foundation.BorderStroke(1.dp, CardBorderLight),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier.padding(vertical = 8.dp)
                    ) {
                        ProfileSectionItem(
                            icon = Icons.Outlined.Person,
                            title = "Personal Information",
                            subtitle = userProfile.phone,
                            onClick = { showInfoDialog = "Personal Information: ${userProfile.name}, Phone: ${userProfile.phone}, Address: ${userProfile.address}" }
                        )

                        HorizontalDivider(color = CardBorderLight.copy(alpha = 0.6f))

                        ProfileSectionItem(
                            icon = Icons.Outlined.ContactPhone,
                            title = "Emergency Contacts",
                            subtitle = userProfile.emergencyContact,
                            onClick = { showInfoDialog = "Emergency Contact: ${userProfile.emergencyContact}. Auto-notified during critical alerts." }
                        )

                        HorizontalDivider(color = CardBorderLight.copy(alpha = 0.6f))

                        ProfileSectionItem(
                            icon = Icons.Outlined.Notifications,
                            title = "Notifications",
                            subtitle = "OBD-II Telemetry & Rescue Alerts Enabled",
                            onClick = { showInfoDialog = "Push notifications are active for critical health & roadside rescue updates." }
                        )

                        HorizontalDivider(color = CardBorderLight.copy(alpha = 0.6f))

                        ProfileSectionItem(
                            icon = Icons.Outlined.Palette,
                            title = "Appearance",
                            subtitle = when (currentThemeMode) {
                                ThemeMode.LIGHT -> "Light Theme"
                                ThemeMode.DARK -> "Dark Theme"
                                ThemeMode.SYSTEM -> "System Default"
                            },
                            onClick = { showThemeDialog = true }
                        )

                        HorizontalDivider(color = CardBorderLight.copy(alpha = 0.6f))

                        ProfileSectionItem(
                            icon = Icons.Outlined.Security,
                            title = "Privacy & Security",
                            subtitle = "End-to-End OBD-II Telemetry Encryption",
                            onClick = { showInfoDialog = "Your vehicle data is stored locally and encrypted according to ISO 26262 functional safety standards." }
                        )

                        HorizontalDivider(color = CardBorderLight.copy(alpha = 0.6f))

                        ProfileSectionItem(
                            icon = Icons.Outlined.HelpOutline,
                            title = "Help & Support",
                            subtitle = "24/7 Roadside Assistance Desk",
                            onClick = { showInfoDialog = "AutoRescue AI Support Hotline: 1800-RESCUE-AI (1800-737-283)" }
                        )

                        HorizontalDivider(color = CardBorderLight.copy(alpha = 0.6f))

                        ProfileSectionItem(
                            icon = Icons.Outlined.Info,
                            title = "About AutoRescue AI",
                            subtitle = "v1.0.0 (Build 2026.07)",
                            onClick = { showInfoDialog = "AutoRescue AI v1.0.0\nNext-Gen AI Vehicle Safety, OBD-II Diagnostics & Rapid Roadside Rescue Platform." }
                        )
                    }
                }
            }
        }
    }

    showInfoDialog?.let { infoText ->
        AlertDialog(
            onDismissRequest = { showInfoDialog = null },
            title = {
                Text(
                    text = "Profile Info",
                    fontWeight = FontWeight.Bold,
                    color = CharcoalText
                )
            },
            text = {
                Text(
                    text = infoText,
                    color = CharcoalText,
                    fontSize = 14.sp
                )
            },
            confirmButton = {
                TextButton(onClick = { showInfoDialog = null }) {
                    Text("OK", color = HealthyGreenDark, fontWeight = FontWeight.Bold)
                }
            },
            shape = RoundedCornerShape(20.dp),
            containerColor = CardSurfaceLight
        )
    }

    if (showThemeDialog) {
        AlertDialog(
            onDismissRequest = { showThemeDialog = false },
            title = {
                Text(
                    text = "Select Appearance",
                    fontWeight = FontWeight.Bold,
                    color = CharcoalText
                )
            },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    ThemeOption(
                        label = "Light",
                        isSelected = currentThemeMode == ThemeMode.LIGHT,
                        onClick = {
                            themeViewModel.setThemeMode(ThemeMode.LIGHT)
                            showThemeDialog = false
                        }
                    )
                    ThemeOption(
                        label = "Dark",
                        isSelected = currentThemeMode == ThemeMode.DARK,
                        onClick = {
                            themeViewModel.setThemeMode(ThemeMode.DARK)
                            showThemeDialog = false
                        }
                    )
                    ThemeOption(
                        label = "System Default",
                        isSelected = currentThemeMode == ThemeMode.SYSTEM,
                        onClick = {
                            themeViewModel.setThemeMode(ThemeMode.SYSTEM)
                            showThemeDialog = false
                        }
                    )
                }
            },
            confirmButton = {
                TextButton(onClick = { showThemeDialog = false }) {
                    Text("Done", color = HealthyGreenDark, fontWeight = FontWeight.Bold)
                }
            },
            shape = RoundedCornerShape(20.dp),
            containerColor = CardSurfaceLight
        )
    }
}

@Composable
private fun ThemeOption(
    label: String,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(
                if (isSelected)
                    HealthyGreen.copy(alpha = 0.1f)
                else
                    Color.Transparent
            )
            .clickable { onClick() }
            .padding(12.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        RadioButton(
            selected = isSelected,
            onClick = { onClick() },
            colors = RadioButtonDefaults.colors(
                selectedColor = HealthyGreen,
                unselectedColor = CharcoalMuted
            )
        )
        Text(
            text = label,
            color = CharcoalText,
            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal
        )
    }
}

@Composable
private fun ProfileSectionItem(
    icon: ImageVector,
    title: String,
    subtitle: String,
    onClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() }
            .padding(horizontal = 20.dp, vertical = 14.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(14.dp)
    ) {
        Box(
            modifier = Modifier
                .size(40.dp)
                .clip(RoundedCornerShape(12.dp))
                .background(BackgroundLight),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = icon,
                contentDescription = title,
                tint = PrimaryDark,
                modifier = Modifier.size(22.dp)
            )
        }

        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = title,
                fontWeight = FontWeight.Bold,
                fontSize = 15.sp,
                color = CharcoalText
            )
            Text(
                text = subtitle,
                fontSize = 12.sp,
                color = CharcoalMuted
            )
        }

        Icon(
            imageVector = Icons.AutoMirrored.Filled.ArrowForwardIos,
            contentDescription = null,
            tint = CharcoalMuted,
            modifier = Modifier.size(14.dp)
        )
    }
}
