import api from '../api/client'
import { useTutorWorkspaceStore } from '../stores/tutorWorkspace.js'
import {
  TUTOR_WORKSPACE_PRIMARY_POSTURE,
  findProfileIdByCode,
  normalizeConversationProfilesResponse,
} from './tutorWorkspaceProfiles.js'

async function resolveWorkspaceProfileId(profileCode, conversationProfiles = []) {
  let profileId = findProfileIdByCode(conversationProfiles, profileCode)
  if (profileId) return { profileId, profiles: conversationProfiles }

  const { data } = await api.get('/hugo/learner-conversation-profiles/')
  const profiles = normalizeConversationProfilesResponse(data)
  profileId = findProfileIdByCode(profiles, profileCode)
  if (!profileId) {
    throw new Error(`Profil ${profileCode} introuvable — lancez bootstrap_tutor_workspace_profiles.`)
  }
  return { profileId, profiles }
}

export async function openTutorWorkspaceChat(router, {
  profileCode,
  groupId,
  learnerId,
  sourceSessionId = '',
  conversationProfiles = [],
}) {
  const { profileId } = await resolveWorkspaceProfileId(profileCode, conversationProfiles)

  const posture = TUTOR_WORKSPACE_PRIMARY_POSTURE[profileCode] || 'reflective_afest'
  const payload = {
    group: groupId,
    learner_conversation_profile_id: profileId,
  }
  const { data } = await api.post('/hugo/sessions/', payload)
  if (posture && posture !== 'reflective_afest') {
    try {
      await api.post(`/hugo/sessions/${data.id}/set-posture/`, { posture })
    } catch {
      // posture par défaut conservée
    }
  }

  const store = useTutorWorkspaceStore()
  store.setContext({
    workspaceSessionId: String(data.id),
    profileCode,
    groupId: String(groupId),
    learnerId: String(learnerId),
    sourceSessionId: sourceSessionId ? String(sourceSessionId) : '',
  })

  await router.push({
    name: 'ProdTutorChatSession',
    params: { sessionId: data.id },
    query: {
      learner_id: String(learnerId),
      group_id: String(groupId),
      source_session_id: sourceSessionId ? String(sourceSessionId) : undefined,
      profile_code: profileCode,
    },
  })

  return data
}

export function importKindForWorkspaceProfile(profileCode) {
  const map = {
    tutor_workspace_prep: 'tutor_session_prep',
    tutor_workspace_diagnostic: 'tutor_diagnostic_notes',
    tutor_workspace_coreflex: 'tutor_reflection',
    tutor_workspace_journal: 'tutor_journal_entry',
  }
  return map[profileCode] || null
}
