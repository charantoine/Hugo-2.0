import test from 'node:test'
import assert from 'node:assert/strict'

import {
  TRAINER_BACK_TO_ORCHESTRATOR_LABEL,
  TRAINER_ORCHESTRATOR_PATH,
  TRAINER_ORCHESTRATOR_ROUTE_NAME,
} from './trainerNavigation.js'

test('trainer orchestrator hub route constants', () => {
  assert.equal(TRAINER_ORCHESTRATOR_ROUTE_NAME, 'ProdTrainerKnowledge')
  assert.equal(TRAINER_ORCHESTRATOR_PATH, '/app/trainer/knowledge')
  assert.equal(TRAINER_BACK_TO_ORCHESTRATOR_LABEL, 'Retour orchestrateur')
})
