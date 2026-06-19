<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const showNavbar = computed(() => !route.meta.public && auth.user)
const isAdmin = computed(() => auth.isAdminLike)

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
              <router-link class="nav-link" to="/referentials">Référentiels</router-link>
            </li>
            <li v-if="isAdmin" class="nav-item">
              <router-link class="nav-link" to="/groups-admin">Groupes</router-link>
            </li>
            <li v-if="isAdmin" class="nav-item">
              <router-link class="nav-link" to="/tutor-prompts">Prompts tuteur</router-link>
            </li>
            <li v-if="isAdmin" class="nav-item">
              <router-link class="nav-link" to="/ovh-llms">OVH LLM</router-link>
            </li>
            <li v-if="isAdmin" class="nav-item">
              <router-link class="nav-link" to="/users">Utilisateurs</router-link>
            </li>
          </ul>
          <ul class="navbar-nav">
            <li class="nav-item dropdown">
              <a
                class="nav-link dropdown-toggle"
                href="#"
                role="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
              >
                {{ auth.user?.username }} — {{ auth.user?.organisation_name }}
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
  </div>
</template>
