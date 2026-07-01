import { isPureTrainerPersona } from './trainerUiLabels.js'
import { isPureTutorPersona } from './tutorUiLabels.js'

export const WORKSPACE_MODES = Object.freeze({
  LEARNER: 'learner',
  TUTOR: 'tutor',
  TRAINER: 'trainer',
})

/** Résout le mode workspace depuis la route et le rôle utilisateur. */
export function resolveWorkspaceMode(route, user) {
  const path = String(route?.path || '')
  const name = String(route?.name || '')

  if (path.startsWith('/app/tutor/chat') || name === 'ProdTutorChatSession') {
    return WORKSPACE_MODES.TUTOR
  }
  if (
    path.startsWith('/app/trainer/chat')
    || name === 'ProdTrainerChatSession'
    || name === 'ProdTrainerChatHome'
  ) {
    return WORKSPACE_MODES.TRAINER
  }

  if (route?.query?.tutor_ctx === '1' && isPureTutorPersona(user)) {
    return WORKSPACE_MODES.TUTOR
  }
  if (isPureTrainerPersona(user) && path.startsWith('/app/session/')) {
    return WORKSPACE_MODES.TRAINER
  }

  return WORKSPACE_MODES.LEARNER
}

export function isLearnerWorkspaceMode(mode) {
  return mode === WORKSPACE_MODES.LEARNER
}
