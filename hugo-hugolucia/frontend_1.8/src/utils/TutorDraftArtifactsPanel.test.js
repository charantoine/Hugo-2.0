/** TutorDraftArtifactsPanel.spec — affichage brouillons session courante. */
import test from 'node:test'
import assert from 'node:assert/strict'

import { formatTutorArtifactList } from './tutorKnowledgeDisplay.js'

test('formatTutorArtifactList renders draft badges', () => {
  const rows = formatTutorArtifactList([
    {
      id: 'a1',
      metaKey: 'tutor_journal_entry',
      payload: {
        summary: 'Point-clé test',
        status: 'draft',
        group_id: 'g1',
        learner_id: 'l1',
      },
    },
  ])
  assert.equal(rows.length, 1)
  assert.equal(rows[0].summary.title, 'Point-clé')
  assert.equal(rows[0].summary.line, 'Point-clé test')
  assert.equal(rows[0].summary.badge, 'brouillon')
})

test('empty artifacts → empty list', () => {
  assert.deepEqual(formatTutorArtifactList([]), [])
})
