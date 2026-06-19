import test from 'node:test'
import assert from 'node:assert/strict'

import {
  DISPLAY_PROFILE_PRESETS,
  DISPLAY_PROFILE_VALUES,
  getDisplayProfilePreset,
  normalizeDisplayProfile,
} from './displayProfilePresets.js'
import { buildDisplayModel } from './engagementUiModel.js'

const BASE_UI_STATE = {
  scene_label: 'Explorer',
  scene_progress: 0.5,
  active_quest_label: 'Nommer une action.',
  quest_progress: 0.4,
  maturity_color: 'orange',
  gamification_profile: 'B',
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

test('normalizeDisplayProfile accepts youth, adult and professional', () => {
  assert.equal(normalizeDisplayProfile('youth'), 'youth')
  assert.equal(normalizeDisplayProfile('adult'), 'adult')
  assert.equal(normalizeDisplayProfile('professional'), 'professional')
  assert.equal(normalizeDisplayProfile('unknown'), 'professional')
})

test('DISPLAY_PROFILE_PRESETS exposes all three profiles', () => {
  for (const profile of DISPLAY_PROFILE_VALUES) {
    assert.ok(DISPLAY_PROFILE_PRESETS[profile], `missing preset for ${profile}`)
    assert.ok(getDisplayProfilePreset(profile))
  }
})

test('adult preset differs from youth on maturity and hints', () => {
  const youth = getDisplayProfilePreset('youth')
  const adult = getDisplayProfilePreset('adult')
  assert.equal(youth.showMaturityBadge, false)
  assert.equal(adult.showMaturityBadge, true)
  assert.notEqual(youth.stepHints.Raconter, adult.stepHints.Raconter)
})

test('DSP-04 and DSP-07 keep CTA contract identical across display profiles', () => {
  const profiles = ['youth', 'adult', 'professional']
  const models = profiles.map((profile) => buildDisplayModel({
    ...BASE_UI_STATE,
    learner_display_profile: profile,
  }))

  for (const model of models) {
    assert.equal(model.synthesisButton.label, 'Obtenir une synthèse')
    assert.equal(model.evaluationButton.label, 'Évaluation possible')
    assert.equal(model.evaluationButton.helperText, 'Prudence recommandée.')
    assert.equal(model.synthesisButton.disabled, false)
    assert.equal(model.evaluationButton.disabled, false)
  }

  const keys = models.map((model) => Object.keys(model).sort().join(','))
  assert.equal(keys[0], keys[1])
  assert.equal(keys[1], keys[2])
})
