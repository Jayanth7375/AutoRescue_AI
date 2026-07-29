package com.example.model

import java.util.UUID

enum class ChatRole {
    USER,
    ASSISTANT
}

data class ChatMessage(
    val id: String = UUID.randomUUID().toString(),
    val text: String,
    val role: ChatRole,
    val timestamp: Long = System.currentTimeMillis()
)

data class ChatRequest(
    val message: String,
    val vehicle_id: String,
    val context: Map<String, Any>? = null
)

data class ChatResponse(
    val reply: String,
    val suggested_actions: List<String> = emptyList()
)
