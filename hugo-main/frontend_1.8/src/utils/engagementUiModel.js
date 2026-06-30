import { frontendFeatures, getGamificationProfileTheme } from './frontendConfig.js'

export const SCENE_STEPS = Object.freeze([
  {
    id: 'raconter',
    label: 'Raconter',
    hint: 'Poser calmement la situation vécue.',
  },
  {
    id: 'comprendre',
    label: 'Comprendre',
    hint: 'Repérer ce qui bloque ou ce qui compte vraiment.',
  },
  {
    id: 'decider',
    label: 'Décider',
    hint: 'Choisir une prochaine action réaliste.',
  },
  {
    id: 'retenir',
    label: 'Retenir',
    hint: "Transformer l'expérience en apprentissage clair.",
  },
  {
    id: 'transmettre',
    label: 'Transmettre',
    hint: 'Préparer un mini-bilan partageable.',
  },
])

const LOW_VALUES = new Set(['low', 'faible', 'weak', 'none', 'absent', 'unknown', ''])
const MEDIUM_VALUES = new Set(['medium', 'moyen', 'moderate'])
const HIGH_VALUES = new Set(['high', 'élevé', 'eleve', 'strong', 'fort', 'ready', 'true'])

function toText(value) {
  return String(value || '').trim()
}

function normalizeToken(value) {
  return toText(value).toLowerCase()
}

function toList(value) {
  if (!Array.isArray(value)) return []
  return value.map((item) => toText(item)).filter(Boolean)
}

function flattenTextList(items) {
  return toList(items).join(' ').toLowerCase()
}

function scoreSignal(value) {
  const normalized = normalizeToken(value)
  if (HIGH_VALUES.has(normalized)) return 2
  if (MEDIUM_VALUES.has(normalized)) return 1
  if (LOW_VALUES.has(normalized)) return 0
  if (normalized === 'true') return 2
  return 0
}

function hasUsefulBoolean(value) {
  return value === true || value === 'true'
}

function hasKeyword(text, keywords) {
  return keywords.some((keyword) => text.includes(keyword))
}

export function extractLatestRequestPayload(messages = []) {
  for (let index = messages.length - 1; index >= 0; index -= 1) {
    const message = messages[index]
    if (message?.role === 'LEARNER' && message.llm_request_payload && Object.keys(message.llm_request_payload).length) {
      return message.llm_request_payload
    }
  }
  return {}
}

export function getLatestTurnState(messages = []) {
  return extractLatestRequestPayload(messages)?.turn_state || {}
}

export function getLatestConversationDecision(messages = []) {
  return extractLatestRequestPayload(messages)?.conversation_decision || {}
}

function deriveStageIndex({ session, turnState, sessionTraces }) {
  const coveredPoints = toList(turnState.covered_points)
  const remainingOpenPoints = toList(turnState.remaining_open_points)
  const phase = normalizeToken(session?.current_phase || turnState.session_phase)
  const coverageText = flattenTextList(coveredPoints)

  let stageIndex = 0

  if (phase === 'exploration') stageIndex = Math.max(stageIndex, 1)
  if (phase === 'conceptualization') stageIndex = Math.max(stageIndex, 2)
  if (phase === 'closure') stageIndex = Math.max(stageIndex, 4)

  if (scoreSignal(turnState.episode_clarity) > 0 || coveredPoints.length > 0) {
    stageIndex = Math.max(stageIndex, 1)
  }

  if (
    hasUsefulBoolean(turnState.has_concrete_actions)
    || hasKeyword(coverageText, ['action', 'prochaine', 'décision', 'decision', 'choix'])
  ) {
    stageIndex = Math.max(stageIndex, 2)
  }

  if (
    scoreSignal(turnState.reflective_depth) > 0
    || scoreSignal(turnState.recent_progress) > 0
    || scoreSignal(turnState.evidence_strength) > 0
    || hasKeyword(coverageText, ['reten', 'apprent', 'repère', 'repere', 'règle', 'regle'])
  ) {
    stageIndex = Math.max(stageIndex, 3)
  }

  if (
    hasUsefulBoolean(turnState.can_close_for_now)
    || scoreSignal(turnState.closure_signal) > 0
    || sessionTraces.length > 0
    || remainingOpenPoints.length === 0
    || hasKeyword(coverageText, ['transmet', 'mini-bilan', 'bilan', 'tuteur', 'partage'])
  ) {
    stageIndex = Math.max(stageIndex, 4)
  }

  return Math.min(stageIndex, SCENE_STEPS.length - 1)
}

