<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ProdLearnerWorkspace from '../components/learner/ProdLearnerWorkspace.vue'

const route = useRoute()
const sessionId = computed(() => String(route.params.sessionId || '').trim())
</script>

<template>
  <div class="container-xxl py-3 py-lg-4">
    <ProdLearnerWorkspace :session-id="sessionId" />
  </div>
</template>
