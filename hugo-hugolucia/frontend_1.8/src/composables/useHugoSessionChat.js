import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import api, { fetchWithAuth } from '../api/client'
import { extractNumberedQuestions, resolveAssistantContent } from '../utils/assistantVariants'
import { consumeSseBuffer, parseSseEventBlock } from '../utils/messageStream'

const STREAMING_COPY = {
  learner: {
    messages: [
      'Hugo analyse ta réponse...',
      'Hugo réfléchit...',
      'Hugo prépare sa réponse...',
    ],
    sendError: 'Ton message n’a pas pu être envoyé.',
  },
  neutral: {
    messages: [
      'Hugo analyse votre message...',
      'Hugo réfléchit...',
      'Hugo prépare sa réponse...',
    ],
    sendError: 'Le message n’a pas pu être envoyé.',
  },
}

const STREAMING_STATUS_BADGES = ['Analyse', 'Réflexion', 'Réponse']

/**
 * Noyau conversationnel partagé (session, messages, envoi, stream SSE).
 * Ne porte pas la logique apprenante (posture, progression, CTA, traces).
 *
 * @param {import('vue').Ref<string>|string} sessionIdRef
 * @param {{
 *   loadUiState?: boolean,
 *   loadLearnerArtifacts?: boolean,
 *   streamingPersona?: 'learner' | 'neutral',
 *   getUiStateParams?: () => Record<string, string>,
 *   onSessionLoaded?: (session: object) => void | Promise<void>,
 * }} options
 */
