/** roleAwareTopbarLabels.spec — labels topbar par rôle (baseline B). */
import test from 'node:test'
import assert from 'node:assert/strict'

import { resolveChatNavLabel as resolveTutorNav } from './tutorUiLabels.js'
import { resolveTrainerChatNavLabel } from './trainerUiLabels.js'

test('TUTOR pure → Mon espace de réflexion', () => {
  assert.equal(resolveTutorNav({ role: 'TUTOR' }), 'Mon espace de réflexion')
})

test('TRAINER pure → Mon chat', () => {
  assert.equal(resolveTrainerChatNavLabel({ role: 'TRAINER' }), 'Mon chat')
})

test('ORGADMIN → Chat apprenant (pas de label tuteur/formateur pur)', () => {
  assert.equal(resolveTutorNav({ role: 'ORGADMIN' }), 'Chat apprenant')
  assert.equal(resolveTrainerChatNavLabel({ role: 'ORGADMIN' }), 'Chat apprenant')
})
