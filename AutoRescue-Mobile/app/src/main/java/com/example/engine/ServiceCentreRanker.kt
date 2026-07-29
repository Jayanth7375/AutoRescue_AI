package com.example.engine

import com.example.model.HealthStatus
import com.example.model.ServiceCentre
import java.util.Locale
import kotlin.math.ln

object ServiceCentreRanker {

    fun rank(
        centres: List<ServiceCentre>,
        issueType: String? = null,
        severity: HealthStatus? = null
    ): List<ServiceCentre> {
        if (centres.isEmpty()) return emptyList()

        val isCritical = severity == HealthStatus.CRITICAL
        val isWarning = severity == HealthStatus.WARNING
        val isUrgent = isCritical || isWarning

        // Weights configuration
        val (wDistance, wRating, wOpen, wIssue, wReview) = when {
            isCritical -> Quintuple(0.25, 0.10, 0.35, 0.25, 0.05)
            isWarning -> Quintuple(0.28, 0.17, 0.25, 0.20, 0.10)
            else -> Quintuple(0.30, 0.25, 0.20, 0.15, 0.10)
        }

        // Distance min/max normalization
        val distances = centres.map { it.distanceKm }
        val minDist = distances.minOrNull() ?: 0.0
        val maxDist = distances.maxOrNull() ?: 0.0

        val rankedCentres = centres.map { centre ->
            // 1. Distance score (0.0 to 1.0) - closer is better
            val distanceNorm = if (maxDist > minDist) {
                1.0 - ((centre.distanceKm - minDist) / (maxDist - minDist))
            } else {
                1.0
            }

            // 2. Rating score (0.0 to 1.0)
            val ratingNorm = ((centre.rating ?: 3.8) / 5.0).coerceIn(0.0, 1.0)

            // 3. Open status score (0.0 to 1.0)
            val openNorm = when (centre.isOpen) {
                true -> 1.0
                false -> 0.0
                null -> 0.5
            }

            // 4. Issue relevance score (0.0 to 1.0)
            val (issueNorm, issueMatchLabel) = evaluateIssueRelevance(centre, issueType)

            // 5. Review confidence score (0.0 to 1.0)
            val reviews = centre.reviewCount ?: 0
            val reviewNorm = if (reviews > 0) {
                (ln(reviews.toDouble() + 1.0) / ln(250.0)).coerceIn(0.0, 1.0)
            } else {
                0.3
            }

            // Base weighted total (0.0 to 100.0)
            var totalScore = (
                wDistance * distanceNorm +
                wRating * ratingNorm +
                wOpen * openNorm +
                wIssue * issueNorm +
                wReview * reviewNorm
            ) * 100.0

            // Closed penalty for urgent cases (open centres strongly outrank closed centres)
            if (isUrgent && centre.isOpen == false) {
                totalScore *= 0.35
            } else if (centre.isOpen == false) {
                totalScore *= 0.70
            }

            val finalPriorityScore = ((totalScore * 10).toInt() / 10.0).coerceIn(0.0, 100.0)

            val reason = buildShortReason(
                centre = centre,
                issueMatchLabel = issueMatchLabel
            )

            centre.copy(
                priorityScore = finalPriorityScore,
                matchReason = reason
            )
        }.sortedByDescending { it.priorityScore }
            .take(10)

        // Mark top 1 as recommended and append "Recommended" if top result
        return rankedCentres.mapIndexed { index, centre ->
            if (index == 0 && rankedCentres.isNotEmpty()) {
                centre.copy(
                    isRecommended = true,
                    matchReason = "Recommended • ${centre.matchReason}"
                )
            } else {
                centre.copy(isRecommended = false)
            }
        }
    }

    private fun evaluateIssueRelevance(
        centre: ServiceCentre,
        issueType: String?
    ): Pair<Double, String> {
        val issue = issueType?.lowercase(Locale.US) ?: ""
        val types = centre.placeTypes.map { it.lowercase(Locale.US) }
        val name = centre.name.lowercase(Locale.US)

        return when {
            // Tyre issues
            issue.contains("tyre") || issue.contains("tire") || issue.contains("flat") || issue.contains("puncture") || issue.contains("wheel") -> {
                val matchesTyreShop = types.any { it.contains("tyre") || it.contains("tire") } || name.contains("tyre") || name.contains("tire") || name.contains("wheel") || name.contains("vulcaniz")
                val matchesRepair = types.any { it.contains("car_repair") || it.contains("auto_repair") } || name.contains("repair") || name.contains("auto") || name.contains("garage") || name.contains("mechanic")
                when {
                    matchesTyreShop -> Pair(1.0, "Matches tyre issue")
                    matchesRepair -> Pair(0.85, "Matches tyre issue")
                    else -> Pair(0.40, "General service")
                }
            }

            // Engine, Coolant, Brake, Battery issues
            issue.contains("engine") || issue.contains("coolant") || issue.contains("brake") || issue.contains("battery") || issue.contains("breakdown") || issue.contains("oil") -> {
                val matchesAutoRepair = types.any { it.contains("car_repair") || it.contains("auto_repair") } || name.contains("repair") || name.contains("garage") || name.contains("service") || name.contains("mechanic") || name.contains("auto")
                val issueTopic = when {
                    issue.contains("engine") -> "engine"
                    issue.contains("coolant") -> "coolant"
                    issue.contains("brake") -> "brake"
                    issue.contains("battery") -> "battery"
                    else -> "breakdown"
                }
                when {
                    matchesAutoRepair -> Pair(1.0, "Matches $issueTopic issue")
                    types.any { it.contains("car_dealer") } -> Pair(0.75, "Matches $issueTopic issue")
                    else -> Pair(0.40, "General service")
                }
            }

            else -> {
                val isAutoRepair = types.any { it.contains("car_repair") || it.contains("auto_repair") } || name.contains("repair") || name.contains("auto") || name.contains("garage")
                if (isAutoRepair) Pair(0.85, "Auto repair expert") else Pair(0.60, "Service centre")
            }
        }
    }

    private fun buildShortReason(
        centre: ServiceCentre,
        issueMatchLabel: String
    ): String {
        val openText = when (centre.isOpen) {
            true -> "Open now"
            false -> "Closed"
            null -> "Status unknown"
        }

        val distText = "${String.format(Locale.US, "%.1f", centre.distanceKm)} km"

        val ratingText = if (centre.rating != null) {
            "${centre.rating} stars"
        } else {
            "3.8 stars"
        }

        return "$openText • $distText • $ratingText • $issueMatchLabel"
    }

    private data class Quintuple<A, B, C, D, E>(
        val first: A,
        val second: B,
        val third: C,
        val fourth: D,
        val fifth: E
    )
}
