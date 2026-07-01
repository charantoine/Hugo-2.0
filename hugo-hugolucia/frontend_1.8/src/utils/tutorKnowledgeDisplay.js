import { summarizeTutorArtifact } from './tutorChatImport.js'

export function formatTutorArtifactList(artifacts) {
  return (artifacts || [])
    .map((item) => ({ item, summary: summarizeTutorArtifact(item) }))
    .filter((entry) => entry.summary)
}

export function tutorArtifactStorageKey(groupId, learnerId) {
  return `${String(groupId || '').trim()}:${String(learnerId || '').trim()}`
}
