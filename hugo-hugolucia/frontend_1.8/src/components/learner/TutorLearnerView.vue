<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useTutorWorkspaceStore } from '../../stores/tutorWorkspace.js'
import api from '../../api/client'
import { resolveAssistantContent } from '../../utils/assistantVariants'
import { formatTutorArtifactList } from '../../utils/tutorKnowledgeDisplay.js'
import {
  TUTOR_WORKSPACE_CTA_LABELS,
  TUTOR_WORKSPACE_PROFILE_CODES,
  findProfileIdByCode,
  normalizeConversationProfilesResponse,
} from '../../utils/tutorWorkspaceProfiles.js'
import { openTutorWorkspaceChat } from '../../utils/tutorWorkspaceSession.js'

const props = defineProps({
  groupId: { type: String, required: true },
  learnerId: { type: String, required: true },
})
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const tutorStore = useTutorWorkspaceStore()
const conversationProfiles = ref([])
const openingChat = ref(false)
const workspaceError = ref('')
const learnerName = ref('')
const timeline = ref({ sessions: [], traces: [] })
const competences = ref([])
const loading = ref({ timeline: false, competences: false, validating: false })
const error = ref('')
const canValidateTraces = computed(() => {
  const role = String(auth.user?.role || '').toUpperCase()
  return auth.isAdminLike || ['TUTOR', 'TRAINER', 'COORDO'].includes(role)
})

const tutorDraftEntries = computed(() => formatTutorArtifactList(
  tutorStore.artifactsForLearner(props.groupId, props.learnerId),
))

const tutorCtaButtons = computed(() => [
  TUTOR_WORKSPACE_PROFILE_CODES.PREP,
  TUTOR_WORKSPACE_PROFILE_CODES.DIAGNOSTIC,
  TUTOR_WORKSPACE_PROFILE_CODES.COREFLEX,
  TUTOR_WORKSPACE_PROFILE_CODES.JOURNAL,
])

async function loadConversationProfiles() {
  try {
    const { data } = await api.get('/hugo/learner-conversation-profiles/')
    conversationProfiles.value = normalizeConversationProfilesResponse(data)
  } catch {
    conversationProfiles.value = []
  }
  return conversationProfiles.value
}

async function openWorkspace(profileCode, sourceSessionId = '') {
  if (openingChat.value) return
  openingChat.value = true
  workspaceError.value = ''
  try {
    if (!findProfileIdByCode(conversationProfiles.value, profileCode)) {
      await loadConversationProfiles()
    }
    await openTutorWorkspaceChat(router, {
      profileCode,
      groupId: props.groupId,
      learnerId: props.learnerId,
      sourceSessionId,
      conversationProfiles: conversationProfiles.value,
    })
  } catch (e) {
    workspaceError.value = e?.message || e?.response?.data?.detail || 'Impossible d\'ouvrir l\'espace de réflexion.'
  } finally {
    openingChat.value = false
  }
}

function formatDate(s) {
  if (!s) return ''
  try {
    return new Date(s).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
  } catch {
    return s
  }
}
function sessionPreview(session) {
  const text = String(session?.first_learner_message || '').trim()
  if (text) return text
  return 'Aucun message apprenant'
}

async function loadTimeline() {
  loading.value.timeline = true
  try {
    const { data } = await api.get(`/dashboard/groups/${props.groupId}/learners/${props.learnerId}/timeline/`)
    timeline.value = { sessions: data.sessions || [], traces: data.traces || [] }
  } catch (e) {
    if (e?.response?.status === 403) {
      error.value = "Accès refusé : cet apprenant n'est pas associé à votre compte tuteur pour ce groupe."
    }
    timeline.value = { sessions: [], traces: [] }
  } finally {
    loading.value.timeline = false
  }
}

function resolveMessageContent(message) {
  return resolveAssistantContent(message)
}

function profileLabel(value) {
  const normalized = String(value || '').toLowerCase()
  if (normalized === 'diagnostic') return 'diagnostic'
  if (normalized === 'knowledge_review') return 'savoirs'
  return 'réflexif'
}

