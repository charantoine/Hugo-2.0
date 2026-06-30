import test from 'node:test'
import assert from 'node:assert/strict'

import {
  buildDisplayModel,
  buildEngagementUiModel,
  buildEvaluationButtonFromCta,
  buildSynthesisButtonFromCta,
} from './engagementUiModel.js'

test('buildSynthesisButtonFromCta uses cta_synthesis as primary source', () => {
  const button = buildSynthesisButtonFromCta({
    cta_synthesis: {
      synthesis_ready_status: 'eligible',
      blocking_reasons: [],
      ui: {
        show_synthesis_button: true,
        button_label: 'Obtenir une synthèse',
        button_disabled: false,
        helper_text: null,
      },
    },
  })

  assert.equal(button.label, 'Obtenir une synthèse')
  assert.equal(button.disabled, false)
  assert.equal(button.readyStatus, 'eligible')
})

test('buildEvaluationButtonFromCta exposes blocking reasons when disabled', () => {
  const button = buildEvaluationButtonFromCta({
    cta_evaluation: {
      evaluation_ready_status: 'blocked_context_incomplete',
      blocking_reasons: ['Nommer une action concrète déjà réalisée.'],
      ui: {
        show_evaluation_button: true,
        button_label: 'Évaluation indisponible',
        button_disabled: true,
        helper_text: 'Nommer une action concrète déjà réalisée.',
      },
      last_evaluation: { status: 'none', completed_at: null },
    },
  })

  assert.equal(button.disabled, true)
  assert.equal(button.blockingReasons[0], 'Nommer une action concrète déjà réalisée.')
  assert.equal(button.helperText, 'Nommer une action concrète déjà réalisée.')
})

test('buildDisplayModel derives CTA buttons from cta_* blocks', () => {
  const model = buildDisplayModel({
    scene_label: 'Explorer',
    scene_progress: 0.65,
    active_quest_label: "Nommer l'action suivante.",
    quest_progress: 0.5,
    maturity_color: 'orange',
    persistent_objects: [{ id: 'branch-1', label: 'Incident tableau', status: 'orange' }],
    gamification_profile: 'A',
    cta_synthesis: {
      synthesis_ready_status: 'eligible',
      blocking_reasons: [],
      ui: {
        show_synthesis_button: true,
        button_label: 'Obtenir une synthèse',
        button_disabled: false,
        helper_text: null,
      },
    },
    cta_evaluation: {
      evaluation_ready_status: 'eligible',
      blocking_reasons: [],
      ui: {
        show_evaluation_button: true,
        button_label: 'Évaluation possible',
        button_disabled: false,
        helper_text: 'La conversation est encore partielle. L’évaluation sera prudente.',
      },
      last_evaluation: { status: 'none', completed_at: null },
    },
  })

  assert.equal(model.synthesisButton.label, 'Obtenir une synthèse')
  assert.equal(model.evaluationButton.label, 'Évaluation possible')
  assert.equal(model.evaluationButton.helperText, 'La conversation est encore partielle. L’évaluation sera prudente.')
  assert.equal(model.evaluationButton.visible, true)
})

test('buildEngagementUiModel falls back to a neutral default without cta blocks', () => {
  const model = buildEngagementUiModel({
    sessionUiState: null,
  })

  assert.equal(model.isDegraded, true)
  assert.equal(model.synthesisButton.visible, false)
  assert.equal(model.evaluationButton.visible, false)
})

test('youth display profile applies compact copy and hides maturity badge', () => {
  const model = buildDisplayModel({
    scene_label: 'Raconter',
    scene_progress: 0.2,
    active_quest_label: 'Nommer une action.',
    quest_progress: 0.1,
    maturity_color: 'orange',
    gamification_profile: 'B',
    learner_display_profile: 'youth',
    conversation_mode: {
      code: 'diagnostic',
      label: 'Diagnostic',
      can_switch: true,
      switch_warning: null,
    },
    cta_synthesis: {
      synthesis_ready_status: 'blocked_not_enough_content',
      blocking_reasons: ['Continuer la conversation.'],
      ui: {
        show_synthesis_button: true,
        button_label: 'Synthèse indisponible',
        button_disabled: true,
        helper_text: 'Continuer la conversation.',
      },
    },
    cta_evaluation: {
      evaluation_ready_status: 'blocked_min_turns_not_reached',
      blocking_reasons: ['Encore quelques échanges.'],
      ui: {
        show_evaluation_button: true,
        button_label: 'Évaluation indisponible',
        button_disabled: true,
        helper_text: 'Encore quelques échanges.',
      },
      last_evaluation: { status: 'none', completed_at: null },
    },
  })

  assert.equal(model.learnerDisplayProfile, 'youth')
  assert.equal(model.compactCopy, true)
  assert.equal(model.showMaturityBadge, false)
  assert.equal(model.conversationMode.label, 'Diagnostic')
  assert.match(model.steps[0].hint, /passé/)
})

