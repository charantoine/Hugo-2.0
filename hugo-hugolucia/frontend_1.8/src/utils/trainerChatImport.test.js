import test from 'node:test'
import assert from 'node:assert/strict'

import {
  TRAINER_IMPORT_KINDS,
  buildChatImportDraft,
  buildCreatePayloadFromDraft,
  buildRationalePatchPayload,
} from './trainerChatImport.js'

const message = {
  id: 'msg-1',
  content: 'Première ligne titre\nCorps détaillé de la réponse.',
}

test('buildChatImportDraft for provisional resource', () => {
  const draft = buildChatImportDraft(message, 'sess-1', TRAINER_IMPORT_KINDS.RESOURCE_PROVISIONAL)
  assert.equal(draft.import_kind, 'trainer_resource_provisional')
  assert.equal(draft.draft_title, 'Première ligne titre')
  assert.deepEqual(draft.source_message_ids, ['msg-1'])
})

test('buildCreatePayloadFromDraft provisional', () => {
  const draft = buildChatImportDraft(message, 'sess-1', TRAINER_IMPORT_KINDS.RESOURCE_PROVISIONAL)
  const payload = buildCreatePayloadFromDraft(draft)
  assert.equal(payload.status, 'derived_provisional')
  assert.equal(payload.source_type, 'chat_import')
  assert.equal(payload.meta.session_id, 'sess-1')
})

test('buildCreatePayloadFromDraft explication', () => {
  const draft = buildChatImportDraft(message, 'sess-2', TRAINER_IMPORT_KINDS.EXPLICATION)
  draft.structured.learning_objective = 'Objectif test'
  const payload = buildCreatePayloadFromDraft(draft, { groupId: 'group-1' })
  assert.equal(payload.content_type, 'pedagogical_explication')
  assert.equal(payload.meta.explication.learning_objective, 'Objectif test')
  assert.equal(payload.meta.source, 'chat')
  assert.equal(payload.meta.group_id, 'group-1')
})

test('buildRationalePatchPayload', () => {
  const draft = buildChatImportDraft(message, 'sess-3', TRAINER_IMPORT_KINDS.DECISION_RATIONALE)
  draft.structured.envisioned_decision = 'Garder provisoire'
  const payload = buildRationalePatchPayload(draft, { groupId: 'grp-1' })
  assert.equal(payload.meta.decision_rationale.envisioned_decision, 'Garder provisoire')
  assert.equal(payload.meta.decision_rationale.status, 'draft')
  assert.equal(payload.meta.decision_rationale.source, 'chat')
  assert.equal(payload.meta.decision_rationale.institutional_decision, false)
  assert.equal(payload.meta.decision_rationale.group_id, 'grp-1')
  assert.match(payload.provenance_note, /brouillon/i)
})
