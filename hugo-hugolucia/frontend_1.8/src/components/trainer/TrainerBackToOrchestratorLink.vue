<script setup>
import {
  TRAINER_BACK_TO_ORCHESTRATOR_LABEL,
  TRAINER_ORCHESTRATOR_ROUTE_NAME,
} from '../../utils/trainerNavigation.js'

defineProps({
  extraClass: { type: String, default: '' },
})
</script>

<template>
  <router-link
    class="btn btn-sm btn-outline-secondary"
    :class="extraClass"
    :to="{ name: TRAINER_ORCHESTRATOR_ROUTE_NAME }"
  >
    {{ TRAINER_BACK_TO_ORCHESTRATOR_LABEL }}
  </router-link>
</template>
