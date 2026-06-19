<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api/client'

const route = useRoute()
const router = useRouter()
const groupId = computed(() => route.params.groupId)
const groupName = ref('')
const learners = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const { data: groupsData } = await api.get('/groups/')
    const groups = Array.isArray(groupsData) ? groupsData : (groupsData.results || [])
    const current = groups.find((g) => String(g.id) === String(groupId.value))
    groupName.value = current?.name || ''
  } catch {
    groupName.value = ''
  }

  try {
    const { data } = await api.get(`/dashboard/groups/${groupId.value}/learners/`)
    learners.value = data.learners || []
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur chargement'
  } finally {
    loading.value = false
  }
})

function openLearner(learner) {
  router.push({
    name: 'ProdTutorLearner',
    params: { groupId: groupId.value, learnerId: learner.id },
  })
}
</script>

<template>
  <div class="container-fluid px-0">
    <nav aria-label="breadcrumb" class="mb-3">
      <ol class="breadcrumb mb-0">
        <li class="breadcrumb-item"><router-link to="/app/tutor">Espace tuteur</router-link></li>
        <li class="breadcrumb-item active">{{ groupName || 'Groupe' }}</li>
      </ol>
    </nav>
    <h1 class="h5 mb-3">Apprenants — {{ groupName || '…' }}</h1>
    <div v-if="loading" class="d-flex justify-content-center py-4">
      <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Chargement…</span></div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    <ul v-else class="list-group list-group-flush">
      <li
        v-for="learner in learners"
        :key="learner.id"
        class="list-group-item d-flex justify-content-between align-items-center px-0"
      >
        <span>{{ learner.username }}</span>
        <button type="button" class="btn btn-sm btn-outline-primary" @click="openLearner(learner)">
          Timeline
        </button>
      </li>
    </ul>
    <p v-if="!loading && !error && learners.length === 0" class="text-muted">Aucun apprenant visible.</p>
  </div>
</template>
