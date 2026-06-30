<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api/client'
import { extractNumberedQuestions, resolveAssistantContent } from '../../utils/assistantVariants'
import { buildEngagementUiModel } from '../../utils/engagementUiModel'
import { frontendFeatures } from '../../utils/frontendConfig'

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
const session = ref(null)
const messages = ref([])
const traces = ref([])
const evidence = ref([])
const groups = ref([])
const error = ref('')
const messageContent = ref('')
const shareFlags = ref({
  share_summary: false,
  share_evidence: false,
  share_verbatim: false,
})
const threadRef = ref(null)

const displayMessages = computed(() => (
  messages.value.map((message) => ({
    ...message,
    displayContent: resolveAssistantContent(message),
  }))
))

const lastAssistantMessage = computed(() => {
  for (let index = displayMessages.value.length - 1; index >= 0; index -= 1) {
    const message = displayMessages.value[index]
    if (message.role === 'ASSISTANT') return message
  }
  return null
})

const questionHints = computed(() => extractNumberedQuestions(lastAssistantMessage.value?.displayContent || ''))
const engagementModel = computed(() => buildEngagementUiModel({
  session: session.value || {},
  messages: messages.value,
  traces: traces.value,
  evidence: evidence.value,
  featureFlags: frontendFeatures,
}))

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

function phaseLabel(value) {
  const normalized = String(value || '').trim().toLowerCase()
  if (normalized === 'opening') return 'Raconter'
  if (normalized === 'exploration') return 'Comprendre'
  if (normalized === 'conceptualization') return 'Retenir'
  if (normalized === 'closure') return 'Transmettre'
  return 'Raconter'
}

function rewardClass(reward) {
  return reward.unlocked ? 'prod-reward prod-reward--unlocked' : 'prod-reward'
}

async function scrollThreadToBottom() {
  await nextTick()
  if (threadRef.value) {
    threadRef.value.scrollTop = threadRef.value.scrollHeight
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

async function loadTracesAndEvidence() {
  const [{ data: tracesData }, { data: evidenceData }] = await Promise.all([
    api.get('/learners/traces/'),
    api.get('/learners/evidence/'),
  ])
  traces.value = Array.isArray(tracesData) ? tracesData : (tracesData.results || [])
  evidence.value = Array.isArray(evidenceData) ? evidenceData : (evidenceData.results || [])
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
      loadTracesAndEvidence(),
    ])
  } catch (err) {
    error.value = err.response?.data?.detail || 'Impossible de charger cette session.'
  } finally {
    if (silent) refreshing.value = false
    else loading.value = false
  }
}

async function sendMessage() {
  const content = String(messageContent.value || '').trim()
  if (!content || sendingMessage.value) return
  sendingMessage.value = true
  error.value = ''
  try {
    await api.post(`/hugo/sessions/${props.sessionId}/messages/`, { content })
    messageContent.value = ''
    await Promise.all([
      loadSession(),
      loadMessages(),
      loadTracesAndEvidence(),
    ])
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ton message n’a pas pu être envoyé.'
  } finally {
    sendingMessage.value = false
  }
}

async function generateTrace() {
  if (generatingTrace.value) return
  generatingTrace.value = true
  error.value = ''
  try {
    await api.post(`/hugo/sessions/${props.sessionId}/generate-trace/`)
    await loadTracesAndEvidence()
  } catch (err) {
    error.value = err.response?.data?.detail || 'La trace n’a pas pu être générée.'
  } finally {
    generatingTrace.value = false
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
  loadWorkspace()
}, { immediate: false })

onMounted(() => {
  loadWorkspace()
})
</script>

