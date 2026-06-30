<script setup>
/**
 * Admin — LearnerConversationGlobalProfile (CRUD)
 * Routes: /admin/conversation/learner/profiles[(/new|:id)]
 * API:
 *   GET/POST  /hugo/learner-conversation-profiles/
 *   GET/PATCH/DELETE /hugo/learner-conversation-profiles/:id/
 *   GET /hugo/learner-conversation-profiles/legacy-template/  (prefill depuis modes legacy)
 * Références: GET /hugo/tutor-prompts/, /hugo/conduct-profiles/, evaluation-* (slots optionnels)
 * Payload create: { name*, description, status, is_default, *_tutor_prompt_id, *_conduct_profile_id, evaluation_* }
 * Slots posture (alignés modèle back) :
 *   - *_tutor_prompt_id → TutorPrompt (prompt orchestrateur apprenant, templates system/user)
 *   - *_conduct_profile_id → TutorConductProfile (règles posture : gestes, max questions, etc.)
 * Les deux familles sont consommées par le moteur ; pas d’inversion front/back.
 * Apprenant: ProdLearnerHomeView consomme les profils actifs via learner_conversation_profile_id (pas tutor_prompt_id).
 */
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../api/client'
import { useAuthStore } from '../../stores/auth'
import { useTenantStore } from '../../stores/tenant'
import { LEARNER_POSTURES } from '../../constants/conversationPostures'
import {
  completenessBadgeClass,
  completenessLabel,
  COMPLETENESS_LEGEND,
} from '../../utils/learnerProfileCompleteness'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const tenant = useTenantStore()

const profiles = ref([])
const tutorPrompts = ref([])
const conductProfiles = ref([])
const evaluationProfiles = ref([])
const evaluationPolicies = ref([])
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const prefilling = ref(false)
const error = ref('')
const success = ref('')

/** UI mode — updated immediately on button click, synced with route. */
const editorMode = ref('list') // list | create | edit
const preserveFormOnCreate = ref(false)

const selectedId = ref('')
const form = ref(createEmptyForm())

const profileIdParam = computed(() => {
  if (route.name === 'AdminLearnerProfilesNew' || route.path.endsWith('/profiles/new')) {
    return 'new'
  }
  return String(route.params.profileId || '')
})
const isCreate = computed(() => editorMode.value === 'create')
const isEdit = computed(() => editorMode.value === 'edit')
const showEditorPanel = computed(() => editorMode.value === 'create' || editorMode.value === 'edit')

const activeOrgLabel = computed(() => {
  if (auth.isSuperAdmin && tenant.activeOrganisationName) return tenant.activeOrganisationName
  return auth.user?.organisation_name || ''
})

const attributionGroupId = computed(() => {
  const q = route.query.groupId
  return q ? String(q) : ''
})

const showAttributionCallout = computed(() => {
  if (!success.value) return false
  return /profil (créé|mis à jour)/i.test(success.value)
})

function preserveGroupQuery() {
  const query = {}
  if (attributionGroupId.value) query.groupId = attributionGroupId.value
  return query
}

const postureSlots = computed(() =>
  LEARNER_POSTURES.map((p) => ({
    code: p.code,
    label: p.code === 'knowledge_review' ? 'Bûchage' : p.label,
    promptField: `${p.code === 'diagnostic' ? 'diagnostic' : p.code === 'reflective_afest' ? 'reflective' : 'knowledge_review'}_tutor_prompt_id`,
    conductField: `${p.code === 'diagnostic' ? 'diagnostic' : p.code === 'reflective_afest' ? 'reflective' : 'knowledge_review'}_conduct_profile_id`,
  }))
)

function createEmptyForm() {
  return {
    name: '',
    description: '',
    status: 'active',
    is_default: false,
    diagnostic_tutor_prompt_id: '',
    reflective_tutor_prompt_id: '',
    knowledge_review_tutor_prompt_id: '',
    diagnostic_conduct_profile_id: '',
    reflective_conduct_profile_id: '',
    knowledge_review_conduct_profile_id: '',
    evaluation_prompt_profile_id: '',
    evaluation_policy_id: '',
  }
}

function fkId(value) {
  if (value == null || value === '') return ''
  if (typeof value === 'object' && value.id != null) return String(value.id)
  return String(value)
}

