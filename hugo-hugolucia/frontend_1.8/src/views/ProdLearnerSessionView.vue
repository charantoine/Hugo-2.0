<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ProdLearnerWorkspace from '../components/learner/ProdLearnerWorkspace.vue'
import { frontendFeatures } from '../utils/frontendConfig'

const route = useRoute()
const sessionId = computed(() => String(route.params.sessionId || '').trim())
const learnerUiV2 = frontendFeatures.learner_ui_v2
</script>

<template>
  <div :class="learnerUiV2 ? 'learner-v2-session-shell' : 'container-xxl py-3 py-lg-4'">
    <ProdLearnerWorkspace :session-id="sessionId" />
  </div>
</template>
