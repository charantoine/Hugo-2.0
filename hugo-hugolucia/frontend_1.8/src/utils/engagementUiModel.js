import { frontendFeatures, getGamificationProfileTheme } from './frontendConfig.js'
import {
  DISPLAY_PROFILE_LABELS,
  getDisplayProfilePreset,
  normalizeDisplayProfile,
} from './displayProfilePresets.js'
import { getDisplayProfileCopy } from './displayProfileCopy.js'
import {
  GAMIFICATION_PROFILES,
  MATURITY_LABELS,
  SCENE_LABELS,
  SCENE_SEQUENCE,
} from './progressionLabels.js'

const DEGRADED_SCENE_KEY = 'Raconter'

const EVALUATION_READY_STATUSES = new Set([
  'eligible',
  'blocked_missing_data',
  'blocked_min_turns_not_reached',
  'blocked_context_incomplete',
  'blocked_other',
])

const SYNTHESIS_READY_STATUSES = new Set([
  'eligible',
  'blocked_not_enough_content',
  'blocked_context_incomplete',
])

function toText(value) {
  return String(value || '').trim()
}

function normalizeToken(value) {
  return toText(value).toLowerCase()
}

function clampProgress(value) {
  const numeric = Number(value)
  if (!Number.isFinite(numeric)) return 0
  return Math.min(1, Math.max(0, numeric))
}

function resolveProfile(profile) {
  const normalized = toText(profile).toUpperCase()
  return ['A', 'B', 'C'].includes(normalized) ? normalized : 'B'
}

function getSceneIndex(sceneLabel) {
  const normalized = normalizeToken(sceneLabel)
  return Math.max(0, SCENE_SEQUENCE.findIndex((step) => normalizeToken(step.key) === normalized))
}

function applyStepHints(steps, hints) {
  if (!hints || !Object.keys(hints).length) return steps
  return steps.map((step) => ({
    ...step,
    hint: hints[step.key] || step.hint,
  }))
}

function buildSteps(sceneLabel, stepHints = {}) {
  const currentStepIndex = getSceneIndex(sceneLabel)
  const steps = SCENE_SEQUENCE.map((step, index) => ({
    ...step,
    state: index < currentStepIndex ? 'done' : (index === currentStepIndex ? 'current' : 'locked'),
  }))
  return {
    currentStepIndex,
    currentStep: SCENE_SEQUENCE[currentStepIndex],
    steps: applyStepHints(steps, stepHints),
  }
}

function mergePresentationFlags(displayPreset) {
  return {
    showProgressBar: Boolean(displayPreset.showProgressBar),
    showQuestLabel: Boolean(displayPreset.showQuestLabel),
    showMaturityBadge: Boolean(displayPreset.showMaturityBadge),
    compactCopy: Boolean(displayPreset.compactCopy),
    showStepIcons: Boolean(displayPreset.showStepIcons),
    progressPanelIntro: displayPreset.progressPanelIntro,
  }
}

function buildConversationMode(uiState) {
  const mode = uiState?.conversation_mode
  if (!mode) return null
  const transitions = Array.isArray(mode.allowed_posture_transitions)
    ? mode.allowed_posture_transitions.map((entry) => ({
      code: toText(entry?.code) || null,
      label: toText(entry?.label) || null,
      allowed: Boolean(entry?.allowed),
      warning: toText(entry?.warning) || null,
    })).filter((entry) => entry.code)
    : []
  return {
    code: toText(mode.code) || null,
    label: toText(mode.label) || null,
    canSwitch: Boolean(mode.can_switch),
    switchWarning: toText(mode.switch_warning) || null,
    switchLockedReason: toText(mode.switch_locked_reason) || null,
    allowedPostureTransitions: transitions,
  }
}

function buildLockedButton(label = 'Indisponible') {
  return {
    state: 'locked',
    label,
    visible: false,
    disabled: true,
    highlighted: false,
    helperText: null,
    blockingReasons: [],
  }
}

export function buildSynthesisButtonFromCta(uiState) {
  const cta = uiState?.cta_synthesis
  if (!cta?.ui) {
    return buildLockedButton('Synthèse indisponible')
  }
  const status = toText(cta.synthesis_ready_status)
  const ui = cta.ui
  const blockingReasons = Array.isArray(cta.blocking_reasons)
    ? cta.blocking_reasons.map((item) => toText(item)).filter(Boolean)
    : []
  const disabled = Boolean(ui.button_disabled)
  return {
    state: status === 'eligible' ? 'ready' : (disabled ? 'locked' : 'possible'),
    label: toText(ui.button_label) || 'Obtenir une synthèse',
    visible: ui.show_synthesis_button !== false,
    disabled,
    highlighted: status === 'eligible' && !disabled,
    helperText: toText(ui.helper_text) || blockingReasons[0] || null,
    blockingReasons,
    readyStatus: SYNTHESIS_READY_STATUSES.has(status) ? status : 'blocked_context_incomplete',
  }
}

