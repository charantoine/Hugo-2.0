<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import api from '../api/client'

const POSTURES = [
  { value: 'diagnostic', label: 'Séance de diagnostic' },
  { value: 'reflective_afest', label: 'Entretien réflexif AFEST' },
  { value: 'knowledge_review', label: 'Révision / bâchage' },
]

const STATIC_FALLBACKS = {
  diagnostic: {
    system_template: 'Bloc posture :\n- posture : {posture}\n- max_questions_per_turn : {max_questions}\n- forbidden_moves : {forbidden_moves}\n- description : {description}',
    user_template: '',
    max_questions_per_turn: 2,
    forbidden_moves: ['project'],
    allowed_moves: ['clarify', 'elicit_action', 'problematize', 'analyze', 'contrast_gently', 'reassure', 'close', 'assist'],
    closure_policy: 'explicit_or_green',
    description: 'Diagnostic guidé.',
  },
  reflective_afest: {
    system_template: 'Bloc posture :\n- posture : {posture}\n- max_questions_per_turn : {max_questions}\n- forbidden_moves : {forbidden_moves}\n- description : {description}',
    user_template: '',
    max_questions_per_turn: 2,
    forbidden_moves: [],
    allowed_moves: ['clarify', 'elicit_action', 'problematize', 'analyze', 'contrast_gently', 'project', 'reassure', 'close', 'assist'],
    closure_policy: 'explicit_or_green',
    description: 'Entretien réflexif AFEST.',
  },
  knowledge_review: {
    system_template: 'Bloc posture :\n- posture : {posture}\n- max_questions_per_turn : {max_questions}\n- forbidden_moves : {forbidden_moves}\n- description : {description}',
    user_template: '',
    max_questions_per_turn: 1,
    forbidden_moves: ['elicit_action', 'project'],
    allowed_moves: ['clarify', 'analyze', 'contrast_gently', 'reassure', 'close', 'assist'],
    closure_policy: 'explicit_or_green',
    description: 'Révision ou bâchage ciblé.',
  },
}

const profiles = ref([])
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')
const selectedPosture = ref('diagnostic')

const form = ref({
  system_template: '',
  user_template: '',
  max_questions_per_turn: 2,
  forbidden_moves_text: '',
  allowed_moves_text: '',
  closure_policy: '',
  description: '',
  is_active: true,
})

const rows = computed(() => POSTURES.map((posture) => {
  const orgProfile = profiles.value.find((item) => item.posture === posture.value && item.organisation)
  const systemProfile = profiles.value.find((item) => item.posture === posture.value && !item.organisation)
  return { ...posture, orgProfile, systemProfile }
}))

const selectedRow = computed(() => rows.value.find((row) => row.value === selectedPosture.value) || rows.value[0])

function listToText(value) {
  return Array.isArray(value) ? value.join(', ') : ''
}

function syncFormFromSelected() {
  const source = selectedRow.value?.orgProfile || selectedRow.value?.systemProfile || STATIC_FALLBACKS[selectedRow.value?.value] || null
  form.value = {
    system_template: source?.system_template || '',
    user_template: source?.user_template || '',
    max_questions_per_turn: Number(source?.max_questions_per_turn || 2),
    forbidden_moves_text: listToText(source?.forbidden_moves || []),
    allowed_moves_text: listToText(source?.allowed_moves || []),
    closure_policy: source?.closure_policy || '',
    description: source?.description || '',
    is_active: source?.is_active ?? true,
  }
}

function parseList(text) {
  return String(text || '')
    .split(',')
    .map((value) => value.trim())
    .filter(Boolean)
}

function buildPreview() {
  const forbiddenMoves = parseList(form.value.forbidden_moves_text).join(', ') || 'aucun'
  if (form.value.system_template) {
    return form.value.system_template
      .replaceAll('{posture}', selectedRow.value?.label?.toUpperCase() || '')
      .replaceAll('{max_questions}', String(form.value.max_questions_per_turn || 2))
      .replaceAll('{forbidden_moves}', forbiddenMoves)
      .replaceAll('{description}', form.value.description || '')
  }
  return [
    `POSTURE DE SÉANCE : ${(selectedRow.value?.label || '').toUpperCase()}`,
    form.value.description || '',
    `Nombre maximum de questions par tour : ${form.value.max_questions_per_turn || 2}.`,
    `Gestes interdits : ${forbiddenMoves}.`,
  ].filter(Boolean).join('\n')
}

async function loadProfiles() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/hugo/conduct-profiles/')
    profiles.value = Array.isArray(data) ? data : (data.results || [])
    syncFormFromSelected()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors du chargement des profils de conduite.'
    profiles.value = []
  } finally {
    loading.value = false
  }
}

