<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../api/client'
import { LEARNER_POSTURES } from '../../constants/conversationPostures'

const route = useRoute()
const router = useRouter()

const profiles = ref([])
const tutorPrompts = ref([])
const conductProfiles = ref([])
const evaluationProfiles = ref([])
const evaluationPolicies = ref([])
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')

const selectedId = ref('')
const form = ref({
  name: '',
  description: '',
  status: 'active',
  is_default: false,
  diagnostic_tutor_prompt_id: '',
  reflective_tutor_prompt_id: '',
  knowledge_review_tutor_prompt_id: '',
  diagnostic_conduct_profile_id: '',
  reflective_conduct_profile_id: '',
  knowledge_review_conduct_profile_id: '',
  evaluation_prompt_profile_id: '',
  evaluation_policy_id: '',
})

const isEditing = computed(() => Boolean(route.params.profileId))
const isCreate = computed(() => route.params.profileId === 'new')
const postureSlots = computed(() =>
  LEARNER_POSTURES.map((p) => ({
    code: p.code,
    label: p.code === 'knowledge_review' ? 'Bûchage' : p.label,
    promptField: `${p.code === 'diagnostic' ? 'diagnostic' : p.code === 'reflective_afest' ? 'reflective' : 'knowledge_review'}_tutor_prompt_id`,
    conductField: `${p.code === 'diagnostic' ? 'diagnostic' : p.code === 'reflective_afest' ? 'reflective' : 'knowledge_review'}_conduct_profile_id`,
  }))
)

function promptsForPosture(code) {
  return tutorPrompts.value.filter((p) => (p.conversation_profile || 'reflective_afest') === code)
}

function conductForPosture(code) {
  return conductProfiles.value.filter((p) => p.posture === code && p.organisation)
}

function resetForm() {
  form.value = {
    name: '',
    description: '',
    status: 'active',
    is_default: false,
    diagnostic_tutor_prompt_id: '',
    reflective_tutor_prompt_id: '',
    knowledge_review_tutor_prompt_id: '',
    diagnostic_conduct_profile_id: '',
    reflective_conduct_profile_id: '',
    knowledge_review_conduct_profile_id: '',
    evaluation_prompt_profile_id: '',
    evaluation_policy_id: '',
  }
}

function syncFormFromProfile(profile) {
  if (!profile) {
    resetForm()
    return
  }
  form.value = {
    name: profile.name || '',
    description: profile.description || '',
    status: profile.status || 'active',
    is_default: !!profile.is_default,
    diagnostic_tutor_prompt_id: profile.diagnostic_tutor_prompt || '',
    reflective_tutor_prompt_id: profile.reflective_tutor_prompt || '',
    knowledge_review_tutor_prompt_id: profile.knowledge_review_tutor_prompt || '',
    diagnostic_conduct_profile_id: profile.diagnostic_conduct_profile || '',
    reflective_conduct_profile_id: profile.reflective_conduct_profile || '',
    knowledge_review_conduct_profile_id: profile.knowledge_review_conduct_profile || '',
    evaluation_prompt_profile_id: profile.evaluation_prompt_profile || '',
    evaluation_policy_id: profile.evaluation_policy || '',
  }
}

async function loadReferenceData() {
  const [promptsRes, conductRes, evalProfRes, evalPolRes] = await Promise.all([
    api.get('/hugo/tutor-prompts/'),
    api.get('/hugo/conduct-profiles/'),
    api.get('/hugo/evaluation-prompt-profiles/'),
    api.get('/hugo/evaluation-policies/'),
  ])
  tutorPrompts.value = Array.isArray(promptsRes.data) ? promptsRes.data : (promptsRes.data.results || [])
  conductProfiles.value = Array.isArray(conductRes.data) ? conductRes.data : (conductRes.data.results || [])
  evaluationProfiles.value = Array.isArray(evalProfRes.data) ? evalProfRes.data : (evalProfRes.data.results || [])
  evaluationPolicies.value = Array.isArray(evalPolRes.data)
    ? evalPolRes.data.filter((p) => !p.group)
    : (evalPolRes.data.results || []).filter((p) => !p.group)
}

async function loadProfiles() {
  loading.value = true
  error.value = ''
  try {
    await loadReferenceData()
    const { data } = await api.get('/hugo/learner-conversation-profiles/')
    profiles.value = Array.isArray(data) ? data : (data.results || [])
    if (isEditing.value && !isCreate.value) {
      selectedId.value = String(route.params.profileId)
      const profile = profiles.value.find((p) => String(p.id) === selectedId.value)
      if (!profile) {
        const detail = await api.get(`/hugo/learner-conversation-profiles/${selectedId.value}/`)
        syncFormFromProfile(detail.data)
      } else {
        syncFormFromProfile(profile)
      }
    } else if (isCreate.value) {
      selectedId.value = ''
      resetForm()
    }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors du chargement.'
  } finally {
    loading.value = false
  }
}

function buildPayload() {
  const payload = { ...form.value }
  for (const key of Object.keys(payload)) {
    if (key.endsWith('_id') && payload[key] === '') {
      payload[key] = null
    }
  }
  return payload
}

async function saveProfile() {
  if (!form.value.name || saving.value) return
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    const payload = buildPayload()
    if (selectedId.value) {
      await api.patch(`/hugo/learner-conversation-profiles/${selectedId.value}/`, payload)
      success.value = 'Profil mis à jour.'
    } else {
      const { data } = await api.post('/hugo/learner-conversation-profiles/', payload)
      selectedId.value = data.id
      router.replace(`/admin/conversation/learner/profiles/${data.id}`)
      success.value = 'Profil créé.'
    }
    await loadProfiles()
  } catch (e) {
    const data = e.response?.data
    error.value = data?.detail || data?.name?.[0] || e.message || 'Erreur lors de la sauvegarde.'
  } finally {
    saving.value = false
  }
}

