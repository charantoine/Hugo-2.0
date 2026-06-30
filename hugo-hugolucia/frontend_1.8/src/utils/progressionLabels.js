export const SCENE_LABELS = Object.freeze({
  Raconter: 'Je raconte ma situation',
  Explorer: "J'explore avec Hugo",
  'Synthétiser': 'Je fais le point',
})

export const SCENE_SEQUENCE = Object.freeze([
  {
    id: 'raconter',
    key: 'Raconter',
    label: 'Raconter',
    displayLabel: SCENE_LABELS.Raconter,
    hint: 'Poser calmement la situation vécue.',
  },
  {
    id: 'explorer',
    key: 'Explorer',
    label: 'Explorer',
    displayLabel: SCENE_LABELS.Explorer,
    hint: 'Repérer ce qui bloque ou ce qui compte vraiment.',
  },
  {
    id: 'synthetiser',
    key: 'Synthétiser',
    label: 'Synthétiser',
    displayLabel: SCENE_LABELS['Synthétiser'],
    hint: 'Faire le point sur ce qui est désormais clair et partageable.',
  },
])

export const MATURITY_LABELS = Object.freeze({
  red: "En cours d'exploration",
  orange: 'Bonne avancée',
  green: 'Prêt à faire le bilan',
})

export const SYNTHESIS_BUTTON_LABELS = Object.freeze({
  locked: 'Continuer la conversation',
  possible: 'Faire une synthèse',
  ready: 'Synthèse disponible',
})

export const EVALUATION_BUTTON_LABELS = Object.freeze({
  locked: 'Évaluation prématurée',
  possible: 'Évaluation possible',
  ready: 'Évaluation recommandée',
})

export const GAMIFICATION_PROFILES = Object.freeze({
  A: { showProgressBar: true, showQuestLabel: true, showMaturityBadge: true },
  B: { showProgressBar: true, showQuestLabel: false, showMaturityBadge: false },
  C: { showProgressBar: false, showQuestLabel: false, showMaturityBadge: false },
})
