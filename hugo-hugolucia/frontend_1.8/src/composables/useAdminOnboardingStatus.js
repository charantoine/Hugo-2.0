import { ref, computed, watch } from 'vue'
import api from '../api/client'
import { useAuthStore } from '../stores/auth'
import { useTenantStore } from '../stores/tenant'
import { useActiveOrganisationLabel } from './useActiveOrganisationLabel'
import { conversationConfigBadge } from '../utils/learnerProfileCompleteness'

export const STEP_STATUS = {
  OK: 'ok',
  TO_CONFIGURE: 'to_configure',
  INCOMPLETE: 'incomplete',
  FALLBACK: 'fallback',
}

const USEFUL_ROLES = ['LEARNER', 'TUTOR', 'TRAINER']

function listFromResponse(data) {
  return Array.isArray(data) ? data : (data?.results ?? [])
}

function countByRole(users) {
  const counts = { LEARNER: 0, TUTOR: 0, TRAINER: 0 }
  for (const u of users) {
    if (u?.is_active === false) continue
    const role = u.role
    if (role in counts) counts[role] += 1
  }
  return counts
}

function mapConversationStatus(badge) {
  if (!badge) return { status: STEP_STATUS.TO_CONFIGURE, label: 'À configurer' }
  if (badge.class === 'text-bg-success') {
    return { status: STEP_STATUS.OK, label: 'OK' }
  }
  if (badge.text?.includes('Fallback') || badge.text?.includes('legacy')) {
    return { status: STEP_STATUS.FALLBACK, label: 'Attention fallback' }
  }
  if (badge.class === 'text-bg-warning') {
    return { status: STEP_STATUS.INCOMPLETE, label: 'Incomplet' }
  }
  return { status: STEP_STATUS.TO_CONFIGURE, label: 'À configurer' }
}

/**
 * Lecture seule — agrège l’état d’onboarding admin (org active + groupe sélectionné).
 * @param {import('vue').Ref<string>} selectedGroupId — ID du groupe choisi dans le wizard
 */
