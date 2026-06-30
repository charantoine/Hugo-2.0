<script setup>
import { useActiveOrganisationLabel } from '../../composables/useActiveOrganisationLabel'

defineProps({
  /** Rappel du switcher navbar pour SUPERADMIN. */
  showSwitcherHint: { type: Boolean, default: false },
  /** Texte complémentaire sous le libellé org (ex. scope wizard). */
  scopeNote: { type: String, default: '' },
  /** Marge basse (mb-3 sur dashboard). */
  compact: { type: Boolean, default: false },
})

const { label, auth } = useActiveOrganisationLabel()
</script>

<template>
  <div
    class="alert alert-light border py-2 small"
    :class="compact ? 'mb-3' : 'mb-4'"
    role="status"
  >
    Organisation active : <strong>{{ label }}</strong>
    <span v-if="showSwitcherHint && auth.isSuperAdmin" class="text-muted">
      — changez-la via le sélecteur en barre de navigation.
    </span>
    <span v-if="scopeNote" class="d-block mt-1 mb-0 text-muted">{{ scopeNote }}</span>
  </div>
</template>
