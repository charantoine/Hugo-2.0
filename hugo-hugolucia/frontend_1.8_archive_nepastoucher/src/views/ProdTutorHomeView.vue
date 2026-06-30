<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/client'

const router = useRouter()
const groups = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const { data } = await api.get('/groups/')
    groups.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors du chargement des groupes.'
    groups.value = []
  } finally {
    loading.value = false
  }
})

function openGroup(group) {
  router.push({ name: 'ProdTutorGroup', params: { groupId: group.id } })
}
</script>

<template>
  <div class="container-fluid px-0">
    <header class="mb-4">
      <h1 class="h4 mb-1">Espace tuteur</h1>
      <p class="text-muted mb-0 small">
        Progression et traces partageables — sans verbatim non partagé.
      </p>
    </header>

    <div v-if="loading" class="d-flex justify-content-center py-5">
      <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Chargement…</span></div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else-if="groups.length" class="row g-3">
      <div v-for="g in groups" :key="g.id" class="col-12 col-md-6">
        <div class="card shadow-sm h-100">
          <div class="card-body d-flex align-items-center justify-content-between">
            <span class="fw-medium">{{ g.name }}</span>
            <button type="button" class="btn btn-outline-primary btn-sm" @click="openGroup(g)">
              Voir les apprenants
            </button>
          </div>
        </div>
      </div>
    </div>
    <p v-else class="text-muted">Aucun groupe accessible.</p>
  </div>
</template>
