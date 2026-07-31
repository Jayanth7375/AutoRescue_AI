package com.example.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.model.ChatMessage
import com.example.repository.ChatRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class ChatViewModel(
    private val chatRepository: ChatRepository,
    private val diagnosticsViewModel: DiagnosticsViewModel
) : ViewModel() {

    private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val messages: StateFlow<List<ChatMessage>> = _messages

    private val _inputText = MutableStateFlow("")
    val inputText: StateFlow<String> = _inputText

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error

    init {
        viewModelScope.launch {
            chatRepository.messages.collect { msgs ->
                _messages.value = msgs
            }
        }
        viewModelScope.launch {
            chatRepository.isLoading.collect { loading ->
                _isLoading.value = loading
            }
        }
        viewModelScope.launch {
            chatRepository.error.collect { err ->
                _error.value = err
            }
        }
    }

    fun updateInputText(text: String) {
        _inputText.value = text
    }

    fun sendMessage(vehicleId: String = "TN38CP7375") {
        val text = _inputText.value.trim()
        if (text.isEmpty() || _isLoading.value) return

        // Get latest diagnosis context from DiagnosticsViewModel
        val diagnosticState = diagnosticsViewModel.diagnosticState.value
        val backendResponse = diagnosticState.backendResponse

        val context = if (backendResponse != null) {
            mapOf(
                "status" to (backendResponse.status ?: "UNKNOWN"),
                "diagnosis" to mapOf(
                    "issue" to (backendResponse.diagnosis?.issue ?: ""),
                    "affected_component" to (backendResponse.diagnosis?.affectedComponent ?: ""),
                    "severity" to (backendResponse.diagnosis?.severity ?: "NORMAL"),
                    "safe_to_drive" to (backendResponse.diagnosis?.safeToDrive ?: true),
                    "recommendation" to (backendResponse.diagnosis?.recommendation ?: "")
                ),
                "navigation_allowed" to (backendResponse.navigationAllowed ?: true),
                "rescue" to mapOf(
                    "tow_required" to (backendResponse.rescue?.towRequired ?: false),
                    "assistance_type" to (backendResponse.rescue?.assistanceType ?: "")
                )
            )
        } else {
            emptyMap()
        }

        viewModelScope.launch {
            chatRepository.sendMessage(text, vehicleId, context)
            _inputText.value = ""
        }
    }

    fun clearChat() {
        chatRepository.clearMessages()
    }
}
