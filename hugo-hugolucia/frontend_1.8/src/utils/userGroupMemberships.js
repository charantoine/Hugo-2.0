/**
 * Résout les groupes auxquels un utilisateur est rattaché à partir des listes membres par groupe.
 * Utilise les endpoints existants GET /groups/ + GET /groups/{id}/members/.
 */
export function isUserInMembership(membership, userId) {
  if (!membership || userId == null) return false
  const memberUserId = membership.user?.id ?? membership.user
  return String(memberUserId) === String(userId)
}

export async function resolveUserGroups(userId, groups, fetchMembers) {
  if (!userId || !Array.isArray(groups) || !groups.length) return []

  const memberships = await Promise.all(
    groups.map(async (group) => {
      try {
        const members = await fetchMembers(group.id)
        const list = Array.isArray(members) ? members : (members?.results || [])
        return list.some((member) => isUserInMembership(member, userId)) ? group : null
      } catch {
        return null
      }
    }),
  )

  return memberships.filter(Boolean)
}
