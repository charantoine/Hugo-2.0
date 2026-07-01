<script setup>
import { TUTOR_IMPORT_KINDS, TUTOR_IMPORT_LABELS } from '../../utils/tutorChatImport.js'

defineProps({
  disabled: { type: Boolean, default: false },
  allowedKinds: { type: Array, default: () => Object.values(TUTOR_IMPORT_KINDS) },
})

const emit = defineEmits(['import'])

function requestImport(importKind) {
  emit('import', importKind)
}
</script>

<template>
  <div class="import-from-chat d-flex flex-wrap gap-2 mt-2" data-testid="tutor-import-from-chat-actions">
    <button
      v-for="kind in allowedKinds"
      :key="kind"
      type="button"
      class="btn btn-sm btn-outline-secondary"
      :disabled="disabled"
      :data-testid="`tutor-import-from-chat-${kind}`"
      @click="requestImport(kind)"
    >
      {{ TUTOR_IMPORT_LABELS[kind] }}
    </button>
  </div>
</template>
