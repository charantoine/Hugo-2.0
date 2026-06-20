<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ConductProfileSection from '../../components/admin/conversation/ConductProfileSection.vue'
import TutorPromptListSection from '../../components/admin/conversation/TutorPromptListSection.vue'
import OrchestratorStaticParamsPanel from '../../components/admin/conversation/OrchestratorStaticParamsPanel.vue'
import { LEARNER_POSTURES } from '../../constants/conversationPostures'
import { isValidLearnerPostureCode, learnerModeMeta } from '../../constants/adminConversationModes'

const route = useRoute()
const router = useRouter()

const postureCode = computed(() => String(route.params.postureCode || ''))
const modeMeta = computed(() => (isValidLearnerPostureCode(postureCode.value) ? learnerModeMeta(postureCode.value) : null))

function ensureValidPosture() {
  if (!isValidLearnerPostureCode(postureCode.value)) {
    router.replace('/admin/conversation')
  }
}

onMounted(ensureValidPosture)
watch(postureCode, ensureValidPosture)

const siblingModes = computed(() =>
  LEARNER_POSTURES.map((p) => ({
    code: p.code,
    label: p.code === 'knowledge_review' ? 'Buchage' : p.label,
    path: `/admin/conversation/learner/${p.code}`,
    active: p.code === postureCode.value,
  }))
)
</script>

<template>
  <div v-if="modeMeta" class="container-fluid">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb">
        <li class="breadcrumb-item"><router-link to="/dashboard">Tableau de bord</router-link></li>
        <li class="breadcrumb-item"><router-link to="/admin/conversation">Configuration conversation</router-link></li>
        <li class="breadcrumb-item active" aria-current="page">{{ modeMeta.adminLabel }}</li>
      </ol>
    </nav>

    <header class="mb-4">
      <h1 class="h4 mb-1">Apprenant — {{ modeMeta.adminLabel }}</h1>
      <p class="text-muted mb-3">{{ modeMeta.description }}</p>
      <ul class="nav nav-pills flex-wrap gap-1">
        <li v-for="mode in siblingModes" :key="mode.code" class="nav-item">
          <router-link
            class="nav-link py-1 px-3"
            :class="{ active: mode.active }"
            :to="mode.path"
          >
            {{ mode.label }}
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link py-1 px-3" to="/admin/conversation/learner/closing">
            Clôture évaluation
          </router-link>
        </li>
      </ul>
    </header>

    <div class="row g-4">
      <div class="col-12 col-xl-7">
        <ConductProfileSection
          :posture-code="postureCode"
          :posture-label="modeMeta.adminLabel"
        />
      </div>
      <div class="col-12 col-xl-5">
        <OrchestratorStaticParamsPanel
          :posture-code="postureCode"
          :static-params="modeMeta.staticParams"
        />
      </div>
      <div class="col-12">
        <TutorPromptListSection :posture-code="postureCode" />
      </div>
    </div>
  </div>
</template>
