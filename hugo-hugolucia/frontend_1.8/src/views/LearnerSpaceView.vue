<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LearnerDetailView from '../components/learner/LearnerDetailView.vue'
import TutorLearnerView from '../components/learner/TutorLearnerView.vue'

const route = useRoute()
const auth = useAuthStore()
const learnerId = computed(() => route.params.learnerId)
const groupId = computed(() => route.params.groupId)
const isOwnSpace = computed(() => auth.user && String(auth.user.id) === String(learnerId.value))
</script>

<template>
  <div class="container-fluid">
    <LearnerDetailView v-if="isOwnSpace" :group-id="groupId" />
    <TutorLearnerView v-else :group-id="groupId" :learner-id="learnerId" />
  </div>
</template>
