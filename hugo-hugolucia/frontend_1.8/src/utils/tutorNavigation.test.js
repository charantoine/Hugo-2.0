import test from 'node:test'
import assert from 'node:assert/strict'

import { TUTOR_REFLECTION_LABEL, TUTOR_REFLECTION_PATH } from './tutorNavigation.js'

test('tutor reflection navigation constants', () => {
  assert.equal(TUTOR_REFLECTION_PATH, '/app')
  assert.equal(TUTOR_REFLECTION_LABEL, 'Mon espace de réflexion')
})
