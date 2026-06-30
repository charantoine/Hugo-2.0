<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import TutorLearnerView from '../components/learner/TutorLearnerView.vue'

const route = useRoute()
const groupId = computed(() => route.params.groupId)
const learnerId = computed(() => route.params.learnerId)
</script>

<template>
  <div class="container-fluid px-0">
    <nav aria-label="breadcrumb" class="mb-3">
      <ol class="breadcrumb mb-0">
        <li class="breadcrumb-item"><router-link to="/app/tutor">Espace tuteur</router-link></li>
        <li class="breadcrumb-item">
          <router-link :to="{ name: 'ProdTutorGroup', params: { groupId } }">Groupe</router-link>
        </li>
        <li class="breadcrumb-item active">Apprenant</li>
      </ol>
    </nav>
    <TutorLearnerView :group-id="groupId" :learner-id="learnerId" />
  </div>
</template>
