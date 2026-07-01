import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { tutorArtifactStorageKey } from '../utils/tutorKnowledgeDisplay.js'

/**
 * Brouillons tuteur P1 — mémoire volatile (session navigateur uniquement, pas de localStorage).
 */
export const useTutorWorkspaceStore = defineStore('tutorWorkspace', () => {
  const context = ref(null)
  const artifactsByLearner = ref({})
  const sessionArtifacts = ref([])

  const activeLearnerKey = computed(() => {
    if (!context.value?.groupId || !context.value?.learnerId) return ''
    return tutorArtifactStorageKey(context.value.groupId, context.value.learnerId)
  })

  const learnerArtifacts = computed(() => {
    const key = activeLearnerKey.value
    if (!key) return []
    return artifactsByLearner.value[key] || []
  })

  function setContext(next) {
    context.value = next ? { ...next } : null
  }

  function clearContext() {
    context.value = null
  }

  function addArtifact(artifact, { mirrorToLearner = true } = {}) {
    if (!artifact?.metaKey || !artifact?.payload) return
    const entry = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      metaKey: artifact.metaKey,
      payload: { ...artifact.payload },
      workspaceSessionId: context.value?.workspaceSessionId || artifact.payload.session_id,
    }
    sessionArtifacts.value = [entry, ...sessionArtifacts.value]

    if (mirrorToLearner && entry.payload.group_id && entry.payload.learner_id) {
      const key = tutorArtifactStorageKey(entry.payload.group_id, entry.payload.learner_id)
      const current = artifactsByLearner.value[key] || []
      artifactsByLearner.value = {
        ...artifactsByLearner.value,
        [key]: [entry, ...current],
      }
    }
  }

  function artifactsForLearner(groupId, learnerId) {
    const key = tutorArtifactStorageKey(groupId, learnerId)
    return artifactsByLearner.value[key] || []
  }

  function resetSessionArtifacts() {
    sessionArtifacts.value = []
  }

  return {
    context,
    sessionArtifacts,
    learnerArtifacts,
    setContext,
    clearContext,
    addArtifact,
    artifactsForLearner,
    resetSessionArtifacts,
  }
})
