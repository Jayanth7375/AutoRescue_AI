package com.example

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.navigation.AutoRescueMainApp
import com.example.navigation.Screen
import com.example.ui.theme.AutoRescueTheme
import com.example.viewmodel.ThemeViewModel

class MainActivity : ComponentActivity() {

    private val initialRouteState = mutableStateOf<String?>(null)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handleNavigateIntent(intent)
        enableEdgeToEdge()
        setContent {
            val themeViewModel: ThemeViewModel = viewModel()
            val themeMode by themeViewModel.themeMode.collectAsState()

            AutoRescueTheme(themeMode = themeMode) {
                AutoRescueMainApp(
                    initialRoute = initialRouteState.value
                )
            }
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        handleNavigateIntent(intent)
    }

    private fun handleNavigateIntent(intent: Intent?) {
        val destination = intent?.getStringExtra("navigate_to")
        if (destination == "diagnose") {
            initialRouteState.value = Screen.Diagnose.route
        }
    }
}
