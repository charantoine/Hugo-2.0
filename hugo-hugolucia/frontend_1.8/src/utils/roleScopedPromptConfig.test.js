/** roleScopedPromptConfig.spec — cloisonnement config prompts par rôle. */
import test from 'node:test'
import assert from 'node:assert/strict'

import { TUTOR_WORKSPACE_PROFILE_CODES } from './tutorWorkspaceProfiles.js'
import { TUTOR_IMPORT_KINDS } from './tutorChatImport.js'
import { TRAINER_IMPORT_KINDS } from './trainerChatImport.js'

const WORKSPACE_IMPORT_MAP = {
  tutor_workspace_prep: 'tutor_session_prep',
  tutor_workspace_diagnostic: 'tutor_diagnostic_notes',
  tutor_workspace_coreflex: 'tutor_reflection',
  tutor_workspace_journal: 'tutor_journal_entry',
}

test('tutor workspace profiles map to distinct import kinds', () => {
  const kinds = Object.values(TUTOR_WORKSPACE_PROFILE_CODES).map((code) => WORKSPACE_IMPORT_MAP[code])
  assert.equal(new Set(kinds).size, 4)
  assert.ok(kinds.every((k) => String(k).startsWith('tutor_')))
})

test('trainer import kinds stay separate from tutor kinds', () => {
  const trainerKinds = Object.values(TRAINER_IMPORT_KINDS)
  const tutorKind = WORKSPACE_IMPORT_MAP.tutor_workspace_journal
  assert.ok(trainerKinds.every((k) => String(k).startsWith('trainer_')))
  assert.ok(!trainerKinds.includes(tutorKind))
  assert.equal(tutorKind, TUTOR_IMPORT_KINDS.JOURNAL_ENTRY)
})
