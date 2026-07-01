/** sessionProfileResolution.spec — résolution profils workspace tuteur. */
import test from 'node:test'
import assert from 'node:assert/strict'

import {
  TUTOR_WORKSPACE_PROFILE_CODES,
  findProfileIdByCode,
  isTutorWorkspaceProfileName,
  normalizeConversationProfilesResponse,
} from './tutorWorkspaceProfiles.js'

const FIXTURE_PROFILES = [
  { id: 'p1', name: 'tutor_workspace_prep', status: 'active' },
  { id: 'p2', name: 'tutor_workspace_journal', status: 'active' },
  { id: 'p3', name: 'legacy_learner_profile', status: 'active' },
]

test('findProfileIdByCode resolves workspace prep', () => {
  assert.equal(
    findProfileIdByCode(FIXTURE_PROFILES, TUTOR_WORKSPACE_PROFILE_CODES.PREP),
    'p1',
  )
})

test('isTutorWorkspaceProfileName excludes learner profiles', () => {
  assert.equal(isTutorWorkspaceProfileName('tutor_workspace_prep'), true)
  assert.equal(isTutorWorkspaceProfileName('legacy_learner_profile'), false)
})

test('normalizeConversationProfilesResponse handles array and paginated', () => {
  assert.equal(normalizeConversationProfilesResponse(FIXTURE_PROFILES).length, 3)
  assert.equal(normalizeConversationProfilesResponse({ results: FIXTURE_PROFILES }).length, 3)
})

test('TUTOR profile list filter keeps only workspace codes', () => {
  const filtered = FIXTURE_PROFILES.filter((p) => isTutorWorkspaceProfileName(p.name))
  assert.equal(filtered.length, 2)
})
