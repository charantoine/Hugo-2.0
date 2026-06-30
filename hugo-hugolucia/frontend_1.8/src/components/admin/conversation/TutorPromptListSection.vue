<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '../../../api/client'

const props = defineProps({
  postureCode: { type: String, required: true },
})

const prompts = ref([])
const loading = ref(false)
const error = ref('')
const saving = ref(false)
const expandedId = ref('')

const showCreate = ref(false)
const code = ref('')
const name = ref('')
const systemTemplate = ref('')
const userTemplate = ref('')
const isDefault = ref(false)

const filteredPrompts = computed(() =>
  prompts.value.filter(
    (p) => p.is_active !== false && String(p.conversation_profile || '') === props.postureCode,
  ),
)

async function loadPrompts() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/hugo/tutor-prompts/')
    prompts.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors du chargement des prompts.'
    prompts.value = []
  } finally {
    loading.value = false
  }
}

function resetCreateForm() {
  code.value = ''
  name.value = ''
  systemTemplate.value = ''
  userTemplate.value = ''
  isDefault.value = false
  showCreate.value = false
}

async function createPrompt() {
  if (!code.value || !name.value || !systemTemplate.value || !userTemplate.value || saving.value) return
  saving.value = true
  error.value = ''
  try {
    await api.post('/hugo/tutor-prompts/', {
      code: code.value,
      name: name.value,
      description: '',
      system_template: systemTemplate.value,
      user_template: userTemplate.value,
      prompt_type: 'AFEST_HUGO',
      language: 'fr',
      tone: 'COACHING',
      conversation_profile: props.postureCode,
      output_format_mode: 'multi_question_numbered',
      default_session_phase: 'exploration',
      max_questions_per_turn: 2,
      max_tokens: 150,
      allow_lists: false,
      is_default: !!isDefault.value,
      is_active: true,
      metadata: {},
    })
    resetCreateForm()
    await loadPrompts()
  } catch (e) {
    error.value = e.response?.data?.detail || e.message || 'Erreur lors de la création.'
  } finally {
    saving.value = false
  }
}

async function deletePrompt(id) {
  if (!id) return
  error.value = ''
  try {
    await api.delete(`/hugo/tutor-prompts/${id}/`)
    prompts.value = prompts.value.filter((p) => p.id !== id)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors de la suppression.'
  }
}

onMounted(loadPrompts)
</script>

<template>
  <div class="card shadow-sm">
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-start mb-3">
        <div>
          <h2 class="h5 mb-1">Prompts orchestrateur apprenant</h2>
          <p class="text-muted small mb-0">
            Templates system / user et paramètres de rendu pour cette posture.
            <router-link to="/tutor-prompts" class="ms-1">Édition avancée (legacy)</router-link>
          </p>
        </div>
        <button type="button" class="btn btn-sm btn-outline-primary" @click="showCreate = !showCreate">
          {{ showCreate ? 'Annuler' : 'Nouveau prompt' }}
        </button>
      </div>

      <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>

      <div v-if="showCreate" class="border rounded p-3 mb-3 bg-light">
        <div class="row g-2">
          <div class="col-md-6">
            <label class="form-label small">Code</label>
            <input v-model="code" type="text" class="form-control form-control-sm">
          </div>
          <div class="col-md-6">
            <label class="form-label small">Nom</label>
            <input v-model="name" type="text" class="form-control form-control-sm">
          </div>
          <div class="col-12">
            <label class="form-label small">Template système</label>
            <textarea v-model="systemTemplate" class="form-control form-control-sm" rows="4" />
          </div>
          <div class="col-12">
            <label class="form-label small">Template utilisateur</label>
            <textarea v-model="userTemplate" class="form-control form-control-sm" rows="3" />
          </div>
          <div class="col-12">
            <div class="form-check">
              <input id="prompt-default-mode" v-model="isDefault" class="form-check-input" type="checkbox">
              <label class="form-check-label small" for="prompt-default-mode">Prompt par défaut (organisation)</label>
            </div>
          </div>
          <div class="col-12">
            <button
              type="button"
              class="btn btn-sm btn-primary"
              :disabled="saving || !code || !name || !systemTemplate || !userTemplate"
              @click="createPrompt"
            >
              Créer
            </button>
          </div>
        </div>
      </div>

      <div v-if="loading" class="text-muted small">Chargement…</div>
      <ul v-else-if="filteredPrompts.length" class="list-group list-group-flush">
        <li v-for="p in filteredPrompts" :key="p.id" class="list-group-item px-0">
          <div class="d-flex justify-content-between gap-2">
            <div class="flex-grow-1">
              <strong>{{ p.name }}</strong>
              <span v-if="p.is_default" class="badge text-bg-primary ms-2">défaut</span>
              <span v-if="!p.is_active" class="badge text-bg-secondary ms-1">inactif</span>
              <p class="small text-muted mb-1">{{ p.code }}</p>
              <button type="button" class="btn btn-link btn-sm p-0" @click="expandedId = expandedId === p.id ? '' : p.id">
                {{ expandedId === p.id ? 'Masquer' : 'Voir templates' }}
              </button>
              <div v-if="expandedId === p.id" class="mt-2">
                <pre class="small bg-light p-2 rounded mb-1" style="white-space: pre-wrap;">{{ p.system_template }}</pre>
                <pre class="small bg-light p-2 rounded mb-0" style="white-space: pre-wrap;">{{ p.user_template }}</pre>
              </div>
            </div>
            <div class="d-flex flex-column gap-1">
              <router-link :to="`/tutor-prompts`" class="btn btn-sm btn-outline-secondary">Modifier (legacy)</router-link>
              <button type="button" class="btn btn-sm btn-outline-danger" @click="deletePrompt(p.id)">Supprimer</button>
            </div>
          </div>
        </li>
      </ul>
      <p v-else class="text-muted small mb-0">Aucun prompt rattaché à cette posture. Créez-en un ou utilisez l’éditeur legacy.</p>
    </div>
  </div>
</template>
