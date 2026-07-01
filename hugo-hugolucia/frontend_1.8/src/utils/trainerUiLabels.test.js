import test from 'node:test'
import assert from 'node:assert/strict'

import {
  isPureTrainerPersona,
  resolveProdBrandSubtitle,
  resolveTrainerChatNavLabel,
  resolveTrainerHomeSessionCta,
} from './trainerUiLabels.js'

test('pure TRAINER gets Mon chat label', () => {
  const user = { role: 'TRAINER' }
  assert.equal(isPureTrainerPersona(user), true)
  assert.equal(resolveTrainerChatNavLabel(user), 'Mon chat')
  assert.equal(resolveProdBrandSubtitle(user, '/app/session/abc'), 'Espace conversationnel formateur')
  assert.equal(resolveTrainerHomeSessionCta(user), 'Démarrer mon échange')
})

test('ORGADMIN keeps Chat apprenant label', () => {
  const user = { role: 'ORGADMIN' }
  assert.equal(isPureTrainerPersona(user), false)
  assert.equal(resolveTrainerChatNavLabel(user), 'Chat apprenant')
})

test('LEARNER keeps learner labels', () => {
  const user = { role: 'LEARNER' }
  assert.equal(resolveTrainerChatNavLabel(user), 'Chat apprenant')
  assert.equal(resolveProdBrandSubtitle(user, '/app'), 'Parcours apprenant')
})
