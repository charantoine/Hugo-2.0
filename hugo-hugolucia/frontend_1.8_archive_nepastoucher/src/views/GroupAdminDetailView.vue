<script setup>
import { ref, onMounted, watch, computed, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import api, { runExportAndDownload } from '../api/client'
import { useAuthStore } from '../stores/auth'
import {
  conversationConfigBadge,
  completenessLabel,
} from '../utils/learnerProfileCompleteness'
import ActiveOrganisationBanner from '../components/admin/ActiveOrganisationBanner.vue'

const route = useRoute()
const auth = useAuthStore()
const canManageTutorLinks = computed(() => auth.isSuperAdmin)

const group = ref(null)
const loadingGroup = ref(false)
const groupError = ref('')
const savingBackend = ref(false)
const backendError = ref('')
const savingDisplayProfile = ref(false)
const displayProfileError = ref('')
const classifierSaving = ref(false)
const classifierError = ref('')

const members = ref([])
const loadingMembers = ref(false)
const membersError = ref('')

const users = ref([])
const loadingUsers = ref(false)
const usersError = ref('')
const selectedMemberId = ref('')
const addingMember = ref(false)
const memberSuccess = ref('')
const tutorLinks = ref([])
const loadingTutorLinks = ref(false)
const tutorLinksError = ref('')
const selectedTutorId = ref('')
const selectedLearnerId = ref('')
const linkingTutorLearner = ref(false)
const tutorLinksSuccess = ref('')

const tutorPrompts = ref([])
const loadingTutorPrompts = ref(false)
const tutorPromptError = ref('')
const selectedTutorPromptId = ref('')
const learnerProfiles = ref([])
const loadingLearnerProfiles = ref(false)
const learnerProfileError = ref('')
const selectedLearnerProfileId = ref('')
const exportPeriodFrom = ref('')
const exportPeriodTo = ref('')
const exportingCsv = ref(false)
const exportingJson = ref(false)
const exportError = ref('')
const exportSuccess = ref('')

const orgDocuments = ref([])
const groupLibraryItems = ref([])
const newDocTitle = ref('')
const newDocSourceText = ref('')
const newDocKnowledgeType = ref('knowledge')
const newDocTrainerPriority = ref('normal')
const newDocIntendedProfiles = ref('reflective_afest')
const newDocMasteryCriteria = ref('')
const newDocCommonMistakes = ref('')
const newDocReasoningPoints = ref('')
const libraryLoading = ref(false)
const libraryError = ref('')
const libraryMsg = ref('')
const indexingDocumentId = ref('')
const libraryActionLoading = ref(false)
const referentialConfig = ref(null)

const selectedLearnerProfile = computed(() => {
  if (!selectedLearnerProfileId.value) return null
  return learnerProfiles.value.find((p) => String(p.id) === String(selectedLearnerProfileId.value))
})

const configBadge = computed(() =>
  conversationConfigBadge(
    group.value,
    selectedLearnerProfileId.value,
    learnerProfiles.value,
    selectedTutorPromptId.value,
  ),
)

const activeLibraryCount = computed(() =>
  groupLibraryItems.value.filter((item) => item.status === 'ACTIVE').length,
)

const classifierPresets = {
  safe: {
    phase_classifier_enabled: true,
    phase_classifier_min_confidence: 0.75,
    phase_classifier_max_tokens: 24,
    phase_classifier_max_input_chars: 500,
  },
  balanced: {
    phase_classifier_enabled: true,
    phase_classifier_min_confidence: 0.6,
    phase_classifier_max_tokens: 48,
    phase_classifier_max_input_chars: 700,
  },
  aggressive: {
    phase_classifier_enabled: true,
    phase_classifier_min_confidence: 0.45,
    phase_classifier_max_tokens: 64,
    phase_classifier_max_input_chars: 900,
  },
}
const p0ClassifierPresets = {
  safe: {
    p0_classifier_enabled: true,
    p0_classifier_min_confidence: 0.75,
    p0_classifier_max_tokens: 120,
    p0_classifier_max_input_chars: 700,
  },
  balanced: {
    p0_classifier_enabled: true,
    p0_classifier_min_confidence: 0.6,
    p0_classifier_max_tokens: 180,
    p0_classifier_max_input_chars: 900,
  },
  aggressive: {
    p0_classifier_enabled: true,
    p0_classifier_min_confidence: 0.45,
    p0_classifier_max_tokens: 240,
    p0_classifier_max_input_chars: 1200,
  },
}

async function loadGroup() {
  loadingGroup.value = true
  groupError.value = ''
  try {
    const { data } = await api.get(`/groups/${route.params.groupId}/`)
    group.value = data
    selectedTutorPromptId.value = data.default_tutor_prompt || ''
    selectedLearnerProfileId.value = data.default_learner_conversation_profile || ''
    await Promise.all([loadLibraryData(), loadReferentialConfig()])
  } catch (e) {
    groupError.value = e.response?.data?.detail || 'Erreur lors du chargement du groupe.'
  } finally {
    loadingGroup.value = false
  }
}

async function loadReferentialConfig() {
  const gid = route.params.groupId
  if (!gid) return
  try {
    const { data } = await api.get(`/groups/${gid}/referential-config/`)
    referentialConfig.value = data?.referential ? data : null
  } catch {
    referentialConfig.value = null
  }
}

async function loadLibraryData() {
  const gid = route.params.groupId
  if (!gid) return
  libraryLoading.value = true
  libraryError.value = ''
  try {
    const [docsRes, libRes] = await Promise.all([
      api.get('/documents/'),
      api.get(`/groups/${gid}/library/`),
    ])
    const d = docsRes.data
    orgDocuments.value = Array.isArray(d) ? d : d.results || []
    groupLibraryItems.value = libRes.data.items || []
  } catch (e) {
    libraryError.value =
      e.response?.data?.detail || "Impossible de charger la bibliothèque (droits admin requis)."
    orgDocuments.value = []
    groupLibraryItems.value = []
  } finally {
    libraryLoading.value = false
  }
}

async function createOrgDocument() {
  if (!newDocTitle.value.trim() || libraryActionLoading.value) return
  libraryActionLoading.value = true
  libraryMsg.value = ''
  libraryError.value = ''
  try {
    const parseList = (value) => String(value || '')
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean)
    await api.post('/documents/', {
      title: newDocTitle.value.trim(),
      source_text: newDocSourceText.value || '',
      meta: {
        knowledge_type: newDocKnowledgeType.value,
        trainer_priority: newDocTrainerPriority.value,
        intended_profiles: parseList(newDocIntendedProfiles.value),
        mastery_criteria: parseList(newDocMasteryCriteria.value),
        common_mistakes: parseList(newDocCommonMistakes.value),
        reasoning_points: parseList(newDocReasoningPoints.value),
      },
    })
    newDocTitle.value = ''
    newDocSourceText.value = ''
    newDocKnowledgeType.value = 'knowledge'
    newDocTrainerPriority.value = 'normal'
    newDocIntendedProfiles.value = 'reflective_afest'
    newDocMasteryCriteria.value = ''
    newDocCommonMistakes.value = ''
    newDocReasoningPoints.value = ''
    libraryMsg.value = 'Document créé. Indexez-le puis liez-le à ce groupe pour le RAG Hugo.'
    await loadLibraryData()
  } catch (e) {
    const d = e.response?.data
    libraryError.value =
      (typeof d === 'string' ? d : d?.detail) ||
      (Array.isArray(d) ? JSON.stringify(d) : null) ||
      'Création impossible.'
  } finally {
    libraryActionLoading.value = false
  }
}

