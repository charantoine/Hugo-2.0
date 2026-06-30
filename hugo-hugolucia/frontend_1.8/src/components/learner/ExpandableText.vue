<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  text: {
    type: String,
    default: '',
  },
  maxChars: {
    type: Number,
    default: 220,
  },
})

const expanded = ref(false)

const normalized = computed(() => String(props.text || '').trim())
const needsExpand = computed(() => normalized.value.length > props.maxChars)
const visibleText = computed(() => {
  if (!needsExpand.value || expanded.value) return normalized.value
  return `${normalized.value.slice(0, props.maxChars).trim()}…`
})
</script>

<template>
  <span v-if="normalized">
    {{ visibleText }}
    <button
      v-if="needsExpand"
      type="button"
      class="btn btn-link btn-sm p-0 align-baseline prod-expandable-text__toggle"
      @click="expanded = !expanded"
    >
      {{ expanded ? 'Voir moins' : 'Voir plus' }}
    </button>
  </span>
</template>
