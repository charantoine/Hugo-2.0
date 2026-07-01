<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ProdTutorChatWorkspace from '../components/tutor/ProdTutorChatWorkspace.vue'

const route = useRoute()
const sessionId = computed(() => String(route.params.sessionId || '').trim())
</script>

<template>
  <div class="learner-v2-session-shell">
    <ProdTutorChatWorkspace :key="sessionId" :session-id="sessionId" />
  </div>
</template>
