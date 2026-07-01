<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ProdLearnerWorkspace from '../components/learner/ProdLearnerWorkspace.vue'
import { useAuthStore } from '../stores/auth'
import { frontendFeatures } from '../utils/frontendConfig'
import { isPureTrainerPersona } from '../utils/trainerUiLabels'
import { isPureTutorPersona } from '../utils/tutorUiLabels'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const sessionId = computed(() => String(route.params.sessionId || '').trim())
const learnerUiV2 = frontendFeatures.learner_ui_v2

function redirectPersonaIfNeeded() {
  const sid = sessionId.value
  if (!sid || !auth.user) return false

  if (route.query.tutor_ctx === '1' && isPureTutorPersona(auth.user)) {
    router.replace({
      name: 'ProdTutorChatSession',
      params: { sessionId: sid },
      query: { ...route.query },
    })
    return true
  }

  if (isPureTrainerPersona(auth.user)) {
    router.replace({
      name: 'ProdTrainerChatSession',
      params: { sessionId: sid },
    })
    return true
  }

  return false
}

onMounted(() => {
  redirectPersonaIfNeeded()
})

watch(sessionId, () => {
  redirectPersonaIfNeeded()
})
</script>

<template>
  <div :class="learnerUiV2 ? 'learner-v2-session-shell' : 'container-xxl py-3 py-lg-4'">
    <ProdLearnerWorkspace :session-id="sessionId" />
  </div>
</template>
