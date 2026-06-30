<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/client'
import { useAuthStore } from '../stores/auth'
import { PLATFORM_VERSION_ADMIN_LINE } from '../utils/platformVersion.js'
import {
  findReferenceGroup,
  isDebugGroupName,
  REFERENCE_GROUP_NAME,
} from '../constants/demoReferenceGroup.js'
import ActiveOrganisationBanner from '../components/admin/ActiveOrganisationBanner.vue'

const router = useRouter()
const auth = useAuthStore()
const groups = ref([])
const loading = ref(true)

const adminLinks = [
  { to: '/users', title: 'Utilisateurs', description: 'Créer et gérer les comptes apprenant, tuteur, formateur.' },
  { to: '/groups-admin', title: 'Groupes', description: 'Cohortes, membres, profil conversationnel et référentiel.' },
  { to: '/admin/conversation', title: 'Conversation apprenant', description: 'Profils globaux et briques par posture.' },
]

onMounted(async () => {
  try {
    const { data } = await api.get('/groups/')
    groups.value = Array.isArray(data) ? data : (data.results || [])
  } catch {
    groups.value = []
  } finally {
    loading.value = false
  }
})

function openGroupCalibration(group) {
  router.push({ name: 'Group', params: { groupId: group.id }, query: { focus: 'calibration' } })
}

function openGroupExports(group) {
  router.push({ name: 'Group', params: { groupId: group.id }, query: { focus: 'exports' } })
}

const canonicalGroup = computed(() => findReferenceGroup(groups.value))

const otherGroups = computed(() =>
  groups.value.filter((g) => g.id !== canonicalGroup.value?.id),
)

const debugGroupCount = computed(() => otherGroups.value.filter((g) => isDebugGroupName(g.name)).length)
</script>

<template>
  <div class="container-fluid">
    <h1 class="h4 mb-2">Tableau de bord</h1>
    <ActiveOrganisationBanner v-if="auth.isAdminLike" compact show-switcher-hint />

    <section v-if="auth.isAdminLike" class="mb-5">
      <div class="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-3">
        <h2 class="h5 mb-0">Administration</h2>
        <router-link to="/admin/onboarding" class="btn btn-outline-primary btn-sm">
          Assistant de mise en route
        </router-link>
      </div>
      <p class="small text-muted mb-3">
        Parcours guidé (lecture seule) : comptes → groupe → conversation → référentiel.
      </p>
      <div class="row g-3">
        <div v-for="link in adminLinks" :key="link.to" class="col-12 col-md-4">
          <router-link :to="link.to" class="text-decoration-none">
            <div class="card h-100 shadow-sm border-primary border-opacity-25">
              <div class="card-body">
                <h3 class="h6 text-primary mb-2">{{ link.title }}</h3>
                <p class="small text-muted mb-0">{{ link.description }}</p>
              </div>
            </div>
          </router-link>
        </div>
      </div>
    </section>

    <section class="mb-5" aria-labelledby="tester-heading">
      <h2 id="tester-heading" class="h5 mb-2">Mode testeur</h2>
      <p class="text-muted small mb-3">
        Raccourcis de démonstration hors parcours d’onboarding admin — calibration encadrant et export
        audit séparés. Cible par défaut : <strong>{{ REFERENCE_GROUP_NAME }}</strong>.
      </p>
      <div v-if="loading" class="d-flex justify-content-center py-4">
        <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Chargement…</span></div>
      </div>
      <div v-else-if="canonicalGroup" class="card shadow-sm border-primary border-2">
        <div class="card-body">
          <div class="d-flex flex-wrap align-items-center justify-content-between gap-3">
            <div>
              <h3 class="h6 mb-1">{{ canonicalGroup.name }}</h3>
              <p class="small text-muted mb-0">
                Cohorte préconfigurée — choisir calibration encadrant ou export audit.
              </p>
            </div>
            <div class="d-flex flex-wrap gap-2">
              <button
                type="button"
                class="btn btn-primary"
                data-testid="dashboard-tester-canonical"
                @click="openGroupCalibration(canonicalGroup)"
              >
                Calibration encadrant
                <i class="bi bi-chevron-right ms-1" aria-hidden="true"></i>
              </button>
              <button
                type="button"
                class="btn btn-outline-secondary"
                data-testid="dashboard-tester-exports"
                @click="openGroupExports(canonicalGroup)"
              >
                Export audit (Felix-ready)
              </button>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="alert alert-warning mb-0" role="alert">
        Raccourci démo : le groupe « {{ REFERENCE_GROUP_NAME }} » est introuvable dans cette organisation.
        <router-link to="/groups-admin" class="alert-link">Créer ou vérifier les groupes</router-link>.
      </div>

      <details v-if="otherGroups.length" class="mt-3 other-groups-panel">
        <summary class="small text-muted">
          Autres groupes ({{ otherGroups.length }})
          <span v-if="debugGroupCount"> — dont {{ debugGroupCount }} temporaire(s) / audit</span>
        </summary>
        <ul class="list-group list-group-flush mt-2 border rounded">
          <li
            v-for="g in otherGroups"
            :key="g.id"
            class="list-group-item d-flex flex-wrap align-items-center justify-content-between gap-2 py-2"
          >
            <span class="small">
              {{ g.name }}
              <span v-if="isDebugGroupName(g.name)" class="badge text-bg-secondary ms-1">debug</span>
            </span>
            <div class="d-flex flex-wrap gap-1">
              <button type="button" class="btn btn-outline-primary btn-sm" @click="openGroupCalibration(g)">
                Calibration
              </button>
              <button type="button" class="btn btn-outline-secondary btn-sm" @click="openGroupExports(g)">
                Exports
              </button>
            </div>
          </li>
        </ul>
      </details>
    </section>

    <aside v-if="auth.isAdminLike" class="mt-5 pt-3 border-top">
      <p class="small text-muted mb-0">{{ PLATFORM_VERSION_ADMIN_LINE }}</p>
    </aside>
  </div>
</template>
