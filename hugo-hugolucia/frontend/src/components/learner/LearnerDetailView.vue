<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../api/client'
import ReferentialExplorerModal from '../referential/ReferentialExplorerModal.vue'
import {
  extractNumberedQuestions,
  resolveAssistantContent,
} from '../../utils/assistantVariants'

const props = defineProps({ groupId: { type: String, default: '' } })
const route = useRoute()
const groupId = computed(() => props.groupId || route.params.groupId || '')
const activeTab = ref('chat')
const sessions = ref([])
/** Filtre liste sessions (onglet Chat) — plage sur la date de création (YYYY-MM-DD) */
const sessionDateFrom = ref('')
const sessionDateTo = ref('')
const sessionSearchQuery = ref('')
const sessionFavoritesOnly = ref(false)
let sessionSearchDebounce = null
const traces = ref([])
const evidence = ref([])
const groups = ref([])
const loading = ref({
  sessions: false,
  traces: false,
  evidence: false,
  groups: false,
  generate: false,
  tutorPrompts: false,
  starterPrompts: false,
  groupLibrary: false,
})
const groupLibraryItems = ref([])
const groupLibraryError = ref('')
const docModalOpen = ref(false)
const docModalTitle = ref('')
const docModalText = ref('')
const docModalLoading = ref(false)
const selectedSession = ref(null)
const messages = ref([])
const messageContent = ref('')
const structuredAnswers = ref({})
const sendingMessage = ref(false)
const shareFlags = ref({ share_summary: false, share_evidence: false, share_verbatim: false })
const uploadFile = ref(null)
const uploadSessionId = ref('')
const uploadTraceId = ref('')
const uploadEvidenceLoading = ref(false)
const evidencePreviewOpen = ref(false)
const evidencePreviewUrl = ref('')
const evidencePreviewTitle = ref('')
const tutorPrompts = ref([])
const selectedTutorPromptId = ref('')
const messagesContainer = ref(null)
const starterPrompts = ref([])
const starterError = ref('')
const manualPhaseOverride = ref('')
const phaseSaving = ref(false)
const phaseError = ref('')
const classifierRuntimeSaving = ref(false)
const classifierRuntimeError = ref('')
const classifierRuntimeSource = ref({})
const classifierRuntimeEffective = ref({})
const sessionClassifierEnabled = ref(null)
const sessionClassifierMaxTokens = ref('')
const sessionClassifierMinConfidence = ref('')
const sessionClassifierMaxInputChars = ref('')
const sessionP0ClassifierEnabled = ref(null)
const sessionP0ClassifierMaxTokens = ref('')
const sessionP0ClassifierMinConfidence = ref('')
const sessionP0ClassifierMaxInputChars = ref('')
const tuningModalOpen = ref(false)
const classifierPresets = ref({
  safe: {
    phase_classifier_enabled: true,
    phase_classifier_min_confidence: 0.75,
    phase_classifier_max_tokens: 24,
    phase_classifier_max_input_chars: 500,
  },
  balanced: {
    phase_classifier_enabled: true,
    phase_classifier_min_confidence: 0.6,
    phase_classifier_max_tokens: 48,
    phase_classifier_max_input_chars: 700,
  },
  aggressive: {
    phase_classifier_enabled: true,
    phase_classifier_min_confidence: 0.45,
    phase_classifier_max_tokens: 64,
    phase_classifier_max_input_chars: 900,
  },
})
const p0ClassifierPresets = ref({
  safe: {
    p0_classifier_enabled: true,
    p0_classifier_min_confidence: 0.75,
    p0_classifier_max_tokens: 120,
    p0_classifier_max_input_chars: 700,
  },
  balanced: {
    p0_classifier_enabled: true,
    p0_classifier_min_confidence: 0.6,
    p0_classifier_max_tokens: 180,
    p0_classifier_max_input_chars: 900,
  },
  aggressive: {
    p0_classifier_enabled: true,
    p0_classifier_min_confidence: 0.45,
    p0_classifier_max_tokens: 240,
    p0_classifier_max_input_chars: 1200,
  },
})
const payloadModalOpen = ref(false)
const payloadModalTitle = ref('')
const payloadModalData = ref({})
const payloadModalRaw = ref('{}')
const tutorSnapshotShowTemplates = ref(false)
const p0ModalOpen = ref(false)
const p0ModalTurnState = ref({})
const p0ModalDecision = ref({})
const p0ModalClassifier = ref({})
const p0ModalContext = ref('')

const groupReferentialConfig = ref(null)
const loadingReferentialConfig = ref(false)
const referentialExplorerOpen = ref(false)
const referentialExplorerId = ref('')
const referentialExplorerName = ref('')

const hasGroupReferential = computed(() => Boolean(groupReferentialConfig.value?.referential?.id))

async function loadReferentialConfig() {
  const gid = String(groupId.value || '').trim()
  if (!gid) {
    groupReferentialConfig.value = null
    return
  }
  loadingReferentialConfig.value = true
  try {
    const { data } = await api.get(`/groups/${gid}/referential-config/`)
    groupReferentialConfig.value = data && data.referential ? data : null
  } catch {
    groupReferentialConfig.value = null
  } finally {
    loadingReferentialConfig.value = false
  }
}

function openReferentialExplorer() {
  const r = groupReferentialConfig.value?.referential
  if (!r?.id) return
  referentialExplorerId.value = r.id
  referentialExplorerName.value = r.name || ''
  referentialExplorerOpen.value = true
}

/**
 * Fallback si `turn_state.p0` est absent : liste étendue alignée sur les champs scalaires du TurnState.
 * Si `p0` est présent (8 clés, voir backend P0_CORE_FIELDS), le tableau affiche ce sous-objet.
 */
const P0_CORE_KEYS = [
  'episode_clarity',
  'has_concrete_actions',
  'problem_salience',
  'reflection_phase',
  'reflective_depth',
  'self_efficacy_signal',
  'affect_valence',
  'cognitive_load',
  'interaction_risk',
  'epistemic_balance',
  'zpd_estimate',
  'session_phase',
  'session_maturity',
  'evidence_strength',
  'intervention_necessity',
  'contradiction_status',
]
const P0_CORE_LABELS = {
  episode_clarity: 'Clarté de l’épisode',
  has_concrete_actions: 'Actions concrètes décrites',
  problem_salience: 'Saillance du problème',
  reflection_phase: 'Phase de réflexion',
  reflective_depth: 'Profondeur réflexive',
  self_efficacy_signal: 'Auto-efficacité',
  affect_valence: 'Valence affective',
  cognitive_load: 'Charge cognitive',
  interaction_risk: 'Risque interactionnel',
  epistemic_balance: 'Équilibre épistémique',
  zpd_estimate: 'Estimation ZPD',
  session_phase: 'Phase de session (état)',
  session_maturity: 'Maturité de session',
  evidence_strength: 'Force des preuves',
  intervention_necessity: 'Nécessité d’intervention',
  contradiction_status: 'Contradiction',
}
/** Couverture du fil & signaux explicites (affichés en premier sous-section dédiée). */
const THREAD_REGULATION_KEYS = [
  'covered_points',
  'remaining_open_points',
  'learner_help_request',
  'closure_signal',
  'repetition_signal',
  'loop_risk',
  'assistant_meta_leak_risk',
]

const HYBRID_LABELS = {
  concept_clarity: 'Clarté conceptuelle',
  available_material: 'Matériel disponible',
  conversation_goal: 'Objectif conversationnel',
  current_phase: 'Phase courante',
  emotional_state: 'État émotionnel',
  action_feasibility: 'Faisabilité de l’action',
  autonomy_level: 'Niveau d’autonomie',
  recent_progress: 'Progression récente',
  need_recap: 'Besoin de récap',
  need_encouragement: 'Besoin d’encouragement',
  need_reframing: 'Besoin de recadrage',
  can_close_for_now: 'Clôture possible',
  covered_points: 'Points couverts (fil)',
  remaining_open_points: 'Points ouverts restants',
  learner_help_request: 'Demande d’aide (signal)',
  closure_signal: 'Signal de clôture',
  repetition_signal: 'Signal de répétition',
  loop_risk: 'Risque de boucle',
  assistant_meta_leak_risk: 'Risque de fuite méta (assistant)',
  last_tutorial_move: 'Dernier geste tutoriel',
  consecutive_clarify_turns: 'Tours de clarification consécutifs',
  sticky_has_concrete_actions: 'Actions concrètes (sticky)',
  tech_representation_level: 'Niveau de représentation technique',
  technical_criterion_focus: 'Focus critère technique',
  safety_or_quality_risk_level: 'Risque sécurité / qualité',
}
const DECISION_LABELS = {
  primary_intent: 'Intention principale',
  pedagogical_move: 'Geste pédagogique',
  number_of_questions: 'Nombre de questions',
  question_style: 'Style de question',
  should_explain_briefly: 'Micro-explication',
  should_recap: 'Récap',
  should_encourage: 'Encouragement',
  should_reframe: 'Recadrage',
  should_close: 'Clôture',
  response_constraints: 'Contraintes de réponse',
  reason_codes: 'Codes de raison',
  metadata: 'Métadonnées',
}

const phaseOptions = [
  { value: 'opening', label: 'opening' },
  { value: 'exploration', label: 'exploration' },
  { value: 'conceptualization', label: 'conceptualization' },
  { value: 'closure', label: 'closure' },
]

function resolveMessageContent(message) {
  return resolveAssistantContent(message)
}

const numberedQuestions = computed(() => {
  const lastAssistant = [...messages.value].reverse().find((m) => m.role === 'ASSISTANT')
  const resolvedContent = resolveMessageContent(lastAssistant)
  return extractNumberedQuestions(resolvedContent)
})

const canSendMessage = computed(() => {
  if (sendingMessage.value || !selectedSession.value) return false
  if (messageContent.value.trim()) return true
  return numberedQuestions.value.some((q) => String(structuredAnswers.value[q.index] || '').trim())
})
const evidenceBySessionId = computed(() => {
  const map = {}
  for (const item of evidence.value || []) {
    const sessionId = String(item?.session || '').trim()
    if (!sessionId) continue
    map[sessionId] = map[sessionId] || []
    map[sessionId].push(item)
  }
  return map
})
const evidenceByTraceId = computed(() => {
  const map = {}
  for (const item of evidence.value || []) {
    const traceId = String(item?.trace || '').trim()
    if (!traceId) continue
    map[traceId] = map[traceId] || []
    map[traceId].push(item)
  }
  return map
})
const evidenceListModalOpen = ref(false)
const evidenceListModalTitle = ref('')
const evidenceListItems = ref([])

async function loadSessions() {
  loading.value.sessions = true
  try {
    const params = {}
    const df = String(sessionDateFrom.value || '').trim()
    const dt = String(sessionDateTo.value || '').trim()
    if (df) params.created_after = df
    if (dt) params.created_before = dt
    const q = String(sessionSearchQuery.value || '').trim()
    if (q) params.q = q
    if (sessionFavoritesOnly.value) params.favorites_only = '1'
    const { data } = await api.get('/hugo/sessions/', { params })
    const allSessions = Array.isArray(data) ? data : (data.results || [])
    const currentGroupId = String(groupId.value || '').trim()
    sessions.value = currentGroupId
      ? allSessions.filter((s) => String(s.group || '').trim() === currentGroupId)
      : allSessions
  } finally {
    loading.value.sessions = false
  }
}

