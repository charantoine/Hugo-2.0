<script setup>
import { computed } from 'vue'

const props = defineProps({
  model: {
    type: Object,
    required: true,
  },
})

const phaseLabel = computed(() => props.model.sceneLabel || '—')
const questLabel = computed(() => props.model.questLabel || null)
const branchLabel = computed(() => props.model.priorityBranchLabel || null)
const showDispersion = computed(() => Boolean(props.model.dispersionRisk))
const maturityTooltip = computed(() => (
  {
    red: 'Début de séance : continuez à décrire votre situation.',
    orange: 'Exploration en cours : des éléments manquent encore pour une synthèse complète.',
    green: 'Niveau suffisant : vous pouvez solliciter une synthèse ou une évaluation.',
  }[props.model.maturityColor] || ''
))
</script>

<template>
  <section
    v-if="!model.isDegraded"
    class="prod-scene-context"
    :class="`prod-scene-context--${model.learnerDisplayProfile || 'professional'}`"
    aria-label="Contexte de la séance"
  >
    <div class="prod-scene-context__row">
      <div class="prod-scene-context__item">
        <span class="prod-scene-context__label">Phase</span>
        <strong>{{ phaseLabel }}</strong>
      </div>

      <div v-if="questLabel" class="prod-scene-context__item">
        <span class="prod-scene-context__label">Objectif actif</span>
        <strong>{{ questLabel }}</strong>
      </div>

      <div v-if="branchLabel" class="prod-scene-context__item">
        <span class="prod-scene-context__label">Fil en cours</span>
        <strong>{{ branchLabel }}</strong>
      </div>

      <div
        v-if="model.showMaturityBadge && model.maturityLabel"
        class="prod-scene-context__item prod-scene-context__item--maturity"
        :title="maturityTooltip"
      >
        <span class="prod-scene-context__label">Maturité</span>
        <span
          class="badge rounded-pill"
          :class="`maturity-badge--${model.maturityColor}`"
        >
          {{ model.maturityLabel }}
        </span>
      </div>
    </div>

    <p
      v-if="showDispersion"
      class="prod-scene-context__dispersion small mb-0"
      role="status"
      title="Plusieurs fils sont ouverts en parallèle ; nous vous conseillons de revenir au fil principal."
    >
      <span class="prod-scene-context__dispersion-icon" aria-hidden="true">↔</span>
      Plusieurs sujets sont ouverts : revenez au fil principal pour avancer sereinement.
    </p>
  </section>
</template>
