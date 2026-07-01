import { isOrgAdminLike, normalizedRole } from './roleGuards.js'
import { isTutorWorkspaceProfileName } from './tutorWorkspaceProfiles.js'

/** Tuteur pur (hors org admin / formateur) — cible réalignement P1 tuteur. */
export function isPureTutorPersona(user) {
  if (!user) return false
  const role = normalizedRole(user)
  return role === 'TUTOR' && !isOrgAdminLike(user)
}

export function resolveChatNavLabel(user) {
  if (isPureTutorPersona(user)) return 'Mon espace de réflexion'
  if (normalizedRole(user) === 'TRAINER' && !isOrgAdminLike(user)) return 'Mon chat'
  return 'Chat apprenant'
}

export function resolveProdBrandSubtitle(user, routePath = '') {
  const path = String(routePath || '')
  if (isPureTutorPersona(user) && path.startsWith('/app') && !path.startsWith('/app/tutor')) {
    return 'Espace de réflexion tuteur'
  }
  if (normalizedRole(user) === 'TRAINER' && !isOrgAdminLike(user) && path.startsWith('/app') && !path.startsWith('/app/trainer')) {
    return 'Espace conversationnel formateur'
  }
  return 'Parcours apprenant'
}

export function resolveTutorHomeSessionCta(user) {
  return isPureTutorPersona(user) ? 'Ouvrir mon espace de réflexion' : null
}

export function resolveWorkspaceSessionTitle(session) {
  const name = session?.learner_conversation_profile?.name
  return resolveWorkspaceTitleFromProfileCode(name)
}

export function resolveWorkspaceTitleFromProfileCode(profileCode) {
  const name = String(profileCode || '').trim()
  if (!isTutorWorkspaceProfileName(name)) return null
  if (name === 'tutor_workspace_prep') return 'Préparation d\'entretien'
  if (name === 'tutor_workspace_diagnostic') return 'Aide au diagnostic'
  if (name === 'tutor_workspace_coreflex') return 'Co-réflexion assistée'
  if (name === 'tutor_workspace_journal') return 'Journal tutorat'
  return null
}
