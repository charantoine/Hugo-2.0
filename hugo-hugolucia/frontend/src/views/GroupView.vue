<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api, { runExportAndDownload } from '../api/client'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const groupId = computed(() => route.params.groupId)
const groupName = ref('')
const learners = ref([])
const loading = ref(true)
const error = ref('')
const exportPeriodFrom = ref('')
const exportPeriodTo = ref('')
const exportingCsv = ref(false)
const exportingJson = ref(false)
const exportError = ref('')
const exportSuccess = ref('')
const canRunExports = computed(() => {
  const role = String(auth.user?.role || auth.user?.user_role || '').toUpperCase()
  return auth.isAdminLike || ['ORGADMIN', 'SUPERADMIN', 'TUTOR', 'TRAINER', 'COORDO'].includes(role)
})

onMounted(async () => {
  try {
    // Endpoint /groups/{id}/ is admin-only; learners can still resolve the
    // group name from the list endpoint they are allowed to access.
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
  router.push({ name: 'LearnerSpace', params: { groupId: groupId.value, learnerId: learner.id } })
}

function isMe(learner) {
  return auth.user && String(auth.user.id) === String(learner.id)
}

function openConfig() {
  router.push({ name: 'GroupReferentialConfig', params: { groupId: groupId.value } })
}

function buildExportPayload(format) {
  const period = {}
  if (exportPeriodFrom.value) period.from = exportPeriodFrom.value
  if (exportPeriodTo.value) period.to = exportPeriodTo.value

  const payload = {
    format,
    group_ids: [String(groupId.value)],
  }
  if (Object.keys(period).length) payload.period = period
  if (format === 'csv') {
    payload.separator = ';'
    payload.include_bom = true
  }
  return payload
}

async function runGroupExport(format) {
  if (!canRunExports.value) return
  const isCsv = format === 'csv'
  if (isCsv && exportingCsv.value) return
  if (!isCsv && exportingJson.value) return
  exportError.value = ''
  exportSuccess.value = ''
  if (isCsv) exportingCsv.value = true
  else exportingJson.value = true

  try {
    const payload = buildExportPayload(format)
    await runExportAndDownload({ format, payload })
    exportSuccess.value = `Export ${isCsv ? 'CSV principal' : 'JSON trace_rich_v1'} téléchargé.`
  } catch (e) {
    exportError.value = e.response?.data?.detail || e.message || "Erreur lors de l'export."
  } finally {
    if (isCsv) exportingCsv.value = false
    else exportingJson.value = false
  }
}
</script>

<template>
  <div class="container-fluid">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item"><router-link to="/dashboard">Tableau de bord</router-link></li>
        <li class="breadcrumb-item active" aria-current="page">
          {{ groupName || 'Groupe' }}
        </li>
      </ol>
    </nav>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="h4 mb-0">Apprenants du groupe {{ groupName || '...' }}</h1>
      <div class="d-flex gap-2">
        <button
          v-if="canRunExports"
          type="button"
          class="btn btn-sm btn-outline-primary"
          :disabled="exportingCsv || exportingJson"
          @click="runGroupExport('csv')"
        >
          {{ exportingCsv ? 'Export CSV…' : 'CSV principal (Felix-ready)' }}
        </button>
        <button
          v-if="canRunExports"
          type="button"
          class="btn btn-sm btn-outline-secondary"
          :disabled="exportingCsv || exportingJson"
          @click="runGroupExport('json')"
        >
          {{ exportingJson ? 'Export JSON…' : 'JSON trace_rich_v1' }}
        </button>
        <button type="button" class="btn btn-sm btn-outline-secondary" @click="openConfig">
          Configurer le référentiel
        </button>
      </div>
    </div>
    <div v-if="canRunExports" class="card shadow-sm mb-3">
      <div class="card-body">
        <p class="small fw-bold mb-2">Exports Felix-ready (v1)</p>
        <div class="row g-2">
          <div class="col-12 col-md-3">
            <label class="form-label small mb-1">Période - du</label>
            <input v-model="exportPeriodFrom" type="date" class="form-control form-control-sm" />
          </div>
          <div class="col-12 col-md-3">
            <label class="form-label small mb-1">au</label>
            <input v-model="exportPeriodTo" type="date" class="form-control form-control-sm" />
          </div>
        </div>
        <p class="text-muted small mb-0 mt-2">
          CSV principal : 1 ligne = trace × item. JSON : payload `trace_rich_v1`.
        </p>
        <p v-if="exportSuccess" class="text-success small mb-0 mt-1">{{ exportSuccess }}</p>
        <p v-if="exportError" class="text-danger small mb-0 mt-1">{{ exportError }}</p>
      </div>
    </div>
    <div v-if="loading" class="d-flex justify-content-center py-5">
      <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Chargement…</span></div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    <ul v-else class="list-group list-group-flush">
      <li v-for="learner in learners" :key="learner.id" class="list-group-item d-flex justify-content-between align-items-center">
        <span>{{ learner.username }} <span v-if="isMe(learner)" class="badge bg-secondary">Moi</span></span>
        <button type="button" class="btn btn-sm btn-outline-primary" @click="openLearner(learner)">
          {{ isMe(learner) ? 'Mon espace' : 'Voir' }}
        </button>
      </li>
    </ul>
    <p v-if="!loading && !error && learners.length === 0" class="text-muted">Aucun apprenant dans ce groupe.</p>
  </div>
</template>
