<script setup>
/**
 * Pass 2 — hub orchestrateur tuteur avec lien vers profils persona.
 */
</script>

<template>
  <div class="container-fluid">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item"><router-link to="/dashboard">Tableau de bord</router-link></li>
        <li class="breadcrumb-item"><router-link to="/admin/conversation">Configuration conversation</router-link></li>
        <li class="breadcrumb-item active" aria-current="page">Orchestrateur tuteur</li>
      </ol>
    </nav>

    <header class="mb-4">
      <h1 class="h4 mb-1">Tuteur — Orchestrateur</h1>
      <p class="text-muted mb-0">
        Profils conversationnels persona tuteur (templates system/user) — hors périmètre apprenant.
      </p>
    </header>

    <div class="alert alert-info small">
      <strong>Pass 2 (baseline B) :</strong> configuration des profils persona tuteur via l’admin.
      Le moteur apprenant et les profils <code>LearnerConversationGlobalProfile</code> ne sont pas modifiés.
    </div>

    <div class="row g-3">
      <div class="col-md-6">
        <div class="card shadow-sm h-100 border-primary">
          <div class="card-body">
            <h2 class="h6">Profils conversationnels tuteur</h2>
            <p class="small text-muted">CRUD, duplication, archivage, prévisualisation sans LLM.</p>
            <router-link to="/admin/conversation/tutor/profiles" class="btn btn-sm btn-primary">
              Gérer les profils tuteur
            </router-link>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h2 class="h6">Espace tuteur (prod)</h2>
            <p class="small text-muted">Suivi apprenants, traces partagées — opérationnel.</p>
            <router-link to="/app/tutor" class="btn btn-sm btn-outline-primary">Ouvrir /app/tutor</router-link>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h2 class="h6">Politique d’évaluation</h2>
            <p class="small text-muted">Partage tuteur, validation — configurable côté clôture apprenant.</p>
            <router-link to="/admin/conversation/learner/closing" class="btn btn-sm btn-outline-secondary">
              Clôture &amp; évaluation
            </router-link>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h2 class="h6">Legacy prompts apprenant</h2>
            <p class="small text-muted">TutorPrompt apprenant (ne pas confondre avec profils persona).</p>
            <router-link to="/tutor-prompts" class="btn btn-sm btn-outline-secondary">Prompts legacy</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
