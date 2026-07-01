<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import LearnerConversationFeed from '../learner/LearnerConversationFeed.vue'
import TutorImportConfirmModal from './TutorImportConfirmModal.vue'
import TutorWorkspaceContextPanel from './TutorWorkspaceContextPanel.vue'
import TutorSessionDraftsPanel from './TutorSessionDraftsPanel.vue'
import { useHugoSessionChat } from '../../composables/useHugoSessionChat.js'
import { buildPersonaConversationFeedModel } from '../../utils/conversationFeedModel.js'
import { buildTutorChatImportDraft } from '../../utils/tutorChatImport.js'
import { importKindForWorkspaceProfile } from '../../utils/tutorWorkspaceSession.js'
import { isTutorWorkspaceProfileName } from '../../utils/tutorWorkspaceProfiles.js'
import { resolveWorkspaceSessionTitle, resolveWorkspaceTitleFromProfileCode } from '../../utils/tutorUiLabels.js'
import { useTutorWorkspaceStore } from '../../stores/tutorWorkspace.js'

const props = defineProps({
  sessionId: { type: String, required: true },
})

const route = useRoute()
const router = useRouter()
const tutorStore = useTutorWorkspaceStore()

const sessionIdRef = computed(() => props.sessionId)
const {
  loading,
  refreshing,
  sendingMessage,
  isStreaming,
  session,
  error,
  streamError,
  messageContent,
  conversationFeedRef,
  displayMessages,
  questionHints,
  shouldAnchorThread,
  streamingStatusBadge,
  streamingStatusMode,
  updateThreadPinnedState,
  loadWorkspace,
  sendMessage,
} = useHugoSessionChat(sessionIdRef, {
  loadUiState: false,
  loadLearnerArtifacts: false,
})

const conversationFeedModel = computed(() => buildPersonaConversationFeedModel())

const tutorImportOpen = ref(false)
const tutorImportDraft = ref(null)
const tutorImportSuccess = ref('')

const tutorWorkspaceContext = computed(() => ({
  learnerId: String(route.query.learner_id || tutorStore.context?.learnerId || '').trim(),
  groupId: String(route.query.group_id || tutorStore.context?.groupId || '').trim(),
  sourceSessionId: String(route.query.source_session_id || tutorStore.context?.sourceSessionId || '').trim(),
  profileCode: String(route.query.profile_code || tutorStore.context?.profileCode || '').trim(),
}))

const tutorImportKinds = computed(() => {
  const profileCode = tutorWorkspaceContext.value.profileCode
    || (isTutorWorkspaceProfileName(session.value?.learner_conversation_profile?.name)
      ? String(session.value?.learner_conversation_profile?.name || '').trim()
      : '')
  const kind = importKindForWorkspaceProfile(profileCode)
  return kind ? [kind] : []
})

const workspaceTitle = computed(() => (
  resolveWorkspaceSessionTitle(session.value)
  || resolveWorkspaceTitleFromProfileCode(tutorWorkspaceContext.value.profileCode)
  || 'Espace de réflexion tuteur'
))

const composerPlaceholder = computed(() => {
  if (isStreaming.value) return 'Hugo prépare sa réponse...'
  return 'Décrivez le contexte, vos observations ou votre intention d\'accompagnement...'
})

function openTutorImport({ importKind, message }) {
  tutorImportSuccess.value = ''
  tutorImportDraft.value = buildTutorChatImportDraft(message, props.sessionId, importKind, {
    learnerId: tutorWorkspaceContext.value.learnerId,
    groupId: tutorWorkspaceContext.value.groupId,
    sourceSessionId: tutorWorkspaceContext.value.sourceSessionId,
  })
  tutorImportOpen.value = true
}

function closeTutorImport() {
  tutorImportOpen.value = false
  tutorImportDraft.value = null
}

function onTutorImportConfirmed(artifact) {
  tutorStore.addArtifact(artifact)
  tutorImportSuccess.value = 'Brouillon enregistré pour cette session (non durable après rechargement).'
  closeTutorImport()
}

function goBack() {
  const { groupId, learnerId } = tutorWorkspaceContext.value
  if (groupId && learnerId) {
    router.push({ name: 'ProdTutorLearner', params: { groupId, learnerId } })
    return
  }
  router.push({ name: 'ProdTutorHome' })
}

onMounted(() => {
  tutorStore.setContext({
    workspaceSessionId: props.sessionId,
    learnerId: tutorWorkspaceContext.value.learnerId,
    groupId: tutorWorkspaceContext.value.groupId,
    sourceSessionId: tutorWorkspaceContext.value.sourceSessionId,
    profileCode: tutorWorkspaceContext.value.profileCode
      || (isTutorWorkspaceProfileName(session.value?.learner_conversation_profile?.name)
        ? String(session.value?.learner_conversation_profile?.name || '').trim()
        : ''),
  })
})
</script>

<template>
  <div v-if="loading" class="d-flex justify-content-center py-5">
    <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Chargement…</span></div>
  </div>

  <div v-else-if="error && !session" class="alert alert-danger">{{ error }}</div>

  <div v-else class="persona-chat-workspace persona-chat-workspace--tutor">
    <header class="card prod-panel mb-3">
      <div class="card-body py-3 d-flex flex-wrap justify-content-between align-items-center gap-3">
        <div class="d-flex flex-wrap align-items-center gap-3">
          <button type="button" class="btn btn-sm btn-outline-primary" @click="goBack">
            <i class="bi bi-arrow-left-short"></i> Retour
          </button>
          <div>
            <strong>Espace de réflexion tuteur</strong>
            <span
              v-if="workspaceTitle"
              class="badge rounded-pill text-bg-light border ms-2"
              data-testid="tutor-workspace-session-title"
            >
              {{ workspaceTitle }}
            </span>
          </div>
        </div>
        <button type="button" class="btn btn-sm btn-outline-secondary" :disabled="refreshing" @click="loadWorkspace({ silent: true })">
          Actualiser
        </button>
      </div>
    </header>

    <p v-if="tutorImportSuccess" class="text-success small">{{ tutorImportSuccess }}</p>

    <TutorWorkspaceContextPanel
      :learner-id="tutorWorkspaceContext.learnerId"
      :group-id="tutorWorkspaceContext.groupId"
      :source-session-id="tutorWorkspaceContext.sourceSessionId"
      :workspace-session-id="sessionId"
    />

    <TutorSessionDraftsPanel :artifacts="tutorStore.sessionArtifacts" />

    <LearnerConversationFeed
      ref="conversationFeedRef"
      compact-header
      persona-mode="tutor"
      :engagement-model="conversationFeedModel"
      :display-messages="displayMessages"
      :question-hints="questionHints"
      :message-content="messageContent"
      :composer-placeholder="composerPlaceholder"
      :sending-message="sendingMessage"
      :is-streaming="isStreaming"
      :should-anchor-thread="shouldAnchorThread"
      :streaming-status-badge="streamingStatusBadge"
      :streaming-status-mode="streamingStatusMode"
      :stream-error="streamError"
      :error="error"
      show-tutor-import-actions
      :tutor-import-kinds="tutorImportKinds"
      @update:message-content="messageContent = $event"
      @send="sendMessage"
      @scroll="updateThreadPinnedState"
      @tutor-import="openTutorImport"
    />

    <TutorImportConfirmModal
      :open="tutorImportOpen"
      :draft="tutorImportDraft"
      @close="closeTutorImport"
      @confirm="onTutorImportConfirmed"
    />
  </div>
</template>
