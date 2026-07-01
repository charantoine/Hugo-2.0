import { isOrgAdminLike, normalizedRole } from './roleGuards.js'

/** Formateur pur (hors org admin testeur) — cible du réalignement P1. */
export function isPureTrainerPersona(user) {
  if (!user) return false
  return normalizedRole(user) === 'TRAINER' && !isOrgAdminLike(user)
}

export function resolveTrainerChatNavLabel(user) {
  return isPureTrainerPersona(user) ? 'Mon chat' : 'Chat apprenant'
}

export function resolveProdBrandSubtitle(user, routePath = '') {
  const path = String(routePath || '')
  if (isPureTrainerPersona(user) && path.startsWith('/app') && !path.startsWith('/app/trainer')) {
    return 'Espace conversationnel formateur'
  }
  return 'Parcours apprenant'
}

export function resolveTrainerHomeSessionCta(user) {
  return isPureTrainerPersona(user) ? 'Démarrer mon échange' : 'Démarrer ma session'
}
