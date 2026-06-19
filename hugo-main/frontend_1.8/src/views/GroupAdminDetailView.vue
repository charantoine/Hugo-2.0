<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api, { runExportAndDownload } from '../api/client'

const route = useRoute()

const group = ref(null)
const loadingGroup = ref(false)
const groupError = ref('')
const savingBackend = ref(false)
const backendError = ref('')
const classifierSaving = ref(false)
const classifierError = ref('')

const members = ref([])
const loadingMembers = ref(false)
const membersError = ref('')

const users = ref([])
const loadingUsers = ref(false)
const usersError = ref('')
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
const libraryLoading = ref(false)
const libraryError = ref('')
const libraryMsg = ref('')
const indexingDocumentId = ref('')
const libraryActionLoading = ref(false)

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
    await loadLibraryData()
  } catch (e) {
    groupError.value = e.response?.data?.detail || 'Erreur lors du chargement du groupe.'
  } finally {
    loadingGroup.value = false
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
    await api.post('/documents/', {
      title: newDocTitle.value.trim(),
      source_text: newDocSourceText.value || '',
    })
    newDocTitle.value = ''
    newDocSourceText.value = ''
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

async function loadTutorPrompts() {
  loadingTutorPrompts.value = true
  tutorPromptError.value = ''
  try {
    const { data } = await api.get('/hugo/tutor-prompts/')
    tutorPrompts.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    tutorPromptError.value = e.response?.data?.detail || 'Erreur lors du chargement des TutorPrompt.'
    tutorPrompts.value = []
  } finally {
    loadingTutorPrompts.value = false
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
    tutorPromptError.value = e.response?.data?.detail || "Erreur lors de l'association du TutorPrompt par défaut."
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

function userById(userId) {
  return users.value.find((u) => String(u.id) === String(userId))
}

onMounted(() => {
  loadGroup()
  loadMembers()
  loadUsers()
  loadTutorLinks()
  loadTutorPrompts()
})

watch(
  () => route.params.groupId,
  () => {
    loadGroup()
    loadMembers()
    loadTutorLinks()
    loadLibraryData()
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

    <h1 class="h4 mb-4">Détail du groupe</h1>

    <div v-if="groupError" class="alert alert-danger" role="alert">
      {{ groupError }}
    </div>

    <div class="row">
      <div class="col-12 col-lg-4 mb-4">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h2 class="h5 mb-3">Informations</h2>
            <div v-if="loadingGroup" class="text-center py-3">
              <div class="spinner-border spinner-border-sm text-primary" role="status">
                <span class="visually-hidden">Chargement…</span>
              </div>
            </div>
            <template v-else-if="group">
              <p><strong>Nom :</strong> {{ group.name }}</p>
              <hr class="my-3" />
              <div>
                <p class="small fw-bold mb-2">Exports Felix-ready (v1)</p>
                <div class="row g-2">
                  <div class="col-6">
                    <label class="form-label small mb-1">Période - du</label>
                    <input
                      v-model="exportPeriodFrom"
                      type="date"
                      class="form-control form-control-sm"
                    />
                  </div>
                  <div class="col-6">
                    <label class="form-label small mb-1">au</label>
                    <input
                      v-model="exportPeriodTo"
                      type="date"
                      class="form-control form-control-sm"
                    />
                  </div>
                </div>
                <div class="d-flex flex-wrap gap-2 mt-2">
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-primary"
                    :disabled="exportingCsv || exportingJson"
                    @click="runGroupExport('csv')"
                  >
                    {{ exportingCsv ? 'Export CSV…' : 'CSV principal (Felix-ready)' }}
                  </button>
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-secondary"
                    :disabled="exportingCsv || exportingJson"
                    @click="runGroupExport('json')"
                  >
                    {{ exportingJson ? 'Export JSON…' : 'JSON trace_rich_v1' }}
                  </button>
                </div>
                <p class="text-muted small mb-0 mt-2">
                  CSV principal : 1 ligne = trace × item. JSON : payload `trace_rich_v1`.
                </p>
                <p v-if="exportSuccess" class="text-success small mb-0 mt-1">
                  {{ exportSuccess }}
                </p>
                <p v-if="exportError" class="text-danger small mb-0 mt-1">
                  {{ exportError }}
                </p>
              </div>
              <hr class="my-3" />
              <div class="mb-3">
                <label for="llm-backend" class="form-label"><strong>Moteur LLM :</strong></label>
                <select
                  id="llm-backend"
                  v-model="group.llm_backend"
                  class="form-select form-select-sm mt-1"
                  :disabled="savingBackend"
                  @change="updateBackend(group.llm_backend)"
                >
                  <option value="OLLAMA">Ollama (local)</option>
                  <option value="OVH_AI">OVH AI Endpoints</option>
                </select>
                <p v-if="backendError" class="text-danger small mb-0">
                  {{ backendError }}
                </p>
              </div>
              <div class="mb-3">
                <label for="default-tutor-prompt" class="form-label"><strong>Prompt tuteur par défaut :</strong></label>
                <select
                  id="default-tutor-prompt"
                  v-model="selectedTutorPromptId"
                  class="form-select form-select-sm mt-1"
                  :disabled="loadingTutorPrompts"
                  @change="updateDefaultTutorPrompt"
                >
                  <option value="">Aucun (utilise le défaut organisation)</option>
                  <option
                    v-for="p in tutorPrompts"
                    :key="p.id"
                    :value="p.id"
                  >
                    {{ p.code }} — {{ p.name }}
                  </option>
                </select>
                <p v-if="tutorPromptError" class="text-danger small mb-0">
                  {{ tutorPromptError }}
                </p>
              </div>
              <div class="border rounded p-2">
                <p class="small fw-bold mb-2">Calibration classifieur de phase (groupe)</p>
                <div class="mb-2">
                  <label class="form-label small mb-1">Preset recommandé</label>
                  <div class="d-flex gap-2">
                    <button type="button" class="btn btn-sm btn-outline-secondary" @click="applyClassifierPreset('safe')">safe</button>
                    <button type="button" class="btn btn-sm btn-outline-secondary" @click="applyClassifierPreset('balanced')">balanced</button>
                    <button type="button" class="btn btn-sm btn-outline-secondary" @click="applyClassifierPreset('aggressive')">aggressive</button>
                  </div>
                </div>
                <div class="row g-2">
                  <div class="col-12">
                    <label class="form-label small mb-1">Enabled</label>
                    <select v-model="group.phase_classifier_enabled" class="form-select form-select-sm">
                      <option :value="null">Fallback settings</option>
                      <option :value="true">true</option>
                      <option :value="false">false</option>
                    </select>
                  </div>
                  <div class="col-6">
                    <label class="form-label small mb-1">Min confidence</label>
                    <input v-model.number="group.phase_classifier_min_confidence" type="number" min="0" max="1" step="0.01" class="form-control form-control-sm" placeholder="fallback" />
                  </div>
                  <div class="col-6">
                    <label class="form-label small mb-1">Max tokens</label>
                    <input v-model.number="group.phase_classifier_max_tokens" type="number" min="1" step="1" class="form-control form-control-sm" placeholder="fallback" />
                  </div>
                  <div class="col-12">
                    <label class="form-label small mb-1">Max input chars</label>
                    <input v-model.number="group.phase_classifier_max_input_chars" type="number" min="1" step="1" class="form-control form-control-sm" placeholder="fallback" />
                  </div>
                </div>
                <button
                  type="button"
                  class="btn btn-sm btn-outline-primary mt-2"
                  :disabled="classifierSaving"
                  @click="saveClassifierConfig"
                >
                  {{ classifierSaving ? 'Enregistrement…' : 'Sauvegarder calibration groupe' }}
                </button>
                <p class="text-muted small mb-0 mt-2">
                  Cascade active: session -> groupe -> settings. Laisser un champ vide = fallback.
                </p>
                <p v-if="classifierError" class="text-danger small mb-0 mt-1">
                  {{ classifierError }}
                </p>
              </div>
              <div class="border rounded p-2 mt-3">
                <p class="small fw-bold mb-2">Calibration classifieur P0 (groupe)</p>
                <div class="mb-2">
                  <label class="form-label small mb-1">Preset recommandé</label>
                  <div class="d-flex gap-2">
                    <button type="button" class="btn btn-sm btn-outline-secondary" @click="applyP0ClassifierPreset('safe')">safe</button>
                    <button type="button" class="btn btn-sm btn-outline-secondary" @click="applyP0ClassifierPreset('balanced')">balanced</button>
                    <button type="button" class="btn btn-sm btn-outline-secondary" @click="applyP0ClassifierPreset('aggressive')">aggressive</button>
                  </div>
                </div>
                <div class="row g-2">
                  <div class="col-12">
                    <label class="form-label small mb-1">Enabled</label>
                    <select v-model="group.p0_classifier_enabled" class="form-select form-select-sm">
                      <option :value="null">Fallback settings</option>
                      <option :value="true">true</option>
                      <option :value="false">false</option>
                    </select>
                  </div>
                  <div class="col-6">
                    <label class="form-label small mb-1">Min confidence</label>
                    <input v-model.number="group.p0_classifier_min_confidence" type="number" min="0" max="1" step="0.01" class="form-control form-control-sm" placeholder="fallback" />
                  </div>
                  <div class="col-6">
                    <label class="form-label small mb-1">Max tokens</label>
                    <input v-model.number="group.p0_classifier_max_tokens" type="number" min="1" step="1" class="form-control form-control-sm" placeholder="fallback" />
                  </div>
                  <div class="col-12">
                    <label class="form-label small mb-1">Max input chars</label>
                    <input v-model.number="group.p0_classifier_max_input_chars" type="number" min="1" step="1" class="form-control form-control-sm" placeholder="fallback" />
                  </div>
                </div>
                <p class="text-muted small mb-0 mt-2">
                  Utilisé pour classifier les variables P0 sémantiques avant la décision locale.
                </p>
              </div>
              <hr class="my-3" />
              <div class="border rounded p-2 mt-3">
                <p class="small fw-bold mb-2">Bibliothèque RAG (documents d’organisation)</p>
                <p class="text-muted small mb-2">
                  Créez un document (titre + texte), indexez-le en chunks, puis liez-le à ce groupe pour
                  que Hugo puisse l’utiliser dans les tours (si le mode RAG du plan est actif).
                </p>
                <div v-if="libraryLoading" class="small text-muted">Chargement bibliothèque…</div>
                <p v-if="libraryError" class="text-danger small mb-1">{{ libraryError }}</p>
                <p v-if="libraryMsg" class="text-success small mb-1">{{ libraryMsg }}</p>
                <div class="mb-3">
                  <label class="form-label small mb-1">Nouveau document</label>
                  <input
                    v-model="newDocTitle"
                    type="text"
                    class="form-control form-control-sm mb-1"
                    placeholder="Titre"
                    maxlength="512"
                  />
                  <textarea
                    v-model="newDocSourceText"
                    class="form-control form-control-sm mb-1"
                    rows="4"
                    placeholder="Coller le contenu (markdown ou texte brut)…"
                  />
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-primary"
                    :disabled="libraryActionLoading || !newDocTitle.trim()"
                    @click="createOrgDocument"
                  >
                    Créer le document
                  </button>
                </div>
                <div v-if="orgDocuments.length" class="table-responsive mb-2">
                  <table class="table table-sm table-bordered align-middle small mb-0">
                    <thead>
                      <tr>
                        <th>Titre</th>
                        <th>Texte</th>
                        <th>Chunks</th>
                        <th>Qualité</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="d in orgDocuments" :key="d.id">
                        <td>{{ d.title }}</td>
                        <td>{{ d.has_source_text ? 'oui' : 'non' }}</td>
                        <td>{{ d.chunks_count ?? 0 }}</td>
                        <td>{{ d.quality_flag }}</td>
                        <td class="text-nowrap">
                          <button
                            type="button"
                            class="btn btn-sm btn-outline-secondary me-1"
                            :disabled="!!indexingDocumentId || libraryActionLoading"
                            @click="indexDocument(d.id)"
                          >
                            {{ indexingDocumentId === d.id ? '…' : 'Indexer' }}
                          </button>
                          <button
                            v-if="!isDocLinkedToGroup(d.id)"
                            type="button"
                            class="btn btn-sm btn-outline-success"
                            :disabled="libraryActionLoading"
                            @click="linkDocumentToGroup(d.id)"
                          >
                            Lier au groupe
                          </button>
                          <span v-else class="badge bg-success">Lié</span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p v-else-if="!libraryLoading" class="text-muted small mb-0">Aucun document dans l’organisation.</p>
                <p class="small fw-bold mb-1 mt-3">Documents liés à ce groupe</p>
                <ul v-if="groupLibraryItems.filter((x) => x.status === 'ACTIVE').length" class="list-group list-group-flush small">
                  <li
                    v-for="item in groupLibraryItems.filter((x) => x.status === 'ACTIVE')"
                    :key="item.id"
                    class="list-group-item px-0 d-flex justify-content-between align-items-start"
                  >
                    <div>
                      <strong>{{ item.document_title }}</strong>
                      <span class="text-muted ms-1">({{ item.chunks_count }} chunks, {{ item.quality_flag }})</span>
                    </div>
                    <button
                      type="button"
                      class="btn btn-sm btn-outline-warning"
                      :disabled="libraryActionLoading"
                      @click="deactivateGroupDocument(item.id)"
                    >
                      Retirer
                    </button>
                  </li>
                </ul>
                <p v-else class="text-muted small mb-0">Aucune liaison active pour ce groupe.</p>
              </div>
              <p class="text-muted small mb-0">
                Les membres ci-contre sont liés via les adhésions de groupe (GroupMembership).
              </p>
              
            </template>
          </div>
        </div>
      </div>

      <div class="col-12 col-lg-8 mb-4">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h2 class="h5 mb-3">Utilisateurs associés</h2>

            <div v-if="membersError || usersError" class="alert alert-danger" role="alert">
              {{ membersError || usersError }}
            </div>

            <div v-if="loadingMembers || loadingUsers" class="text-center py-3">
              <div class="spinner-border spinner-border-sm text-primary" role="status">
                <span class="visually-hidden">Chargement…</span>
              </div>
            </div>

            <ul v-else-if="members.length" class="list-group list-group-flush">
              <li
                v-for="m in members"
                :key="m.id"
                class="list-group-item d-flex justify-content-between align-items-center"
              >
                <div>
                  <router-link
                    v-if="memberUser(m)"
                    :to="{ name: 'UserDetail', params: { userId: memberUser(m).id } }"
                  >
                    {{ memberUser(m).username || memberUser(m).email }}
                  </router-link>
                  <span v-else>
                    {{ m.user }}
                  </span>
                  <span
                    v-if="memberUser(m)?.email && memberUser(m)?.username"
                    class="text-muted small"
                  >
                    ({{ memberUser(m).email }})
                  </span>
                </div>
                <span
                  v-if="memberUser(m)"
                  class="badge bg-light text-muted text-uppercase"
                >
                  {{ memberUser(m).role }}
                </span>
              </li>
            </ul>
            <p v-else class="text-muted small mb-0">
              Aucun utilisateur associé à ce groupe pour le moment.
            </p>
            <hr class="my-3" />
            <h3 class="h6 mb-2">Associations tuteur/apprenant</h3>
            <div v-if="tutorLinksError" class="alert alert-danger py-2" role="alert">
              {{ tutorLinksError }}
            </div>
            <div v-if="tutorLinksSuccess" class="alert alert-success py-2" role="alert">
              {{ tutorLinksSuccess }}
            </div>
            <div class="row g-2 align-items-end mb-3">
              <div class="col-12 col-md-5">
                <label for="tutor-select" class="form-label small mb-1">Tuteur</label>
                <select
                  id="tutor-select"
                  v-model="selectedTutorId"
                  class="form-select form-select-sm"
                  :disabled="loadingMembers || loadingUsers || linkingTutorLearner"
                >
                  <option value="">Sélectionner un tuteur…</option>
                  <option
                    v-for="m in tutorMembers()"
                    :key="m.id"
                    :value="m.user"
                  >
                    {{ displayName(memberUser(m)) }}
                  </option>
                </select>
              </div>
              <div class="col-12 col-md-5">
                <label for="learner-select" class="form-label small mb-1">Apprenant</label>
                <select
                  id="learner-select"
                  v-model="selectedLearnerId"
                  class="form-select form-select-sm"
                  :disabled="loadingMembers || loadingUsers || linkingTutorLearner"
                >
                  <option value="">Sélectionner un apprenant…</option>
                  <option
                    v-for="m in learnerMembers()"
                    :key="m.id"
                    :value="m.user"
                  >
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
                  {{ linkingTutorLearner ? 'Association…' : 'Associer' }}
                </button>
              </div>
            </div>
            <div v-if="loadingTutorLinks" class="text-center py-2">
              <div class="spinner-border spinner-border-sm text-primary" role="status">
                <span class="visually-hidden">Chargement…</span>
              </div>
            </div>
            <ul v-else-if="tutorLinks.length" class="list-group list-group-flush">
              <li
                v-for="link in tutorLinks"
                :key="link.id"
                class="list-group-item d-flex justify-content-between align-items-center px-0"
              >
                <div class="small">
                  <strong>{{ displayName(userById(link.tutor)) }}</strong>
                  <span class="text-muted"> accompagne </span>
                  <strong>{{ displayName(userById(link.learner)) }}</strong>
                  <span class="badge bg-light text-muted border ms-2">
                    {{ group?.name || 'Groupe' }}
                  </span>
                </div>
              </li>
            </ul>
            <p v-else class="text-muted small mb-0">
              Aucune association tuteur/apprenant pour ce groupe.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