async function toggleSessionFavorite(session, evt) {
  evt?.preventDefault?.()
  evt?.stopPropagation?.()
  if (!session?.id) return
  const next = !session.is_favorite
  try {
    const { data } = await api.patch(`/hugo/sessions/${session.id}/`, { is_favorite: next })
    const patch = data && typeof data === 'object' ? data : {}
    sessions.value = sessions.value.map((s) => (s.id === session.id ? { ...s, ...patch } : s))
    if (selectedSession.value?.id === session.id) {
      selectedSession.value = { ...selectedSession.value, ...patch }
    }
  } catch {
    /* ignore */
  }
}
async function loadTraces() {
  loading.value.traces = true
  try {
    const { data } = await api.get('/learners/traces/')
    traces.value = Array.isArray(data) ? data : (data.results || [])
  } finally {
    loading.value.traces = false
  }
}
async function loadEvidence() {
  loading.value.evidence = true
  try {
    const { data } = await api.get('/learners/evidence/')
    evidence.value = Array.isArray(data) ? data : (data.results || [])
  } finally {
    loading.value.evidence = false
  }
}
async function loadGroups() {
  loading.value.groups = true
  try {
    const { data } = await api.get('/groups/')
    groups.value = Array.isArray(data) ? data : (data.results || [])
  } finally {
    loading.value.groups = false
  }
}
async function loadTutorPrompts() {
  loading.value.tutorPrompts = true
  try {
    const { data } = await api.get('/hugo/tutor-prompts/')
    tutorPrompts.value = Array.isArray(data) ? data : (data.results || [])
    if (!selectedTutorPromptId.value) {
      const defaultPrompt = tutorPrompts.value.find((p) => p?.is_default)
      if (defaultPrompt?.id) {
        selectedTutorPromptId.value = defaultPrompt.id
      }
    }
  } catch {
    tutorPrompts.value = []
  } finally {
    loading.value.tutorPrompts = false
  }
}

async function loadStarterPrompts() {
  loading.value.starterPrompts = true
  starterError.value = ''
  try {
    const { data } = await api.get('/hugo/starter-prompts/')
    starterPrompts.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    starterPrompts.value = []
    starterError.value = e.response?.data?.detail || 'Erreur lors du chargement des suggestions.'
  } finally {
    loading.value.starterPrompts = false
  }
}
async function loadMessages(session) {
  selectedSession.value = session
  manualPhaseOverride.value = session.manual_phase_override || ''
  sessionClassifierEnabled.value = session.phase_classifier_enabled ?? null
  sessionClassifierMaxTokens.value = session.phase_classifier_max_tokens ?? ''
  sessionClassifierMinConfidence.value = session.phase_classifier_min_confidence ?? ''
  sessionClassifierMaxInputChars.value = session.phase_classifier_max_input_chars ?? ''
  sessionP0ClassifierEnabled.value = session.p0_classifier_enabled ?? null
  sessionP0ClassifierMaxTokens.value = session.p0_classifier_max_tokens ?? ''
  sessionP0ClassifierMinConfidence.value = session.p0_classifier_min_confidence ?? ''
  sessionP0ClassifierMaxInputChars.value = session.p0_classifier_max_input_chars ?? ''
  classifierRuntimeSource.value = {}
  classifierRuntimeEffective.value = {}
  phaseError.value = ''
  classifierRuntimeError.value = ''
  shareFlags.value = {
    share_summary: session.share_summary,
    share_evidence: session.share_evidence,
    share_verbatim: session.share_verbatim,
  }
  try {
    const { data } = await api.get(`/hugo/sessions/${session.id}/messages/`)
    messages.value = data.messages || []
    const firstLearnerMessage = (messages.value || []).find((m) => m.role === 'LEARNER')?.content || ''
    if (firstLearnerMessage && !selectedSession.value.first_learner_message) {
      selectedSession.value = { ...selectedSession.value, first_learner_message: firstLearnerMessage }
      sessions.value = sessions.value.map((s) =>
        s.id === selectedSession.value.id ? { ...s, first_learner_message: firstLearnerMessage } : s,
      )
    }
  } catch {
    messages.value = []
  }
}
function closeSession() {
  selectedSession.value = null
  messages.value = []
  tuningModalOpen.value = false
  payloadModalOpen.value = false
}
function openTuningModal() {
  if (!selectedSession.value) return
  tuningModalOpen.value = true
}
function closeTuningModal() {
  tuningModalOpen.value = false
}
async function createSession() {
  const gid = groupId.value || (groups.value[0]?.id)
  if (!gid) return
  try {
    const payload = { group: gid }
    if (selectedTutorPromptId.value) payload.tutor_prompt_id = selectedTutorPromptId.value
    const { data } = await api.post('/hugo/sessions/', payload)
    await loadSessions()
    selectedSession.value = data
    shareFlags.value = { share_summary: false, share_evidence: false, share_verbatim: false }
    messages.value = []
  } catch (e) {
    console.error(e)
  }
}
async function sendMessage() {
  if (!selectedSession.value || sendingMessage.value) return
  const indexedLines = numberedQuestions.value
    .map((q) => {
      const answer = String(structuredAnswers.value[q.index] || '').trim()
      return answer ? `${q.index}: ${answer}` : ''
    })
    .filter(Boolean)
  const freeText = messageContent.value.trim()
  const payloadContent = [indexedLines.join('\n'), freeText].filter(Boolean).join('\n\n').trim()
  if (!payloadContent) return
  sendingMessage.value = true
  try {
    const { data } = await api.post(`/hugo/sessions/${selectedSession.value.id}/messages/`, { content: payloadContent })
    if (!selectedSession.value.first_learner_message) {
      const firstLearnerMessage = payloadContent.split('\n')[0].trim()
      selectedSession.value = { ...selectedSession.value, first_learner_message: firstLearnerMessage }
      sessions.value = sessions.value.map((s) =>
        s.id === selectedSession.value.id ? { ...s, first_learner_message: firstLearnerMessage } : s,
      )
    }
    syncSessionPhase(selectedSession.value.id, data || {})
    classifierRuntimeSource.value = data?.phase_runtime_config_source || {}
    classifierRuntimeEffective.value = data?.phase_runtime_config || {}
    await loadMessages(selectedSession.value)
    messageContent.value = ''
    structuredAnswers.value = {}
  } finally {
    sendingMessage.value = false
  }
}

function syncSessionPhase(sessionId, payload) {
  sessions.value = sessions.value.map((s) => {
    if (s.id !== sessionId) return s
    return {
      ...s,
      current_phase: payload.current_phase ?? s.current_phase,
      manual_phase_override: payload.manual_phase_override ?? null,
      phase_classifier_enabled: payload.phase_classifier_enabled ?? s.phase_classifier_enabled,
      phase_classifier_max_tokens: payload.phase_classifier_max_tokens ?? s.phase_classifier_max_tokens,
      phase_classifier_min_confidence: payload.phase_classifier_min_confidence ?? s.phase_classifier_min_confidence,
      phase_classifier_max_input_chars: payload.phase_classifier_max_input_chars ?? s.phase_classifier_max_input_chars,
      p0_classifier_enabled: payload.p0_classifier_enabled ?? s.p0_classifier_enabled,
      p0_classifier_max_tokens: payload.p0_classifier_max_tokens ?? s.p0_classifier_max_tokens,
      p0_classifier_min_confidence: payload.p0_classifier_min_confidence ?? s.p0_classifier_min_confidence,
      p0_classifier_max_input_chars: payload.p0_classifier_max_input_chars ?? s.p0_classifier_max_input_chars,
    }
  })
  if (selectedSession.value?.id === sessionId) {
    selectedSession.value = {
      ...selectedSession.value,
      current_phase: payload.current_phase ?? selectedSession.value.current_phase,
      manual_phase_override: payload.manual_phase_override ?? null,
      phase_classifier_enabled: payload.phase_classifier_enabled ?? selectedSession.value.phase_classifier_enabled,
      phase_classifier_max_tokens: payload.phase_classifier_max_tokens ?? selectedSession.value.phase_classifier_max_tokens,
      phase_classifier_min_confidence: payload.phase_classifier_min_confidence ?? selectedSession.value.phase_classifier_min_confidence,
      phase_classifier_max_input_chars: payload.phase_classifier_max_input_chars ?? selectedSession.value.phase_classifier_max_input_chars,
      p0_classifier_enabled: payload.p0_classifier_enabled ?? selectedSession.value.p0_classifier_enabled,
      p0_classifier_max_tokens: payload.p0_classifier_max_tokens ?? selectedSession.value.p0_classifier_max_tokens,
      p0_classifier_min_confidence: payload.p0_classifier_min_confidence ?? selectedSession.value.p0_classifier_min_confidence,
      p0_classifier_max_input_chars: payload.p0_classifier_max_input_chars ?? selectedSession.value.p0_classifier_max_input_chars,
    }
    manualPhaseOverride.value = selectedSession.value.manual_phase_override || ''
  }
}

async function saveManualPhaseOverride() {
  if (!selectedSession.value || phaseSaving.value) return
  phaseSaving.value = true
  phaseError.value = ''
  try {
    const payload = { manual_phase_override: manualPhaseOverride.value || null }
    const { data } = await api.patch(`/hugo/sessions/${selectedSession.value.id}/phase/`, payload)
    syncSessionPhase(selectedSession.value.id, data || {})
  } catch (e) {
    phaseError.value = e.response?.data?.detail || "Impossible d'enregistrer le forçage de phase."
  } finally {
    phaseSaving.value = false
  }
}