export function buildEvaluationButtonFromCta(uiState) {
  const cta = uiState?.cta_evaluation
  if (!cta?.ui) {
    return buildLockedButton('Évaluation indisponible')
  }
  const status = toText(cta.evaluation_ready_status)
  const ui = cta.ui
  const blockingReasons = Array.isArray(cta.blocking_reasons)
    ? cta.blocking_reasons.map((item) => toText(item)).filter(Boolean)
    : []
  const disabled = Boolean(ui.button_disabled)
  const advisory = Boolean(ui.advisory)
  const label = toText(ui.button_label) || 'Demander une évaluation'
  const isFullyReady = status === 'eligible' && !advisory && !disabled
  return {
    state: status === 'eligible' ? (isFullyReady ? 'ready' : 'possible') : 'locked',
    label,
    visible: ui.show_evaluation_button !== false,
    disabled,
    advisory,
    highlighted: isFullyReady,
    helperText: toText(ui.helper_text) || blockingReasons[0] || null,
    blockingReasons,
    readyStatus: EVALUATION_READY_STATUSES.has(status) ? status : 'blocked_other',
    lastEvaluation: cta.last_evaluation || { status: 'none', completed_at: null },
  }
}

function buildPersistentObjects(uiState) {
  return Array.isArray(uiState?.persistent_objects)
    ? uiState.persistent_objects.map((item, index) => ({
      id: item?.id || `persistent-${index}`,
      kind: item?.kind || 'memory',
      title: item?.label || item?.title || 'Repère',
      description: item?.description || item?.label || '',
      status: item?.status || 'visible',
      meta: item?.meta || '',
    }))
    : []
}

function buildSymbolicRewards(sceneProgress, profile) {
  const percent = Math.round(clampProgress(sceneProgress) * 100)
  return [
    {
      id: 'badge-scene',
      kind: 'badge',
      label: 'Premier pas',
      description: 'Débloqué dès que la scène est vraiment lancée.',
      unlocked: percent > 0,
    },
    {
      id: 'theme-scene',
      kind: 'theme',
      label: percent >= 65 ? 'Thème Horizon' : 'Thème Élan',
      description: 'Un thème léger, strictement cosmétique.',
      unlocked: percent >= 25,
    },
    {
      id: 'avatar-hugo',
      kind: 'avatar',
      label: profile === 'A' ? 'Hugo Curieux' : (profile === 'C' ? 'Hugo Focus' : 'Hugo Complice'),
      description: 'Une variation visuelle sans effet pédagogique.',
      unlocked: percent >= 65,
    },
  ]
}

function buildDefaultDisplayModel(profile, featureFlags, learnerDisplayProfile = 'professional') {
  const effectiveProfile = resolveProfile(profile)
  const cosmeticProfile = GAMIFICATION_PROFILES[effectiveProfile] || GAMIFICATION_PROFILES.B
  const displayProfile = normalizeDisplayProfile(learnerDisplayProfile)
  const displayPreset = getDisplayProfilePreset(displayProfile)
  const presentation = mergePresentationFlags(displayPreset)
  const { currentStepIndex, currentStep, steps } = buildSteps(DEGRADED_SCENE_KEY, displayPreset.stepHints)

  return {
    isDegraded: true,
    sceneLabel: 'Chargement...',
    sceneLabelRaw: DEGRADED_SCENE_KEY,
    sceneProgress: 0,
    sceneProgressPercent: 0,
    currentStepIndex,
    currentStep,
    steps,
    showProgressBar: false,
    questLabel: null,
    showQuestLabel: presentation.showQuestLabel,
    questProgress: 0,
    questProgressPercent: 0,
    maturityLabel: null,
    showMaturityBadge: false,
    maturityColor: 'red',
    synthesisButton: buildLockedButton('Synthèse indisponible'),
    evaluationButton: buildLockedButton('Évaluation indisponible'),
    evaluationTriggerState: 'red',
    evaluationTriggerMessage: null,
    persistentObjects: [],
    symbolicRewards: buildSymbolicRewards(0, effectiveProfile),
    gamificationProfile: {
      code: effectiveProfile,
      ...getGamificationProfileTheme(effectiveProfile),
    },
    learnerDisplayProfile: displayProfile,
    displayProfileLabel: DISPLAY_PROFILE_LABELS[displayProfile] || DISPLAY_PROFILE_LABELS.professional,
    profileCopy: getDisplayProfileCopy(displayProfile),
    conversationMode: null,
    dispersionRisk: false,
    priorityBranchLabel: null,
    compactCopy: presentation.compactCopy,
    showStepIcons: presentation.showStepIcons,
    progressPanelIntro: presentation.progressPanelIntro,
    uiVisibilityFlags: {
      frontendMode: featureFlags.frontend_mode,
      engagementUiEnabled: featureFlags.engagement_ui_enabled,
      sceneProgressEnabled: featureFlags.scene_progress_enabled,
      persistentObjectsEnabled: featureFlags.persistent_objects_enabled,
      symbolicRewardsEnabled: featureFlags.symbolic_rewards_enabled,
      synthesisVisible: false,
      evaluationVisible: false,
    },
  }
}