function rephraseOpenPoint(point, index) {
  const normalized = normalizeToken(point)
  if (normalized.includes('cause')) {
    return {
      id: `quest-open-${index}`,
      title: 'Comprendre ce qui a pesé',
      description: 'Repère une cause plausible ou un élément qui a vraiment compté.',
    }
  }
  if (normalized.includes('action') || normalized.includes('prochaine') || normalized.includes('next')) {
    return {
      id: `quest-open-${index}`,
      title: 'Choisir la prochaine action',
      description: 'Formule une action simple et réaliste pour la suite.',
    }
  }
  if (normalized.includes('tuteur') || normalized.includes('partage') || normalized.includes('trace')) {
    return {
      id: `quest-open-${index}`,
      title: 'Préparer le message utile',
      description: 'Mets en forme ce que tu pourras transmettre ensuite.',
    }
  }
  return {
    id: `quest-open-${index}`,
    title: 'Faire avancer la scène',
    description: point,
  }
}

function buildQuestCards(turnState, stageIndex) {
  const remainingOpenPoints = toList(turnState.remaining_open_points)
  const quests = remainingOpenPoints.slice(0, 3).map((item, index) => ({
    ...rephraseOpenPoint(item, index),
    status: 'next',
  }))

  if (!quests.length && scoreSignal(turnState.episode_clarity) === 0) {
    quests.push({
      id: 'clarify-scene',
      title: 'Clarifier la situation',
      description: 'Décris ce qui s’est passé avec un exemple concret.',
      status: 'next',
    })
  }

  if (quests.length < 3 && !hasUsefulBoolean(turnState.has_concrete_actions)) {
    quests.push({
      id: 'next-action',
      title: 'Nommer une prochaine action',
      description: 'Choisis un petit pas que tu pourrais tester rapidement.',
      status: 'next',
    })
  }

  if (quests.length < 3 && stageIndex >= 2 && scoreSignal(turnState.reflective_depth) === 0) {
    quests.push({
      id: 'learning-capsule',
      title: 'Retenir l’essentiel',
      description: 'Transforme ce que tu vis en règle simple à garder en tête.',
      status: 'next',
    })
  }

  if (quests.length < 3 && !hasUsefulBoolean(turnState.can_close_for_now)) {
    quests.push({
      id: 'mini-bilan',
      title: 'Préparer le mini-bilan',
      description: 'Rassemble ce qu’il faudra transmettre au bon moment.',
      status: 'next',
    })
  }

  return quests.slice(0, 3)
}

function buildPersistentObjects({ session, turnState, sessionTraces, sessionEvidence }) {
  const coveredPoints = toList(turnState.covered_points)
  const firstCoveredPoint = coveredPoints[0]
  const lastTrace = sessionTraces[0]
  const traceReady = Boolean(lastTrace) || hasUsefulBoolean(turnState.can_close_for_now)

  const objects = [
    {
      id: 'trace-ready',
      kind: 'trace',
      title: traceReady ? 'Trace prête à relire' : 'Trace en préparation',
      description: traceReady
        ? 'Ta scène peut déjà être transformée en mini-bilan exploitable.'
        : 'La scène avance. Une trace claire pourra être générée quand le fil sera assez mûr.',
      status: traceReady ? 'ready' : 'building',
      meta: lastTrace?.validated_at ? 'Trace validée' : (traceReady ? 'Prête à générer' : 'Encore en construction'),
    },
    {
      id: 'skill-illustration',
      kind: 'skill',
      title: 'Compétence mobilisée',
      description: firstCoveredPoint
        ? `On voit déjà un appui utile autour de : ${firstCoveredPoint}.`
        : 'La compétence mobilisée apparaîtra ici quand la situation sera mieux décrite.',
      status: firstCoveredPoint ? 'visible' : 'building',
      meta: firstCoveredPoint ? 'Illustration honnête, sans validation automatique' : 'À illustrer',
    },
    {
      id: 'progress-capsule',
      kind: 'capsule',
      title: 'Capsule de progrès',
      description: scoreSignal(turnState.recent_progress) > 0
        ? 'Tu as déjà franchi une étape utile dans cette scène.'
        : 'La capsule apparaîtra dès qu’un vrai pas en avant sera repéré.',
      status: scoreSignal(turnState.recent_progress) > 0 ? 'ready' : 'building',
      meta: sessionEvidence.length ? `${sessionEvidence.length} preuve(s) liée(s)` : (session?.current_phase || 'en cours'),
    },
  ]

  return objects
}

