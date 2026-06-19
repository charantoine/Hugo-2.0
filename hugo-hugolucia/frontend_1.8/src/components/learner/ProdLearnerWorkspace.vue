<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import api, { fetchWithAuth } from '../../api/client'
import PostureSelector from './PostureSelector.vue'
import LearnerMemoryPanel from './LearnerMemoryPanel.vue'
import LearnerSceneContextBar from './LearnerSceneContextBar.vue'
import HugoProgressPanel from './HugoProgressPanel.vue'
import { extractNumberedQuestions, resolveAssistantContent } from '../../utils/assistantVariants'
import { buildEngagementUiModel } from '../../utils/engagementUiModel'
import { frontendFeatures } from '../../utils/frontendConfig'
import { consumeSseBuffer, parseSseEventBlock } from '../../utils/messageStream'

const props = defineProps({
  sessionId: {
    type: String,
    required: true,
  },
})

const router = useRouter()

const loading = ref(true)
const refreshing = ref(false)
const sendingMessage = ref(false)
const generatingTrace = ref(false)
const isStreaming = ref(false)
const hasStreamingChunk = ref(false)
const session = ref(null)
const messages = ref([])
const traces = ref([])
const evidence = ref([])
const groups = ref([])
const sessionUiState = ref(null)
const requestingSynthesis = ref(false)
const requestingEvaluation = ref(false)
const actionFeedback = ref(null)
const synthesisResult = ref(null)
const evaluationResult = ref(null)
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
const shareFlags = ref({
  share_summary: false,
  share_evidence: false,
  share_verbatim: false,
})
const threadRef = ref(null)
const isThreadPinnedToBottom = ref(true)

const STREAMING_STATUS_MESSAGES = [
  'Hugo analyse ta réponse...',
  'Hugo réfléchit...',
  'Hugo prépare sa réponse...',
]

const STREAMING_STATUS_BADGES = [
  'Analyse',
  'Réflexion',
  'Réponse',
]

