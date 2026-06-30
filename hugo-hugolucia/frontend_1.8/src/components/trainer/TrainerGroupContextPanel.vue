<script setup>
import { onMounted } from 'vue'
import { useTrainerGroupContext } from '../../composables/useTrainerGroupContext'

defineProps({
  compact: { type: Boolean, default: false },
})

const {
  groups,
  groupId,
  selectedGroup,
  referentialSummary,
  membershipSummary,
  loading,
  error,
  refresh,
  setGroupId,
} = useTrainerGroupContext()

onMounted(refresh)
</script>

<template>
  <div class="card shadow-sm mb-4" data-testid="trainer-group-context">
    <div class="card-body">
      <div class="d-flex flex-wrap justify-content-between align-items-start gap-2 mb-2">
        <div>
          <h2 class="h6 mb-1">Contexte groupe</h2>
          <p class="text-muted small mb-0">
            Groupes auxquels vous êtes rattaché dans votre organisation.
          </p>
        </div>
        <button
          type="button"
          class="btn btn-sm btn-outline-secondary"
          :disabled="loading"
          @click="refresh"
        >
          Rafraîchir
        </button>
      </div>

      <div v-if="loading" class="small text-muted">Chargement du contexte…</div>
      <div v-else-if="error" class="alert alert-danger py-2 small mb-0">{{ error }}</div>
      <div v-else-if="!groups.length" class="alert alert-warning py-2 small mb-0">
        Aucun groupe accessible pour votre compte formateur.
      </div>
      <template v-else>
        <div class="row g-2 align-items-end" :class="compact ? 'mb-2' : 'mb-3'">
          <div class="col-md-6">
            <label class="form-label small mb-1" for="trainer-context-group">Groupe actif</label>
            <select
              id="trainer-context-group"
              class="form-select form-select-sm"
              :value="groupId"
              @change="setGroupId($event.target.value)"
            >
              <option v-if="groups.length > 1" value="">— Choisir un groupe —</option>
              <option v-for="group in groups" :key="group.id" :value="group.id">
                {{ group.name }}
              </option>
            </select>
          </div>
          <div v-if="selectedGroup" class="col-md-6">
            <p class="small mb-0">
              <span class="text-muted">Rattaché à :</span>
              <strong>{{ selectedGroup.name }}</strong>
            </p>
          </div>
        </div>

        <div v-if="selectedGroup" class="row g-3">
          <div class="col-md-6">
            <p class="small text-muted mb-1">Référentiel du groupe</p>
            <p v-if="referentialSummary" class="mb-0 small">
              <strong>{{ referentialSummary.name }}</strong>
              <span v-if="referentialSummary.sourceRef" class="text-muted">
                — {{ referentialSummary.sourceRef }}
              </span>
            </p>
            <p v-else class="mb-0 small text-muted">Aucun référentiel associé à ce groupe.</p>
          </div>
          <div class="col-md-6">
            <p class="small text-muted mb-1">Effectif du groupe</p>
            <p class="mb-0 small">
              <strong>{{ membershipSummary.count }}</strong>
              compte{{ membershipSummary.count > 1 ? 's' : '' }} rattaché{{ membershipSummary.count > 1 ? 's' : '' }}
            </p>
            <ul v-if="membershipSummary.roster?.length" class="small mb-2 ps-3">
              <li v-for="row in membershipSummary.roster" :key="row.username">
                <strong>{{ row.username }}</strong>
                <span class="text-muted text-uppercase"> — {{ row.role }}</span>
              </li>
            </ul>
            <router-link
              v-if="selectedGroup"
              class="small"
              :to="{ name: 'ProdTrainerLibrary', query: { groupId: selectedGroup.id } }"
            >
              Ouvrir la bibliothèque de ce groupe
            </router-link>
          </div>
        </div>
        <p v-else-if="groups.length > 1" class="small text-muted mb-0">
          Sélectionnez un groupe pour voir le référentiel et l’effectif.
        </p>
      </template>
    </div>
  </div>
</template>
