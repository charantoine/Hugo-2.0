export const TUTOR_IMPORT_KINDS = Object.freeze({
  SESSION_PREP: 'tutor_session_prep',
  DIAGNOSTIC_NOTES: 'tutor_diagnostic_notes',
  REFLECTION: 'tutor_reflection',
  JOURNAL_ENTRY: 'tutor_journal_entry',
})

export const TUTOR_IMPORT_LABELS = Object.freeze({
  [TUTOR_IMPORT_KINDS.SESSION_PREP]: 'Enregistrer la préparation',
  [TUTOR_IMPORT_KINDS.DIAGNOSTIC_NOTES]: 'Enregistrer les hypothèses',
  [TUTOR_IMPORT_KINDS.REFLECTION]: 'Enregistrer les questions préparées',
  [TUTOR_IMPORT_KINDS.JOURNAL_ENTRY]: 'Enregistrer le point-clé',
})

const KIND_TO_META_KEY = Object.freeze({
  [TUTOR_IMPORT_KINDS.SESSION_PREP]: 'tutor_session_prep',
  [TUTOR_IMPORT_KINDS.DIAGNOSTIC_NOTES]: 'tutor_diagnostic_notes',
  [TUTOR_IMPORT_KINDS.REFLECTION]: 'tutor_reflection',
  [TUTOR_IMPORT_KINDS.JOURNAL_ENTRY]: 'tutor_journal_entry',
})

function firstMeaningfulLine(text) {
  return String(text || '').split('\n').map((line) => line.trim()).find(Boolean) || 'Brouillon tuteur'
}

export function buildTutorChatImportDraft(message, sessionId, importKind, context = {}) {
  const body = String(message?.displayContent || message?.content || '').trim()
  const titleLine = firstMeaningfulLine(body)
  const draftTitle = titleLine.length > 120 ? `${titleLine.slice(0, 117)}...` : titleLine

  const base = {
    session_id: String(sessionId || '').trim(),
    source_message_ids: message?.id ? [String(message.id)] : [],
    import_kind: importKind,
    draft_title: draftTitle,
    draft_body: body,
    source_summary: body.slice(0, 280),
    human_validation_required: true,
    learner_id: String(context.learnerId || '').trim(),
    group_id: String(context.groupId || '').trim(),
    source_session_id: String(context.sourceSessionId || '').trim() || null,
  }

  if (importKind === TUTOR_IMPORT_KINDS.SESSION_PREP) {
    return {
      ...base,
      structured: {
        goal: draftTitle,
        questions_to_explore: '',
        risks_to_watch: '',
        next_contact_intent: '',
      },
    }
  }

  if (importKind === TUTOR_IMPORT_KINDS.DIAGNOSTIC_NOTES) {
    return {
      ...base,
      structured: {
        hypotheses: '',
        signals_observed: '',
        questions_to_confirm: '',
      },
    }
  }

  if (importKind === TUTOR_IMPORT_KINDS.REFLECTION) {
    return {
      ...base,
      structured: {
        key_moments: '',
        learner_strengths: '',
        points_of_attention: '',
        suggested_questions: '',
      },
    }
  }

  if (importKind === TUTOR_IMPORT_KINDS.JOURNAL_ENTRY) {
    return {
      ...base,
      structured: {
        summary: body,
        actions_next: '',
        emotional_tone: 'neutral',
      },
    }
  }

  return base
}

export function buildTutorArtifactMeta(draft) {
  const importKind = draft?.import_kind
  const metaKey = KIND_TO_META_KEY[importKind]
  if (!metaKey || !draft) return null

  const now = new Date().toISOString()
  const structured = draft.structured || {}

  if (importKind === TUTOR_IMPORT_KINDS.SESSION_PREP) {
    return {
      metaKey,
      payload: {
        learner_id: draft.learner_id || null,
        group_id: draft.group_id || null,
        source_session_id: draft.source_session_id,
        goal: String(structured.goal || draft.draft_title || '').trim(),
        questions_to_explore: splitLines(structured.questions_to_explore),
        risks_to_watch: splitLines(structured.risks_to_watch),
        next_contact_intent: String(structured.next_contact_intent || '').trim(),
        status: 'draft',
        session_id: draft.session_id,
        source_message_ids: draft.source_message_ids,
        created_at: now,
        visibility: 'tutor_private',
      },
    }
  }

  if (importKind === TUTOR_IMPORT_KINDS.DIAGNOSTIC_NOTES) {
    return {
      metaKey,
      payload: {
        learner_id: draft.learner_id || null,
        group_id: draft.group_id || null,
        hypotheses: parseHypotheses(structured.hypotheses),
        signals_observed: splitLines(structured.signals_observed),
        questions_to_confirm: splitLines(structured.questions_to_confirm),
        status: 'draft',
        session_id: draft.session_id,
        source_message_ids: draft.source_message_ids,
        created_at: now,
        visibility: 'tutor_private',
      },
    }
  }

  if (importKind === TUTOR_IMPORT_KINDS.REFLECTION) {
    return {
      metaKey,
      payload: {
        learner_id: draft.learner_id || null,
        group_id: draft.group_id || null,
        key_moments: splitLines(structured.key_moments),
        learner_strengths: splitLines(structured.learner_strengths),
        points_of_attention: splitLines(structured.points_of_attention),
        suggested_questions: splitLines(structured.suggested_questions),
        status: 'draft',
        session_id: draft.session_id,
        source_message_ids: draft.source_message_ids,
        created_at: now,
        visibility: 'tutor_private',
      },
    }
  }

  if (importKind === TUTOR_IMPORT_KINDS.JOURNAL_ENTRY) {
    return {
      metaKey,
      payload: {
        learner_id: draft.learner_id || null,
        group_id: draft.group_id || null,
        date_time: now,
        summary: String(structured.summary || draft.draft_body || '').trim(),
        actions_next: splitLines(structured.actions_next),
        emotional_tone: String(structured.emotional_tone || 'neutral').trim(),
        status: 'draft',
        session_id: draft.session_id,
        source_message_ids: draft.source_message_ids,
        visibility: 'tutor_private',
      },
    }
  }

  return null
}

function splitLines(value) {
  return String(value || '')
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
}

function parseHypotheses(value) {
  return splitLines(value).map((line) => ({
    label: line,
    confidence: 'low',
    evidence: '',
  }))
}

export function summarizeTutorArtifact(artifact) {
  if (!artifact?.payload) return null
  const p = artifact.payload
  if (artifact.metaKey === 'tutor_session_prep') {
    return { title: 'Préparation', line: p.goal, badge: 'brouillon' }
  }
  if (artifact.metaKey === 'tutor_diagnostic_notes') {
    const first = (p.hypotheses || [])[0]?.label
    return { title: 'Hypothèses', line: first || 'Diagnostic prudent', badge: 'brouillon' }
  }
  if (artifact.metaKey === 'tutor_reflection') {
    const first = (p.suggested_questions || [])[0]
    return { title: 'Questions préparées', line: first || 'Co-réflexion', badge: 'brouillon' }
  }
  if (artifact.metaKey === 'tutor_journal_entry') {
    return { title: 'Point-clé', line: p.summary, badge: 'brouillon' }
  }
  return null
}
