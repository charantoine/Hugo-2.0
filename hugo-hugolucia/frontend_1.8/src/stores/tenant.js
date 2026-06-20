import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'
import { isSuperAdmin } from '../utils/roleGuards'

const STORAGE_KEY = 'hugo_active_organisation_id'

export const useTenantStore = defineStore('tenant', () => {
  const activeOrganisationId = ref(localStorage.getItem(STORAGE_KEY) || '')
  const activeOrganisationName = ref('')

  const hasActiveOrganisation = computed(() => Boolean(activeOrganisationId.value))

  function syncFromUser(user) {
    if (!user) {
      clearTenant()
      return
    }
    if (!isSuperAdmin(user)) {
      activeOrganisationId.value = user.organisation_id || ''
      activeOrganisationName.value = user.organisation_name || ''
      return
    }
    if (!activeOrganisationId.value) {
      activeOrganisationId.value = user.organisation_id || ''
      activeOrganisationName.value = user.organisation_name || ''
    }
  }

  function setActiveOrganisation(org) {
    if (!org?.id) return
    activeOrganisationId.value = String(org.id)
    activeOrganisationName.value = org.name || ''
    localStorage.setItem(STORAGE_KEY, activeOrganisationId.value)
  }

  function clearTenant() {
    activeOrganisationId.value = ''
    activeOrganisationName.value = ''
    localStorage.removeItem(STORAGE_KEY)
  }

  watch(activeOrganisationId, (value) => {
    if (value) localStorage.setItem(STORAGE_KEY, value)
    else localStorage.removeItem(STORAGE_KEY)
  })

  return {
    activeOrganisationId,
    activeOrganisationName,
    hasActiveOrganisation,
    syncFromUser,
    setActiveOrganisation,
    clearTenant,
  }
})
