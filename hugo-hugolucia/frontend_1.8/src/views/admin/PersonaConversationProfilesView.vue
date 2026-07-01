<script setup>
/**
 * Admin — PersonaConversationProfile (tuteur / formateur)
 * Routes: /admin/conversation/:personaKind/profiles[(/new|:id)]
 * API:
 *   GET/POST  /hugo/persona-conversation-profiles/?persona=tutor|trainer
 *   GET/PATCH/DELETE /hugo/persona-conversation-profiles/:id/
 *   POST /hugo/persona-conversation-profiles/:id/preview-render/
 */
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../api/client'
import { useAuthStore } from '../../stores/auth'
import { useTenantStore } from '../../stores/tenant'

const props = defineProps({
  personaKind: {
    type: String,
    required: true,
    validator: (v) => ['tutor', 'trainer'].includes(v),
  },
  personaLabel: {
    type: String,
    required: true,
  },
  orchestratorRoute: {
    type: String,
    required: true,
  },
})

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const tenant = useTenantStore()

const profiles = ref([])
const loading = ref(false)
const saving = ref(false)
const previewing = ref(false)
const deleting = ref(false)
const error = ref('')
const success = ref('')
const previewResult = ref(null)

const editorMode = ref('list')
const form = ref(createEmptyForm())

const profileIdParam = computed(() => {
  if (route.name?.toString().includes('New') || route.path.endsWith('/profiles/new')) {
    return 'new'
  }
  return String(route.params.profileId || '')
})
const showEditorPanel = computed(() => editorMode.value === 'create' || editorMode.value === 'edit')

const activeOrgLabel = computed(() => {
  if (auth.isSuperAdmin && tenant.activeOrganisationName) return tenant.activeOrganisationName
  return auth.user?.organisation_name || ''
})

const availableVariables = [
  'situation_content',
  'history_block',
  'referential_block',
  'persona_context_block',
  'tutor_context_block',
  'trainer_context_block',
  'organisation_id',
  'session_id',
]

function createEmptyForm() {
  return {
    code: '',
    name: '',
    description: '',
    status: 'active',
    is_default: false,
    system_template: '',
    user_template: 'Situation ou question :\n{situation_content}',
  }
}

function resetForm() {
  form.value = createEmptyForm()
}

function syncFormFromProfile(profile) {
  if (!profile) {
    resetForm()
    return
  }
  const prompt = profile.tutor_prompt || {}
  form.value = {
    code: profile.code || '',
    name: profile.name || '',
    description: profile.description || '',
    status: profile.status || 'active',
    is_default: !!profile.is_default,
    system_template: prompt.system_template || '',
    user_template: prompt.user_template || '',
  }
}

async function loadProfiles() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/hugo/persona-conversation-profiles/', {
      params: { persona: props.personaKind },
    })
    profiles.value = Array.isArray(data) ? data : data.results || []
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur chargement profils persona.'
    profiles.value = []
  } finally {
    loading.value = false
  }
}

function openList() {
  editorMode.value = 'list'
  previewResult.value = null
  router.push({ path: `/admin/conversation/${props.personaKind}/profiles` })
}

function openCreate() {
  editorMode.value = 'create'
  resetForm()
  previewResult.value = null
  router.push({ path: `/admin/conversation/${props.personaKind}/profiles/new` })
}

function openEdit(profile) {
  editorMode.value = 'edit'
  syncFormFromProfile(profile)
  previewResult.value = null
  router.push({
    path: `/admin/conversation/${props.personaKind}/profiles/${profile.id}`,
  })
}

async function saveProfile() {
  if (!form.value.code?.trim() || !form.value.name?.trim()) {
    error.value = 'Code et nom requis.'
    return
  }
  saving.value = true
  error.value = ''
  success.value = ''
  const payload = {
    persona: props.personaKind,
    code: form.value.code.trim(),
    name: form.value.name.trim(),
    description: form.value.description || '',
    status: form.value.status,
    is_default: !!form.value.is_default,
    system_template: form.value.system_template,
    user_template: form.value.user_template,
  }
  try {
    if (editorMode.value === 'edit' && profileIdParam.value && profileIdParam.value !== 'new') {
      await api.patch(`/hugo/persona-conversation-profiles/${profileIdParam.value}/`, payload)
      success.value = 'Profil mis à jour.'
    } else {
      const { data } = await api.post('/hugo/persona-conversation-profiles/', payload)
      success.value = 'Profil créé.'
      editorMode.value = 'edit'
      router.replace({
        path: `/admin/conversation/${props.personaKind}/profiles/${data.id}`,
      })
    }
    await loadProfiles()
  } catch (e) {
    error.value = JSON.stringify(e.response?.data || e.message)
  } finally {
    saving.value = false
  }
}