export function useAdminOnboardingStatus(selectedGroupId) {
  const auth = useAuthStore()
  const tenant = useTenantStore()
  const { label: activeOrganisationLabel } = useActiveOrganisationLabel()

  const loading = ref(false)
  const error = ref('')
  const users = ref([])
  const groups = ref([])
  const focusGroup = ref(null)
  const focusGroupMembers = ref([])
  const learnerProfiles = ref([])
  const referentialConfig = ref(null)

  const roleCounts = computed(() => countByRole(users.value))

  const accountsStep = computed(() => {
    const counts = roleCounts.value
    const missing = USEFUL_ROLES.filter((r) => counts[r] < 1)
    const total = USEFUL_ROLES.reduce((n, r) => n + counts[r], 0)
    let status = STEP_STATUS.OK
    let summary = `${counts.LEARNER} apprenant(s), ${counts.TUTOR} tuteur(s), ${counts.TRAINER} formateur(s).`
    if (total === 0) {
      status = STEP_STATUS.TO_CONFIGURE
      summary = 'Aucun compte apprenant, tuteur ou formateur trouvé.'
    } else if (missing.length) {
      status = STEP_STATUS.INCOMPLETE
      const labels = { LEARNER: 'apprenant', TUTOR: 'tuteur', TRAINER: 'formateur' }
      summary += ` Manque : ${missing.map((r) => labels[r]).join(', ')}.`
    }
    return {
      id: 'accounts',
      title: 'Comptes',
      status,
      statusLabel: statusLabel(status),
      summary,
      ctaLabel: 'Gérer les utilisateurs',
      ctaTo: '/users',
    }
  })

  const groupStep = computed(() => {
    if (!groups.value.length) {
      return {
        id: 'group',
        title: 'Groupe',
        status: STEP_STATUS.TO_CONFIGURE,
        statusLabel: statusLabel(STEP_STATUS.TO_CONFIGURE),
        summary: 'Aucun groupe dans cette organisation.',
        groupName: null,
        ctaLabel: 'Créer un groupe',
        ctaTo: '/groups-admin',
      }
    }
    const g = focusGroup.value
    const memberCount = focusGroupMembers.value.length
    if (!g) {
      return {
        id: 'group',
        title: 'Groupe',
        status: STEP_STATUS.TO_CONFIGURE,
        statusLabel: statusLabel(STEP_STATUS.TO_CONFIGURE),
        summary: 'Sélectionnez un groupe à configurer.',
        groupName: null,
        ctaLabel: 'Gérer les groupes',
        ctaTo: '/groups-admin',
      }
    }
    if (memberCount === 0) {
      return {
        id: 'group',
        title: 'Groupe',
        status: STEP_STATUS.INCOMPLETE,
        statusLabel: statusLabel(STEP_STATUS.INCOMPLETE),
        summary: `Groupe « ${g.name} » créé mais sans membres.`,
        groupName: g.name,
        ctaLabel: 'Gérer le groupe',
        ctaTo: `/groups-admin/${g.id}`,
      }
    }
    return {
      id: 'group',
      title: 'Groupe',
      status: STEP_STATUS.OK,
      statusLabel: statusLabel(STEP_STATUS.OK),
      summary: `Groupe « ${g.name} » — ${memberCount} membre(s).`,
      groupName: g.name,
      ctaLabel: 'Gérer le groupe',
      ctaTo: `/groups-admin/${g.id}`,
    }
  })

  const conversationStep = computed(() => {
    const g = focusGroup.value
    if (!groups.value.length) {
      return {
        id: 'conversation',
        title: 'Conversation apprenant',
        status: STEP_STATUS.TO_CONFIGURE,
        statusLabel: statusLabel(STEP_STATUS.TO_CONFIGURE),
        summary: 'Créez d’abord un groupe dans cette organisation.',
        profileName: null,
        completeness: null,
        ctaLabel: 'Créer un groupe',
        ctaTo: '/groups-admin',
      }
    }
    if (!g) {
      return {
        id: 'conversation',
        title: 'Conversation apprenant',
        status: STEP_STATUS.TO_CONFIGURE,
        statusLabel: statusLabel(STEP_STATUS.TO_CONFIGURE),
        summary: 'Sélectionnez un groupe à configurer.',
        profileName: null,
        completeness: null,
        ctaLabel: 'Attribuer le profil au groupe',
        ctaTo: '/groups-admin',
        secondaryCtaLabel: 'Créer ou éditer un profil',
        secondaryCtaTo: '/admin/conversation/learner/profiles',
      }
    }
    const profileId = g.default_learner_conversation_profile
    const profile = profileId
      ? learnerProfiles.value.find((p) => String(p.id) === String(profileId))
      : null
    const badge = conversationConfigBadge(
      g,
      profileId,
      learnerProfiles.value,
      g.default_tutor_prompt,
    )
    const { status, label } = mapConversationStatus(badge)
    let summary = badge?.text || 'Conversation non configurée.'
    if (profile) {
      const filled = profile.completeness?.filled
      const total = profile.completeness?.total ?? 7
      summary = `Profil « ${profile.name} » — complétude ${filled ?? '?'}/${total}.`
      if (status === STEP_STATUS.FALLBACK) {
        summary += ' Mode fallback legacy (TutorPrompt) détecté.'
      }
    } else if (g.default_tutor_prompt) {
      summary = 'Aucun profil global ; fallback TutorPrompt legacy actif.'
    }
    return {
      id: 'conversation',
      title: 'Conversation apprenant',
      status,
      statusLabel: label,
      summary,
      profileName: profile?.name ?? null,
      completeness: profile ? `${profile.completeness?.filled ?? '?'}/${profile.completeness?.total ?? 7}` : null,
      ctaLabel: 'Attribuer le profil au groupe',
      ctaTo: `/groups-admin/${g.id}?section=conversation`,
      secondaryCtaLabel: 'Créer ou éditer un profil',
      secondaryCtaTo: `/admin/conversation/learner/profiles?groupId=${g.id}`,
    }
  })

  const referentialStep = computed(() => {
    const g = focusGroup.value
    const ref = referentialConfig.value?.referential
    if (!groups.value.length) {
      return {
        id: 'referential',
        title: 'Référentiel',
        status: STEP_STATUS.TO_CONFIGURE,
        statusLabel: statusLabel(STEP_STATUS.TO_CONFIGURE),
        summary: 'Créez d’abord un groupe dans cette organisation.',
        referentialName: null,
        ctaLabel: 'Créer un groupe',
        ctaTo: '/groups-admin',
      }
    }
    if (!g) {
      return {
        id: 'referential',
        title: 'Référentiel',
        status: STEP_STATUS.TO_CONFIGURE,
        statusLabel: statusLabel(STEP_STATUS.TO_CONFIGURE),
        summary: 'Sélectionnez un groupe à configurer.',
        referentialName: null,
        ctaLabel: 'Associer un référentiel',
        ctaTo: '/referentials',
      }
    }
    if (!ref) {
      return {
        id: 'referential',
        title: 'Référentiel',
        status: STEP_STATUS.TO_CONFIGURE,
        statusLabel: statusLabel(STEP_STATUS.TO_CONFIGURE),
        summary: `Aucun référentiel associé au groupe « ${g.name} ».`,
        referentialName: null,
        ctaLabel: 'Associer un référentiel',
        ctaTo: `/group/${g.id}/referential`,
      }
    }
    return {
      id: 'referential',
      title: 'Référentiel',
      status: STEP_STATUS.OK,
      statusLabel: statusLabel(STEP_STATUS.OK),
      summary: `Référentiel associé : ${ref.name}${ref.source_ref ? ` (${ref.source_ref})` : ''}.`,
      referentialName: ref.name,
      ctaLabel: 'Associer un référentiel',
      ctaTo: `/group/${g.id}/referential`,
    }
  })

  const steps = computed(() => [
    accountsStep.value,
    groupStep.value,
    conversationStep.value,
    referentialStep.value,
  ])

  const completedCount = computed(
    () => steps.value.filter((s) => s.status === STEP_STATUS.OK).length,
  )

  const progressPercent = computed(() => Math.round((completedCount.value / 4) * 100))

  async function loadGroupDetails(groupId) {
    focusGroupMembers.value = []
    referentialConfig.value = null
    focusGroup.value = null
    if (!groupId) return

    const listItem = groups.value.find((g) => String(g.id) === String(groupId))
    const [membersRes, refRes, groupDetail] = await Promise.all([
      api.get(`/groups/${groupId}/members/`).catch(() => ({ data: [] })),
      api.get(`/groups/${groupId}/referential-config/`).catch(() => ({ data: null })),
      api.get(`/groups/${groupId}/`).catch(() => null),
    ])
    focusGroupMembers.value = listFromResponse(membersRes.data)
    referentialConfig.value = refRes.data?.referential ? refRes.data : null
    focusGroup.value = groupDetail?.data
      ? { ...listItem, ...groupDetail.data }
      : listItem || null
  }

  async function refresh() {
    loading.value = true
    error.value = ''
    try {
      const [usersRes, groupsRes, profilesRes] = await Promise.all([
        api.get('/users/'),
        api.get('/groups/'),
        api.get('/hugo/learner-conversation-profiles/').catch(() => ({ data: [] })),
      ])
      users.value = listFromResponse(usersRes.data)
      groups.value = listFromResponse(groupsRes.data)
      learnerProfiles.value = listFromResponse(profilesRes.data)

      const currentId = selectedGroupId?.value
      const stillValid = currentId && groups.value.some((g) => String(g.id) === String(currentId))
      if (!stillValid && groups.value.length) {
        selectedGroupId.value = String(groups.value[0].id)
      } else if (!groups.value.length) {
        selectedGroupId.value = ''
      }

      await loadGroupDetails(selectedGroupId?.value)
    } catch (e) {
      error.value = e.response?.data?.detail || 'Impossible de charger l’état d’onboarding.'
    } finally {
      loading.value = false
    }
  }

  watch(
    () => tenant.activeOrganisationId,
    () => {
      selectedGroupId.value = ''
      refresh()
    },
  )

  watch(
    () => selectedGroupId?.value,
    async (groupId) => {
      if (loading.value) return
      await loadGroupDetails(groupId)
    },
  )

  return {
    loading,
    error,
    activeOrganisationLabel,
    groups,
    focusGroup,
    steps,
    completedCount,
    progressPercent,
    refresh,
    loadGroupDetails,
  }
}

export function statusLabel(status) {
  switch (status) {
    case STEP_STATUS.OK:
      return 'OK'
    case STEP_STATUS.INCOMPLETE:
      return 'Incomplet'
    case STEP_STATUS.FALLBACK:
      return 'Attention fallback'
    default:
      return 'À configurer'
  }
}

export function statusBadgeClass(status) {
  switch (status) {
    case STEP_STATUS.OK:
      return 'text-bg-success'
    case STEP_STATUS.INCOMPLETE:
      return 'text-bg-warning'
    case STEP_STATUS.FALLBACK:
      return 'text-bg-warning'
    default:
      return 'text-bg-secondary'
  }
}