/** Badges compacts à partir d'un pilotage produit-safe (timeline dashboard). */
function pilotageBadges(d) {
  if (!d || typeof d !== 'object') return []
  const out = []
  const profile = String(d.conversation_profile || '').trim()
  if (profile) out.push({ label: profileLabel(profile), cls: 'text-bg-info' })
  const objective = String(d.active_objective || '').trim()
  if (objective) out.push({ label: objective, cls: 'text-bg-primary' })
  const step = String(d.current_step_label || '').trim()
  if (step) out.push({ label: step, cls: 'text-bg-light text-dark border' })
  if (typeof d.progress_percent === 'number') out.push({ label: `${d.progress_percent}%`, cls: 'text-bg-light text-dark border' })
  const clo = String(d.closure_signal || 'none')
  if (clo && clo !== 'none') out.push({ label: `clôture: ${clo}`, cls: 'text-bg-success' })
  const help = String(d.learner_help_request || 'none')
  if (help && help !== 'none') out.push({ label: `aide: ${help}`, cls: 'text-bg-warning' })
  const lr = String(d.loop_risk || 'low')
  if (lr && lr !== 'low') out.push({ label: `boucle: ${lr}`, cls: 'text-bg-danger' })
  if (d.can_summarize) out.push({ label: 'synthèse possible', cls: 'text-bg-success' })
  for (const reason of (Array.isArray(d.reason_codes) ? d.reason_codes : []).slice(0, 2)) {
    out.push({ label: reason, cls: 'text-bg-secondary' })
  }
  return out
}
async function loadCompetences() {
  loading.value.competences = true
  try {
    const { data } = await api.get(`/dashboard/groups/${props.groupId}/competences/`)
    const list = data.competences || []
    competences.value = list.filter((c) => String(c.learner_id) === String(props.learnerId))
  } catch (e) {
    if (e?.response?.status === 403) {
      error.value = "Accès refusé : cet apprenant n'est pas associé à votre compte tuteur pour ce groupe."
    }
    competences.value = []
  } finally {
    loading.value.competences = false
  }
}
async function loadLearnerName() {
  try {
    const { data } = await api.get(`/dashboard/groups/${props.groupId}/learners/`)
    const learner = (data.learners || []).find((l) => String(l.id) === String(props.learnerId))
    learnerName.value = learner ? learner.username : 'Apprenant'
  } catch (e) {
    if (e?.response?.status === 403) {
      error.value = "Accès refusé : cet apprenant n'est pas associé à votre compte tuteur pour ce groupe."
    }
    learnerName.value = 'Apprenant'
  }
}

async function validateTrace(traceId) {
  if (loading.value.validating) return
  loading.value.validating = true
  error.value = ''
  try {
    await api.post(`/traces/${traceId}/validate/`)
    await loadTimeline()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors de la validation de la trace.'
  } finally {
    loading.value.validating = false
  }
}

onMounted(() => {
  loadLearnerName()
  loadTimeline()
  loadCompetences()
  loadConversationProfiles()
})
watch(() => [props.learnerId, props.groupId], () => {
  loadLearnerName()
  loadTimeline()
  loadCompetences()
})
</script>

