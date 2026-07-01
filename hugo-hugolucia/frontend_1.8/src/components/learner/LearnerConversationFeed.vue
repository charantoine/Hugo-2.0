<script setup>
import { computed, ref } from 'vue'
import ImportFromChatAction from '../trainer/ImportFromChatAction.vue'
import TutorImportFromChatAction from '../tutor/TutorImportFromChatAction.vue'
import { WORKSPACE_MODES } from '../../utils/chatWorkspaceMode.js'

const PERSONA_COPY = {
  [WORKSPACE_MODES.LEARNER]: {
    emptyTitle: 'La scène est prête à commencer.',
    emptyBody: 'Décris un moment concret, une difficulté rencontrée ou une action que tu aimerais analyser avec Hugo.',
    composerLabel: 'Ton message',
    composerHint: 'Un seul message suffit. Hugo s’appuie ensuite sur le fil réel de la scène.',
    userLabel: 'Toi',
  },
  [WORKSPACE_MODES.TUTOR]: {
    emptyTitle: 'Conversation avec Hugo',
    emptyBody: 'Échangez sur le contexte apprenant, vos observations ou votre préparation d\'accompagnement.',
    composerLabel: 'Votre message',
    composerHint: 'Hugo vous aide à préparer ou documenter votre réflexion tuteur.',
    userLabel: 'Vous',
  },
  [WORKSPACE_MODES.TRAINER]: {
    emptyTitle: 'Conversation avec Hugo',
    emptyBody: 'Formulez une question métier, une explicitation pédagogique ou un arbitrage à préparer.',
    composerLabel: 'Votre message',
    composerHint: 'Les réponses peuvent être importées vers la base de connaissances après validation.',
    userLabel: 'Vous',
  },
}

const props = defineProps({
  engagementModel: { type: Object, required: true },
  displayMessages: { type: Array, default: () => [] },
  questionHints: { type: Array, default: () => [] },
  messageContent: { type: String, default: '' },
  composerPlaceholder: { type: String, default: '' },
  sendingMessage: { type: Boolean, default: false },
  isStreaming: { type: Boolean, default: false },
  shouldAnchorThread: { type: Boolean, default: false },
  streamingStatusBadge: { type: String, default: '' },
  streamingStatusMode: { type: String, default: '' },
  streamError: { type: String, default: '' },
  error: { type: String, default: '' },
  compactHeader: { type: Boolean, default: false },
  personaMode: { type: String, default: WORKSPACE_MODES.LEARNER },
  showTrainerImportActions: { type: Boolean, default: false },
  showTutorImportActions: { type: Boolean, default: false },
  tutorImportKinds: { type: Array, default: () => [] },
})

defineEmits(['update:messageContent', 'send', 'scroll', 'trainer-import', 'tutor-import'])

const copy = computed(() => PERSONA_COPY[props.personaMode] || PERSONA_COPY[WORKSPACE_MODES.LEARNER])

const lastImportableAssistantMessage = computed(() => {
  for (let index = props.displayMessages.length - 1; index >= 0; index -= 1) {
    const message = props.displayMessages[index]
    if (message.role === 'ASSISTANT' && !message.isPlaceholder && !message.isStreaming) {
      return message
    }
  }
  return null
})

const showPersonaTrainerToolbar = computed(() => (
  props.compactHeader && props.showTrainerImportActions
))
const showPersonaTutorToolbar = computed(() => (
  props.compactHeader && props.showTutorImportActions
))

const threadRef = ref(null)
defineExpose({ threadRef })

function formatDate(value) {
  if (!value) return ''
  try {
    return new Date(value).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return String(value)
  }
}
</script>

