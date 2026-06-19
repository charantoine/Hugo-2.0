<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/client'

const router = useRouter()

const items = ref([])
const loading = ref(true)
const error = ref('')
const success = ref('')
const actionItemId = ref(null)
const statusFilter = ref('')
const rejectReason = ref('')
const rejectTargetId = ref(null)
const editContent = ref('')
const editTargetId = ref(null)

const STATUS_LABELS = {
  declared: 'Déclaré',
  derived_provisional: 'Provisoire',
  validated_trainer: 'Validé formateur',
}

const CONTENT_TYPE_LABELS = {
  mastery_criterion: 'Critère de maîtrise',
  frequent_error: 'Erreur fréquente',
  reasoning_chain: 'Chaîne de raisonnement',
  reference_rule: 'Règle de référence',
  procedure: 'Procédure',
}

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' })
}

function statusLabel(status) {
  return STATUS_LABELS[status] || status
}

function contentTypeLabel(type) {
  return CONTENT_TYPE_LABELS[type] || type
}

async function loadItems() {
  loading.value = true
  error.value = ''
  try {
    const params = statusFilter.value ? { status: statusFilter.value } : {}
    const { data } = await api.get('/hugo/trainer/knowledge-items/', { params })
    items.value = data.items || []
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur chargement des items.'
    items.value = []
  } finally {
    loading.value = false
  }
}

async function runAction(itemId, action, payload = {}) {
  actionItemId.value = itemId
  success.value = ''
  error.value = ''
  try {
    await api.post(`/hugo/trainer/knowledge-items/${itemId}/validate/`, { action, ...payload })
    success.value = 'Action enregistrée.'
    rejectTargetId.value = null
    editTargetId.value = null
    await loadItems()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Action impossible.'
  } finally {
    actionItemId.value = null
  }
}

function openReject(item) {
  rejectTargetId.value = item.id
  rejectReason.value = ''
}

function openEdit(item) {
  editTargetId.value = item.id
  editContent.value = item.content
}

function goToElicitation() {
  router.push({ name: 'ProdTrainerElicitation' })
}

onMounted(loadItems)
</script>

<template>
  <div class="container-fluid px-0">
    <header class="mb-4 d-flex flex-column flex-lg-row justify-content-between gap-3">
      <div>
        <h1 class="h4 mb-1">Orchestrateur de connaissance</h1>
        <p class="text-muted mb-0 small">
          Savoirs métier gouvernés — validation humaine obligatoire avant exploitation moteur.
        </p>
      </div>
      <div class="d-flex flex-wrap gap-2">
        <button type="button" class="btn btn-sm btn-primary" @click="goToElicitation">
          Atelier d’élicitation
        </button>
        <button type="button" class="btn btn-sm btn-outline-secondary" @click="loadItems">
          Rafraîchir
        </button>
      </div>
    </header>

    <div class="row g-2 align-items-end mb-3">
      <div class="col-auto">
        <label class="form-label small mb-1">Filtrer par statut</label>
        <select v-model="statusFilter" class="form-select form-select-sm" @change="loadItems">
          <option value="">Tous</option>
          <option value="declared">Déclaré</option>
          <option value="derived_provisional">Provisoire</option>
          <option value="validated_trainer">Validé</option>
        </select>
      </div>
    </div>

    <p v-if="success" class="text-success small">{{ success }}</p>
    <p v-if="error" class="text-danger small">{{ error }}</p>

    <div v-if="loading" class="d-flex justify-content-center py-5">
      <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Chargement…</span></div>
    </div>

    <div v-else-if="items.length" class="table-responsive">
      <table class="table table-sm align-middle">
        <thead>
          <tr>
            <th>Titre / contenu</th>
            <th>Type</th>
            <th>Statut</th>
            <th>Mis à jour</th>
            <th>Validé par</th>
            <th>Usage</th>
            <th class="text-end">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td>
              <div class="small text-muted mb-1" v-if="item.referential_item_id">
                Réf. {{ item.referential_item_id }}
              </div>
              <div>{{ item.content }}</div>
              <div v-if="item.provenance_note" class="small text-muted mt-1">{{ item.provenance_note }}</div>
            </td>
            <td>{{ contentTypeLabel(item.content_type) }}</td>
            <td><span class="badge bg-light text-dark border">{{ statusLabel(item.status) }}</span></td>
            <td class="small">{{ formatDate(item.updated_at) }}</td>
            <td class="small">{{ item.validated_by || '—' }}</td>
            <td class="small">
              <span :class="item.usage_stats?.exploitable ? 'text-success' : 'text-muted'">
                {{ item.usage_stats?.usage_note || '—' }}
              </span>
            </td>
            <td class="text-end">
              <div class="d-flex flex-wrap gap-1 justify-content-end">
                <button
                  v-if="item.status !== 'validated_trainer'"
                  type="button"
                  class="btn btn-sm btn-primary"
                  :disabled="actionItemId === item.id"
                  @click="runAction(item.id, 'validate')"
                >
                  Valider
                </button>
                <button
                  v-if="item.status === 'declared'"
                  type="button"
                  class="btn btn-sm btn-outline-secondary"
                  :disabled="actionItemId === item.id"
                  @click="runAction(item.id, 'mark_provisional')"
                >
                  Provisoire
                </button>
                <button
                  v-if="item.status !== 'validated_trainer'"
                  type="button"
                  class="btn btn-sm btn-outline-warning"
                  @click="openEdit(item)"
                >
                  Éditer
                </button>
                <button
                  type="button"
                  class="btn btn-sm btn-outline-danger"
                  @click="openReject(item)"
                >
                  Rejeter
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-else class="text-muted">Aucun item de connaissance pour le moment.</p>

    <div v-if="rejectTargetId" class="card mt-4">
      <div class="card-body">
        <h2 class="h6">Motif de rejet</h2>
        <textarea v-model="rejectReason" class="form-control form-control-sm mb-2" rows="3" placeholder="Expliquez brièvement le motif…" />
        <div class="d-flex gap-2">
          <button
            type="button"
            class="btn btn-sm btn-danger"
            :disabled="actionItemId === rejectTargetId"
            @click="runAction(rejectTargetId, 'reject', { reason: rejectReason })"
          >
            Confirmer le rejet
          </button>
          <button type="button" class="btn btn-sm btn-outline-secondary" @click="rejectTargetId = null">
            Annuler
          </button>
        </div>
      </div>
    </div>

    <div v-if="editTargetId" class="card mt-4">
      <div class="card-body">
        <h2 class="h6">Édition avant validation</h2>
        <textarea v-model="editContent" class="form-control form-control-sm mb-2" rows="4" />
        <div class="d-flex gap-2">
          <button
            type="button"
            class="btn btn-sm btn-primary"
            :disabled="actionItemId === editTargetId"
            @click="runAction(editTargetId, 'edit', { content: editContent })"
          >
            Valider avec ce contenu
          </button>
          <button type="button" class="btn btn-sm btn-outline-secondary" @click="editTargetId = null">
            Annuler
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
