<script setup>
import { computed, ref, watch } from 'vue'
import {
  TUTOR_IMPORT_KINDS,
  TUTOR_IMPORT_LABELS,
  buildTutorArtifactMeta,
} from '../../utils/tutorChatImport.js'

const props = defineProps({
  open: { type: Boolean, default: false },
  draft: { type: Object, default: null },
})

const emit = defineEmits(['close', 'confirm'])

const submitting = ref(false)
const error = ref('')
const structured = ref({})

const modalTitle = computed(() => (
  props.draft?.import_kind ? (TUTOR_IMPORT_LABELS[props.draft.import_kind] || 'Confirmer le brouillon') : 'Confirmer le brouillon'
))

watch(
  () => [props.open, props.draft],
  ([open, draft]) => {
    if (open && draft) {
      error.value = ''
      structured.value = { ...(draft.structured || {}) }
    }
  },
  { immediate: true },
)

function closeModal() {
  if (submitting.value) return
  emit('close')
}

function confirmDraft() {
  if (!props.draft || submitting.value) return
  submitting.value = true
  error.value = ''
  try {
    const merged = {
      ...props.draft,
      structured: { ...structured.value },
    }
    const artifact = buildTutorArtifactMeta(merged)
    if (!artifact) {
      error.value = 'Brouillon invalide.'
      return
    }
    emit('confirm', artifact)
    emit('close')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div
    v-if="open && draft"
    class="modal fade show d-block"
    tabindex="-1"
    role="dialog"
    aria-modal="true"
    data-testid="tutor-import-confirm-modal"
  >
    <div class="modal-dialog modal-lg modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title h6">{{ modalTitle }}</h2>
          <button type="button" class="btn-close" aria-label="Fermer" @click="closeModal" />
        </div>
        <div class="modal-body">
          <p class="small text-muted">
            Brouillon d'aide à la décision — non partagé à l'apprenant, non durable après rechargement (P1).
          </p>

          <template v-if="draft.import_kind === TUTOR_IMPORT_KINDS.SESSION_PREP">
            <div class="mb-2">
              <label class="form-label small" for="tutor-prep-goal">Objectif de l'entretien</label>
              <input id="tutor-prep-goal" v-model="structured.goal" class="form-control form-control-sm" />
            </div>
            <div class="mb-2">
              <label class="form-label small" for="tutor-prep-questions">Questions à explorer (une par ligne)</label>
              <textarea id="tutor-prep-questions" v-model="structured.questions_to_explore" class="form-control form-control-sm" rows="3" />
            </div>
            <div class="mb-2">
              <label class="form-label small" for="tutor-prep-risks">Points de vigilance</label>
              <textarea id="tutor-prep-risks" v-model="structured.risks_to_watch" class="form-control form-control-sm" rows="2" />
            </div>
          </template>

          <template v-else-if="draft.import_kind === TUTOR_IMPORT_KINDS.DIAGNOSTIC_NOTES">
            <div class="mb-2">
              <label class="form-label small" for="tutor-diag-hyp">Hypothèses prudentes</label>
              <textarea id="tutor-diag-hyp" v-model="structured.hypotheses" class="form-control form-control-sm" rows="3" />
            </div>
            <div class="mb-2">
              <label class="form-label small" for="tutor-diag-signals">Signaux observés</label>
              <textarea id="tutor-diag-signals" v-model="structured.signals_observed" class="form-control form-control-sm" rows="2" />
            </div>
          </template>

          <template v-else-if="draft.import_kind === TUTOR_IMPORT_KINDS.REFLECTION">
            <div class="mb-2">
              <label class="form-label small" for="tutor-refl-questions">Questions à poser</label>
              <textarea id="tutor-refl-questions" v-model="structured.suggested_questions" class="form-control form-control-sm" rows="3" />
            </div>
          </template>

          <template v-else-if="draft.import_kind === TUTOR_IMPORT_KINDS.JOURNAL_ENTRY">
            <div class="mb-2">
              <label class="form-label small" for="tutor-journal-summary">Synthèse</label>
              <textarea id="tutor-journal-summary" v-model="structured.summary" class="form-control form-control-sm" rows="4" />
            </div>
            <div class="mb-2">
              <label class="form-label small" for="tutor-journal-actions">Actions suivantes</label>
              <textarea id="tutor-journal-actions" v-model="structured.actions_next" class="form-control form-control-sm" rows="2" />
            </div>
          </template>

          <p v-if="error" class="text-danger small mb-0">{{ error }}</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-sm btn-outline-secondary" @click="closeModal">Annuler</button>
          <button
            type="button"
            class="btn btn-sm btn-primary"
            data-testid="tutor-import-confirm-btn"
            :disabled="submitting"
            @click="confirmDraft"
          >
            Enregistrer le brouillon (session)
          </button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="open && draft" class="modal-backdrop fade show" />
</template>
