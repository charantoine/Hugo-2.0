<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../api/client'
import ReferentialExplorerModal from '../components/referential/ReferentialExplorerModal.vue'
import TrainerGroupContextPanel from '../components/trainer/TrainerGroupContextPanel.vue'
import TrainerBackToOrchestratorLink from '../components/trainer/TrainerBackToOrchestratorLink.vue'

const router = useRouter()
const route = useRoute()
const referentials = ref([])
const loading = ref(true)
const error = ref('')
const explorerOpen = ref(false)
const explorerRefId = ref('')
const explorerRefName = ref('')

const inTrainerShell = computed(() => route.meta.trainerShell === true || route.path.startsWith('/app/trainer/referentials'))
const homeRoute = computed(() => (
  inTrainerShell.value
    ? { name: 'ProdTrainerKnowledge' }
    : { path: '/dashboard' }
))
const importRouteName = computed(() => (
  inTrainerShell.value ? 'ProdTrainerReferentialImport' : 'ReferentialImport'
))

onMounted(async () => {
  try {
    const { data } = await api.get('/referentials/')
    referentials.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors du chargement des référentiels.'
  } finally {
    loading.value = false
  }
})

function goImport() {
  router.push({ name: importRouteName.value })
}

function openExplorer(r) {
  explorerRefId.value = r.id
  explorerRefName.value = r.name || ''
  explorerOpen.value = true
}
</script>

<template>
  <div class="container-fluid">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item">
          <router-link :to="homeRoute">
            {{ inTrainerShell ? 'Espace formateur' : 'Tableau de bord' }}
          </router-link>
        </li>
        <li class="breadcrumb-item active" aria-current="page">Référentiels</li>
      </ol>
    </nav>

    <TrainerGroupContextPanel v-if="inTrainerShell" compact />

    <div class="d-flex flex-wrap justify-content-between align-items-center mb-3 gap-2">
      <h1 class="h4 mb-0">Référentiels</h1>
      <div class="d-flex flex-wrap gap-2">
        <TrainerBackToOrchestratorLink v-if="inTrainerShell" />
        <button type="button" class="btn btn-primary btn-sm" @click="goImport">
          <i class="bi bi-plus-lg me-1"></i>
          Importer un référentiel
        </button>
      </div>
    </div>

    <div v-if="loading" class="d-flex justify-content-center py-5">
      <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Chargement…</span></div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else-if="referentials.length" class="table-responsive">
      <table class="table table-sm align-middle">
        <thead>
          <tr>
            <th>Nom</th>
            <th>Code source</th>
            <th>Items</th>
            <th>Activités</th>
            <th>Tâches</th>
            <th>Créé le</th>
            <th class="text-end">Détail</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in referentials" :key="r.id">
            <td>{{ r.name }}</td>
            <td><code v-if="r.source_ref">{{ r.source_ref }}</code></td>
            <td>{{ r.items_count }}</td>
            <td>{{ r.activities_count ?? 0 }}</td>
            <td>{{ r.tasks_count ?? 0 }}</td>
            <td>{{ new Date(r.created_at).toLocaleDateString('fr-FR') }}</td>
            <td class="text-end">
              <button
                type="button"
                class="btn btn-sm btn-outline-primary"
                title="Blocs, compétences et critères"
                @click="openExplorer(r)"
              >
                <i class="bi bi-diagram-3 me-1"></i>
                Voir
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else class="text-muted">Aucun référentiel importé pour l’instant.</p>

    <ReferentialExplorerModal
      v-model="explorerOpen"
      :referential-id="explorerRefId"
      :referential-name="explorerRefName"
    />
  </div>
</template>

