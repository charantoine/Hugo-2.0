<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/client'
import { frontendFeatures, getGamificationProfileTheme } from '../utils/frontendConfig'

const router = useRouter()

const loading = ref(true)
const creatingSession = ref(false)
const loadingTutorPrompts = ref(false)
const favoriteUpdatingId = ref('')
const error = ref('')
const groups = ref([])
const sessions = ref([])
const tutorPrompts = ref([])
const selectedGroupId = ref('')
const selectedTutorPromptId = ref('')
const sessionDateFrom = ref('')
const sessionDateTo = ref('')
const favoritesOnly = ref(false)

const theme = computed(() => getGamificationProfileTheme(frontendFeatures.gamification_profile))
const selectedGroup = computed(() => groups.value.find((group) => String(group.id) === String(selectedGroupId.value)) || null)
const selectedTutorPrompt = computed(() => (
  tutorPrompts.value.find((prompt) => String(prompt.id) === String(selectedTutorPromptId.value)) || null
))
const visibleSessions = computed(() => {
  const currentGroupId = String(selectedGroupId.value || '').trim()
  const createdAfter = String(sessionDateFrom.value || '').trim()
  const createdBefore = String(sessionDateTo.value || '').trim()
  const source = [...sessions.value]
  source.sort((left, right) => new Date(right.updated_at || right.created_at || 0) - new Date(left.updated_at || left.created_at || 0))
  return source.filter((session) => {
    if (currentGroupId && String(session.group || '') !== currentGroupId) return false
    if (favoritesOnly.value && !session.is_favorite) return false

    const createdAt = String(session.created_at || '').slice(0, 10)
    if (createdAfter && createdAt && createdAt < createdAfter) return false
    if (createdBefore && createdAt && createdAt > createdBefore) return false
    return true
  })
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

function summarizePhase(phase) {
  const value = String(phase || '').trim().toLowerCase()
  if (value === 'opening') return 'Raconter'
  if (value === 'exploration') return 'Comprendre'
  if (value === 'conceptualization') return 'Retenir'
  if (value === 'closure') return 'Transmettre'
  return 'Raconter'
}

function sessionPreview(session) {
  const text = String(session?.first_learner_message || '').trim()
  if (!text) return 'Nouvelle scène prête à démarrer.'
  return text.length > 110 ? `${text.slice(0, 110).trim()}...` : text
}

function clearSessionDateFilters() {
  sessionDateFrom.value = ''
  sessionDateTo.value = ''
}

async function loadTutorPrompts() {
  loadingTutorPrompts.value = true
  try {
    const { data } = await api.get('/hugo/tutor-prompts/')
    tutorPrompts.value = Array.isArray(data) ? data : (data.results || [])
    if (!selectedTutorPromptId.value) {
      const defaultPrompt = tutorPrompts.value.find((prompt) => prompt?.is_default)
      if (defaultPrompt?.id) {
        selectedTutorPromptId.value = defaultPrompt.id
      }
    }
  } catch {
    tutorPrompts.value = []
  } finally {
    loadingTutorPrompts.value = false
  }
}

async function loadHome() {
  loading.value = true
  error.value = ''
  try {
    const [{ data: groupsData }, { data: sessionsData }] = await Promise.all([
      api.get('/groups/'),
      api.get('/hugo/sessions/'),
      loadTutorPrompts(),
    ])
    groups.value = Array.isArray(groupsData) ? groupsData : (groupsData.results || [])
    sessions.value = Array.isArray(sessionsData) ? sessionsData : (sessionsData.results || [])

    if (!selectedGroupId.value && groups.value.length) {
      selectedGroupId.value = groups.value[0].id
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Impossible de charger ton espace.'
  } finally {
    loading.value = false
  }
}

async function createSession() {
  const groupId = selectedGroupId.value || groups.value[0]?.id
  if (!groupId || creatingSession.value) return
  creatingSession.value = true
  error.value = ''
  try {
    const payload = { group: groupId }
    if (selectedTutorPromptId.value) payload.tutor_prompt_id = selectedTutorPromptId.value
    const { data } = await api.post('/hugo/sessions/', payload)
    router.push({ name: 'ProdLearnerSession', params: { sessionId: data.id } })
  } catch (err) {
    error.value = err.response?.data?.detail || 'Impossible de créer une nouvelle session.'
  } finally {
    creatingSession.value = false
  }
}

function openSession(session) {
  router.push({ name: 'ProdLearnerSession', params: { sessionId: session.id } })
}

async function toggleSessionFavorite(session, event) {
  event?.preventDefault?.()
  event?.stopPropagation?.()
  if (!session?.id || favoriteUpdatingId.value) return
  favoriteUpdatingId.value = String(session.id)
  error.value = ''
  try {
    const { data } = await api.patch(`/hugo/sessions/${session.id}/`, {
      is_favorite: !session.is_favorite,
    })
    const patch = data && typeof data === 'object' ? data : {}
    sessions.value = sessions.value.map((item) => (
      item.id === session.id ? { ...item, ...patch } : item
    ))
  } catch (err) {
    error.value = err.response?.data?.detail || 'Impossible de mettre à jour ce favori.'
  } finally {
    favoriteUpdatingId.value = ''
  }
}

onMounted(loadHome)
</script>

<template>
  <div class="container-xxl py-3 py-lg-4">
    <section class="prod-hero mb-4 mb-lg-5 d-none">
      <div>
        <span class="prod-hero__eyebrow">Parcours montrable</span>
        <h1 class="prod-hero__title">Tuteur numérique</h1>
        <p class="prod-hero__text">
          Ici, tu retrouves seulement l’essentiel : démarrer une session, reprendre une conversation et voir ce qui progresse vraiment.
        </p>
      </div>
      <div class="prod-hero__aside">
        <div class="prod-pill prod-pill--bright">
          <span class="prod-pill__label">{{ theme.label }}</span>
          <strong>{{ theme.title }}</strong>
        </div>
        <p class="prod-hero__aside-text">{{ theme.subtitle }}</p>
      </div>
    </section>

    <div v-if="loading" class="d-flex justify-content-center py-5">
      <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Chargement…</span></div>
    </div>

    <div v-else class="row g-4">
      <div class="col-12 col-xl-4">
        <section class="card prod-panel h-100">
          <div class="card-body">
            <h2 class="prod-section-title">Démarrer une nouvelle scène</h2>
            <p class="text-muted mb-4">
              Choisis ton groupe, puis lance une session. Tu verras ensuite la progression, les quêtes utiles et les traces à garder.
            </p>

            <div class="mb-3">
              <label class="form-label" for="selected-group">Groupe</label>
              <select id="selected-group" v-model="selectedGroupId" class="form-select" :disabled="!groups.length">
                <option v-for="group in groups" :key="group.id" :value="group.id">{{ group.name }}</option>
              </select>
            </div>

            <div class="mb-3">
              <label class="form-label" for="selected-tutor-prompt">TutorPrompt</label>
              <select
                id="selected-tutor-prompt"
                v-model="selectedTutorPromptId"
                class="form-select"
                :disabled="loadingTutorPrompts"
              >
                <option value="">Par défaut</option>
                <option
                  v-for="prompt in tutorPrompts"
                  :key="prompt.id"
                  :value="prompt.id"
                >
                  {{ prompt.code }} — {{ prompt.name }}
                </option>
              </select>
              <p class="small text-muted mb-0 mt-2">
                {{ selectedTutorPrompt ? `Prompt actif pour la prochaine session : ${selectedTutorPrompt.code} — ${selectedTutorPrompt.name}` : 'Le prompt par défaut sera utilisé.' }}
              </p>
            </div>

            <button
              type="button"
              class="btn btn-primary w-100"
              :disabled="!groups.length || creatingSession || loadingTutorPrompts"
              @click="createSession"
            >
              {{ creatingSession ? 'Ouverture...' : 'Lancer une nouvelle session' }}
            </button>

            <p v-if="selectedGroup" class="small text-muted mb-0 mt-3">
              Groupe actif : <strong>{{ selectedGroup.name }}</strong>
            </p>
            <div v-if="error" class="alert alert-danger mt-3 mb-0">{{ error }}</div>
          </div>
        </section>
      </div>

      <div class="col-12 col-xl-8">
        <section class="card prod-panel">
          <div class="card-body">
            <div class="d-flex flex-wrap justify-content-between align-items-center gap-3 mb-4">
              <div>
                <h2 class="prod-section-title mb-1">Sessions récentes</h2>
                <p class="text-muted mb-0">Reprends une scène déjà commencée ou continue là où tu t’étais arrêté.</p>
              </div>
              <span class="badge rounded-pill text-bg-light border">{{ visibleSessions.length }} session(s)</span>
            </div>

            <div class="row g-3 align-items-end mb-4">
              <div class="col-12 col-md-4">
                <label class="form-label" for="session-date-from">Créées du</label>
                <input
                  id="session-date-from"
                  v-model="sessionDateFrom"
                  type="date"
                  class="form-control"
                >
              </div>
              <div class="col-12 col-md-4">
                <label class="form-label" for="session-date-to">au</label>
                <input
                  id="session-date-to"
                  v-model="sessionDateTo"
                  type="date"
                  class="form-control"
                >
              </div>
              <div class="col-12 col-md-4">
                <label class="form-label d-block">Filtres</label>
                <div class="d-flex flex-wrap gap-3 align-items-center">
                  <label class="form-check mb-0">
                    <input v-model="favoritesOnly" class="form-check-input" type="checkbox">
                    <span class="form-check-label">Favoris uniquement</span>
                  </label>
                  <button
                    v-if="sessionDateFrom || sessionDateTo"
                    type="button"
                    class="btn btn-link btn-sm px-0"
                    @click="clearSessionDateFilters"
                  >
                    Effacer les dates
                  </button>
                </div>
              </div>
            </div>

            <div v-if="visibleSessions.length" class="row g-3">
              <div v-for="session in visibleSessions" :key="session.id" class="col-12 col-lg-6">
                <div
                  class="prod-session-card"
                  role="button"
                  tabindex="0"
                  @click="openSession(session)"
                  @keydown.enter.prevent="openSession(session)"
                  @keydown.space.prevent="openSession(session)"
                >
                  <div class="prod-session-card__topline">
                    <span class="prod-session-card__phase">{{ summarizePhase(session.current_phase) }}</span>
                    <button
                      type="button"
                      class="prod-session-card__favorite-btn"
                      :class="session.is_favorite ? 'prod-session-card__favorite-btn--active' : ''"
                      :disabled="favoriteUpdatingId === String(session.id)"
                      :aria-pressed="session.is_favorite"
                      :title="session.is_favorite ? 'Retirer des favoris' : 'Ajouter aux favoris'"
                      @click="toggleSessionFavorite(session, $event)"
                    >
                      <i :class="session.is_favorite ? 'bi bi-heart-fill' : 'bi bi-heart'"></i>
                      <span>{{ session.is_favorite ? 'Favori' : 'Ajouter' }}</span>
                    </button>
                  </div>
                  <strong class="prod-session-card__title">
                    {{ selectedGroupId && String(session.group) === String(selectedGroupId) ? 'Session du groupe actif' : 'Session Hugo' }}
                  </strong>
                  <span v-if="session.tutor_prompt" class="prod-session-card__prompt">
                    {{ session.tutor_prompt.code }} — {{ session.tutor_prompt.name }}
                  </span>
                  <span class="prod-session-card__preview">{{ sessionPreview(session) }}</span>
                  <span class="prod-session-card__meta">
                    Dernière activité : {{ formatDate(session.updated_at || session.created_at) }}
                  </span>
                </div>
              </div>
            </div>

            <div v-else class="prod-empty-state">
              <h3>Aucune session ne correspond aux filtres</h3>
              <p>Ajuste les dates ou le filtre favoris, ou commence une première scène pour alimenter la liste.</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>