const streamingStatusMessage = computed(() => {
  if (hasBackendStreamStatus.value && streamStatusMessageText.value) return streamStatusMessageText.value
  return STREAMING_STATUS_MESSAGES[streamStatusIndex.value] || STREAMING_STATUS_MESSAGES[0]
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
const engagementModel = computed(() => buildEngagementUiModel({
  featureFlags: frontendFeatures,
  sessionUiState: sessionUiState.value,
}))
const isProgressActionBusy = computed(() => requestingSynthesis.value || requestingEvaluation.value)
const productHeaderBadges = computed(() => {
  const badges = [
    { id: 'scene', label: 'Scène', value: engagementModel.value.currentStep.label },
  ]
  if (engagementModel.value.conversationMode?.label) {
    badges.push({ id: 'mode', label: 'Mode', value: engagementModel.value.conversationMode.label })
  }
  if (engagementModel.value.showMaturityBadge && engagementModel.value.maturityLabel) {
    badges.push({ id: 'maturity', label: 'Maturité', value: engagementModel.value.maturityLabel })
  }
  if (engagementModel.value.displayProfileLabel) {
    badges.push({ id: 'display-profile', label: 'Style', value: engagementModel.value.displayProfileLabel })
  }
  badges.push({
    id: 'engagement',
    label: 'Engagement',
    value: engagementModel.value.gamificationProfile.label,
  })
  return badges
})

const groupName = computed(() => {
  const groupId = String(session.value?.group || '').trim()
  return groups.value.find((group) => String(group.id) === groupId)?.name || 'Groupe'
})

const sessionTraces = computed(() => (
  traces.value
    .filter((trace) => String(trace?.session || '') === String(props.sessionId))
    .sort((left, right) => new Date(right.created_at || 0) - new Date(left.created_at || 0))
))

const sessionEvidenceCount = computed(() => {
  const traceIds = new Set(sessionTraces.value.map((trace) => String(trace.id)))
  return evidence.value.filter((item) => (
    String(item?.session || '') === String(props.sessionId)
    || traceIds.has(String(item?.trace || ''))
  )).length
})

const composerPlaceholder = computed(() => {
  if (isStreaming.value) return 'Hugo est en train de formuler sa réponse...'
  if (questionHints.value.length) return questionHints.value[0].question
  return 'Écris ce que tu vis, ce que tu as testé, ou ce qui te bloque.'
})

function formatDate(value) {
  if (!value) return ''
  try {
    return new Date(value).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return String(value)
  }
}

function rewardClass(reward) {
  return reward.unlocked ? 'prod-reward prod-reward--unlocked' : 'prod-reward'
}

function uiStateRequestParams() {
  const params = {
    gamification_profile: frontendFeatures.gamification_profile || 'B',
  }
  const resolvedProfile = sessionUiState.value?.learner_display_profile
  if (resolvedProfile) params.learner_display_profile = resolvedProfile
  return params
}

function updateThreadPinnedState() {
  if (!threadRef.value) return
  const { scrollTop, clientHeight, scrollHeight } = threadRef.value
  isThreadPinnedToBottom.value = scrollTop + clientHeight >= scrollHeight - 24
}

async function scrollThreadToBottom({ force = false } = {}) {
  await nextTick()
  if (threadRef.value && (force || isThreadPinnedToBottom.value)) {
    threadRef.value.scrollTop = threadRef.value.scrollHeight
    updateThreadPinnedState()
  }
}

async function loadGroups() {
  const { data } = await api.get('/groups/')
  groups.value = Array.isArray(data) ? data : (data.results || [])
}

async function loadSession() {
  const { data } = await api.get(`/hugo/sessions/${props.sessionId}/`)
  session.value = data
  shareFlags.value = {
    share_summary: Boolean(data?.share_summary),
    share_evidence: Boolean(data?.share_evidence),
    share_verbatim: Boolean(data?.share_verbatim),
  }
}

async function loadMessages() {
  const { data } = await api.get(`/hugo/sessions/${props.sessionId}/messages/`)
  messages.value = data.messages || []
  await scrollThreadToBottom()
}

async function loadSessionUiState() {
  try {
    const { data } = await api.get(`/hugo/sessions/${props.sessionId}/ui-state/`, {
      params: uiStateRequestParams(),
    })
    sessionUiState.value = data || null
  } catch {
    sessionUiState.value = null
  }
}

async function loadTracesAndEvidence() {
  const [{ data: tracesData }, { data: evidenceData }] = await Promise.all([
    api.get('/learners/traces/'),
    api.get('/learners/evidence/'),
  ])
  traces.value = Array.isArray(tracesData) ? tracesData : (tracesData.results || [])
  evidence.value = Array.isArray(evidenceData) ? evidenceData : (evidenceData.results || [])
}

async function onPostureChanged() {
  await loadSessionUiState()
}

async function loadWorkspace({ silent = false } = {}) {
  if (silent) refreshing.value = true
  else loading.value = true
  error.value = ''
  try {
    await Promise.all([
      loadGroups(),
      loadSession(),
      loadMessages(),
      loadSessionUiState(),
      loadTracesAndEvidence(),
    ])
  } catch (err) {
    error.value = err.response?.data?.detail || 'Impossible de charger cette session.'
  } finally {
    if (silent) refreshing.value = false
    else loading.value = false
  }
}

async function refreshConversationWorkspace() {
  await Promise.all([
    loadSession(),
    loadMessages(),
    loadSessionUiState(),
    loadTracesAndEvidence(),
  ])
}

function storeActionArtifact(kind, payload) {
  if (!payload || typeof payload !== 'object') return
  if (kind === 'synthesis') synthesisResult.value = payload
  if (kind === 'evaluation') {
    evaluationResult.value = {
      ...payload,
      text: payload.text || payload.first_message || '',
    }
  }
}

function setActionFeedback(type, message) {
  actionFeedback.value = message ? { type, message } : null
}

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
  if (streamAbortController.value) {
    streamAbortController.value.abort()
  }
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
  await api.post(`/hugo/sessions/${props.sessionId}/messages/`, { content })
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
  streamStatusPhaseLabel.value = engagementModel.value.conversationMode?.label || ''
  hasBackendStreamStatus.value = false
  const controller = new AbortController()
  streamAbortController.value = controller
  await scrollThreadToBottom({ force: true })
  if (streamStatusTimer.value) clearInterval(streamStatusTimer.value)
  streamStatusTimer.value = setInterval(() => {
    if (hasStreamingChunk.value) return
    streamStatusIndex.value = (streamStatusIndex.value + 1) % STREAMING_STATUS_MESSAGES.length
    scrollThreadToBottom()
  }, 1800)

  const response = await fetchWithAuth(`/hugo/sessions/${props.sessionId}/messages/stream/`, {
    method: 'POST',
    signal: controller.signal,
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ content }),
  })

  if ([404, 405, 406, 415, 501].includes(response.status)) {
    const error = new Error('Streaming indisponible sur ce backend.')
    error.status = response.status
    throw error
  }

  if (!response.ok) {
    let detail = 'Le streaming a échoué.'
    const contentType = String(response.headers.get('content-type') || '')
    try {
      if (contentType.includes('application/json')) {
        const payload = await response.json()
        detail = payload?.detail || detail
      } else {
        const text = await response.text()
        if (text) detail = text
      }
    } catch {
      /* ignore parse errors */
    }
    const error = new Error(detail)
    error.status = response.status
    throw error
  }

  const contentType = String(response.headers.get('content-type') || '')
  if (!contentType.includes('text/event-stream')) {
    const error = new Error('Réponse non streaming.')
    error.code = 'stream_unsupported'
    error.status = response.status
    throw error
  }

  const reader = response.body?.getReader()
  if (!reader) {
    const error = new Error('Flux navigateur indisponible.')
    error.code = 'stream_unsupported'
    throw error
  }

  const decoder = new TextDecoder()
  let buffer = ''
  let sawDone = false

  const processEvent = async (eventPayload) => {
    if (!eventPayload) return
    if (eventPayload.event === 'status') {
      hasBackendStreamStatus.value = true
      streamStatusLabel.value = String(eventPayload.data?.label || streamStatusLabel.value || '')
      streamStatusMessageText.value = String(eventPayload.data?.message || streamStatusMessageText.value || '')
      streamStatusPhaseLabel.value = String(
        eventPayload.data?.phase_label || streamStatusPhaseLabel.value || engagementModel.value.conversationMode?.label || '',
      )
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
    const error = new Error(streamError.value)
    error.status = 502
    throw error
  }
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
    await refreshConversationWorkspace()
  } catch (err) {
    if (!isAbortError(err)) {
      error.value = toErrorMessage(err, 'Ton message n’a pas pu être envoyé.')
    }
  } finally {
    resetStreamingState()
    sendingMessage.value = false
  }
}

