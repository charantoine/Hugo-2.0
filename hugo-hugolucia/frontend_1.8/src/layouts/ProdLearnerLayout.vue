<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { frontendFeatures, getGamificationProfileTheme } from '../utils/frontendConfig'
import { resolveChatNavLabel, isPureTutorPersona, resolveProdBrandSubtitle as resolveTutorBrandSubtitle } from '../utils/tutorUiLabels'
import { resolveProdBrandSubtitle, resolveTrainerChatNavLabel, isPureTrainerPersona } from '../utils/trainerUiLabels'
import { TRAINER_CHAT_PATH } from '../utils/trainerNavigation'
import PlatformVersionFooter from '../components/PlatformVersionFooter.vue'

const learnerUiV2 = frontendFeatures.learner_ui_v2

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const theme = computed(() => getGamificationProfileTheme(frontendFeatures.gamification_profile))
const showTopbar = computed(() => Boolean(auth.user) && !route.meta.public)
const chatNavLabel = computed(() => {
  if (isPureTutorPersona(auth.user)) return resolveChatNavLabel(auth.user)
  return resolveTrainerChatNavLabel(auth.user)
})
const chatNavHref = computed(() => {
  if (isPureTutorPersona(auth.user)) return '/app/tutor'
  if (isPureTrainerPersona(auth.user)) return TRAINER_CHAT_PATH
  return '/app'
})
const brandSubtitle = computed(() => {
  if (isPureTutorPersona(auth.user)) return resolveTutorBrandSubtitle(auth.user, route.path)
  return resolveProdBrandSubtitle(auth.user, route.path)
})

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
      learnerUiV2 ? 'prod-shell--learner-v2' : '',
    ]"
  >
    <div class="prod-shell__aurora prod-shell__aurora--one"></div>
    <div class="prod-shell__aurora prod-shell__aurora--two"></div>

    <header v-if="showTopbar" class="prod-topbar">
      <div class="prod-topbar__brand">
        <router-link class="prod-brand" to="/app">
          <span class="prod-brand__avatar">H</span>
          <span>
            <strong>Hugo - Lucia</strong>
            <small>{{ brandSubtitle }}</small>
          </span>
        </router-link>
      </div>

      <nav class="prod-topbar__nav">
        <router-link
          v-if="auth.isTutorLike"
          class="prod-topbar__link prod-topbar__link--subtle"
          to="/app/tutor"
        >
          Espace tuteur
        </router-link>
        <router-link
          v-if="auth.isTrainerLike"
          class="prod-topbar__link prod-topbar__link--subtle"
          to="/app/trainer/knowledge"
        >
          Espace formateur
        </router-link>
        <router-link
          v-if="auth.isOrgAdminLike"
          class="prod-topbar__link prod-topbar__link--subtle"
          to="/dashboard"
        >
          Administration
        </router-link>
      </nav>

      <div class="prod-topbar__actions">
        <router-link
          class="prod-topbar__link prod-topbar__link--subtle prod-topbar__link--trailing"
          :to="chatNavHref"
        >
          {{ chatNavLabel }}
        </router-link>
        <div v-if="!learnerUiV2" class="prod-pill">
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

    <PlatformVersionFooter />
  </div>
</template>
