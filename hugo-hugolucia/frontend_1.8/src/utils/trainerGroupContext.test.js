import test from 'node:test'
import assert from 'node:assert/strict'

import {
  formatMembershipPreview,
  pickDefaultGroupId,
  summarizeMemberships,
  summarizeReferentialConfig,
} from './trainerGroupContext.js'

test('pickDefaultGroupId prefers valid query group', () => {
  const groups = [{ id: 'g1' }, { id: 'g2' }]
  assert.equal(pickDefaultGroupId(groups, 'g2'), 'g2')
})

test('pickDefaultGroupId auto-selects single group', () => {
  assert.equal(pickDefaultGroupId([{ id: 'only' }], ''), 'only')
})

test('summarizeReferentialConfig builds label with source ref', () => {
  const summary = summarizeReferentialConfig({
    referential: { id: 'r1', name: 'BAC PRO', source_ref: 'RNCP38878' },
  })
  assert.equal(summary.label, 'BAC PRO (RNCP38878)')
})

test('summarizeMemberships extracts user ids', () => {
  const summary = summarizeMemberships([
    { user: 'u1' },
    { user: { id: 'u2' } },
  ])
  assert.equal(summary.count, 2)
  assert.deepEqual(summary.userIds, ['u1', 'u2'])
})

test('summarizeMemberships builds roster from serializer fields', () => {
  const summary = summarizeMemberships([
    { user: 'u1', user_username: 'apprenant_test_2', user_role: 'LEARNER' },
    { user: 'u2', user_username: 'tuteur_test_2', user_role: 'TUTOR' },
  ])
  assert.equal(summary.roster.length, 2)
  assert.equal(summary.roster[0].username, 'apprenant_test_2')
})

test('formatMembershipPreview truncates long lists', () => {
  const preview = formatMembershipPreview(['abcdef12-0000', 'bcdef123-0000', 'cdef1234-0000', 'def12345-0000'], 2)
  assert.match(preview, /\+2/)
})
