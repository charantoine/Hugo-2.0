/** TrainerWorkspaceProfileSelector.spec — formateur voit profils apprenant, pas workspace tuteur. */
import test from 'node:test'
import assert from 'node:assert/strict'

import { isTutorWorkspaceProfileName } from './tutorWorkspaceProfiles.js'

function filterProfilesForTrainer(profiles) {
  return (profiles || []).filter(
    (p) => String(p?.status || '').toLowerCase() === 'active'
      && !isTutorWorkspaceProfileName(p?.name),
  )
}

test('trainer active profiles exclude tutor workspace codes', () => {
  const profiles = [
    { name: 'tutor_workspace_prep', status: 'active' },
    { name: 'bac_pro_default', status: 'active' },
    { name: 'tutor_workspace_journal', status: 'active' },
  ]
  const filtered = filterProfilesForTrainer(profiles)
  assert.equal(filtered.length, 1)
  assert.equal(filtered[0].name, 'bac_pro_default')
})
