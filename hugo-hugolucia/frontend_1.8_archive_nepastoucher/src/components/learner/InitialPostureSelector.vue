<script setup>
import { computed } from 'vue'
import { LEARNER_POSTURES, postureDescription, postureLabel } from '../../constants/conversationPostures'

const props = defineProps({
  modelValue: { type: String, default: 'reflective_afest' },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

const selectedDescription = computed(() => postureDescription(props.modelValue))

function onChange(event) {
  emit('update:modelValue', event.target.value)
}
</script>

<template>
  <div class="mb-3" data-testid="initial-posture-selector">
    <label class="form-label" for="initial-posture">Posture initiale</label>
    <select
      id="initial-posture"
      class="form-select"
      :disabled="disabled"
      :value="modelValue"
      data-testid="initial-posture-select"
      @change="onChange"
    >
      <option
        v-for="posture in LEARNER_POSTURES"
        :key="posture.code"
        :value="posture.code"
      >
        {{ posture.label }}
      </option>
    </select>
    <p v-if="selectedDescription" class="small text-muted mb-0 mt-2">
      {{ selectedDescription }}
    </p>
    <p class="small text-muted mb-0 mt-1">
      Par défaut : {{ postureLabel('reflective_afest') }}. Tu pourras changer de mode en séance.
    </p>
  </div>
</template>
