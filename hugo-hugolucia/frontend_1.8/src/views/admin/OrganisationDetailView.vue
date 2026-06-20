<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../api/client'
import { useTenantStore } from '../../stores/tenant'

const route = useRoute()
const router = useRouter()
const tenant = useTenantStore()

const organisation = ref(null)
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const saveError = ref('')
const saveMsg = ref('')

const editName = ref('')
const editProfile = ref('professional')

const orgId = computed(() => route.params.orgId)

async function loadOrganisation() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get(`/admin/organisations/${orgId.value}/`)
    organisation.value = data
    editName.value = data.name
    editProfile.value = data.default_learner_display_profile || 'professional'
    tenant.setActiveOrganisation(data)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Organisation introuvable.'
    organisation.value = null
  } finally {
    loading.value = false
  }
}

async function saveOrganisation() {
  if (!organisation.value || saving.value) return
  saving.value = true
  saveError.value = ''
  saveMsg.value = ''
  try {
    const { data } = await api.patch(`/admin/organisations/${orgId.value}/`, {
      name: editName.value.trim(),
      default_learner_display_profile: editProfile.value,
    })
    organisation.value = data
    tenant.setActiveOrganisation(data)
    saveMsg.value = 'Organisation mise à jour.'
  } catch (e) {
    saveError.value = e.response?.data?.detail || 'Mise à jour impossible.'
  } finally {
    saving.value = false
  }
}

function goToUsers() {
  router.push('/users')
}

function goToGroups() {
  router.push('/groups-admin')
}

onMounted(loadOrganisation)
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h1 class="h4 mb-0">Organisation</h1>
      <router-link class="btn btn-outline-secondary btn-sm" to="/admin/organisations">
        Retour à la liste
      </router-link>
    </div>

    <p v-if="loading" class="text-muted">Chargement…</p>
    <p v-else-if="error" class="text-danger">{{ error }}</p>

    <template v-else-if="organisation">
      <div class="alert alert-info py-2">
        Contexte actif : <strong>{{ tenant.activeOrganisationName }}</strong>
        — les pages admin (utilisateurs, groupes, config.) opèrent dans cette organisation.
      </div>

      <div class="card mb-4">
        <div class="card-body">
          <h2 class="h6">Paramètres</h2>
          <div class="mb-3">
            <label class="form-label small">Nom</label>
            <input v-model="editName" class="form-control form-control-sm" type="text" />
          </div>
          <div class="mb-3">
            <label class="form-label small">Profil apprenant par défaut</label>
            <select v-model="editProfile" class="form-select form-select-sm">
              <option value="professional">Professionnel</option>
              <option value="adult">Adulte</option>
              <option value="youth">Jeune</option>
            </select>
          </div>
          <button class="btn btn-primary btn-sm" :disabled="saving" @click="saveOrganisation">
            {{ saving ? 'Enregistrement…' : 'Enregistrer' }}
          </button>
          <p v-if="saveMsg" class="text-success small mt-2 mb-0">{{ saveMsg }}</p>
          <p v-if="saveError" class="text-danger small mt-2 mb-0">{{ saveError }}</p>
        </div>
      </div>

      <div class="d-flex flex-wrap gap-2">
        <button class="btn btn-outline-primary btn-sm" @click="goToUsers">Utilisateurs</button>
        <button class="btn btn-outline-primary btn-sm" @click="goToGroups">Groupes</button>
        <router-link class="btn btn-outline-primary btn-sm" to="/admin/conversation">
          Config. conversation
        </router-link>
      </div>
    </template>
  </div>
</template>
