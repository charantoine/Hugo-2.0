<script setup>
defineProps({
  conversationMode: {
    type: Object,
    default: null,
  },
})
</script>

<template>
  <section
    v-if="conversationMode?.label"
    class="prod-conversation-mode card prod-panel"
    :data-conversation-mode="conversationMode.code || undefined"
    aria-label="Mode conversationnel"
  >
    <div class="card-body py-3">
      <div class="d-flex flex-wrap align-items-center gap-2">
        <span class="prod-conversation-mode__label text-muted small mb-0">Mode</span>
        <span class="badge rounded-pill text-bg-light border prod-conversation-mode__pill">
          {{ conversationMode.label }}
        </span>
      </div>
      <div
        v-if="conversationMode.switchWarning"
        class="alert alert-warning small mb-0 mt-3"
        role="status"
      >
        {{ conversationMode.switchWarning }}
      </div>
    </div>
  </section>
</template>
