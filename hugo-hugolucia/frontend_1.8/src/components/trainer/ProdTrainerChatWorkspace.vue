<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import LearnerConversationFeed from '../learner/LearnerConversationFeed.vue'
import TrainerImportConfirmModal from './TrainerImportConfirmModal.vue'
import { useHugoSessionChat } from '../../composables/useHugoSessionChat.js'
import { buildPersonaConversationFeedModel } from '../../utils/conversationFeedModel.js'
import { buildChatImportDraft } from '../../utils/trainerChatImport.js'
import { TRAINER_ORCHESTRATOR_ROUTE_NAME, TRAINER_CHAT_PATH } from '../../utils/trainerNavigation.js'

const props = defineProps({
  sessionId: { type: String, required: true },
})

const router = useRouter()
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

const trainerImportOpen = ref(false)
const trainerImportDraft = ref(null)
const trainerImportSuccess = ref('')

const composerPlaceholder = computed(() => {
  if (isStreaming.value) return 'Hugo prépare sa réponse...'
  return 'Formulez une question métier, une situation à expliciter ou un arbitrage à préparer...'
})

function openTrainerImport({ importKind, message }) {
  trainerImportSuccess.value = ''
  trainerImportDraft.value = buildChatImportDraft(message, props.sessionId, importKind)
  trainerImportOpen.value = true
}

function closeTrainerImport() {
  trainerImportOpen.value = false
  trainerImportDraft.value = null
}

function onTrainerImportSuccess() {
  trainerImportSuccess.value = 'Import enregistré — consultez l\'orchestrateur de connaissance pour valider.'
  closeTrainerImport()
}

function goBack() {
  router.push(TRAINER_CHAT_PATH)
}

function goToOrchestrator() {
  router.push({ name: TRAINER_ORCHESTRATOR_ROUTE_NAME })
}
</script>

<template>
  <div v-if="loading" class="d-flex justify-content-center py-5">
    <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Chargement…</span></div>
  </div>

  <div v-else-if="error && !session" class="alert alert-danger">{{ error }}</div>

  <div v-else class="persona-chat-workspace persona-chat-workspace--trainer">
    <header class="card prod-panel mb-3">
      <div class="card-body py-3 d-flex flex-wrap justify-content-between align-items-center gap-3">
        <div class="d-flex flex-wrap align-items-center gap-3">
          <button type="button" class="btn btn-sm btn-outline-primary" @click="goBack">
            <i class="bi bi-arrow-left-short"></i> Retour aux sessions
          </button>
          <button type="button" class="btn btn-sm btn-outline-secondary" @click="goToOrchestrator">
            Orchestrateur
          </button>
          <div>
            <strong>Mon chat formateur</strong>
            <span class="badge rounded-pill text-bg-light border ms-2">Espace conversationnel formateur</span>
          </div>
        </div>
        <button type="button" class="btn btn-sm btn-outline-secondary" :disabled="refreshing" @click="loadWorkspace({ silent: true })">
          Actualiser
        </button>
      </div>
    </header>

    <p v-if="trainerImportSuccess" class="text-success small">{{ trainerImportSuccess }}</p>

    <LearnerConversationFeed
      ref="conversationFeedRef"
      compact-header
      persona-mode="trainer"
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
      show-trainer-import-actions
      @update:message-content="messageContent = $event"
      @send="sendMessage"
      @scroll="updateThreadPinnedState"
      @trainer-import="openTrainerImport"
    />

    <TrainerImportConfirmModal
      :open="trainerImportOpen"
      :draft="trainerImportDraft"
      :session-group-id="String(session?.group || '')"
      @close="closeTrainerImport"
      @success="onTrainerImportSuccess"
    />
  </div>
</template>
