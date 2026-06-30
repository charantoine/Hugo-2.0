import test from 'node:test'
import assert from 'node:assert/strict'

import { isUserInMembership, resolveUserGroups } from './userGroupMemberships.js'

test('isUserInMembership matches UUID string on membership.user', () => {
  assert.equal(isUserInMembership({ user: 'abc-123' }, 'abc-123'), true)
})

test('isUserInMembership matches nested user object', () => {
  assert.equal(isUserInMembership({ user: { id: 'abc-123' } }, 'abc-123'), true)
})

test('resolveUserGroups returns groups where user appears in members list', async () => {
  const groups = [
    { id: 'g1', name: 'Groupe A' },
    { id: 'g2', name: 'Groupe B' },
  ]
  const fetchMembers = async (groupId) => {
    if (groupId === 'g1') return [{ user: 'user-1' }]
    return [{ user: 'other' }]
  }

  const result = await resolveUserGroups('user-1', groups, fetchMembers)
  assert.deepEqual(result, [{ id: 'g1', name: 'Groupe A' }])
})

test('resolveUserGroups returns empty list when groups is empty', async () => {
  const result = await resolveUserGroups('user-1', [], async () => [])
  assert.deepEqual(result, [])
})
