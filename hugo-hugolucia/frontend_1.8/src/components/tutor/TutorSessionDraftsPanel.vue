<script setup>
import { computed } from 'vue'
import { summarizeTutorArtifact } from '../../utils/tutorChatImport.js'

const props = defineProps({
  artifacts: { type: Array, default: () => [] },
})

const entries = computed(() => (
  (props.artifacts || []).map((item) => ({
    item,
    summary: summarizeTutorArtifact(item),
  })).filter((row) => row.summary)
))
</script>

<template>
  <section
    v-if="entries.length"
    class="card mb-3"
    data-testid="tutor-session-drafts-panel"
  >
    <div class="card-header py-2">
      <span class="small fw-semibold">Brouillons tutoraux (session courante)</span>
      <span class="badge text-bg-secondary ms-2">non durable</span>
    </div>
    <ul class="list-group list-group-flush">
      <li
        v-for="row in entries"
        :key="row.item.id"
        class="list-group-item small"
        data-testid="tutor-session-draft-item"
      >
        <div class="fw-semibold">{{ row.summary.title }}</div>
        <div class="text-muted">{{ row.summary.line }}</div>
      </li>
    </ul>
  </section>
</template>
