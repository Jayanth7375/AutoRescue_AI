package com.example.navigation

import android.content.pm.PackageManager
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.core.content.ContextCompat
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.example.ui.components.AutoRescueBottomBar
import com.example.ui.screens.*
import com.example.viewmodel.DiagnosticsViewModel
import com.example.viewmodel.VehicleViewModel

@Composable
fun AutoRescueMainApp(
    navController: NavHostController = rememberNavController(),
    vehicleViewModel: VehicleViewModel = viewModel(),
    diagnosticsViewModel: DiagnosticsViewModel = viewModel(),
    initialRoute: String? = null
) {
    val context = LocalContext.current

    // Request POST_NOTIFICATIONS permission on Android 13+
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        val notificationPermissionLauncher = rememberLauncherForActivityResult(
            ActivityResultContracts.RequestPermission()
        ) { /* permission handle result */ }

        LaunchedEffect(Unit) {
            val hasPermission = ContextCompat.checkSelfPermission(
                context,
                android.Manifest.permission.POST_NOTIFICATIONS
            ) == PackageManager.PERMISSION_GRANTED

            if (!hasPermission) {
                notificationPermissionLauncher.launch(android.Manifest.permission.POST_NOTIFICATIONS)
            }
        }
    }

    LaunchedEffect(initialRoute) {
        if (!initialRoute.isNullOrEmpty()) {
            navController.navigate(initialRoute) {
                popUpTo(Screen.Home.route) {
                    saveState = true
                }
                launchSingleTop = true
                restoreState = true
            }
        }
    }
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route ?: Screen.Splash.route

    val isBottomBarVisible = currentRoute in listOf(
        Screen.Home.route,
        Screen.Diagnose.route,
        Screen.Assistant.route,
        Screen.Rescue.route,
        Screen.Vehicle.route
    )

    Scaffold(
        bottomBar = {
            if (isBottomBarVisible) {
                AutoRescueBottomBar(
                    currentRoute = currentRoute,
                    onNavigateToRoute = { route ->
                        if (currentRoute != route) {
                            navController.navigate(route) {
                                popUpTo(Screen.Home.route) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        }
                    }
                )
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.Splash.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Screen.Splash.route) {
                SplashScreen(
                    onSplashFinished = {
                        navController.navigate(Screen.Home.route) {
                            popUpTo(Screen.Splash.route) { inclusive = true }
                        }
                    }
                )
            }

            composable(Screen.Home.route) {
                HomeScreen(
                    vehicleViewModel = vehicleViewModel,
                    diagnosticsViewModel = diagnosticsViewModel,
                    onNavigateToDiagnose = { navController.navigate(Screen.Diagnose.route) },
                    onNavigateToRescue = { navController.navigate(Screen.Rescue.route) },
                    onNavigateToNotifications = { navController.navigate(Screen.Notifications.route) },
                    onNavigateToProfile = { navController.navigate(Screen.Profile.route) }
                )
            }

            composable(Screen.Diagnose.route) {
                DiagnoseScreen(
                    vehicleViewModel = vehicleViewModel,
                    diagnosticsViewModel = diagnosticsViewModel,
                    onNavigateToNotifications = { navController.navigate(Screen.Notifications.route) },
                    onNavigateToProfile = { navController.navigate(Screen.Profile.route) }
                )
            }

            composable(Screen.Assistant.route) {
                ChatScreen(
                    diagnosticsViewModel = diagnosticsViewModel
                )
            }

            composable(Screen.Rescue.route) {
                RescueScreen(
                    vehicleViewModel = vehicleViewModel,
                    diagnosticsViewModel = diagnosticsViewModel,
                    onNavigateToNotifications = { navController.navigate(Screen.Notifications.route) },
                    onNavigateToProfile = { navController.navigate(Screen.Profile.route) }
                )
            }

            composable(Screen.Vehicle.route) {
                VehicleScreen(
                    viewModel = vehicleViewModel,
                    onNavigateToNotifications = { navController.navigate(Screen.Notifications.route) },
                    onNavigateToProfile = { navController.navigate(Screen.Profile.route) }
                )
            }

            composable(Screen.Notifications.route) {
                NotificationsScreen(
                    vehicleViewModel = vehicleViewModel,
                    diagnosticsViewModel = diagnosticsViewModel,
                    onNavigateBack = { navController.popBackStack() }
                )
            }

            composable(Screen.Profile.route) {
                ProfileScreen(
                    viewModel = vehicleViewModel,
                    onNavigateBack = { navController.popBackStack() }
                )
            }

        }
    }
}
