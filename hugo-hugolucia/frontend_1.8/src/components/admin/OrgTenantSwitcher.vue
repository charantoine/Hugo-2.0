<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import api from '../../api/client'
import { useAuthStore } from '../../stores/auth'
import { useTenantStore } from '../../stores/tenant'

const auth = useAuthStore()
const tenant = useTenantStore()

const organisations = ref([])
const loading = ref(false)

const selectedId = computed({
  get: () => tenant.activeOrganisationId,
  set: (value) => {
    const org = organisations.value.find((item) => String(item.id) === String(value))
    if (org) tenant.setActiveOrganisation(org)
  },
})

async function loadOrganisations() {
  if (!auth.isSuperAdmin) return
  loading.value = true
  try {
    const { data } = await api.get('/admin/organisations/')
    organisations.value = Array.isArray(data) ? data : (data.results || [])
    if (!tenant.activeOrganisationId && organisations.value.length) {
      tenant.setActiveOrganisation(organisations.value[0])
    } else if (tenant.activeOrganisationId) {
      const current = organisations.value.find(
        (item) => String(item.id) === String(tenant.activeOrganisationId),
      )
      if (current) tenant.setActiveOrganisation(current)
    }
  } finally {
    loading.value = false
  }
}

function onSwitch() {
  window.location.reload()
}

watch(
  () => auth.user,
  (user) => {
    if (user) tenant.syncFromUser(user)
  },
  { immediate: true },
)

onMounted(loadOrganisations)
</script>

<template>
  <div v-if="auth.isSuperAdmin" class="d-flex align-items-center gap-2 me-3">
    <label class="small text-white-50 mb-0" for="tenant-switcher">Organisation active</label>
    <select
      id="tenant-switcher"
      v-model="selectedId"
      class="form-select form-select-sm"
      style="min-width: 220px"
      :disabled="loading || !organisations.length"
      @change="onSwitch"
    >
      <option v-for="org in organisations" :key="org.id" :value="org.id">
        {{ org.name }}
      </option>
    </select>
  </div>
</template>
