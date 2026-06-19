<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/client'

const route = useRoute()
const user = ref(null)
const loading = ref(true)
const error = ref('')

const groups = ref([])
const loadingGroups = ref(false)
const groupsError = ref('')
const selectedGroupId = ref('')
const savingMembership = ref(false)
const membershipSuccess = ref('')

async function loadUser() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get(`/users/${route.params.userId}/`)
    user.value = data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors du chargement de l’utilisateur.'
  } finally {
    loading.value = false
  }
}

async function loadGroups() {
  loadingGroups.value = true
  groupsError.value = ''
  try {
    const { data } = await api.get('/groups/')
    groups.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    groupsError.value = e.response?.data?.detail || 'Erreur lors du chargement des groupes.'
    groups.value = []
  } finally {
    loadingGroups.value = false
  }
}

async function saveMembership() {
  if (!selectedGroupId.value || !user.value?.id || savingMembership.value) return
  membershipSuccess.value = ''
  groupsError.value = ''
  savingMembership.value = true
  try {
    await api.post(`/groups/${selectedGroupId.value}/members/`, {
      user: user.value.id,
    })
    membershipSuccess.value = 'Utilisateur associé au groupe.'
  } catch (e) {
    groupsError.value = e.response?.data?.detail || 'Erreur lors de l’association au groupe.'
  } finally {
    savingMembership.value = false
  }
}

onMounted(() => {
  loadUser()
  loadGroups()
})

watch(
  () => route.params.userId,
  () => {
    loadUser()
  },
)
</script>

<template>
  <div class="container-fluid">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item">
          <router-link to="/dashboard">Tableau de bord</router-link>
        </li>
        <li class="breadcrumb-item">
          <router-link to="/users">Utilisateurs</router-link>
        </li>
        <li class="breadcrumb-item active" aria-current="page">
          {{ [user?.first_name, user?.last_name].filter(Boolean).join(' ') || user?.username || 'Utilisateur' }}
        </li>
      </ol>
    </nav>

    <h1 class="h4 mb-4">Détail utilisateur</h1>

    <div v-if="loading" class="d-flex justify-content-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Chargement…</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>
    <div v-else-if="user" class="row">
      <div class="col-12 col-lg-4 mb-4">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h2 class="h5 mb-3">Profil</h2>
            <p><strong>Identifiant :</strong> {{ user.username }}</p>
            <p><strong>Email :</strong> {{ user.email || '—' }}</p>
            <p><strong>Prénom :</strong> {{ user.first_name || '—' }}</p>
            <p><strong>Nom :</strong> {{ user.last_name || '—' }}</p>
            <p>
              <strong>Rôle :</strong>
              <span class="badge bg-light text-muted text-uppercase">{{ user.role }}</span>
            </p>
            <p class="text-muted small mb-0">
              Utilisateur de la même organisation. Seuls les admins/superadmins peuvent modifier son rattachement aux
              groupes.
            </p>
          </div>
        </div>
      </div>
      <div class="col-12 col-lg-8 mb-4">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h2 class="h5 mb-3">Rattachement à un groupe</h2>

            <div v-if="groupsError" class="alert alert-danger" role="alert">
              {{ groupsError }}
            </div>
            <div v-if="membershipSuccess" class="alert alert-success" role="alert">
              {{ membershipSuccess }}
            </div>

            <div class="mb-3">
              <label for="group" class="form-label">Groupe</label>
              <select
                id="group"
                v-model="selectedGroupId"
                class="form-select"
                :disabled="loadingGroups || savingMembership"
              >
                <option value="">Sélectionner un groupe…</option>
                <option v-for="g in groups" :key="g.id" :value="g.id">
                  {{ g.name }}
                </option>
              </select>
            </div>

            <button
              type="button"
              class="btn btn-primary"
              :disabled="!selectedGroupId || savingMembership"
              @click="saveMembership"
            >
              <span
                v-if="savingMembership"
                class="spinner-border spinner-border-sm me-2"
                role="status"
                aria-hidden="true"
              />
              Associer l’utilisateur au groupe
            </button>

            <p class="text-muted small mt-3 mb-0">
              Pour le moment, un simple lien est créé entre l’utilisateur et le groupe (via les membres du groupe).
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

