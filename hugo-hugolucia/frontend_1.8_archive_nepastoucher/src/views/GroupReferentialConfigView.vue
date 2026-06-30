<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/client'
import ReferentialExplorerModal from '../components/referential/ReferentialExplorerModal.vue'

const route = useRoute()
const groupId = computed(() => route.params.groupId)
const referentials = ref([])
const selectedRefId = ref('')
const currentConfig = ref(null)
const activitySummary = ref([])
const loading = ref({ refs: true, config: true, saving: false })
const error = ref('')
const success = ref('')
const explorerOpen = ref(false)
const explorerRefId = ref('')
const explorerRefName = ref('')

const previewReferentialId = computed(() => selectedRefId.value || currentConfig.value?.referential?.id || '')
const previewReferentialName = computed(() => {
  const id = previewReferentialId.value
  if (!id) return ''
  const fromList = referentials.value.find((r) => r.id === id)
  if (fromList?.name) return fromList.name
  return currentConfig.value?.referential?.name || ''
})

function openReferentialExplorer() {
  if (!previewReferentialId.value) return
  explorerRefId.value = previewReferentialId.value
  explorerRefName.value = previewReferentialName.value
  explorerOpen.value = true
}

async function loadReferentials() {
  loading.value.refs = true
  try {
    const { data } = await api.get('/referentials/')
    referentials.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors du chargement des référentiels.'
  } finally {
    loading.value.refs = false
  }
}

async function loadConfig() {
  loading.value.config = true
  try {
    const { data } = await api.get(`/groups/${groupId.value}/referential-config/`)
    currentConfig.value = data && data.referential ? data : null
    if (currentConfig.value?.referential?.id) {
      selectedRefId.value = currentConfig.value.referential.id
      await loadActivitySummary(currentConfig.value.referential.id)
    } else {
      activitySummary.value = []
    }
  } catch (e) {
    // En cas d'erreur inattendue, on affiche le message mais on ne bloque pas l'écran
    error.value = e.response?.data?.detail || 'Erreur chargement configuration.'
  } finally {
    loading.value.config = false
  }
}

async function loadActivitySummary(refId) {
  activitySummary.value = []
  if (!refId) return
  try {
    const { data: activitiesData } = await api.get(`/referentials/${refId}/activities/`)
    const activities = Array.isArray(activitiesData) ? activitiesData : (activitiesData.results || [])
    const enriched = []
    for (const a of activities) {
      const { data: tasksData } = await api.get(`/referentials/${refId}/activities/${a.id}/tasks/`)
      const tasks = Array.isArray(tasksData) ? tasksData : (tasksData.results || [])
      enriched.push({
        ...a,
        tasks: tasks.slice(0, 4),
      })
    }
    activitySummary.value = enriched
  } catch {
    activitySummary.value = []
  }
}

async function save() {
  error.value = ''
  success.value = ''
  if (!selectedRefId.value) {
    error.value = 'Sélectionnez un référentiel.'
    return
  }
  loading.value.saving = true
  try {
    await api.put(`/groups/${groupId.value}/referential-config/`, { referential_id: selectedRefId.value })
    success.value = 'Référentiel associé au groupe.'
    await loadConfig()
    await loadActivitySummary(selectedRefId.value)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors de l’association.'
  } finally {
    loading.value.saving = false
  }
}

const groupName = ref('')

async function loadGroupName() {
  if (!groupId.value) return
  try {
    const { data } = await api.get(`/groups/${groupId.value}/`)
    groupName.value = data.name || ''
  } catch {
    groupName.value = ''
  }
}

onMounted(async () => {
  await Promise.all([loadReferentials(), loadConfig(), loadGroupName()])
})
</script>

<template>
  <div class="container-fluid">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item"><router-link to="/dashboard">Tableau de bord</router-link></li>
        <li class="breadcrumb-item"><router-link to="/groups-admin">Groupes</router-link></li>
        <li class="breadcrumb-item">
          <router-link :to="{ name: 'GroupAdminDetail', params: { groupId } }">
            {{ groupName || 'Groupe' }}
          </router-link>
        </li>
        <li class="breadcrumb-item active" aria-current="page">Référentiel</li>
      </ol>
    </nav>

    <h1 class="h4 mb-4">Référentiel associé au groupe</h1>

    <div class="row">
      <div class="col-12 col-lg-6">
        <div class="card mb-3">
          <div class="card-header">Sélection du référentiel</div>
          <div class="card-body">
            <div class="mb-3">
              <label class="form-label" for="ref-select">Référentiel</label>
              <select
                id="ref-select"
                v-model="selectedRefId"
                class="form-select"
                :disabled="loading.refs || loading.saving"
              >
                <option value="">— Choisir un référentiel —</option>
                <option v-for="r in referentials" :key="r.id" :value="r.id">
                  {{ r.name }} <span v-if="r.source_ref">({{ r.source_ref }})</span>
                </option>
              </select>
            </div>
            <div class="d-flex flex-wrap gap-2">
              <button
                type="button"
                class="btn btn-primary"
                :disabled="loading.refs || loading.saving || !selectedRefId"
                @click="save"
              >
                {{ loading.saving ? 'Enregistrement…' : 'Associer au groupe' }}
              </button>
              <button
                type="button"
                class="btn btn-outline-secondary"
                :disabled="loading.refs || !previewReferentialId"
                title="Blocs, compétences et critères"
                @click="openReferentialExplorer"
              >
                <i class="bi bi-diagram-3 me-1"></i>
                Voir le référentiel
              </button>
            </div>
          </div>
        </div>
      </div>
      <div class="col-12 col-lg-6">
        <div v-if="loading.refs || loading.config" class="d-flex justify-content-center py-4">
          <div class="spinner-border text-primary"></div>
        </div>
        <div v-else>
          <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
          <div v-if="success" class="alert alert-success" role="alert">{{ success }}</div>
          <div class="card" v-if="currentConfig">
            <div class="card-header">Configuration actuelle</div>
            <div class="card-body">
              <p class="mb-1"><strong>Référentiel :</strong> {{ currentConfig.referential.name }}</p>
              <p v-if="currentConfig.referential.source_ref" class="mb-1">
                <strong>Code source :</strong> <code>{{ currentConfig.referential.source_ref }}</code>
              </p>
              <div class="mt-3" v-if="activitySummary.length">
                <p class="mb-1"><strong>Résumé activités / tâches</strong></p>
                <ul class="small mb-0">
                  <li v-for="a in activitySummary" :key="a.id">
                    <strong>{{ a.code }}</strong> — {{ a.label }} ({{ a.tasks_count ?? a.tasks?.length ?? 0 }} tâches)
                    <ul>
                      <li v-for="t in a.tasks" :key="t.id">
                        {{ t.code }} — {{ t.label }}
                      </li>
                    </ul>
                  </li>
                </ul>
              </div>
            </div>
          </div>
          <p v-else class="text-muted">Aucun référentiel n’est encore associé à ce groupe.</p>
        </div>
      </div>
    </div>

    <ReferentialExplorerModal
      v-model="explorerOpen"
      :referential-id="explorerRefId"
      :referential-name="explorerRefName"
    />
  </div>
</template>

