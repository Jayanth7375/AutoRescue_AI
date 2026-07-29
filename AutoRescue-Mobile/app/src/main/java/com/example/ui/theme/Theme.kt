package com.example.ui.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

private val LightColorScheme = lightColorScheme(
    primary = PrimaryAccent,
    onPrimary = Color(0xFFFFFFFF),
    primaryContainer = Color(0xFFE0F7F0),
    onPrimaryContainer = PrimaryAccentLight,
    secondary = SecondarySlate,
    onSecondary = Color(0xFFFFFFFF),
    tertiary = WarningAmber,
    background = BackgroundLight,
    onBackground = CharcoalText,
    surface = SurfaceLight,
    onSurface = CharcoalText,
    surfaceVariant = SurfaceVariantLight,
    onSurfaceVariant = CharcoalMuted,
    outline = CardBorderLight,
    outlineVariant = Color(0xFFD0D5DD),
    error = CriticalRed,
    onError = Color(0xFFFFFFFF)
)

private val DarkColorScheme = darkColorScheme(
    primary = PrimaryAccentDark,
    onPrimary = CharcoalDark,
    primaryContainer = Color(0xFF0F3A2A),
    onPrimaryContainer = PrimaryAccentDark,
    secondary = TextSecondaryDark,
    onSecondary = CharcoalDark,
    tertiary = WarningAmberDarkBg,
    background = CharcoalDark,
    onBackground = TextLightDark,
    surface = CharcoalSurface,
    onSurface = TextLightDark,
    surfaceVariant = SurfaceVariantDark,
    onSurfaceVariant = TextSecondaryDark,
    outline = OutlineDark,
    outlineVariant = Color(0xFF464F59),
    error = CriticalRed,
    onError = Color(0xFFFFFFFF)
)

@Composable
fun AutoRescueTheme(
    themeMode: ThemeMode = ThemeMode.SYSTEM,
    content: @Composable () -> Unit
) {
    val darkTheme = when (themeMode) {
        ThemeMode.LIGHT -> false
        ThemeMode.DARK -> true
        ThemeMode.SYSTEM -> isSystemInDarkTheme()
    }
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.background.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = !darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