async function indexDocument(docId) {
  indexingDocumentId.value = docId
  libraryMsg.value = ''
  libraryError.value = ''
  try {
    const { data } = await api.post(`/documents/${docId}/index/`)
    libraryMsg.value = `Indexation : ${data.chunks_count} chunk(s), statut ${data.quality_flag}.`
    await loadLibraryData()
  } catch (e) {
    libraryError.value = e.response?.data?.detail || 'Indexation impossible.'
  } finally {
    indexingDocumentId.value = ''
  }
}

async function linkDocumentToGroup(docId) {
  if (!group.value?.id || libraryActionLoading.value) return
  libraryActionLoading.value = true
  libraryMsg.value = ''
  libraryError.value = ''
  try {
    await api.post(`/groups/${group.value.id}/library/`, { document_id: docId })
    libraryMsg.value = 'Document lié au groupe (RAG).'
    await loadLibraryData()
  } catch (e) {
    libraryError.value = e.response?.data?.detail || 'Liaison impossible.'
  } finally {
    libraryActionLoading.value = false
  }
}

async function deactivateGroupDocument(gdId) {
  if (!group.value?.id || libraryActionLoading.value) return
  libraryActionLoading.value = true
  libraryError.value = ''
  try {
    await api.put(`/groups/${group.value.id}/library/${gdId}/`, { status: 'INACTIVE' })
    libraryMsg.value = 'Liaison désactivée pour ce document.'
    await loadLibraryData()
  } catch (e) {
    libraryError.value = e.response?.data?.detail || 'Mise à jour impossible.'
  } finally {
    libraryActionLoading.value = false
  }
}

function isDocLinkedToGroup(docId) {
  return groupLibraryItems.value.some(
    (item) => String(item.document_id) === String(docId) && item.status === 'ACTIVE',
  )
}

