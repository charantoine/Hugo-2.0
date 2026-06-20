<script setup>
import { onMounted, ref } from 'vue'
import api from '../../api/client'

const profiles = ref([])
const policies = ref([])
const loading = ref(false)
const error = ref('')
const success = ref('')
const savingProfileId = ref('')
const savingPolicyId = ref('')

const SYNTHESIS_NOTE =
  'Les prompts de synthèse sont encore codés en dur dans synthesis_service.py — édition admin prévue Phase 3.'

async function loadAll() {
  loading.value = true
  error.value = ''
  try {
    const [profilesResp, policiesResp] = await Promise.all([
      api.get('/hugo/evaluation-prompt-profiles/'),
      api.get('/hugo/evaluation-policies/'),
    ])
    profiles.value = Array.isArray(profilesResp.data) ? profilesResp.data : (profilesResp.data.results || [])
    policies.value = Array.isArray(policiesResp.data) ? policiesResp.data : (policiesResp.data.results || [])
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors du chargement de la configuration clôture / évaluation.'
  } finally {
    loading.value = false
  }
}

async function saveProfile(profile) {
  if (!profile?.id || savingProfileId.value) return
  savingProfileId.value = profile.id
  error.value = ''
  success.value = ''
  try {
    await api.patch(`/hugo/evaluation-prompt-profiles/${profile.id}/`, {
      label: profile.label,
      is_active: profile.is_active,
      prompt_frame: profile.prompt_frame,
      prompt_judgement_guide: profile.prompt_judgement_guide,
      prompt_output_guide: profile.prompt_output_guide,
      max_dialogue_turns: profile.max_dialogue_turns,
      ask_learner_confirmation: profile.ask_learner_confirmation,
      human_validation_required: profile.human_validation_required,
    })
    success.value = `Profil « ${profile.code} » enregistré.`
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors de la sauvegarde du profil.'
  } finally {
    savingProfileId.value = ''
  }
}

async function createOrgProfile() {
  error.value = ''
  success.value = ''
  try {
    await api.post('/hugo/evaluation-prompt-profiles/', {
      code: 'default',
      label: 'Profil évaluation organisation',
      is_active: true,
      prompt_frame: "Tu es en phase d'évaluation réflexive avec l'apprenant.",
      prompt_judgement_guide: 'Classe prudemment chaque critère.',
      prompt_output_guide: 'Retourne un JSON structuré avec recap_text et items.',
      max_dialogue_turns: 6,
      ask_learner_confirmation: true,
      human_validation_required: true,
    })
    success.value = 'Profil d’évaluation créé.'
    await loadAll()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Impossible de créer le profil (code peut-être déjà utilisé).'
  }
}

async function savePolicy(policy) {
  if (!policy?.id || savingPolicyId.value) return
  savingPolicyId.value = policy.id
  error.value = ''
  success.value = ''
  try {
    await api.patch(`/hugo/evaluation-policies/${policy.id}/`, {
      share_with_tutor: policy.share_with_tutor,
      tutor_validation_required: policy.tutor_validation_required,
      allow_early_trigger: policy.allow_early_trigger,
      early_trigger_warning: policy.early_trigger_warning,
      evaluation_profile_code: policy.evaluation_profile_code,
      trainer_directives: policy.trainer_directives,
    })
    success.value = 'Politique d’évaluation enregistrée.'
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erreur lors de la sauvegarde de la politique.'
  } finally {
    savingPolicyId.value = ''
  }
}

async function createOrgPolicy() {
  error.value = ''
  success.value = ''
  try {
    await api.post('/hugo/evaluation-policies/', {
      share_with_tutor: true,
      tutor_validation_required: false,
      allow_early_trigger: true,
      early_trigger_warning: "La conversation n'est pas encore suffisamment mûre. L'évaluation sera partielle.",
      evaluation_profile_code: 'default',
      trainer_directives: '',
    })
    success.value = 'Politique d’évaluation créée.'
    await loadAll()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Impossible de créer la politique.'
  }
}

onMounted(loadAll)
</script>

