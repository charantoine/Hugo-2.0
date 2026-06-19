<script setup>
defineProps({
  model: {
    type: Object,
    required: true,
  },
  busy: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['request-synthesis', 'request-evaluation'])

function stageStateLabel(state) {
  if (state === 'current') return 'En cours'
  if (state === 'done') return 'Terminé'
  return 'À venir'
}
</script>

<template>
  <section
    v-if="model.uiVisibilityFlags.engagementUiEnabled && model.uiVisibilityFlags.sceneProgressEnabled"
    class="card prod-panel prod-panel--progress"
    :class="`prod-panel--${model.learnerDisplayProfile || 'professional'}`"
    aria-label="Progression de la conversation"
  >
    <div class="card-body">
      <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-4">
        <div>
          <h2 class="prod-section-title mb-1">Progression de la scène</h2>
          <p v-if="model.isDegraded" class="text-muted mb-0">
            L'état produit n'est pas encore disponible. L'interface reste volontairement neutre.
          </p>
          <p v-else class="text-muted mb-0">
            {{ model.progressPanelIntro }}
          </p>
        </div>
        <div v-if="!model.isDegraded" class="prod-progress-score">
          <strong>{{ model.sceneProgressPercent }}%</strong>
          <span>{{ model.currentStep.label }}</span>
        </div>
      </div>

      <div v-if="model.showProgressBar" class="mb-4">
        <label class="form-label small text-muted mb-1" for="hugo-scene-progress">Avancement</label>
        <progress
          id="hugo-scene-progress"
          class="w-100"
          :class="`maturity-bar--${model.maturityColor}`"
          :value="model.sceneProgress"
          max="1"
          aria-label="Avancement de la séance"
        ></progress>
      </div>

      <div
        v-if="!model.isDegraded"
        class="prod-stage-rail"
        :class="{ 'prod-stage-rail--icons': model.showStepIcons }"
      >
        <div
          v-for="(step, index) in model.steps"
          :key="step.id"
          class="prod-stage"
          :class="[
            `prod-stage--${step.state}`,
            index <= model.currentStepIndex ? 'prod-stage--reachable' : '',
          ]"
          :aria-current="step.state === 'current' ? 'step' : undefined"
        >
          <div class="prod-stage__dot">{{ index + 1 }}</div>
          <div>
            <div class="prod-stage__header">
              <strong>{{ step.label }}</strong>
              <span class="prod-stage__state" :class="`prod-stage__state--${step.state}`">
                {{ stageStateLabel(step.state) }}
              </span>
            </div>
            <p>{{ step.hint }}</p>
          </div>
        </div>
      </div>

      <div class="row g-3 mt-1">
        <div class="col-12 col-lg-6">
          <div class="prod-list-card">
            <h3>Scène courante</h3>
            <p class="mb-2">{{ model.sceneLabel }}</p>
            <p v-if="!model.isDegraded && model.showQuestLabel && model.questLabel" class="text-muted mb-0">
              Objectif actif : {{ model.questLabel }}
            </p>
            <p v-else-if="model.isDegraded" class="text-muted mb-0">
              Hugo attend le prochain contrat `/ui-state` avant d'afficher une progression.
            </p>
            <p v-else class="text-muted mb-0">La prochaine étape dépend du contrat produit courant.</p>
          </div>
        </div>

        <div class="col-12 col-lg-6">
          <div class="prod-list-card prod-list-card--soft">
            <h3>Maturité</h3>
            <p class="mb-2">
              {{ model.isDegraded ? 'Lecture indisponible tant que le backend ne renvoie pas l’état produit.' : (model.maturityLabel || 'Lecture sobre du niveau de maturité.') }}
            </p>
            <span
              v-if="model.showMaturityBadge && model.maturityLabel"
              class="badge rounded-pill"
              :class="`maturity-badge--${model.maturityColor}`"
            >
              {{ model.maturityLabel }}
            </span>
          </div>
        </div>
      </div>

      <div class="d-flex flex-wrap gap-2 mt-4">
        <button
          v-if="model.synthesisButton.visible"
          type="button"
          class="btn"
          :class="[
            model.synthesisButton.highlighted ? 'btn-primary' : 'btn-outline-primary',
            `hugo-btn--${model.synthesisButton.state}`,
          ]"
          :disabled="busy || model.synthesisButton.disabled"
          @click="$emit('request-synthesis')"
        >
          {{ model.synthesisButton.label }}
        </button>
        <button
          v-if="model.evaluationButton.visible"
          type="button"
          class="btn"
          :class="[
            model.evaluationButton.advisory
              ? 'btn-outline-secondary hugo-btn--advisory'
              : (model.evaluationButton.highlighted ? 'btn-success' : 'btn-outline-success'),
            `hugo-btn--${model.evaluationButton.state}`,
          ]"
          :disabled="busy || model.evaluationButton.disabled"
          @click="$emit('request-evaluation')"
        >
          <span
            v-if="model.evaluationButton.advisory"
            class="hugo-btn__advisory-icon"
            aria-hidden="true"
            title="Évaluation possible mais déconseillée pour l’instant"
          >!</span>
          {{ model.evaluationButton.label }}
        </button>
      </div>
      <p
        v-if="model.evaluationButton.visible && model.evaluationButton.advisory && model.evaluationButton.helperText"
        class="small text-muted mt-3 mb-0 prod-cta-advisory"
        role="status"
      >
        {{ model.evaluationButton.helperText }}
      </p>
      <p
        v-else-if="model.evaluationButton.visible && (model.evaluationButton.helperText || model.evaluationTriggerMessage)"
        class="small text-muted mt-3 mb-0"
      >
        {{ model.evaluationButton.helperText || model.evaluationTriggerMessage }}
      </p>
      <p
        v-if="model.synthesisButton.visible && model.synthesisButton.helperText"
        class="small text-muted mt-2 mb-0"
      >
        {{ model.synthesisButton.helperText }}
      </p>
      <ul
        v-if="model.evaluationButton.blockingReasons?.length && model.evaluationButton.disabled"
        class="small text-muted mt-2 mb-0"
      >
        <li v-for="reason in model.evaluationButton.blockingReasons" :key="reason">{{ reason }}</li>
      </ul>
    </div>
  </section>
</template>