async function updateBackend(newBackend) {
  if (!group.value?.id || savingBackend.value) return
  savingBackend.value = true
  backendError.value = ''
  try {
    await api.patch(`/groups/${group.value.id}/`, {
      llm_backend: newBackend,
    })
    group.value.llm_backend = newBackend
  } catch (e) {
    backendError.value = e.response?.data?.detail || "Erreur lors du changement de moteur LLM."
  } finally {
    savingBackend.value = false
  }
}

async function updateDisplayProfile(profile) {
  if (!group.value?.id || savingDisplayProfile.value) return
  savingDisplayProfile.value = true
  displayProfileError.value = ''
  try {
    const { data } = await api.patch(`/groups/${group.value.id}/`, {
      learner_display_profile: profile,
    })
    group.value = data
  } catch (e) {
    displayProfileError.value = e.response?.data?.detail || 'Erreur lors du changement de profil d’affichage.'
  } finally {
    savingDisplayProfile.value = false
  }
}

async function loadMembers() {
  loadingMembers.value = true
  membersError.value = ''
  try {
    const { data } = await api.get(`/groups/${route.params.groupId}/members/`)
    members.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    membersError.value = e.response?.data?.detail || 'Erreur lors du chargement des membres.'
    members.value = []
  } finally {
    loadingMembers.value = false
  }
}

async function loadUsers() {
  loadingUsers.value = true
  usersError.value = ''
  try {
    const { data } = await api.get('/users/')
    users.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    usersError.value = e.response?.data?.detail || 'Erreur lors du chargement des utilisateurs.'
    users.value = []
  } finally {
    loadingUsers.value = false
  }
}

async function addMemberToGroup() {
  if (!selectedMemberId.value || addingMember.value) return
  addingMember.value = true
  membersError.value = ''
  memberSuccess.value = ''
  try {
    await api.post(`/groups/${route.params.groupId}/members/`, {
      user: selectedMemberId.value,
    })
    memberSuccess.value = 'Utilisateur rattaché au groupe.'
    selectedMemberId.value = ''
    await Promise.all([loadMembers(), loadTutorLinks()])
  } catch (e) {
    membersError.value = e.response?.data?.detail || 'Erreur lors du rattachement au groupe.'
  } finally {
    addingMember.value = false
  }
}

async function loadTutorPrompts() {
  loadingTutorPrompts.value = true
  tutorPromptError.value = ''
  try {
    const { data } = await api.get('/hugo/tutor-prompts/')
    tutorPrompts.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    tutorPromptError.value = e.response?.data?.detail || 'Erreur lors du chargement des prompts apprenant.'
    tutorPrompts.value = []
  } finally {
    loadingTutorPrompts.value = false
  }
}

async function loadLearnerProfiles() {
  loadingLearnerProfiles.value = true
  learnerProfileError.value = ''
  try {
    const { data } = await api.get('/hugo/learner-conversation-profiles/')
    learnerProfiles.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    learnerProfileError.value = e.response?.data?.detail || 'Erreur lors du chargement des profils conversationnels.'
    learnerProfiles.value = []
  } finally {
    loadingLearnerProfiles.value = false
  }
}

async function loadTutorLinks() {
  loadingTutorLinks.value = true
  tutorLinksError.value = ''
  try {
    const { data } = await api.get(`/groups/${route.params.groupId}/tutor-links/`)
    tutorLinks.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    tutorLinksError.value = e.response?.data?.detail || 'Erreur lors du chargement des associations tuteur/apprenant.'
    tutorLinks.value = []
  } finally {
    loadingTutorLinks.value = false
  }
}

async function createTutorLearnerLink() {
  if (!selectedTutorId.value || !selectedLearnerId.value || linkingTutorLearner.value) return
  linkingTutorLearner.value = true
  tutorLinksError.value = ''
  tutorLinksSuccess.value = ''
  try {
    await api.post(`/groups/${route.params.groupId}/tutor-links/`, {
      tutor: selectedTutorId.value,
      learner: selectedLearnerId.value,
    })
    tutorLinksSuccess.value = 'Association tuteur/apprenant créée.'
    selectedLearnerId.value = ''
    await loadTutorLinks()
  } catch (e) {
    tutorLinksError.value = e.response?.data?.detail || "Erreur lors de l'association tuteur/apprenant."
  } finally {
    linkingTutorLearner.value = false
  }
}

async function updateDefaultTutorPrompt() {
  if (!group.value?.id) return
  tutorPromptError.value = ''
  try {
    await api.patch(`/groups/${group.value.id}/`, {
      default_tutor_prompt: selectedTutorPromptId.value || null,
    })
  } catch (e) {
    tutorPromptError.value = e.response?.data?.detail || "Erreur lors de l'association du prompt apprenant legacy."
  }
}

