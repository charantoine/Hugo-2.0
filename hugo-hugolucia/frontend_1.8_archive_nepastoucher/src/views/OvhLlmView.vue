<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/client'

const items = ref([])
const loading = ref(false)
const error = ref('')

const name = ref('')
const code = ref('')
const description = ref('')
const priceInput = ref('')
const priceOutput = ref('')
const saving = ref(false)

const editingId = ref('')
const editingName = ref('')
const editingCode = ref('')
const editingDescription = ref('')
const editingPriceInput = ref('')
const editingPriceOutput = ref('')
const editingSaving = ref(false)

const basePath = '/hugo/ovh-llms/'

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get(basePath)
    items.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors du chargement des OVH LLM.'
    items.value = []
  } finally {
    loading.value = false
  }
}

async function createItem() {
  if (!name.value || !code.value || !priceInput.value || !priceOutput.value || saving.value) return
  saving.value = true
  error.value = ''
  try {
    await api.post(basePath, {
      name: name.value,
      code: code.value,
      description: description.value,
      price_per_million_input: priceInput.value,
      price_per_million_output: priceOutput.value,
    })
    name.value = ''
    code.value = ''
    description.value = ''
    priceInput.value = ''
    priceOutput.value = ''
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors de la création.'
  } finally {
    saving.value = false
  }
}

function startEdit(item) {
  editingId.value = item.id
  editingName.value = item.name
  editingCode.value = item.code
  editingDescription.value = item.description || ''
  editingPriceInput.value = item.price_per_million_input || ''
  editingPriceOutput.value = item.price_per_million_output || ''
}

function cancelEdit() {
  editingId.value = ''
  editingName.value = ''
  editingCode.value = ''
  editingDescription.value = ''
  editingPriceInput.value = ''
  editingPriceOutput.value = ''
}

async function saveEdit() {
  if (!editingId.value || !editingName.value || !editingCode.value || !editingPriceInput.value || !editingPriceOutput.value || editingSaving.value) return
  editingSaving.value = true
  error.value = ''
  try {
    await api.patch(`${basePath}${editingId.value}/`, {
      name: editingName.value,
      code: editingCode.value,
      description: editingDescription.value,
      price_per_million_input: editingPriceInput.value,
      price_per_million_output: editingPriceOutput.value,
    })
    await load()
    cancelEdit()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors de la mise à jour.'
  } finally {
    editingSaving.value = false
  }
}

async function deleteItem(id) {
  if (!id) return
  error.value = ''
  try {
    await api.delete(`${basePath}${id}/`)
    items.value = items.value.filter((i) => i.id !== id)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors de la suppression.'
  }
}

onMounted(() => {
  load()
})
</script>

