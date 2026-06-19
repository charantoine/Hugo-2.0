<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const sessionExpired = computed(() => route.query.session === 'expired')
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function onSubmit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Identifiants incorrects'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-12 col-md-6 col-lg-4">
        <div class="card shadow">
          <div class="card-body p-4">
            <h1 class="h4 card-title mb-4 text-center">POC Hugo — Connexion</h1>
            <div v-if="sessionExpired" class="alert alert-warning mb-3" role="alert">
              Votre session a expiré. Merci de vous reconnecter.
            </div>
            <form @submit.prevent="onSubmit">
              <div class="mb-3">
                <label class="form-label" for="username">Identifiant</label>
                <input id="username" v-model="username" type="text" class="form-control" placeholder="Identifiant" required autocomplete="username" />
              </div>
              <div class="mb-3">
                <label class="form-label" for="password">Mot de passe</label>
                <input id="password" v-model="password" type="password" class="form-control" placeholder="Mot de passe" required autocomplete="current-password" />
              </div>
              <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                {{ loading ? 'Connexion…' : 'Se connecter' }}
              </button>
            </form>
            <div v-if="error" class="alert alert-danger mt-3 mb-0" role="alert">{{ error }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
