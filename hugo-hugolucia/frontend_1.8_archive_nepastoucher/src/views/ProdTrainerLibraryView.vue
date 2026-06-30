<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api/client'
import {
  CONVERSATION_ROLES,
  PEDAGOGICAL_INTENTS,
  VISIBILITY_OPTIONS,
  approxDocumentSize,
  buildCreateDocumentPayload,
  buildDocumentMeta,
  buildPatchDocumentMetaPayload,
  intentLabel,
  isDocumentLinked,
  normalizeDocumentsList,
  normalizeLibraryItems,
  roleLabel,
} from '../utils/trainerLibrary.js'

const route = useRoute()
const router = useRouter()

const groups = ref([])
const groupId = ref('')
const libraryItems = ref([])
const orgDocuments = ref([])
const loading = ref(false)
const error = ref('')
const msg = ref('')
const actionLoading = ref(false)

const newDocTitle = ref('')
const newDocSourceText = ref('')
const newDocFile = ref(null)
const newDocConversationRole = ref('reference_course')
const newDocPedagogicalIntent = ref('explanation')
const newDocVisibility = ref('learner_citable')

const selectedGroup = computed(() => groups.value.find((g) => String(g.id) === String(groupId.value)))

async function loadGroups() {
  try {
    const { data } = await api.get('/groups/')
    groups.value = Array.isArray(data) ? data : data.results || []
  } catch (e) {
    error.value = e.response?.data?.detail || 'Impossible de charger les groupes.'
  }
}

async function loadLibrary() {
  if (!groupId.value) {
    libraryItems.value = []
    orgDocuments.value = []
    return
  }
  loading.value = true
  error.value = ''
  try {
    const [docsRes, libRes] = await Promise.all([
      api.get('/documents/'),
      api.get(`/groups/${groupId.value}/library/`),
    ])
    const d = docsRes.data
    orgDocuments.value = normalizeDocumentsList(d)
    libraryItems.value = normalizeLibraryItems(libRes.data)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Impossible de charger la bibliothèque.'
    libraryItems.value = []
    orgDocuments.value = []
  } finally {
    loading.value = false
  }
}

function onGroupChange() {
  router.replace({ query: { ...route.query, groupId: groupId.value || undefined } })
  loadLibrary()
}

function onFileChange(event) {
  const files = event.target.files
  newDocFile.value = files && files[0] ? files[0] : null
}

function buildMeta() {
  return buildDocumentMeta({
    conversationRole: newDocConversationRole.value,
    pedagogicalIntent: newDocPedagogicalIntent.value,
    visibility: newDocVisibility.value,
  })
}