export function useHugoSessionChat(sessionIdRef, options = {}) {
  const loadUiState = options.loadUiState ?? false
  const loadLearnerArtifacts = options.loadLearnerArtifacts ?? false
  const streamingPersona = options.streamingPersona === 'learner' ? 'learner' : 'neutral'
  const streamingMessages = STREAMING_COPY[streamingPersona].messages
  const sendErrorFallback = STREAMING_COPY[streamingPersona].sendError

  const loading = ref(true)
  const refreshing = ref(false)
  const sendingMessage = ref(false)
  const isStreaming = ref(false)
  const hasStreamingChunk = ref(false)
  const session = ref(null)
  const messages = ref([])
  const groups = ref([])
  const sessionUiState = ref(null)
  const uiStateLoading = ref(false)
  const uiStateError = ref(null)
  const error = ref('')
  const streamError = ref('')
  const streamingText = ref('')
  const streamStartedAt = ref('')
  const streamAbortController = ref(null)
  const streamStatusTimer = ref(null)
  const streamStatusIndex = ref(0)
  const streamStatusLabel = ref('')
  const streamStatusMessageText = ref('')
  const streamStatusPhaseLabel = ref('')
  const hasBackendStreamStatus = ref(false)
  const messageContent = ref('')
  const conversationFeedRef = ref(null)
  const isThreadPinnedToBottom = ref(true)

  const resolvedSessionId = computed(() => String(
    typeof sessionIdRef === 'object' && sessionIdRef?.value != null
      ? sessionIdRef.value
      : sessionIdRef,
  ).trim())

  const streamingStatusMessage = computed(() => {
    if (hasBackendStreamStatus.value && streamStatusMessageText.value) {
      return streamStatusMessageText.value
    }
    return streamingMessages[streamStatusIndex.value] || streamingMessages[0]
  })

  const streamingStatusBadge = computed(() => (
    streamStatusLabel.value || STREAMING_STATUS_BADGES[streamStatusIndex.value] || STREAMING_STATUS_BADGES[0]
  ))

  const streamingStatusMode = computed(() => (
    hasBackendStreamStatus.value ? 'Signal réel' : 'Préparation'
  ))

  const shouldAnchorThread = computed(() => isStreaming.value && !hasStreamingChunk.value)

  const streamingAssistantMessage = computed(() => {
    if (!isStreaming.value) return null
    const content = hasStreamingChunk.value
      ? streamingText.value
      : streamingStatusMessage.value
    return {
      id: 'streaming-assistant',
      role: 'ASSISTANT',
      content,
      displayContent: content,
      created_at: streamStartedAt.value || new Date().toISOString(),
      isStreaming: true,
      isPlaceholder: !hasStreamingChunk.value,
    }
  })

  const displayMessages = computed(() => {
    const persisted = messages.value.map((message) => ({
      ...message,
      displayContent: resolveAssistantContent(message),
    }))
    if (streamingAssistantMessage.value) persisted.push(streamingAssistantMessage.value)
    return persisted
  })

  const lastAssistantMessage = computed(() => {
    for (let index = displayMessages.value.length - 1; index >= 0; index -= 1) {
      const message = displayMessages.value[index]
      if (message.role === 'ASSISTANT') return message
    }
    return null
  })

  const questionHints = computed(() => (
    isStreaming.value ? [] : extractNumberedQuestions(lastAssistantMessage.value?.displayContent || '')
  ))

  function resolveThreadElement() {
    const exposed = conversationFeedRef.value?.threadRef
    if (exposed) return exposed.value ?? exposed
    return null
  }

  function updateThreadPinnedState() {
    const element = resolveThreadElement()
    if (!element) return
    const { scrollTop, clientHeight, scrollHeight } = element
    isThreadPinnedToBottom.value = scrollTop + clientHeight >= scrollHeight - 24
  }

  async function scrollThreadToBottom({ force = false } = {}) {
    await nextTick()
    const element = resolveThreadElement()
    if (element && (force || isThreadPinnedToBottom.value)) {
      element.scrollTop = element.scrollHeight
      updateThreadPinnedState()
    }
  }

  async function loadGroups() {
    const { data } = await api.get('/groups/')
    groups.value = Array.isArray(data) ? data : (data.results || [])
  }

  async function loadSession() {
    const { data } = await api.get(`/hugo/sessions/${resolvedSessionId.value}/`)
    session.value = data
    if (typeof options.onSessionLoaded === 'function') {
      await options.onSessionLoaded(data)
    }
  }

  async function loadMessages() {
    const { data } = await api.get(`/hugo/sessions/${resolvedSessionId.value}/messages/`)
    messages.value = data.messages || []
    await scrollThreadToBottom()
  }

  function hasValidUiStateContract(data) {
    return Boolean(data && typeof data === 'object' && data.scene_label && data.conversation_mode)
  }

  async function loadSessionUiState() {
    if (!loadUiState) return
    uiStateLoading.value = true
    uiStateError.value = null
    try {
      const extraParams = typeof options.getUiStateParams === 'function'
        ? options.getUiStateParams()
        : {}
      const { data } = await api.get(`/hugo/sessions/${resolvedSessionId.value}/ui-state/`, {
        params: extraParams,
      })
      if (hasValidUiStateContract(data)) {
        sessionUiState.value = data
      } else if (!sessionUiState.value) {
        sessionUiState.value = null
        uiStateError.value = 'Impossible de charger le pilotage pour l’instant.'
      } else {
        uiStateError.value = 'Impossible de charger le pilotage pour l’instant.'
      }
    } catch (err) {
      if (!sessionUiState.value) {
        sessionUiState.value = null
      }
      uiStateError.value = err.response?.data?.detail
        || 'Impossible de charger le pilotage pour l’instant.'
    } finally {
      uiStateLoading.value = false
    }
  }

  const reloadUiState = loadSessionUiState

  function resetStreamingState() {
    isStreaming.value = false
    hasStreamingChunk.value = false
    streamError.value = ''
    streamingText.value = ''
    streamStartedAt.value = ''
    streamStatusIndex.value = 0
    streamStatusLabel.value = ''
    streamStatusMessageText.value = ''
    streamStatusPhaseLabel.value = ''
    hasBackendStreamStatus.value = false
    if (streamStatusTimer.value) {
      clearInterval(streamStatusTimer.value)
      streamStatusTimer.value = null
    }
    streamAbortController.value = null
  }

  function abortStreaming() {
    streamAbortController.value?.abort()
  }

  function isAbortError(errorLike) {
    return errorLike?.name === 'AbortError'
  }

  function shouldFallbackToNonStreaming(errorLike) {
    const statusCode = Number(errorLike?.status || errorLike?.response?.status || 0)
    return [404, 405, 406, 415, 501].includes(statusCode) || errorLike?.code === 'stream_unsupported'
  }

  function toErrorMessage(errorLike, fallbackMessage) {
    return errorLike?.response?.data?.detail || errorLike?.message || fallbackMessage
  }

  async function sendMessageNonStreaming(content) {
    await api.post(`/hugo/sessions/${resolvedSessionId.value}/messages/`, { content })
  }

  async function sendMessageWithStreaming(content) {
    isStreaming.value = true
    hasStreamingChunk.value = false
    streamError.value = ''
    streamingText.value = ''
    streamStartedAt.value = new Date().toISOString()
    streamStatusIndex.value = 0
    streamStatusLabel.value = STREAMING_STATUS_BADGES[0]
    streamStatusMessageText.value = ''
    streamStatusPhaseLabel.value = ''
    hasBackendStreamStatus.value = false
    const controller = new AbortController()
    streamAbortController.value = controller
    await scrollThreadToBottom({ force: true })
    if (streamStatusTimer.value) clearInterval(streamStatusTimer.value)
    streamStatusTimer.value = setInterval(() => {
      if (hasStreamingChunk.value) return
      streamStatusIndex.value = (streamStatusIndex.value + 1) % streamingMessages.length
      scrollThreadToBottom()
    }, 1800)

    const response = await fetchWithAuth(`/hugo/sessions/${resolvedSessionId.value}/messages/stream/`, {
      method: 'POST',
      signal: controller.signal,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    })

    if ([404, 405, 406, 415, 501].includes(response.status)) {
      const err = new Error('Streaming indisponible sur ce backend.')
      err.status = response.status
      throw err
    }

    if (!response.ok) {
      let detail = 'Le streaming a échoué.'
      try {
        const contentType = String(response.headers.get('content-type') || '')
        if (contentType.includes('application/json')) {
          const payload = await response.json()
          detail = payload?.detail || detail
        }
      } catch {
        /* ignore */
      }
      const err = new Error(detail)
      err.status = response.status
      throw err
    }

    const contentType = String(response.headers.get('content-type') || '')
    if (!contentType.includes('text/event-stream')) {
      const err = new Error('Réponse non streaming.')
      err.code = 'stream_unsupported'
      throw err
    }

    const reader = response.body?.getReader()
    if (!reader) {
      const err = new Error('Flux navigateur indisponible.')
      err.code = 'stream_unsupported'
      throw err
    }

    const decoder = new TextDecoder()
    let buffer = ''
    let sawDone = false

    const processEvent = async (eventPayload) => {
      if (!eventPayload) return
      if (eventPayload.event === 'status') {
        hasBackendStreamStatus.value = true
        streamStatusLabel.value = String(eventPayload.data?.label || streamStatusLabel.value || '')
        streamStatusMessageText.value = String(eventPayload.data?.message || '')
        streamStatusPhaseLabel.value = String(eventPayload.data?.phase_label || streamStatusPhaseLabel.value || '')
        if (streamStatusTimer.value) {
          clearInterval(streamStatusTimer.value)
          streamStatusTimer.value = null
        }
        await scrollThreadToBottom()
        return
      }
      if (eventPayload.event === 'chunk') {
        const text = String(eventPayload.data?.text || '')
        if (!text) return
        hasStreamingChunk.value = true
        streamingText.value += text
        await scrollThreadToBottom()
        return
      }
      if (eventPayload.event === 'error') {
        streamError.value = String(eventPayload.data?.detail || 'Le streaming a rencontré une erreur.')
        return
      }
      if (eventPayload.event === 'done') {
        sawDone = true
        const finalContent = String(eventPayload.data?.content || '')
        if (finalContent) {
          streamingText.value = finalContent
          await scrollThreadToBottom()
        }
      }
    }

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const parsed = consumeSseBuffer(buffer)
      buffer = parsed.remainder
      for (const eventPayload of parsed.events) {
        await processEvent(eventPayload)
      }
    }

    buffer += decoder.decode()
    if (buffer.trim()) {
      await processEvent(parseSseEventBlock(buffer))
    }

    if (!sawDone && streamError.value) {
      const err = new Error(streamError.value)
      err.status = 502
      throw err
    }
  }

  async function refreshConversation() {
    await Promise.all([
      loadSession(),
      loadMessages(),
      loadSessionUiState(),
    ])
  }

  async function sendMessage() {
    const content = String(messageContent.value || '').trim()
    if (!content || sendingMessage.value) return
    sendingMessage.value = true
    error.value = ''
    streamError.value = ''
    try {
      try {
        await sendMessageWithStreaming(content)
      } catch (err) {
        if (isAbortError(err)) return
        if (shouldFallbackToNonStreaming(err)) {
          resetStreamingState()
          await sendMessageNonStreaming(content)
        } else {
          throw err
        }
      }
      messageContent.value = ''
      await refreshConversation()
    } catch (err) {
      if (!isAbortError(err)) {
        error.value = toErrorMessage(err, sendErrorFallback)
      }
    } finally {
      resetStreamingState()
      sendingMessage.value = false
    }
  }

  async function loadWorkspace({ silent = false } = {}) {
    if (silent) refreshing.value = true
    else loading.value = true
    error.value = ''
    try {
      const tasks = [loadSession(), loadMessages()]
      if (loadUiState) tasks.push(loadSessionUiState())
      if (loadLearnerArtifacts) tasks.push(loadGroups())
      await Promise.all(tasks)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Impossible de charger cette session.'
    } finally {
      if (silent) refreshing.value = false
      else loading.value = false
    }
  }

  watch(resolvedSessionId, (nextId, prevId) => {
    if (!nextId) return
    if (prevId && nextId === prevId) return
    abortStreaming()
    resetStreamingState()
    loadWorkspace()
  }, { immediate: true })

  onBeforeUnmount(() => {
    abortStreaming()
  })

  return {
    loading,
    refreshing,
    sendingMessage,
    isStreaming,
    session,
    messages,
    groups,
    sessionUiState,
    uiStateLoading,
    uiStateError,
    error,
    streamError,
    messageContent,
    conversationFeedRef,
    displayMessages,
    questionHints,
    shouldAnchorThread,
    streamingStatusBadge,
    streamingStatusMode,
    updateThreadPinnedState,
    loadWorkspace,
    refreshConversation,
    sendMessage,
    loadSessionUiState,
    reloadUiState,
    abortStreaming,
    resetStreamingState,
  }
}