function promptsForPosture(code) {
  return tutorPrompts.value.filter(
    (p) => p.is_active !== false && String(p.conversation_profile || '') === code,
  )
}

function conductForPosture(code) {
  return conductProfiles.value.filter(
    (c) => c.is_active !== false && String(c.posture || '') === code,
  )
}

function conductOptionLabel(profile) {
  const title = (profile.description || '').trim() || profile.posture || '—'
  const scope = profile.organisation ? 'organisation' : 'système'
  return `${title} (${scope})`
}

function evaluationProfilesForSelect() {
  return evaluationProfiles.value.filter((ep) => ep.is_active !== false)
}

/** Drop slot FK values that no longer match the expected reference type/posture. */
function sanitizeSlotReferences() {
  for (const slot of postureSlots.value) {
    const promptId = form.value[slot.promptField]
    if (promptId && !promptsForPosture(slot.code).some((p) => String(p.id) === String(promptId))) {
      form.value[slot.promptField] = ''
    }
    const conductId = form.value[slot.conductField]
    if (conductId && !conductForPosture(slot.code).some((c) => String(c.id) === String(conductId))) {
      form.value[slot.conductField] = ''
    }
  }
  const evalProfileId = form.value.evaluation_prompt_profile_id
  if (
    evalProfileId
    && !evaluationProfilesForSelect().some((ep) => String(ep.id) === String(evalProfileId))
  ) {
    form.value.evaluation_prompt_profile_id = ''
  }
  const policyId = form.value.evaluation_policy_id
  if (policyId && !evaluationPolicies.value.some((pol) => String(pol.id) === String(policyId))) {
    form.value.evaluation_policy_id = ''
  }
}

function defaultEmptyProfileName() {
  const stamp = new Date().toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' })
  return `Profil conversationnel ${stamp}`
}

function resetForm() {
  form.value = createEmptyForm()
}

function syncFormFromProfile(profile) {
  if (!profile) {
    resetForm()
    return
  }
  form.value = {
    name: profile.name || '',
    description: profile.description || '',
    status: profile.status || 'active',
    is_default: !!profile.is_default,
    diagnostic_tutor_prompt_id: fkId(profile.diagnostic_tutor_prompt),
    reflective_tutor_prompt_id: fkId(profile.reflective_tutor_prompt),
    knowledge_review_tutor_prompt_id: fkId(profile.knowledge_review_tutor_prompt),
    diagnostic_conduct_profile_id: fkId(profile.diagnostic_conduct_profile),
    reflective_conduct_profile_id: fkId(profile.reflective_conduct_profile),
    knowledge_review_conduct_profile_id: fkId(profile.knowledge_review_conduct_profile),
    evaluation_prompt_profile_id: fkId(profile.evaluation_prompt_profile),
    evaluation_policy_id: fkId(profile.evaluation_policy),
  }
  sanitizeSlotReferences()
}

function applyLegacySuggestions(data) {
  if (!data) return
  if (!form.value.name && data.name_suggestion) {
    form.value.name = data.name_suggestion
  }
  if (!form.value.description && data.description_suggestion) {
    form.value.description = data.description_suggestion
  }
  for (const key of Object.keys(form.value)) {
    if (!key.endsWith('_id')) continue
    const suggested = data[key]
    if (suggested && !form.value[key]) {
      form.value[key] = String(suggested)
    }
  }
}

