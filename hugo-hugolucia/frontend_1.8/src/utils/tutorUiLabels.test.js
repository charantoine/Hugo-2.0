import test from 'node:test'
import assert from 'node:assert/strict'

import {
  isPureTutorPersona,
  resolveChatNavLabel,
  resolveProdBrandSubtitle,
} from './tutorUiLabels.js'

test('pure TUTOR gets Mon espace de réflexion label', () => {
  assert.equal(resolveChatNavLabel({ role: 'TUTOR' }), 'Mon espace de réflexion')
})

test('TRAINER keeps Mon chat via trainerUiLabels path', () => {
  assert.equal(resolveChatNavLabel({ role: 'TRAINER' }), 'Mon chat')
})

test('isPureTutorPersona excludes org admin', () => {
  assert.equal(isPureTutorPersona({ role: 'TUTOR' }), true)
  assert.equal(isPureTutorPersona({ role: 'ORGADMIN' }), false)
})

test('tutor brand subtitle on /app', () => {
  assert.equal(
    resolveProdBrandSubtitle({ role: 'TUTOR' }, '/app/session/x'),
    'Espace de réflexion tuteur',
  )
})
