<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api/client'
import PostureSelector from './PostureSelector.vue'
import LearnerMemoryPanel from './LearnerMemoryPanel.vue'
import LearnerSceneContextBar from './LearnerSceneContextBar.vue'
import HugoProgressPanel from './HugoProgressPanel.vue'
import LearnerActionSidebar from './LearnerActionSidebar.vue'
import LearnerConversationFeed from './LearnerConversationFeed.vue'
import { buildEngagementUiModel } from '../../utils/engagementUiModel'
import { frontendFeatures } from '../../utils/frontendConfig'
import { useHugoSessionChat } from '../../composables/useHugoSessionChat.js'
import { useAuthStore } from '../../stores/auth'

const learnerUiV2 = frontendFeatures.learner_ui_v2
const auth = useAuthStore()

const props = defineProps({
  sessionId: {
    type: String,
    required: true,
  },
})

const router = useRouter()
const sessionIdRef = computed(() => props.sessionId)

const generatingTrace = ref(false)
const traces = ref([])
const evidence = ref([])
const groupReferentialConfig = ref(null)
const requestingSynthesis = ref(false)
const requestingEvaluation = ref(false)
const actionFeedback = ref(null)
const synthesisResult = ref(null)
const evaluationResult = ref(null)
const shareFlags = ref({
  share_summary: false,
  share_evidence: false,
  share_verbatim: false,
})

const {
  loading,
  refreshing,
  sendingMessage,
  isStreaming,
  session,
  groups,
  sessionUiState,
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
  sendMessage: sendChatMessage,
  loadSessionUiState,
} = useHugoSessionChat(sessionIdRef, {
  loadUiState: true,
  loadLearnerArtifacts: true,
  streamingPersona: 'learner',
  getUiStateParams: () => uiStateRequestParams(),
  onSessionLoaded: async (data) => {
    shareFlags.value = {
      share_summary: Boolean(data?.share_summary),
      share_evidence: Boolean(data?.share_evidence),
      share_verbatim: Boolean(data?.share_verbatim),
    }
    await loadGroupReferentialConfig()
  },
})

const engagementModel = computed(() => buildEngagementUiModel({
  featureFlags: frontendFeatures,
  sessionUiState: sessionUiState.value,
}))

