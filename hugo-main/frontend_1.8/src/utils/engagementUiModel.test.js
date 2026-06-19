import test from 'node:test'
import assert from 'node:assert/strict'

import { buildEngagementUiModel, getLatestTurnState } from './engagementUiModel.js'

test('getLatestTurnState extracts the latest learner runtime payload', () => {
  const messages = [
    { role: 'ASSISTANT', content: 'Bonjour' },
    {
      role: 'LEARNER',
      content: 'J’ai essayé hier.',
      llm_request_payload: {
        turn_state: {
          episode_clarity: 'medium',
          has_concrete_actions: true,
        },
      },
    },
  ]

  assert.deepEqual(getLatestTurnState(messages), {
    episode_clarity: 'medium',
    has_concrete_actions: true,
  })
})

test('buildEngagementUiModel derives scene progress and quests from runtime signals', () => {
  const model = buildEngagementUiModel({
    session: {
      id: 'session-1',
      current_phase: 'conceptualization',
    },
    messages: [
      {
        role: 'LEARNER',
        content: 'J’ai mieux compris ce qui coinçait.',
        llm_request_payload: {
          turn_state: {
            session_phase: 'conceptualization',
            episode_clarity: 'medium',
            reflective_depth: 'medium',
            has_concrete_actions: false,
            recent_progress: 'medium',
            can_close_for_now: false,
            covered_points: ['Le problème est mieux nommé'],
            remaining_open_points: ['Formuler la prochaine action'],
          },
          conversation_decision: {
            pedagogical_move: 'assist',
          },
        },
      },
    ],
    traces: [],
    evidence: [],
  })

  assert.equal(model.scene_progress.current_step.label, 'Retenir')
  assert.equal(model.scene_progress.current_step_index, 3)
  assert.equal(model.quest_cards[0].title, 'Choisir la prochaine action')
  assert.equal(model.persistent_objects[0].status, 'building')
})

test('buildEngagementUiModel promotes transmettre when closure or traces are ready', () => {
  const model = buildEngagementUiModel({
    session: {
      id: 'session-2',
      current_phase: 'closure',
    },
    messages: [
      {
        role: 'LEARNER',
        llm_request_payload: {
          turn_state: {
            session_phase: 'closure',
            can_close_for_now: true,
            closure_signal: 'explicit',
            covered_points: ['Mini-bilan prêt pour le tuteur'],
            remaining_open_points: [],
          },
        },
      },
    ],
    traces: [
      {
        id: 'trace-1',
        session: 'session-2',
        created_at: '2026-04-23T10:00:00Z',
      },
    ],
    evidence: [],
  })

  assert.equal(model.scene_progress.current_step.label, 'Transmettre')
  assert.equal(model.persistent_objects[0].status, 'ready')
  assert.equal(model.symbolic_rewards[2].unlocked, true)
})