<template>
  <div class="container-fluid">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item"><router-link to="/dashboard">Tableau de bord</router-link></li>
        <li class="breadcrumb-item"><router-link to="/admin/conversation">Configuration conversation</router-link></li>
        <li class="breadcrumb-item active" aria-current="page">Clôture évaluation</li>
      </ol>
    </nav>

    <header class="mb-4">
      <h1 class="h4 mb-1">Apprenant — Clôture &amp; évaluation</h1>
      <p class="text-muted mb-0">
        Branche terminale : profils de prompt d’évaluation et politique organisationnelle.
        Distinct des postures de séance (diagnostic, réflexif, bâchage).
      </p>
    </header>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>
    <div v-if="loading" class="text-muted">Chargement…</div>

    <template v-else>
      <div class="alert alert-info small">{{ SYNTHESIS_NOTE }}</div>

      <section class="mb-4">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h2 class="h5 mb-0">Profils d’évaluation (prompts)</h2>
          <button type="button" class="btn btn-sm btn-outline-primary" @click="createOrgProfile">
            Créer profil org (default)
          </button>
        </div>
        <div v-if="profiles.length" class="row g-3">
          <div v-for="profile in profiles" :key="profile.id" class="col-12">
            <div class="card shadow-sm">
              <div class="card-body">
                <div class="d-flex justify-content-between mb-2">
                  <div>
                    <strong>{{ profile.label }}</strong>
                    <span class="badge text-bg-light border ms-2">{{ profile.code }}</span>
                    <span v-if="!profile.organisation" class="badge text-bg-secondary ms-1">système</span>
                  </div>
                  <div class="form-check">
                    <input :id="`active-${profile.id}`" v-model="profile.is_active" class="form-check-input" type="checkbox">
                    <label class="form-check-label small" :for="`active-${profile.id}`">Actif</label>
                  </div>
                </div>
                <div class="row g-2">
                  <div class="col-12">
                    <label class="form-label small">Cadre (prompt_frame)</label>
                    <textarea v-model="profile.prompt_frame" class="form-control form-control-sm" rows="2" :disabled="!profile.organisation" />
                  </div>
                  <div class="col-md-6">
                    <label class="form-label small">Guide jugement</label>
                    <textarea v-model="profile.prompt_judgement_guide" class="form-control form-control-sm" rows="3" :disabled="!profile.organisation" />
                  </div>
                  <div class="col-md-6">
                    <label class="form-label small">Guide sortie JSON</label>
                    <textarea v-model="profile.prompt_output_guide" class="form-control form-control-sm" rows="3" :disabled="!profile.organisation" />
                  </div>
                </div>
                <p v-if="!profile.organisation" class="small text-muted mt-2 mb-0">Profil système — lecture seule (SUPERADMIN Django admin pour modification globale).</p>
                <button
                  v-else
                  type="button"
                  class="btn btn-sm btn-primary mt-2"
                  :disabled="savingProfileId === profile.id"
                  @click="saveProfile(profile)"
                >
                  Enregistrer
                </button>
              </div>
            </div>
          </div>
        </div>
        <p v-else class="text-muted small">Aucun profil en base — les fallbacks statiques du moteur s’appliquent.</p>
      </section>

      <section>
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h2 class="h5 mb-0">Politique d’évaluation (organisation)</h2>
          <button type="button" class="btn btn-sm btn-outline-primary" @click="createOrgPolicy">
            Créer politique org
          </button>
        </div>
        <div v-for="policy in policies" :key="policy.id" class="card shadow-sm mb-3">
          <div class="card-body">
            <div class="row g-2">
              <div class="col-md-6">
                <label class="form-label small">Code profil d’évaluation</label>
                <input v-model="policy.evaluation_profile_code" type="text" class="form-control form-control-sm">
              </div>
              <div class="col-md-6">
                <label class="form-label small">Avertissement early trigger</label>
                <input v-model="policy.early_trigger_warning" type="text" class="form-control form-control-sm">
              </div>
              <div class="col-12">
                <label class="form-label small">Directives formateur</label>
                <textarea v-model="policy.trainer_directives" class="form-control form-control-sm" rows="2" />
              </div>
              <div class="col-md-4">
                <div class="form-check">
                  <input :id="`share-${policy.id}`" v-model="policy.share_with_tutor" class="form-check-input" type="checkbox">
                  <label class="form-check-label small" :for="`share-${policy.id}`">Partager avec tuteur</label>
                </div>
              </div>
              <div class="col-md-4">
                <div class="form-check">
                  <input :id="`tutor-val-${policy.id}`" v-model="policy.tutor_validation_required" class="form-check-input" type="checkbox">
                  <label class="form-check-label small" :for="`tutor-val-${policy.id}`">Validation tuteur requise</label>
                </div>
              </div>
              <div class="col-md-4">
                <div class="form-check">
                  <input :id="`early-${policy.id}`" v-model="policy.allow_early_trigger" class="form-check-input" type="checkbox">
                  <label class="form-check-label small" :for="`early-${policy.id}`">Autoriser early trigger</label>
                </div>
              </div>
            </div>
            <button
              type="button"
              class="btn btn-sm btn-primary mt-2"
              :disabled="savingPolicyId === policy.id"
              @click="savePolicy(policy)"
            >
              Enregistrer la politique
            </button>
          </div>
        </div>
        <p v-if="!policies.length" class="text-muted small">Aucune politique — le moteur créera une politique par défaut à la demande.</p>
      </section>
    </template>
  </div>
</template>