function formatApiError(e) {
  const data = e.response?.data
  if (!data) return e.message || 'Erreur inattendue.'
  if (typeof data === 'string') return data
  if (data.detail) return String(data.detail)
  if (typeof data === 'object') {
    const flat = Object.entries(data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
    if (flat.length) return flat.join(' · ')
  }
  return 'Erreur lors de l’opération.'
}

async function loadReferenceData() {
  const loadList = async (url, label) => {
    try {
      const { data } = await api.get(url)
      return Array.isArray(data) ? data : (data.results || [])
    } catch (err) {
      console.warn(`[LearnerConversationProfiles] ${label} (${url}):`, err.response?.data || err.message)
      return []
    }
  }
  const [prompts, conduct, evalProf, evalPol] = await Promise.all([
    loadList('/hugo/tutor-prompts/', 'tutor-prompts'),
    loadList('/hugo/conduct-profiles/', 'conduct-profiles'),
    loadList('/hugo/evaluation-prompt-profiles/', 'evaluation-prompt-profiles'),
    loadList('/hugo/evaluation-policies/', 'evaluation-policies'),
  ])
  tutorPrompts.value = prompts
  conductProfiles.value = conduct
  evaluationProfiles.value = evalProf
  evaluationPolicies.value = evalPol.filter((p) => !p.group)
  sanitizeSlotReferences()
}

async function loadProfiles() {
  loading.value = true
  error.value = ''
  try {
    await loadReferenceData()
    const { data } = await api.get('/hugo/learner-conversation-profiles/')
    profiles.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    error.value = formatApiError(e)
  } finally {
    loading.value = false
  }
}

async function syncRouteState() {
  const param = profileIdParam.value

  if (param === 'new') {
    editorMode.value = 'create'
    selectedId.value = ''
    if (!preserveFormOnCreate.value && !form.value.name?.trim()) {
      resetForm()
    }
    return
  }

  if (!param) {
    editorMode.value = 'list'
    selectedId.value = ''
    return
  }

  editorMode.value = 'edit'
  selectedId.value = param
  const profile = profiles.value.find((p) => String(p.id) === selectedId.value)
  if (profile) {
    syncFormFromProfile(profile)
    return
  }
  try {
    const { data } = await api.get(`/hugo/learner-conversation-profiles/${selectedId.value}/`)
    syncFormFromProfile(data)
  } catch (e) {
    error.value = formatApiError(e)
    cancelEdit()
  }
}

function buildPayload() {
  const payload = { ...form.value }
  for (const key of Object.keys(payload)) {
    if (key.endsWith('_id') && payload[key] === '') {
      payload[key] = null
    }
  }
  return payload
}

async function saveProfile() {
  if (!form.value.name?.trim() || saving.value) return
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    const payload = buildPayload()
    if (isEdit.value && selectedId.value) {
      await api.patch(`/hugo/learner-conversation-profiles/${selectedId.value}/`, payload)
      success.value = 'Profil mis à jour.'
      await loadProfiles()
    } else {
      const { data } = await api.post('/hugo/learner-conversation-profiles/', payload)
      selectedId.value = data.id
      editorMode.value = 'edit'
      preserveFormOnCreate.value = false
      success.value = 'Profil créé.'
      await router.replace({
        path: `/admin/conversation/learner/profiles/${data.id}`,
        query: preserveGroupQuery(),
      })
      await loadProfiles()
    }
  } catch (e) {
    error.value = formatApiError(e)
  } finally {
    saving.value = false
  }
}

async function deleteProfile() {
  if (!isEdit.value || !selectedId.value || deleting.value) return
  if (!window.confirm('Supprimer ce profil conversationnel global ?')) return
  deleting.value = true
  error.value = ''
  try {
    await api.delete(`/hugo/learner-conversation-profiles/${selectedId.value}/`)
    success.value = 'Profil supprimé.'
    cancelEdit()
    await loadProfiles()
  } catch (e) {
    error.value = formatApiError(e)
  } finally {
    deleting.value = false
  }
}

async function prefillFromLegacy() {
  prefilling.value = true
  error.value = ''
  try {
    const { data } = await api.get('/hugo/learner-conversation-profiles/legacy-template/')
    if (!data?.has_legacy_data) {
      error.value = 'Aucune configuration legacy trouvée pour cette organisation.'
      return false
    }
    applyLegacySuggestions(data)
    sanitizeSlotReferences()
    success.value = `Prérempli depuis legacy (${data.filled_slots} slot(s)). Vérifiez le nom puis enregistrez.`
    return true
  } catch (e) {
    error.value = formatApiError(e)
    return false
  } finally {
    prefilling.value = false
  }
}

function openCreate() {
  preserveFormOnCreate.value = false
  editorMode.value = 'create'
  selectedId.value = ''
  resetForm()
  form.value.name = defaultEmptyProfileName()
  error.value = ''
  success.value = ''
  router.push({ path: '/admin/conversation/learner/profiles/new', query: preserveGroupQuery() }).catch(() => {})
}