<template>
  <div v-if="loading" class="d-flex justify-content-center py-5">
    <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Chargement…</span></div>
  </div>

  <div v-else-if="error && !session" class="alert alert-danger">{{ error }}</div>

  <div v-else class="prod-workspace">
    <section class="prod-session-header card prod-panel">
      <div class="card-body">
        <div class="d-flex flex-column flex-lg-row justify-content-between gap-3">
          <div>
            <button type="button" class="btn btn-sm btn-outline-primary mb-3" @click="goHome">
              <i class="bi bi-arrow-left-short"></i> Retour à mon espace
            </button>
            <div class="d-flex flex-wrap gap-2 align-items-center mb-2">
              <span class="badge rounded-pill text-bg-light border">{{ groupName }}</span>
              <span class="badge rounded-pill text-bg-light border">Étape : {{ phaseLabel(session?.current_phase) }}</span>
              <span v-if="session?.tutor_prompt" class="badge rounded-pill text-bg-light border">
                Prompt : {{ session.tutor_prompt.code }}
              </span>
              <span v-if="refreshing" class="badge rounded-pill text-bg-light border">Actualisation...</span>
            </div>
            <h1 class="prod-session-header__title">Ta scène avec Hugo - Lucia</h1>
            <p class="prod-session-header__text">
              Hugo t’aide à clarifier la situation, repérer l’essentiel et préparer une trace utile sans te noyer dans la technique.
            </p>
            <p v-if="session?.tutor_prompt" class="small text-muted mb-0 mt-2">
              TutorPrompt actif : <strong>{{ session.tutor_prompt.code }}</strong> — {{ session.tutor_prompt.name }}
            </p>
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

    <section
      v-if="engagementModel.ui_visibility_flags.engagement_ui_enabled && engagementModel.ui_visibility_flags.scene_progress_enabled"
      class="card prod-panel prod-panel--progress"
    >
      <div class="card-body">
        <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-4">
          <div>
            <h2 class="prod-section-title mb-1">Progression de la scène</h2>
            <p class="text-muted mb-0">
              Une lecture simple de ce qui progresse vraiment, basée sur les signaux déjà présents dans la conversation.
            </p>
          </div>
          <div class="prod-progress-score">
            <strong>{{ engagementModel.scene_progress.percent }}%</strong>
            <span>{{ engagementModel.scene_progress.current_step.label }}</span>
          </div>
        </div>

        <div class="prod-stage-rail">
          <div
            v-for="(step, index) in engagementModel.scene_progress.steps"
            :key="step.id"
            class="prod-stage"
            :class="[
              `prod-stage--${step.state}`,
              index <= engagementModel.scene_progress.current_step_index ? 'prod-stage--reachable' : '',
            ]"
          >
            <div class="prod-stage__dot">{{ index + 1 }}</div>
            <div>
              <strong>{{ step.label }}</strong>
              <p>{{ step.hint }}</p>
            </div>
          </div>
        </div>

        <div class="row g-3 mt-1">
          <div class="col-12 col-lg-6">
            <div class="prod-list-card">
              <h3>Déjà éclairci</h3>
              <ul v-if="engagementModel.scene_progress.covered_points.length">
                <li v-for="point in engagementModel.scene_progress.covered_points" :key="point">{{ point }}</li>
              </ul>
              <p v-else class="text-muted mb-0">Les premiers repères apparaîtront ici quand la scène sera mieux posée.</p>
            </div>
          </div>

          <div class="col-12 col-lg-6">
            <div class="prod-list-card prod-list-card--soft">
              <h3>Encore utile à travailler</h3>
              <ul v-if="engagementModel.scene_progress.remaining_open_points.length">
                <li v-for="point in engagementModel.scene_progress.remaining_open_points" :key="point">{{ point }}</li>
              </ul>
              <p v-else class="text-muted mb-0">La scène est déjà bien avancée. Tu peux préparer la transmission.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <div class="row g-4">
      <div class="col-12 col-xl-7">
        <section class="card prod-panel h-100">
          <div class="card-body d-flex flex-column">
            <div class="d-flex justify-content-between align-items-start gap-3 mb-3">
              <div>
                <h2 class="prod-section-title mb-1">Conversation</h2>
                <p class="text-muted mb-0">Raconte ce que tu vis, ce que tu as testé, ou ce que tu veux formuler plus clairement.</p>
              </div>
              <span class="badge rounded-pill text-bg-light border">{{ displayMessages.length }} message(s)</span>
            </div>

            <div ref="threadRef" class="prod-thread flex-grow-1">
              <div v-if="!displayMessages.length" class="prod-thread__empty">
                <strong>La scène est prête à commencer.</strong>
                <p>Décris un moment concret, une difficulté rencontrée ou une action que tu aimerais analyser avec Hugo.</p>
              </div>

              <article
                v-for="message in displayMessages"
                :key="message.id"
                class="prod-message"
                :class="message.role === 'ASSISTANT' ? 'prod-message--assistant' : 'prod-message--learner'"
              >
                <div class="prod-message__meta">
                  <span>{{ message.role === 'ASSISTANT' ? 'Hugo' : 'Toi' }}</span>
                  <time>{{ formatDate(message.created_at) }}</time>
                </div>
                <div class="prod-message__bubble">
                  <p v-for="(line, index) in String(message.displayContent || message.content || '').split('\n').filter(Boolean)" :key="`${message.id}-${index}`">
                    {{ line }}
                  </p>
                </div>
              </article>
            </div>

            <div v-if="questionHints.length" class="prod-hints">
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
                  {{ sendingMessage ? 'Envoi...' : 'Envoyer à Hugo' }}
                </button>
              </div>
            </form>

            <div v-if="error" class="alert alert-danger mt-3 mb-0">{{ error }}</div>
          </div>
        </section>
      </div>

      <div class="col-12 col-xl-5">
        <div class="d-grid gap-4">
          <section class="card prod-panel">
            <div class="card-body">
              <h2 class="prod-section-title mb-1">Quêtes utiles</h2>
              <p class="text-muted mb-3">De petites étapes concrètes, alignées sur ce qui manque encore dans la scène.</p>

              <div class="d-grid gap-3">
                <article v-for="quest in engagementModel.quest_cards" :key="quest.id" class="prod-quest-card">
                  <span class="prod-quest-card__tag">À faire maintenant</span>
                  <strong>{{ quest.title }}</strong>
                  <p>{{ quest.description }}</p>
                </article>
              </div>
            </div>
          </section>

          <section class="card prod-panel">
            <div class="card-body">
              <h2 class="prod-section-title mb-1">Traces et acquis</h2>
              <p class="text-muted mb-3">
                Ce panneau rassemble ce qui est déjà réutilisable, partageable et visible comme progression utile.
              </p>

              <div
                v-if="engagementModel.ui_visibility_flags.persistent_objects_enabled"
                class="d-grid gap-3 mb-4"
              >
                <article
                  v-for="item in engagementModel.persistent_objects"
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
                v-if="engagementModel.ui_visibility_flags.symbolic_rewards_enabled"
                class="mt-4"
              >
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <h3 class="h6 mb-0">Récompenses symboliques</h3>
                  <span class="badge rounded-pill text-bg-light border">{{ engagementModel.gamification_profile.title }}</span>
                </div>
                <div class="d-grid gap-2">
                  <article
                    v-for="reward in engagementModel.symbolic_rewards"
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
