package com.example.repository

import com.example.model.ChatMessage
import com.example.model.ChatRequest
import com.example.model.ChatResponse
import com.example.model.ChatRole
import com.example.network.AutoRescueApi
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import javax.inject.Inject

class ChatRepository @Inject constructor(
    private val api: AutoRescueApi
) {
    private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val messages: StateFlow<List<ChatMessage>> = _messages

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error

    fun clearMessages() {
        _messages.value = emptyList()
        _error.value = null
    }

    suspend fun sendMessage(
        message: String,
        vehicleId: String,
        context: Map<String, Any>? = null
    ) {
        try {
            _isLoading.value = true
            _error.value = null

            // Add user message
            val userMessage = ChatMessage(
                text = message,
                role = ChatRole.USER
            )
            _messages.value = _messages.value + userMessage

            // Send to backend
            val request = ChatRequest(
                message = message,
                vehicle_id = vehicleId,
                context = context
            )

            val response = api.sendChatMessage(request)

            // Add assistant message
            val assistantMessage = ChatMessage(
                text = response.reply,
                role = ChatRole.ASSISTANT
            )
            _messages.value = _messages.value + assistantMessage

        } catch (e: Exception) {
            _error.value = e.message ?: "Failed to send message"

            // Add error message from assistant
            val errorMessage = ChatMessage(
                text = "Sorry, I couldn't process that. Please try again.",
                role = ChatRole.ASSISTANT
            )
            _messages.value = _messages.value + errorMessage

        } finally {
            _isLoading.value = false
        }
    }

    fun getMessages(): Flow<List<ChatMessage>> = messages
}