async function updateDefaultLearnerProfile() {
  if (!group.value?.id) return
  learnerProfileError.value = ''
  try {
    await api.patch(`/groups/${group.value.id}/`, {
      default_learner_conversation_profile: selectedLearnerProfileId.value || null,
    })
  } catch (e) {
    learnerProfileError.value =
      e.response?.data?.detail || "Erreur lors de l'association du profil conversationnel apprenant."
  }
}

function buildExportPayload(format) {
  const period = {}
  if (exportPeriodFrom.value) period.from = exportPeriodFrom.value
  if (exportPeriodTo.value) period.to = exportPeriodTo.value
  const payload = {
    format,
    group_ids: [String(route.params.groupId)],
  }
  if (Object.keys(period).length) payload.period = period
  if (format === 'csv') {
    payload.separator = ';'
    payload.include_bom = true
  }
  return payload
}

async function runGroupExport(format) {
  const isCsv = format === 'csv'
  if (isCsv && exportingCsv.value) return
  if (!isCsv && exportingJson.value) return
  exportError.value = ''
  exportSuccess.value = ''
  if (isCsv) exportingCsv.value = true
  else exportingJson.value = true

  try {
    const payload = buildExportPayload(format)
    await runExportAndDownload({ format, payload })
    exportSuccess.value = `Export ${isCsv ? 'CSV principal' : 'JSON trace_rich_v1'} téléchargé.`
  } catch (e) {
    exportError.value = e.response?.data?.detail || e.message || "Erreur lors de l'export."
  } finally {
    if (isCsv) exportingCsv.value = false
    else exportingJson.value = false
  }
}

