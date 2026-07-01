<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/client'
import ConversationProfileSelector from '../components/learner/ConversationProfileSelector.vue'
import { resolveTrainerHomeSessionCta } from '../utils/trainerUiLabels'
import { isTutorWorkspaceProfileName } from '../utils/tutorWorkspaceProfiles.js'

const router = useRouter()

const loading = ref(true)
const creatingSession = ref(false)
const loadingProfiles = ref(false)
const error = ref('')
const groups = ref([])
const sessions = ref([])
const conversationProfiles = ref([])
const selectedGroupId = ref('')
const selectedProfileId = ref('')

const activeProfiles = computed(() => {
  const active = conversationProfiles.value.filter((profile) => (
    String(profile?.status || '').toLowerCase() === 'active'
  ))
  const nonTutor = active.filter((profile) => !isTutorWorkspaceProfileName(profile?.name))
  return nonTutor.length ? nonTutor : active
})

const canCreateSession = computed(() => (
  Boolean(selectedGroupId.value || groups.value.length)
  && Boolean(selectedProfileId.value)
  && activeProfiles.value.length > 0
))

const sessionCtaLabel = computed(() => resolveTrainerHomeSessionCta({ role: 'TRAINER' }))

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

function syncProfileSelection() {
  const profiles = activeProfiles.value
  if (!profiles.length) {
    selectedProfileId.value = ''
    return
  }
  const orgDefault = profiles.find((profile) => profile.is_default)
  if (orgDefault?.id) {
    selectedProfileId.value = String(orgDefault.id)
    return
  }
  const currentStillValid = profiles.some((profile) => (
    String(profile.id) === String(selectedProfileId.value)
  ))
  if (!currentStillValid) {
    selectedProfileId.value = String(profiles[0].id)
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
    const [groupsResponse, sessionsResponse] = await Promise.all([
      api.get('/groups/'),
      api.get('/hugo/sessions/'),
    ])
    await loadConversationProfiles()
    const groupsData = groupsResponse.data
    const sessionsData = sessionsResponse.data
    groups.value = Array.isArray(groupsData) ? groupsData : (groupsData.results || [])
    sessions.value = Array.isArray(sessionsData) ? sessionsData : (sessionsData.results || [])
    if (!selectedGroupId.value && groups.value.length) {
      selectedGroupId.value = groups.value[0].id
    }
    syncProfileSelection()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Impossible de charger votre espace formateur.'
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
    const { data } = await api.post('/hugo/sessions/', payload)
    router.push({ name: 'ProdTrainerChatSession', params: { sessionId: data.id } })
  } catch (err) {
    error.value = err.response?.data?.detail || 'Impossible de créer une nouvelle session.'
  } finally {
    creatingSession.value = false
  }
}

function trainerSessionRoute(session) {
  return {
    name: 'ProdTrainerChatSession',
    params: { sessionId: String(session?.id || '').trim() },
  }
}

watch(selectedGroupId, syncProfileSelection)

onMounted(loadHome)
</script>

<template>
  <div class="container-xxl py-3 py-lg-4">
    <header class="mb-4">
      <h1 class="h4 mb-1">Mon chat formateur</h1>
      <p class="text-muted mb-0 small">
        Espace conversationnel pour expliciter, arbitrer et importer vers la base de connaissances.
      </p>
    </header>

    <div v-if="loading" class="d-flex justify-content-center py-5">
      <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Chargement…</span></div>
    </div>

    <div v-else class="row g-4">
      <div class="col-12 col-xl-4">
        <section class="card prod-panel h-100">
          <div class="card-body">
            <h2 class="prod-section-title">Démarrer un échange</h2>
            <p class="text-muted mb-4">
              Lancez une session pour dialoguer avec Hugo sur un sujet métier ou pédagogique.
            </p>
            <ConversationProfileSelector
              v-model="selectedProfileId"
              :profiles="activeProfiles"
              :disabled="creatingSession"
              :loading="loadingProfiles"
            />
            <p v-if="!loadingProfiles && !activeProfiles.length" class="alert alert-warning py-2 px-3 small mt-3 mb-0">
              Aucun profil conversationnel actif — vous pouvez tout de même rouvrir une session existante ci-contre.
            </p>
            <button
              type="button"
              class="btn btn-primary w-100 mt-3"
              data-testid="trainer-create-session-btn"
              :disabled="!canCreateSession || creatingSession || loadingProfiles"
              @click="createSession"
            >
              {{ creatingSession ? 'Ouverture...' : sessionCtaLabel }}
            </button>
            <div v-if="error" class="alert alert-danger mt-3 mb-0">{{ error }}</div>
          </div>
        </section>
      </div>

      <div class="col-12 col-xl-8">
        <section class="card prod-panel">
          <div class="card-body">
            <h2 class="prod-section-title mb-3">Sessions récentes</h2>
            <div v-if="!sessions.length" class="text-muted">Aucune session pour le moment.</div>
            <div v-else class="row g-3">
              <div v-for="session in sessions" :key="session.id" class="col-12 col-md-6">
                <router-link
                  :to="trainerSessionRoute(session)"
                  class="prod-session-card w-100 text-start text-decoration-none text-body"
                  data-testid="trainer-open-session-card"
                >
                  <p class="prod-session-card__preview mb-2">
                    {{ session.learner_conversation_profile?.name || 'Session formateur' }}
                  </p>
                  <span class="small text-muted">{{ formatDate(session.updated_at || session.created_at) }}</span>
                </router-link>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>