<template>
  <section class="card prod-panel prod-panel--conversation h-100 learner-conversation-feed">
    <div class="card-body d-flex flex-column">
      <div v-if="!compactHeader" class="d-flex justify-content-between align-items-start gap-3 mb-3">
        <div>
          <h2 class="prod-section-title mb-1">{{ engagementModel.profileCopy?.conversationTitle }}</h2>
          <p class="text-muted mb-0">{{ engagementModel.profileCopy?.conversationLead }}</p>
        </div>
        <span class="badge rounded-pill text-bg-light border">{{ displayMessages.length }} message(s)</span>
      </div>
      <div v-else class="d-flex justify-content-between align-items-center gap-2 mb-2">
        <h2 class="h5 mb-0">Conversation avec Hugo</h2>
        <span class="badge rounded-pill text-bg-light border">{{ displayMessages.length }} message(s)</span>
      </div>

      <div
        ref="threadRef"
        class="prod-thread"
        :class="{ 'prod-thread--empty': !displayMessages.length, 'prod-thread--v2': compactHeader }"
        @scroll.passive="$emit('scroll', $event)"
      >
        <div class="prod-thread__content" :class="{ 'prod-thread__content--anchored': shouldAnchorThread }">
          <div v-if="!displayMessages.length" class="prod-thread__empty">
            <strong>{{ copy.emptyTitle }}</strong>
            <p>{{ copy.emptyBody }}</p>
          </div>

          <article
            v-for="message in displayMessages"
            :key="message.id"
            class="prod-message"
            :class="[
              message.role === 'ASSISTANT' ? 'prod-message--assistant' : 'prod-message--learner',
              message.isPlaceholder ? 'prod-message--placeholder' : '',
            ]"
          >
            <div class="prod-message__meta">
              <span>{{ message.role === 'ASSISTANT' ? 'Hugo' : copy.userLabel }}</span>
              <time>{{ message.isStreaming ? (message.isPlaceholder ? 'préparation...' : 'en direct') : formatDate(message.created_at) }}</time>
            </div>
            <div class="prod-message__bubble">
              <div v-if="message.isPlaceholder" class="prod-message__status">
                <span class="prod-message__status-badge">{{ streamingStatusBadge }}</span>
                <span class="prod-message__status-phase">{{ streamingStatusMode }}</span>
              </div>
              <p v-for="(line, index) in String(message.displayContent || message.content || '').split('\n').filter(Boolean)" :key="`${message.id}-${index}`">
                {{ line }}
              </p>
              <div
                v-if="message.role === 'ASSISTANT' && message.rag_citations?.length"
                class="d-flex flex-wrap gap-2 mt-3"
              >
                <span
                  v-for="citation in message.rag_citations"
                  :key="`${message.id}-${citation.chunk_id}`"
                  class="badge rounded-pill text-bg-light border"
                >
                  Appui : {{ citation.document_title || citation.document_id }}
                </span>
              </div>
              <div v-if="message.isPlaceholder" class="prod-message__typing" aria-hidden="true">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <ImportFromChatAction
                v-if="showTrainerImportActions && !compactHeader && message.role === 'ASSISTANT' && !message.isPlaceholder && !message.isStreaming"
                :disabled="sendingMessage || isStreaming"
                @import="$emit('trainer-import', { importKind: $event, message })"
              />
              <TutorImportFromChatAction
                v-if="showTutorImportActions && !compactHeader && message.role === 'ASSISTANT' && !message.isPlaceholder && !message.isStreaming"
                :disabled="sendingMessage || isStreaming"
                :allowed-kinds="tutorImportKinds"
                @import="$emit('tutor-import', { importKind: $event, message })"
              />
            </div>
          </article>
        </div>
      </div>

      <div
        v-if="showPersonaTrainerToolbar"
        class="persona-import-toolbar border-top pt-3 mt-2"
        data-testid="trainer-import-toolbar"
      >
        <p class="small text-muted mb-2">
          <template v-if="lastImportableAssistantMessage">
            Importer la dernière réponse de Hugo vers la base de connaissances
          </template>
          <template v-else>
            Les boutons d'import apparaîtront après une première réponse de Hugo.
          </template>
        </p>
        <ImportFromChatAction
          :disabled="!lastImportableAssistantMessage || sendingMessage || isStreaming"
          @import="$emit('trainer-import', { importKind: $event, message: lastImportableAssistantMessage })"
        />
      </div>

      <div
        v-if="showPersonaTutorToolbar"
        class="persona-import-toolbar border-top pt-3 mt-2"
        data-testid="tutor-import-toolbar"
      >
        <p class="small text-muted mb-2">
          <template v-if="lastImportableAssistantMessage">
            Enregistrer la dernière réponse de Hugo comme brouillon tuteur
          </template>
          <template v-else>
            L'import tuteur sera disponible après une première réponse de Hugo.
          </template>
        </p>
        <TutorImportFromChatAction
          :disabled="!lastImportableAssistantMessage || sendingMessage || isStreaming"
          :allowed-kinds="tutorImportKinds"
          @import="$emit('tutor-import', { importKind: $event, message: lastImportableAssistantMessage })"
        />
      </div>

      <div v-if="questionHints.length" class="prod-hints mt-3">
        <span class="prod-hints__label">Pistes à traiter</span>
        <div class="prod-hints__list">
          <span v-for="hint in questionHints" :key="hint.index" class="prod-hint-chip">{{ hint.question }}</span>
        </div>
      </div>

      <form class="prod-composer mt-3" @submit.prevent="$emit('send')">
        <label class="form-label" for="message-content">{{ copy.composerLabel }}</label>
        <textarea
          id="message-content"
          :value="messageContent"
          class="form-control prod-composer__textarea"
          rows="4"
          :placeholder="composerPlaceholder"
          @input="$emit('update:messageContent', $event.target.value)"
        ></textarea>
        <div class="d-flex justify-content-between align-items-center gap-3 mt-3">
          <p class="text-muted small mb-0">{{ copy.composerHint }}</p>
          <button type="submit" class="btn btn-primary" :disabled="sendingMessage || !messageContent.trim()">
            {{ isStreaming ? 'Réponse en cours...' : (sendingMessage ? 'Envoi...' : 'Envoyer à Hugo') }}
          </button>
        </div>
      </form>

      <div v-if="streamError && !error" class="alert alert-warning mt-3 mb-0">{{ streamError }}</div>
      <div v-if="error" class="alert alert-danger mt-3 mb-0">{{ error }}</div>
    </div>
  </section>
</template>