export function buildDisplayModel(uiState, featureFlags = frontendFeatures) {
  const effectiveProfile = resolveProfile(uiState?.gamification_profile || featureFlags.gamification_profile)
  const cosmeticProfile = GAMIFICATION_PROFILES[effectiveProfile] || GAMIFICATION_PROFILES.B
  const displayProfile = normalizeDisplayProfile(uiState?.learner_display_profile)
  const displayPreset = getDisplayProfilePreset(displayProfile)
  const presentation = mergePresentationFlags(displayPreset)
  const sceneLabelRaw = toText(uiState?.scene_label || 'Raconter')
  const sceneProgress = clampProgress(uiState?.scene_progress)
  const questProgress = clampProgress(uiState?.quest_progress)
  const maturityColor = ['red', 'orange', 'green'].includes(normalizeToken(uiState?.maturity_color))
    ? normalizeToken(uiState?.maturity_color)
    : 'red'
  const { currentStepIndex, currentStep, steps } = buildSteps(sceneLabelRaw, displayPreset.stepHints)
  const synthesisButton = buildSynthesisButtonFromCta(uiState)
  const evaluationButton = buildEvaluationButtonFromCta(uiState)

  return {
    isDegraded: false,
    sceneLabel: SCENE_LABELS[sceneLabelRaw] || sceneLabelRaw,
    sceneLabelRaw,
    sceneProgress,
    sceneProgressPercent: Math.round(sceneProgress * 100),
    currentStepIndex,
    currentStep,
    steps,
    showProgressBar: presentation.showProgressBar,
    questLabel: presentation.showQuestLabel ? toText(uiState?.active_quest_label) || null : null,
    showQuestLabel: presentation.showQuestLabel,
    questProgress,
    questProgressPercent: Math.round(questProgress * 100),
    maturityLabel: presentation.showMaturityBadge ? (MATURITY_LABELS[maturityColor] || '') : null,
    showMaturityBadge: presentation.showMaturityBadge,
    maturityColor,
    synthesisButton,
    evaluationButton,
    evaluationTriggerState: toText(uiState?.evaluation_trigger_state || 'red') || 'red',
    evaluationTriggerMessage: evaluationButton.helperText,
    persistentObjects: buildPersistentObjects(uiState),
    symbolicRewards: buildSymbolicRewards(sceneProgress, effectiveProfile),
    gamificationProfile: {
      code: effectiveProfile,
      ...getGamificationProfileTheme(effectiveProfile),
    },
    learnerDisplayProfile: displayProfile,
    displayProfileLabel: DISPLAY_PROFILE_LABELS[displayProfile] || DISPLAY_PROFILE_LABELS.professional,
    profileCopy: getDisplayProfileCopy(displayProfile),
    conversationMode: buildConversationMode(uiState),
    dispersionRisk: Boolean(uiState?.dispersion_risk),
    priorityBranchLabel: toText(uiState?.priority_branch_label) || null,
    compactCopy: presentation.compactCopy,
    showStepIcons: presentation.showStepIcons,
    progressPanelIntro: presentation.progressPanelIntro,
    uiVisibilityFlags: {
      frontendMode: featureFlags.frontend_mode,
      engagementUiEnabled: featureFlags.engagement_ui_enabled,
      sceneProgressEnabled: featureFlags.scene_progress_enabled,
      persistentObjectsEnabled: featureFlags.persistent_objects_enabled,
      symbolicRewardsEnabled: featureFlags.symbolic_rewards_enabled,
      synthesisVisible: synthesisButton.visible,
      evaluationVisible: evaluationButton.visible,
    },
  }
}

export function buildEngagementUiModel({
  featureFlags = frontendFeatures,
  sessionUiState = null,
} = {}) {
  const profile = resolveProfile(sessionUiState?.gamification_profile || featureFlags.gamification_profile)
  const learnerDisplayProfile = sessionUiState?.learner_display_profile
  if (!sessionUiState || !sessionUiState.scene_label) {
    return buildDefaultDisplayModel(profile, featureFlags, learnerDisplayProfile)
  }
  return buildDisplayModel(sessionUiState, featureFlags)
}
