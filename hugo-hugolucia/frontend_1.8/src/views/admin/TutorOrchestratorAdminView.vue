<script setup>
/**
 * Phase 1 — Orchestrateur tuteur : hub de liens + périmètre documenté.
 * Arbitrage produit requis avant config prompts tuteur (cible 2.0 = lecture/interprétation).
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
        Couche d’accompagnement humain : progression, traces partagées, signaux — sans pilotage direct du moteur apprenant.
      </p>
    </header>

    <div class="alert alert-warning small">
      <strong>Phase 1 :</strong> pas de modèle backend « orchestrateur tuteur » configurable (prompts/comportement).
      La cible 2.0 privilégie la lecture et l’interprétation. Arbitrage produit nécessaire avant Phase 2.
    </div>

    <div class="row g-3">
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
            <h2 class="h6">Espace testeur</h2>
            <p class="small text-muted">Timeline apprenant, traces, calibration (mode testeur).</p>
            <router-link to="/dashboard" class="btn btn-sm btn-outline-secondary">Dashboard testeur</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
