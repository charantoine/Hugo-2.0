/** Codes profils globaux espace tuteur P1 (noms = codes backend). */
export const TUTOR_WORKSPACE_PROFILE_CODES = Object.freeze({
  PREP: 'tutor_workspace_prep',
  DIAGNOSTIC: 'tutor_workspace_diagnostic',
  COREFLEX: 'tutor_workspace_coreflex',
  JOURNAL: 'tutor_workspace_journal',
})

export const TUTOR_WORKSPACE_PRIMARY_POSTURE = Object.freeze({
  [TUTOR_WORKSPACE_PROFILE_CODES.PREP]: 'reflective_afest',
  [TUTOR_WORKSPACE_PROFILE_CODES.DIAGNOSTIC]: 'diagnostic',
  [TUTOR_WORKSPACE_PROFILE_CODES.COREFLEX]: 'reflective_afest',
  [TUTOR_WORKSPACE_PROFILE_CODES.JOURNAL]: 'knowledge_review',
})

export const TUTOR_WORKSPACE_CTA_LABELS = Object.freeze({
  [TUTOR_WORKSPACE_PROFILE_CODES.PREP]: 'Préparer mon entretien',
  [TUTOR_WORKSPACE_PROFILE_CODES.DIAGNOSTIC]: 'Aide au diagnostic',
  [TUTOR_WORKSPACE_PROFILE_CODES.COREFLEX]: 'Préparer des questions',
  [TUTOR_WORKSPACE_PROFILE_CODES.JOURNAL]: 'Noter un point-clé',
})

export function isTutorWorkspaceProfileName(name) {
  return Object.values(TUTOR_WORKSPACE_PROFILE_CODES).includes(String(name || '').trim())
}

export function findProfileIdByCode(profiles, code) {
  const match = (profiles || []).find((p) => String(p?.name || '').trim() === String(code).trim())
  return match?.id ? String(match.id) : ''
}

export function normalizeConversationProfilesResponse(data) {
  if (Array.isArray(data)) return data
  if (data && Array.isArray(data.results)) return data.results
  return []
}
