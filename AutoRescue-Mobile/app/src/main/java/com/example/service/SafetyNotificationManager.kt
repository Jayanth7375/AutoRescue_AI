package com.example.service

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.media.AudioAttributes
import android.media.RingtoneManager
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import com.example.MainActivity
import com.example.R

class SafetyNotificationManager(private val context: Context) {

    companion object {
        const val CHANNEL_WARNINGS_ID = "vehicle_warnings_channel"
        const val CHANNEL_CRITICAL_ID = "critical_alerts_channel"

        const val CHANNEL_WARNINGS_NAME = "Vehicle Warnings"
        const val CHANNEL_CRITICAL_NAME = "Critical Vehicle Alerts"

        private const val CRITICAL_NOTIFICATION_ID = 9001

        @Volatile
        private var lastNotifiedIssue: String? = null
        private var lastNotificationTime: Long = 0L
    }

    init {
        createNotificationChannels()
    }

    fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val notificationManager =
                context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

            // 1. Vehicle Warnings Channel
            val warningsChannel = NotificationChannel(
                CHANNEL_WARNINGS_ID,
                CHANNEL_WARNINGS_NAME,
                NotificationManager.IMPORTANCE_DEFAULT
            ).apply {
                description = "General vehicle status updates and non-critical warnings"
            }

            // 2. Critical Vehicle Alerts Channel
            val criticalChannel = NotificationChannel(
                CHANNEL_CRITICAL_ID,
                CHANNEL_CRITICAL_NAME,
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "High-priority critical safety alerts requiring immediate driver action"
                enableLights(true)
                enableVibration(true)
                vibrationPattern = longArrayOf(0, 500, 250, 500)
                val soundUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)
                val audioAttributes = AudioAttributes.Builder()
                    .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                    .setUsage(AudioAttributes.USAGE_NOTIFICATION)
                    .build()
                setSound(soundUri, audioAttributes)
            }

            notificationManager.createNotificationChannel(warningsChannel)
            notificationManager.createNotificationChannel(criticalChannel)
        }
    }

    fun showCriticalAlert(issue: String) {
        val currentTime = System.currentTimeMillis()
        // Avoid sending duplicate notifications repeatedly for the same issue (60s cooldown for identical issue)
        if (issue == lastNotifiedIssue && (currentTime - lastNotificationTime) < 60_000) {
            return
        }

        lastNotifiedIssue = issue
        lastNotificationTime = currentTime

        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
            putExtra("navigate_to", "diagnose")
        }

        val pendingIntent = PendingIntent.getActivity(
            context,
            CRITICAL_NOTIFICATION_ID,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notificationBody = "$issue. Your vehicle may NOT be safe to drive. Stop in a safe location."

        val builder = NotificationCompat.Builder(context, CHANNEL_CRITICAL_ID)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setContentTitle("CRITICAL VEHICLE ALERT")
            .setContentText(notificationBody)
            .setStyle(NotificationCompat.BigTextStyle().bigText(notificationBody))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setDefaults(NotificationCompat.DEFAULT_ALL)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)

        try {
            val notificationManager = NotificationManagerCompat.from(context)
            notificationManager.notify(CRITICAL_NOTIFICATION_ID, builder.build())
        } catch (e: SecurityException) {
            e.printStackTrace()
        }
    }

    fun clearDuplicateCache() {
        lastNotifiedIssue = null
        lastNotificationTime = 0L
    }
}
