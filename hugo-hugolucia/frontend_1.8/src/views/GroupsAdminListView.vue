<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/client'
import { useAuthStore } from '../stores/auth'
import ActiveOrganisationBanner from '../components/admin/ActiveOrganisationBanner.vue'

const auth = useAuthStore()

const groups = ref([])
const loading = ref(false)
const error = ref('')

const name = ref('')
const llmBackend = ref('OLLAMA')
const saving = ref(false)
const showAdvancedLlm = ref(false)

const editGroupId = ref('')
const editName = ref('')
const editSaving = ref(false)

async function loadGroups() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/groups/')
    groups.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors du chargement des groupes.'
    groups.value = []
  } finally {
    loading.value = false
  }
}

async function createGroup() {
  if (!name.value || saving.value) return
  saving.value = true
  error.value = ''
  try {
    await api.post('/groups/', {
      name: name.value,
      llm_backend: llmBackend.value,
    })
    name.value = ''
    llmBackend.value = 'OLLAMA'
    await loadGroups()
  } catch (e) {
    error.value = e.response?.data?.detail || "Erreur lors de la création du groupe."
  } finally {
    saving.value = false
  }
}

function startEdit(group) {
  editGroupId.value = group.id
  editName.value = group.name
}

function cancelEdit() {
  editGroupId.value = ''
  editName.value = ''
}

async function saveEdit() {
  if (!editGroupId.value || !editName.value || editSaving.value) return
  editSaving.value = true
  error.value = ''
  try {
    await api.patch(`/groups/${editGroupId.value}/`, {
      name: editName.value,
    })
    editGroupId.value = ''
    editName.value = ''
    await loadGroups()
  } catch (e) {
    error.value = e.response?.data?.detail || "Erreur lors de la mise à jour du groupe."
  } finally {
    editSaving.value = false
  }
}

onMounted(() => {
  loadGroups()
})
</script>

<template>
  <div class="container-fluid">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item">
          <router-link to="/dashboard">Tableau de bord</router-link>
        </li>
        <li class="breadcrumb-item active" aria-current="page">Groupes</li>
      </ol>
    </nav>

    <h1 class="h4 mb-2">Groupes de l’organisation</h1>
    <ActiveOrganisationBanner show-switcher-hint />

    <div class="row mb-4">
      <div class="col-12 col-lg-6">
        <div class="card shadow-sm">
          <div class="card-body">
            <h2 class="h5 mb-3">Nouveau groupe</h2>

            <div class="mb-3">
              <label for="group-name" class="form-label">Nom du groupe</label>
              <input
                id="group-name"
                v-model="name"
                type="text"
                class="form-control"
                :disabled="saving"
                autocomplete="off"
              />
            </div>

            <div class="mb-3">
              <button
                type="button"
                class="btn btn-sm btn-link px-0 text-decoration-none"
                @click="showAdvancedLlm = !showAdvancedLlm"
              >
                {{ showAdvancedLlm ? '▾' : '▸' }} Paramètres avancés (moteur LLM)
              </button>
              <div v-show="showAdvancedLlm" class="mt-2 border rounded p-2 bg-light">
                <label for="llm-backend" class="form-label small mb-1">Moteur LLM</label>
                <select
                  id="llm-backend"
                  v-model="llmBackend"
                  class="form-select form-select-sm"
                  :disabled="saving"
                >
                  <option value="OLLAMA">Ollama (local)</option>
                  <option value="OVH_AI">OVH AI Endpoints</option>
                </select>
                <p class="text-muted small mb-0 mt-1">Par défaut : Ollama. Modifiable ensuite sur le détail du groupe.</p>
              </div>
            </div>

            <button
              type="button"
              class="btn btn-primary"
              :disabled="saving || !name"
              @click="createGroup"
            >
              <span v-if="saving" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
              Créer le groupe
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm">
      <div class="card-body">
        <h2 class="h5 mb-3">Liste des groupes</h2>

        <div v-if="error" class="alert alert-danger" role="alert">
          {{ error }}
        </div>

        <div v-if="loading" class="text-center py-3">
          <div class="spinner-border spinner-border-sm text-primary" role="status">
            <span class="visually-hidden">Chargement…</span>
          </div>
        </div>

        <ul v-else-if="groups.length" class="list-group list-group-flush">
          <li
            v-for="g in groups"
            :key="g.id"
            class="list-group-item d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-2"
          >
            <div>
              <router-link :to="{ name: 'GroupAdminDetail', params: { groupId: g.id } }">
                {{ g.name }}
              </router-link>
              <span class="text-muted small ms-2">
                ({{ g.llm_backend }})
              </span>
            </div>
            <div class="d-flex align-items-center gap-2">
              <template v-if="editGroupId === g.id">
                <input
                  v-model="editName"
                  type="text"
                  class="form-control form-control-sm"
                  style="max-width: 200px"
                  :disabled="editSaving"
                />
                <button
                  type="button"
                  class="btn btn-sm btn-primary"
                  :disabled="editSaving || !editName"
                  @click="saveEdit"
                >
                  <span
                    v-if="editSaving"
                    class="spinner-border spinner-border-sm me-1"
                    role="status"
                    aria-hidden="true"
                  />
                  Enregistrer
                </button>
                <button
                  type="button"
                  class="btn btn-sm btn-outline-secondary"
                  :disabled="editSaving"
                  @click="cancelEdit"
                >
                  Annuler
                </button>
              </template>
              <template v-else>
                <button
                  type="button"
                  class="btn btn-sm btn-outline-secondary"
                  @click="startEdit(g)"
                >
                  Renommer
                </button>
              </template>
            </div>
          </li>
        </ul>
        <p v-else class="text-muted small mb-0">Aucun groupe pour le moment.</p>
      </div>
    </div>
  </div>
</template>

