<script setup>
import { computed } from 'vue'
import { LEARNER_POSTURES, postureBetaDescription, postureLabel, postureShortLabel } from '../../constants/conversationPostures'
import {
  getContractCtaEvaluation,
  getContractCtaSynthesis,
  isContractCtaEvaluationEligible,
  isContractCtaSynthesisEligible,
  isContractUiStateReady,
  parseContractConversationMode,
} from '../../utils/engagementUiModel'

const props = defineProps({
  sessionId: { type: String, required: true },
  sessionUiState: { type: Object, default: null },
  uiStateLoading: { type: Boolean, default: false },
  uiStateError: { type: String, default: null },
  postureSwitching: { type: Boolean, default: false },
  model: { type: Object, required: true },
  busy: { type: Boolean, default: false },
  actionFeedback: { type: Object, default: null },
  synthesisResult: { type: Object, default: null },
  evaluationResult: { type: Object, default: null },
  sessionTraces: { type: Array, default: () => [] },
  sessionEvidenceCount: { type: Number, default: 0 },
  shareFlags: { type: Object, required: true },
  hideSymbolicRewards: { type: Boolean, default: true },
})

const emit = defineEmits([
  'change-posture',
  'request-synthesis',
  'request-evaluation',
  'reload-ui-state',
  'update-share',
])

const conversationMode = computed(() => parseContractConversationMode(props.sessionUiState))
const ctaEvaluation = computed(() => getContractCtaEvaluation(props.sessionUiState))
const ctaSynthesis = computed(() => getContractCtaSynthesis(props.sessionUiState))

const pilotageReady = computed(() => isContractUiStateReady(props.sessionUiState))

const currentCode = computed(() => conversationMode.value?.code || '')
const currentLabel = computed(() => (
  conversationMode.value?.label || postureLabel(currentCode.value) || 'Mode non renseigné'
))
const currentDescription = computed(() => postureBetaDescription(currentCode.value))
const canSwitch = computed(() => Boolean(conversationMode.value?.canSwitch) && !props.busy && !props.postureSwitching)

const postureOptions = computed(() => {
  const transitionMap = new Map()
  for (const entry of conversationMode.value?.allowedPostureTransitions || []) {
    if (entry?.code) transitionMap.set(entry.code, entry)
  }
  return LEARNER_POSTURES.map((entry) => {
    const transition = transitionMap.get(entry.code)
    const isCurrent = entry.code === currentCode.value
    const allowed = isCurrent || Boolean(transition?.allowed)
    return {
      ...entry,
      shortLabel: postureShortLabel(entry.code),
      isCurrent,
      allowed,
      disabled: isCurrent || !allowed,
      optionWarning: transition?.warning || null,
    }
  })
})

const showEvaluationCta = computed(() => isContractCtaEvaluationEligible(ctaEvaluation.value))
const showSynthesisCta = computed(() => isContractCtaSynthesisEligible(ctaSynthesis.value))

const evaluationLabel = computed(() => (
  ctaEvaluation.value?.ui?.button_label || 'Demander une évaluation'
))
const evaluationAdvisory = computed(() => Boolean(ctaEvaluation.value?.ui?.advisory))
const evaluationDisabled = computed(() => Boolean(ctaEvaluation.value?.ui?.button_disabled))
const evaluationHelper = computed(() => (
  ctaEvaluation.value?.ui?.helper_text
  || ctaEvaluation.value?.blocking_reasons?.[0]
  || null
))

const synthesisLabel = computed(() => (
  ctaSynthesis.value?.ui?.button_label || 'Obtenir une synthèse'
))
const synthesisDisabled = computed(() => Boolean(ctaSynthesis.value?.ui?.button_disabled))
const synthesisHelper = computed(() => (
  ctaSynthesis.value?.ui?.helper_text
  || ctaSynthesis.value?.blocking_reasons?.[0]
  || null
))

const synthesisBlockedVisible = computed(() => (
  !showSynthesisCta.value
  && ctaSynthesis.value?.ui?.show_synthesis_button !== false
  && ctaSynthesis.value?.ui?.button_label
))

function onShareChange() {
  emit('update-share')
}

function onPostureClick(code) {
  if (!canSwitch.value || props.postureSwitching || code === currentCode.value) return
  const target = postureOptions.value.find((option) => option.code === code)
  if (target?.disabled) return
  emit('change-posture', code)
}
</script>

