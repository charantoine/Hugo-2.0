<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import api from '../../../api/client'

const props = defineProps({
  postureCode: { type: String, required: true },
  postureLabel: { type: String, default: '' },
})

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

const orgProfile = computed(() =>
  profiles.value.find((item) => item.posture === props.postureCode && item.organisation)
)
const systemProfile = computed(() =>
  profiles.value.find((item) => item.posture === props.postureCode && !item.organisation)
)
const scopeLabel = computed(() => {
  if (orgProfile.value) return 'Personnalisé (organisation)'
  if (systemProfile.value) return 'Défaut système'
  return 'Statique (code)'
})

function listToText(value) {
  return Array.isArray(value) ? value.join(', ') : ''
}

function parseList(text) {
  return String(text || '')
    .split(',')
    .map((value) => value.trim())
    .filter(Boolean)
}

function syncForm() {
  const source = orgProfile.value || systemProfile.value || STATIC_FALLBACKS[props.postureCode] || null
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

const preview = computed(() => {
  const forbiddenMoves = parseList(form.value.forbidden_moves_text).join(', ') || 'aucun'
  if (form.value.system_template) {
    return form.value.system_template
      .replaceAll('{posture}', (props.postureLabel || props.postureCode).toUpperCase())
      .replaceAll('{max_questions}', String(form.value.max_questions_per_turn || 2))
      .replaceAll('{forbidden_moves}', forbiddenMoves)
      .replaceAll('{description}', form.value.description || '')
  }
  return [
    `POSTURE DE SÉANCE : ${(props.postureLabel || props.postureCode).toUpperCase()}`,
    form.value.description || '',
    `Nombre maximum de questions par tour : ${form.value.max_questions_per_turn || 2}.`,
    `Gestes interdits : ${forbiddenMoves}.`,
  ].filter(Boolean).join('\n')
})

async function loadProfiles() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/hugo/conduct-profiles/')
    profiles.value = Array.isArray(data) ? data : (data.results || [])
    syncForm()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors du chargement du profil de conduite.'
    profiles.value = []
  } finally {
    loading.value = false
  }
}

async function saveProfile() {
  if (!form.value.system_template || saving.value) return
  saving.value = true
  error.value = ''
  success.value = ''
  const payload = {
    posture: props.postureCode,
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
    if (orgProfile.value?.id) {
      await api.patch(`/hugo/conduct-profiles/${orgProfile.value.id}/`, payload)
    } else {
      await api.post('/hugo/conduct-profiles/', payload)
    }
    success.value = 'Profil de conduite enregistré.'
    await loadProfiles()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors de l’enregistrement.'
  } finally {
    saving.value = false
  }
}

async function resetToSystemDefault() {
  if (!orgProfile.value?.id || saving.value) return
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    await api.delete(`/hugo/conduct-profiles/${orgProfile.value.id}/`)
    success.value = 'Profil réinitialisé au défaut système.'
    await loadProfiles()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors de la réinitialisation.'
  } finally {
    saving.value = false
  }
}

watch(() => props.postureCode, () => {
  success.value = ''
  syncForm()
})

onMounted(loadProfiles)
</script>

<template>
  <div class="card shadow-sm">
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-start mb-3">
        <div>
          <h2 class="h5 mb-1">Profil de conduite (posture)</h2>
          <p class="text-muted small mb-0">
            Règles injectées dans le prompt pour la posture « {{ postureLabel || postureCode }} ».
          </p>
        </div>
        <span class="badge text-bg-light border">{{ scopeLabel }}</span>
      </div>

      <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
      <div v-if="success" class="alert alert-success py-2">{{ success }}</div>
      <div v-if="loading" class="text-muted small">Chargement…</div>

      <template v-else>
        <div class="row g-3">
          <div class="col-12">
            <label class="form-label">Template système (bloc posture)</label>
            <textarea v-model="form.system_template" class="form-control" rows="5" />
          </div>
          <div class="col-12">
            <label class="form-label">Template utilisateur (optionnel)</label>
            <textarea v-model="form.user_template" class="form-control" rows="2" />
          </div>
          <div class="col-md-4">
            <label class="form-label">Max questions / tour</label>
            <input v-model.number="form.max_questions_per_turn" type="number" min="1" max="5" class="form-control">
          </div>
          <div class="col-md-4">
            <label class="form-label">Gestes interdits</label>
            <input v-model="form.forbidden_moves_text" type="text" class="form-control" placeholder="project, …">
          </div>
          <div class="col-md-4">
            <label class="form-label">Politique de clôture</label>
            <input v-model="form.closure_policy" type="text" class="form-control" placeholder="explicit_or_green">
          </div>
          <div class="col-12">
            <label class="form-label">Description métier</label>
            <input v-model="form.description" type="text" class="form-control">
          </div>
        </div>

        <div class="d-flex gap-2 mt-3">
          <button type="button" class="btn btn-primary btn-sm" :disabled="saving || !form.system_template" @click="saveProfile">
            {{ saving ? 'Enregistrement…' : 'Enregistrer la conduite' }}
          </button>
          <button
            type="button"
            class="btn btn-outline-secondary btn-sm"
            :disabled="saving || !orgProfile"
            @click="resetToSystemDefault"
          >
            Réinitialiser au défaut système
          </button>
        </div>

        <div class="mt-3">
          <p class="small text-muted mb-1">Prévisualisation du bloc posture</p>
          <pre class="small bg-light p-3 rounded mb-0" style="white-space: pre-wrap;">{{ preview }}</pre>
        </div>
      </template>
    </div>
  </div>
</template>
