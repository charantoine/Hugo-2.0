<script setup>
/**
 * État des lieux (migration TutorPrompt → LearnerConversationGlobalProfile) :
 * - Sélection groupe : selectedGroupId + GET /groups/
 * - Profils conversation : GET /hugo/learner-conversation-profiles/ + ConversationProfileSelector
 * - Création session : POST /hugo/sessions/ avec learner_conversation_profile_id (plus tutor_prompt_id)
 * - Posture initiale : POST /hugo/sessions/{id}/set-posture/ après création (initial_posture absent du back create)
 */
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/client'
import ConversationProfileSelector from '../components/learner/ConversationProfileSelector.vue'
import InitialPostureSelector from '../components/learner/InitialPostureSelector.vue'
import { frontendFeatures, getGamificationProfileTheme } from '../utils/frontendConfig'

const learnerUiV2 = frontendFeatures.learner_ui_v2

const router = useRouter()

const loading = ref(true)
const creatingSession = ref(false)
const loadingProfiles = ref(false)
const favoriteUpdatingId = ref('')
const error = ref('')
const groups = ref([])
const sessions = ref([])
const conversationProfiles = ref([])
const selectedGroupId = ref('')
const selectedProfileId = ref('')
const initialPosture = ref('reflective_afest')
const sessionDateFrom = ref('')
const sessionDateTo = ref('')
const favoritesOnly = ref(false)

