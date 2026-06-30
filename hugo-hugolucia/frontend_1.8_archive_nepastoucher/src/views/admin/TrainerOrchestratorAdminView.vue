<script setup>
/**
 * Phase 1 — Orchestrateur formateur : sépare base de connaissances (existant) de la config conversationnelle (future).
 */
</script>

<template>
  <div class="container-fluid">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item"><router-link to="/dashboard">Tableau de bord</router-link></li>
        <li class="breadcrumb-item"><router-link to="/admin/conversation">Configuration conversation</router-link></li>
        <li class="breadcrumb-item active" aria-current="page">Orchestrateur formateur</li>
      </ol>
    </nav>

    <header class="mb-4">
      <h1 class="h4 mb-1">Formateur — Orchestrateur</h1>
      <p class="text-muted mb-0">
        Préparation et validation du matériau pédagogique exploitable par les orchestrateurs apprenant.
      </p>
    </header>

    <div class="alert alert-info small">
      <strong>Phase 1 :</strong> le workflow formateur prod (connaissances, élicitation) est opérationnel.
      La configuration conversationnelle héritée (prompts formateur) n’existe pas encore en backend.
    </div>

    <div class="row g-3">
      <div class="col-md-6">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h2 class="h6">Base de connaissances</h2>
            <p class="small text-muted">Validation, rejet, items exploitables par le moteur.</p>
            <router-link to="/app/trainer/knowledge" class="btn btn-sm btn-outline-primary">
              Ouvrir /app/trainer/knowledge
            </router-link>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h2 class="h6">Atelier d’élicitation</h2>
            <p class="small text-muted">Questions → items déclarés (V0 cluster 15).</p>
            <router-link to="/app/trainer/elicitation" class="btn btn-sm btn-outline-primary">
              Ouvrir /app/trainer/elicitation
            </router-link>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h2 class="h6">Documents &amp; RAG (groupe)</h2>
            <p class="small text-muted">Upload et indexation — admin groupe testeur.</p>
            <router-link to="/groups-admin" class="btn btn-sm btn-outline-secondary">Admin groupes</router-link>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h2 class="h6">Directives formateur (évaluation)</h2>
            <p class="small text-muted">Champ <code>trainer_directives</code> sur la politique d’évaluation.</p>
            <router-link to="/admin/conversation/learner/closing" class="btn btn-sm btn-outline-secondary">
              Clôture &amp; évaluation
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
