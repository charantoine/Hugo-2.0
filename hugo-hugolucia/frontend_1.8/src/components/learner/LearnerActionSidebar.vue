<script setup>
import { computed } from 'vue'
import PostureSelector from './PostureSelector.vue'

const props = defineProps({
  sessionId: { type: String, required: true },
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
  'posture-changed',
  'request-synthesis',
  'request-evaluation',
  'update-share',
])

const evaluationVisualState = computed(() => {
  const button = props.model.evaluationButton
  if (!button?.visible) return 'hidden'
  if (button.disabled) return 'unavailable'
  if (button.advisory) return 'discouraged'
  if (button.highlighted || button.state === 'ready') return 'ok'
  return 'discouraged'
})

const synthesisVisualState = computed(() => {
  const button = props.model.synthesisButton
  if (!button?.visible) return 'hidden'
  if (button.disabled) return 'unavailable'
  return 'ok'
})

function onShareChange() {
  emit('update-share')
}
</script>

<template>
  <aside class="learner-action-sidebar card prod-panel h-100" aria-label="Actions de session">
    <div class="card-body d-flex flex-column gap-3">
      <PostureSelector
        :session-id="sessionId"
        :conversation-mode="model.conversationMode"
        :busy="busy"
        variant="buttons"
        @posture-changed="emit('posture-changed', $event)"
      />

      <div
        v-if="model.synthesisButton.visible || model.evaluationButton.visible"
        class="learner-action-sidebar__cta-row"
      >
        <button
          v-if="model.synthesisButton.visible"
          type="button"
          class="btn btn-sm learner-cta-btn"
          :class="[
            synthesisVisualState === 'ok' ? 'learner-cta-btn--ok' : 'learner-cta-btn--muted',
            `hugo-btn--${model.synthesisButton.state}`,
          ]"
          :data-state="synthesisVisualState"
          :disabled="busy || model.synthesisButton.disabled"
          :title="model.synthesisButton.helperText || undefined"
          @click="emit('request-synthesis')"
        >
          {{ model.synthesisButton.label }}
        </button>
        <button
          v-if="model.evaluationButton.visible"
          type="button"
          class="btn btn-sm learner-cta-btn btn-evaluation"
          :class="`learner-cta-btn--${evaluationVisualState}`"
          :data-state="evaluationVisualState"
          :disabled="busy || model.evaluationButton.disabled"
          @click="emit('request-evaluation')"
        >
          {{ model.evaluationButton.label }}
        </button>
      </div>

      <p
        v-if="model.evaluationButton.visible && (model.evaluationButton.helperText || model.evaluationTriggerMessage)"
        class="small text-muted mb-0 learner-action-sidebar__eval-hint"
        role="status"
      >
        {{ model.evaluationButton.helperText || model.evaluationTriggerMessage }}
      </p>
      <p
        v-if="model.synthesisButton.visible && model.synthesisButton.helperText"
        class="small text-muted mb-0"
      >
        {{ model.synthesisButton.helperText }}
      </p>
      <ul
        v-if="model.evaluationButton.blockingReasons?.length && model.evaluationButton.disabled"
        class="small text-muted mb-0 ps-3"
      >
        <li v-for="reason in model.evaluationButton.blockingReasons" :key="reason">{{ reason }}</li>
      </ul>

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

        <!-- BETA_HIDDEN: récompenses symboliques -->
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
