/** Helpers for trainer group / cohort context (pure, testable). */

export function pickDefaultGroupId(groups, queryGroupId) {
  const list = Array.isArray(groups) ? groups : []
  const fromQuery = String(queryGroupId || '').trim()
  if (fromQuery && list.some((group) => String(group.id) === fromQuery)) {
    return fromQuery
  }
  if (list.length === 1) {
    return String(list[0].id)
  }
  return fromQuery || ''
}

export function summarizeReferentialConfig(config) {
  const referential = config?.referential
  if (!referential) return null
  return {
    id: referential.id,
    name: referential.name || '',
    sourceRef: referential.source_ref || '',
    label: referential.source_ref
      ? `${referential.name || referential.source_ref} (${referential.source_ref})`
      : (referential.name || ''),
  }
}

export function summarizeMemberships(members) {
  const list = Array.isArray(members) ? members : []
  return {
    count: list.length,
    userIds: list.map((member) => String(member.user?.id ?? member.user ?? '')).filter(Boolean),
    roster: list.map((member) => ({
      username: member.user_username || '',
      role: member.user_role || '',
    })).filter((row) => row.username),
  }
}

export function formatMembershipPreview(userIds, maxItems = 3) {
  const ids = Array.isArray(userIds) ? userIds : []
  if (!ids.length) return ''
  const shortIds = ids.slice(0, maxItems).map((id) => String(id).slice(0, 8))
  const suffix = ids.length > maxItems ? ` +${ids.length - maxItems}` : ''
  return `${shortIds.join(', ')}${suffix}`
}
