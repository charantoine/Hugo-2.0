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
