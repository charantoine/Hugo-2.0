/** Shared completeness helpers for LearnerConversationGlobalProfile (list + group admin badge). */

export function completenessBadgeClass(profile) {
  const score = Number(profile?.completeness?.score ?? 0)
  if (score >= 0.85) return 'text-bg-success'
  if (score >= 0.5) return 'text-bg-warning'
  return 'text-bg-secondary'
}

export function completenessLabel(profile) {
  const filled = profile?.completeness?.filled
  const total = profile?.completeness?.total
  if (filled == null || total == null) return '—'
  return `${filled}/${total}`
}

export const COMPLETENESS_LEGEND =
  '7 slots : 3 prompts orchestrateur, 3 profils de conduite, 1 profil d’évaluation (+ politique optionnelle).'

export function conversationConfigBadge(group, selectedProfileId, learnerProfiles, selectedTutorPromptId) {
  const profile = selectedProfileId
    ? learnerProfiles.find((p) => String(p.id) === String(selectedProfileId))
    : null
  if (profile) {
    const filled = profile.completeness?.filled
    const total = profile.completeness?.total ?? 7
    if (filled != null && total != null && filled >= total) {
      return {
        class: 'text-bg-success',
        text: `Profil ${profile.name} — complet ${filled}/${total}`,
      }
    }
    return { class: 'text-bg-warning', text: '⚠ Profil global incomplet' }
  }
  if (selectedTutorPromptId || group?.default_tutor_prompt) {
    return { class: 'text-bg-warning', text: '⚠ Fallback tutor prompt legacy' }
  }
  return { class: 'text-bg-secondary', text: 'Conversation non configurée' }
}