async function openCreateFromLegacy() {
  preserveFormOnCreate.value = true
  editorMode.value = 'create'
  selectedId.value = ''
  resetForm()
  error.value = ''
  success.value = ''
  try {
    await router.push({ path: '/admin/conversation/learner/profiles/new', query: preserveGroupQuery() })
    const ok = await prefillFromLegacy()
    if (ok && !form.value.name?.trim()) {
      form.value.name = defaultEmptyProfileName()
    }
  } catch (err) {
    console.error('[LearnerConversationProfiles] openCreateFromLegacy:', err)
    error.value = 'Impossible d’ouvrir l’éditeur de création depuis les modes existants.'
  } finally {
    preserveFormOnCreate.value = false
  }
}

function openProfile(id) {
  router.push({ path: `/admin/conversation/learner/profiles/${id}`, query: preserveGroupQuery() })
}

function cancelEdit() {
  preserveFormOnCreate.value = false
  editorMode.value = 'list'
  selectedId.value = ''
  router.push('/admin/conversation/learner/profiles').catch(() => {})
}

watch(profileIdParam, () => {
  syncRouteState()
})

watch(
  () => tenant.activeOrganisationId,
  async () => {
    if (loading.value) return
    await loadProfiles()
    await syncRouteState()
  },
)

onMounted(async () => {
  await loadProfiles()
  await syncRouteState()
})
</script>

