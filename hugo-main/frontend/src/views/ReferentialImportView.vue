<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/client'

const jsonInput = ref('')
const result = ref(null)
const error = ref('')
const loading = ref(false)
const fileInput = ref(null)
const groups = ref([])
const selectedGroupId = ref('')
const loadingGroups = ref(true)
const associatedGroupName = ref('')

onMounted(async () => {
  try {
    const { data } = await api.get('/groups/')
    groups.value = Array.isArray(data) ? data : (data.results || [])
  } catch {
    groups.value = []
  } finally {
    loadingGroups.value = false
  }
})

const example = `{
  "name": "BAC PRO MELEC",
  "source_ref": "RNCP38878",
  "items": [
    {
      "code": "C1",
      "title": "Analyser les conditions de l'opération et son contexte",
      "block_code": "BC01",
      "block_label": "Préparation des opérations à réaliser",
      "evaluation_criteria": [],
      "evaluation_modalities": [],
      "expected_evidence": [],
      "criteria": [
        {
          "code": "C1.1",
          "label": "Les informations nécessaires sont recueillies",
          "expected_evidence": [],
          "question_seeds": []
        }
      ],
      "tasks": ["T1-1", "T1-2"]
    }
  ],
  "activities": [
    {
      "code": "A1",
      "label": "Préparation des opérations",
      "order_index": 1,
      "tasks": [
        { "code": "T1-1", "label": "Prendre connaissance du dossier", "order_index": 1 },
        { "code": "T1-2", "label": "Rechercher les informations d'exécution", "order_index": 2 }
      ]
    }
  ],
  "competency_tasks": [
    { "competency_code": "C1", "task_code": "T1-1" },
    { "competency_code": "C1", "task_code": "T1-2" }
  ]
}`

function loadFile(event) {
  const file = event.target.files?.[0]
  if (!file) return
  error.value = ''
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const text = e.target?.result
      if (typeof text !== 'string') return
      JSON.parse(text)
      jsonInput.value = text
    } catch (err) {
      error.value = 'Fichier JSON invalide : ' + (err.message || err)
    }
  }
  reader.readAsText(file, 'UTF-8')
  if (fileInput.value) fileInput.value.value = ''
}

async function submit() {
  error.value = ''
  result.value = null
  const raw = jsonInput.value.trim()
  if (!raw) {
    error.value = 'Collez ou chargez un JSON.'
    return
  }
  let data
  try {
    data = JSON.parse(raw)
  } catch (err) {
    error.value = 'JSON invalide : ' + (err.message || err)
    return
  }
  if (!data.items || !Array.isArray(data.items)) {
    error.value = 'Le JSON doit contenir un tableau "items".'
    return
  }
  loading.value = true
  associatedGroupName.value = ''
  try {
    const { data: res } = await api.post('/referentials/import-v2/', data)
    result.value = res
    if (selectedGroupId.value) {
      try {
        await api.put(`/groups/${selectedGroupId.value}/referential-config/`, { referential_id: res.id })
        const g = groups.value.find((x) => String(x.id) === String(selectedGroupId.value))
        associatedGroupName.value = g ? g.name : ''
      } catch (e) {
        result.value = { ...res, _configError: e.response?.data?.detail || 'Erreur association au groupe.' }
      }
    }
  } catch (err) {
    error.value = err.response?.data?.detail || err.response?.data?.message || err.message || 'Erreur lors de l\'import.'
  } finally {
    loading.value = false
  }
}

function setExample() {
  jsonInput.value = example
  error.value = ''
  result.value = null
}
</script>

<template>
  <div class="container-fluid">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item"><router-link to="/dashboard">Tableau de bord</router-link></li>
        <li class="breadcrumb-item active" aria-current="page">Importer un référentiel</li>
      </ol>
    </nav>
    <h1 class="h4 mb-4">Importer un référentiel (import v2)</h1>
    <p class="text-muted small mb-4">
      Collez un JSON ou chargez un fichier .json (items + criteria) et, en option, activities/tasks/competency_tasks.
    </p>

    <div class="row">
      <div class="col-12 col-lg-8">
        <div class="card mb-3">
          <div class="card-header d-flex justify-content-between align-items-center">
            <span>JSON du référentiel</span>
            <div class="btn-group btn-group-sm">
              <button type="button" class="btn btn-outline-secondary" @click="setExample">Exemple</button>
              <label class="btn btn-outline-primary mb-0">
                Charger un fichier
                <input ref="fileInput" type="file" accept=".json,application/json" class="d-none" @change="loadFile" />
              </label>
            </div>
          </div>
          <div class="card-body p-0">
            <textarea
              v-model="jsonInput"
              class="form-control border-0 font-monospace small"
              rows="16"
              placeholder='{"name": "...", "source_ref": "...", "items": [...]}'
              spellcheck="false"
            ></textarea>
          </div>
        </div>
        <div class="mb-3">
          <label class="form-label" for="import-group">Associer à un groupe (optionnel)</label>
          <select
            id="import-group"
            v-model="selectedGroupId"
            class="form-select form-select-sm"
            :disabled="loadingGroups || loading"
          >
            <option value="">— Aucun —</option>
            <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
        </div>
        <button type="button" class="btn btn-primary" :disabled="loading" @click="submit">
          {{ loading ? 'Import en cours…' : 'Importer' }}
        </button>
      </div>
      <div class="col-12 col-lg-4">
        <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
        <div v-if="result" class="alert alert-success" role="alert">
          <strong>Référentiel créé</strong>
          <ul class="mb-0 mt-2">
            <li>ID : <code>{{ result.id }}</code></li>
            <li>Nom : {{ result.name }}</li>
            <li>Items : {{ result.items_count }}</li>
            <li>Activités : {{ result.activities_count ?? 0 }}</li>
            <li>Tâches : {{ result.tasks_count ?? 0 }}</li>
            <li v-if="associatedGroupName">Associé au groupe : <strong>{{ associatedGroupName }}</strong></li>
            <li v-else-if="result._configError" class="text-warning">Association au groupe : {{ result._configError }}</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>
