import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api/client'
import {
  pickDefaultGroupId,
  summarizeMemberships,
  summarizeReferentialConfig,
} from '../utils/trainerGroupContext'

/**
 * Contexte groupe formateur : groupes visibles, référentiel lié, effectif.
 * S’appuie sur GET /groups/, /groups/{id}/referential-config/, /groups/{id}/members/.
 */
export function useTrainerGroupContext() {
  const route = useRoute()
  const router = useRouter()

  const groups = ref([])
  const groupId = ref('')
  const referentialConfig = ref(null)
  const members = ref([])
  const loading = ref(false)
  const error = ref('')

  const selectedGroup = computed(() => (
    groups.value.find((group) => String(group.id) === String(groupId.value)) || null
  ))

  const referentialSummary = computed(() => summarizeReferentialConfig(referentialConfig.value))

  const membershipSummary = computed(() => summarizeMemberships(members.value))

  async function loadGroupDetails() {
    if (!groupId.value) {
      referentialConfig.value = null
      members.value = []
      return
    }
    const [configRes, membersRes] = await Promise.all([
      api.get(`/groups/${groupId.value}/referential-config/`),
      api.get(`/groups/${groupId.value}/members/`),
    ])
    referentialConfig.value = configRes.data
    const rawMembers = membersRes.data
    members.value = Array.isArray(rawMembers) ? rawMembers : (rawMembers?.results || [])
  }

  async function loadGroups() {
    const { data } = await api.get('/groups/')
    groups.value = Array.isArray(data) ? data : (data.results || [])
    groupId.value = pickDefaultGroupId(groups.value, route.query.groupId)
  }

  async function refresh() {
    loading.value = true
    error.value = ''
    try {
      await loadGroups()
      await loadGroupDetails()
    } catch (err) {
      error.value = err.response?.data?.detail || 'Impossible de charger le contexte groupe.'
      groups.value = []
      groupId.value = ''
      referentialConfig.value = null
      members.value = []
    } finally {
      loading.value = false
    }
  }

  async function setGroupId(nextId) {
    groupId.value = String(nextId || '')
    await router.replace({
      query: {
        ...route.query,
        groupId: groupId.value || undefined,
      },
    })
    await loadGroupDetails()
  }

  return {
    groups,
    groupId,
    selectedGroup,
    referentialConfig,
    referentialSummary,
    members,
    membershipSummary,
    loading,
    error,
    refresh,
    setGroupId,
    loadGroupDetails,
  }
}