function openCreate() {
  selectedId.value = ''
  resetForm()
  router.push('/admin/conversation/learner/profiles/new')
}

function openProfile(id) {
  router.push(`/admin/conversation/learner/profiles/${id}`)
}

onMounted(loadProfiles)
</script>

<template>
  <div class="container-fluid">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item"><router-link to="/dashboard">Tableau de bord</router-link></li>
        <li class="breadcrumb-item"><router-link to="/admin/conversation">Configuration conversation</router-link></li>
        <li class="breadcrumb-item active" aria-current="page">Profils conversationnels apprenant</li>
      </ol>
    </nav>

    <header class="mb-4">
      <h1 class="h4 mb-1">Profils conversationnels apprenant</h1>
      <p class="text-muted mb-0">
        Regroupe diag, réflexif, bûchage et évaluation finale sous un nom de profil global.
        Les écrans par posture restent disponibles en mode legacy.
      </p>
    </header>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>

    <div class="row g-4">
      <div class="col-12 col-lg-4">
        <div class="card shadow-sm">
          <div class="card-header d-flex justify-content-between align-items-center">
            <span class="fw-semibold">Profils</span>
            <button type="button" class="btn btn-sm btn-primary" @click="openCreate">Nouveau</button>
          </div>
          <div class="list-group list-group-flush">
            <button
              v-for="profile in profiles"
              :key="profile.id"
              type="button"
              class="list-group-item list-group-item-action text-start"
              :class="{ active: String(profile.id) === selectedId }"
              @click="openProfile(profile.id)"
            >
              <div class="fw-semibold">{{ profile.name }}</div>
              <small class="text-muted">
                {{ profile.status }}
                <span v-if="profile.is_default"> · défaut org</span>
              </small>
            </button>
            <div v-if="!loading && !profiles.length" class="list-group-item text-muted small">
              Aucun profil global. Créez-en un ou continuez avec le mode legacy.
            </div>
          </div>
        </div>
      </div>

      <div v-if="isEditing" class="col-12 col-lg-8">
        <div class="card shadow-sm">
          <div class="card-body">
            <div class="mb-3">
              <label class="form-label">Nom du profil</label>
              <input v-model="form.name" class="form-control" type="text" required />
            </div>
            <div class="mb-3">
              <label class="form-label">Description</label>
              <textarea v-model="form.description" class="form-control" rows="2" />
            </div>
            <div class="row mb-3">
              <div class="col-md-6">
                <label class="form-label">Statut</label>
                <select v-model="form.status" class="form-select">
                  <option value="draft">Brouillon</option>
                  <option value="active">Actif</option>
                  <option value="inactive">Inactif</option>
                </select>
              </div>
              <div class="col-md-6 d-flex align-items-end">
                <div class="form-check">
                  <input id="isDefault" v-model="form.is_default" class="form-check-input" type="checkbox" />
                  <label class="form-check-label" for="isDefault">Profil par défaut (organisation)</label>
                </div>
              </div>
            </div>

            <h2 class="h6 mt-4">Sous-configurations par posture</h2>
            <div v-for="slot in postureSlots" :key="slot.code" class="border rounded p-3 mb-3">
              <h3 class="h6">{{ slot.label }}</h3>
              <div class="mb-2">
                <label class="form-label small">Prompt apprenant (TutorPrompt)</label>
                <select v-model="form[slot.promptField]" class="form-select form-select-sm">
                  <option value="">— héritage legacy —</option>
                  <option v-for="p in promptsForPosture(slot.code)" :key="p.id" :value="p.id">
                    {{ p.name }} ({{ p.code }})
                  </option>
                </select>
              </div>
              <div>
                <label class="form-label small">Profil de conduite (optionnel)</label>
                <select v-model="form[slot.conductField]" class="form-select form-select-sm">
                  <option value="">— résolution org / système —</option>
                  <option v-for="c in conductForPosture(slot.code)" :key="c.id" :value="c.id">
                    {{ c.description || c.posture }}
                  </option>
                </select>
              </div>
            </div>

            <h2 class="h6 mt-4">Évaluation finale</h2>
            <div class="border rounded p-3 mb-3">
              <div class="mb-2">
                <label class="form-label small">Profil d'évaluation (EvaluationPromptProfile)</label>
                <select v-model="form.evaluation_prompt_profile_id" class="form-select form-select-sm">
                  <option value="">— héritage politique org —</option>
                  <option v-for="ep in evaluationProfiles" :key="ep.id" :value="ep.id">
                    {{ ep.label }} ({{ ep.code }})
                  </option>
                </select>
              </div>
              <div>
                <label class="form-label small">Politique d'évaluation org (optionnel)</label>
                <select v-model="form.evaluation_policy_id" class="form-select form-select-sm">
                  <option value="">— get_or_create groupe/org —</option>
                  <option v-for="pol in evaluationPolicies" :key="pol.id" :value="pol.id">
                    Politique org #{{ pol.id }}
                  </option>
                </select>
              </div>
            </div>

            <button type="button" class="btn btn-primary" :disabled="saving || !form.name" @click="saveProfile">
              {{ saving ? 'Enregistrement…' : 'Enregistrer' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
