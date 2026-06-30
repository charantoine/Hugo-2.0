/** Pure helpers for trainer library UI (testable without Vue Test Utils). */

export const CONVERSATION_ROLES = [
  { value: 'reference_course', label: 'Référence cours' },
  { value: 'support', label: 'Support' },
  { value: 'context', label: 'Contexte' },
  { value: 'example', label: 'Exemple' },
  { value: 'technical_point', label: 'Point technique' },
  { value: 'other', label: 'Autre' },
]

export const PEDAGOGICAL_INTENTS = [
  { value: 'diagnosis', label: 'Diagnostic' },
  { value: 'explanation', label: 'Explication' },
  { value: 'practice_support', label: 'Aide pratique' },
  { value: 'contextualization', label: 'Contextualisation' },
]

export const VISIBILITY_OPTIONS = [
  { value: 'learner_citable', label: 'Citable apprenant' },
  { value: 'internal_only', label: 'Interne seulement' },
]

/** Fiabilité formateur : * = brouillon, **** = référence stricte. */
export const TRAINER_RELIABILITY_OPTIONS = [
  { value: '1', label: '*', title: 'Brouillon — prudence maximale' },
  { value: '2', label: '**', title: 'Provisoire' },
  { value: '3', label: '***', title: 'Bon niveau (défaut)' },
  { value: '4', label: '****', title: 'Référence — à suivre strictement' },
]

export function buildDocumentMeta({
  conversationRole = 'reference_course',
  pedagogicalIntent = 'explanation',
  visibility = 'learner_citable',
  trainerReliability = '3',
} = {}) {
  return {
    conversation_role: conversationRole,
    pedagogical_intent: pedagogicalIntent,
    visibility,
    trainer_reliability: trainerReliability,
  }
}

export function mergeDocumentMeta(existingMeta, patch) {
  const merged = { ...(existingMeta || {}), ...(patch || {}) }
  delete merged.origin
  return merged
}

export function normalizeDocumentsList(apiResponse) {
  if (Array.isArray(apiResponse)) return apiResponse
  return apiResponse?.results || []
}

export function normalizeLibraryItems(apiResponse) {
  return apiResponse?.items || []
}

export function isDocumentLinked(libraryItems, documentId, status = 'ACTIVE') {
  return (libraryItems || []).some(
    (item) => item.document_id === documentId && item.status === status,
  )
}

export function approxDocumentSize(extractedChars = 0) {
  const chars = Number(extractedChars) || 0
  if (chars > 1_000_000) return `${(chars / 1_000_000).toFixed(1)} Mo (texte)`
  if (chars > 1000) return `${Math.round(chars / 1000)} ko (texte)`
  return chars ? `${chars} car.` : '—'
}

export function roleLabel(value) {
  return CONVERSATION_ROLES.find((r) => r.value === value)?.label || value || '—'
}

export function intentLabel(value) {
  return PEDAGOGICAL_INTENTS.find((r) => r.value === value)?.label || value || '—'
}

export function reliabilityLabel(value) {
  return TRAINER_RELIABILITY_OPTIONS.find((r) => r.value === value)?.label || '***'
}

/**
 * Payload for POST /documents/ (text creation from trainer library).
 * Note: meta.origin is stamped server-side; never sent from client.
 */
export function buildCreateDocumentPayload({ title, sourceText, meta }) {
  return {
    title: String(title || '').trim(),
    source_text: sourceText || '',
    meta: meta || buildDocumentMeta(),
  }
}

/**
 * Payload for PATCH /documents/{id}/ when editing inline meta.
 */
export function buildPatchDocumentMetaPayload(existingMeta, patch) {
  return { meta: mergeDocumentMeta(existingMeta, patch) }
}
