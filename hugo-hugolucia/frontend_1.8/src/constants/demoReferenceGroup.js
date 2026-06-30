/** Groupe de démonstration / référence pour onboarding, dashboard testeur et audits runtime. */
export const REFERENCE_GROUP_NAME = 'bac pro melec'

/** ID connu en démo locale (override via AUDIT_GROUP_ID en scripts). */
export const REFERENCE_GROUP_ID = '29e5cdb9-de89-49b3-a36e-53b4b9bbbc50'

const DEBUG_NAME_PATTERNS = [/^_/i, /_tmp/i, /^tmp_/i, /_ux_audit/i, /debug/i]

/** Groupes créés par scripts d’audit ou tests — hors viewport principal du dashboard. */
export function isDebugGroupName(name) {
  if (!name) return false
  const n = name.trim()
  return DEBUG_NAME_PATTERNS.some((pattern) => pattern.test(n))
}

export function findReferenceGroup(groups) {
  if (!Array.isArray(groups)) return null
  return (
    groups.find((g) => g.name?.trim().toLowerCase() === REFERENCE_GROUP_NAME.toLowerCase()) ?? null
  )
}

/** Route mode testeur (GroupView legacy / calibration encadrant). */
export function canonicalTesterPath(groupId) {
  return groupCalibrationPath(groupId)
}

/** Liste apprenants en premier — calibration encadrant. */
export function groupCalibrationPath(groupId) {
  return `/group/${groupId}?focus=calibration`
}

/** Zone exports Felix-ready / Qualiopi lite mise en avant. */
export function groupExportsPath(groupId) {
  return `/group/${groupId}?focus=exports`
}