function buildSymbolicRewards({ stageIndex, messages, profile }) {
  const userMessages = messages.filter((message) => message?.role === 'LEARNER')

  return [
    {
      id: 'badge-scene',
      kind: 'badge',
      label: 'Premier pas',
      description: 'Débloqué dès que la scène est vraiment lancée.',
      unlocked: userMessages.length > 0,
    },
    {
      id: 'theme-scene',
      kind: 'theme',
      label: stageIndex >= 2 ? 'Thème Horizon' : 'Thème Élan',
      description: 'Un thème visuel symbolique lié à la progression réelle.',
      unlocked: stageIndex >= 1,
    },
    {
      id: 'avatar-hugo',
      kind: 'avatar',
      label: profile === 'A' ? 'Hugo Curieux' : (profile === 'C' ? 'Hugo Focus' : 'Hugo Complice'),
      description: 'Une légère variation d’avatar, sans effet sur le moteur.',
      unlocked: stageIndex >= 3,
    },
  ]
}

export function buildEngagementUiModel({
  session = {},
  messages = [],
  traces = [],
  evidence = [],
  featureFlags = frontendFeatures,
} = {}) {
  const profile = featureFlags.gamification_profile || frontendFeatures.gamification_profile
  const turnState = getLatestTurnState(messages)
  const decision = getLatestConversationDecision(messages)
  const sessionId = toText(session.id)
  const sessionTraces = traces
    .filter((trace) => toText(trace?.session) === sessionId)
    .sort((left, right) => new Date(right.created_at || 0) - new Date(left.created_at || 0))
  const traceIds = new Set(sessionTraces.map((trace) => toText(trace.id)))
  const sessionEvidence = evidence.filter((item) => (
    toText(item?.session) === sessionId
    || traceIds.has(toText(item?.trace))
  ))
  const stageIndex = deriveStageIndex({ session, turnState, sessionTraces })
  const sceneProgress = {
    current_step_index: stageIndex,
    current_step: SCENE_STEPS[stageIndex],
    percent: Math.round(((stageIndex + 1) / SCENE_STEPS.length) * 100),
    steps: SCENE_STEPS.map((step, index) => ({
      ...step,
      state: index < stageIndex ? 'done' : (index === stageIndex ? 'current' : 'locked'),
    })),
    covered_points: toList(turnState.covered_points),
    remaining_open_points: toList(turnState.remaining_open_points),
  }

  return {
    scene_progress: sceneProgress,
    quest_cards: buildQuestCards(turnState, stageIndex),
    persistent_objects: buildPersistentObjects({ session, turnState, sessionTraces, sessionEvidence }),
    symbolic_rewards: buildSymbolicRewards({ stageIndex, messages, profile }),
    gamification_profile: {
      code: profile,
      ...getGamificationProfileTheme(profile),
    },
    ui_visibility_flags: {
      frontend_mode: featureFlags.frontend_mode,
      engagement_ui_enabled: featureFlags.engagement_ui_enabled,
      scene_progress_enabled: featureFlags.scene_progress_enabled,
      persistent_objects_enabled: featureFlags.persistent_objects_enabled,
      symbolic_rewards_enabled: featureFlags.symbolic_rewards_enabled,
    },
    tutor_signals: {
      current_phase: toText(session.current_phase || turnState.session_phase || 'exploration'),
      can_close_for_now: hasUsefulBoolean(turnState.can_close_for_now),
      closure_signal: toText(turnState.closure_signal || 'none'),
      recent_progress: toText(turnState.recent_progress || ''),
      decision_move: toText(decision.pedagogical_move || ''),
    },
  }
}
