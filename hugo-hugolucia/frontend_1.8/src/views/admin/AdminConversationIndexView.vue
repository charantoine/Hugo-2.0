<script setup>
import { ADMIN_CONVERSATION_SECTIONS, LEGACY_ADMIN_ROUTES } from '../../constants/adminConversationModes'
</script>

<template>
  <div class="container-fluid">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item"><router-link to="/dashboard">Tableau de bord</router-link></li>
        <li class="breadcrumb-item active" aria-current="page">Configuration conversation</li>
      </ol>
    </nav>

    <header class="mb-4">
      <h1 class="h4 mb-1">Configuration conversationnelle</h1>
      <p class="text-muted mb-0">
        Pilotage métier des orchestrateurs apprenant, tuteur et formateur — distinct des écrans techniques legacy.
      </p>
    </header>

    <div v-for="section in ADMIN_CONVERSATION_SECTIONS" :key="section.id" class="mb-4">
      <h2 class="h5 mb-3">{{ section.title }}</h2>
      <div class="row g-3">
        <div v-for="item in section.items" :key="item.path" class="col-12 col-md-6 col-xl-4">
          <router-link :to="item.path" class="text-decoration-none">
            <div class="card shadow-sm h-100 admin-conversation-card">
              <div class="card-body">
                <h3 class="h6 mb-2 text-primary">{{ item.label }}</h3>
                <p class="small text-muted mb-0">{{ item.description }}</p>
              </div>
            </div>
          </router-link>
        </div>
      </div>
    </div>

    <div class="card shadow-sm border-secondary">
      <div class="card-body">
        <h2 class="h6 mb-2">Accès legacy (compatibilité)</h2>
        <p class="small text-muted mb-2">Conservés temporairement — seront dépréciés après Phase 2.</p>
        <ul class="list-inline mb-0 small">
          <li v-for="route in LEGACY_ADMIN_ROUTES" :key="route.path" class="list-inline-item me-3">
            <router-link :to="route.path">{{ route.label }}</router-link>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-conversation-card {
  transition: box-shadow 0.15s ease;
}
.admin-conversation-card:hover {
  box-shadow: 0 0.25rem 0.75rem rgba(0, 0, 0, 0.1) !important;
}
</style>
