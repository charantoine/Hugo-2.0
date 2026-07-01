<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import api from '../../api/client'

const props = defineProps({
  learnerId: { type: String, default: '' },
  groupId: { type: String, default: '' },
  sourceSessionId: { type: String, default: '' },
  workspaceSessionId: { type: String, default: '' },
})

const memoryLoading = ref(false)
const memoryError = ref('')
const memoryNote = ref('')

const hasLearnerContext = computed(() => Boolean(props.learnerId && props.groupId))

async function probeMemoryAccess() {
  if (!props.sourceSessionId) {
    memoryNote.value = 'Aucune session apprenant liée — consultez la timeline depuis la fiche.'
    return
  }
  memoryLoading.value = true
  memoryError.value = ''
  memoryNote.value = ''
  try {
    await api.get(`/hugo/sessions/${props.sourceSessionId}/memory-summary/`)
    memoryNote.value = 'Mémoire accessible (cas exceptionnel).'
  } catch (err) {
    const status = err?.response?.status
    if (status === 404 || status === 403) {
      memoryNote.value = (
        'La mémoire gouvernée de l\'apprenant n\'est pas exposée au tuteur via memory-summary '
        + '(ACL actuelle). Utilisez la timeline sur la fiche apprenant.'
      )
    } else {
      memoryError.value = err?.response?.data?.detail || 'Contexte mémoire indisponible.'
    }
  } finally {
    memoryLoading.value = false
  }
}

onMounted(probeMemoryAccess)
watch(() => [props.sourceSessionId, props.learnerId], probeMemoryAccess)
</script>

<template>
  <section
    v-if="hasLearnerContext"
    class="card prod-panel mb-3"
    data-testid="tutor-workspace-context-panel"
  >
    <div class="card-body">
      <h2 class="h6 mb-2">Contexte apprenant (lecture)</h2>
      <p class="small text-muted mb-2">
        Outil visuel pour le tuteur — non injecté dans le prompt LLM.
      </p>
      <dl class="small mb-2">
        <dt class="d-inline">Apprenant :</dt>
        <dd class="d-inline ms-1">{{ learnerId }}</dd>
        <dt class="d-inline ms-2">Groupe :</dt>
        <dd class="d-inline ms-1">{{ groupId }}</dd>
        <template v-if="sourceSessionId">
          <dt class="d-inline ms-2">Session source :</dt>
          <dd class="d-inline ms-1"><code>{{ sourceSessionId.slice(0, 8) }}</code></dd>
        </template>
      </dl>
      <div v-if="memoryLoading" class="small text-muted">Vérification du contexte mémoire…</div>
      <p v-else-if="memoryError" class="small text-danger mb-0">{{ memoryError }}</p>
      <p v-else class="small text-muted mb-0">{{ memoryNote }}</p>
    </div>
  </section>
</template>
