import test from 'node:test'
import assert from 'node:assert/strict'

import {
  isEncadrantLike,
  isLearnerOnly,
  isOrgAdminLike,
  isSuperAdmin,
  isTrainerLike,
  isTutorLike,
} from './roleGuards.js'

test('isOrgAdminLike matches ORGADMIN and SUPERADMIN only', () => {
  assert.equal(isOrgAdminLike({ role: 'ORGADMIN' }), true)
  assert.equal(isOrgAdminLike({ role: 'SUPERADMIN' }), true)
  assert.equal(isOrgAdminLike({ role: 'TRAINER' }), false)
  assert.equal(isOrgAdminLike({ role: 'TUTOR' }), false)
  assert.equal(isOrgAdminLike({ is_superuser: true, role: 'TRAINER' }), false)
})

test('isSuperAdmin matches SUPERADMIN role only', () => {
  assert.equal(isSuperAdmin({ role: 'SUPERADMIN' }), true)
  assert.equal(isSuperAdmin({ role: 'ORGADMIN' }), false)
  assert.equal(isSuperAdmin({ is_superuser: true, role: 'ORGADMIN' }), false)
})

test('isTrainerLike includes TRAINER and org admins', () => {
  assert.equal(isTrainerLike({ role: 'TRAINER' }), true)
  assert.equal(isTrainerLike({ role: 'ORGADMIN' }), true)
  assert.equal(isTrainerLike({ role: 'TUTOR' }), false)
})

test('isTutorLike includes tutor roles and org admins', () => {
  assert.equal(isTutorLike({ role: 'TUTOR' }), true)
  assert.equal(isTutorLike({ role: 'COORDO' }), true)
  assert.equal(isTutorLike({ role: 'LEARNER' }), false)
})

test('export affordance roles: only org admins', () => {
  assert.equal(isOrgAdminLike({ role: 'TUTOR' }), false)
  assert.equal(isOrgAdminLike({ role: 'TRAINER' }), false)
})

test('isEncadrantLike excludes pure learners', () => {
  assert.equal(isEncadrantLike({ role: 'LEARNER' }), false)
  assert.equal(isLearnerOnly({ role: 'LEARNER' }), true)
})
