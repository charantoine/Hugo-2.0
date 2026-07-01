import { buildEngagementUiModel } from './engagementUiModel.js'
import { frontendFeatures } from './frontendConfig.js'

/** Modèle minimal pour alimenter LearnerConversationFeed en mode persona (tuteur/formateur). */
export function buildPersonaConversationFeedModel() {
  return buildEngagementUiModel({
    featureFlags: frontendFeatures,
    sessionUiState: null,
  })
}
