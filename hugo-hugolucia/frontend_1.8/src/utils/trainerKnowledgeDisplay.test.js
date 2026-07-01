import test from 'node:test'
import assert from 'node:assert/strict'

import { summarizeDecisionRationale } from './trainerKnowledgeDisplay.js'

test('summarizeDecisionRationale returns null when absent', () => {
  assert.equal(summarizeDecisionRationale({ meta: {} }), null)
  assert.equal(summarizeDecisionRationale(null), null)
})

test('summarizeDecisionRationale extracts draft fields', () => {
  const summary = summarizeDecisionRationale({
    meta: {
      decision_rationale: {
        envisioned_decision: 'Laisser provisoire',
        reasons: 'Relecture collective',
        status: 'draft',
      },
    },
  })
  assert.equal(summary.envisionedDecision, 'Laisser provisoire')
  assert.equal(summary.reasons, 'Relecture collective')
  assert.equal(summary.isDraft, true)
})
