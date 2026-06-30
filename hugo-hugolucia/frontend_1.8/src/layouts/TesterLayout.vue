<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useTenantStore } from '../stores/tenant'
import OrgTenantSwitcher from '../components/admin/OrgTenantSwitcher.vue'
import PlatformVersionFooter from '../components/PlatformVersionFooter.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const tenant = useTenantStore()

const showNavbar = computed(() => !route.meta.public && auth.user)
const isAdmin = computed(() => auth.isAdminLike)
const isSuperAdminUser = computed(() => auth.isSuperAdmin)

const activeOrgLabel = computed(() => {
  if (auth.isSuperAdmin && tenant.activeOrganisationName) {
    return tenant.activeOrganisationName
  }
  return auth.user?.organisation_name || ''
})

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="d-flex flex-column min-vh-100">
    <nav v-if="showNavbar" class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container-fluid">
        <router-link class="navbar-brand" to="/dashboard">POC Hugo</router-link>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div id="navbarNav" class="collapse navbar-collapse">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/dashboard">Tableau de bord</router-link>
            </li>
            <li class="nav-item">
              <router-link v-if="auth.isOrgAdminLike" class="nav-link" to="/referentials">Référentiels</router-link>
            </li>
            <li v-if="isSuperAdminUser" class="nav-item">
              <router-link class="nav-link" to="/admin/organisations">Organisations</router-link>
            </li>
            <li v-if="isAdmin" class="nav-item">
              <router-link class="nav-link" to="/admin/conversation">Config. conversation</router-link>
            </li>
            <li v-if="isAdmin" class="nav-item">
              <router-link class="nav-link" to="/groups-admin">Groupes</router-link>
            </li>
            <li v-if="isAdmin" class="nav-item">
              <router-link class="nav-link" to="/ovh-llms">OVH LLM</router-link>
            </li>
            <li v-if="isAdmin" class="nav-item">
              <router-link class="nav-link" to="/users">Utilisateurs</router-link>
            </li>
          </ul>
          <ul class="navbar-nav align-items-lg-center">
            <OrgTenantSwitcher />
            <li class="nav-item dropdown">
              <a
                class="nav-link dropdown-toggle"
                href="#"
                role="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
              >
                {{ auth.user?.username }}
                <span v-if="activeOrgLabel"> — {{ activeOrgLabel }}</span>
                <span v-if="isSuperAdminUser" class="badge text-bg-warning ms-1">SUPERADMIN</span>
                <span v-else-if="isAdmin" class="badge text-bg-light ms-1">ORGADMIN</span>
              </a>
              <ul class="dropdown-menu dropdown-menu-end">
                <li><a class="dropdown-item" href="#" @click.prevent="logout">Déconnexion</a></li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <main class="flex-grow-1 p-3">
      <slot />
    </main>

    <PlatformVersionFooter />
  </div>
</template>
