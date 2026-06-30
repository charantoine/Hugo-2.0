import { isOrgAdminLike, normalizedRole } from './roleGuards.js'

const env = import.meta.env || {}

function parseBooleanEnv(value, fallback) {
  if (value === undefined || value === null || value === '') return fallback
  const normalized = String(value).trim().toLowerCase()
  if (['1', 'true', 'yes', 'on'].includes(normalized)) return true
  if (['0', 'false', 'no', 'off'].includes(normalized)) return false
  return fallback
}

function normalizeFrontendMode(value) {
  return String(value || '').trim() === 'tester' ? 'tester' : 'prod_showable'
}

function normalizeGamificationProfile(value) {
  const normalized = String(value || '').trim().toUpperCase()
  return ['A', 'B', 'C'].includes(normalized) ? normalized : 'B'
}

export const frontendFeatures = Object.freeze({
  frontend_mode: normalizeFrontendMode(env.VITE_FRONTEND_MODE),
  /** Interface apprenant simplifiée 2.0 (bêta testeurs externes). */
  learner_ui_v2: parseBooleanEnv(env.VITE_LEARNER_UI_V2, true),
  engagement_ui_enabled: parseBooleanEnv(env.VITE_ENGAGEMENT_UI_ENABLED, true),
  scene_progress_enabled: parseBooleanEnv(env.VITE_SCENE_PROGRESS_ENABLED, true),
  persistent_objects_enabled: parseBooleanEnv(env.VITE_PERSISTENT_OBJECTS_ENABLED, true),
  symbolic_rewards_enabled: parseBooleanEnv(env.VITE_SYMBOLIC_REWARDS_ENABLED, true),
  p0_debug_enabled: parseBooleanEnv(env.VITE_P0_DEBUG_ENABLED, false),
  gamification_profile: normalizeGamificationProfile(env.VITE_GAMIFICATION_PROFILE),
})

export function getDefaultAuthenticatedPath() {
  return frontendFeatures.frontend_mode === 'tester' ? '/dashboard' : '/app'
}

/** Home route after login — role-aware; org admins keep tester dashboard in tester mode. */
export function resolveAuthenticatedHome(user) {
  if (!user) return getDefaultAuthenticatedPath()
  const role = normalizedRole(user)
  if (role === 'TRAINER' && !isOrgAdminLike(user)) {
    return '/app/trainer/knowledge'
  }
  if (['TUTOR', 'COORDO'].includes(role) && !isOrgAdminLike(user)) {
    return frontendFeatures.frontend_mode === 'tester' ? '/dashboard' : '/app/tutor'
  }
  if (role === 'LEARNER') {
    return '/app'
  }
  return getDefaultAuthenticatedPath()
}

export function getGamificationProfileTheme(profile = frontendFeatures.gamification_profile) {
  const normalized = normalizeGamificationProfile(profile)
  if (normalized === 'A') {
    return {
      code: 'A',
      label: 'Profil A',
      title: 'Ludique assumé',
      subtitle: 'Plus de relief visuel et de petits retours positifs.',
    }
  }
  if (normalized === 'C') {
    return {
      code: 'C',
      label: 'Profil C',
      title: 'Sobre pro',
      subtitle: "Une expérience plus discrète, toujours claire et engageante.",
    }
  }
  return {
    code: 'B',
    label: 'Profil B',
    title: 'Intermédiaire',
    subtitle: 'Un bon équilibre entre chaleur visuelle et sobriété.',
  }
}