function numberOrNull(value) {
  if (value === '' || value === null || value === undefined) return null
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

function applySessionClassifierPreset(name) {
  const preset = classifierPresets.value[name]
  if (!preset) return
  sessionClassifierEnabled.value = preset.phase_classifier_enabled
  sessionClassifierMaxTokens.value = preset.phase_classifier_max_tokens
  sessionClassifierMinConfidence.value = preset.phase_classifier_min_confidence
  sessionClassifierMaxInputChars.value = preset.phase_classifier_max_input_chars
}

function applySessionP0ClassifierPreset(name) {
  const preset = p0ClassifierPresets.value[name]
  if (!preset) return
  sessionP0ClassifierEnabled.value = preset.p0_classifier_enabled
  sessionP0ClassifierMaxTokens.value = preset.p0_classifier_max_tokens
  sessionP0ClassifierMinConfidence.value = preset.p0_classifier_min_confidence
  sessionP0ClassifierMaxInputChars.value = preset.p0_classifier_max_input_chars
}

async function saveSessionClassifierConfig() {
  if (!selectedSession.value || classifierRuntimeSaving.value) return
  classifierRuntimeSaving.value = true
  classifierRuntimeError.value = ''
  const payload = {
    phase_classifier_enabled: sessionClassifierEnabled.value,
    phase_classifier_max_tokens: numberOrNull(sessionClassifierMaxTokens.value),
    phase_classifier_min_confidence: numberOrNull(sessionClassifierMinConfidence.value),
    phase_classifier_max_input_chars: numberOrNull(sessionClassifierMaxInputChars.value),
    p0_classifier_enabled: sessionP0ClassifierEnabled.value,
    p0_classifier_max_tokens: numberOrNull(sessionP0ClassifierMaxTokens.value),
    p0_classifier_min_confidence: numberOrNull(sessionP0ClassifierMinConfidence.value),
    p0_classifier_max_input_chars: numberOrNull(sessionP0ClassifierMaxInputChars.value),
  }
  try {
    const { data } = await api.patch(`/hugo/sessions/${selectedSession.value.id}/classifier-config/`, payload)
    syncSessionPhase(selectedSession.value.id, data || {})
    if (data?.presets_reference) classifierPresets.value = data.presets_reference
    if (data?.p0_presets_reference) p0ClassifierPresets.value = data.p0_presets_reference
    sessionClassifierEnabled.value = data?.phase_classifier_enabled ?? null
    sessionClassifierMaxTokens.value = data?.phase_classifier_max_tokens ?? ''
    sessionClassifierMinConfidence.value = data?.phase_classifier_min_confidence ?? ''
    sessionClassifierMaxInputChars.value = data?.phase_classifier_max_input_chars ?? ''
    sessionP0ClassifierEnabled.value = data?.p0_classifier_enabled ?? null
    sessionP0ClassifierMaxTokens.value = data?.p0_classifier_max_tokens ?? ''
    sessionP0ClassifierMinConfidence.value = data?.p0_classifier_min_confidence ?? ''
    sessionP0ClassifierMaxInputChars.value = data?.p0_classifier_max_input_chars ?? ''
  } catch (e) {
    classifierRuntimeError.value = e.response?.data?.detail || 'Impossible de sauvegarder la calibration session.'
  } finally {
    classifierRuntimeSaving.value = false
  }
}

function applyStarterPrompt(starter) {
  if (!selectedSession.value || !starter?.question) return
  const now = new Date().toISOString()
  messages.value.push({
    id: `local-${Date.now()}`,
    role: 'ASSISTANT',
    content: starter.question,
    assistant_display_variants: {
      short: starter.question,
      long: starter.question,
      default_variant: 'short',
      available_variants: ['short'],
    },
    created_at: now,
  })
}
async function generateTrace() {
  if (!selectedSession.value || loading.value.generate) return
  loading.value.generate = true
  try {
    await api.post(`/hugo/sessions/${selectedSession.value.id}/generate-trace/`)
    await loadTraces()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value.generate = false
  }
}
async function updateShare() {
  if (!selectedSession.value) return
  try {
    const { data } = await api.post(`/hugo/sessions/${selectedSession.value.id}/share/`, shareFlags.value)
    shareFlags.value = { ...data }
    selectedSession.value = { ...selectedSession.value, ...data }
  } catch (e) {
    console.error(e)
  }
}
async function uploadEvidence() {
  const el = uploadFile.value
  const file = el?.files?.[0]
  const sessionId = uploadSessionId.value || selectedSession.value?.id
  const traceId = uploadTraceId.value
  if (!file || (!sessionId && !traceId)) return
  uploadEvidenceLoading.value = true
  try {
    const form = new FormData()
    form.append('file', file)
    if (sessionId) form.append('session_id', sessionId)
    if (traceId) form.append('trace_id', traceId)
    await api.post('/evidence/', form, { headers: { 'Content-Type': 'multipart/form-data' } })
    if (el) el.value = ''
    await loadEvidence()
  } catch (e) {
    console.error(e)
  } finally {
    uploadEvidenceLoading.value = false
  }
}
function formatDate(s) {
  if (!s) return ''
  try {
    const d = new Date(s)
    return d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
  } catch {
    return s
  }
}
function shortId(value) {
  return String(value || '').slice(0, 8)
}
function evidenceSessionLabel(session) {
  const preview = sessionPreview(session)
  return `${formatDate(session.created_at)} — ${preview}`
}
function evidenceTraceLabel(trace) {
  const status = trace.validated_at ? 'validée' : 'non validée'
  return `${formatDate(trace.created_at)} — ${status} (${shortId(trace.id)})`
}
function evidenceUrl(evidenceItem) {
  return String(evidenceItem?.file_url || evidenceItem?.file_path || '').trim()
}
function isImageEvidence(evidenceItem) {
  const path = evidenceUrl(evidenceItem).toLowerCase()
  return ['.jpg', '.jpeg', '.png', '.gif', '.webp'].some((ext) => path.endsWith(ext))
}
function openEvidencePreview(evidenceItem) {
  if (!isImageEvidence(evidenceItem)) return
  evidencePreviewUrl.value = import.meta.env.VITE_API_URL + evidenceUrl(evidenceItem)
  evidencePreviewTitle.value = `Preuve du ${formatDate(evidenceItem.created_at)}`
  evidencePreviewOpen.value = true
}
function closeEvidencePreview() {
  evidencePreviewOpen.value = false
  evidencePreviewUrl.value = ''
  evidencePreviewTitle.value = ''
}
function evidenceCountForSession(sessionId) {
  const key = String(sessionId || '').trim()
  return (evidenceBySessionId.value[key] || []).length
}
function evidenceCountForTrace(traceId) {
  const key = String(traceId || '').trim()
  return (evidenceByTraceId.value[key] || []).length
}
function evidenceItemsForSession(sessionId) {
  const key = String(sessionId || '').trim()
  return evidenceBySessionId.value[key] || []
}
function openEvidenceListModalForSession(session) {
  const items = evidenceItemsForSession(session?.id)
  evidenceListItems.value = items
  evidenceListModalTitle.value = `Preuves associées à la session (${items.length})`
  evidenceListModalOpen.value = true
}
function openEvidenceListModalForTrace(trace) {
  const key = String(trace?.id || '').trim()
  const items = evidenceByTraceId.value[key] || []
  evidenceListItems.value = items
  evidenceListModalTitle.value = `Preuves associées à la trace (${items.length})`
  evidenceListModalOpen.value = true
}
function closeEvidenceListModal() {
  evidenceListModalOpen.value = false
  evidenceListModalTitle.value = ''
  evidenceListItems.value = []
}
function canShowPayloadDetails(message) {
  if (!message) return false
  const requestPayload = message.llm_request_payload
  const responsePayload = message.llm_response_payload
  return (requestPayload && Object.keys(requestPayload).length > 0)
    || (responsePayload && Object.keys(responsePayload).length > 0)
}
function payloadPreview(text, maxLen = 300) {
  const raw = String(text || '').trim()
  if (!raw) return ''
  return raw.length > maxLen ? `${raw.slice(0, maxLen).trim()}...` : raw
}
function payloadKeyValueRows(payload) {
  const rows = [
    ['Provider', payload.provider],
    ['Modèle', payload.model_used],
    ['Max tokens', payload.max_tokens],
    ['Phase session', payload.session_phase],
    ['Phase suivante', payload.next_session_phase],
    ['Forçage manuel phase', payload.manual_phase_override],
    ['Mode output résolu', payload.resolved_output_mode],
    ['Prompt résolu (id)', payload.resolved_tutor_prompt_id],
    ['Alignement appliqué', payload.indexed_alignment_applied],
    ['Paires alignées', payload.aligned_pairs_count],
    ['Source décision phase', payload.phase_decision_source],
    ['Raison décision phase', payload.phase_decision_reason],
    ['Confiance décision phase', payload.phase_decision_confidence],
    ['Raison fallback phase', payload.phase_decision_fallback_reason],
    ['Provider classifier', payload.phase_classifier_provider],
    ['Modèle classifier', payload.phase_classifier_model],
  ]
  return rows.filter(([, value]) => value !== undefined && value !== null && value !== '')
}
function responseKeyValueRows(payload) {
  const usage = payload?.raw_response?.usage || {}
  const rows = [
    ['Provider', payload.provider],
    ['Modèle', payload.model_used],
    ['Response ID', payload?.raw_response?.id],
    ['Object', payload?.raw_response?.object],
    ['Finish reason', payload?.raw_response?.choices?.[0]?.finish_reason],
    ['Prompt tokens', usage.prompt_tokens],
    ['Completion tokens', usage.completion_tokens],
    ['Total tokens', usage.total_tokens],
  ]
  return rows.filter(([, value]) => value !== undefined && value !== null && value !== '')
}

function p0ClassifierKeyValueRows(classifier) {
  const payload = classifier || {}
  const raw = payload.classifier_reply_text
  const rawPreview =
    raw != null && String(raw).trim()
      ? String(raw).length > 600
        ? `${String(raw).slice(0, 600)}…`
        : String(raw)
      : ''
  const rows = [
    ['Source', payload.source],
    ['Confiance', payload.confidence],
    ['Raison fallback', payload.fallback_reason],
    ['Réponse brute (extrait)', rawPreview],
    ['Provider P0', payload.classifier_provider],
    ['Modèle P0', payload.classifier_model],
  ]
  return rows.filter(([, value]) => value !== undefined && value !== null && value !== '')
}

function hasObjectEntries(value) {
  return !!(value && typeof value === 'object' && Object.keys(value).length)
}
function openPayloadModal(message) {
  if (!canShowPayloadDetails(message)) return
  tutorSnapshotShowTemplates.value = false
  if (message.role === 'LEARNER') {
    payloadModalTitle.value = 'Détail LLM request payload (learner)'
    payloadModalData.value = message.llm_request_payload || {}
    payloadModalRaw.value = JSON.stringify(message.llm_request_payload || {}, null, 2)
  } else {
    payloadModalTitle.value = 'Détail LLM response payload (assistant)'
    payloadModalData.value = message.llm_response_payload || {}
    payloadModalRaw.value = JSON.stringify(message.llm_response_payload || {}, null, 2)
  }
  payloadModalOpen.value = true
}
function closePayloadModal() {
  payloadModalOpen.value = false
  payloadModalData.value = {}
  payloadModalRaw.value = '{}'
  tutorSnapshotShowTemplates.value = false
}

async function copyTutorPromptSnapshotJson() {
  const snap = payloadModalData.value?.tutor_prompt_snapshot
  if (!snap || typeof snap !== 'object') return
  const text = JSON.stringify(snap, null, 2)
  try {
    await navigator.clipboard.writeText(text)
  } catch {
    /* ignore */
  }
}

function resolveLlmRequestPayloadForMessage(message) {
  if (!message) return null
  if (message.role === 'LEARNER') {
    const p = message.llm_request_payload
    return p && Object.keys(p).length ? p : null
  }
  const idx = messages.value.findIndex((x) => x.id === message.id)
  if (idx <= 0) return null
  for (let i = idx - 1; i >= 0; i -= 1) {
    const m = messages.value[i]
    if (m.role === 'LEARNER' && m.llm_request_payload && Object.keys(m.llm_request_payload).length) {
      return m.llm_request_payload
    }
  }
  return null
}

function canShowP0Modal(message) {
  const req = resolveLlmRequestPayloadForMessage(message)
  const ts = req?.turn_state
  return !!(ts && typeof ts === 'object' && Object.keys(ts).length)
}

function formatP0Value(value) {
  if (typeof value === 'boolean') return value ? 'oui' : 'non'
  if (value === null || value === undefined) return '—'
  if (Array.isArray(value)) {
    if (!value.length) return '—'
    return value.map((x) => String(x)).join(', ')
  }
  return String(value)
}

/** Liste pour affichage `<ul>` ; chaînes vides filtrées. */
function formatP0ListItems(value) {
  if (!Array.isArray(value) || !value.length) return []
  return value.map((x) => String(x).trim()).filter(Boolean)
}

function p0NucleusEntries(turnState) {
  const ts = turnState || {}
  const nucleus = ts.p0 && typeof ts.p0 === 'object' ? ts.p0 : null
  const source = nucleus || {}
  const keys = Object.keys(source).length ? Object.keys(source) : P0_CORE_KEYS
  return keys.map((key) => ({
    key,
    label: P0_CORE_LABELS[key] || key,
    value: formatP0Value(source[key] ?? ts[key]),
  }))
}

function p0ThreadRegulationEntries(turnState) {
  const ts = turnState || {}
  const rows = []
  for (const key of THREAD_REGULATION_KEYS) {
    if (!(key in ts)) continue
    const raw = ts[key]
    rows.push({
      key,
      label: HYBRID_LABELS[key] || key,
      raw,
      isList: key === 'covered_points' || key === 'remaining_open_points',
      listItems: key === 'covered_points' || key === 'remaining_open_points' ? formatP0ListItems(raw) : [],
      value: formatP0Value(raw),
    })
  }
  return rows
}

function p0OtherHybridEntries(turnState) {
  const ts = turnState || {}
  const core = new Set(P0_CORE_KEYS)
  const thread = new Set(THREAD_REGULATION_KEYS)
  return Object.entries(ts).filter(
    ([k]) => k !== 'p0' && k !== 'debug_signals' && !core.has(k) && !thread.has(k),
  )
}

function p0DecisionConstraintBadges(decision) {
  const d = decision || {}
  const list = Array.isArray(d.response_constraints) ? d.response_constraints : []
  const badges = []
  const highlight = new Set([
    'respect_explicit_closure',
    'no_question_final',
    'acknowledge_repetition_briefly',
    'brief_help_first',
  ])
  for (const c of list) {
    const s = String(c || '').trim()
    if (!s) continue
    badges.push({
      label: s,
      emphasized: highlight.has(s),
    })
  }
  return badges
}

function numberOfQuestionsBadgeClass(n) {
  const v = Number(n)
  if (v === 0) return 'text-bg-warning'
  if (v === 1) return 'text-bg-primary'
  if (v === 2) return 'text-bg-info'
  return 'text-bg-secondary'
}

function pedagogicalMoveBadgeClass(move, decision) {
  const m = String(move || '').toLowerCase()
  const d = decision || {}
  if (m === 'assist') return 'text-bg-info'
  if (m === 'close' || d.should_close) return 'text-bg-success'
  if (m === 'repair' || m === 'pace') return 'text-bg-secondary'
  return 'text-bg-dark'
}

function buildP0ModalSummary(turnState, decision) {
  const ts = turnState || {}
  const d = decision || {}
  const chips = []
  const nq = d.number_of_questions
  if (nq !== undefined && nq !== null && nq !== '') {
    chips.push({
      kind: 'nq',
      label: `Q${nq}`,
      badgeClass: numberOfQuestionsBadgeClass(nq),
    })
  }
  if (d.pedagogical_move !== undefined && d.pedagogical_move !== null && d.pedagogical_move !== '') {
    chips.push({
      kind: 'move',
      label: String(d.pedagogical_move),
      badgeClass: pedagogicalMoveBadgeClass(d.pedagogical_move, d),
    })
  }
  if (d.primary_intent) {
    chips.push({
      kind: 'intent',
      label: String(d.primary_intent),
      badgeClass: 'text-bg-secondary',
    })
  }
  const help = String(ts.learner_help_request || 'none')
  if (help && help !== 'none') {
    chips.push({ kind: 'help', label: `aide: ${help}`, badgeClass: 'text-bg-info' })
  }
  const clo = String(ts.closure_signal || 'none')
  if (clo && clo !== 'none') {
    chips.push({ kind: 'closure', label: `clôture: ${clo}`, badgeClass: 'text-bg-success' })
  }
  const rep = String(ts.repetition_signal || 'none')
  if (rep && rep !== 'none') {
    chips.push({ kind: 'repetition', label: `répétition: ${rep}`, badgeClass: 'text-bg-warning' })
  }
  const cov = formatP0ListItems(ts.covered_points)
  const rem = formatP0ListItems(ts.remaining_open_points)
  chips.push({
    kind: 'coverage',
    label: `couvert ${cov.length} · reste ${rem.length}`,
    badgeClass: 'text-bg-light text-dark border',
  })
  const lr = String(ts.loop_risk || 'low')
  if (lr !== 'low') {
    chips.push({ kind: 'loop', label: `boucle: ${lr}`, badgeClass: 'text-bg-danger' })
  }
  const ml = String(ts.assistant_meta_leak_risk || 'low')
  if (ml !== 'low') {
    chips.push({ kind: 'meta', label: `méta: ${ml}`, badgeClass: 'text-bg-danger' })
  }
  return { chips }
}

function p0DecisionEntries(decision) {
  const d = decision || {}
  const rows = []
  const order = [
    'primary_intent',
    'pedagogical_move',
    'number_of_questions',
    'question_style',
    'should_explain_briefly',
    'should_recap',
    'should_encourage',
    'should_reframe',
    'should_close',
  ]
  for (const key of order) {
    if (d[key] === undefined) continue
    rows.push({
      key,
      label: DECISION_LABELS[key] || key,
      value: formatP0Value(d[key]),
      raw: d[key],
    })
  }
  if (Array.isArray(d.response_constraints) && d.response_constraints.length) {
    rows.push({
      key: 'response_constraints',
      label: DECISION_LABELS.response_constraints,
      value: d.response_constraints.join(', '),
    })
  }
  if (Array.isArray(d.reason_codes) && d.reason_codes.length) {
    rows.push({
      key: 'reason_codes',
      label: DECISION_LABELS.reason_codes,
      value: d.reason_codes.join(', '),
    })
  }
  if (d.metadata && typeof d.metadata === 'object' && Object.keys(d.metadata).length) {
    rows.push({
      key: 'metadata',
      label: DECISION_LABELS.metadata,
      value: JSON.stringify(d.metadata),
    })
  }
  return rows
}

function openP0Modal(message) {
  const req = resolveLlmRequestPayloadForMessage(message)
  if (!req?.turn_state) return
  p0ModalTurnState.value = req.turn_state
  p0ModalDecision.value = req.conversation_decision || {}
  p0ModalClassifier.value = req.p0_classifier || {}
  p0ModalContext.value =
    message.role === 'LEARNER'
      ? 'État calculé pour ce message apprenant (tour courant).'
      : 'État du tour associé à la réponse Hugo (même tour que le message apprenant précédent).'
  p0ModalOpen.value = true
}

function closeP0Modal() {
  p0ModalOpen.value = false
  p0ModalTurnState.value = {}
  p0ModalDecision.value = {}
  p0ModalClassifier.value = {}
  p0ModalContext.value = ''
}

const p0ModalSummaryComputed = computed(() =>
  buildP0ModalSummary(p0ModalTurnState.value, p0ModalDecision.value),
)

/** Badge timeline: source du classifieur P0 (même payload que la modale P0). */
const P0_REPLI_REASONS = new Set([
  'parse_invalide',
  'parse_invalide_reponse_probablement_tronquee',
  'payload_invalide',
  'confiance_trop_faible',
])

function p0ClassifierBadgeMeta(message) {
  const req = resolveLlmRequestPayloadForMessage(message)
  const pc = req?.p0_classifier
  if (!pc || typeof pc !== 'object') return null
  const src = String(pc.source || '')
  const fr = String(pc.fallback_reason || '').trim()
  const c = pc.confidence
  const titleBits = []
  if (fr) titleBits.push(`Raison : ${fr}`)
  if (c !== undefined && c !== null && c !== '') titleBits.push(`Confiance : ${c}`)

  if (src === 'llm_classifier') {
    titleBits.unshift('Variables P0 sémantiques : classifieur LLM')
    return {
      kind: 'llm',
      label: 'llm',
      title: titleBits.join(' · '),
      badgeClass: 'text-bg-success',
    }
  }
  if (fr === 'llm_indisponible') {
    titleBits.unshift('Erreur appel LLM (réseau, quota, config)')
    return {
      kind: 'llm_error',
      label: 'err',
      title: titleBits.join(' · '),
      badgeClass: 'text-bg-danger',
    }
  }
  if (fr === 'reponse_vide') {
    titleBits.unshift('Réponse modèle vide (tokens trop bas ou filtrage)')
    return {
      kind: 'empty',
      label: 'vide',
      title: titleBits.join(' · '),
      badgeClass: 'text-bg-warning',
    }
  }
  if (P0_REPLI_REASONS.has(fr)) {
    titleBits.unshift('Repli heuristique après classifieur')
    return {
      kind: 'fallback',
      label: 'repli',
      title: titleBits.join(' · '),
      badgeClass: 'text-bg-warning',
    }
  }
  titleBits.unshift('Heuristique seule (classifieur désactivé, entrée vide, ou pas d’appel LLM)')
  return {
    kind: 'heuristic',
    label: 'heur.',
    title: titleBits.join(' · '),
    badgeClass: 'text-bg-secondary',
  }
}

const p0ClassifierBadgesByMessageId = computed(() => {
  const out = {}
  for (const m of messages.value) {
    const meta = p0ClassifierBadgeMeta(m)
    if (meta) out[m.id] = meta
  }
  return out
})

/** Badges Réf. / Docs : ce qui était dans le prompt du tour (pas une preuve d’usage par le modèle). */
const promptSourcesBadgesByMessageId = computed(() => {
  const out = {}
  for (const m of messages.value) {
    if (m.role !== 'ASSISTANT') continue
    const req = resolveLlmRequestPayloadForMessage(m)
    const ps = req?.prompt_sources
    if (!ps) continue
    const ref = ps.referential?.included
    const docs = ps.rag?.used
    if (!ref && !docs) continue
    out[m.id] = { ref: !!ref, docs: !!docs }
  }
  return out
})

async function loadGroupLibrary() {
  const gid = String(groupId.value || '').trim()
  if (!gid) {
    groupLibraryItems.value = []
    return
  }
  loading.value.groupLibrary = true
  groupLibraryError.value = ''
  try {
    const { data } = await api.get(`/groups/${gid}/library/`)
    groupLibraryItems.value = Array.isArray(data?.items) ? data.items : []
  } catch (e) {
    groupLibraryError.value = e.response?.data?.detail || e.message || 'Erreur de chargement'
    groupLibraryItems.value = []
  } finally {
    loading.value.groupLibrary = false
  }
}

async function openDocumentModal(doc) {
  const gid = String(groupId.value || '').trim()
  const did = doc?.document_id
  if (!gid || !did) return
  docModalOpen.value = true
  docModalTitle.value = doc.document_title || 'Document'
  docModalText.value = ''
  docModalLoading.value = true
  try {
    const { data } = await api.get(`/groups/${gid}/library/documents/${did}/content/`)
    docModalTitle.value = data.title || docModalTitle.value
    docModalText.value = data.source_text || ''
  } catch (e) {
    docModalText.value = e.response?.data?.detail || e.message || 'Impossible de charger le document.'
  } finally {
    docModalLoading.value = false
  }
}

function closeDocumentModal() {
  docModalOpen.value = false
  docModalTitle.value = ''
  docModalText.value = ''
}

function sessionPreview(session) {
  const text = String(session?.first_learner_message || '').trim()
  if (text) return text
  return 'Aucun message apprenant'
}

onMounted(() => {
  loadSessions()
  loadEvidence()
  loadGroups()
  loadReferentialConfig()
  loadTutorPrompts()
  loadStarterPrompts()
})
watch(activeTab, (tab) => {
  if (tab === 'traces') loadTraces()
  if (tab === 'evidence') loadEvidence()
  if (tab === 'documents') loadGroupLibrary()
})
watch(
  groupId,
  () => {
    loadSessions()
    loadReferentialConfig()
    if (selectedSession.value && String(selectedSession.value.group || '') !== String(groupId.value || '')) {
      closeSession()
    }
  },
)

watch(sessionSearchQuery, () => {
  clearTimeout(sessionSearchDebounce)
  sessionSearchDebounce = setTimeout(() => loadSessions(), 400)
})

watch([sessionDateFrom, sessionDateTo, sessionFavoritesOnly], () => {
  loadSessions()
})

watch(
  messages,
  async () => {
    await nextTick()
    const el = messagesContainer.value
    if (el) {
      el.scrollTop = el.scrollHeight
    }
  },
  { deep: true },
)

watch(
  numberedQuestions,
  (items) => {
    const nextAnswers = {}
    for (const q of items) {
      nextAnswers[q.index] = structuredAnswers.value[q.index] || ''
    }
    structuredAnswers.value = nextAnswers
  },
  { immediate: true },
)
</script>

<template>
  <nav aria-label="breadcrumb">
    <ol class="breadcrumb">
      <li class="breadcrumb-item"><router-link to="/dashboard">Tableau de bord</router-link></li>
      <li v-if="groupId" class="breadcrumb-item"><router-link :to="{ name: 'Group', params: { groupId } }">Groupe</router-link></li>
      <li class="breadcrumb-item active" aria-current="page">Mon espace</li>
    </ol>
  </nav>
  <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-4">
    <h1 class="h4 mb-0">Mon espace apprenant</h1>
    <button
      type="button"
      class="btn btn-outline-primary btn-sm"
      :disabled="loadingReferentialConfig || !hasGroupReferential"
      :title="hasGroupReferential ? 'Blocs, compétences et critères' : 'Aucun référentiel associé à ce groupe'"
      @click="openReferentialExplorer"
    >
      <span
        v-if="loadingReferentialConfig"
        class="spinner-border spinner-border-sm me-1"
        role="status"
        aria-hidden="true"
      />
      <i v-else class="bi bi-diagram-3 me-1" />
      Référentiel
    </button>
  </div>

  <ul class="nav nav-tabs mb-3">
    <li class="nav-item"><a class="nav-link" :class="{ active: activeTab === 'chat' }" href="#" @click.prevent="activeTab = 'chat'">Chat Hugo</a></li>
    <li class="nav-item"><a class="nav-link" :class="{ active: activeTab === 'traces' }" href="#" @click.prevent="activeTab = 'traces'">Traces</a></li>
    <li class="nav-item"><a class="nav-link" :class="{ active: activeTab === 'evidence' }" href="#" @click.prevent="activeTab = 'evidence'">Preuves</a></li>
    <li class="nav-item"><a class="nav-link" :class="{ active: activeTab === 'documents' }" href="#" @click.prevent="activeTab = 'documents'">Documents</a></li>
  </ul>

  <div
    v-if="evidencePreviewOpen"
    class="modal fade show d-block"
    tabindex="-1"
    role="dialog"
    aria-modal="true"
  >
    <div class="modal-dialog modal-lg modal-dialog-centered" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ evidencePreviewTitle }}</h5>
          <button type="button" class="btn-close" aria-label="Close" @click="closeEvidencePreview" />
        </div>
        <div class="modal-body text-center">
          <img
            v-if="evidencePreviewUrl"
            :src="evidencePreviewUrl"
            alt="Aperçu de la preuve"
            class="img-fluid rounded"
            style="max-height: 70vh;"
          />
        </div>
        <div class="modal-footer">
          <a
            v-if="evidencePreviewUrl"
            :href="evidencePreviewUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="btn btn-sm btn-outline-primary"
          >
            Ouvrir dans un nouvel onglet
          </a>
          <button type="button" class="btn btn-sm btn-secondary" @click="closeEvidencePreview">Fermer</button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="evidencePreviewOpen" class="modal-backdrop fade show" @click="closeEvidencePreview"></div>

  <div
    v-if="evidenceListModalOpen"
    class="modal fade show d-block"
    tabindex="-1"
    role="dialog"
    aria-modal="true"
  >
    <div class="modal-dialog modal-lg modal-dialog-scrollable" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ evidenceListModalTitle }}</h5>
          <button type="button" class="btn-close" aria-label="Close" @click="closeEvidenceListModal" />
        </div>
        <div class="modal-body">
          <ul v-if="evidenceListItems.length" class="list-group list-group-flush">
            <li
              v-for="item in evidenceListItems"
              :key="item.id"
              class="list-group-item d-flex justify-content-between align-items-center px-0"
            >
              <div>
                <div class="small">{{ formatDate(item.created_at) }}</div>
                <code class="small">{{ item.file_path }}</code>
              </div>
              <button
                v-if="isImageEvidence(item)"
                type="button"
                class="btn btn-sm btn-outline-primary"
                @click="openEvidencePreview(item)"
              >
                Voir
              </button>
            </li>
          </ul>
          <p v-else class="text-muted small mb-0">Aucune preuve associée.</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-sm btn-secondary" @click="closeEvidenceListModal">Fermer</button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="evidenceListModalOpen" class="modal-backdrop fade show" @click="closeEvidenceListModal"></div>

  <!-- Chat -->
  <div v-show="activeTab === 'chat'" class="row">
    <div class="col-12 col-md-4">
      <div class="card">
        <div class="card-header">
          <div class="d-flex flex-column gap-2">
            <div class="d-flex justify-content-between align-items-center">
              <span>Sessions</span>
              <button
                type="button"
                class="btn btn-sm btn-primary"
                :disabled="loading.groups || loading.tutorPrompts"
                @click="createSession"
              >
                Nouvelle
              </button>
            </div>
            <div class="small">
              <label for="tutor-prompt" class="form-label mb-1">Prompt tuteur</label>
              <select
                id="tutor-prompt"
                v-model="selectedTutorPromptId"
                class="form-select form-select-sm"
                :disabled="loading.tutorPrompts"
              >
                <option value="">Par défaut</option>
                <option
                  v-for="p in tutorPrompts"
                  :key="p.id"
                  :value="p.id"
                >
                  {{ p.code }} — {{ p.name }}
                </option>
              </select>
            </div>
            <div class="small">
              <span class="form-label d-block mb-1">Période (date de création de la session)</span>
              <div class="row g-2">
                <div class="col-6">
                  <label for="session-date-from" class="visually-hidden">Du</label>
                  <input
                    id="session-date-from"
                    v-model="sessionDateFrom"
                    type="date"
                    class="form-control form-control-sm"
                    title="Date de début"
                  >
                </div>
                <div class="col-6">
                  <label for="session-date-to" class="visually-hidden">Au</label>
                  <input
                    id="session-date-to"
                    v-model="sessionDateTo"
                    type="date"
                    class="form-control form-control-sm"
                    title="Date de fin"
                  >
                </div>
              </div>
              <button
                v-if="sessionDateFrom || sessionDateTo"
                type="button"
                class="btn btn-link btn-sm px-0 py-0 mt-1"
                @click="sessionDateFrom = ''; sessionDateTo = ''"
              >
                Effacer les dates
              </button>
            </div>
            <div class="small">
              <label for="session-search" class="form-label mb-1">Recherche dans les messages</label>
              <input
                id="session-search"
                v-model="sessionSearchQuery"
                type="search"
                class="form-control form-control-sm"
                placeholder="Mot ou phrase…"
                autocomplete="off"
              >
            </div>
            <div class="form-check small mb-0">
              <input
                id="session-favorites-only"
                v-model="sessionFavoritesOnly"
                class="form-check-input"
                type="checkbox"
              >
              <label class="form-check-label" for="session-favorites-only">Favoris uniquement</label>
            </div>
          </div>
        </div>
        <div class="list-group list-group-flush">
          <template v-if="loading.sessions">
            <div class="list-group-item text-muted">Chargement…</div>
          </template>
          <a
            v-for="s in sessions"
            :key="s.id"
            href="#"
            class="list-group-item list-group-item-action d-flex align-items-start gap-2"
            :class="{ active: selectedSession?.id === s.id }"
            @click.prevent="loadMessages(s)"
          >
            <button
              type="button"
              class="btn btn-link p-0 mt-n1 flex-shrink-0"
              :class="s.is_favorite ? 'text-danger' : 'text-secondary'"
              :title="s.is_favorite ? 'Retirer des favoris' : 'Ajouter aux favoris'"
              :aria-pressed="s.is_favorite"
              aria-label="Favori"
              @click="toggleSessionFavorite(s, $event)"
            >
              <i v-if="s.is_favorite" class="bi bi-heart-fill" />
              <i v-else class="bi bi-heart" />
            </button>
            <div class="flex-grow-1 min-w-0">
              <small class="d-block">{{ formatDate(s.created_at) }}</small>
              <small class="d-block text-truncate-no">{{ sessionPreview(s) }}</small>
              <span class="badge bg-secondary ms-1">
                {{ s.current_phase || 'exploration' }}
              </span>
              <span class="badge bg-light text-dark border ms-1">
                Preuves {{ evidenceCountForSession(s.id) }}
              </span>
              <span v-if="s.share_summary || s.share_evidence || s.share_verbatim" class="badge bg-info ms-1">Partagé</span>
            </div>
          </a>
          <div v-if="!loading.sessions && !sessions.length" class="list-group-item text-muted">Aucune session. Créez-en une.</div>
        </div>
      </div>
    </div>
    <div class="col-12 col-md-8">
      <div v-if="!selectedSession" class="card">
        <div class="card-body text-center text-muted py-5">Sélectionnez une session ou créez-en une.</div>
      </div>
      <div v-else class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
          <span>
            Session {{ formatDate(selectedSession.created_at) }}
            <span class="small text-muted d-block">
              1er message apprenant : {{ sessionPreview(selectedSession) }}
            </span>
            <span v-if="selectedSession.tutor_prompt" class="small text-muted d-block">
              Prompt tuteur : {{ selectedSession.tutor_prompt.code }} — {{ selectedSession.tutor_prompt.name }}
            </span>
            <span class="small text-muted d-block">
              Phase courante : <strong>{{ selectedSession.current_phase || 'exploration' }}</strong>
            </span>
            <span v-if="selectedSession.manual_phase_override" class="small text-muted d-block">
              Forçage manuel : {{ selectedSession.manual_phase_override }}
            </span>
            <span class="small text-muted d-block">
              Runtime classifier source :
              <code>{{ classifierRuntimeSource.effective || 'settings' }}</code>
            </span>
          </span>
          <div class="d-flex gap-2">
            <button type="button" class="btn btn-sm btn-outline-primary" @click="openTuningModal">
              Tuning
            </button>
            <button
              type="button"
              class="btn btn-sm btn-outline-success"
              :disabled="loading.generate"
              @click="generateTrace"
            >
              {{ loading.generate ? 'Génération…' : 'Générer une trace AFEST' }}
            </button>
            <button type="button" class="btn btn-sm btn-outline-secondary" @click="closeSession">Fermer</button>
          </div>
        </div>
        <div class="card-body">
          <div
            v-if="tuningModalOpen"
            class="modal fade show d-block"
            tabindex="-1"
            role="dialog"
            aria-modal="true"
          >
            <div class="modal-dialog modal-lg modal-dialog-scrollable" role="document">
              <div class="modal-content">
                <div class="modal-header">
                  <h5 class="modal-title">Tuning session</h5>
                  <button type="button" class="btn-close" aria-label="Close" @click="closeTuningModal" />
                </div>
                <div class="modal-body">
                  <div class="border rounded p-2 mb-2">
                    <div class="row g-2 align-items-end">
                      <div class="col-12 col-md-7">
                        <label class="form-label small mb-1">Forçage manuel de phase (optionnel)</label>
                        <select
                          v-model="manualPhaseOverride"
                          class="form-select form-select-sm"
                          :disabled="sendingMessage || phaseSaving"
                        >
                          <option value="">Aucun (auto)</option>
                          <option
                            v-for="opt in phaseOptions"
                            :key="opt.value"
                            :value="opt.value"
                          >
                            {{ opt.label }}
                          </option>
                        </select>
                      </div>
                      <div class="col-12 col-md-5 d-grid">
                        <button
                          type="button"
                          class="btn btn-sm btn-outline-secondary"
                          :disabled="sendingMessage || phaseSaving || !selectedSession"
                          @click="saveManualPhaseOverride"
                        >
                          {{ phaseSaving ? 'Enregistrement…' : 'Appliquer le forçage' }}
                        </button>
                      </div>
                    </div>
                    <p v-if="phaseError" class="text-danger small mb-0 mt-2">
                      {{ phaseError }}
                    </p>
                  </div>
                  <div class="border rounded p-2 mb-2">
                    <p class="small fw-bold mb-2">Classifier runtime (override session, optionnel)</p>
                    <div class="d-flex gap-2 mb-2">
                      <button type="button" class="btn btn-sm btn-outline-secondary" @click="applySessionClassifierPreset('safe')">safe</button>
                      <button type="button" class="btn btn-sm btn-outline-secondary" @click="applySessionClassifierPreset('balanced')">balanced</button>
                      <button type="button" class="btn btn-sm btn-outline-secondary" @click="applySessionClassifierPreset('aggressive')">aggressive</button>
                    </div>
                    <div class="row g-2">
                      <div class="col-12 col-md-3">
                        <label class="form-label small mb-1">Enabled</label>
                        <select
                          v-model="sessionClassifierEnabled"
                          class="form-select form-select-sm"
                          :disabled="classifierRuntimeSaving || sendingMessage"
                        >
                          <option :value="null">Fallback groupe/settings</option>
                          <option :value="true">true</option>
                          <option :value="false">false</option>
                        </select>
                      </div>
                      <div class="col-12 col-md-3">
                        <label class="form-label small mb-1">Min confidence</label>
                        <input
                          v-model.number="sessionClassifierMinConfidence"
                          type="number"
                          min="0"
                          max="1"
                          step="0.01"
                          class="form-control form-control-sm"
                          placeholder="fallback"
                          :disabled="classifierRuntimeSaving || sendingMessage"
                        />
                      </div>
                      <div class="col-12 col-md-3">
                        <label class="form-label small mb-1">Max tokens</label>
                        <input
                          v-model.number="sessionClassifierMaxTokens"
                          type="number"
                          min="1"
                          step="1"
                          class="form-control form-control-sm"
                          placeholder="fallback"
                          :disabled="classifierRuntimeSaving || sendingMessage"
                        />
                      </div>
                      <div class="col-12 col-md-3">
                        <label class="form-label small mb-1">Max input chars</label>
                        <input
                          v-model.number="sessionClassifierMaxInputChars"
                          type="number"
                          min="1"
                          step="1"
                          class="form-control form-control-sm"
                          placeholder="fallback"
                          :disabled="classifierRuntimeSaving || sendingMessage"
                        />
                      </div>
                    </div>
                    <div class="d-flex justify-content-end mt-2">
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-primary"
                        :disabled="classifierRuntimeSaving || sendingMessage || !selectedSession"
                        @click="saveSessionClassifierConfig"
                      >
                        {{ classifierRuntimeSaving ? 'Enregistrement…' : 'Sauvegarder override session' }}
                      </button>
                    </div>
                    <p class="text-muted small mb-0 mt-2">
                      Config effective: conf={{ classifierRuntimeEffective.phase_classifier_min_confidence ?? '-' }},
                      tokens={{ classifierRuntimeEffective.phase_classifier_max_tokens ?? '-' }},
                      chars={{ classifierRuntimeEffective.phase_classifier_max_input_chars ?? '-' }}.
                    </p>
                    <p v-if="classifierRuntimeError" class="text-danger small mb-0 mt-1">
                      {{ classifierRuntimeError }}
                    </p>
                  </div>
                  <div class="border rounded p-2 mb-2">
                    <p class="small fw-bold mb-2">P0 classifier runtime (override session, optionnel)</p>
                    <div class="d-flex gap-2 mb-2">
                      <button type="button" class="btn btn-sm btn-outline-secondary" @click="applySessionP0ClassifierPreset('safe')">safe</button>
                      <button type="button" class="btn btn-sm btn-outline-secondary" @click="applySessionP0ClassifierPreset('balanced')">balanced</button>
                      <button type="button" class="btn btn-sm btn-outline-secondary" @click="applySessionP0ClassifierPreset('aggressive')">aggressive</button>
                    </div>
                    <div class="row g-2">
                      <div class="col-12 col-md-3">
                        <label class="form-label small mb-1">Enabled</label>
                        <select
                          v-model="sessionP0ClassifierEnabled"
                          class="form-select form-select-sm"
                          :disabled="classifierRuntimeSaving || sendingMessage"
                        >
                          <option :value="null">Fallback groupe/settings</option>
                          <option :value="true">true</option>
                          <option :value="false">false</option>
                        </select>
                      </div>
                      <div class="col-12 col-md-3">
                        <label class="form-label small mb-1">Min confidence</label>
                        <input
                          v-model.number="sessionP0ClassifierMinConfidence"
                          type="number"
                          min="0"
                          max="1"
                          step="0.01"
                          class="form-control form-control-sm"
                          placeholder="fallback"
                          :disabled="classifierRuntimeSaving || sendingMessage"
                        />
                      </div>
                      <div class="col-12 col-md-3">
                        <label class="form-label small mb-1">Max tokens</label>
                        <input
                          v-model.number="sessionP0ClassifierMaxTokens"
                          type="number"
                          min="1"
                          step="1"
                          class="form-control form-control-sm"
                          placeholder="fallback"
                          :disabled="classifierRuntimeSaving || sendingMessage"
                        />
                      </div>
                      <div class="col-12 col-md-3">
                        <label class="form-label small mb-1">Max input chars</label>
                        <input
                          v-model.number="sessionP0ClassifierMaxInputChars"
                          type="number"
                          min="1"
                          step="1"
                          class="form-control form-control-sm"
                          placeholder="fallback"
                          :disabled="classifierRuntimeSaving || sendingMessage"
                        />
                      </div>
                    </div>
                    <p class="text-muted small mb-0 mt-2">
                      Utilisé pour classifier les variables P0 sémantiques avant `DecisionEngine`.
                    </p>
                  </div>
                </div>
                <div class="modal-footer">
                  <button type="button" class="btn btn-sm btn-secondary" @click="closeTuningModal">Fermer</button>
                </div>
              </div>
            </div>
          </div>
          <div v-if="tuningModalOpen" class="modal-backdrop fade show" @click="closeTuningModal"></div>
          <div
            ref="messagesContainer"
            class="border rounded p-3 mb-2"
            id="messages-container"
            style="max-height: 320px; overflow-y: auto;"
          >
            <Teleport to="body">
            <div
              v-if="payloadModalOpen"
              class="modal fade show d-block"
              style="z-index: 1055"
              tabindex="-1"
              role="dialog"
              aria-modal="true"
            >
              <div class="modal-dialog modal-lg modal-dialog-scrollable" role="document">
                <div class="modal-content">
                  <div class="modal-header">
                    <h5 class="modal-title">{{ payloadModalTitle }}</h5>
                    <button type="button" class="btn-close" aria-label="Close" @click="closePayloadModal" />
                  </div>
                  <div class="modal-body">
                    <template v-if="payloadModalTitle.includes('request')">
                      <div class="row g-2 mb-3">
                        <div
                          v-for="(row, idx) in payloadKeyValueRows(payloadModalData)"
                          :key="`rq-kv-${idx}`"
                          class="col-12 col-md-6"
                        >
                          <div class="small text-muted">{{ row[0] }}</div>
                          <div class="small"><strong>{{ row[1] }}</strong></div>
                        </div>
                      </div>
                      <div
                        v-if="payloadModalTitle.includes('request') && hasObjectEntries(payloadModalData.tutor_prompt_snapshot)"
                        class="mb-3 border rounded p-2 bg-light-subtle"
                      >
                        <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-2">
                          <div class="small fw-bold text-muted mb-0">TutorPrompt au moment du tour</div>
                          <div class="d-flex flex-wrap gap-1">
                            <button
                              type="button"
                              class="btn btn-sm btn-outline-secondary"
                              @click="copyTutorPromptSnapshotJson"
                            >
                              Copier le JSON
                            </button>
                            <button
                              type="button"
                              class="btn btn-sm btn-outline-secondary"
                              @click="tutorSnapshotShowTemplates = !tutorSnapshotShowTemplates"
                            >
                              {{ tutorSnapshotShowTemplates ? 'Masquer les templates' : 'Voir les templates' }}
                            </button>
                          </div>
                        </div>
                        <div class="row g-2 small">
                          <div class="col-12 col-md-6">
                            <div class="text-muted">code</div>
                            <div><code>{{ payloadModalData.tutor_prompt_snapshot.code }}</code></div>
                          </div>
                          <div class="col-12 col-md-6">
                            <div class="text-muted">output_format_mode</div>
                            <div><code>{{ payloadModalData.tutor_prompt_snapshot.output_format_mode }}</code></div>
                          </div>
                          <div class="col-12 col-md-6">
                            <div class="text-muted">max_questions_per_turn</div>
                            <div><code>{{ payloadModalData.tutor_prompt_snapshot.max_questions_per_turn }}</code></div>
                          </div>
                          <div class="col-12 col-md-6">
                            <div class="text-muted">max_tokens</div>
                            <div><code>{{ payloadModalData.tutor_prompt_snapshot.max_tokens }}</code></div>
                          </div>
                        </div>
                        <div v-if="tutorSnapshotShowTemplates" class="mt-2">
                          <div class="small text-muted mb-1">system_template</div>
                          <pre
                            class="small bg-white p-2 rounded mb-2"
                            style="white-space: pre-wrap;"
                          >{{ payloadModalData.tutor_prompt_snapshot.system_template || '—' }}</pre>
                          <div class="small text-muted mb-1">user_template</div>
                          <pre
                            class="small bg-white p-2 rounded mb-0"
                            style="white-space: pre-wrap;"
                          >{{ payloadModalData.tutor_prompt_snapshot.user_template || '—' }}</pre>
                        </div>
                      </div>
                      <div class="mb-3">
                        <div class="small text-muted mb-1">System prompt</div>
                        <pre class="small bg-light p-2 rounded mb-0" style="white-space: pre-wrap;">{{ payloadModalData.system_prompt || '—' }}</pre>
                      </div>
                      <div class="mb-3">
                        <div class="small text-muted mb-1">User prompt</div>
                        <pre class="small bg-light p-2 rounded mb-0" style="white-space: pre-wrap;">{{ payloadModalData.user_prompt || '—' }}</pre>
                      </div>
                      <div v-if="payloadModalData.phase_classifier_runtime_config" class="mb-3">
                        <div class="small text-muted mb-1">Classifier runtime config</div>
                        <pre class="small bg-light p-2 rounded mb-0" style="white-space: pre-wrap;">{{ JSON.stringify(payloadModalData.phase_classifier_runtime_config, null, 2) }}</pre>
                      </div>
                      <div v-if="payloadModalData.phase_classifier_runtime_config_source" class="mb-3">
                        <div class="small text-muted mb-1">Classifier runtime source</div>
                        <pre class="small bg-light p-2 rounded mb-0" style="white-space: pre-wrap;">{{ JSON.stringify(payloadModalData.phase_classifier_runtime_config_source, null, 2) }}</pre>
                      </div>
                      <div v-if="p0ClassifierKeyValueRows(payloadModalData.p0_classifier).length" class="mb-3">
                        <div class="small text-muted mb-1">P0 classifier</div>
                        <div class="row g-2">
                          <div
                            v-for="(row, idx) in p0ClassifierKeyValueRows(payloadModalData.p0_classifier)"
                            :key="`p0clf-kv-${idx}`"
                            class="col-12 col-md-6"
                          >
                            <div class="small text-muted">{{ row[0] }}</div>
                            <div class="small"><strong>{{ row[1] }}</strong></div>
                          </div>
                        </div>
                      </div>
                      <div v-if="hasObjectEntries(payloadModalData.p0_classifier?.runtime_config)" class="mb-3">
                        <div class="small text-muted mb-1">P0 classifier runtime config</div>
                        <pre class="small bg-light p-2 rounded mb-0" style="white-space: pre-wrap;">{{ JSON.stringify(payloadModalData.p0_classifier.runtime_config, null, 2) }}</pre>
                      </div>
                      <div v-if="hasObjectEntries(payloadModalData.p0_classifier?.runtime_config_source)" class="mb-3">
                        <div class="small text-muted mb-1">P0 classifier runtime source</div>
                        <pre class="small bg-light p-2 rounded mb-0" style="white-space: pre-wrap;">{{ JSON.stringify(payloadModalData.p0_classifier.runtime_config_source, null, 2) }}</pre>
                      </div>
                      <div v-if="hasObjectEntries(payloadModalData.p0_classifier?.source_by_field)" class="mb-3">
                        <div class="small text-muted mb-1">P0 source par variable</div>
                        <pre class="small bg-light p-2 rounded mb-0" style="white-space: pre-wrap;">{{ JSON.stringify(payloadModalData.p0_classifier.source_by_field, null, 2) }}</pre>
                      </div>
                      <div v-if="payloadModalData.request_payload?.messages?.length" class="mb-3">
                        <div class="small text-muted mb-1">Historique envoyé au modèle</div>
                        <ul class="list-group list-group-flush">
                          <li
                            v-for="(msg, msgIndex) in payloadModalData.request_payload.messages"
                            :key="`request-msg-${msgIndex}`"
                            class="list-group-item px-0"
                          >
                            <div class="small">
                              <span class="badge bg-secondary me-1">{{ msg.role }}</span>
                              {{ payloadPreview(msg.content, 500) }}
                            </div>
                          </li>
                        </ul>
                      </div>
                    </template>
                    <template v-else>
                      <div class="row g-2 mb-3">
                        <div
                          v-for="(row, idx) in responseKeyValueRows(payloadModalData)"
                          :key="`rs-kv-${idx}`"
                          class="col-12 col-md-6"
                        >
                          <div class="small text-muted">{{ row[0] }}</div>
                          <div class="small"><strong>{{ row[1] }}</strong></div>
                        </div>
                      </div>
                      <div class="mb-3">
                        <div class="small text-muted mb-1">Contenu assistant (raw_response)</div>
                        <pre class="small bg-light p-2 rounded mb-0" style="white-space: pre-wrap;">{{ payloadModalData.raw_response?.choices?.[0]?.message?.content || '—' }}</pre>
                      </div>
                    </template>
                    <div v-if="payloadModalData.prompt_sources" class="mb-3">
                      <div class="small text-muted mb-1">Sources dans le prompt (tour)</div>
                      <ul class="small mb-1 ps-3">
                        <li v-if="payloadModalData.prompt_sources.referential?.included">
                          Référentiel : {{ payloadModalData.prompt_sources.referential.referential_name || '—' }}
                          <span
                            v-if="payloadModalData.prompt_sources.referential.referential_source_ref"
                            class="text-muted"
                          >
                            ({{ payloadModalData.prompt_sources.referential.referential_source_ref }})
                          </span>
                          — {{ payloadModalData.prompt_sources.referential.focus_items_count }} item(s) en focus
                        </li>
                        <li v-if="payloadModalData.prompt_sources.rag?.used">
                          Documents RAG : {{ payloadModalData.prompt_sources.rag.selection_count }} extrait(s)
                        </li>
                        <li
                          v-if="
                            !payloadModalData.prompt_sources.referential?.included &&
                              !payloadModalData.prompt_sources.rag?.used
                          "
                          class="text-muted"
                        >
                          Aucune source référentiel ni RAG dans le prompt.
                        </li>
                      </ul>
                      <ul
                        v-if="payloadModalData.prompt_sources.rag?.selections?.length"
                        class="list-unstyled small mb-0"
                      >
                        <li
                          v-for="(s, i) in payloadModalData.prompt_sources.rag.selections"
                          :key="`pss-${i}`"
                        >
                          <span class="text-body">{{ s.document_title }}</span>
                          <span v-if="s.score != null" class="text-muted"> (score {{ s.score }})</span>
                        </li>
                      </ul>
                    </div>
                    <div>
                      <div class="small text-muted mb-1">JSON brut</div>
                      <pre class="small bg-light p-2 rounded mb-0" style="white-space: pre-wrap;">{{ payloadModalRaw }}</pre>
                    </div>
                  </div>
                  <div class="modal-footer">
                    <button type="button" class="btn btn-sm btn-secondary" @click="closePayloadModal">Fermer</button>
                  </div>
                </div>
              </div>
            </div>
            <div
              v-if="payloadModalOpen"
              class="modal-backdrop fade show"
              style="z-index: 1050"
              @click="closePayloadModal"
            ></div>
            <div
              v-if="p0ModalOpen"
              class="modal fade show d-block"
              style="z-index: 1055"
              tabindex="-1"
              role="dialog"
              aria-modal="true"
            >
              <div class="modal-dialog modal-xl modal-dialog-scrollable" role="document">
                <div class="modal-content">
                  <div class="modal-header">
                    <h5 class="modal-title">État P0 & décision locale</h5>
                    <button type="button" class="btn-close" aria-label="Close" @click="closeP0Modal" />
                  </div>
                  <div class="modal-body">
                    <p class="small text-muted mb-3">{{ p0ModalContext }}</p>
                    <div
                      v-if="p0ModalSummaryComputed.chips.length"
                      class="border rounded p-2 mb-3 bg-light-subtle"
                    >
                      <div class="small text-muted mb-2">Résumé du tour</div>
                      <div class="d-flex flex-wrap gap-1">
                        <span
                          v-for="(c, i) in p0ModalSummaryComputed.chips"
                          :key="`p0sum-${i}-${c.kind}`"
                          class="badge rounded-pill"
                          :class="c.badgeClass"
                        >
                          {{ c.label }}
                        </span>
                      </div>
                    </div>
                    <h6 class="text-secondary border-bottom pb-1 mb-2">Variables P0 (noyau sémantique)</h6>
                    <div class="table-responsive mb-4">
                      <table class="table table-sm table-bordered align-middle mb-0">
                        <tbody>
                          <tr v-for="row in p0NucleusEntries(p0ModalTurnState)" :key="`p0n-${row.key}`">
                            <td class="small text-muted" style="width: 38%;">{{ row.label }}</td>
                            <td class="small"><code>{{ row.value }}</code></td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                    <template v-if="p0ThreadRegulationEntries(p0ModalTurnState).length">
                      <h6 class="text-secondary border-bottom pb-1 mb-2">Couverture du fil & signaux explicites</h6>
                      <div class="table-responsive mb-4">
                        <table class="table table-sm table-bordered align-middle mb-0">
                          <tbody>
                            <tr
                              v-for="row in p0ThreadRegulationEntries(p0ModalTurnState)"
                              :key="`p0tr-${row.key}`"
                            >
                              <td class="small text-muted" style="width: 38%;">{{ row.label }}</td>
                              <td class="small">
                                <template v-if="row.isList">
                                  <ul v-if="row.listItems.length" class="mb-0 ps-3">
                                    <li v-for="(item, li) in row.listItems" :key="`p0li-${row.key}-${li}`">
                                      {{ item }}
                                    </li>
                                  </ul>
                                  <span v-else class="text-muted">(vide)</span>
                                </template>
                                <code v-else>{{ row.value }}</code>
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </template>
                    <template v-if="p0OtherHybridEntries(p0ModalTurnState).length">
                      <h6 class="text-secondary border-bottom pb-1 mb-2">Signaux complémentaires</h6>
                      <div class="table-responsive mb-4">
                        <table class="table table-sm table-bordered align-middle mb-0">
                          <tbody>
                            <tr
                              v-for="[hKey, hVal] in p0OtherHybridEntries(p0ModalTurnState)"
                              :key="`p0h-${hKey}`"
                            >
                              <td class="small text-muted" style="width: 38%;">{{ HYBRID_LABELS[hKey] || hKey }}</td>
                              <td class="small"><code>{{ formatP0Value(hVal) }}</code></td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </template>
                    <div
                      v-if="p0ModalTurnState.debug_signals && Object.keys(p0ModalTurnState.debug_signals).length"
                      class="mb-4"
                    >
                      <h6 class="text-secondary border-bottom pb-1 mb-2">Debug signaux</h6>
                      <pre class="small bg-light p-2 rounded mb-0" style="white-space: pre-wrap;">{{ JSON.stringify(p0ModalTurnState.debug_signals, null, 2) }}</pre>
                    </div>
                    <template v-if="p0ClassifierKeyValueRows(p0ModalClassifier).length">
                      <h6 class="text-secondary border-bottom pb-1 mb-2">Classifieur P0</h6>
                      <div class="table-responsive mb-4">
                        <table class="table table-sm table-bordered align-middle mb-0">
                          <tbody>
                            <tr v-for="row in p0ClassifierKeyValueRows(p0ModalClassifier)" :key="`p0c-${row[0]}`">
                              <td class="small text-muted" style="width: 38%;">{{ row[0] }}</td>
                              <td class="small"><code>{{ row[1] }}</code></td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </template>
                    <div v-if="hasObjectEntries(p0ModalClassifier.runtime_config)" class="mb-4">
                      <h6 class="text-secondary border-bottom pb-1 mb-2">Runtime config P0 effectif</h6>
                      <pre class="small bg-light p-2 rounded mb-0" style="white-space: pre-wrap;">{{ JSON.stringify(p0ModalClassifier.runtime_config, null, 2) }}</pre>
                    </div>
                    <div v-if="hasObjectEntries(p0ModalClassifier.runtime_config_source)" class="mb-4">
                      <h6 class="text-secondary border-bottom pb-1 mb-2">Source du runtime P0</h6>
                      <pre class="small bg-light p-2 rounded mb-0" style="white-space: pre-wrap;">{{ JSON.stringify(p0ModalClassifier.runtime_config_source, null, 2) }}</pre>
                    </div>
                    <div v-if="hasObjectEntries(p0ModalClassifier.source_by_field)" class="mb-4">
                      <h6 class="text-secondary border-bottom pb-1 mb-2">Source finale par variable</h6>
                      <pre class="small bg-light p-2 rounded mb-0" style="white-space: pre-wrap;">{{ JSON.stringify(p0ModalClassifier.source_by_field, null, 2) }}</pre>
                    </div>
                    <h6 class="text-secondary border-bottom pb-1 mb-2">Décision conversationnelle locale</h6>
                    <div
                      v-if="p0DecisionConstraintBadges(p0ModalDecision).length"
                      class="d-flex flex-wrap gap-1 mb-2"
                    >
                      <span
                        v-for="(b, bi) in p0DecisionConstraintBadges(p0ModalDecision)"
                        :key="`p0con-${bi}`"
                        class="badge rounded-pill"
                        :class="b.emphasized ? 'text-bg-warning' : 'text-bg-light text-dark border'"
                      >
                        {{ b.label }}
                      </span>
                    </div>
                    <div v-if="p0DecisionEntries(p0ModalDecision).length" class="table-responsive">
                      <table class="table table-sm table-bordered align-middle mb-0">
                        <tbody>
                          <tr v-for="row in p0DecisionEntries(p0ModalDecision)" :key="`p0d-${row.key}`">
                            <td class="small text-muted" style="width: 38%;">{{ row.label }}</td>
                            <td class="small">
                              <span
                                v-if="row.key === 'number_of_questions'"
                                class="badge rounded-pill"
                                :class="numberOfQuestionsBadgeClass(row.raw)"
                              >{{ row.value }}</span>
                              <span
                                v-else-if="row.key === 'pedagogical_move'"
                                class="badge rounded-pill"
                                :class="pedagogicalMoveBadgeClass(row.raw, p0ModalDecision)"
                              >{{ row.value }}</span>
                              <code v-else>{{ row.value }}</code>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                    <p v-else class="small text-muted mb-0">
                      Aucune décision structurée enregistrée pour ce tour.
                    </p>
                  </div>
                  <div class="modal-footer">
                    <button type="button" class="btn btn-sm btn-secondary" @click="closeP0Modal">Fermer</button>
                  </div>
                </div>
              </div>
            </div>
            <div
              v-if="p0ModalOpen"
              class="modal-backdrop fade show"
              style="z-index: 1050"
              @click="closeP0Modal"
            ></div>
            </Teleport>
            <div
              v-for="m in messages"
              :key="m.id"
              class="mb-2"
              :class="m.role === 'ASSISTANT' ? 'text-start bg-secondary-subtle rounded p-2' : 'text-end'"
            >
              <div class="d-inline-flex align-items-center gap-2">
                <span class="badge bg-secondary">{{ m.role === 'ASSISTANT' ? 'Hugo' : 'Moi' }}</span>
                <span
                  v-if="canShowPayloadDetails(m)"
                  class="badge rounded-pill text-bg-light border"
                  title="Payload LLM disponible"
                >
                  payload
                </span>
                <button
                  v-if="canShowPayloadDetails(m)"
                  type="button"
                  class="btn btn-sm btn-link p-0 text-decoration-none"
                  title="Voir le payload LLM"
                  @click="openPayloadModal(m)"
                >
                  <i class="bi bi-eye" />
                </button>
                <span
                  v-if="canShowP0Modal(m)"
                  class="badge rounded-pill text-bg-info border"
                  title="État P0 disponible"
                >
                  P0
                </span>
                <button
                  v-if="canShowP0Modal(m)"
                  type="button"
                  class="btn btn-sm btn-link p-0 text-decoration-none"
                  title="Voir l’état P0 et la décision locale pour ce tour"
                  @click="openP0Modal(m)"
                >
                  <i class="bi bi-grid-3x3-gap" />
                </button>
                <span
                  v-if="p0ClassifierBadgesByMessageId[m.id]"
                  class="badge rounded-pill border small"
                  :class="p0ClassifierBadgesByMessageId[m.id].badgeClass"
                  :title="p0ClassifierBadgesByMessageId[m.id].title"
                >
                  P0 {{ p0ClassifierBadgesByMessageId[m.id].label }}
                </span>
                <span
                  v-if="promptSourcesBadgesByMessageId[m.id]?.ref"
                  class="badge rounded-pill text-bg-primary border"
                  title="Référentiel présent dans le prompt de ce tour (pas une preuve d’usage par le modèle)"
                >
                  Réf.
                </span>
                <span
                  v-if="promptSourcesBadgesByMessageId[m.id]?.docs"
                  class="badge rounded-pill text-bg-dark border"
                  title="Extraits documentaires (RAG) présents dans le prompt de ce tour (pas une preuve d’usage par le modèle)"
                >
                  Docs
                </span>
              </div>
              <div class="small text-muted">{{ formatDate(m.created_at) }}</div>
              <div style="white-space: pre-wrap;">{{ resolveMessageContent(m) }}</div>
            </div>
            <div v-if="sendingMessage" class="mt-2 text-start text-muted small">
              <div class="d-inline-flex align-items-center gap-2">
                <span class="spinner-border spinner-border-sm text-primary" role="status" aria-hidden="true" />
                <span>Hugo réfléchit…</span>
              </div>
            </div>
          </div>
          <div v-if="selectedSession && !messages.length" class="mb-3">
            <p class="small text-muted mb-2">Besoin d’une idée pour démarrer ?</p>
            <div v-if="loading.starterPrompts" class="small text-muted">Chargement des suggestions…</div>
            <div v-else class="d-flex flex-wrap gap-2">
              <button
                v-for="sp in starterPrompts"
                :key="sp.id"
                type="button"
                class="btn btn-sm btn-outline-secondary"
                @click="applyStarterPrompt(sp)"
              >
                {{ sp.button }}
              </button>
            </div>
            <p v-if="starterError" class="text-danger small mb-0">
              {{ starterError }}
            </p>
          </div>
          <form @submit.prevent="sendMessage" class="mb-3">
            <div v-if="numberedQuestions.length" class="border rounded p-2 mb-2 bg-light-subtle">
              <p class="small text-muted mb-2">
                Réponse guidée (optionnelle) : répondez question par question.
              </p>
              <div
                v-for="q in numberedQuestions"
                :key="q.index"
                class="mb-2"
              >
                <label class="form-label small mb-1">
                  {{ q.index }}. {{ q.question }}
                </label>
                <input
                  v-model="structuredAnswers[q.index]"
                  type="text"
                  class="form-control form-control-sm"
                  :placeholder="`Réponse à la question ${q.index}`"
                  :disabled="sendingMessage"
                />
              </div>
            </div>
            <div class="mb-2">
              <textarea
                v-model="messageContent"
                class="form-control"
                rows="3"
                :placeholder="numberedQuestions.length ? 'Commentaire libre (optionnel)…' : 'Commentaire'"
                :disabled="sendingMessage"
              />
            </div>
            <div class="d-flex justify-content-end">
              <button
                type="submit"
                class="btn btn-primary"
                :disabled="!canSendMessage"
              >
                {{ sendingMessage ? '…' : 'Envoyer' }}
              </button>
            </div>
          </form>
          <div class="border-top pt-3 mb-3">
            <div class="d-flex justify-content-between align-items-center">
              <label class="form-label small fw-bold mb-0">
                Preuves associées à la session
                ({{ evidenceCountForSession(selectedSession?.id) }})
              </label>
              <button
                type="button"
                class="btn btn-sm btn-outline-primary"
                :disabled="!evidenceCountForSession(selectedSession?.id)"
                @click="openEvidenceListModalForSession(selectedSession)"
              >
                Voir le détail
              </button>
            </div>
          </div>
          <div class="border-top pt-3">
            <label class="form-label small fw-bold">Partage avec le tuteur (défaut: tout désactivé)</label>
            <div class="form-check form-switch">
              <input id="share_summary" v-model="shareFlags.share_summary" class="form-check-input" type="checkbox" @change="updateShare" />
              <label class="form-check-label" for="share_summary">Résumé</label>
            </div>
            <div class="form-check form-switch">
              <input id="share_evidence" v-model="shareFlags.share_evidence" class="form-check-input" type="checkbox" @change="updateShare" />
              <label class="form-check-label" for="share_evidence">Preuves</label>
            </div>
            <div class="form-check form-switch">
              <input id="share_verbatim" v-model="shareFlags.share_verbatim" class="form-check-input" type="checkbox" @change="updateShare" />
              <label class="form-check-label" for="share_verbatim">Verbatim (texte du chat)</label>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Traces -->
  <div v-show="activeTab === 'traces'" class="card">
    <div class="card-body">
      <div v-if="loading.traces" class="text-center py-4"><div class="spinner-border text-primary"></div></div>
      <div v-else-if="traces.length" class="table-responsive">
        <table class="table table-sm">
          <thead><tr><th>Date</th><th>Validé</th><th>Session</th><th>Preuves</th></tr></thead>
          <tbody>
            <tr v-for="t in traces" :key="t.id">
              <td>{{ formatDate(t.created_at) }}</td>
              <td><span v-if="t.validated_at" class="badge bg-success">Oui</span><span v-else class="badge bg-secondary">Non</span></td>
              <td>{{ t.session }}</td>
              <td>
                <div class="d-flex align-items-center gap-2">
                  <span class="badge bg-light text-dark border">{{ evidenceCountForTrace(t.id) }}</span>
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-primary"
                    :disabled="!evidenceCountForTrace(t.id)"
                    @click="openEvidenceListModalForTrace(t)"
                  >
                    Voir
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="text-muted mb-0">Aucune trace. Générez une trace depuis une session Hugo (endpoint generate-trace).</p>
    </div>
  </div>

  <!-- Preuves -->
  <div v-show="activeTab === 'evidence'" class="card">
    <div class="card-body">
      <div class="mb-4">
        <label class="form-label">Ajouter une preuve (lier à une session ou une trace)</label>
        <div class="row g-2">
          <div class="col-12 col-md-4">
            <label for="evidence-session-select" class="form-label small mb-1">Session (optionnel)</label>
            <select
              id="evidence-session-select"
              v-model="uploadSessionId"
              class="form-select form-select-sm"
            >
              <option value="">Sélectionner une session…</option>
              <option v-for="s in sessions" :key="s.id" :value="s.id">
                {{ evidenceSessionLabel(s) }}
              </option>
            </select>
          </div>
          <div class="col-12 col-md-4">
            <label for="evidence-trace-select" class="form-label small mb-1">Trace (optionnel)</label>
            <select
              id="evidence-trace-select"
              v-model="uploadTraceId"
              class="form-select form-select-sm"
            >
              <option value="">Sélectionner une trace…</option>
              <option v-for="t in traces" :key="t.id" :value="t.id">
                {{ evidenceTraceLabel(t) }}
              </option>
            </select>
          </div>
          <div class="col-12 col-md-4 d-flex gap-2">
            <input ref="uploadFile" type="file" class="form-control form-control-sm" accept="image/*,.pdf" />
            <button type="button" class="btn btn-sm btn-primary" :disabled="uploadEvidenceLoading" @click="uploadEvidence">Envoyer</button>
          </div>
        </div>
        <small class="text-muted">Au moins un de session ou trace doit être renseigné.</small>
      </div>
      <div v-if="loading.evidence" class="text-center py-4"><div class="spinner-border text-primary"></div></div>
      <div v-else-if="evidence.length" class="table-responsive">
        <table class="table table-sm">
          <thead><tr><th>Date</th><th>Fichier</th></tr></thead>
          <tbody>
            <tr v-for="e in evidence" :key="e.id">
              <td>{{ formatDate(e.created_at) }}</td>
              <td>
                <div class="d-flex align-items-center gap-2">
                  <code>{{ e.file_path }}</code>
                  <button
                    v-if="isImageEvidence(e)"
                    type="button"
                    class="btn btn-sm btn-outline-primary"
                    @click="openEvidencePreview(e)"
                  >
                    Voir
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="text-muted mb-0">Aucune preuve.</p>
    </div>
  </div>

  <div v-show="activeTab === 'documents'" class="card">
    <div class="card-body">
      <p v-if="!groupId" class="text-muted mb-0">Aucun groupe sélectionné.</p>
      <template v-else>
        <p class="small text-muted mb-3">
          Documents liés à votre groupe (même bibliothèque que pour Hugo RAG). Cliquez pour lire le texte source.
        </p>
        <div v-if="loading.groupLibrary" class="text-center py-4">
          <div class="spinner-border text-primary" role="status" />
        </div>
        <p v-else-if="groupLibraryError" class="text-danger small mb-0">{{ groupLibraryError }}</p>
        <div v-else-if="groupLibraryItems.length" class="list-group">
          <button
            v-for="item in groupLibraryItems"
            :key="item.id"
            type="button"
            class="list-group-item list-group-item-action d-flex justify-content-between align-items-center text-start"
            @click="openDocumentModal(item)"
          >
            <span class="me-2">{{ item.document_title }}</span>
            <span class="badge bg-light text-dark border text-nowrap">{{ item.chunks_count }} chunk(s)</span>
          </button>
        </div>
        <p v-else class="text-muted mb-0">Aucun document pour ce groupe.</p>
      </template>
    </div>
  </div>

  <Teleport to="body">
    <div
      v-if="docModalOpen"
      class="modal fade show d-block"
      style="z-index: 1055"
      tabindex="-1"
      role="dialog"
      aria-modal="true"
    >
      <div class="modal-dialog modal-lg modal-dialog-scrollable" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ docModalTitle }}</h5>
            <button type="button" class="btn-close" aria-label="Fermer" @click="closeDocumentModal" />
          </div>
          <div class="modal-body">
            <div v-if="docModalLoading" class="text-center py-4">
              <div class="spinner-border text-primary" role="status" />
            </div>
            <pre
              v-else
              class="small bg-light p-3 rounded mb-0"
              style="white-space: pre-wrap; max-height: 70vh; overflow: auto;"
            >{{ docModalText || '—' }}</pre>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" @click="closeDocumentModal">Fermer</button>
          </div>
        </div>
      </div>
    </div>
    <div
      v-if="docModalOpen"
      class="modal-backdrop fade show"
      style="z-index: 1050"
      @click="closeDocumentModal"
    />
  </Teleport>

  <ReferentialExplorerModal
    v-model="referentialExplorerOpen"
    :referential-id="referentialExplorerId"
    :referential-name="referentialExplorerName"
  />
</template>