async function generateTrace() {
  if (generatingTrace.value) return
  generatingTrace.value = true
  error.value = ''
  try {
    await api.post(`/hugo/sessions/${props.sessionId}/generate-trace/`)
    setActionFeedback('success', 'La trace a été préparée à partir de la session courante.')
    await Promise.all([loadSessionUiState(), loadTracesAndEvidence()])
  } catch (err) {
    error.value = err.response?.data?.detail || 'La trace n’a pas pu être générée.'
  } finally {
    generatingTrace.value = false
  }
}

async function requestSynthesis() {
  if (requestingSynthesis.value || engagementModel.value.synthesisButton.disabled) return
  requestingSynthesis.value = true
  error.value = ''
  setActionFeedback(null, '')
  try {
    const { data } = await api.post(`/hugo/sessions/${props.sessionId}/request-synthesis/`, {
      gamification_profile: frontendFeatures.gamification_profile,
      learner_display_profile: sessionUiState.value?.learner_display_profile,
    })
    if (data?.ui_state) sessionUiState.value = data.ui_state
    storeActionArtifact('synthesis', data?.synthesis)
    setActionFeedback('success', 'La synthèse est disponible.')
    await loadSessionUiState()
  } catch (err) {
    const detail = err.response?.data?.detail
      || err.response?.data?.error
      || 'La synthèse n’a pas pu être générée.'
    error.value = detail
  } finally {
    requestingSynthesis.value = false
  }
}

async function requestEvaluation() {
  if (requestingEvaluation.value || engagementModel.value.evaluationButton.disabled) return
  requestingEvaluation.value = true
  error.value = ''
  setActionFeedback(null, '')
  try {
    const { data } = await api.post(`/hugo/sessions/${props.sessionId}/request-evaluation/`, {
      gamification_profile: frontendFeatures.gamification_profile,
      learner_display_profile: sessionUiState.value?.learner_display_profile,
    })
    if (data?.ui_state) sessionUiState.value = data.ui_state
    storeActionArtifact('evaluation', data?.evaluation)
    if (data?.warning) setActionFeedback('warning', data.warning)
    else setActionFeedback('success', 'L’évaluation est disponible.')
    await loadSessionUiState()
  } catch (err) {
    const detail = err.response?.data?.detail
      || err.response?.data?.error
      || 'L’évaluation n’a pas pu être générée.'
    error.value = detail
  } finally {
    requestingEvaluation.value = false
  }
}