const sceneContextModel = computed(() => ({
  ...engagementModel.value,
  sessionGroupName: groupName.value !== 'Groupe' ? groupName.value : null,
  sessionProfileName: session.value?.learner_conversation_profile?.name || null,
  sessionReferentialName: groupReferentialConfig.value?.referential?.name || null,
  sessionPostureLabel: engagementModel.value.conversationMode?.label || null,
  isLegacySession: Boolean(session.value?.tutor_prompt && !session.value?.learner_conversation_profile),
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

const learnerDisplayName = computed(() => auth.user?.username || 'Apprenant')
const activeModeLabel = computed(() => (
  engagementModel.value.conversationMode?.label || null
))

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

async function loadGroupReferentialConfig() {
  const groupId = String(session.value?.group || '').trim()
  if (!groupId) {
    groupReferentialConfig.value = null
    return
  }
  try {
    const { data } = await api.get(`/groups/${groupId}/referential-config/`)
    groupReferentialConfig.value = data?.referential ? data : null
  } catch {
    groupReferentialConfig.value = null
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

async function loadLearnerWorkspace({ silent = false } = {}) {
  await loadWorkspace({ silent })
  try {
    await loadTracesAndEvidence()
  } catch (err) {
    if (!silent) {
      error.value = err.response?.data?.detail || 'Impossible de charger les traces.'
    }
  }
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

async function sendMessage() {
  await sendChatMessage()
  await loadTracesAndEvidence()
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
</script>

<template>
  <div v-if="loading" class="d-flex justify-content-center py-5">
    <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Chargement…</span></div>
  </div>

  <div v-else-if="error && !session" class="alert alert-danger">{{ error }}</div>

  <div v-else-if="learnerUiV2" class="prod-workspace prod-workspace--v2" :class="`prod-workspace--${engagementModel.learnerDisplayProfile}`">
    <header class="learner-v2-header card prod-panel">
      <div class="card-body py-3 d-flex flex-wrap justify-content-between align-items-center gap-3">
        <div class="d-flex flex-wrap align-items-center gap-3">
          <button type="button" class="btn btn-sm btn-outline-primary" @click="goHome">
            <i class="bi bi-arrow-left-short"></i> Retour
          </button>
          <div class="learner-v2-header__identity">
            <strong>{{ learnerDisplayName }}</strong>
            <span v-if="activeModeLabel" class="badge rounded-pill text-bg-primary ms-2">
              {{ activeModeLabel }}
            </span>
          </div>
        </div>
        <div class="d-flex flex-wrap gap-2">
          <button type="button" class="btn btn-sm btn-outline-secondary" :disabled="refreshing" @click="loadLearnerWorkspace({ silent: true })">
            Actualiser
          </button>
          <button
            type="button"
            class="btn btn-sm btn-outline-primary"
            :disabled="generatingTrace"
            @click="generateTrace"
          >
            {{ generatingTrace ? 'Préparation...' : 'Préparer une trace' }}
          </button>
        </div>
      </div>
    </header>

    <div class="learner-v2-layout">
      <LearnerConversationFeed
        ref="conversationFeedRef"
        compact-header
        :engagement-model="engagementModel"
        :display-messages="displayMessages"
        :question-hints="questionHints"
        :message-content="messageContent"
        :composer-placeholder="composerPlaceholder"
        :sending-message="sendingMessage"
        :is-streaming="isStreaming"
        :should-anchor-thread="shouldAnchorThread"
        :streaming-status-badge="streamingStatusBadge"
        :streaming-status-mode="streamingStatusMode"
        :stream-error="streamError"
        :error="error"
        @update:message-content="messageContent = $event"
        @send="sendMessage"
        @scroll="updateThreadPinnedState"
      />

      <LearnerActionSidebar
        :session-id="sessionId"
        :model="engagementModel"
        :busy="sendingMessage || isStreaming || refreshing || isProgressActionBusy"
        :action-feedback="actionFeedback"
        :synthesis-result="synthesisResult"
        :evaluation-result="evaluationResult"
        :session-traces="sessionTraces"
        :session-evidence-count="sessionEvidenceCount"
        :share-flags="shareFlags"
        hide-symbolic-rewards
        @posture-changed="onPostureChanged"
        @request-synthesis="requestSynthesis"
        @request-evaluation="requestEvaluation"
        @update-share="updateShare"
      />
    </div>

    <div class="learner-v2-bottom">
      <HugoProgressPanel
        :model="engagementModel"
        :busy="sendingMessage || generatingTrace || isProgressActionBusy"
        hide-cta-buttons
        @request-synthesis="requestSynthesis"
        @request-evaluation="requestEvaluation"
      />
      <LearnerMemoryPanel
        :session-id="sessionId"
        :display-profile="engagementModel.learnerDisplayProfile"
      />
    </div>
  </div>

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
              <span
                v-if="session?.learner_conversation_profile?.name"
                class="badge rounded-pill text-bg-light border"
                data-testid="session-global-profile-badge"
              >
                Profil : {{ session.learner_conversation_profile.name }}
              </span>
              <span
                v-else-if="session?.tutor_prompt && !session?.learner_conversation_profile"
                class="badge rounded-pill text-bg-warning border"
                data-testid="session-legacy-profile-badge"
              >
                Session historique
              </span>
              <span
                v-if="engagementModel.conversationMode?.label"
                class="badge rounded-pill text-bg-primary border"
                data-testid="session-posture-badge"
              >
                Mode : {{ engagementModel.conversationMode.label }}
              </span>
              <span v-if="refreshing" class="badge rounded-pill text-bg-light border">Actualisation...</span>
            </div>
            <h1 class="prod-session-header__title d-none">Ta scène avec Hugo - Lucia</h1>
            <p class="prod-session-header__text">
              {{ engagementModel.profileCopy?.sessionIntro }}
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
            <button type="button" class="btn btn-outline-primary" :disabled="refreshing" @click="loadLearnerWorkspace({ silent: true })">
              Actualiser
            </button>
            <button
              type="button"
              class="btn btn-primary"
              :disabled="generatingTrace"
              @click="generateTrace"
            >
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

    <LearnerSceneContextBar :model="sceneContextModel" />

    <HugoProgressPanel
      :model="engagementModel"
      :busy="sendingMessage || generatingTrace || isProgressActionBusy"
      @request-synthesis="requestSynthesis"
      @request-evaluation="requestEvaluation"
    />

    <div class="row g-4">
      <div class="col-12 col-xl-7">
        <LearnerConversationFeed
          ref="conversationFeedRef"
          :engagement-model="engagementModel"
          :display-messages="displayMessages"
          :question-hints="questionHints"
          :message-content="messageContent"
          :composer-placeholder="composerPlaceholder"
          :sending-message="sendingMessage"
          :is-streaming="isStreaming"
          :should-anchor-thread="shouldAnchorThread"
          :streaming-status-badge="streamingStatusBadge"
          :streaming-status-mode="streamingStatusMode"
          :stream-error="streamError"
          :error="error"
          @update:message-content="messageContent = $event"
          @send="sendMessage"
          @scroll="updateThreadPinnedState"
        />
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
