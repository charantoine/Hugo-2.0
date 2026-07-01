import test from 'node:test'
import assert from 'node:assert/strict'

import { formatTutorArtifactList } from './tutorKnowledgeDisplay.js'

test('formatTutorArtifactList renders summaries', () => {
  const rows = formatTutorArtifactList([
    {
      id: '1',
      metaKey: 'tutor_journal_entry',
      payload: { summary: 'Point noté', status: 'draft' },
    },
  ])
  assert.equal(rows.length, 1)
  assert.equal(rows[0].summary.title, 'Point-clé')
})