<template>
  <nav aria-label="breadcrumb">
    <ol class="breadcrumb">
      <li class="breadcrumb-item"><router-link to="/dashboard">Tableau de bord</router-link></li>
      <li class="breadcrumb-item"><router-link :to="{ name: 'Group', params: { groupId: groupId } }">Groupe</router-link></li>
      <li class="breadcrumb-item active" aria-current="page">{{ learnerName || 'Apprenant' }} (vue tuteur)</li>
    </ol>
  </nav>
  <h1 class="h4 mb-4">Vue tuteur — {{ learnerName || '…' }}</h1>
  <p class="text-muted small">Données visibles uniquement si l'apprenant a activé le partage (résumé, preuves, verbatim).</p>
  <div v-if="workspaceError" class="alert alert-warning small">{{ workspaceError }}</div>

  <div class="card mb-4" data-testid="tutor-learner-cta-panel">
    <div class="card-body">
      <h2 class="h6 mb-2">Espace de réflexion tuteur</h2>
      <p class="small text-muted mb-3">Préparer un entretien, formuler des hypothèses ou noter un point-clé — sans parler à la place de l'apprenant.</p>
      <div class="d-flex flex-wrap gap-2">
        <button
          v-for="code in tutorCtaButtons"
          :key="code"
          type="button"
          class="btn btn-sm btn-outline-primary"
          :disabled="openingChat"
          :data-testid="`tutor-cta-${code}`"
          @click="openWorkspace(code)"
        >
          {{ TUTOR_WORKSPACE_CTA_LABELS[code] }}
        </button>
      </div>
    </div>
  </div>

  <section
    v-if="tutorDraftEntries.length"
    class="card mb-4"
    data-testid="tutor-learner-drafts-panel"
  >
    <div class="card-header py-2 d-flex align-items-center gap-2">
      <span class="small fw-semibold">Notes tutorales (session courante)</span>
      <span class="badge text-bg-secondary">brouillon</span>
      <span class="badge text-bg-light text-dark border">non durable</span>
    </div>
    <ul class="list-group list-group-flush">
      <li
        v-for="row in tutorDraftEntries"
        :key="row.item.id"
        class="list-group-item small"
      >
        <div class="fw-semibold">{{ row.summary.title }}</div>
        <div class="text-muted">{{ row.summary.line }}</div>
      </li>
    </ul>
  </section>

  <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>

  <div class="row">
    <div class="col-12 col-lg-6 mb-4">
      <div class="card">
        <div class="card-header">Timeline (sessions & traces)</div>
        <div class="card-body">
          <div v-if="loading.timeline" class="text-center py-3"><div class="spinner-border spinner-border-sm text-primary"></div></div>
          <div v-else>
            <p class="small text-muted mb-2">Sessions</p>
            <ul class="list-group list-group-flush">
              <li v-for="s in timeline.sessions" :key="s.id" class="list-group-item">
                <div class="d-flex justify-content-between align-items-start gap-2">
                  <div>
                    <div>{{ formatDate(s.created_at) }}</div>
                    <small class="text-muted d-block">{{ sessionPreview(s) }}</small>
                  </div>
                  <div class="text-end">
                    <code class="small d-block">{{ s.id.slice(0, 8) }}</code>
                    <button
                      type="button"
                      class="btn btn-link btn-sm p-0 mt-1"
                      :data-testid="`tutor-prep-from-session-${s.id}`"
                      @click="openWorkspace(TUTOR_WORKSPACE_PROFILE_CODES.PREP, s.id)"
                    >
                      Préparer depuis cette session
                    </button>
                    <span
                      v-if="s.share_verbatim"
                      class="badge bg-info-subtle text-info-emphasis border mt-1"
                    >
                      Verbatim partagé
                    </span>
                  </div>
                </div>
                <div
                  v-if="s.share_verbatim && s.messages?.length"
                  class="border rounded bg-light-subtle p-2 mt-2"
                >
                  <div
                    v-for="message in s.messages"
                    :key="message.id"
                    class="mb-2"
                    :class="message.role === 'ASSISTANT' ? 'text-start' : 'text-end'"
                  >
                    <div class="d-inline-flex align-items-center gap-2">
                      <span class="badge bg-secondary">
                        {{ message.role === 'ASSISTANT' ? 'Hugo' : learnerName || 'Apprenant' }}
                      </span>
                      <small class="text-muted">{{ formatDate(message.created_at) }}</small>
                    </div>
                    <div class="small mt-1" style="white-space: pre-wrap;">{{ resolveMessageContent(message) }}</div>
                    <div
                      v-if="message.role !== 'ASSISTANT' && pilotageBadges(message.pilotage).length"
                      class="d-flex flex-wrap justify-content-end gap-1 mt-1"
                    >
                      <span
                        v-for="(b, bi) in pilotageBadges(message.pilotage)"
                        :key="`p0d-${message.id}-${bi}`"
                        class="badge rounded-pill small"
                        :class="b.cls"
                      >{{ b.label }}</span>
                    </div>
                  </div>
                </div>
              </li>
            </ul>
            <p class="small text-muted mt-3 mb-2">Traces AFEST</p>
            <ul class="list-group list-group-flush">
              <li
                v-for="t in timeline.traces"
                :key="t.id"
                class="list-group-item d-flex justify-content-between align-items-center"
              >
                <div>
                  <div>{{ formatDate(t.created_at) }}</div>
                  <small class="text-muted">Trace {{ t.id.slice(0, 8) }}</small>
                </div>
                <div class="d-flex align-items-center gap-2">
                  <span v-if="t.validated_at" class="badge bg-success">Validé</span>
                  <span v-else class="badge bg-secondary">Non validé</span>
                  <button
                    v-if="!t.validated_at"
                    type="button"
                    class="btn btn-sm btn-outline-success"
                    :disabled="loading.validating || !canValidateTraces"
                    @click="validateTrace(t.id)"
                  >
                    Valider
                  </button>
                </div>
              </li>
            </ul>
            <p v-if="!timeline.sessions?.length && !timeline.traces?.length" class="text-muted small mb-0">Aucune donnée partagée.</p>
          </div>
        </div>
      </div>
    </div>
    <div class="col-12 col-lg-6 mb-4">
      <div class="card">
        <div class="card-header">Compétences / état</div>
        <div class="card-body">
          <div v-if="loading.competences" class="text-center py-3"><div class="spinner-border spinner-border-sm text-primary"></div></div>
          <div v-else-if="competences.length">
            <div v-for="(c, i) in competences" :key="i" class="mb-3">
              <p v-if="c.summary" class="small mb-1"><strong>Résumé :</strong> {{ c.summary }}</p>
              <pre v-if="c.skills_matrix" class="small bg-light p-2 rounded mb-0" style="max-height: 200px; overflow: auto;">{{ typeof c.skills_matrix === 'object' ? JSON.stringify(c.skills_matrix, null, 2) : c.skills_matrix }}</pre>
            </div>
          </div>
          <p v-else class="text-muted small mb-0">Aucun état de compétences pour cet apprenant.</p>
        </div>
      </div>
    </div>
  </div>
</template>
