<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/client'

const prompts = ref([])
const ovhLlms = ref([])
const loading = ref(false)
const error = ref('')

const code = ref('')
const name = ref('')
const description = ref('')
const systemTemplate = ref('')
const userTemplate = ref('')
const promptType = ref('AFEST_HUGO')
const language = ref('fr')
const tone = ref('COACHING')
const sotProfile = ref('')
const conversationProfile = ref('reflective_afest')
const outputFormatMode = ref('multi_question_numbered')
const defaultSessionPhase = ref('exploration')
const maxQuestionsPerTurn = ref(2)
const maxTokens = ref(150)
const allowLists = ref(false)
const isDefault = ref(false)
const isActive = ref(true)
const ovhLlmId = ref('')
const metadataText = ref('{}')
const saving = ref(false)
const createAdvancedOpen = ref(false)

const expandedPromptId = ref('')
const editingId = ref('')
const editingCode = ref('')
const editingName = ref('')
const editingDescription = ref('')
const editingSystemTemplate = ref('')
const editingUserTemplate = ref('')
const editingPromptType = ref('AFEST_HUGO')
const editingLanguage = ref('fr')
const editingTone = ref('COACHING')
const editingSotProfile = ref('')
const editingConversationProfile = ref('reflective_afest')
const editingOutputFormatMode = ref('multi_question_numbered')
const editingDefaultSessionPhase = ref('exploration')
const editingMaxQuestionsPerTurn = ref(2)
const editingMaxTokens = ref(150)
const editingAllowLists = ref(false)
const editingIsDefault = ref(false)
const editingIsActive = ref(true)
const editingOvhLlmId = ref('')
const editingMetadataText = ref('{}')
const editingSaving = ref(false)
const editingAdvancedOpen = ref(false)

const basePath = '/hugo/tutor-prompts/'

async function loadPrompts() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get(basePath)
    prompts.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors du chargement des TutorPrompt.'
    prompts.value = []
  } finally {
    loading.value = false
  }
}

async function loadOvhLlms() {
  try {
    const { data } = await api.get('/hugo/ovh-llms/')
    ovhLlms.value = Array.isArray(data) ? data : (data.results || [])
  } catch {
    ovhLlms.value = []
  }
}

function parseMetadataOrThrow(text) {
  const clean = String(text || '').trim()
  if (!clean) return {}
  const parsed = JSON.parse(clean)
  if (parsed === null || Array.isArray(parsed) || typeof parsed !== 'object') {
    throw new Error('metadata doit être un objet JSON.')
  }
  return parsed
}

function resetCreateForm() {
  code.value = ''
  name.value = ''
  description.value = ''
  systemTemplate.value = ''
  userTemplate.value = ''
  promptType.value = 'AFEST_HUGO'
  language.value = 'fr'
  tone.value = 'COACHING'
  sotProfile.value = ''
  conversationProfile.value = 'reflective_afest'
  outputFormatMode.value = 'multi_question_numbered'
  defaultSessionPhase.value = 'exploration'
  maxQuestionsPerTurn.value = 2
  maxTokens.value = 150
  allowLists.value = false
  isDefault.value = false
  isActive.value = true
  ovhLlmId.value = ''
  metadataText.value = '{}'
  createAdvancedOpen.value = false
}

async function createPrompt() {
  if (!code.value || !name.value || !systemTemplate.value || !userTemplate.value || saving.value) return
  saving.value = true
  error.value = ''
  try {
    const metadata = parseMetadataOrThrow(metadataText.value)
    await api.post(basePath, {
      code: code.value,
      name: name.value,
      description: description.value,
      system_template: systemTemplate.value,
      user_template: userTemplate.value,
      prompt_type: promptType.value,
      language: language.value,
      tone: tone.value,
      sot_profile: sotProfile.value || '',
      conversation_profile: conversationProfile.value,
      output_format_mode: outputFormatMode.value,
      default_session_phase: defaultSessionPhase.value,
      max_questions_per_turn: Number(maxQuestionsPerTurn.value) || 2,
      max_tokens: Number(maxTokens.value) || 150,
      allow_lists: !!allowLists.value,
      is_default: !!isDefault.value,
      is_active: !!isActive.value,
      ovh_llm_id: ovhLlmId.value || null,
      metadata,
    })
    resetCreateForm()
    await loadPrompts()
  } catch (e) {
    error.value = e.response?.data?.detail || e.message || 'Erreur lors de la création du TutorPrompt.'
  } finally {
    saving.value = false
  }
}

