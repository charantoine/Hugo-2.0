<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/client'
import { useAuthStore } from '../stores/auth'
import { PLATFORM_VERSION_ADMIN_LINE } from '../utils/platformVersion.js'

const router = useRouter()
const auth = useAuthStore()
const groups = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await api.get('/groups/')
    groups.value = Array.isArray(data) ? data : (data.results || [])
  } catch {
    groups.value = []
  } finally {
    loading.value = false
  }
})

function openGroup(group) {
  router.push({ name: 'Group', params: { groupId: group.id } })
}
</script>

<template>
  <div class="container-fluid">
    <h1 class="h4 mb-4">Tableau de bord</h1>
    <p class="text-muted mb-4">Classes / groupes</p>
    <div v-if="loading" class="d-flex justify-content-center py-5">
      <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Chargement…</span></div>
    </div>
    <div v-else-if="groups.length" class="row g-3">
      <div v-for="g in groups" :key="g.id" class="col-12 col-md-6 col-lg-4">
        <div class="card h-100 shadow-sm">
          <div class="card-body d-flex align-items-center justify-content-between">
            <span class="fw-medium">{{ g.name }}</span>
            <button type="button" class="btn btn-outline-primary btn-sm" @click="openGroup(g)">
              Voir les apprenants <i class="bi bi-chevron-right"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
    <p v-else class="text-muted">Aucun groupe.</p>

    <aside v-if="auth.isAdminLike" class="mt-5 pt-3 border-top">
      <p class="small text-muted mb-0">{{ PLATFORM_VERSION_ADMIN_LINE }}</p>
    </aside>
  </div>
</template>
