<script setup>
import { ref, onMounted, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import ActiveOrganisationBanner from '../../components/admin/ActiveOrganisationBanner.vue'
import {
  useAdminOnboardingStatus,
  statusBadgeClass,
  STEP_STATUS,
} from '../../composables/useAdminOnboardingStatus'

const route = useRoute()
const router = useRouter()
const selectedGroupId = ref('')

const {
  loading,
  error,
  groups,
  focusGroup,
  steps,
  completedCount,
  progressPercent,
  refresh,
} = useAdminOnboardingStatus(selectedGroupId)

const WIZARD_SCOPE_NOTE =
  'Ce parcours concerne cette organisation. Les groupes proposés ci-dessous appartiennent à cette organisation.'

function applyQueryGroupId() {
  const qId = route.query.groupId
  if (!qId || !groups.value.length) return
  const match = groups.value.find((g) => String(g.id) === String(qId))
  if (match) selectedGroupId.value = String(match.id)
}

function onGroupSelectChange() {
  const query = { ...route.query }
  if (selectedGroupId.value) query.groupId = selectedGroupId.value
  else delete query.groupId
  router.replace({ query })
}

onMounted(async () => {
  await refresh()
  if (route.query.groupId) {
    applyQueryGroupId()
  }
})

watch(groups, () => {
  if (route.query.groupId && !selectedGroupId.value) {
    applyQueryGroupId()
  }
})
</script>

<template>
  <div class="container-fluid admin-onboarding-wizard">
    <nav aria-label="breadcrumb" class="mb-3">
      <ol class="breadcrumb mb-0">
        <li class="breadcrumb-item">
          <RouterLink to="/dashboard">Tableau de bord</RouterLink>
        </li>
        <li class="breadcrumb-item active" aria-current="page">Mise en route admin</li>
      </ol>
    </nav>

    <header class="mb-4">
      <h1 class="h4 mb-2">Assistant de mise en route</h1>
      <p class="text-muted mb-3">
        Ce parcours vous guide dans la configuration admin — il ne crée ni ne modifie rien à votre place.
        Utilisez les boutons ci-dessous pour ouvrir les pages de gestion existantes.
      </p>
      <ActiveOrganisationBanner show-switcher-hint :scope-note="WIZARD_SCOPE_NOTE" />
    </header>

    <div v-if="loading" class="d-flex justify-content-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Chargement…</span>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-danger" role="alert">
      {{ error }}
      <button type="button" class="btn btn-sm btn-outline-danger ms-2" @click="refresh">
        Réessayer
      </button>
    </div>

    <template v-else>
      <section v-if="groups.length" class="card shadow-sm mb-4" aria-label="Sélection du groupe">
        <div class="card-body">
          <label for="wizard-group-select" class="form-label fw-medium mb-1">Groupe à configurer</label>
          <select
            id="wizard-group-select"
            v-model="selectedGroupId"
            class="form-select"
            data-testid="wizard-group-select"
            @change="onGroupSelectChange"
          >
            <option v-for="g in groups" :key="g.id" :value="String(g.id)">
              {{ g.name }}
            </option>
          </select>
          <p v-if="focusGroup" class="small text-muted mb-0 mt-2">
            Groupe sélectionné : <strong>{{ focusGroup.name }}</strong>
          </p>
        </div>
      </section>

      <div v-else class="alert alert-warning mb-4" role="alert">
        Aucun groupe dans cette organisation.
        <RouterLink to="/groups-admin" class="alert-link">Créer un groupe</RouterLink>
      </div>

      <section class="mb-4" aria-label="Progression">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <span class="small fw-medium">Progression</span>
          <span class="small text-muted">{{ completedCount }} / 4 étapes prêtes</span>
        </div>
        <div class="progress" style="height: 8px">
          <div
            class="progress-bar bg-primary"
            role="progressbar"
            :style="{ width: `${progressPercent}%` }"
            :aria-valuenow="progressPercent"
            aria-valuemin="0"
            aria-valuemax="100"
          />
        </div>
      </section>

      <ol class="list-unstyled onboarding-steps mb-4">
        <li
          v-for="(step, index) in steps"
          :key="step.id"
          class="onboarding-step card shadow-sm mb-3"
          :class="{ 'border-warning border-opacity-50': step.status === STEP_STATUS.FALLBACK }"
        >
          <div class="card-body">
            <div class="d-flex flex-wrap align-items-start gap-2 mb-2">
              <span class="step-index badge rounded-pill text-bg-light border">{{ index + 1 }}</span>
              <div class="flex-grow-1">
                <div class="d-flex flex-wrap align-items-center gap-2 mb-1">
                  <h2 class="h6 mb-0">{{ step.title }}</h2>
                  <span class="badge" :class="statusBadgeClass(step.status)">
                    {{ step.statusLabel }}
                  </span>
                </div>
                <p class="small text-muted mb-0">{{ step.summary }}</p>
              </div>
            </div>
            <div class="mt-3 d-flex flex-wrap gap-2">
              <RouterLink
                :to="step.ctaTo"
                class="btn btn-outline-primary btn-sm"
                :data-testid="step.id === 'conversation' ? 'wizard-conversation-cta' : undefined"
              >
                {{ step.ctaLabel }}
                <i class="bi bi-box-arrow-up-right ms-1" aria-hidden="true" />
              </RouterLink>
              <RouterLink
                v-if="step.secondaryCtaTo"
                :to="step.secondaryCtaTo"
                class="btn btn-outline-secondary btn-sm"
                data-testid="wizard-conversation-profiles-secondary"
              >
                {{ step.secondaryCtaLabel }}
                <i class="bi bi-box-arrow-up-right ms-1" aria-hidden="true" />
              </RouterLink>
            </div>
          </div>
        </li>
      </ol>

      <footer class="border-top pt-3">
        <p class="small text-muted mb-2">
          Les actions réelles (création de comptes, rattachements, profils, référentiels) se font sur les
          pages dédiées. Rechargez cette vue après vos modifications pour mettre à jour les statuts.
        </p>
        <button type="button" class="btn btn-sm btn-outline-secondary" @click="refresh">
          Actualiser les statuts
        </button>
        <RouterLink to="/dashboard" class="btn btn-sm btn-link">Retour au tableau de bord</RouterLink>
      </footer>
    </template>
  </div>
</template>

<style scoped>
.admin-onboarding-wizard {
  max-width: 52rem;
}

.step-index {
  min-width: 1.75rem;
  font-size: 0.75rem;
}
</style>
