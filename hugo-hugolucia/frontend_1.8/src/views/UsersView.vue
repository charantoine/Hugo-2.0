<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/client'

const role = ref('LEARNER')
const username = ref('')
const email = ref('')
const firstName = ref('')
const lastName = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')
const users = ref([])
const loadingUsers = ref(false)
const usersError = ref('')
const updatingUserId = ref('')

async function loadUsers() {
  loadingUsers.value = true
  usersError.value = ''
  try {
    const { data } = await api.get('/users/')
    // backend returns a list of users of the organisation
    users.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    usersError.value = e.response?.data?.detail || 'Erreur lors du chargement des utilisateurs.'
    users.value = []
  } finally {
    loadingUsers.value = false
  }
}

async function submit() {
  if (loading.value) return
  error.value = ''
  success.value = ''

  if (!username.value || !email.value || !firstName.value || !lastName.value || !password.value) {
    error.value = 'Veuillez renseigner identifiant, email, prénom, nom et mot de passe.'
    return
  }

  loading.value = true
  try {
    await api.post('/users/', {
      username: username.value,
      email: email.value,
      first_name: firstName.value,
      last_name: lastName.value,
      password: password.value,
      role: role.value,
    })
    success.value = role.value === 'TUTOR' ? 'Compte tuteur créé.' : 'Compte apprenant créé.'
    username.value = ''
    email.value = ''
    firstName.value = ''
    lastName.value = ''
    password.value = ''
    role.value = 'LEARNER'
    await loadUsers()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors de la création du compte.'
  } finally {
    loading.value = false
  }
}

async function toggleUserActive(user) {
  if (!user?.id || updatingUserId.value) return
  updatingUserId.value = user.id
  usersError.value = ''
  try {
    await api.patch(`/users/${user.id}/`, {
      is_active: !user.is_active,
      role: user.role,
      email: user.email,
      first_name: user.first_name,
      last_name: user.last_name,
    })
    await loadUsers()
  } catch (e) {
    usersError.value = e.response?.data?.detail || 'Erreur lors de la mise à jour du compte.'
  } finally {
    updatingUserId.value = ''
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<template>
  <div class="container-fluid">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item">
          <router-link to="/dashboard">Tableau de bord</router-link>
        </li>
        <li class="breadcrumb-item active" aria-current="page">Utilisateurs</li>
      </ol>
    </nav>

    <h1 class="h4 mb-4">Création de comptes</h1>
    <p class="text-muted mb-4">
      Créez ici des comptes <strong>tuteur</strong> ou <strong>apprenant</strong>. Cette page est réservée aux profils
      administrateur.
    </p>

    <div class="row">
      <div class="col-12 col-lg-6 mb-4">
        <div class="card shadow-sm">
          <div class="card-body">
            <h2 class="h5 mb-3">Nouveau compte</h2>

            <div v-if="error" class="alert alert-danger" role="alert">
              {{ error }}
            </div>
            <div v-if="success" class="alert alert-success" role="alert">
              {{ success }}
            </div>

            <form @submit.prevent="submit">
              <div class="mb-3">
                <label for="role" class="form-label">Type de compte</label>
                <select
                  id="role"
                  v-model="role"
                  class="form-select"
                  :disabled="loading"
                >
                  <option value="LEARNER">Apprenant</option>
                  <option value="TUTOR">Tuteur</option>
                </select>
              </div>

              <div class="mb-3">
                <label for="username" class="form-label">Identifiant</label>
                <input
                  id="username"
                  v-model="username"
                  type="text"
                  class="form-control"
                  autocomplete="off"
                  :disabled="loading"
                  required
                />
              </div>

              <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input
                  id="email"
                  v-model="email"
                  type="email"
                  class="form-control"
                  autocomplete="off"
                  :disabled="loading"
                  required
                />
              </div>

              <div class="row g-2">
                <div class="col-12 col-md-6 mb-3">
                  <label for="first_name" class="form-label">Prénom</label>
                  <input
                    id="first_name"
                    v-model="firstName"
                    type="text"
                    class="form-control"
                    autocomplete="off"
                    :disabled="loading"
                    required
                  />
                </div>
                <div class="col-12 col-md-6 mb-3">
                  <label for="last_name" class="form-label">Nom</label>
                  <input
                    id="last_name"
                    v-model="lastName"
                    type="text"
                    class="form-control"
                    autocomplete="off"
                    :disabled="loading"
                    required
                  />
                </div>
              </div>

              <div class="mb-3">
                <label for="password" class="form-label">Mot de passe</label>
                <input
                  id="password"
                  v-model="password"
                  type="password"
                  class="form-control"
                  autocomplete="new-password"
                  :disabled="loading"
                  required
                />
              </div>

              <button
                type="submit"
                class="btn btn-primary"
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
                {{ role === 'TUTOR' ? 'Créer le tuteur' : 'Créer l’apprenant' }}
              </button>
            </form>
          </div>
        </div>
      </div>
      <div class="col-12 col-lg-6">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h2 class="h5 mb-3">Utilisateurs de l’organisation</h2>
            <p class="text-muted small mb-3">
              Liste des comptes rattachés à la même organisation (rôle en suffixe).
            </p>

            <div v-if="loadingUsers" class="text-center py-3">
              <div class="spinner-border spinner-border-sm text-primary" role="status">
                <span class="visually-hidden">Chargement…</span>
              </div>
            </div>
            <div v-else-if="usersError" class="alert alert-danger" role="alert">
              {{ usersError }}
            </div>
            <ul v-else-if="users.length" class="list-group list-group-flush">
              <li
                v-for="u in users"
                :key="u.id"
                class="list-group-item d-flex justify-content-between align-items-center gap-3"
              >
                <div>
                  <router-link :to="{ name: 'UserDetail', params: { userId: u.id } }">
                    {{ [u.first_name, u.last_name].filter(Boolean).join(' ') || u.username || u.email }}
                  </router-link>
                  <span v-if="u.email && u.username" class="text-muted small">({{ u.email }})</span>
                </div>
                <div class="d-flex align-items-center gap-2">
                  <span class="badge bg-light text-muted text-uppercase">
                    {{ u.role }}
                  </span>
                  <span class="badge" :class="u.is_active ? 'text-bg-success' : 'text-bg-secondary'">
                    {{ u.is_active ? 'Actif' : 'Désactivé' }}
                  </span>
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-secondary"
                    :disabled="updatingUserId === u.id"
                    @click="toggleUserActive(u)"
                  >
                    {{ updatingUserId === u.id ? '...' : (u.is_active ? 'Désactiver' : 'Réactiver') }}
                  </button>
                </div>
              </li>
            </ul>
            <p v-else class="text-muted small mb-0">
              Aucun utilisateur dans cette organisation.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

