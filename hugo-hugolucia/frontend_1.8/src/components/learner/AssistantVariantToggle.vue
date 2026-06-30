<script setup>
const props = defineProps({
  selectedVariant: { type: String, default: 'short' },
})

const emit = defineEmits(['select'])

function choose(variant) {
  emit('select', variant)
}
</script>

<template>
  <div class="btn-group btn-group-sm" role="group" aria-label="Variantes de réponse assistant">
    <button
      type="button"
      class="btn"
      :class="props.selectedVariant === 'short' ? 'btn-secondary' : 'btn-outline-secondary'"
      @click="choose('short')"
    >
      Court
    </button>
    <button
      type="button"
      class="btn"
      :class="props.selectedVariant === 'long' ? 'btn-secondary' : 'btn-outline-secondary'"
      @click="choose('long')"
    >
      Développé
    </button>
  </div>
</template>
