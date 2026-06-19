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
  engagement_ui_enabled: parseBooleanEnv(env.VITE_ENGAGEMENT_UI_ENABLED, true),
  scene_progress_enabled: parseBooleanEnv(env.VITE_SCENE_PROGRESS_ENABLED, true),
  persistent_objects_enabled: parseBooleanEnv(env.VITE_PERSISTENT_OBJECTS_ENABLED, true),
  symbolic_rewards_enabled: parseBooleanEnv(env.VITE_SYMBOLIC_REWARDS_ENABLED, true),
  gamification_profile: normalizeGamificationProfile(env.VITE_GAMIFICATION_PROFILE),
})

export function getDefaultAuthenticatedPath() {
  return frontendFeatures.frontend_mode === 'tester' ? '/dashboard' : '/app'
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