const theme = computed(() => getGamificationProfileTheme(frontendFeatures.gamification_profile))
const selectedGroup = computed(() => groups.value.find((group) => String(group.id) === String(selectedGroupId.value)) || null)
const activeProfiles = computed(() => (
  conversationProfiles.value.filter((profile) => String(profile?.status || '').toLowerCase() === 'active')
))
const canCreateSession = computed(() => (
  Boolean(selectedGroupId.value || groups.value.length)
  && Boolean(selectedProfileId.value)
  && activeProfiles.value.length > 0
))
const groupDefaultProfileId = computed(() => (
  String(selectedGroup.value?.default_learner_conversation_profile || '').trim()
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

function sessionProfileLabel(session) {
  const profile = session?.learner_conversation_profile
  if (profile?.name) return profile.name
  if (session?.tutor_prompt) return 'Session historique'
  return 'Profil non renseigné'
}

function clearSessionDateFilters() {
  sessionDateFrom.value = ''
  sessionDateTo.value = ''
}

function syncProfileSelection() {
  const groupDefault = groupDefaultProfileId.value
  if (groupDefault && activeProfiles.value.some((profile) => String(profile.id) === groupDefault)) {
    selectedProfileId.value = groupDefault
    return
  }
  const orgDefault = activeProfiles.value.find((profile) => profile.is_default)
  if (orgDefault?.id) {
    selectedProfileId.value = orgDefault.id
    return
  }
  if (activeProfiles.value.length === 1) {
    selectedProfileId.value = activeProfiles.value[0].id
    return
  }
  if (!activeProfiles.value.some((profile) => String(profile.id) === String(selectedProfileId.value))) {
    selectedProfileId.value = activeProfiles.value[0]?.id || ''
  }
}

async function loadConversationProfiles() {
  loadingProfiles.value = true
  try {
    const { data } = await api.get('/hugo/learner-conversation-profiles/')
    conversationProfiles.value = Array.isArray(data) ? data : (data.results || [])
    syncProfileSelection()
  } catch {
    conversationProfiles.value = []
    selectedProfileId.value = ''
  } finally {
    loadingProfiles.value = false
  }
}

async function loadHome() {
  loading.value = true
  error.value = ''
  try {
    const [{ data: groupsData }, { data: sessionsData }] = await Promise.all([
      api.get('/groups/'),
      api.get('/hugo/sessions/'),
      loadConversationProfiles(),
    ])
    groups.value = Array.isArray(groupsData) ? groupsData : (groupsData.results || [])
    sessions.value = Array.isArray(sessionsData) ? sessionsData : (sessionsData.results || [])

    if (!selectedGroupId.value && groups.value.length) {
      selectedGroupId.value = groups.value[0].id
    }
    syncProfileSelection()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Impossible de charger ton espace.'
  } finally {
    loading.value = false
  }
}

async function createSession() {
  const groupId = selectedGroupId.value || groups.value[0]?.id
  if (!groupId || creatingSession.value || !canCreateSession.value) return
  creatingSession.value = true
  error.value = ''
  try {
    const payload = { group: groupId }
    if (selectedProfileId.value) {
      payload.learner_conversation_profile_id = selectedProfileId.value
    }
    // TODO(back): remplacer set-posture post-create par initial_posture dans POST /hugo/sessions/
    const { data } = await api.post('/hugo/sessions/', payload)
    const chosenPosture = String(initialPosture.value || 'reflective_afest').trim()
    if (chosenPosture && chosenPosture !== 'reflective_afest') {
      try {
        await api.post(`/hugo/sessions/${data.id}/set-posture/`, { posture: chosenPosture })
      } catch {
        // Session créée ; la posture par défaut du backend reste réflexive.
      }
    }
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

watch(selectedGroupId, () => {
  syncProfileSelection()
})

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
      <div :class="learnerUiV2 ? 'col-12' : 'col-12 col-xl-4'">
        <section class="card prod-panel h-100">
          <div class="card-body">
            <h2 class="prod-section-title">{{ learnerUiV2 ? 'Prêt à commencer ?' : 'Démarrer une nouvelle scène' }}</h2>
            <p v-if="!learnerUiV2" class="text-muted mb-4">
              Choisis ton groupe et ton profil conversationnel, puis lance une session.
            </p>
            <p v-else class="text-muted mb-4">
              Lance une nouvelle session pour échanger avec Hugo sur une situation concrète.
            </p>

            <!-- BETA_HIDDEN: sélecteurs groupe / profil / posture -->
            <template v-if="!learnerUiV2">
              <div class="mb-3 group-profile-selector">
                <label class="form-label" for="selected-group">Groupe</label>
                <select id="selected-group" v-model="selectedGroupId" class="form-select" :disabled="!groups.length">
                  <option v-for="group in groups" :key="group.id" :value="group.id">{{ group.name }}</option>
                </select>
              </div>

              <ConversationProfileSelector
                v-model="selectedProfileId"
                :profiles="conversationProfiles"
                :group-default-profile-id="groupDefaultProfileId"
                :disabled="creatingSession"
                :loading="loadingProfiles"
              />

              <InitialPostureSelector
                v-model="initialPosture"
                :disabled="creatingSession || !selectedProfileId"
              />
            </template>

            <button
              type="button"
              class="btn btn-primary w-100 mt-3"
              data-testid="create-session-btn"
              :disabled="!canCreateSession || creatingSession || loadingProfiles"
              @click="createSession"
            >
              {{ creatingSession ? 'Ouverture...' : (learnerUiV2 ? 'Démarrer ma session' : 'Lancer une nouvelle session') }}
            </button>

            <p v-if="!learnerUiV2 && selectedGroup" class="small text-muted mb-0 mt-3">
              Groupe actif : <strong>{{ selectedGroup.name }}</strong>
            </p>
            <div v-if="error" class="alert alert-danger mt-3 mb-0">{{ error }}</div>
          </div>
        </section>
      </div>

      <div :class="learnerUiV2 ? 'col-12' : 'col-12 col-xl-8'">
        <section class="card prod-panel">
          <div class="card-body">
            <div class="d-flex flex-wrap justify-content-between align-items-center gap-3 mb-4">
              <div>
                <h2 class="prod-section-title mb-1">Sessions récentes</h2>
                <p class="text-muted mb-0">Reprends une scène déjà commencée ou continue là où tu t’étais arrêté.</p>
              </div>
            </div>

            <div class="row g-2 mb-4">
              <div class="col-12 col-md-4">
                <label class="form-label small" for="session-date-from">Du</label>
                <input id="session-date-from" v-model="sessionDateFrom" type="date" class="form-control form-control-sm">
              </div>
              <div class="col-12 col-md-4">
                <label class="form-label small" for="session-date-to">Au</label>
                <input id="session-date-to" v-model="sessionDateTo" type="date" class="form-control form-control-sm">
              </div>
              <div class="col-12 col-md-4 d-flex align-items-end gap-2">
                <button type="button" class="btn btn-sm btn-outline-secondary" @click="clearSessionDateFilters">Réinitialiser</button>
                <div class="form-check mb-1">
                  <input id="favorites-only" v-model="favoritesOnly" class="form-check-input" type="checkbox">
                  <label class="form-check-label small" for="favorites-only">Favoris seulement</label>
                </div>
              </div>
            </div>

            <div v-if="!visibleSessions.length" class="text-muted">Aucune session pour ces filtres.</div>

            <div v-else class="row g-3">
              <div v-for="session in visibleSessions" :key="session.id" class="col-12 col-md-6">
                <button
                  type="button"
                  class="prod-session-card w-100 text-start"
                  @click="openSession(session)"
                >
                  <div class="d-flex justify-content-between gap-2 mb-2">
                    <span class="prod-session-card__phase">{{ summarizePhase(session.current_phase) }}</span>
                    <span
                      class="prod-session-card__favorite"
                      :class="{ 'is-active': session.is_favorite }"
                      @click="toggleSessionFavorite(session, $event)"
                    >
                      ★
                    </span>
                  </div>
                  <p class="prod-session-card__preview mb-2">{{ sessionPreview(session) }}</p>
                  <div class="d-flex flex-wrap gap-2 small text-muted">
                    <span>{{ formatDate(session.updated_at || session.created_at) }}</span>
                    <span class="prod-session-card__prompt">
                      {{ sessionProfileLabel(session) }}
                    </span>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>