async function duplicateProfile(profile) {
  const prompt = profile.tutor_prompt || {}
  form.value = {
    code: `${profile.code}_copy`,
    name: `${profile.name} (copie)`,
    description: profile.description || '',
    status: 'draft',
    is_default: false,
    system_template: prompt.system_template || '',
    user_template: prompt.user_template || '',
  }
  editorMode.value = 'create'
  router.push({ path: `/admin/conversation/${props.personaKind}/profiles/new` })
}

async function archiveProfile(profile) {
  if (!confirm(`Archiver le profil « ${profile.name} » ?`)) return
  deleting.value = true
  try {
    await api.patch(`/hugo/persona-conversation-profiles/${profile.id}/`, { status: 'inactive' })
    success.value = 'Profil archivé.'
    await loadProfiles()
    if (profileIdParam.value === String(profile.id)) openList()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur archivage.'
  } finally {
    deleting.value = false
  }
}

async function previewRender() {
  if (editorMode.value === 'create' || !profileIdParam.value || profileIdParam.value === 'new') {
    error.value = 'Enregistrez le profil avant la prévisualisation.'
    return
  }
  previewing.value = true
  error.value = ''
  try {
    const { data } = await api.post(
      `/hugo/persona-conversation-profiles/${profileIdParam.value}/preview-render/`,
      {
        system_template: form.value.system_template,
        user_template: form.value.user_template,
        sample_content: 'Message d’exemple pour prévisualisation.',
      },
    )
    previewResult.value = data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur prévisualisation.'
  } finally {
    previewing.value = false
  }
}

async function syncRouteToEditor() {
  await loadProfiles()
  const id = profileIdParam.value
  if (!id || id === 'new') {
    if (route.path.endsWith('/new')) {
      editorMode.value = 'create'
      if (!form.value.code) resetForm()
    } else {
      editorMode.value = 'list'
    }
    return
  }
  const profile = profiles.value.find((p) => String(p.id) === id)
  if (profile) {
    editorMode.value = 'edit'
    syncFormFromProfile(profile)
  }
}

watch(() => route.fullPath, syncRouteToEditor)
onMounted(syncRouteToEditor)
</script>

