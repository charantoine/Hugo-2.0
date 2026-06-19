<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import api from '../../api/client'
import { resolveAssistantContent } from '../../utils/assistantVariants'

const props = defineProps({
  groupId: { type: String, required: true },
  learnerId: { type: String, required: true },
})
const route = useRoute()
const auth = useAuthStore()
const learnerName = ref('')
const timeline = ref({ sessions: [], traces: [] })
const competences = ref([])
const loading = ref({ timeline: false, competences: false, validating: false })
const error = ref('')
const canValidateTraces = computed(() => {
  const role = String(auth.user?.role || '').toUpperCase()
  return auth.isAdminLike || ['TUTOR', 'TRAINER', 'COORDO'].includes(role)
})

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

/** Badges compacts à partir de `p0_debug` (timeline dashboard). */
function p0DebugBadges(d) {
  if (!d || typeof d !== 'object') return []
  const out = []
  const move = String(d.move || '').trim()
  if (move) out.push({ label: move, cls: 'text-bg-info' })
  const nq = d.n_questions
  if (nq !== undefined && nq !== null && nq !== '') {
    out.push({ label: `Q${nq}`, cls: 'text-bg-primary' })
  }
  const clo = String(d.closure_signal || 'none')
  if (clo && clo !== 'none') out.push({ label: `clôture: ${clo}`, cls: 'text-bg-success' })
  const help = String(d.learner_help_request || 'none')
  if (help && help !== 'none') out.push({ label: `aide: ${help}`, cls: 'text-bg-warning' })
  const rep = String(d.repetition_signal || 'none')
  if (rep && rep !== 'none') out.push({ label: `répétition: ${rep}`, cls: 'text-bg-secondary' })
  if (typeof d.covered_count === 'number' || typeof d.remaining_count === 'number') {
    out.push({
      label: `fil ${d.covered_count ?? 0}/${d.remaining_count ?? 0}`,
      cls: 'text-bg-light text-dark border',
    })
  }
  const lr = String(d.loop_risk || 'low')
  if (lr && lr !== 'low') out.push({ label: `boucle: ${lr}`, cls: 'text-bg-danger' })
  const ml = String(d.meta_leak_risk || 'low')
  if (ml && ml !== 'low') out.push({ label: `méta: ${ml}`, cls: 'text-bg-danger' })
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
                      v-if="message.role !== 'ASSISTANT' && p0DebugBadges(message.p0_debug).length"
                      class="d-flex flex-wrap justify-content-end gap-1 mt-1"
                    >
                      <span
                        v-for="(b, bi) in p0DebugBadges(message.p0_debug)"
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
