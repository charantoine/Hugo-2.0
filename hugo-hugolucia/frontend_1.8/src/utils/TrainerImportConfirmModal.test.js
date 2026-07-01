/** TrainerImportConfirmModal.spec — structures import formateur. */
import test from 'node:test'
import assert from 'node:assert/strict'

import {
  TRAINER_IMPORT_KINDS,
  buildChatImportDraft,
  buildCreatePayloadFromDraft,
} from './trainerChatImport.js'

test('buildChatImportDraft explication shape', () => {
  const draft = buildChatImportDraft(
    { id: 'm1', content: 'Explication proposée' },
    'sess-trainer',
    TRAINER_IMPORT_KINDS.EXPLICATION,
  )
  assert.equal(draft.import_kind, TRAINER_IMPORT_KINDS.EXPLICATION)
  assert.ok(draft.structured)
})

test('buildCreatePayloadFromDraft matches backend contract fields', () => {
  const draft = buildChatImportDraft(
    { id: 'm1', content: 'Ressource' },
    'sess-trainer',
    TRAINER_IMPORT_KINDS.RESOURCE_PROVISIONAL,
  )
  const payload = buildCreatePayloadFromDraft(draft)
  assert.equal(payload.source_type, 'chat_import')
  assert.equal(payload.meta.import_kind, TRAINER_IMPORT_KINDS.RESOURCE_PROVISIONAL)
  assert.equal(payload.meta.session_id, 'sess-trainer')
})
