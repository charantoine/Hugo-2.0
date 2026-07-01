export const TRAINER_IMPORT_KINDS = Object.freeze({
  RESOURCE_PROVISIONAL: 'trainer_resource_provisional',
  EXPLICATION: 'trainer_explication',
  DECISION_RATIONALE: 'trainer_decision_rationale',
})

export const TRAINER_IMPORT_LABELS = Object.freeze({
  [TRAINER_IMPORT_KINDS.RESOURCE_PROVISIONAL]: 'Importer comme ressource provisoire',
  [TRAINER_IMPORT_KINDS.EXPLICATION]: 'Importer comme explicitation pédagogique',
  [TRAINER_IMPORT_KINDS.DECISION_RATIONALE]: 'Importer comme justification d\'arbitrage',
})

function firstMeaningfulLine(text) {
  return String(text || '').split('\n').map((line) => line.trim()).find(Boolean) || 'Import depuis chat'
}

export function buildChatImportDraft(message, sessionId, importKind) {
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
  }

  if (importKind === TRAINER_IMPORT_KINDS.EXPLICATION) {
    return {
      ...base,
      structured: {
        learning_objective: '',
        reference_situation: '',
        frequent_errors: '',
        success_indicators: '',
        recommended_usage: '',
      },
    }
  }

  if (importKind === TRAINER_IMPORT_KINDS.DECISION_RATIONALE) {
    return {
      ...base,
      target_knowledge_item_id: '',
      structured: {
        envisioned_decision: '',
        reasons: '',
        risks: '',
        criteria_used: '',
        next_action: '',
      },
    }
  }

  return base
}

function importMeta(draft, { groupId = '' } = {}) {
  const meta = {
    import_kind: draft.import_kind,
    session_id: draft.session_id,
    source_message_ids: draft.source_message_ids,
    draft_title: draft.draft_title,
    source_summary: draft.source_summary,
    source: 'chat',
  }
  const normalizedGroupId = String(groupId || draft.group_id || '').trim()
  if (normalizedGroupId) {
    meta.group_id = normalizedGroupId
  }
  return meta
}

export function buildCreatePayloadFromDraft(draft, { referentialItemId = '', groupId = '' } = {}) {
  if (draft.import_kind === TRAINER_IMPORT_KINDS.EXPLICATION) {
    const structured = draft.structured || {}
    const sections = [
      draft.draft_title,
      '',
      structured.learning_objective && `Notion / objectif : ${structured.learning_objective}`,
      structured.reference_situation && `Situation de référence : ${structured.reference_situation}`,
      structured.frequent_errors && `Erreurs fréquentes : ${structured.frequent_errors}`,
      structured.success_indicators && `Indices de réussite : ${structured.success_indicators}`,
      structured.recommended_usage && `Usages recommandés : ${structured.recommended_usage}`,
      '',
      'Explication structurée :',
      draft.draft_body,
    ].filter((line) => line !== false && String(line).trim()).join('\n')

    return {
      content: sections,
      content_type: 'pedagogical_explication',
      source_type: 'chat_import',
      status: 'derived_provisional',
      referential_item_id: referentialItemId,
      provenance_note: `Créé depuis chat — à relire (session ${draft.session_id})`,
      meta: {
        ...importMeta(draft, { groupId }),
        explication: { ...structured },
      },
    }
  }

  return {
    content: draft.draft_body,
    content_type: 'mastery_criterion',
    source_type: 'chat_import',
    status: 'derived_provisional',
    referential_item_id: referentialItemId,
    provenance_note: `Créé depuis chat — à relire (session ${draft.session_id})`,
    meta: importMeta(draft, { groupId }),
  }
}

export function buildRationalePatchPayload(draft, { groupId = '' } = {}) {
  const structured = draft.structured || {}
  const normalizedGroupId = String(groupId || draft.group_id || '').trim()
  const decisionRationale = {
    ...structured,
    draft_body: draft.draft_body,
    draft_title: draft.draft_title,
    import_kind: draft.import_kind,
    session_id: draft.session_id,
    source_message_ids: draft.source_message_ids,
    source: 'chat',
    status: 'draft',
    human_validation_required: true,
    institutional_decision: false,
  }
  if (normalizedGroupId) {
    decisionRationale.group_id = normalizedGroupId
  }
  return {
    provenance_note: `Justification d'arbitrage importée depuis chat (session ${draft.session_id}) — brouillon, pas décision institutionnelle.`,
    meta: {
      decision_rationale: decisionRationale,
    },
  }
}