function togglePromptDetails(id) {
  expandedPromptId.value = expandedPromptId.value === id ? '' : id
}

function startEdit(p) {
  expandedPromptId.value = p.id
  editingId.value = p.id
  editingCode.value = p.code
  editingName.value = p.name
  editingDescription.value = p.description || ''
  editingSystemTemplate.value = p.system_template || ''
  editingUserTemplate.value = p.user_template || ''
  editingPromptType.value = p.prompt_type || 'AFEST_HUGO'
  editingLanguage.value = p.language || 'fr'
  editingTone.value = p.tone || 'COACHING'
  editingSotProfile.value = p.sot_profile || ''
  editingConversationProfile.value = p.conversation_profile || 'reflective_afest'
  editingOutputFormatMode.value = p.output_format_mode || 'multi_question_numbered'
  editingDefaultSessionPhase.value = p.default_session_phase || 'exploration'
  editingMaxQuestionsPerTurn.value = Number(p.max_questions_per_turn || 2)
  editingMaxTokens.value = Number(p.max_tokens || 150)
  editingAllowLists.value = !!p.allow_lists
  editingIsDefault.value = !!p.is_default
  editingIsActive.value = !!p.is_active
  editingOvhLlmId.value = p.ovh_llm?.id || ''
  editingMetadataText.value = JSON.stringify(p.metadata || {}, null, 2)
  editingAdvancedOpen.value = false
}

function cancelEdit() {
  editingId.value = ''
  editingCode.value = ''
  editingName.value = ''
  editingDescription.value = ''
  editingSystemTemplate.value = ''
  editingUserTemplate.value = ''
  editingPromptType.value = 'AFEST_HUGO'
  editingLanguage.value = 'fr'
  editingTone.value = 'COACHING'
  editingSotProfile.value = ''
  editingConversationProfile.value = 'reflective_afest'
  editingOutputFormatMode.value = 'multi_question_numbered'
  editingDefaultSessionPhase.value = 'exploration'
  editingMaxQuestionsPerTurn.value = 2
  editingMaxTokens.value = 150
  editingAllowLists.value = false
  editingIsDefault.value = false
  editingIsActive.value = true
  editingOvhLlmId.value = ''
  editingMetadataText.value = '{}'
  editingAdvancedOpen.value = false
}

async function saveEdit() {
  if (!editingId.value || !editingCode.value || !editingName.value || !editingSystemTemplate.value || !editingUserTemplate.value || editingSaving.value) return
  editingSaving.value = true
  error.value = ''
  try {
    const metadata = parseMetadataOrThrow(editingMetadataText.value)
    await api.patch(`${basePath}${editingId.value}/`, {
      code: editingCode.value,
      name: editingName.value,
      description: editingDescription.value,
      system_template: editingSystemTemplate.value,
      user_template: editingUserTemplate.value,
      prompt_type: editingPromptType.value,
      language: editingLanguage.value,
      tone: editingTone.value,
      sot_profile: editingSotProfile.value || '',
      conversation_profile: editingConversationProfile.value,
      output_format_mode: editingOutputFormatMode.value,
      default_session_phase: editingDefaultSessionPhase.value,
      max_questions_per_turn: Number(editingMaxQuestionsPerTurn.value) || 2,
      max_tokens: Number(editingMaxTokens.value) || 150,
      allow_lists: !!editingAllowLists.value,
      is_default: !!editingIsDefault.value,
      is_active: !!editingIsActive.value,
      ovh_llm_id: editingOvhLlmId.value || null,
      metadata,
    })
    await loadPrompts()
    cancelEdit()
  } catch (e) {
    error.value = e.response?.data?.detail || e.message || 'Erreur lors de la mise à jour du TutorPrompt.'
  } finally {
    editingSaving.value = false
  }
}

async function deletePrompt(id) {
  if (!id) return
  error.value = ''
  try {
    await api.delete(`${basePath}${id}/`)
    prompts.value = prompts.value.filter((p) => p.id !== id)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors de la suppression du TutorPrompt.'
  }
}

onMounted(() => {
  loadPrompts()
  loadOvhLlms()
})
</script>

