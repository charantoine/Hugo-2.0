<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import api from '../../api/client'
import ExpandableText from './ExpandableText.vue'

const props = defineProps({
  sessionId: {
    type: String,
    required: true,
  },
  displayProfile: {
    type: String,
    default: 'professional',
  },
})

const loading = ref(true)
const error = ref('')
const sessionMemory = ref(null)

const hasContent = computed(() => {
  const memory = sessionMemory.value
  if (!memory) return false
  return Boolean(
    memory.theme
    || memory.learning_objective
    || memory.facts_confirmed?.length
    || memory.open_points?.length
    || memory.pending_actions?.length,
  )
})

async function loadMemorySummary() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get(`/hugo/sessions/${props.sessionId}/memory-summary/`)
    sessionMemory.value = data?.session_memory || null
  } catch (err) {
    sessionMemory.value = null
    error.value = err.response?.data?.detail || 'Mémoire indisponible pour le moment.'
  } finally {
    loading.value = false
  }
}

onMounted(loadMemorySummary)
watch(() => props.sessionId, loadMemorySummary)
</script>

<template>
  <section
    class="card prod-panel prod-panel--memory"
    :class="`prod-panel--${displayProfile || 'professional'}`"
    aria-label="Mémoire de la conversation"
  >
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-start gap-2 mb-3">
        <div>
          <h2 class="prod-section-title h6 mb-1">Mémoire de la séance</h2>
          <p class="small text-muted mb-0">
            Résumé gouverné de cette conversation uniquement — pas de dossier global ni d’historique brut.
          </p>
        </div>
        <button
          type="button"
          class="btn btn-sm btn-outline-secondary"
          :disabled="loading"
          @click="loadMemorySummary"
        >
          Actualiser
        </button>
      </div>

      <div v-if="loading" class="text-center py-3">
        <div class="spinner-border spinner-border-sm text-primary" role="status">
          <span class="visually-hidden">Chargement…</span>
        </div>
      </div>

      <p v-else-if="error" class="text-danger small mb-0">{{ error }}</p>

      <div v-else-if="hasContent" class="prod-memory-summary">
        <p v-if="sessionMemory.theme" class="mb-3">
          <span class="text-muted small d-block">Thème</span>
          <strong><ExpandableText :text="sessionMemory.theme" /></strong>
        </p>
        <p v-if="sessionMemory.learning_objective" class="mb-3">
          <span class="text-muted small d-block">Objectif</span>
          <ExpandableText :text="sessionMemory.learning_objective" />
        </p>

        <div v-if="sessionMemory.facts_confirmed?.length" class="mb-3">
          <span class="text-muted small d-block mb-1">Vous avez déjà travaillé sur</span>
          <ul class="small mb-0 ps-3">
            <li v-for="(point, index) in sessionMemory.facts_confirmed" :key="`fact-${index}`">
              <ExpandableText :text="point" />
            </li>
          </ul>
        </div>

        <div v-if="sessionMemory.open_points?.length" class="mb-3">
          <span class="text-muted small d-block mb-1">Il reste à clarifier</span>
          <ul class="small mb-0 ps-3">
            <li v-for="(point, index) in sessionMemory.open_points" :key="`open-${index}`">
              <ExpandableText :text="point" />
            </li>
          </ul>
        </div>

        <div v-if="sessionMemory.pending_actions?.length">
          <span class="text-muted small d-block mb-1">Prochaines actions suggérées</span>
          <ul class="small mb-0 ps-3">
            <li v-for="(action, index) in sessionMemory.pending_actions" :key="`action-${index}`">
              <ExpandableText :text="action" />
            </li>
          </ul>
        </div>
      </div>

      <p v-else class="text-muted small mb-0">
        Aucun repère structuré pour l’instant. Continuez la conversation pour enrichir cette mémoire.
      </p>
    </div>
  </section>
</template>
