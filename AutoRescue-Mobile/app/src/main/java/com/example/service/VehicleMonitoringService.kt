package com.example.service

import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Binder
import android.os.IBinder
import com.example.model.DiagnosticResult
import com.example.model.HealthStatus

class VehicleMonitoringService : Service() {

    private val binder = LocalBinder()
    private lateinit var safetyNotificationManager: SafetyNotificationManager

    inner class LocalBinder : Binder() {
        fun getService(): VehicleMonitoringService = this@VehicleMonitoringService
    }

    override fun onCreate() {
        super.onCreate()
        safetyNotificationManager = SafetyNotificationManager(this)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        intent?.let {
            val issue = it.getStringExtra(EXTRA_ISSUE)
            val isCritical = it.getBooleanExtra(EXTRA_IS_CRITICAL, false)
            val safeToDrive = it.getBooleanExtra(EXTRA_SAFE_TO_DRIVE, true)

            if (isCritical && !safeToDrive && !issue.isNullOrEmpty()) {
                safetyNotificationManager.showCriticalAlert(issue)
            }
        }
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder = binder

    fun evaluateDiagnosticResult(result: DiagnosticResult) {
        if (result.severity == HealthStatus.CRITICAL && !result.safeToDrive) {
            safetyNotificationManager.showCriticalAlert(result.issue)
        }
    }

    companion object {
        const val EXTRA_ISSUE = "extra_issue"
        const val EXTRA_IS_CRITICAL = "extra_is_critical"
        const val EXTRA_SAFE_TO_DRIVE = "extra_safe_to_drive"

        fun evaluateAndNotify(context: Context, result: DiagnosticResult) {
            val notificationManager = SafetyNotificationManager(context.applicationContext)
            if (result.severity == HealthStatus.CRITICAL && !result.safeToDrive) {
                notificationManager.showCriticalAlert(result.issue)
            }
        }

        fun startService(context: Context) {
            val intent = Intent(context, VehicleMonitoringService::class.java)
            context.startService(intent)
        }
    }
}
