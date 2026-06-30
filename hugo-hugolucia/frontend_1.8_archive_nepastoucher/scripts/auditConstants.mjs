/** Constantes partagées — scripts d’audit UI (alignées sur demoReferenceGroup.js). */
export const REFERENCE_GROUP_NAME = 'bac pro melec'
export const REFERENCE_GROUP_ID =
  process.env.AUDIT_GROUP_ID || '29e5cdb9-de89-49b3-a36e-53b4b9bbbc50'

export function canonicalTesterPath(groupId = REFERENCE_GROUP_ID) {
  return `/group/${groupId}`
}

/** Sélecteur Playwright — bouton mode testeur canonique sur /dashboard. */
export const DASHBOARD_TESTER_CANONICAL_TEST_ID = 'dashboard-tester-canonical'
