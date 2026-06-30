<script setup>
import { computed, ref } from 'vue'
import api from '../../api/client'
import { LEARNER_POSTURES, postureBetaDescription, postureDescription, postureLabel, postureShortLabel } from '../../constants/conversationPostures'

const props = defineProps({
  sessionId: {
    type: String,
    required: true,
  },
  conversationMode: {
    type: Object,
    default: null,
  },
  busy: {
    type: Boolean,
    default: false,
  },
  variant: {
    type: String,
    default: 'select',
    validator: (value) => ['select', 'buttons'].includes(value),
  },
})

const emit = defineEmits(['posture-changed'])

const switching = ref(false)
const localError = ref('')
const localWarning = ref('')

const currentCode = computed(() => props.conversationMode?.code || '')
const currentLabel = computed(() => props.conversationMode?.label || postureLabel(currentCode.value))
const currentDescription = computed(() => (
  props.variant === 'buttons'
    ? postureBetaDescription(currentCode.value)
    : postureDescription(currentCode.value)
))
const canSwitch = computed(() => Boolean(props.conversationMode?.canSwitch) && !props.busy)
const backendWarning = computed(() => props.conversationMode?.switchWarning || '')
const switchLockedReason = computed(() => (
  props.conversationMode?.switchLockedReason
  || 'Le changement de mode n’est pas disponible dans le contexte actuel de la séance.'
))

const transitionMap = computed(() => {
  const map = new Map()
  for (const entry of props.conversationMode?.allowedPostureTransitions || []) {
    if (entry?.code) map.set(entry.code, entry)
  }
  return map
})

const postureOptions = computed(() => (
  LEARNER_POSTURES.map((entry) => {
    const transition = transitionMap.value.get(entry.code)
    const isCurrent = entry.code === currentCode.value
    const allowed = isCurrent || (transition ? transition.allowed : false)
    return {
      ...entry,
      shortLabel: postureShortLabel(entry.code),
      disabled: isCurrent || !allowed,
      optionWarning: transition?.warning || null,
    }
  })
))

async function onPostureChange(event) {
  const nextPosture = String(event?.target?.value || event || '').trim()
  if (!nextPosture || nextPosture === currentCode.value) return

  const target = postureOptions.value.find((option) => option.code === nextPosture)
  if (target?.disabled) {
    localError.value = target.optionWarning || 'Ce changement de mode n’est pas autorisé pour l’instant.'
    if (event?.target) event.target.value = currentCode.value
    return
  }

  switching.value = true
  localError.value = ''
  localWarning.value = ''
  try {
    const { data } = await api.post(`/hugo/sessions/${props.sessionId}/set-posture/`, {
      posture: nextPosture,
    })
    localWarning.value = data?.warning || target?.optionWarning || ''
    emit('posture-changed', data)
  } catch (err) {
    const detail = err.response?.data?.detail
    if (detail === 'transition_not_allowed') {
      localError.value = 'Ce changement de mode n’est pas autorisé pour l’instant.'
    } else if (detail === 'Invalid posture.') {
      localError.value = 'Mode demandé non reconnu.'
    } else {
      localError.value = detail || 'Impossible de changer de mode pour le moment.'
    }
    if (event?.target) event.target.value = currentCode.value
  } finally {
    switching.value = false
  }
}
</script>

<template>
  <!-- BETA_HIDDEN: variante select (testeurs internes) -->
  <section
    v-if="conversationMode?.label && variant === 'select'"
    class="prod-conversation-mode card prod-panel"
    :data-conversation-mode="currentCode || undefined"
    aria-label="Mode conversationnel"
  >
    <div class="card-body py-3">
      <div class="d-flex flex-column flex-lg-row align-items-lg-center justify-content-between gap-3">
        <div>
          <span class="prod-conversation-mode__label text-muted small d-block mb-1">Mode conversationnel</span>
          <div class="d-flex flex-wrap align-items-center gap-2">
            <span class="badge rounded-pill text-bg-light border prod-conversation-mode__pill">
              {{ currentLabel }}
            </span>
            <span v-if="switching" class="small text-muted">Mise à jour…</span>
          </div>
          <p v-if="currentDescription" class="small text-muted mb-0 mt-2">
            {{ currentDescription }}
          </p>
        </div>

        <div class="prod-conversation-mode__selector">
          <label :for="`posture-select-${sessionId}`" class="form-label small text-muted mb-1">
            Changer de mode
          </label>
          <select
            :id="`posture-select-${sessionId}`"
            class="form-select form-select-sm"
            :class="{ 'prod-conversation-mode__select--locked': !canSwitch }"
            :value="currentCode"
            :disabled="!canSwitch || switching || busy"
            @change="onPostureChange"
          >
            <option
              v-for="option in postureOptions"
              :key="option.code"
              :value="option.code"
              :disabled="option.disabled"
            >
              {{ option.label }}
            </option>
          </select>
          <p v-if="!canSwitch" class="small text-muted mb-0 mt-2" role="status">
            {{ switchLockedReason }}
          </p>
        </div>
      </div>

      <div v-if="backendWarning" class="alert alert-warning small mb-0 mt-3" role="status">
        {{ backendWarning }}
      </div>
      <div v-if="localWarning" class="alert alert-warning small mb-0 mt-3" role="status">
        {{ localWarning }}
      </div>
      <div v-if="localError" class="alert alert-danger small mb-0 mt-3" role="alert">
        {{ localError }}
      </div>
    </div>
  </section>

  <!-- UI 2.0 — boutons Diag / Réflexif / Bûchage -->
  <section
    v-else-if="conversationMode?.label && variant === 'buttons'"
    class="learner-mode-buttons"
    :data-conversation-mode="currentCode || undefined"
    aria-label="Modes de conversation"
  >
    <div class="learner-mode-buttons__row" role="group" aria-label="Choisir un mode">
      <button
        v-for="option in postureOptions"
        :key="option.code"
        type="button"
        class="btn btn-sm learner-mode-buttons__btn"
        :class="option.code === currentCode ? 'learner-mode-buttons__btn--active' : 'btn-outline-secondary'"
        :disabled="option.disabled || !canSwitch || switching || busy"
        :aria-pressed="option.code === currentCode"
        :aria-label="`Mode ${option.shortLabel}`"
        @click="onPostureChange(option.code)"
      >
        {{ option.shortLabel }}
      </button>
    </div>
    <p v-if="currentDescription" class="learner-mode-buttons__description small text-muted mb-0">
      {{ currentDescription }}
    </p>
    <p v-if="switching" class="small text-muted mb-0 mt-1">Mise à jour du mode…</p>
    <p v-else-if="!canSwitch" class="small text-muted mb-0 mt-1" role="status">
      {{ switchLockedReason }}
    </p>
    <div v-if="backendWarning" class="alert alert-warning small mb-0 mt-2 py-2" role="status">
      {{ backendWarning }}
    </div>
    <div v-if="localWarning" class="alert alert-warning small mb-0 mt-2 py-2" role="status">
      {{ localWarning }}
    </div>
    <div v-if="localError" class="alert alert-danger small mb-0 mt-2 py-2" role="alert">
      {{ localError }}
    </div>
  </section>
</template>