async function createDocument() {
  if (!newDocTitle.value.trim() && !newDocFile.value) return
  actionLoading.value = true
  msg.value = ''
  error.value = ''
  try {
    let docId = null
    if (newDocFile.value) {
      const form = new FormData()
      form.append('file', newDocFile.value)
      form.append('title', newDocTitle.value.trim() || newDocFile.value.name)
      form.append('meta', JSON.stringify(buildMeta()))
      const { data } = await api.post('/documents/upload/', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      docId = data.id
    } else {
      const { data } = await api.post(
        '/documents/',
        buildCreateDocumentPayload({
          title: newDocTitle.value.trim(),
          sourceText: newDocSourceText.value || '',
          meta: buildMeta(),
        }),
      )
      docId = data.id
    }
    msg.value = 'Document créé. Indexez-le puis liez-le au groupe.'
    newDocTitle.value = ''
    newDocSourceText.value = ''
    newDocFile.value = null
    await loadLibrary()
    if (docId) await indexDocument(docId)
  } catch (e) {
    error.value = e.response?.data?.detail || e.response?.data?.meta || 'Création impossible.'
  } finally {
    actionLoading.value = false
  }
}

async function indexDocument(docId) {
  try {
    const { data } = await api.post(`/documents/${docId}/index/`)
    msg.value = `Indexation : ${data.chunks_count} chunk(s), ${data.quality_flag}.`
    await loadLibrary()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Indexation impossible.'
  }
}

async function linkDocument(docId) {
  if (!groupId.value) return
  actionLoading.value = true
  try {
    await api.post(`/groups/${groupId.value}/library/`, { document_id: docId })
    msg.value = 'Document lié au groupe.'
    await loadLibrary()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Liaison impossible.'
  } finally {
    actionLoading.value = false
  }
}

async function patchDocumentMeta(docId, metaPatch) {
  try {
    const doc = orgDocuments.value.find((d) => d.id === docId)
    await api.patch(`/documents/${docId}/`, buildPatchDocumentMetaPayload(doc?.meta, metaPatch))
    msg.value = 'Métadonnées mises à jour.'
    await loadLibrary()
  } catch (e) {
    error.value = e.response?.data?.detail || e.response?.data?.meta || 'Mise à jour impossible.'
  }
}

async function deactivateLink(gdId) {
  if (!groupId.value) return
  actionLoading.value = true
  try {
    await api.put(`/groups/${groupId.value}/library/${gdId}/`, { status: 'INACTIVE' })
    msg.value = 'Document retiré du groupe.'
    await loadLibrary()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Retrait impossible.'
  } finally {
    actionLoading.value = false
  }
}

function isLinked(docId) {
  return isDocumentLinked(libraryItems.value, docId)
}

function approxSize(doc) {
  return approxDocumentSize(doc.extracted_chars)
}

watch(
  () => route.query.groupId,
  (value) => {
    if (value && String(value) !== String(groupId.value)) {
      groupId.value = String(value)
      loadLibrary()
    }
  },
)

onMounted(async () => {
  await loadGroups()
  if (route.query.groupId) {
    groupId.value = String(route.query.groupId)
  } else if (groups.value.length === 1) {
    groupId.value = String(groups.value[0].id)
  }
  await loadLibrary()
})
</script>

<template>
  <div class="container-fluid px-0">
    <div class="d-flex flex-wrap justify-content-between align-items-center mb-3 gap-2">
      <div>
        <h1 class="h4 mb-1">Bibliothèque de cours</h1>
        <p class="text-muted small mb-0">
          Documents indexés pour le RAG conversationnel Hugo — par groupe.
        </p>
      </div>
      <router-link class="btn btn-sm btn-outline-secondary" :to="{ name: 'ProdTrainerKnowledge' }">
        Retour connaissance
      </router-link>
    </div>

    <div class="card mb-3">
      <div class="card-body row g-2 align-items-end">
        <div class="col-md-6">
          <label class="form-label small">Groupe</label>
          <select v-model="groupId" class="form-select form-select-sm" @change="onGroupChange">
            <option value="">— Choisir un groupe —</option>
            <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
        </div>
        <div class="col-md-6" v-if="selectedGroup">
          <span class="small text-muted">Groupe actif : <strong>{{ selectedGroup.name }}</strong></span>
        </div>
      </div>
    </div>

    <p v-if="loading" class="small text-muted">Chargement…</p>
    <p v-if="error" class="text-danger small">{{ error }}</p>
    <p v-if="msg" class="text-success small">{{ msg }}</p>

    <template v-if="groupId">
      <div class="card mb-4">
        <div class="card-header">Ajouter un document</div>
        <div class="card-body">
          <input v-model="newDocTitle" type="text" class="form-control form-control-sm mb-2" placeholder="Titre" />
          <textarea
            v-model="newDocSourceText"
            class="form-control form-control-sm mb-2"
            rows="4"
            placeholder="Texte brut (ou laisser vide si PDF)"
          />
          <input type="file" class="form-control form-control-sm mb-2" accept=".pdf,.txt,.md" @change="onFileChange" />
          <div class="row g-2 mb-2">
            <div class="col-md-4">
              <label class="form-label small">Rôle conversationnel</label>
              <select v-model="newDocConversationRole" class="form-select form-select-sm">
                <option v-for="opt in CONVERSATION_ROLES" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="form-label small">Intention pédagogique</label>
              <select v-model="newDocPedagogicalIntent" class="form-select form-select-sm">
                <option v-for="opt in PEDAGOGICAL_INTENTS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="form-label small">Visibilité</label>
              <select v-model="newDocVisibility" class="form-select form-select-sm">
                <option v-for="opt in VISIBILITY_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
            </div>
          </div>
          <button
            type="button"
            class="btn btn-sm btn-primary"
            :disabled="actionLoading || (!newDocTitle.trim() && !newDocFile)"
            @click="createDocument"
          >
            Créer et indexer
          </button>
        </div>
      </div>

      <div class="card mb-4">
        <div class="card-header">Documents de l'organisation</div>
        <div class="card-body table-responsive">
          <table v-if="orgDocuments.length" class="table table-sm align-middle">
            <thead>
              <tr>
                <th>Titre</th>
                <th>Taille</th>
                <th>Chunks</th>
                <th>Rôle</th>
                <th>Intent</th>
                <th>Visibilité</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="d in orgDocuments" :key="d.id">
                <td>{{ d.title }}</td>
                <td class="small">{{ approxSize(d) }}</td>
                <td>{{ d.chunks_count ?? 0 }}</td>
                <td>
                  <select
                    class="form-select form-select-sm"
                    :value="(d.meta && d.meta.conversation_role) || 'other'"
                    @change="patchDocumentMeta(d.id, { conversation_role: $event.target.value })"
                  >
                    <option v-for="opt in CONVERSATION_ROLES" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                  </select>
                </td>
                <td>
                  <select
                    class="form-select form-select-sm"
                    :value="(d.meta && d.meta.pedagogical_intent) || 'explanation'"
                    @change="patchDocumentMeta(d.id, { pedagogical_intent: $event.target.value })"
                  >
                    <option v-for="opt in PEDAGOGICAL_INTENTS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                  </select>
                </td>
                <td>
                  <select
                    class="form-select form-select-sm"
                    :value="(d.meta && d.meta.visibility) || 'learner_citable'"
                    @change="patchDocumentMeta(d.id, { visibility: $event.target.value })"
                  >
                    <option v-for="opt in VISIBILITY_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                  </select>
                </td>
                <td class="text-nowrap">
                  <button type="button" class="btn btn-sm btn-outline-secondary me-1" @click="indexDocument(d.id)">Indexer</button>
                  <button
                    v-if="!isLinked(d.id)"
                    type="button"
                    class="btn btn-sm btn-outline-success"
                    :disabled="actionLoading"
                    @click="linkDocument(d.id)"
                  >
                    Lier
                  </button>
                  <span v-else class="badge bg-success">Lié</span>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-else class="text-muted small mb-0">Aucun document.</p>
        </div>
      </div>

      <div class="card">
        <div class="card-header">Bibliothèque active du groupe</div>
        <ul v-if="libraryItems.filter((x) => x.status === 'ACTIVE').length" class="list-group list-group-flush">
          <li
            v-for="item in libraryItems.filter((x) => x.status === 'ACTIVE')"
            :key="item.id"
            class="list-group-item d-flex flex-wrap justify-content-between gap-2"
          >
            <div>
              <strong>{{ item.document_title }}</strong>
              <span class="small text-muted ms-2">{{ item.chunks_count }} chunks</span>
              <div class="small text-muted">
                {{ roleLabel(item.document_meta?.conversation_role) }}
                · {{ intentLabel(item.document_meta?.pedagogical_intent) }}
              </div>
            </div>
            <button type="button" class="btn btn-sm btn-outline-warning" @click="deactivateLink(item.id)">Retirer</button>
          </li>
        </ul>
        <p v-else class="text-muted small p-3 mb-0">Aucune liaison active pour ce groupe.</p>
      </div>
    </template>
    <p v-else class="text-muted">Sélectionnez un groupe pour gérer sa bibliothèque.</p>
  </div>
</template>
