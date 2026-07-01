import assert from 'node:assert/strict'
import test from 'node:test'
import { resolveWorkspaceMode, WORKSPACE_MODES } from './chatWorkspaceMode.js'

test('resolveWorkspaceMode returns tutor for dedicated tutor chat route', () => {
  const mode = resolveWorkspaceMode(
    { path: '/app/tutor/chat/abc', name: 'ProdTutorChatSession', query: {} },
    { role: 'TUTOR' },
  )
  assert.equal(mode, WORKSPACE_MODES.TUTOR)
})

test('resolveWorkspaceMode returns trainer for dedicated trainer chat route', () => {
  const mode = resolveWorkspaceMode(
    { path: '/app/trainer/chat/xyz', name: 'ProdTrainerChatSession', query: {} },
    { role: 'TRAINER' },
  )
  assert.equal(mode, WORKSPACE_MODES.TRAINER)
})

test('resolveWorkspaceMode returns learner for learner session route', () => {
  const mode = resolveWorkspaceMode(
    { path: '/app/session/s1', name: 'ProdLearnerSession', query: {} },
    { role: 'LEARNER' },
  )
  assert.equal(mode, WORKSPACE_MODES.LEARNER)
})

test('resolveWorkspaceMode legacy tutor_ctx maps to tutor for pure tutor', () => {
  const mode = resolveWorkspaceMode(
    { path: '/app/session/s1', name: 'ProdLearnerSession', query: { tutor_ctx: '1' } },
    { role: 'TUTOR', roles: ['TUTOR'] },
  )
  assert.equal(mode, WORKSPACE_MODES.TUTOR)
})

test('resolveWorkspaceMode legacy learner session maps to trainer for pure trainer', () => {
  const mode = resolveWorkspaceMode(
    { path: '/app/session/s1', name: 'ProdLearnerSession', query: {} },
    { role: 'TRAINER', roles: ['TRAINER'] },
  )
  assert.equal(mode, WORKSPACE_MODES.TRAINER)
})
