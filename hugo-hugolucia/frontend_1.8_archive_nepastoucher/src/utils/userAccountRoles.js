/** Roles créables depuis UsersView (administration IAM). */
export const CREATABLE_ACCOUNT_ROLES = [
  { value: 'LEARNER', label: 'Apprenant' },
  { value: 'TUTOR', label: 'Tuteur' },
  { value: 'TRAINER', label: 'Formateur' },
]

const CREATE_BUTTON_LABELS = {
  LEARNER: 'Créer l’apprenant',
  TUTOR: 'Créer le tuteur',
  TRAINER: 'Créer le formateur',
}

const CREATE_SUCCESS_MESSAGES = {
  LEARNER: 'Compte apprenant créé.',
  TUTOR: 'Compte tuteur créé.',
  TRAINER: 'Compte formateur créé.',
}

export function getCreateButtonLabel(role) {
  return CREATE_BUTTON_LABELS[role] || CREATE_BUTTON_LABELS.LEARNER
}

export function getCreateSuccessMessage(role) {
  return CREATE_SUCCESS_MESSAGES[role] || CREATE_SUCCESS_MESSAGES.LEARNER
}

/** Filtre liste utilisateurs par rôle (chaîne vide = tous). */
export function filterUsersByRole(users, roleFilter) {
  if (!roleFilter) return users
  return users.filter((u) => u.role === roleFilter)
}
