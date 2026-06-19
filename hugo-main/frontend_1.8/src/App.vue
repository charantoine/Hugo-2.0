<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ProdLearnerLayout from './layouts/ProdLearnerLayout.vue'
import TesterLayout from './layouts/TesterLayout.vue'

const route = useRoute()

const activeLayout = computed(() => (
  route.meta.layout === 'tester' ? TesterLayout : ProdLearnerLayout
))
</script>

<template>
  <component :is="activeLayout">
    <router-view />
  </component>
</template>
