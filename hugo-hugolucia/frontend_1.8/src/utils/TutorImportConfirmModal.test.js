/** TutorImportConfirmModal.spec — logique confirmation brouillon (sans write backend). */
import test from 'node:test'
import assert from 'node:assert/strict'

import {
  TUTOR_IMPORT_KINDS,
  buildTutorArtifactMeta,
  buildTutorChatImportDraft,
} from './tutorChatImport.js'

test('buildTutorArtifactMeta produces draft journal payload', () => {
  const draft = buildTutorChatImportDraft(
    { id: 'm1', content: 'Point observé' },
    'sess-1',
    TUTOR_IMPORT_KINDS.JOURNAL_ENTRY,
    { learnerId: 'l1', groupId: 'g1' },
  )
  draft.structured.summary = 'Synthèse confirmée'
  const artifact = buildTutorArtifactMeta(draft)
  assert.equal(artifact.metaKey, 'tutor_journal_entry')
  assert.equal(artifact.payload.status, 'draft')
  assert.equal(artifact.payload.visibility, 'tutor_private')
  assert.equal(artifact.payload.summary, 'Synthèse confirmée')
})

test('invalid draft returns null artifact (modal would block)', () => {
  assert.equal(buildTutorArtifactMeta({ import_kind: 'unknown' }), null)
})
