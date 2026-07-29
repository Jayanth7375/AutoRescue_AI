package com.example.ui.screens

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.DirectionsCar
import androidx.compose.material.icons.filled.LocalGasStation
import androidx.compose.material.icons.filled.Speed
import androidx.compose.material.icons.outlined.Event
import androidx.compose.material.icons.outlined.Pin
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
import com.example.ui.components.StatusBadge
import com.example.ui.theme.*
import com.example.viewmodel.VehicleViewModel

@Composable
fun VehicleScreen(
    viewModel: VehicleViewModel,
    onNavigateToNotifications: () -> Unit,
    onNavigateToProfile: () -> Unit
) {
    val vehicleInfo by viewModel.vehicleInfo.collectAsState()
    val components by viewModel.componentHealthList.collectAsState()
    val notifications by viewModel.notifications.collectAsState()

    Scaffold(
        topBar = {
            AutoRescueHeader(
                title = "Vehicle Profile",
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
            // Vehicle Hero Image & Title
            item {
                Card(
                    shape = RoundedCornerShape(24.dp),
                    colors = CardDefaults.cardColors(containerColor = PrimaryDark),
                    elevation = CardDefaults.cardElevation(defaultElevation = 6.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier.padding(20.dp),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(160.dp)
                                .clip(RoundedCornerShape(18.dp))
                                .background(CharcoalSurface)
                        ) {
                            Image(
                                painter = painterResource(id = R.drawable.img_nexon_vehicle),
                                contentDescription = "Tata Nexon Vehicle",
                                contentScale = ContentScale.Crop,
                                modifier = Modifier.fillMaxSize()
                            )
                        }

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column {
                                Text(
                                    text = vehicleInfo.name,
                                    style = MaterialTheme.typography.displayMedium,
                                    color = CardSurfaceLight,
                                    fontWeight = FontWeight.Bold
                                )
                                Text(
                                    text = "Smart Connected SUV",
                                    fontSize = 13.sp,
                                    color = Color.White.copy(alpha = 0.7f)
                                )
                            }

                            StatusBadge(
                                status = HealthStatus.HEALTHY,
                                text = "HEALTHY"
                            )
                        }
                    }
                }
            }

            // Specs & Details Grid
            item {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text(
                        text = "Vehicle Specifications",
                        style = MaterialTheme.typography.titleMedium,
                        color = CharcoalText,
                        fontWeight = FontWeight.Bold
                    )

                    Card(
                        shape = RoundedCornerShape(20.dp),
                        colors = CardDefaults.cardColors(containerColor = CardSurfaceLight),
                        border = androidx.compose.foundation.BorderStroke(1.dp, CardBorderLight),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(
                            modifier = Modifier.padding(18.dp),
                            verticalArrangement = Arrangement.spacedBy(14.dp)
                        ) {
                            // Registration
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                                ) {
                                    Icon(
                                        imageVector = Icons.Outlined.Pin,
                                        contentDescription = null,
                                        tint = SecondarySlate,
                                        modifier = Modifier.size(20.dp)
                                    )
                                    Text(
                                        text = "Registration",
                                        fontWeight = FontWeight.SemiBold,
                                        fontSize = 14.sp,
                                        color = CharcoalMuted
                                    )
                                }
                                Text(
                                    text = vehicleInfo.registrationNumber,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 15.sp,
                                    color = CharcoalText
                                )
                            }

                            HorizontalDivider(color = CardBorderLight.copy(alpha = 0.6f))

                            // Fuel
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.LocalGasStation,
                                        contentDescription = null,
                                        tint = SecondarySlate,
                                        modifier = Modifier.size(20.dp)
                                    )
                                    Text(
                                        text = "Fuel Type",
                                        fontWeight = FontWeight.SemiBold,
                                        fontSize = 14.sp,
                                        color = CharcoalMuted
                                    )
                                }
                                Text(
                                    text = vehicleInfo.fuelType,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 15.sp,
                                    color = CharcoalText
                                )
                            }

                            HorizontalDivider(color = CardBorderLight.copy(alpha = 0.6f))

                            // Model year
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                                ) {
                                    Icon(
                                        imageVector = Icons.Outlined.Event,
                                        contentDescription = null,
                                        tint = SecondarySlate,
                                        modifier = Modifier.size(20.dp)
                                    )
                                    Text(
                                        text = "Model Year",
                                        fontWeight = FontWeight.SemiBold,
                                        fontSize = 14.sp,
                                        color = CharcoalMuted
                                    )
                                }
                                Text(
                                    text = vehicleInfo.modelYear,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 15.sp,
                                    color = CharcoalText
                                )
                            }

                            HorizontalDivider(color = CardBorderLight.copy(alpha = 0.6f))

                            // Odometer
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.Speed,
                                        contentDescription = null,
                                        tint = SecondarySlate,
                                        modifier = Modifier.size(20.dp)
                                    )
                                    Text(
                                        text = "Odometer",
                                        fontWeight = FontWeight.SemiBold,
                                        fontSize = 14.sp,
                                        color = CharcoalMuted
                                    )
                                }
                                Text(
                                    text = vehicleInfo.odometer,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 15.sp,
                                    color = PrimaryDark
                                )
                            }
                        }
                    }
                }
            }

            // Component Health Breakdown
            item {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text(
                        text = "Component Health Status",
                        style = MaterialTheme.typography.titleMedium,
                        color = CharcoalText,
                        fontWeight = FontWeight.Bold
                    )

                    Card(
                        shape = RoundedCornerShape(20.dp),
                        colors = CardDefaults.cardColors(containerColor = CardSurfaceLight),
                        border = androidx.compose.foundation.BorderStroke(1.dp, CardBorderLight),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(
                            modifier = Modifier.padding(18.dp),
                            verticalArrangement = Arrangement.spacedBy(16.dp)
                        ) {
                            components.forEach { comp ->
                                Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                                    Row(
                                        modifier = Modifier.fillMaxWidth(),
                                        horizontalArrangement = Arrangement.SpaceBetween,
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Text(
                                            text = comp.name,
                                            fontWeight = FontWeight.Bold,
                                            fontSize = 15.sp,
                                            color = CharcoalText
                                        )

                                        Row(
                                            verticalAlignment = Alignment.CenterVertically,
                                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                                        ) {
                                            StatusBadge(
                                                status = comp.status,
                                                text = comp.statusText
                                            )
                                            Text(
                                                text = "${comp.percentage}%",
                                                fontWeight = FontWeight.ExtraBold,
                                                fontSize = 14.sp,
                                                color = CharcoalText
                                            )
                                        }
                                    }

                                    HealthProgressBar(
                                        percentage = comp.percentage,
                                        status = comp.status,
                                        height = 8.dp
                                    )
                                }

                                if (comp != components.last()) {
                                    HorizontalDivider(color = CardBorderLight.copy(alpha = 0.6f))
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
