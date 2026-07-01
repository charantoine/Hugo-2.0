/** TutorWorkspaceProfileSelector.spec — sélection profils workspace tuteur. */
import test from 'node:test'
import assert from 'node:assert/strict'

import {
  TUTOR_WORKSPACE_CTA_LABELS,
  TUTOR_WORKSPACE_PROFILE_CODES,
  findProfileIdByCode,
} from './tutorWorkspaceProfiles.js'

test('four CTA labels map to four workspace codes', () => {
  assert.equal(Object.keys(TUTOR_WORKSPACE_CTA_LABELS).length, 4)
  for (const code of Object.values(TUTOR_WORKSPACE_PROFILE_CODES)) {
    assert.ok(TUTOR_WORKSPACE_CTA_LABELS[code])
  }
})

test('profile selector resolves prep id from API list', () => {
  const profiles = [
    { id: 'uuid-prep', name: 'tutor_workspace_prep' },
    { id: 'uuid-other', name: 'default_learner' },
  ]
  assert.equal(findProfileIdByCode(profiles, 'tutor_workspace_prep'), 'uuid-prep')
})
