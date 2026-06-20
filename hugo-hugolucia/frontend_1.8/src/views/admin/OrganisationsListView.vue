<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api/client'
import { useAuthStore } from '../../stores/auth'
import { useTenantStore } from '../../stores/tenant'

const router = useRouter()
const auth = useAuthStore()
const tenant = useTenantStore()

const organisations = ref([])
const loading = ref(false)
const error = ref('')
const creating = ref(false)
const createError = ref('')
const newOrgName = ref('')
const newOrgProfile = ref('professional')

async function loadOrganisations() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/admin/organisations/')
    organisations.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    error.value = e.response?.data?.detail || 'Impossible de charger les organisations.'
    organisations.value = []
  } finally {
    loading.value = false
  }
}

async function createOrganisation() {
  if (!newOrgName.value.trim() || creating.value) return
  creating.value = true
  createError.value = ''
  try {
    const { data } = await api.post('/admin/organisations/', {
      name: newOrgName.value.trim(),
      default_learner_display_profile: newOrgProfile.value,
    })
    newOrgName.value = ''
    await loadOrganisations()
    if (auth.isSuperAdmin) {
      tenant.setActiveOrganisation(data)
    }
  } catch (e) {
    createError.value = e.response?.data?.detail || 'Création impossible.'
  } finally {
    creating.value = false
  }
}

function openOrganisation(org) {
  tenant.setActiveOrganisation(org)
  router.push(`/admin/organisations/${org.id}`)
}

onMounted(loadOrganisations)
</script>

<template>
  <div>
    <h1 class="h4 mb-3">Organisations</h1>
    <p v-if="auth.isSuperAdmin" class="text-muted">
      Vue multi-organisation réservée au SUPERADMIN. Sélectionnez une organisation pour gérer ses ressources.
    </p>
    <p v-else class="text-muted">
      Votre périmètre organisationnel. Vous pouvez créer une nouvelle organisation via cette interface.
    </p>

    <div class="card mb-4">
      <div class="card-body">
        <h2 class="h6">Créer une organisation</h2>
        <div class="row g-2 align-items-end">
          <div class="col-md-5">
            <label class="form-label small">Nom</label>
            <input v-model="newOrgName" class="form-control form-control-sm" type="text" />
          </div>
          <div class="col-md-4">
            <label class="form-label small">Profil apprenant par défaut</label>
            <select v-model="newOrgProfile" class="form-select form-select-sm">
              <option value="professional">Professionnel</option>
              <option value="adult">Adulte</option>
              <option value="youth">Jeune</option>
            </select>
          </div>
          <div class="col-md-3">
            <button class="btn btn-primary btn-sm w-100" :disabled="creating" @click="createOrganisation">
              {{ creating ? 'Création…' : 'Créer' }}
            </button>
          </div>
        </div>
        <p v-if="createError" class="text-danger small mt-2 mb-0">{{ createError }}</p>
      </div>
    </div>

    <p v-if="loading" class="text-muted">Chargement…</p>
    <p v-else-if="error" class="text-danger">{{ error }}</p>
    <div v-else class="table-responsive">
      <table class="table table-sm align-middle">
        <thead>
          <tr>
            <th>Nom</th>
            <th>Profil par défaut</th>
            <th v-if="auth.isSuperAdmin">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="org in organisations" :key="org.id">
            <td>{{ org.name }}</td>
            <td>{{ org.default_learner_display_profile }}</td>
            <td v-if="auth.isSuperAdmin">
              <button class="btn btn-outline-primary btn-sm" @click="openOrganisation(org)">
                Ouvrir
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="!organisations.length" class="text-muted mb-0">Aucune organisation.</p>
    </div>
  </div>
</template>
