<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ProdTrainerChatWorkspace from '../components/trainer/ProdTrainerChatWorkspace.vue'

const route = useRoute()
const sessionId = computed(() => String(route.params.sessionId || '').trim())
</script>

<template>
  <div class="learner-v2-session-shell">
    <ProdTrainerChatWorkspace :key="sessionId" :session-id="sessionId" />
  </div>
</template>
