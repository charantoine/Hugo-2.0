<script setup>
import { TRAINER_IMPORT_KINDS, TRAINER_IMPORT_LABELS } from '../../utils/trainerChatImport.js'

defineProps({
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['import'])

const kinds = [
  TRAINER_IMPORT_KINDS.RESOURCE_PROVISIONAL,
  TRAINER_IMPORT_KINDS.EXPLICATION,
  TRAINER_IMPORT_KINDS.DECISION_RATIONALE,
]

function requestImport(importKind) {
  emit('import', importKind)
}
</script>

<template>
  <div class="import-from-chat d-flex flex-wrap gap-2 mt-2" data-testid="import-from-chat-actions">
    <button
      v-for="kind in kinds"
      :key="kind"
      type="button"
      class="btn btn-sm btn-outline-secondary"
      :disabled="disabled"
      :data-testid="`import-from-chat-${kind}`"
      @click="requestImport(kind)"
    >
      {{ TRAINER_IMPORT_LABELS[kind] }}
    </button>
  </div>
</template>