function asNumberOrNull(value) {
  if (value === '' || value === null || value === undefined) return null
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

async function saveClassifierConfig() {
  if (!group.value?.id || classifierSaving.value) return
  classifierSaving.value = true
  classifierError.value = ''
  const payload = {
    phase_classifier_enabled: group.value.phase_classifier_enabled === null
      ? null
      : Boolean(group.value.phase_classifier_enabled),
    phase_classifier_max_tokens: asNumberOrNull(group.value.phase_classifier_max_tokens),
    phase_classifier_min_confidence: asNumberOrNull(group.value.phase_classifier_min_confidence),
    phase_classifier_max_input_chars: asNumberOrNull(group.value.phase_classifier_max_input_chars),
    p0_classifier_enabled: group.value.p0_classifier_enabled === null
      ? null
      : Boolean(group.value.p0_classifier_enabled),
    p0_classifier_max_tokens: asNumberOrNull(group.value.p0_classifier_max_tokens),
    p0_classifier_min_confidence: asNumberOrNull(group.value.p0_classifier_min_confidence),
    p0_classifier_max_input_chars: asNumberOrNull(group.value.p0_classifier_max_input_chars),
  }
  try {
    const { data } = await api.patch(`/groups/${group.value.id}/`, payload)
    group.value = data
  } catch (e) {
    classifierError.value = e.response?.data?.detail || 'Erreur lors de la sauvegarde de la calibration.'
  } finally {
    classifierSaving.value = false
  }
}

function applyClassifierPreset(presetName) {
  const preset = classifierPresets[presetName]
  if (!group.value || !preset) return
  group.value.phase_classifier_enabled = preset.phase_classifier_enabled
  group.value.phase_classifier_max_tokens = preset.phase_classifier_max_tokens
  group.value.phase_classifier_min_confidence = preset.phase_classifier_min_confidence
  group.value.phase_classifier_max_input_chars = preset.phase_classifier_max_input_chars
}

function applyP0ClassifierPreset(presetName) {
  const preset = p0ClassifierPresets[presetName]
  if (!group.value || !preset) return
  group.value.p0_classifier_enabled = preset.p0_classifier_enabled
  group.value.p0_classifier_max_tokens = preset.p0_classifier_max_tokens
  group.value.p0_classifier_min_confidence = preset.p0_classifier_min_confidence
  group.value.p0_classifier_max_input_chars = preset.p0_classifier_max_input_chars
}

function memberUser(m) {
  return users.value.find((u) => String(u.id) === String(m.user))
}

function displayName(u) {
  if (!u) return ''
  const full = [u.first_name, u.last_name].filter(Boolean).join(' ').trim()
  if (full) return full
  return u.username || u.email || String(u.id || '')
}

function roleOfMember(member) {
  return String(memberUser(member)?.role || '').toUpperCase()
}

function tutorMembers() {
  return members.value.filter((m) => {
    const role = roleOfMember(m)
    return role === 'TUTOR' || role === 'TRAINER' || role === 'COORDO'
  })
}

function learnerMembers() {
  return members.value.filter((m) => roleOfMember(m) === 'LEARNER')
}

function availableUsersForMembership() {
  const existingUserIds = new Set(members.value.map((member) => String(member.user)))
  return users.value.filter((user) => (
    !existingUserIds.has(String(user.id))
    && ['LEARNER', 'TUTOR', 'TRAINER', 'COORDO'].includes(String(user.role || '').toUpperCase())
    && user.is_active !== false
  ))
}

function userById(userId) {
  return users.value.find((u) => String(u.id) === String(userId))
}

onMounted(() => {
  loadGroup()
  loadMembers()
  loadUsers()
  loadTutorLinks()
  loadTutorPrompts()
  loadLearnerProfiles()
})

async function scrollToConversationSection() {
  if (String(route.query.section || '').toLowerCase() !== 'conversation') return
  await nextTick()
  document.getElementById('conversation-apprenant')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

watch(
  () => [loadingGroup.value, route.query.section],
  async ([loading]) => {
    if (loading) return
    await scrollToConversationSection()
  },
)

watch(
  () => route.params.groupId,
  () => {
    loadGroup()
    loadMembers()
    loadTutorLinks()
    loadLibraryData()
    loadReferentialConfig()
  },
)
</script>
<template>
  <div class="container-fluid">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item">
          <router-link to="/dashboard">Tableau de bord</router-link>
        </li>
        <li class="breadcrumb-item">
          <router-link to="/groups-admin">Groupes</router-link>
        </li>
        <li class="breadcrumb-item active" aria-current="page">
          {{ group?.name || 'Groupe' }}
        </li>
      </ol>
    </nav>

    <div class="d-flex flex-wrap align-items-center gap-2 mb-2">
      <h1 class="h4 mb-0">{{ group?.name || 'Détail du groupe' }}</h1>
      <span v-if="group" class="badge rounded-pill" :class="configBadge.class" data-testid="group-config-badge">
        {{ configBadge.text }}
      </span>
    </div>
    <ActiveOrganisationBanner show-switcher-hint />

    <div v-if="groupError" class="alert alert-danger" role="alert">{{ groupError }}</div>

    <div v-if="loadingGroup" class="text-center py-4">
      <div class="spinner-border spinner-border-sm text-primary" role="status">
        <span class="visually-hidden">Chargement…</span>
      </div>
    </div>

    <template v-else-if="group">
      <!-- Cohorte -->
      <div class="card shadow-sm mb-4">
        <div class="card-body">
          <h2 class="h5 mb-3">Cohorte</h2>
          <div v-if="membersError || usersError" class="alert alert-danger" role="alert">
            {{ membersError || usersError }}
          </div>
          <div v-if="loadingMembers || loadingUsers" class="text-center py-3">
            <div class="spinner-border spinner-border-sm text-primary" role="status">
              <span class="visually-hidden">Chargement…</span>
            </div>
          </div>
          <ul v-else-if="members.length" class="list-group list-group-flush mb-3">
            <li
              v-for="m in members"
              :key="m.id"
              class="list-group-item d-flex justify-content-between align-items-center px-0"
            >
              <div>
                <router-link
                  v-if="memberUser(m)"
                  :to="{ name: 'UserDetail', params: { userId: memberUser(m).id } }"
                >
                  {{ memberUser(m).username || memberUser(m).email }}
                </router-link>
                <span v-else>{{ m.user }}</span>
                <span
                  v-if="memberUser(m)?.email && memberUser(m)?.username"
                  class="text-muted small"
                >
                  ({{ memberUser(m).email }})
                </span>
              </div>
              <span v-if="memberUser(m)" class="badge bg-light text-muted text-uppercase">
                {{ memberUser(m).role }}
              </span>
            </li>
          </ul>
          <p v-else class="text-muted small">Aucun membre pour le moment.</p>

          <h3 class="h6 mb-2">Ajouter un membre</h3>
          <div v-if="memberSuccess" class="alert alert-success py-2">{{ memberSuccess }}</div>
          <div class="row g-2 align-items-end mb-3">
            <div class="col-12 col-md-9">
              <label for="member-select" class="form-label small mb-1">Utilisateur actif</label>
              <select
                id="member-select"
                v-model="selectedMemberId"
                class="form-select form-select-sm"
                :disabled="loadingMembers || loadingUsers || addingMember"
              >
                <option value="">Sélectionner un utilisateur…</option>
                <option v-for="user in availableUsersForMembership()" :key="user.id" :value="user.id">
                  {{ displayName(user) }} — {{ user.role }}
                </option>
              </select>
            </div>
            <div class="col-12 col-md-3 d-grid">
              <button
                type="button"
                class="btn btn-sm btn-primary"
                :disabled="!selectedMemberId || addingMember"
                @click="addMemberToGroup"
              >
                {{ addingMember ? 'Ajout…' : 'Ajouter' }}
              </button>
            </div>
          </div>

          <template v-if="canManageTutorLinks">
            <hr />
            <h3 class="h6 mb-2">Associations tuteur / apprenant</h3>
            <p class="small text-muted">Réservé au SUPERADMIN (transitoire).</p>
            <div v-if="tutorLinksError" class="alert alert-danger py-2">{{ tutorLinksError }}</div>
            <div v-if="tutorLinksSuccess" class="alert alert-success py-2">{{ tutorLinksSuccess }}</div>
            <div class="row g-2 align-items-end mb-3">
              <div class="col-12 col-md-5">
                <label for="tutor-select" class="form-label small mb-1">Tuteur</label>
                <select id="tutor-select" v-model="selectedTutorId" class="form-select form-select-sm">
                  <option value="">Sélectionner…</option>
                  <option v-for="m in tutorMembers()" :key="m.id" :value="m.user">
                    {{ displayName(memberUser(m)) }}
                  </option>
                </select>
              </div>
              <div class="col-12 col-md-5">
                <label for="learner-select" class="form-label small mb-1">Apprenant</label>
                <select id="learner-select" v-model="selectedLearnerId" class="form-select form-select-sm">
                  <option value="">Sélectionner…</option>
                  <option v-for="m in learnerMembers()" :key="m.id" :value="m.user">
                    {{ displayName(memberUser(m)) }}
                  </option>
                </select>
              </div>
              <div class="col-12 col-md-2 d-grid">
                <button
                  type="button"
                  class="btn btn-sm btn-outline-primary"
                  :disabled="!selectedTutorId || !selectedLearnerId || linkingTutorLearner"
                  @click="createTutorLearnerLink"
                >
                  Associer
                </button>
              </div>
            </div>
            <ul v-if="tutorLinks.length" class="list-group list-group-flush small">
              <li v-for="link in tutorLinks" :key="link.id" class="list-group-item px-0">
                <strong>{{ displayName(userById(link.tutor)) }}</strong>
                <span class="text-muted"> accompagne </span>
                <strong>{{ displayName(userById(link.learner)) }}</strong>
              </li>
            </ul>
          </template>
        </div>
      </div>

      <!-- Conversation apprenant -->
      <div id="conversation-apprenant" class="card shadow-sm mb-4">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start flex-wrap gap-2 mb-3">
            <h2 class="h5 mb-0">Conversation apprenant</h2>
            <router-link
              :to="{ path: '/admin/conversation/learner/profiles', query: { groupId: route.params.groupId } }"
              class="small"
            >
              Gérer les profils globaux
            </router-link>
          </div>
          <label for="default-learner-profile" class="form-label"><strong>Profil conversationnel du groupe</strong></label>
          <select
            id="default-learner-profile"
            v-model="selectedLearnerProfileId"
            class="form-select form-select-sm mb-2"
            :disabled="loadingLearnerProfiles"
            @change="updateDefaultLearnerProfile"
          >
            <option value="">Aucun (profil org ou legacy)</option>
            <option v-for="p in learnerProfiles" :key="p.id" :value="p.id">
              {{ p.name }}{{ p.is_default ? ' (défaut org)' : '' }}
            </option>
          </select>
          <p v-if="selectedLearnerProfile" class="small mb-2">
            Profil actif : <strong>{{ selectedLearnerProfile.name }}</strong>
            <span class="badge rounded-pill ms-1 text-bg-light border">
              {{ completenessLabel(selectedLearnerProfile) }} slots
            </span>
          </p>
          <p class="text-muted small mb-3">
            Le profil global s’applique à toutes les séances du groupe ; l’apprenant choisit diag / réflexif / bûchage en séance.
          </p>
          <p v-if="learnerProfileError" class="text-danger small">{{ learnerProfileError }}</p>

          <label for="learner-display-profile" class="form-label"><strong>Profil d’affichage apprenant</strong></label>
          <select
            id="learner-display-profile"
            :value="group.learner_display_profile || 'professional'"
            class="form-select form-select-sm"
            :disabled="savingDisplayProfile"
            @change="updateDisplayProfile($event.target.value)"
          >
            <option value="youth">Jeune (A1)</option>
            <option value="adult">Adulte</option>
            <option value="professional">Standard professionnel</option>
          </select>
          <p v-if="displayProfileError" class="text-danger small mb-0">{{ displayProfileError }}</p>
        </div>
      </div>

      <!-- Référentiel & bibliothèque -->
      <div class="card shadow-sm mb-4">
        <div class="card-body">
          <h2 class="h5 mb-3">Référentiel &amp; bibliothèque</h2>
          <p class="mb-2">
            <router-link
              :to="{ name: 'GroupReferentialConfig', params: { groupId: group.id } }"
              class="btn btn-sm btn-outline-primary"
              data-testid="group-referential-link"
            >
              Référentiel RNCP du groupe
            </router-link>
          </p>
          <p v-if="referentialConfig?.referential" class="small text-muted mb-2">
            Référentiel associé : <strong>{{ referentialConfig.referential.name }}</strong>
            <span v-if="referentialConfig.referential.source_ref">({{ referentialConfig.referential.source_ref }})</span>
          </p>
          <p v-else class="small text-muted mb-2">Aucun référentiel associé à ce groupe.</p>
          <p class="small mb-0">
            Bibliothèque documentaire (RAG) :
            <strong>{{ activeLibraryCount }}</strong> document(s) lié(s) activement.
            <span class="text-muted">— détail dans Paramètres avancés ci-dessous.</span>
          </p>
        </div>
      </div>

      <!-- Expert accordion -->
      <div class="accordion mb-4" id="groupExpertAccordion">
        <div class="accordion-item">
          <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#expertExports">
              Exports (Felix-ready)
            </button>
          </h2>
          <div id="expertExports" class="accordion-collapse collapse" data-bs-parent="#groupExpertAccordion">
            <div class="accordion-body">
              <div class="row g-2">
                <div class="col-6">
                  <label class="form-label small mb-1">Période — du</label>
                  <input v-model="exportPeriodFrom" type="date" class="form-control form-control-sm" />
                </div>
                <div class="col-6">
                  <label class="form-label small mb-1">au</label>
                  <input v-model="exportPeriodTo" type="date" class="form-control form-control-sm" />
                </div>
              </div>
              <div class="d-flex flex-wrap gap-2 mt-2">
                <button type="button" class="btn btn-sm btn-outline-primary" :disabled="exportingCsv || exportingJson" @click="runGroupExport('csv')">
                  {{ exportingCsv ? 'Export…' : 'CSV principal' }}
                </button>
                <button type="button" class="btn btn-sm btn-outline-secondary" :disabled="exportingCsv || exportingJson" @click="runGroupExport('json')">
                  {{ exportingJson ? 'Export…' : 'JSON trace_rich_v1' }}
                </button>
              </div>
              <p v-if="exportSuccess" class="text-success small mb-0 mt-1">{{ exportSuccess }}</p>
              <p v-if="exportError" class="text-danger small mb-0 mt-1">{{ exportError }}</p>
            </div>
          </div>
        </div>

        <div class="accordion-item">
          <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#expertLlm">
              Moteur LLM du groupe
            </button>
          </h2>
          <div id="expertLlm" class="accordion-collapse collapse" data-bs-parent="#groupExpertAccordion">
            <div class="accordion-body">
              <select
                id="llm-backend"
                v-model="group.llm_backend"
                class="form-select form-select-sm"
                :disabled="savingBackend"
                @change="updateBackend(group.llm_backend)"
              >
                <option value="OLLAMA">Ollama (local)</option>
                <option value="OVH_AI">OVH AI Endpoints</option>
              </select>
              <p v-if="backendError" class="text-danger small mb-0 mt-1">{{ backendError }}</p>
            </div>
          </div>
        </div>

        <div class="accordion-item">
          <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#expertClassifiers">
              Calibrations classifieurs (phase &amp; P0)
            </button>
          </h2>
          <div id="expertClassifiers" class="accordion-collapse collapse" data-bs-parent="#groupExpertAccordion">
            <div class="accordion-body">
              <p class="small fw-bold mb-2">Classifieur de phase</p>
              <div class="d-flex gap-2 mb-2">
                <button type="button" class="btn btn-sm btn-outline-secondary" @click="applyClassifierPreset('safe')">safe</button>
                <button type="button" class="btn btn-sm btn-outline-secondary" @click="applyClassifierPreset('balanced')">balanced</button>
                <button type="button" class="btn btn-sm btn-outline-secondary" @click="applyClassifierPreset('aggressive')">aggressive</button>
              </div>
              <div class="row g-2 mb-3">
                <div class="col-12">
                  <select v-model="group.phase_classifier_enabled" class="form-select form-select-sm">
                    <option :value="null">Fallback settings</option>
                    <option :value="true">true</option>
                    <option :value="false">false</option>
                  </select>
                </div>
                <div class="col-6">
                  <input v-model.number="group.phase_classifier_min_confidence" type="number" min="0" max="1" step="0.01" class="form-control form-control-sm" placeholder="Min confidence" />
                </div>
                <div class="col-6">
                  <input v-model.number="group.phase_classifier_max_tokens" type="number" min="1" class="form-control form-control-sm" placeholder="Max tokens" />
                </div>
              </div>
              <p class="small fw-bold mb-2">Classifieur P0</p>
              <div class="d-flex gap-2 mb-2">
                <button type="button" class="btn btn-sm btn-outline-secondary" @click="applyP0ClassifierPreset('safe')">safe</button>
                <button type="button" class="btn btn-sm btn-outline-secondary" @click="applyP0ClassifierPreset('balanced')">balanced</button>
                <button type="button" class="btn btn-sm btn-outline-secondary" @click="applyP0ClassifierPreset('aggressive')">aggressive</button>
              </div>
              <div class="row g-2 mb-2">
                <div class="col-12">
                  <select v-model="group.p0_classifier_enabled" class="form-select form-select-sm">
                    <option :value="null">Fallback settings</option>
                    <option :value="true">true</option>
                    <option :value="false">false</option>
                  </select>
                </div>
              </div>
              <button type="button" class="btn btn-sm btn-outline-primary" :disabled="classifierSaving" @click="saveClassifierConfig">
                {{ classifierSaving ? 'Enregistrement…' : 'Sauvegarder calibrations' }}
              </button>
              <p v-if="classifierError" class="text-danger small mb-0 mt-1">{{ classifierError }}</p>
            </div>
          </div>
        </div>

        <div v-if="!selectedLearnerProfileId" class="accordion-item">
          <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#expertLegacyPrompt">
              Prompt apprenant legacy (1.6)
            </button>
          </h2>
          <div id="expertLegacyPrompt" class="accordion-collapse collapse" data-bs-parent="#groupExpertAccordion">
            <div class="accordion-body">
              <select
                id="default-tutor-prompt"
                v-model="selectedTutorPromptId"
                class="form-select form-select-sm"
                :disabled="loadingTutorPrompts"
                @change="updateDefaultTutorPrompt"
              >
                <option value="">Aucun (défaut organisation)</option>
                <option v-for="p in tutorPrompts" :key="p.id" :value="p.id">{{ p.code }} — {{ p.name }}</option>
              </select>
              <p v-if="tutorPromptError" class="text-danger small mb-0">{{ tutorPromptError }}</p>
            </div>
          </div>
        </div>

        <div class="accordion-item">
          <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#expertRag">
              Bibliothèque RAG — gestion détaillée
            </button>
          </h2>
          <div id="expertRag" class="accordion-collapse collapse" data-bs-parent="#groupExpertAccordion">
            <div class="accordion-body">
              <p v-if="libraryLoading" class="small text-muted">Chargement…</p>
              <p v-if="libraryError" class="text-danger small">{{ libraryError }}</p>
              <p v-if="libraryMsg" class="text-success small">{{ libraryMsg }}</p>
              <div class="mb-3">
                <label class="form-label small">Nouveau document</label>
                <input v-model="newDocTitle" type="text" class="form-control form-control-sm mb-1" placeholder="Titre" />
                <textarea v-model="newDocSourceText" class="form-control form-control-sm mb-2" rows="3" placeholder="Contenu…" />
                <button type="button" class="btn btn-sm btn-outline-primary" :disabled="libraryActionLoading || !newDocTitle.trim()" @click="createOrgDocument">
                  Créer le document
                </button>
              </div>
              <div v-if="orgDocuments.length" class="table-responsive small mb-3">
                <table class="table table-sm table-bordered">
                  <thead><tr><th>Titre</th><th>Chunks</th><th></th></tr></thead>
                  <tbody>
                    <tr v-for="d in orgDocuments" :key="d.id">
                      <td>{{ d.title }}</td>
                      <td>{{ d.chunks_count ?? 0 }}</td>
                      <td class="text-nowrap">
                        <button type="button" class="btn btn-sm btn-outline-secondary me-1" @click="indexDocument(d.id)">Indexer</button>
                        <button v-if="!isDocLinkedToGroup(d.id)" type="button" class="btn btn-sm btn-outline-success" @click="linkDocumentToGroup(d.id)">Lier</button>
                        <span v-else class="badge bg-success">Lié</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <p class="small fw-bold">Documents liés au groupe</p>
              <ul v-if="groupLibraryItems.filter((x) => x.status === 'ACTIVE').length" class="list-group list-group-flush small">
                <li v-for="item in groupLibraryItems.filter((x) => x.status === 'ACTIVE')" :key="item.id" class="list-group-item px-0 d-flex justify-content-between">
                  <span>{{ item.document_title }} ({{ item.chunks_count }} chunks)</span>
                  <button type="button" class="btn btn-sm btn-outline-warning" @click="deactivateGroupDocument(item.id)">Retirer</button>
                </li>
              </ul>
              <p v-else class="text-muted small mb-0">Aucune liaison active.</p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
