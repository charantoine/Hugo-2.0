<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { frontendFeatures, getGamificationProfileTheme } from '../utils/frontendConfig'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const theme = computed(() => getGamificationProfileTheme(frontendFeatures.gamification_profile))
const showTopbar = computed(() => Boolean(auth.user) && !route.meta.public)

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div
    class="prod-shell"
    :class="[
      `prod-shell--profile-${theme.code.toLowerCase()}`,
      route.meta.public ? 'prod-shell--public' : 'prod-shell--private',
    ]"
  >
    <div class="prod-shell__aurora prod-shell__aurora--one"></div>
    <div class="prod-shell__aurora prod-shell__aurora--two"></div>

    <header v-if="showTopbar" class="prod-topbar">
      <div class="prod-topbar__brand">
        <router-link class="prod-brand" to="/app">
          <span class="prod-brand__avatar">H</span>
          <span>
            <strong>Hugo 1.8 - Lucia</strong>
            <small>Parcours apprenant</small>
          </span>
        </router-link>
      </div>

      <nav class="prod-topbar__nav">
        <router-link class="prod-topbar__link" to="/app">Mon espace</router-link>
        <router-link
          v-if="auth.isAdminLike"
          class="prod-topbar__link prod-topbar__link--subtle"
          to="/dashboard"
        >
          Vue testeur
        </router-link>
      </nav>

      <div class="prod-topbar__actions">
        <div class="prod-pill">
          <span class="prod-pill__label">{{ theme.label }}</span>
          <strong>{{ theme.title }}</strong>
        </div>
        <div class="prod-user">
          <span class="prod-user__name">{{ auth.user?.username }}</span>
          <small>{{ auth.user?.organisation_name }}</small>
        </div>
        <button type="button" class="btn btn-light btn-sm" @click="logout">Déconnexion</button>
      </div>
    </header>

    <main class="prod-main">
      <slot />
    </main>
  </div>
</template>