async function saveProfile() {
  if (!selectedRow.value || !form.value.system_template || saving.value) return
  saving.value = true
  error.value = ''
  success.value = ''
  const payload = {
    posture: selectedRow.value.value,
    system_template: form.value.system_template,
    user_template: form.value.user_template,
    max_questions_per_turn: Number(form.value.max_questions_per_turn) || 2,
    forbidden_moves: parseList(form.value.forbidden_moves_text),
    allowed_moves: parseList(form.value.allowed_moves_text),
    closure_policy: form.value.closure_policy,
    description: form.value.description,
    is_active: !!form.value.is_active,
  }
  try {
    if (selectedRow.value.orgProfile?.id) {
      await api.patch(`/hugo/conduct-profiles/${selectedRow.value.orgProfile.id}/`, payload)
    } else {
      await api.post('/hugo/conduct-profiles/', payload)
    }
    success.value = 'Profil de conduite enregistré.'
    await loadProfiles()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors de l’enregistrement du profil.'
  } finally {
    saving.value = false
  }
}

async function resetToSystemDefault() {
  if (!selectedRow.value?.orgProfile?.id || saving.value) return
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    await api.delete(`/hugo/conduct-profiles/${selectedRow.value.orgProfile.id}/`)
    success.value = 'Profil réinitialisé au défaut système.'
    await loadProfiles()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors de la réinitialisation.'
  } finally {
    saving.value = false
  }
}

watch(selectedPosture, () => {
  success.value = ''
  error.value = ''
  syncFormFromSelected()
})

onMounted(() => {
  loadProfiles()
})
</script>

<template>
  <div class="container-fluid">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item"><router-link to="/dashboard">Tableau de bord</router-link></li>
        <li class="breadcrumb-item active" aria-current="page">Profils de conduite</li>
      </ol>
    </nav>

    <h1 class="h4 mb-4">TutorConductProfiles</h1>
    <p class="text-muted mb-4">
      Ajustez ici les règles de conduite par posture, sans modifier le noyau conversationnel.
    </p>

    <div class="row g-4">
      <div class="col-12 col-xl-4">
        <div class="card shadow-sm">
          <div class="card-body">
            <h2 class="h5 mb-3">Postures</h2>
            <div v-if="loading" class="text-muted small">Chargement...</div>
            <div v-else class="list-group">
              <button
                v-for="row in rows"
                :key="row.value"
                type="button"
                class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
                :class="{ active: selectedPosture === row.value }"
                @click="selectedPosture = row.value"
              >
                <span>{{ row.label }}</span>
                <span class="badge text-bg-light border">
                  {{ row.orgProfile ? 'Personnalisé' : (row.systemProfile ? 'Défaut système' : 'Statique') }}
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="col-12 col-xl-8">
        <div class="card shadow-sm">
          <div class="card-body">
            <h2 class="h5 mb-3">{{ selectedRow?.label }}</h2>

            <div v-if="error" class="alert alert-danger">{{ error }}</div>
            <div v-if="success" class="alert alert-success">{{ success }}</div>

            <div class="row g-3">
              <div class="col-12">
                <label class="form-label">Template système</label>
                <textarea v-model="form.system_template" class="form-control" rows="6"></textarea>
              </div>
              <div class="col-12">
                <label class="form-label">Template utilisateur</label>
                <textarea v-model="form.user_template" class="form-control" rows="3"></textarea>
              </div>
              <div class="col-12 col-md-4">
                <label class="form-label">Max questions</label>
                <input v-model.number="form.max_questions_per_turn" type="number" min="1" max="5" class="form-control">
              </div>
              <div class="col-12 col-md-4">
                <label class="form-label">Gestes interdits</label>
                <input v-model="form.forbidden_moves_text" type="text" class="form-control" placeholder="clarify, project">
              </div>
              <div class="col-12 col-md-4">
                <label class="form-label">Gestes autorisés</label>
                <input v-model="form.allowed_moves_text" type="text" class="form-control" placeholder="analyze, reassure">
              </div>
              <div class="col-12 col-md-6">
                <label class="form-label">Politique de clôture</label>
                <input v-model="form.closure_policy" type="text" class="form-control" placeholder="explicit_or_green">
              </div>
              <div class="col-12 col-md-6">
                <label class="form-label">Description</label>
                <input v-model="form.description" type="text" class="form-control">
              </div>
              <div class="col-12">
                <div class="form-check">
                  <input id="conduct-active" v-model="form.is_active" class="form-check-input" type="checkbox">
                  <label for="conduct-active" class="form-check-label">Profil actif</label>
                </div>
              </div>
            </div>

            <div class="d-flex gap-2 mt-4">
              <button type="button" class="btn btn-primary" :disabled="saving || !form.system_template" @click="saveProfile">
                {{ saving ? 'Enregistrement...' : 'Enregistrer' }}
              </button>
              <button
                type="button"
                class="btn btn-outline-secondary"
                :disabled="saving || !selectedRow?.orgProfile"
                @click="resetToSystemDefault"
              >
                Réinitialiser au défaut système
              </button>
            </div>
          </div>
        </div>

        <div class="card shadow-sm mt-4">
          <div class="card-body">
            <h2 class="h5 mb-3">Prévisualisation du bloc posture</h2>
            <pre class="small bg-light p-3 rounded mb-0" style="white-space: pre-wrap;">{{ buildPreview() }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