<template>
  <div class="container-fluid">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item"><router-link to="/dashboard">Tableau de bord</router-link></li>
        <li class="breadcrumb-item"><router-link to="/admin/conversation">Configuration conversation</router-link></li>
        <li class="breadcrumb-item">
          <router-link :to="orchestratorRoute">Orchestrateur {{ personaLabel.toLowerCase() }}</router-link>
        </li>
        <li class="breadcrumb-item active" aria-current="page">Profils {{ personaLabel.toLowerCase() }}</li>
      </ol>
    </nav>

    <header class="d-flex flex-wrap justify-content-between align-items-start gap-2 mb-4">
      <div>
        <h1 class="h4 mb-1">{{ personaLabel }} — profils conversationnels</h1>
        <p class="text-muted small mb-0">
          Templates system/user persona. N’affecte pas les profils apprenant.
          <span v-if="activeOrgLabel">Organisation : {{ activeOrgLabel }}</span>
        </p>
      </div>
      <div class="d-flex gap-2">
        <button v-if="showEditorPanel" type="button" class="btn btn-sm btn-outline-secondary" @click="openList">
          Retour liste
        </button>
        <button v-else type="button" class="btn btn-sm btn-primary" @click="openCreate">
          Nouveau profil
        </button>
      </div>
    </header>

    <div v-if="error" class="alert alert-danger small">{{ error }}</div>
    <div v-if="success" class="alert alert-success small">{{ success }}</div>

    <div v-if="!showEditorPanel" class="card shadow-sm">
      <div class="card-body p-0">
        <div v-if="loading" class="p-4 text-center text-muted">Chargement…</div>
        <table v-else class="table table-sm mb-0 align-middle">
          <thead>
            <tr>
              <th>Code</th>
              <th>Nom</th>
              <th>Statut</th>
              <th>Défaut</th>
              <th class="text-end">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="profile in profiles" :key="profile.id">
              <td><code>{{ profile.code }}</code></td>
              <td>{{ profile.name }}</td>
              <td>{{ profile.status }}</td>
              <td>{{ profile.is_default ? 'oui' : '—' }}</td>
              <td class="text-end">
                <button type="button" class="btn btn-sm btn-outline-primary me-1" @click="openEdit(profile)">
                  Éditer
                </button>
                <button type="button" class="btn btn-sm btn-outline-secondary me-1" @click="duplicateProfile(profile)">
                  Dupliquer
                </button>
                <button
                  type="button"
                  class="btn btn-sm btn-outline-danger"
                  :disabled="deleting"
                  @click="archiveProfile(profile)"
                >
                  Archiver
                </button>
              </td>
            </tr>
            <tr v-if="!profiles.length">
              <td colspan="5" class="text-muted text-center py-4">Aucun profil persona.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-else class="row g-3">
      <div class="col-lg-7">
        <div class="card shadow-sm">
          <div class="card-body d-grid gap-3">
            <div class="row g-2">
              <div class="col-md-6">
                <label class="form-label">Code</label>
                <input v-model="form.code" class="form-control form-control-sm" :disabled="editorMode === 'edit'" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Nom</label>
                <input v-model="form.name" class="form-control form-control-sm" />
              </div>
            </div>
            <div>
              <label class="form-label">Description</label>
              <textarea v-model="form.description" class="form-control form-control-sm" rows="2" />
            </div>
            <div class="row g-2">
              <div class="col-md-6">
                <label class="form-label">Statut</label>
                <select v-model="form.status" class="form-select form-select-sm">
                  <option value="draft">Brouillon</option>
                  <option value="active">Actif</option>
                  <option value="inactive">Inactif</option>
                </select>
              </div>
              <div class="col-md-6 d-flex align-items-end">
                <div class="form-check">
                  <input id="is_default" v-model="form.is_default" class="form-check-input" type="checkbox" />
                  <label class="form-check-label" for="is_default">Profil par défaut</label>
                </div>
              </div>
            </div>
            <div>
              <label class="form-label">System template</label>
              <textarea v-model="form.system_template" class="form-control form-control-sm font-monospace" rows="8" />
            </div>
            <div>
              <label class="form-label">User template</label>
              <textarea v-model="form.user_template" class="form-control form-control-sm font-monospace" rows="4" />
            </div>
            <div class="d-flex gap-2">
              <button type="button" class="btn btn-primary btn-sm" :disabled="saving" @click="saveProfile">
                {{ saving ? 'Enregistrement…' : 'Enregistrer' }}
              </button>
              <button
                type="button"
                class="btn btn-outline-secondary btn-sm"
                :disabled="previewing"
                @click="previewRender"
              >
                {{ previewing ? 'Prévisualisation…' : 'Prévisualiser (sans LLM)' }}
              </button>
            </div>
          </div>
        </div>
      </div>
      <div class="col-lg-5">
        <div class="card shadow-sm mb-3">
          <div class="card-header py-2"><strong class="small">Variables disponibles</strong></div>
          <div class="card-body small">
            <code v-for="v in availableVariables" :key="v" class="d-block mb-1">{{ '{' + v + '}' }}</code>
          </div>
        </div>
        <div v-if="previewResult" class="card shadow-sm">
          <div class="card-header py-2"><strong class="small">Aperçu rendu</strong></div>
          <div class="card-body small">
            <p class="fw-semibold mb-1">System</p>
            <pre class="bg-light p-2 rounded small mb-3">{{ previewResult.system_prompt }}</pre>
            <p class="fw-semibold mb-1">User</p>
            <pre class="bg-light p-2 rounded small">{{ previewResult.user_prompt }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