test('CTA labels stay backend-driven regardless of learner_display_profile', () => {
  const uiState = {
    scene_label: 'Explorer',
    scene_progress: 0.65,
    gamification_profile: 'A',
    learner_display_profile: 'youth',
    cta_synthesis: {
      synthesis_ready_status: 'eligible',
      blocking_reasons: [],
      ui: {
        show_synthesis_button: true,
        button_label: 'Obtenir une synthèse',
        button_disabled: false,
        helper_text: null,
      },
    },
    cta_evaluation: {
      evaluation_ready_status: 'eligible',
      blocking_reasons: [],
      ui: {
        show_evaluation_button: true,
        button_label: 'Évaluation possible',
        button_disabled: false,
        helper_text: 'Prudence recommandée.',
      },
      last_evaluation: { status: 'none', completed_at: null },
    },
  }

  const youthModel = buildDisplayModel({ ...uiState, learner_display_profile: 'youth' })
  const proModel = buildDisplayModel({ ...uiState, learner_display_profile: 'professional' })

  assert.equal(youthModel.synthesisButton.label, 'Obtenir une synthèse')
  assert.equal(proModel.synthesisButton.label, 'Obtenir une synthèse')
  assert.equal(youthModel.evaluationButton.label, 'Évaluation possible')
  assert.equal(proModel.evaluationButton.label, 'Évaluation possible')
  assert.equal(youthModel.evaluationButton.helperText, 'Prudence recommandée.')
  assert.equal(proModel.evaluationButton.helperText, 'Prudence recommandée.')
})

test('adult display profile shows maturity badge and adult hints', () => {
  const model = buildDisplayModel({
    scene_label: 'Raconter',
    scene_progress: 0.35,
    active_quest_label: 'Clarifier le contexte.',
    quest_progress: 0.2,
    maturity_color: 'orange',
    gamification_profile: 'A',
    learner_display_profile: 'adult',
    cta_synthesis: {
      synthesis_ready_status: 'blocked_not_enough_content',
      blocking_reasons: [],
      ui: {
        show_synthesis_button: true,
        button_label: 'Synthèse indisponible',
        button_disabled: true,
        helper_text: null,
      },
    },
    cta_evaluation: {
      evaluation_ready_status: 'blocked_min_turns_not_reached',
      blocking_reasons: [],
      ui: {
        show_evaluation_button: true,
        button_label: 'Évaluation indisponible',
        button_disabled: true,
        helper_text: null,
      },
      last_evaluation: { status: 'none', completed_at: null },
    },
  })

  assert.equal(model.learnerDisplayProfile, 'adult')
  assert.equal(model.compactCopy, false)
  assert.equal(model.showMaturityBadge, true)
  assert.match(model.steps[0].hint, /situation/)
  assert.match(model.profileCopy.sessionIntro, /vous accompagne/i)
})

test('professional display profile keeps discursive defaults', () => {
  const model = buildDisplayModel({
    scene_label: 'Explorer',
    scene_progress: 0.7,
    active_quest_label: 'Formaliser un critère.',
    quest_progress: 0.6,
    maturity_color: 'green',
    gamification_profile: 'A',
    learner_display_profile: 'professional',
    cta_synthesis: {
      synthesis_ready_status: 'eligible',
      blocking_reasons: [],
      ui: {
        show_synthesis_button: true,
        button_label: 'Obtenir une synthèse',
        button_disabled: false,
        helper_text: null,
      },
    },
    cta_evaluation: {
      evaluation_ready_status: 'eligible',
      blocking_reasons: [],
      ui: {
        show_evaluation_button: true,
        button_label: 'Demander une évaluation',
        button_disabled: false,
        helper_text: null,
      },
      last_evaluation: { status: 'none', completed_at: null },
    },
  })

  assert.equal(model.learnerDisplayProfile, 'professional')
  assert.equal(model.showStepIcons, false)
  assert.equal(model.showMaturityBadge, true)
  assert.match(model.profileCopy.sessionIntro, /progression structurée/i)
})

test('INV-08 keeps gamification profile separate from learner display profile', () => {
  const model = buildDisplayModel({
    scene_label: 'Explorer',
    scene_progress: 0.5,
    gamification_profile: 'C',
    learner_display_profile: 'youth',
    cta_synthesis: {
      synthesis_ready_status: 'eligible',
      blocking_reasons: [],
      ui: {
        show_synthesis_button: true,
        button_label: 'Obtenir une synthèse',
        button_disabled: false,
        helper_text: null,
      },
    },
    cta_evaluation: {
      evaluation_ready_status: 'eligible',
      blocking_reasons: [],
      ui: {
        show_evaluation_button: true,
        button_label: 'Demander une évaluation',
        button_disabled: false,
        helper_text: null,
      },
      last_evaluation: { status: 'none', completed_at: null },
    },
  })

  assert.equal(model.learnerDisplayProfile, 'youth')
  assert.equal(model.gamificationProfile.code, 'C')
  assert.equal(model.displayProfileLabel, 'Jeune')
  assert.notEqual(model.gamificationProfile.label, model.displayProfileLabel)
})

test('INV-07 and A1-08 expose conversation_mode label from UIState', () => {
  const model = buildDisplayModel({
    scene_label: 'Raconter',
    scene_progress: 0.1,
    learner_display_profile: 'adult',
    conversation_mode: {
      code: 'diagnostic',
      label: 'Diagnostic',
      can_switch: true,
      switch_warning: 'Attention avant changement.',
    },
    cta_synthesis: {
      synthesis_ready_status: 'blocked_not_enough_content',
      blocking_reasons: [],
      ui: {
        show_synthesis_button: true,
        button_label: 'Synthèse indisponible',
        button_disabled: true,
        helper_text: null,
      },
    },
    cta_evaluation: {
      evaluation_ready_status: 'blocked_other',
      blocking_reasons: [],
      ui: {
        show_evaluation_button: true,
        button_label: 'Évaluation indisponible',
        button_disabled: true,
        helper_text: null,
      },
      last_evaluation: { status: 'none', completed_at: null },
    },
  })

  assert.equal(model.conversationMode.code, 'diagnostic')
  assert.equal(model.conversationMode.label, 'Diagnostic')
  assert.equal(model.conversationMode.switchWarning, 'Attention avant changement.')
})
