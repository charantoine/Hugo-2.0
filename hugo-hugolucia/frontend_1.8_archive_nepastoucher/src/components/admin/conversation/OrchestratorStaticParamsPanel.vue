<script setup>
import { computed } from 'vue'

const props = defineProps({
  postureCode: { type: String, required: true },
  staticParams: { type: Object, default: null },
})

const rows = computed(() => {
  if (!props.staticParams) return []
  return [
    { label: 'Branches actives max', value: props.staticParams.max_branches },
    { label: 'Synthèse requiert', value: props.staticParams.synthesis_requires },
    { label: 'Évaluation requiert', value: props.staticParams.evaluation_requires },
    { label: 'Vert exige transfert', value: props.staticParams.green_requires_transfer ? 'Oui' : 'Non' },
  ]
})
</script>

<template>
  <div class="card shadow-sm border-info">
    <div class="card-body">
      <h2 class="h6 mb-2">Paramètres orchestrateur (lecture seule — Phase 1)</h2>
      <p class="text-muted small mb-3">
        Seuils d’éligibilité synthèse / évaluation définis côté moteur
        (<code>tutor_profiles.py</code>). Édition admin prévue Phase 3.
      </p>
      <dl v-if="rows.length" class="row mb-0 small">
        <template v-for="row in rows" :key="row.label">
          <dt class="col-sm-5">{{ row.label }}</dt>
          <dd class="col-sm-7">{{ row.value }}</dd>
        </template>
      </dl>
      <p v-else class="text-muted small mb-0">Paramètres non disponibles pour cette posture.</p>
    </div>
  </div>
</template>
