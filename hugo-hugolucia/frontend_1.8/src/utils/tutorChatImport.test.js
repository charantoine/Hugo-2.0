import test from 'node:test'
import assert from 'node:assert/strict'

import {
  TUTOR_IMPORT_KINDS,
  buildTutorArtifactMeta,
  buildTutorChatImportDraft,
} from './tutorChatImport.js'

test('buildTutorChatImportDraft journal shape', () => {
  const draft = buildTutorChatImportDraft(
    { id: 'm1', content: 'Point-clé de séance' },
    'sess-1',
    TUTOR_IMPORT_KINDS.JOURNAL_ENTRY,
    { learnerId: 'l1', groupId: 'g1' },
  )
  assert.equal(draft.import_kind, 'tutor_journal_entry')
  assert.equal(draft.learner_id, 'l1')
})

test('buildTutorArtifactMeta journal payload', () => {
  const draft = buildTutorChatImportDraft(
    { id: 'm1', content: 'Synthèse courte' },
    'sess-1',
    TUTOR_IMPORT_KINDS.JOURNAL_ENTRY,
    { learnerId: 'l1', groupId: 'g1' },
  )
  draft.structured.summary = 'Synthèse courte'
  const artifact = buildTutorArtifactMeta(draft)
  assert.equal(artifact.metaKey, 'tutor_journal_entry')
  assert.equal(artifact.payload.summary, 'Synthèse courte')
  assert.equal(artifact.payload.visibility, 'tutor_private')
})
