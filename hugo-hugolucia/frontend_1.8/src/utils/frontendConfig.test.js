import test from 'node:test'
import assert from 'node:assert/strict'

import { getDefaultAuthenticatedPath, resolveAuthenticatedHome } from './frontendConfig.js'

test('resolveAuthenticatedHome sends pure TRAINER to orchestrateur connaissance', () => {
  assert.equal(
    resolveAuthenticatedHome({ role: 'TRAINER' }),
    '/app/trainer/knowledge',
  )
})

test('resolveAuthenticatedHome keeps ORGADMIN on default authenticated path', () => {
  assert.equal(
    resolveAuthenticatedHome({ role: 'ORGADMIN' }),
    getDefaultAuthenticatedPath(),
  )
})

test('resolveAuthenticatedHome sends LEARNER to /app', () => {
  assert.equal(resolveAuthenticatedHome({ role: 'LEARNER' }), '/app')
})