<template>
  <div class="container-fluid">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item">
          <router-link to="/dashboard">Tableau de bord</router-link>
        </li>
        <li class="breadcrumb-item active" aria-current="page">Prompts tuteur</li>
      </ol>
    </nav>

    <h1 class="h4 mb-4">TutorPrompt (CRUD)</h1>
    <p class="text-muted mb-4">
      Gestion des messages système / consignes utilisés pour le tuteur virtuel.
    </p>

    <div class="row mb-4">
      <div class="col-12 col-lg-8">
        <div class="card shadow-sm">
          <div class="card-body">
            <h2 class="h5 mb-3">Nouveau TutorPrompt</h2>

            <div class="mb-3">
              <label for="prompt-code" class="form-label">Code</label>
              <input id="prompt-code" v-model="code" type="text" class="form-control" :disabled="saving" autocomplete="off" />
            </div>

            <div class="mb-3">
              <label for="prompt-name" class="form-label">Nom</label>
              <input id="prompt-name" v-model="name" type="text" class="form-control" :disabled="saving" autocomplete="off" />
            </div>

            <div class="mb-3">
              <label for="prompt-description" class="form-label">Description (optionnelle)</label>
              <textarea id="prompt-description" v-model="description" class="form-control" rows="2" :disabled="saving" />
            </div>

            <div class="mb-3">
              <label for="prompt-system" class="form-label">Template système</label>
              <textarea id="prompt-system" v-model="systemTemplate" class="form-control" rows="5" :disabled="saving" />
            </div>

            <div class="mb-3">
              <label for="prompt-user" class="form-label">Template utilisateur</label>
              <textarea id="prompt-user" v-model="userTemplate" class="form-control" rows="5" :disabled="saving" />
            </div>

            <div class="row g-2 mb-3">
              <div class="col-12 col-md-4">
                <label for="prompt-type" class="form-label">Prompt type</label>
                <select id="prompt-type" v-model="promptType" class="form-select" :disabled="saving">
                  <option value="AFEST_HUGO">AFEST_HUGO</option>
                </select>
              </div>
              <div class="col-12 col-md-4">
                <label for="prompt-language" class="form-label">Langue</label>
                <select id="prompt-language" v-model="language" class="form-select" :disabled="saving">
                  <option value="fr">fr</option>
                  <option value="en">en</option>
                </select>
              </div>
              <div class="col-12 col-md-4">
                <label for="prompt-tone" class="form-label">Ton</label>
                <select id="prompt-tone" v-model="tone" class="form-select" :disabled="saving">
                  <option value="COACHING">COACHING</option>
                  <option value="NEUTRAL">NEUTRAL</option>
                  <option value="FRIENDLY">FRIENDLY</option>
                </select>
              </div>
            </div>

            <div class="mb-3">
              <button
                type="button"
                class="btn btn-sm btn-outline-secondary"
                :disabled="saving"
                @click="createAdvancedOpen = !createAdvancedOpen"
              >
                {{ createAdvancedOpen ? 'Masquer options avancées' : 'Afficher options avancées' }}
              </button>
            </div>

            <div v-if="createAdvancedOpen" class="row g-2 mb-3">
              <div class="col-12 col-md-6">
                <label for="prompt-sot-profile" class="form-label">sot_profile</label>
                <input id="prompt-sot-profile" v-model="sotProfile" type="text" class="form-control" :disabled="saving" />
              </div>
              <div class="col-12 col-md-6">
                <label for="prompt-conversation-profile" class="form-label">Posture conversationnelle</label>
                <select id="prompt-conversation-profile" v-model="conversationProfile" class="form-select" :disabled="saving">
                  <option value="reflective_afest">reflective_afest</option>
                  <option value="diagnostic">diagnostic</option>
                  <option value="knowledge_review">knowledge_review</option>
                </select>
              </div>
              <div class="col-12 col-md-6">
                <label for="prompt-ovh-llm" class="form-label">OVH LLM</label>
                <select id="prompt-ovh-llm" v-model="ovhLlmId" class="form-select" :disabled="saving">
                  <option value="">Aucun</option>
                  <option v-for="llm in ovhLlms" :key="llm.id" :value="llm.id">
                    {{ llm.name }} ({{ llm.code }})
                  </option>
                </select>
              </div>
            </div>

            <div class="row g-2 mb-3">
              <div class="col-12 col-md-4">
                <label for="prompt-output-mode" class="form-label">Format de sortie</label>
                <select id="prompt-output-mode" v-model="outputFormatMode" class="form-select" :disabled="saving">
                  <option value="single_question">single_question</option>
                  <option value="multi_question_numbered">multi_question_numbered</option>
                  <option value="reflection_block">reflection_block</option>
                </select>
              </div>
              <div class="col-12 col-md-4">
                <label for="prompt-phase" class="form-label">Phase par défaut</label>
                <select id="prompt-phase" v-model="defaultSessionPhase" class="form-select" :disabled="saving">
                  <option value="">(auto)</option>
                  <option value="opening">opening</option>
                  <option value="exploration">exploration</option>
                  <option value="deepening">deepening</option>
                  <option value="potential_closure">potential_closure</option>
                </select>
              </div>
              <div class="col-6 col-md-2">
                <label for="prompt-max-q" class="form-label">Max questions</label>
                <input id="prompt-max-q" v-model.number="maxQuestionsPerTurn" type="number" min="1" max="3" class="form-control" :disabled="saving" />
              </div>
              <div class="col-6 col-md-2">
                <label for="prompt-max-tokens" class="form-label">Max tokens</label>
                <input id="prompt-max-tokens" v-model.number="maxTokens" type="number" min="64" class="form-control" :disabled="saving" />
              </div>
            </div>

            <div class="row g-2 mb-3">
              <div class="col-12 col-md-4">
                <div class="form-check">
                  <input id="prompt-allow-lists" v-model="allowLists" class="form-check-input" type="checkbox" :disabled="saving" />
                  <label class="form-check-label" for="prompt-allow-lists">allow_lists</label>
                </div>
              </div>
              <div class="col-12 col-md-4">
                <div class="form-check">
                  <input id="prompt-is-default" v-model="isDefault" class="form-check-input" type="checkbox" :disabled="saving" />
                  <label class="form-check-label" for="prompt-is-default">is_default</label>
                </div>
              </div>
              <div class="col-12 col-md-4">
                <div class="form-check">
                  <input id="prompt-is-active" v-model="isActive" class="form-check-input" type="checkbox" :disabled="saving" />
                  <label class="form-check-label" for="prompt-is-active">is_active</label>
                </div>
              </div>
            </div>

            <div v-if="createAdvancedOpen" class="mb-3">
              <label for="prompt-metadata" class="form-label">metadata (JSON object)</label>
              <textarea id="prompt-metadata" v-model="metadataText" class="form-control" rows="4" :disabled="saving" />
            </div>

            <button type="button" class="btn btn-primary" :disabled="saving || !code || !name || !systemTemplate || !userTemplate" @click="createPrompt">
              <span v-if="saving" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
              Créer le TutorPrompt
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm">
      <div class="card-body">
        <h2 class="h5 mb-3">Liste des TutorPrompt</h2>

        <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>

        <div v-if="loading" class="text-center py-3">
          <div class="spinner-border spinner-border-sm text-primary" role="status">
            <span class="visually-hidden">Chargement…</span>
          </div>
        </div>

        <ul v-else-if="prompts.length" class="list-group list-group-flush">
          <li v-for="p in prompts" :key="p.id" class="list-group-item">
            <div class="d-flex justify-content-between align-items-start gap-3">
              <div class="flex-grow-1">
                <template v-if="editingId === p.id">
                  <div class="mb-2 d-flex gap-2">
                    <input v-model="editingCode" type="text" class="form-control form-control-sm" placeholder="Code" :disabled="editingSaving" />
                    <input v-model="editingName" type="text" class="form-control form-control-sm" placeholder="Nom" :disabled="editingSaving" />
                  </div>
                  <textarea v-model="editingDescription" class="form-control form-control-sm mb-2" rows="2" placeholder="Description (optionnelle)" :disabled="editingSaving" />
                  <textarea v-model="editingSystemTemplate" class="form-control form-control-sm mb-2" rows="3" placeholder="Template système" :disabled="editingSaving" />
                  <textarea v-model="editingUserTemplate" class="form-control form-control-sm mb-2" rows="3" placeholder="Template utilisateur" :disabled="editingSaving" />

                  <div class="row g-2">
                    <div class="col-12 col-md-4">
                      <label class="form-label small mb-1">Prompt type</label>
                      <select v-model="editingPromptType" class="form-select form-select-sm" :disabled="editingSaving">
                        <option value="AFEST_HUGO">AFEST_HUGO</option>
                      </select>
                    </div>
                    <div class="col-12 col-md-4">
                      <label class="form-label small mb-1">Langue</label>
                      <select v-model="editingLanguage" class="form-select form-select-sm" :disabled="editingSaving">
                        <option value="fr">fr</option>
                        <option value="en">en</option>
                      </select>
                    </div>
                    <div class="col-12 col-md-4">
                      <label class="form-label small mb-1">Ton</label>
                      <select v-model="editingTone" class="form-select form-select-sm" :disabled="editingSaving">
                        <option value="COACHING">COACHING</option>
                        <option value="NEUTRAL">NEUTRAL</option>
                        <option value="FRIENDLY">FRIENDLY</option>
                      </select>
                    </div>
                  </div>

                  <div class="mt-2">
                    <button
                      type="button"
                      class="btn btn-sm btn-outline-secondary"
                      :disabled="editingSaving"
                      @click="editingAdvancedOpen = !editingAdvancedOpen"
                    >
                      {{ editingAdvancedOpen ? 'Masquer options avancées' : 'Afficher options avancées' }}
                    </button>
                  </div>

                  <div v-if="editingAdvancedOpen" class="row g-2 mt-2">
                    <div class="col-12 col-md-6">
                      <label class="form-label small mb-1">sot_profile</label>
                      <input v-model="editingSotProfile" type="text" class="form-control form-control-sm" :disabled="editingSaving" />
                    </div>
                    <div class="col-12 col-md-6">
                      <label class="form-label small mb-1">Posture conversationnelle</label>
                      <select v-model="editingConversationProfile" class="form-select form-select-sm" :disabled="editingSaving">
                        <option value="reflective_afest">reflective_afest</option>
                        <option value="diagnostic">diagnostic</option>
                        <option value="knowledge_review">knowledge_review</option>
                      </select>
                    </div>
                    <div class="col-12 col-md-6">
                      <label class="form-label small mb-1">OVH LLM</label>
                      <select v-model="editingOvhLlmId" class="form-select form-select-sm" :disabled="editingSaving">
                        <option value="">Aucun</option>
                        <option v-for="llm in ovhLlms" :key="llm.id" :value="llm.id">
                          {{ llm.name }} ({{ llm.code }})
                        </option>
                      </select>
                    </div>
                  </div>

                  <div class="row g-2 mt-2">
                    <div class="col-12 col-md-4">
                      <label class="form-label small mb-1">Format de sortie</label>
                      <select v-model="editingOutputFormatMode" class="form-select form-select-sm" :disabled="editingSaving">
                        <option value="single_question">single_question</option>
                        <option value="multi_question_numbered">multi_question_numbered</option>
                        <option value="reflection_block">reflection_block</option>
                      </select>
                    </div>
                    <div class="col-12 col-md-4">
                      <label class="form-label small mb-1">Phase par défaut</label>
                      <select v-model="editingDefaultSessionPhase" class="form-select form-select-sm" :disabled="editingSaving">
                        <option value="">(auto)</option>
                        <option value="opening">opening</option>
                        <option value="exploration">exploration</option>
                        <option value="deepening">deepening</option>
                        <option value="potential_closure">potential_closure</option>
                      </select>
                    </div>
                    <div class="col-6 col-md-2">
                      <label class="form-label small mb-1">Max questions</label>
                      <input v-model.number="editingMaxQuestionsPerTurn" type="number" min="1" max="3" class="form-control form-control-sm" :disabled="editingSaving" />
                    </div>
                    <div class="col-6 col-md-2">
                      <label class="form-label small mb-1">Max tokens</label>
                      <input v-model.number="editingMaxTokens" type="number" min="64" class="form-control form-control-sm" :disabled="editingSaving" />
                    </div>
                  </div>

                  <div class="row g-2 mt-2">
                    <div class="col-12 col-md-4">
                      <div class="form-check">
                        <input :id="`allow-lists-${p.id}`" v-model="editingAllowLists" class="form-check-input" type="checkbox" :disabled="editingSaving" />
                        <label class="form-check-label small" :for="`allow-lists-${p.id}`">allow_lists</label>
                      </div>
                    </div>
                    <div class="col-12 col-md-4">
                      <div class="form-check">
                        <input :id="`is-default-${p.id}`" v-model="editingIsDefault" class="form-check-input" type="checkbox" :disabled="editingSaving" />
                        <label class="form-check-label small" :for="`is-default-${p.id}`">is_default</label>
                      </div>
                    </div>
                    <div class="col-12 col-md-4">
                      <div class="form-check">
                        <input :id="`is-active-${p.id}`" v-model="editingIsActive" class="form-check-input" type="checkbox" :disabled="editingSaving" />
                        <label class="form-check-label small" :for="`is-active-${p.id}`">is_active</label>
                      </div>
                    </div>
                  </div>

                  <div v-if="editingAdvancedOpen" class="mt-2">
                    <label class="form-label small mb-1">metadata (JSON object)</label>
                    <textarea v-model="editingMetadataText" class="form-control form-control-sm" rows="4" :disabled="editingSaving" />
                  </div>
                </template>

                <template v-else>
                  <h3 class="h6 mb-1">{{ p.name }}</h3>
                  <p v-if="p.description" class="small text-muted mb-2">{{ p.description }}</p>
                  <p v-else class="small text-muted mb-2">Sans description</p>

                  <div v-if="expandedPromptId === p.id" class="mt-2">
                    <p class="small mb-1"><strong>Code:</strong> {{ p.code }}</p>
                    <p class="small mb-1"><strong>Type:</strong> {{ p.prompt_type }}</p>
                    <p class="small mb-1"><strong>Langue:</strong> {{ p.language }}</p>
                    <p class="small mb-1"><strong>Ton:</strong> {{ p.tone }}</p>
                    <p class="small mb-1"><strong>sot_profile:</strong> {{ p.sot_profile || '—' }}</p>
                    <p class="small mb-1"><strong>posture:</strong> {{ p.conversation_profile || 'reflective_afest' }}</p>
                    <p class="small mb-1"><strong>is_default:</strong> {{ !!p.is_default }}</p>
                    <p class="small mb-1"><strong>is_active:</strong> {{ !!p.is_active }}</p>
                    <p class="small mb-1"><strong>OVH LLM:</strong> {{ p.ovh_llm?.name || 'Aucun' }}</p>
                    <pre class="small bg-light p-2 rounded mb-1" style="white-space: pre-wrap">{{ p.system_template }}</pre>
                    <pre class="small bg-light p-2 rounded mb-1" style="white-space: pre-wrap">{{ p.user_template }}</pre>
                    <p class="small text-muted mt-2 mb-1">
                      format={{ p.output_format_mode }} | phase={{ p.default_session_phase || 'auto' }} |
                      maxQ={{ p.max_questions_per_turn }} | maxTokens={{ p.max_tokens }} | allowLists={{ !!p.allow_lists }}
                    </p>
                    <pre class="small bg-light p-2 rounded mb-0" style="white-space: pre-wrap">{{ JSON.stringify(p.metadata || {}, null, 2) }}</pre>
                  </div>
                </template>
              </div>

              <div class="d-flex flex-column gap-2">
                <template v-if="editingId === p.id">
                  <button
                    type="button"
                    class="btn btn-sm btn-primary"
                    :disabled="editingSaving || !editingCode || !editingName || !editingSystemTemplate || !editingUserTemplate"
                    @click="saveEdit"
                  >
                    <span v-if="editingSaving" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true" />
                    Enregistrer
                  </button>
                  <button type="button" class="btn btn-sm btn-outline-secondary" :disabled="editingSaving" @click="cancelEdit">Annuler</button>
                </template>
                <template v-else>
                  <button type="button" class="btn btn-sm btn-outline-primary" @click="togglePromptDetails(p.id)">
                    {{ expandedPromptId === p.id ? 'Masquer' : 'Voir' }}
                  </button>
                  <button type="button" class="btn btn-sm btn-outline-secondary" @click="startEdit(p)">Modifier</button>
                  <button type="button" class="btn btn-sm btn-outline-danger" @click="deletePrompt(p.id)">Supprimer</button>
                </template>
              </div>
            </div>
          </li>
        </ul>

        <p v-else class="text-muted small mb-0">Aucun TutorPrompt défini pour le moment.</p>
      </div>
    </div>
  </div>
</template>

