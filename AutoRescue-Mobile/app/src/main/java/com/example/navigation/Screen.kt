package com.example.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.DirectionsCar
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.MedicalServices
import androidx.compose.material.icons.outlined.Build
import androidx.compose.material.icons.outlined.DirectionsCar
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.MedicalServices
import androidx.compose.ui.graphics.vector.ImageVector

sealed class Screen(
    val route: String,
    val title: String,
    val selectedIcon: ImageVector? = null,
    val unselectedIcon: ImageVector? = null
) {
    object Splash : Screen("splash", "Splash")
    object Home : Screen("home", "Home", Icons.Filled.Home, Icons.Outlined.Home)
    object Diagnose : Screen("diagnose", "Diagnose", Icons.Filled.Build, Icons.Outlined.Build)
    object Rescue : Screen("rescue", "Rescue", Icons.Filled.MedicalServices, Icons.Outlined.MedicalServices)
    object Vehicle : Screen("vehicle", "Vehicle", Icons.Filled.DirectionsCar, Icons.Outlined.DirectionsCar)
    object Notifications : Screen("notifications", "Notifications")
    object Profile : Screen("profile", "Profile")
    object Chat : Screen("chat", "Chat")
}

val bottomNavScreens = listOf(
    Screen.Home,
    Screen.Diagnose,
    Screen.Rescue,
    Screen.Vehicle
)