<template>
  <div class="container-fluid">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item">
          <router-link to="/dashboard">Tableau de bord</router-link>
        </li>
        <li class="breadcrumb-item active" aria-current="page">OVH LLM</li>
      </ol>
    </nav>

    <h1 class="h4 mb-4">Catalogue OVH LLM</h1>
    <p class="text-muted mb-4">
      Modèles LLM OVH avec tarifs (1M tokens entrée / sortie). Utilisables dans les prompts tuteur.
    </p>

    <div class="row mb-4">
      <div class="col-12 col-lg-6">
        <div class="card shadow-sm">
          <div class="card-body">
            <h2 class="h5 mb-3">Nouveau modèle</h2>

            <div class="mb-3">
              <label for="ovh-name" class="form-label">Nom</label>
              <input
                id="ovh-name"
                v-model="name"
                type="text"
                class="form-control"
                :disabled="saving"
                autocomplete="off"
              />
            </div>

            <div class="mb-3">
              <label for="ovh-code" class="form-label">Code</label>
              <input
                id="ovh-code"
                v-model="code"
                type="text"
                class="form-control"
                :disabled="saving"
                autocomplete="off"
              />
            </div>

            <div class="mb-3">
              <label for="ovh-description" class="form-label">Description (optionnelle)</label>
              <textarea
                id="ovh-description"
                v-model="description"
                class="form-control"
                rows="2"
                :disabled="saving"
              />
            </div>

            <div class="mb-3">
              <label for="ovh-price-in" class="form-label">Tarif 1M tokens entrée</label>
              <input
                id="ovh-price-in"
                v-model="priceInput"
                type="text"
                class="form-control"
                :disabled="saving"
                placeholder="ex. 0.50 €"
              />
            </div>

            <div class="mb-3">
              <label for="ovh-price-out" class="form-label">Tarif 1M tokens sortie</label>
              <input
                id="ovh-price-out"
                v-model="priceOutput"
                type="text"
                class="form-control"
                :disabled="saving"
                placeholder="ex. 1.20 €"
              />
            </div>

            <button
              type="button"
              class="btn btn-primary"
              :disabled="saving || !name || !code || !priceInput || !priceOutput"
              @click="createItem"
            >
              <span v-if="saving" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
              Créer
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm">
      <div class="card-body">
        <h2 class="h5 mb-3">Liste des modèles</h2>

        <div v-if="error" class="alert alert-danger" role="alert">
          {{ error }}
        </div>

        <div v-if="loading" class="text-center py-3">
          <div class="spinner-border spinner-border-sm text-primary" role="status">
            <span class="visually-hidden">Chargement…</span>
          </div>
        </div>

        <ul v-else-if="items.length" class="list-group list-group-flush">
          <li
            v-for="item in items"
            :key="item.id"
            class="list-group-item"
          >
            <div class="d-flex justify-content-between align-items-start gap-3">
              <div class="flex-grow-1">
                <template v-if="editingId === item.id">
                  <div class="row g-2 mb-2">
                    <div class="col-12 col-md-6">
                      <input
                        v-model="editingName"
                        type="text"
                        class="form-control form-control-sm"
                        placeholder="Nom"
                        :disabled="editingSaving"
                      />
                    </div>
                    <div class="col-12 col-md-6">
                      <input
                        v-model="editingCode"
                        type="text"
                        class="form-control form-control-sm"
                        placeholder="Code"
                        :disabled="editingSaving"
                      />
                    </div>
                    <div class="col-12 col-md-6">
                      <input
                        v-model="editingPriceInput"
                        type="text"
                        class="form-control form-control-sm"
                        placeholder="Tarif entrée"
                        :disabled="editingSaving"
                      />
                    </div>
                    <div class="col-12 col-md-6">
                      <input
                        v-model="editingPriceOutput"
                        type="text"
                        class="form-control form-control-sm"
                        placeholder="Tarif sortie"
                        :disabled="editingSaving"
                      />
                    </div>
                  </div>
                  <textarea
                    v-model="editingDescription"
                    class="form-control form-control-sm mb-2"
                    rows="2"
                    placeholder="Description (optionnelle)"
                    :disabled="editingSaving"
                  />
                </template>
                <template v-else>
                  <strong>{{ item.name }}</strong>
                  <code class="ms-2 small">{{ item.code }}</code>
                  <div v-if="item.description" class="small text-muted mt-1">
                    {{ item.description }}
                  </div>
                  <div class="small text-muted mt-1">
                    Entrée : {{ item.price_per_million_input }} — Sortie : {{ item.price_per_million_output }}
                  </div>
                </template>
              </div>
              <div class="d-flex flex-column gap-2">
                <template v-if="editingId === item.id">
                  <button
                    type="button"
                    class="btn btn-sm btn-primary"
                    :disabled="editingSaving || !editingName || !editingCode || !editingPriceInput || !editingPriceOutput"
                    @click="saveEdit"
                  >
                    <span v-if="editingSaving" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true" />
                    Enregistrer
                  </button>
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-secondary"
                    :disabled="editingSaving"
                    @click="cancelEdit"
                  >
                    Annuler
                  </button>
                </template>
                <template v-else>
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-secondary"
                    @click="startEdit(item)"
                  >
                    Modifier
                  </button>
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-danger"
                    @click="deleteItem(item.id)"
                  >
                    Supprimer
                  </button>
                </template>
              </div>
            </div>
          </li>
        </ul>
        <p v-else class="text-muted small mb-0">
          Aucun modèle OVH LLM pour le moment.
        </p>
      </div>
    </div>
  </div>
</template>
