/** Role helpers aligned with backend access_control (domain 90). */

export function normalizedRole(user) {
  return String(user?.role || user?.user_role || '').toUpperCase()
}

export function isOrgAdminLike(user) {
  if (!user) return false
  const role = normalizedRole(user)
  return (
    Boolean(user.is_superuser || user.is_staff) ||
    role === 'ORGADMIN' ||
    role === 'SUPERADMIN' ||
    role === 'ADMIN'
  )
}

export function isTrainerLike(user) {
  if (!user) return false
  const role = normalizedRole(user)
  return isOrgAdminLike(user) || role === 'TRAINER'
}

export function isTutorLike(user) {
  if (!user) return false
  const role = normalizedRole(user)
  return isOrgAdminLike(user) || ['TUTOR', 'TRAINER', 'COORDO'].includes(role)
}

export function isEncadrantLike(user) {
  if (!user) return false
  const role = normalizedRole(user)
  return isOrgAdminLike(user) || ['TUTOR', 'TRAINER', 'COORDO'].includes(role)
}

export function isLearnerOnly(user) {
  if (!user) return false
  return normalizedRole(user) === 'LEARNER'
}
