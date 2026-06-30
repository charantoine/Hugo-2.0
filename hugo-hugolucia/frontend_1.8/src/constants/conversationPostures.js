/** Canonical learner postures — must match backend ConversationPosture. */
export const LEARNER_POSTURES = [
  {
    code: 'diagnostic',
    label: 'Diagnostic',
    description: 'Explorer la situation et clarifier le contexte avant d’approfondir.',
  },
  {
    code: 'reflective_afest',
    label: 'Réflexif AFEST',
    description: 'Analyser une expérience concrète et en tirer des repères actionnables.',
  },
  {
    code: 'knowledge_review',
    label: 'Savoirs / révision',
    description: 'Consolider des savoirs ou réviser des points déjà abordés.',
  },
]

export function postureLabel(code) {
  const match = LEARNER_POSTURES.find((entry) => entry.code === code)
  return match?.label || code || '—'
}

export function postureDescription(code) {
  const match = LEARNER_POSTURES.find((entry) => entry.code === code)
  return match?.description || ''
}

/** Labels courts pour l’UI apprenant 2.0 (barre de modes). */
export const LEARNER_POSTURE_SHORT_LABELS = {
  diagnostic: 'Diag',
  reflective_afest: 'Réflexif',
  knowledge_review: 'Bûchage',
}

export function postureShortLabel(code) {
  return LEARNER_POSTURE_SHORT_LABELS[code] || postureLabel(code)
}

/** Phrase descriptive affichée sous les boutons de mode (UI 2.0). */
export function postureBetaDescription(code) {
  const descriptions = {
    diagnostic: 'Mode diagnostic : tu explores la situation avec Hugo avant d’approfondir.',
    reflective_afest: 'Mode réflexif : tu analyses ta pratique avec Hugo.',
    knowledge_review: 'Mode bûchage : tu consolides des savoirs ou révises des points clés.',
  }
  return descriptions[code] || postureDescription(code)
}