async function updateShare() {
  error.value = ''
  try {
    const { data } = await api.post(`/hugo/sessions/${props.sessionId}/share/`, shareFlags.value)
    shareFlags.value = { ...data }
    session.value = { ...session.value, ...data }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Impossible de mettre à jour le partage.'
  }
}

function goHome() {
  router.push({ name: 'ProdLearnerHome' })
}

watch(() => props.sessionId, () => {
  abortStreaming()
  resetStreamingState()
  loadWorkspace()
}, { immediate: false })

onBeforeUnmount(() => {
  abortStreaming()
})

onMounted(() => {
  loadWorkspace()
})
</script>

<template>
  <div v-if="loading" class="d-flex justify-content-center py-5">
    <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Chargement…</span></div>
  </div>

  <div v-else-if="error && !session" class="alert alert-danger">{{ error }}</div>

  <div v-else class="prod-workspace" :class="`prod-workspace--${engagementModel.learnerDisplayProfile}`">
    <section class="prod-session-header card prod-panel">
      <div class="card-body">
        <div class="d-flex flex-column flex-lg-row justify-content-between gap-3">
          <div>
            <button type="button" class="btn btn-sm btn-outline-primary mb-3" @click="goHome">
              <i class="bi bi-arrow-left-short"></i> Retour à mon espace
            </button>
            <div class="d-flex flex-wrap gap-2 align-items-center mb-2">
              <span class="badge rounded-pill text-bg-light border">{{ groupName }}</span>
              <span v-if="session?.tutor_prompt" class="badge rounded-pill text-bg-light border">
                Prompt : {{ session.tutor_prompt.code }}
              </span>
              <span v-if="refreshing" class="badge rounded-pill text-bg-light border">Actualisation...</span>
            </div>
            <h1 class="prod-session-header__title d-none">Ta scène avec Hugo - Lucia</h1>
            <p class="prod-session-header__text">
              {{ engagementModel.profileCopy?.sessionIntro }}
            </p>
            <p v-if="session?.tutor_prompt" class="small text-muted mb-0 mt-2">
              TutorPrompt actif : <strong>{{ session.tutor_prompt.code }}</strong> — {{ session.tutor_prompt.name }}
            </p>
            <div v-if="productHeaderBadges.length" class="d-flex flex-wrap gap-2 mt-3">
              <span
                v-for="badge in productHeaderBadges"
                :key="badge.id"
                class="badge rounded-pill text-bg-light border"
              >
                {{ badge.label }} : {{ badge.value }}
              </span>
            </div>
          </div>

          <div class="prod-session-header__actions">
            <button type="button" class="btn btn-outline-primary" :disabled="refreshing" @click="loadWorkspace({ silent: true })">
              Actualiser
            </button>
            <button type="button" class="btn btn-primary" :disabled="generatingTrace" @click="generateTrace">
              {{ generatingTrace ? 'Préparation...' : 'Préparer une trace' }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <PostureSelector
      :session-id="sessionId"
      :conversation-mode="engagementModel.conversationMode"
      :busy="sendingMessage || isStreaming || refreshing"
      @posture-changed="onPostureChanged"
    />

    <LearnerSceneContextBar :model="engagementModel" />

    <HugoProgressPanel
      :model="engagementModel"
      :busy="sendingMessage || generatingTrace || isProgressActionBusy"
      @request-synthesis="requestSynthesis"
      @request-evaluation="requestEvaluation"
    />

    <div class="row g-4">
      <div class="col-12 col-xl-7">
        <section class="card prod-panel prod-panel--conversation h-100">
          <div class="card-body d-flex flex-column">
            <div class="d-flex justify-content-between align-items-start gap-3 mb-3">
              <div>
                <h2 class="prod-section-title mb-1">{{ engagementModel.profileCopy?.conversationTitle }}</h2>
                <p class="text-muted mb-0">{{ engagementModel.profileCopy?.conversationLead }}</p>
              </div>
              <span class="badge rounded-pill text-bg-light border">{{ displayMessages.length }} message(s)</span>
            </div>

            <div
              ref="threadRef"
              class="prod-thread"
              :class="{ 'prod-thread--empty': !displayMessages.length }"
              @scroll.passive="updateThreadPinnedState"
            >
              <div class="prod-thread__content" :class="{ 'prod-thread__content--anchored': shouldAnchorThread }">
                <div v-if="!displayMessages.length" class="prod-thread__empty">
                  <strong>La scène est prête à commencer.</strong>
                  <p>Décris un moment concret, une difficulté rencontrée ou une action que tu aimerais analyser avec Hugo.</p>
                </div>

                <article
                  v-for="message in displayMessages"
                  :key="message.id"
                  class="prod-message"
                  :class="[
                    message.role === 'ASSISTANT' ? 'prod-message--assistant' : 'prod-message--learner',
                    message.isPlaceholder ? 'prod-message--placeholder' : '',
                  ]"
                >
                  <div class="prod-message__meta">
                    <span>{{ message.role === 'ASSISTANT' ? 'Hugo' : 'Toi' }}</span>
                    <time>{{ message.isStreaming ? (message.isPlaceholder ? 'préparation...' : 'en direct') : formatDate(message.created_at) }}</time>
                  </div>
                  <div class="prod-message__bubble">
                    <div v-if="message.isPlaceholder" class="prod-message__status">
                      <span class="prod-message__status-badge">{{ streamingStatusBadge }}</span>
                      <span class="prod-message__status-phase">{{ streamingStatusMode }}</span>
                    </div>
                    <p v-for="(line, index) in String(message.displayContent || message.content || '').split('\n').filter(Boolean)" :key="`${message.id}-${index}`">
                      {{ line }}
                    </p>
                    <div
                      v-if="message.role === 'ASSISTANT' && message.rag_citations?.length"
                      class="d-flex flex-wrap gap-2 mt-3"
                    >
                      <span
                        v-for="citation in message.rag_citations"
                        :key="`${message.id}-${citation.chunk_id}`"
                        class="badge rounded-pill text-bg-light border"
                      >
                        Appui : {{ citation.document_title || citation.document_id }}
                      </span>
                    </div>
                    <div v-if="message.isPlaceholder" class="prod-message__typing" aria-hidden="true">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </article>
              </div>
            </div>

            <div v-if="questionHints.length" class="prod-hints mt-3">
              <span class="prod-hints__label">Pistes à traiter</span>
              <div class="prod-hints__list">
                <span v-for="hint in questionHints" :key="hint.index" class="prod-hint-chip">{{ hint.question }}</span>
              </div>
            </div>

            <form class="prod-composer mt-3" @submit.prevent="sendMessage">
              <label class="form-label" for="message-content">Ton message</label>
              <textarea
                id="message-content"
                v-model="messageContent"
                class="form-control prod-composer__textarea"
                rows="4"
                :placeholder="composerPlaceholder"
              ></textarea>
              <div class="d-flex justify-content-between align-items-center gap-3 mt-3">
                <p class="text-muted small mb-0">Un seul message suffit. Hugo s’appuie ensuite sur le fil réel de la scène.</p>
                <button type="submit" class="btn btn-primary" :disabled="sendingMessage || !messageContent.trim()">
                  {{ isStreaming ? 'Réponse en cours...' : (sendingMessage ? 'Envoi...' : 'Envoyer à Hugo') }}
                </button>
              </div>
            </form>

            <div v-if="streamError && !error" class="alert alert-warning mt-3 mb-0">{{ streamError }}</div>
            <div v-if="error" class="alert alert-danger mt-3 mb-0">{{ error }}</div>
          </div>
        </section>
      </div>

      <div class="col-12 col-xl-5">
        <div class="d-grid gap-4">
          <LearnerMemoryPanel
            :session-id="sessionId"
            :display-profile="engagementModel.learnerDisplayProfile"
          />

          <section v-if="engagementModel.showQuestLabel && engagementModel.questLabel" class="card prod-panel">
            <div class="card-body">
              <h2 class="prod-section-title mb-1">{{ engagementModel.profileCopy?.questSectionLead }}</h2>
              <p class="text-muted mb-3">{{ engagementModel.profileCopy?.questPanelNote }}</p>

              <article class="prod-quest-card">
                <span class="prod-quest-card__tag">À faire maintenant</span>
                <strong>{{ engagementModel.sceneLabel }}</strong>
                <p>{{ engagementModel.questLabel }}</p>
              </article>
            </div>
          </section>

          <section class="card prod-panel">
            <div class="card-body">
              <div v-if="actionFeedback" class="alert mb-3" :class="actionFeedback.type === 'success' ? 'alert-success' : 'alert-warning'">
                {{ actionFeedback.message }}
              </div>
              <h2 class="prod-section-title mb-1">Traces et acquis</h2>
              <p class="text-muted mb-3">
                {{ engagementModel.profileCopy?.tracesSectionLead }}
              </p>

              <div
                v-if="engagementModel.uiVisibilityFlags.persistentObjectsEnabled"
                class="d-grid gap-3 mb-4"
              >
                <article
                  v-for="item in engagementModel.persistentObjects"
                  :key="item.id"
                  class="prod-object-card"
                  :class="`prod-object-card--${item.status}`"
                >
                  <div class="d-flex justify-content-between gap-3 align-items-start">
                    <div>
                      <strong>{{ item.title }}</strong>
                      <p>{{ item.description }}</p>
                    </div>
                    <span class="badge rounded-pill text-bg-light border">{{ item.meta }}</span>
                  </div>
                </article>
              </div>

              <div v-if="synthesisResult" class="prod-list-card mb-3">
                <h3>{{ synthesisResult.title || 'Synthèse' }}</h3>
                <p class="mb-0" style="white-space: pre-wrap;">{{ synthesisResult.text }}</p>
              </div>

              <div v-if="evaluationResult" class="prod-list-card prod-list-card--soft mb-3">
                <h3>{{ evaluationResult.title || 'Évaluation' }}</h3>
                <p class="mb-2" style="white-space: pre-wrap;">{{ evaluationResult.text }}</p>
                <ul v-if="evaluationResult.competence_items?.length" class="mb-2">
                  <li v-for="item in evaluationResult.competence_items" :key="`${item.label}-${item.status}`">
                    {{ item.label }} — {{ item.status }}
                  </li>
                </ul>
                <p v-if="evaluationResult.validation_candidates?.length" class="small text-muted mb-0">
                  Vigilances : {{ evaluationResult.validation_candidates.join(' ; ') }}
                </p>
              </div>

              <div class="prod-trace-summary">
                <div class="prod-trace-summary__item">
                  <strong>{{ sessionTraces.length }}</strong>
                  <span>trace(s)</span>
                </div>
                <div class="prod-trace-summary__item">
                  <strong>{{ sessionEvidenceCount }}</strong>
                  <span>preuve(s)</span>
                </div>
                <div class="prod-trace-summary__item">
                  <strong>{{ sessionTraces.some((trace) => trace.validated_at) ? 'Oui' : 'Pas encore' }}</strong>
                  <span>validation</span>
                </div>
              </div>

              <div class="row g-2 mt-1">
                <div class="col-12">
                  <label class="form-check prod-check">
                    <input v-model="shareFlags.share_summary" class="form-check-input" type="checkbox" @change="updateShare" />
                    <span>
                      <strong>Partager le résumé</strong>
                      <small>Autorise la transmission du mini-bilan.</small>
                    </span>
                  </label>
                </div>
                <div class="col-12">
                  <label class="form-check prod-check">
                    <input v-model="shareFlags.share_evidence" class="form-check-input" type="checkbox" @change="updateShare" />
                    <span>
                      <strong>Partager les preuves</strong>
                      <small>Autorise les pièces utiles liées à la scène.</small>
                    </span>
                  </label>
                </div>
                <div class="col-12">
                  <label class="form-check prod-check">
                    <input v-model="shareFlags.share_verbatim" class="form-check-input" type="checkbox" @change="updateShare" />
                    <span>
                      <strong>Partager le texte du chat</strong>
                      <small>Le verbatim reste privé tant que cette option n’est pas activée.</small>
                    </span>
                  </label>
                </div>
              </div>

              <div
                v-if="engagementModel.uiVisibilityFlags.symbolicRewardsEnabled"
                class="mt-4"
              >
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <h3 class="h6 mb-0">Récompenses symboliques</h3>
                  <span class="badge rounded-pill text-bg-light border">{{ engagementModel.gamificationProfile.title }}</span>
                </div>
                <div class="d-grid gap-2">
                  <article
                    v-for="reward in engagementModel.symbolicRewards"
                    :key="reward.id"
                    :class="rewardClass(reward)"
                  >
                    <strong>{{ reward.label }}</strong>
                    <p class="d-none">{{ reward.description }}</p>
                  </article>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>