<template>
  <div class="container-fluid" data-testid="learner-profiles-page">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item"><router-link to="/dashboard">Tableau de bord</router-link></li>
        <li class="breadcrumb-item"><router-link to="/admin/conversation">Configuration conversation</router-link></li>
        <li class="breadcrumb-item active" aria-current="page">Profils conversationnels apprenant</li>
      </ol>
    </nav>

    <header class="mb-4">
      <h1 class="h4 mb-1">Profils conversationnels apprenant</h1>
      <p class="text-muted mb-0">
        Objet admin regroupant diag, réflexif, bûchage et évaluation finale.
        L’apprenant choisit uniquement son <strong>mode conversationnel</strong> en séance ;
        le profil global est attribué au <strong>groupe</strong> par l’administrateur.
      </p>
      <p v-if="activeOrgLabel" class="small text-muted mb-0 mt-1">
        Organisation active : <strong>{{ activeOrgLabel }}</strong>
        <span v-if="auth.isSuperAdmin" class="text-warning"> (vérifiez le sélecteur d’org en barre de navigation)</span>
      </p>
      <p class="small text-muted mb-0 mt-2">
        Complétude :
        <span
          class="text-primary"
          data-bs-toggle="tooltip"
          :title="COMPLETENESS_LEGEND"
        >{{ COMPLETENESS_LEGEND }}</span>
      </p>
    </header>

    <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
    <div v-if="success" class="alert alert-success" role="status">{{ success }}</div>
    <div
      v-if="showAttributionCallout"
      class="alert alert-info"
      role="status"
      data-testid="profile-attribution-hint"
    >
      <strong>Étape suivante :</strong>
      la création ou la mise à jour du profil ne l’active pas sur un groupe.
      Attribuez-le dans la fiche groupe admin, section « Profil conversationnel du groupe ».
      <template v-if="attributionGroupId">
        <router-link
          :to="`/groups-admin/${attributionGroupId}?section=conversation`"
          class="alert-link ms-1"
        >
          Ouvrir la fiche du groupe
        </router-link>
      </template>
      <template v-else>
        <router-link to="/groups-admin" class="alert-link ms-1">Gérer les groupes</router-link>
      </template>
    </div>

    <div class="row g-4">
      <div class="col-12 col-lg-4">
        <div class="card shadow-sm">
          <div class="card-header d-flex justify-content-between align-items-center">
            <span class="fw-semibold">Profils</span>
            <button
              type="button"
              class="btn btn-primary btn-sm"
              data-testid="learner-profile-create-btn"
              @click="openCreate"
            >
              Créer
            </button>
          </div>
          <div class="list-group list-group-flush">
            <button
              v-for="profile in profiles"
              :key="profile.id"
              type="button"
              class="list-group-item list-group-item-action text-start"
              :class="{ active: String(profile.id) === selectedId }"
              data-testid="learner-profile-list-item"
              @click="openProfile(profile.id)"
            >
              <div class="d-flex justify-content-between align-items-start gap-2">
                <div class="fw-semibold">{{ profile.name }}</div>
                <span
                  class="badge rounded-pill"
                  :class="completenessBadgeClass(profile)"
                  :title="(profile.warnings || []).join(' ')"
                >
                  {{ completenessLabel(profile) }}
                </span>
              </div>
              <small class="text-muted">
                {{ profile.status }}
                <span v-if="profile.is_default"> · défaut org</span>
              </small>
              <div v-if="profile.missing_slots?.length" class="small text-warning mt-1">
                Manque : {{ profile.missing_slots.slice(0, 3).join(', ') }}
                <span v-if="profile.missing_slots.length > 3">…</span>
              </div>
            </button>
            <div v-if="loading" class="list-group-item text-muted small">Chargement…</div>
            <div v-else-if="!profiles.length" class="list-group-item text-muted small">
              Aucun profil global. Utilisez « Créer un profil vide ».
            </div>
          </div>
          <div class="card-footer bg-light border-top">
            <p class="small fw-semibold mb-2 text-muted">Compatibilité 1.6 / Import legacy</p>
            <button
              type="button"
              class="btn btn-sm btn-outline-secondary"
              data-testid="learner-profile-create-legacy-btn"
              :disabled="prefilling"
              @click="openCreateFromLegacy"
            >
              {{ prefilling ? 'Chargement…' : 'Créer depuis legacy' }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="!showEditorPanel" class="col-12 col-lg-8">
        <div class="card shadow-sm border-primary border-opacity-25">
          <div class="card-body">
            <h2 class="h6">Créer un profil conversationnel global</h2>
            <p class="text-muted small mb-3">
              Sélectionnez un profil dans la liste ou créez-en un nouveau.
            </p>
            <button
              type="button"
              class="btn btn-primary"
              data-testid="learner-profile-create-empty-btn"
              @click="openCreate"
            >
              Créer un profil vide
            </button>
          </div>
        </div>
        <div class="card shadow-sm mt-3 border-secondary border-opacity-50">
          <div class="card-body py-3">
            <h3 class="h6 text-muted mb-2">Compatibilité 1.6 / Import legacy</h3>
            <p class="small text-muted mb-2">
              Préremplit un profil à partir des modes TutorPrompt / conduct existants — chemin de migration, pas le flux principal.
            </p>
            <button
              type="button"
              class="btn btn-outline-secondary btn-sm"
              data-testid="learner-profile-create-legacy-main-btn"
              :disabled="prefilling"
              @click="openCreateFromLegacy"
            >
              Créer à partir des modes existants (legacy)
            </button>
          </div>
        </div>
      </div>

      <div v-else class="col-12 col-lg-8" data-testid="learner-profile-editor">
        <div class="card shadow-sm">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <h2 class="h6 mb-0">{{ isCreate ? 'Nouveau profil global' : 'Édition du profil' }}</h2>
              <button type="button" class="btn btn-sm btn-outline-secondary" @click="cancelEdit">Retour liste</button>
            </div>

            <div class="mb-3">
              <label class="form-label" for="profile-name">Nom du profil <span class="text-danger">*</span></label>
              <input
                id="profile-name"
                v-model="form.name"
                data-testid="learner-profile-name-input"
                class="form-control"
                type="text"
                required
                placeholder="Ex. AFEST standard"
              />
            </div>
            <div class="mb-3">
              <label class="form-label" for="profile-description">Description</label>
              <textarea id="profile-description" v-model="form.description" class="form-control" rows="2" />
            </div>
            <div class="row mb-3">
              <div class="col-md-6">
                <label class="form-label" for="profile-status">Statut</label>
                <select id="profile-status" v-model="form.status" class="form-select">
                  <option value="draft">Brouillon</option>
                  <option value="active">Actif</option>
                  <option value="inactive">Inactif</option>
                </select>
              </div>
              <div class="col-md-6 d-flex align-items-end">
                <div class="form-check">
                  <input id="isDefault" v-model="form.is_default" class="form-check-input" type="checkbox" />
                  <label class="form-check-label" for="isDefault">Profil par défaut (organisation)</label>
                </div>
              </div>
            </div>

            <div v-if="isCreate" class="d-flex flex-wrap gap-2 mb-3">
              <button
                type="button"
                class="btn btn-sm btn-outline-secondary"
                :disabled="prefilling"
                @click="prefillFromLegacy"
              >
                {{ prefilling ? 'Chargement…' : 'Préremplir depuis legacy' }}
              </button>
            </div>

            <h3 class="h6 mt-2">Modes conversationnels (postures)</h3>
            <p class="small text-muted mb-2">
              Deux réglages distincts par posture, tous deux consommés par le moteur :
              le <strong>prompt orchestrateur</strong> (templates system/user — identifiant technique du TutorPrompt, ex. code posture)
              et le <strong>profil de conduite</strong> (règles posture : gestes interdits, max questions, etc.).
              Laisser vide = repli org / système / legacy.
            </p>
            <p class="small text-muted mb-3">
              Édition détaillée par posture :
              <router-link to="/admin/conversation/learner/diagnostic">Diagnostic</router-link>,
              <router-link to="/admin/conversation/learner/reflective_afest">Réflexif</router-link>,
              <router-link to="/admin/conversation/learner/knowledge_review">Bûchage</router-link>.
            </p>
            <div v-for="slot in postureSlots" :key="slot.code" class="border rounded p-3 mb-3">
              <h4 class="h6 mb-2">{{ slot.label }}</h4>
              <div class="mb-2">
                <label class="form-label small">Prompt orchestrateur apprenant (TutorPrompt, optionnel)</label>
                <select v-model="form[slot.promptField]" class="form-select form-select-sm">
                  <option value="">— héritage org / legacy —</option>
                  <option v-for="p in promptsForPosture(slot.code)" :key="p.id" :value="p.id">
                    {{ p.name }} ({{ p.code }})
                  </option>
                </select>
                <p class="small text-muted mb-0 mt-1">
                  Templates system/user du tour LLM. Modèle back : <code>{{ slot.promptField.replace('_id', '') }}</code>.
                </p>
              </div>
              <div>
                <label class="form-label small">Profil de conduite (TutorConductProfile, optionnel)</label>
                <select v-model="form[slot.conductField]" class="form-select form-select-sm">
                  <option value="">— résolution org / système —</option>
                  <option v-for="c in conductForPosture(slot.code)" :key="c.id" :value="c.id">
                    {{ conductOptionLabel(c) }}
                  </option>
                </select>
                <p class="small text-muted mb-0 mt-1">
                  Règles de posture injectées dans le prompt. Modèle back : <code>{{ slot.conductField.replace('_id', '') }}</code>.
                </p>
              </div>
            </div>

            <h3 class="h6 mt-4">Évaluation finale</h3>
            <div class="border rounded p-3 mb-3">
              <div class="mb-2">
                <label class="form-label small">Profil d'évaluation</label>
                <select v-model="form.evaluation_prompt_profile_id" class="form-select form-select-sm">
                  <option value="">— héritage politique org —</option>
                  <option v-for="ep in evaluationProfilesForSelect()" :key="ep.id" :value="ep.id">
                    {{ ep.label }} ({{ ep.code }}){{ ep.organisation ? '' : ' · plateforme' }}
                  </option>
                </select>
              </div>
              <div>
                <label class="form-label small">Politique d'évaluation org (optionnel)</label>
                <select v-model="form.evaluation_policy_id" class="form-select form-select-sm">
                  <option value="">— get_or_create groupe/org —</option>
                  <option v-for="pol in evaluationPolicies" :key="pol.id" :value="pol.id">
                    Politique org #{{ pol.id }}
                  </option>
                </select>
              </div>
            </div>

            <div class="d-flex flex-wrap gap-2">
              <button
                type="button"
                class="btn btn-primary"
                data-testid="learner-profile-save-btn"
                :disabled="saving || !form.name?.trim()"
                @click="saveProfile"
              >
                {{ saving ? 'Enregistrement…' : (isCreate ? 'Créer le profil' : 'Enregistrer') }}
              </button>
              <button
                v-if="isEdit"
                type="button"
                class="btn btn-outline-danger"
                data-testid="learner-profile-delete-btn"
                :disabled="deleting"
                @click="deleteProfile"
              >
                {{ deleting ? 'Suppression…' : 'Supprimer' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
