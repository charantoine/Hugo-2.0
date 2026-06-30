import test from 'node:test'
import assert from 'node:assert/strict'

import {
  CREATABLE_ACCOUNT_ROLES,
  filterUsersByRole,
  getCreateButtonLabel,
  getCreateSuccessMessage,
} from './userAccountRoles.js'

test('CREATABLE_ACCOUNT_ROLES includes learner, tutor and trainer', () => {
  const values = CREATABLE_ACCOUNT_ROLES.map((r) => r.value)
  assert.deepEqual(values, ['LEARNER', 'TUTOR', 'TRAINER'])
  const labels = CREATABLE_ACCOUNT_ROLES.map((r) => r.label)
  assert.deepEqual(labels, ['Apprenant', 'Tuteur', 'Formateur'])
})

test('getCreateButtonLabel returns role-specific submit label', () => {
  assert.equal(getCreateButtonLabel('LEARNER'), 'Créer l’apprenant')
  assert.equal(getCreateButtonLabel('TUTOR'), 'Créer le tuteur')
  assert.equal(getCreateButtonLabel('TRAINER'), 'Créer le formateur')
})

test('getCreateSuccessMessage returns role-specific success message', () => {
  assert.equal(getCreateSuccessMessage('LEARNER'), 'Compte apprenant créé.')
  assert.equal(getCreateSuccessMessage('TUTOR'), 'Compte tuteur créé.')
  assert.equal(getCreateSuccessMessage('TRAINER'), 'Compte formateur créé.')
})

test('filterUsersByRole filters by role or returns all', () => {
  const users = [
    { id: '1', role: 'LEARNER' },
    { id: '2', role: 'TRAINER' },
    { id: '3', role: 'TUTOR' },
  ]
  assert.equal(filterUsersByRole(users, '').length, 3)
  assert.equal(filterUsersByRole(users, 'TRAINER').length, 1)
  assert.equal(filterUsersByRole(users, 'TRAINER')[0].id, '2')
})
