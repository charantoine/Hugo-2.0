import { computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useTenantStore } from '../stores/tenant'

/** Libellé harmonisé de l’organisation active (tenant store + fallback user). */
export function useActiveOrganisationLabel() {
  const auth = useAuthStore()
  const tenant = useTenantStore()

  const label = computed(() => {
    if (tenant.activeOrganisationName) return tenant.activeOrganisationName
    return auth.user?.organisation_name || '—'
  })

  return { label, tenant, auth }
}