<template>
  <aside class="learner-action-sidebar card prod-panel h-100" aria-label="Actions de session">
    <div class="card-body d-flex flex-column gap-3">
      <section class="learner-pilotage-panel" aria-label="Pilotage de la conversation">
        <h2 class="h6 mb-2">Pilotage de la conversation</h2>

        <div
          v-if="uiStateLoading && !sessionUiState"
          class="learner-pilotage-panel__state text-muted small d-flex align-items-center gap-2"
          role="status"
        >
          <span class="spinner-border spinner-border-sm" aria-hidden="true"></span>
          Chargement des contrôles…
        </div>

        <div
          v-else-if="uiStateError && !pilotageReady"
          class="learner-pilotage-panel__state alert alert-warning py-2 small mb-0"
          role="alert"
        >
          <p class="mb-2">Pilotage de la conversation indisponible pour le moment.</p>
          <p v-if="uiStateError" class="mb-2 text-muted">{{ uiStateError }}</p>
          <button
            type="button"
            class="btn btn-sm btn-outline-secondary"
            :disabled="uiStateLoading"
            @click="emit('reload-ui-state')"
          >
            Réessayer
          </button>
        </div>

        <template v-else-if="pilotageReady">
          <p v-if="uiStateError" class="small text-warning mb-2" role="status">
            Affichage sur dernier état connu — {{ uiStateError }}
          </p>

          <section
            class="learner-mode-buttons"
            :data-conversation-mode="currentCode || undefined"
            aria-label="Modes de conversation"
          >
            <p class="small text-muted mb-2 mb-md-1">
              Mode actuel : <strong>{{ currentLabel }}</strong>
            </p>
            <div class="learner-mode-buttons__row" role="group" aria-label="Choisir un mode">
              <button
                v-for="option in postureOptions"
                :key="option.code"
                type="button"
                class="btn btn-sm learner-mode-buttons__btn"
                :class="option.isCurrent ? 'learner-mode-buttons__btn--active' : 'btn-outline-secondary'"
                :disabled="option.disabled || !canSwitch || postureSwitching"
                :aria-pressed="option.isCurrent"
                :aria-label="`Mode ${option.shortLabel}`"
                :title="option.optionWarning || (option.disabled && !option.isCurrent ? 'Transition non autorisée' : undefined)"
                @click="onPostureClick(option.code)"
              >
                {{ option.shortLabel }}
              </button>
            </div>
            <p v-if="currentDescription" class="learner-mode-buttons__description small text-muted mb-0">
              {{ currentDescription }}
            </p>
            <p v-if="postureSwitching" class="small text-muted mb-0 mt-1">Mise à jour du mode…</p>
            <p
              v-else-if="!conversationMode?.canSwitch"
              class="small text-muted mb-0 mt-1"
              role="status"
            >
              {{ conversationMode?.switchLockedReason || 'Le changement de mode n’est pas disponible dans le contexte actuel de la séance.' }}
            </p>
            <p
              v-else-if="conversationMode?.switchWarning"
              class="small text-warning mb-0 mt-1"
              role="status"
            >
              {{ conversationMode.switchWarning }}
            </p>
          </section>

          <div class="learner-action-sidebar__cta-row mt-3">
            <button
              v-if="showSynthesisCta"
              type="button"
              class="btn btn-sm learner-cta-btn learner-cta-btn--ok"
              :disabled="busy || synthesisDisabled"
              :title="synthesisHelper || undefined"
              @click="emit('request-synthesis')"
            >
              {{ synthesisLabel }}
            </button>
            <button
              v-else-if="synthesisBlockedVisible"
              type="button"
              class="btn btn-sm learner-cta-btn learner-cta-btn--muted"
              disabled
              :title="synthesisHelper || undefined"
            >
              {{ synthesisLabel }}
            </button>
            <button
              v-if="showEvaluationCta"
              type="button"
              class="btn btn-sm learner-cta-btn btn-evaluation"
              :class="evaluationAdvisory ? 'learner-cta-btn--discouraged' : 'learner-cta-btn--ok'"
              :disabled="busy || evaluationDisabled"
              @click="emit('request-evaluation')"
            >
              {{ evaluationLabel }}
              <span v-if="evaluationAdvisory" class="ms-1">(conseillée)</span>
            </button>
          </div>

          <p
            v-if="showEvaluationCta && evaluationHelper"
            class="small text-muted mb-0 learner-action-sidebar__eval-hint"
            role="status"
          >
            {{ evaluationHelper }}
          </p>
          <p
            v-if="(showSynthesisCta || synthesisBlockedVisible) && synthesisHelper"
            class="small text-muted mb-0"
          >
            {{ synthesisHelper }}
          </p>
        </template>
      </section>

      <div v-if="actionFeedback" class="alert py-2 small mb-0" :class="actionFeedback.type === 'success' ? 'alert-success' : 'alert-warning'">
        {{ actionFeedback.message }}
      </div>

      <section class="learner-traces-panel">
        <h2 class="h6 mb-1">Traces et acquis</h2>
        <p class="text-muted small mb-3">
          {{ model.profileCopy?.tracesSectionLead }}
        </p>

        <div
          v-if="model.uiVisibilityFlags.persistentObjectsEnabled"
          class="d-grid gap-2 mb-3"
        >
          <article
            v-for="item in model.persistentObjects"
            :key="item.id"
            class="prod-object-card"
            :class="`prod-object-card--${item.status}`"
          >
            <div class="d-flex justify-content-between gap-2 align-items-start">
              <div>
                <strong>{{ item.title }}</strong>
                <p class="small mb-0">{{ item.description }}</p>
              </div>
              <span class="badge rounded-pill text-bg-light border">{{ item.meta }}</span>
            </div>
          </article>
        </div>

        <div v-if="synthesisResult" class="prod-list-card mb-3">
          <h3 class="h6">{{ synthesisResult.title || 'Synthèse' }}</h3>
          <p class="mb-0 small" style="white-space: pre-wrap;">{{ synthesisResult.text }}</p>
        </div>

        <div v-if="evaluationResult" class="prod-list-card prod-list-card--soft mb-3">
          <h3 class="h6">{{ evaluationResult.title || 'Évaluation' }}</h3>
          <p class="mb-2 small" style="white-space: pre-wrap;">{{ evaluationResult.text }}</p>
        </div>

        <div class="prod-trace-summary">
          <div class="prod-trace-summary__item">
            <strong>{{ sessionTraces.length }}</strong>
            <span>trace(s)</span>
          </div>
          <div class="prod-trace-summary__item">
            <strong>{{ sessionEvidenceCount }}</strong>
            <span>preuve(s)</span>
          </div>
          <div class="prod-trace-summary__item">
            <strong>{{ sessionTraces.some((trace) => trace.validated_at) ? 'Oui' : 'Pas encore' }}</strong>
            <span>validation</span>
          </div>
        </div>

        <div class="d-grid gap-2 mt-2">
          <label class="form-check prod-check">
            <input v-model="shareFlags.share_summary" class="form-check-input" type="checkbox" @change="onShareChange" />
            <span>
              <strong>Partager le résumé</strong>
              <small>Autorise la transmission du mini-bilan.</small>
            </span>
          </label>
          <label class="form-check prod-check">
            <input v-model="shareFlags.share_evidence" class="form-check-input" type="checkbox" @change="onShareChange" />
            <span>
              <strong>Partager les preuves</strong>
              <small>Autorise les pièces utiles liées à la scène.</small>
            </span>
          </label>
          <label class="form-check prod-check">
            <input v-model="shareFlags.share_verbatim" class="form-check-input" type="checkbox" @change="onShareChange" />
            <span>
              <strong>Partager le texte du chat</strong>
              <small>Le verbatim reste privé tant que cette option n’est pas activée.</small>
            </span>
          </label>
        </div>

        <div
          v-if="!hideSymbolicRewards && model.uiVisibilityFlags.symbolicRewardsEnabled"
          class="mt-3 symbolic-rewards-block"
        >
          <h3 class="h6 mb-2">Récompenses symboliques</h3>
          <div class="d-grid gap-2">
            <article
              v-for="reward in model.symbolicRewards"
              :key="reward.id"
              :class="reward.unlocked ? 'prod-reward prod-reward--unlocked' : 'prod-reward'"
            >
              <strong>{{ reward.label }}</strong>
            </article>
          </div>
        </div>
      </section>
    </div>
  </aside>
</template>
