<script setup>
import { computed, ref, watch } from 'vue'
import api from '../../api/client'
import {
  TRAINER_IMPORT_KINDS,
  TRAINER_IMPORT_LABELS,
  buildCreatePayloadFromDraft,
  buildRationalePatchPayload,
} from '../../utils/trainerChatImport.js'

const props = defineProps({
  open: { type: Boolean, default: false },
  draft: { type: Object, default: null },
  sessionGroupId: { type: String, default: '' },
})

const emit = defineEmits(['close', 'success'])

const referentialItemId = ref('')
const submitting = ref(false)
const error = ref('')
const knowledgeItems = ref([])
const loadingItems = ref(false)

const isRationale = computed(() => props.draft?.import_kind === TRAINER_IMPORT_KINDS.DECISION_RATIONALE)
const modalTitle = computed(() => (
  props.draft?.import_kind ? (TRAINER_IMPORT_LABELS[props.draft.import_kind] || 'Confirmer l\'import') : 'Confirmer l\'import'
))

async function loadKnowledgeItems() {
  if (!isRationale.value) return
  loadingItems.value = true
  try {
    const { data } = await api.get('/hugo/trainer/knowledge-items/')
    knowledgeItems.value = data.items || []
  } catch {
    knowledgeItems.value = []
  } finally {
    loadingItems.value = false
  }
}

watch(
  () => [props.open, props.draft?.import_kind],
  ([open]) => {
    if (open) {
      error.value = ''
      referentialItemId.value = ''
      loadKnowledgeItems()
    }
  },
)

function closeModal() {
  if (submitting.value) return
  emit('close')
}

async function confirmImport() {
  if (!props.draft || submitting.value) return
  submitting.value = true
  error.value = ''
  try {
    if (isRationale.value) {
      const targetId = String(props.draft.target_knowledge_item_id || '').trim()
      if (!targetId) {
        error.value = 'Sélectionnez la ressource cible.'
        return
      }
      const payload = buildRationalePatchPayload(props.draft, {
        groupId: props.sessionGroupId,
      })
      await api.patch(`/hugo/trainer/knowledge-items/${targetId}/`, payload)
    } else {
      const payload = buildCreatePayloadFromDraft(props.draft, {
        referentialItemId: referentialItemId.value.trim(),
        groupId: props.sessionGroupId,
      })
      await api.post('/hugo/trainer/knowledge-items/', payload)
    }
    emit('success')
    emit('close')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Import impossible.'
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
    data-testid="trainer-import-confirm-modal"
  >
    <div class="modal-dialog modal-lg modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title h5">{{ modalTitle }}</h2>
          <button type="button" class="btn-close" aria-label="Fermer" @click="closeModal" />
        </div>
        <div class="modal-body d-grid gap-3">
          <div class="alert alert-warning small mb-0">
            <template v-if="isRationale">
              Brouillon d’aide à la décision — relisez avant enregistrement. Ceci n’est pas une décision institutionnelle
              et ne modifie pas le statut de la ressource cible.
            </template>
            <template v-else>
              Créé depuis chat — relisez et corrigez avant validation. Aucune écriture automatique sans votre confirmation.
            </template>
          </div>

          <div v-if="isRationale">
            <label class="form-label small" for="target-knowledge-item">Ressource cible</label>
            <select
              id="target-knowledge-item"
              v-model="draft.target_knowledge_item_id"
              class="form-select form-select-sm"
              data-testid="rationale-target-item"
              :disabled="loadingItems || submitting"
            >
              <option value="">Choisir un item…</option>
              <option v-for="item in knowledgeItems" :key="item.id" :value="item.id">
                {{ item.content?.slice(0, 80) }}… ({{ item.status }})
              </option>
            </select>
          </div>

          <div v-if="sessionGroupId && !isRationale" class="small text-muted">
            Groupe cible (session) : <code>{{ sessionGroupId }}</code>
          </div>

          <div v-if="!isRationale">
            <label class="form-label small" for="import-draft-title">Titre</label>
            <input id="import-draft-title" v-model="draft.draft_title" type="text" class="form-control form-control-sm" />
          </div>

          <div v-if="!isRationale">
            <label class="form-label small" for="import-referential-item">Référentiel (optionnel)</label>
            <input
              id="import-referential-item"
              v-model="referentialItemId"
              type="text"
              class="form-control form-control-sm"
              placeholder="Identifiant référentiel"
            />
          </div>

          <div v-if="draft.import_kind === TRAINER_IMPORT_KINDS.EXPLICATION && draft.structured">
            <label class="form-label small" for="explication-objective">Notion / objectif d'apprentissage</label>
            <input id="explication-objective" v-model="draft.structured.learning_objective" type="text" class="form-control form-control-sm mb-2" />
            <label class="form-label small" for="explication-situation">Situation de référence</label>
            <textarea id="explication-situation" v-model="draft.structured.reference_situation" class="form-control form-control-sm mb-2" rows="2" />
            <label class="form-label small" for="explication-errors">Erreurs fréquentes</label>
            <textarea id="explication-errors" v-model="draft.structured.frequent_errors" class="form-control form-control-sm mb-2" rows="2" />
            <label class="form-label small" for="explication-success">Indices de réussite</label>
            <textarea id="explication-success" v-model="draft.structured.success_indicators" class="form-control form-control-sm mb-2" rows="2" />
            <label class="form-label small" for="explication-usage">Usages recommandés</label>
            <textarea id="explication-usage" v-model="draft.structured.recommended_usage" class="form-control form-control-sm" rows="2" />
          </div>

          <div v-if="isRationale && draft.structured">
            <label class="form-label small" for="rationale-decision">Décision envisagée</label>
            <input id="rationale-decision" v-model="draft.structured.envisioned_decision" type="text" class="form-control form-control-sm mb-2" />
            <label class="form-label small" for="rationale-reasons">Raisons</label>
            <textarea id="rationale-reasons" v-model="draft.structured.reasons" class="form-control form-control-sm mb-2" rows="2" />
            <label class="form-label small" for="rationale-risks">Risques</label>
            <textarea id="rationale-risks" v-model="draft.structured.risks" class="form-control form-control-sm mb-2" rows="2" />
            <label class="form-label small" for="rationale-criteria">Critères utilisés</label>
            <textarea id="rationale-criteria" v-model="draft.structured.criteria_used" class="form-control form-control-sm mb-2" rows="2" />
            <label class="form-label small" for="rationale-next">Action suivante</label>
            <textarea id="rationale-next" v-model="draft.structured.next_action" class="form-control form-control-sm" rows="2" />
          </div>

          <div>
            <label class="form-label small" for="import-draft-body">Contenu importé (révisable)</label>
            <textarea id="import-draft-body" v-model="draft.draft_body" class="form-control form-control-sm" rows="6" />
          </div>

          <p v-if="error" class="text-danger small mb-0">{{ error }}</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-sm btn-outline-secondary" :disabled="submitting" @click="closeModal">
            Annuler
          </button>
          <button type="button" class="btn btn-sm btn-primary" :disabled="submitting" data-testid="trainer-import-confirm-btn" @click="confirmImport">
            {{ submitting ? 'Enregistrement…' : 'Confirmer l\'import' }}
          </button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="open" class="modal-backdrop fade show" />
</template>
