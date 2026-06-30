<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { getDefaultAuthenticatedPath } from '../utils/frontendConfig'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const sessionExpired = computed(() => route.query.session === 'expired')
const nextPath = computed(() => (
  typeof route.query.redirect === 'string' && route.query.redirect
    ? route.query.redirect
    : getDefaultAuthenticatedPath()
))
const username = ref('')
const password = ref('')
const showPassword = ref(false)
const error = ref('')
const loading = ref(false)

async function onSubmit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push(nextPath.value)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Identifiants incorrects'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="container py-4 py-md-5">
    <div class="row align-items-center justify-content-center g-4">
      <div class="col-12 col-lg-5">
        <div class="prod-auth-copy">
          <span class="prod-auth-copy__eyebrow">POC Hugo Lucia</span>
          <h1 class="prod-auth-copy__title">Tuteur numérique</h1>
          <p class="prod-auth-copy__text d-none">
            Une interface plus claire, plus chaleureuse et pensée pour suivre ta progression sans afficher toute la mécanique interne.
          </p>
          <ul class="prod-auth-copy__list">
            <li>Une conversation simple avec Hugo</li>
            <li>Des quêtes courtes pour avancer pas à pas</li>
            <li>Des traces et acquis visibles au bon moment</li>
          </ul>
        </div>
      </div>

      <div class="col-12 col-md-8 col-lg-4">
        <div class="card shadow-lg border-0">
          <div class="card-body p-4 p-md-5">
            <h2 class="h4 card-title mb-2 text-center">Connexion</h2>
            <p class="text-muted text-center mb-4">Retrouve ton parcours et reprends là où tu t’es arrêté.</p>
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
                <div class="input-group">
                  <input
                    id="password"
                    v-model="password"
                    :type="showPassword ? 'text' : 'password'"
                    class="form-control"
                    placeholder="Mot de passe"
                    required
                    autocomplete="current-password"
                  />
                  <button
                    type="button"
                    class="btn btn-outline-secondary"
                    :aria-label="showPassword ? 'Masquer le mot de passe' : 'Afficher le mot de passe'"
                    :title="showPassword ? 'Masquer le mot de passe' : 'Afficher le mot de passe'"
                    @click="showPassword = !showPassword"
                  >
                    <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                  </button>
                </div>
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
