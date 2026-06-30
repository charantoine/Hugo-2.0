<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/client'
import TrainerGroupContextPanel from '../components/trainer/TrainerGroupContextPanel.vue'
import TrainerBackToOrchestratorLink from '../components/trainer/TrainerBackToOrchestratorLink.vue'
import { TRAINER_ORCHESTRATOR_ROUTE_NAME } from '../utils/trainerNavigation.js'

const router = useRouter()

const referentialItemId = ref('')
const filePath = ref('')
const questions = ref([])
const answers = ref({})
const loadingQuestions = ref(false)
const submitting = ref(false)
const ingesting = ref(false)
const error = ref('')
const success = ref('')

const canSubmitAnswers = computed(() => (
  referentialItemId.value.trim()
  && questions.value.length
  && Object.values(answers.value).some((value) => String(value || '').trim())
))

async function loadQuestions() {
  const itemId = referentialItemId.value.trim()
  if (!itemId) {
    error.value = 'Indiquez un identifiant référentiel.'
    return
  }
  loadingQuestions.value = true
  error.value = ''
  success.value = ''
  try {
    const { data } = await api.get(`/hugo/trainer/referential-items/${itemId}/elicitation-questions/`)
    questions.value = data.questions || []
    answers.value = Object.fromEntries(questions.value.map((question) => [question.id, '']))
  } catch (e) {
    questions.value = []
    answers.value = {}
    error.value = e.response?.data?.detail || 'Impossible de charger l’atelier.'
  } finally {
    loadingQuestions.value = false
  }
}

async function submitAnswers() {
  const itemId = referentialItemId.value.trim()
  if (!itemId) return
  submitting.value = true
  error.value = ''
  success.value = ''
  try {
    const { data } = await api.post(`/hugo/trainer/referential-items/${itemId}/elicitation-answers/`, {
      answers: answers.value,
    })
    success.value = `${data.created?.length || 0} item(s) créé(s) en statut déclaré — validation humaine requise.`
    router.push({ name: TRAINER_ORCHESTRATOR_ROUTE_NAME })
  } catch (e) {
    error.value = e.response?.data?.detail || 'Enregistrement impossible.'
  } finally {
    submitting.value = false
  }
}

async function ingestDocument() {
  const itemId = referentialItemId.value.trim()
  const path = filePath.value.trim()
  if (!path) {
    error.value = 'Indiquez un chemin de document côté serveur.'
    return
  }
  ingesting.value = true
  error.value = ''
  success.value = ''
  try {
    const { data } = await api.post('/hugo/trainer/documents/ingest/', {
      file_path: path,
      referential_item_id: itemId,
    })
    success.value = `${data.created?.length || 0} extrait(s) créé(s) — à valider dans la liste.`
    router.push({ name: TRAINER_ORCHESTRATOR_ROUTE_NAME })
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ingestion impossible.'
  } finally {
    ingesting.value = false
  }
}

</script>

<template>
  <div class="container-fluid px-0">
    <header class="mb-4">
      <TrainerBackToOrchestratorLink extra-class="mb-3" />
      <h1 class="h4 mb-1">Atelier d’élicitation (V0)</h1>
      <p class="text-muted mb-0 small">
        Dialoguer avec Hugo pour structurer une connaissance — sans accès au verbatim apprenant.
      </p>
    </header>

    <TrainerGroupContextPanel compact />

    <div class="card mb-4">
      <div class="card-body">
        <label class="form-label small" for="referential-item-id">Thème / item référentiel</label>
        <div class="row g-2 align-items-end">
          <div class="col-md-8">
            <input
              id="referential-item-id"
              v-model="referentialItemId"
              type="text"
              class="form-control form-control-sm"
              placeholder="Identifiant référentiel (ex. critère ou compétence)"
            />
          </div>
          <div class="col-md-4">
            <button
              type="button"
              class="btn btn-sm btn-primary w-100"
              :disabled="loadingQuestions"
              @click="loadQuestions"
            >
              {{ loadingQuestions ? 'Chargement…' : 'Démarrer l’atelier' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="questions.length" class="card mb-4">
      <div class="card-body d-grid gap-3">
        <h2 class="h6 mb-0">Questions d’élicitation</h2>
        <div v-for="question in questions" :key="question.id">
          <label class="form-label small" :for="question.id">{{ question.text }}</label>
          <textarea
            :id="question.id"
            v-model="answers[question.id]"
            class="form-control form-control-sm"
            rows="3"
          />
        </div>
        <button
          type="button"
          class="btn btn-primary btn-sm align-self-start"
          :disabled="submitting || !canSubmitAnswers"
          @click="submitAnswers"
        >
          {{ submitting ? 'Enregistrement…' : 'Créer les items provisoires' }}
        </button>
      </div>
    </div>

    <div class="card">
      <div class="card-body">
        <h2 class="h6">Import document (optionnel)</h2>
        <p class="small text-muted">
          Chemin serveur déjà disponible — pas d’upload direct dans cette V0.
        </p>
        <input
          v-model="filePath"
          type="text"
          class="form-control form-control-sm mb-2"
          placeholder="/chemin/vers/document.pdf"
        />
        <button
          type="button"
          class="btn btn-sm btn-outline-secondary"
          :disabled="ingesting"
          @click="ingestDocument"
        >
          {{ ingesting ? 'Ingestion…' : 'Ingérer le document' }}
        </button>
      </div>
    </div>

    <p v-if="success" class="text-success small mt-3">{{ success }}</p>
    <p v-if="error" class="text-danger small mt-3">{{ error }}</p>
  </div>
</template>
