// Presentation-only presets for learner_display_profile (DSP-04: same UIState, different render).

export const DISPLAY_PROFILE_VALUES = ['youth', 'adult', 'professional']

export const DISPLAY_PROFILE_LABELS = {
  youth: 'Jeune',
  adult: 'Adulte',
  professional: 'Standard',
}

const YOUTH_STEP_HINTS = {
  Raconter: 'Décrivez ce qui s’est passé.',
  Explorer: 'Repérez ce qui bloque.',
  Synthétiser: 'Faites le point sur ce qui est clair.',
}

const ADULT_STEP_HINTS = {
  Raconter: 'Décrivez la situation de départ.',
  Explorer: 'Identifiez ce qui freine ou ce qui manque.',
  Synthétiser: 'Reformulez ce qui est déjà clair.',
}

export const DISPLAY_PROFILE_PRESETS = {
  youth: {
    compactCopy: true,
    showProgressBar: true,
    showQuestLabel: true,
    showMaturityBadge: true,
    showStepIcons: true,
    progressPanelIntro: 'Où vous en êtes dans votre scène.',
    stepHints: YOUTH_STEP_HINTS,
  },
  adult: {
    compactCopy: false,
    showProgressBar: true,
    showQuestLabel: true,
    showMaturityBadge: true,
    showStepIcons: true,
    progressPanelIntro: 'Avancement de la scène tel que renvoyé par Hugo.',
    stepHints: ADULT_STEP_HINTS,
  },
  professional: {
    compactCopy: false,
    showProgressBar: true,
    showQuestLabel: true,
    showMaturityBadge: true,
    showStepIcons: false,
    progressPanelIntro: 'Ce panneau reflète uniquement l’état produit renvoyé par Hugo.',
    stepHints: {},
  },
}

export function normalizeDisplayProfile(value) {
  const normalized = String(value || 'professional').trim().toLowerCase()
  return DISPLAY_PROFILE_VALUES.includes(normalized) ? normalized : 'professional'
}

export function getDisplayProfilePreset(profile) {
  return DISPLAY_PROFILE_PRESETS[normalizeDisplayProfile(profile)] || DISPLAY_PROFILE_PRESETS.professional
}
