import { createRouter, createWebHistory } from 'vue-router'
import { getDefaultAuthenticatedPath, resolveAuthenticatedHome } from '../utils/frontendConfig'
import {
  isEncadrantLike,
  isLearnerOnly,
  isOrgAdminLike,
  isSuperAdmin,
  isTrainerLike,
  isTutorLike,
} from '../utils/roleGuards'

const defaultAuthenticatedPath = getDefaultAuthenticatedPath()

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { public: true, layout: 'prod' },
  },
  { path: '/', redirect: defaultAuthenticatedPath },
  {
    path: '/app',
    name: 'ProdLearnerHome',
    component: () => import('../views/ProdLearnerHomeView.vue'),
    meta: { layout: 'prod' },
  },
  {
    path: '/app/session/:sessionId',
    name: 'ProdLearnerSession',
    component: () => import('../views/ProdLearnerSessionView.vue'),
    meta: { layout: 'prod' },
  },
  {
    path: '/app/tutor/chat/:sessionId',
    name: 'ProdTutorChatSession',
    component: () => import('../views/ProdTutorChatSessionView.vue'),
    meta: { layout: 'prod', requiresTutorLike: true },
  },
  {
    path: '/app/trainer/chat',
    name: 'ProdTrainerChatHome',
    component: () => import('../views/ProdTrainerChatHomeView.vue'),
    meta: { layout: 'prod', requiresTrainerLike: true },
  },
  {
    path: '/app/trainer/chat/:sessionId',
    name: 'ProdTrainerChatSession',
    component: () => import('../views/ProdTrainerChatSessionView.vue'),
    meta: { layout: 'prod', requiresTrainerLike: true },
  },
  {
    path: '/app/tutor',
    name: 'ProdTutorHome',
    component: () => import('../views/ProdTutorHomeView.vue'),
    meta: { layout: 'prod', requiresTutorLike: true },
  },
  {
    path: '/app/tutor/group/:groupId',
    name: 'ProdTutorGroup',
    component: () => import('../views/ProdTutorGroupView.vue'),
    meta: { layout: 'prod', requiresTutorLike: true },
  },
  {
    path: '/app/tutor/group/:groupId/learner/:learnerId',
    name: 'ProdTutorLearner',
    component: () => import('../views/ProdTutorLearnerView.vue'),
    meta: { layout: 'prod', requiresTutorLike: true },
  },
  {
    path: '/app/trainer',
    redirect: '/app/trainer/knowledge',
  },
  {
    path: '/app/trainer/library',
    name: 'ProdTrainerLibrary',
    component: () => import('../views/ProdTrainerLibraryView.vue'),
    meta: { layout: 'prod', requiresTrainerLike: true },
  },
  {
    path: '/app/trainer/referentials',
    name: 'ProdTrainerReferentials',
    component: () => import('../views/ReferentialListView.vue'),
    meta: { layout: 'prod', requiresTrainerLike: true, trainerShell: true },
  },
  {
    path: '/app/trainer/referentials/import',
    name: 'ProdTrainerReferentialImport',
    component: () => import('../views/ReferentialImportView.vue'),
    meta: { layout: 'prod', requiresTrainerLike: true, trainerShell: true },
  },
  {
    path: '/app/trainer/knowledge',
    name: 'ProdTrainerKnowledge',
    component: () => import('../views/ProdTrainerKnowledgeView.vue'),
    meta: { layout: 'prod', requiresTrainerLike: true },
  },
  {
    path: '/app/trainer/elicitation',
    name: 'ProdTrainerElicitation',
    component: () => import('../views/ProdTrainerElicitationView.vue'),
    meta: { layout: 'prod', requiresTrainerLike: true },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: { layout: 'tester', requiresEncadrant: true },
  },
  {
    path: '/group/:groupId',
    name: 'Group',
    component: () => import('../views/GroupView.vue'),
    meta: { layout: 'tester' },
  },
  {
    path: '/group/:groupId/learner/:learnerId',
    name: 'LearnerSpace',
    component: () => import('../views/LearnerSpaceView.vue'),
    meta: { layout: 'tester' },
  },
  {
    path: '/group/:groupId/referential',
    name: 'GroupReferentialConfig',
    component: () => import('../views/GroupReferentialConfigView.vue'),
    meta: { layout: 'tester', requiresEncadrant: true },
  },
  {
    path: '/referentials',
    name: 'ReferentialList',
    component: () => import('../views/ReferentialListView.vue'),
    meta: { layout: 'tester', requiresEncadrant: true },
  },
  {
    path: '/referentials/import',
    name: 'ReferentialImport',
    component: () => import('../views/ReferentialImportView.vue'),
    meta: { layout: 'tester', requiresEncadrant: true },
  },
  {
    path: '/admin/organisations',
    name: 'AdminOrganisations',
    component: () => import('../views/admin/OrganisationsListView.vue'),
    meta: { layout: 'tester', requiresOrgAdmin: true },
  },
  {
    path: '/admin/organisations/:orgId',
    name: 'AdminOrganisationDetail',
    component: () => import('../views/admin/OrganisationDetailView.vue'),
    meta: { layout: 'tester', requiresSuperAdmin: true },
  },
  {
    path: '/groups-admin',
    name: 'GroupsAdmin',
    component: () => import('../views/GroupsAdminListView.vue'),
    meta: { layout: 'tester', requiresOrgAdmin: true },
  },
  {
    path: '/groups-admin/:groupId',
    name: 'GroupAdminDetail',
    component: () => import('../views/GroupAdminDetailView.vue'),
    meta: { layout: 'tester', requiresOrgAdmin: true },
  },
  {
    path: '/admin/onboarding',
    name: 'AdminOnboarding',
    component: () => import('../views/admin/AdminOnboardingWizardView.vue'),
    meta: { layout: 'tester', requiresOrgAdmin: true },
  },
  {
    path: '/admin/conversation',
    name: 'AdminConversationIndex',
    component: () => import('../views/admin/AdminConversationIndexView.vue'),
    meta: { layout: 'tester', requiresOrgAdmin: true },
  },
  {
    path: '/admin/conversation/learner/closing',
    name: 'AdminLearnerClosing',
    component: () => import('../views/admin/LearnerClosingEvaluationView.vue'),
    meta: { layout: 'tester', requiresOrgAdmin: true },
  },
  {
    path: '/admin/conversation/learner/profiles/new',
    name: 'AdminLearnerProfilesNew',
    component: () => import('../views/admin/LearnerConversationProfilesView.vue'),
    meta: { layout: 'tester', requiresOrgAdmin: true },
  },
  {
    path: '/admin/conversation/learner/profiles/:profileId',
    name: 'AdminLearnerProfilesDetail',
    component: () => import('../views/admin/LearnerConversationProfilesView.vue'),
    meta: { layout: 'tester', requiresOrgAdmin: true },
  },
  {
    path: '/admin/conversation/learner/profiles',
    name: 'AdminLearnerProfiles',
    component: () => import('../views/admin/LearnerConversationProfilesView.vue'),
    meta: { layout: 'tester', requiresOrgAdmin: true },
  },
  {
    path: '/admin/conversation/learner/:postureCode',
    name: 'AdminLearnerModeHub',
    component: () => import('../views/admin/LearnerModeHubView.vue'),
    meta: { layout: 'tester', requiresOrgAdmin: true },
  },
  {
    path: '/admin/conversation/tutor/profiles/new',
    name: 'AdminTutorPersonaProfilesNew',
    component: () => import('../views/admin/PersonaConversationProfilesView.vue'),
    props: {
      personaKind: 'tutor',
      personaLabel: 'Tuteur',
      orchestratorRoute: '/admin/conversation/tutor',
    },
    meta: { layout: 'tester', requiresOrgAdmin: true },
  },
  {
    path: '/admin/conversation/tutor/profiles/:profileId',
    name: 'AdminTutorPersonaProfilesDetail',
    component: () => import('../views/admin/PersonaConversationProfilesView.vue'),
    props: {
      personaKind: 'tutor',
      personaLabel: 'Tuteur',
      orchestratorRoute: '/admin/conversation/tutor',
    },
    meta: { layout: 'tester', requiresOrgAdmin: true },
  },
  {
    path: '/admin/conversation/tutor/profiles',
    name: 'AdminTutorPersonaProfiles',
    component: () => import('../views/admin/PersonaConversationProfilesView.vue'),
    props: {
      personaKind: 'tutor',
      personaLabel: 'Tuteur',
      orchestratorRoute: '/admin/conversation/tutor',
    },
    meta: { layout: 'tester', requiresOrgAdmin: true },
  },
  {
    path: '/admin/conversation/tutor',
    name: 'AdminTutorOrchestrator',
    component: () => import('../views/admin/TutorOrchestratorAdminView.vue'),
    meta: { layout: 'tester', requiresOrgAdmin: true },
  },
  {
    path: '/admin/conversation/trainer/profiles/new',
    name: 'AdminTrainerPersonaProfilesNew',
    component: () => import('../views/admin/PersonaConversationProfilesView.vue'),
    props: {
      personaKind: 'trainer',
      personaLabel: 'Formateur',
      orchestratorRoute: '/admin/conversation/trainer',
    },
    meta: { layout: 'tester', requiresOrgAdmin: true },
  },
  {
    path: '/admin/conversation/trainer/profiles/:profileId',
    name: 'AdminTrainerPersonaProfilesDetail',
    component: () => import('../views/admin/PersonaConversationProfilesView.vue'),
    props: {
      personaKind: 'trainer',
      personaLabel: 'Formateur',
      orchestratorRoute: '/admin/conversation/trainer',
    },
    meta: { layout: 'tester', requiresOrgAdmin: true },
  },
  {
    path: '/admin/conversation/trainer/profiles',
    name: 'AdminTrainerPersonaProfiles',
    component: () => import('../views/admin/PersonaConversationProfilesView.vue'),
    props: {
      personaKind: 'trainer',
      personaLabel: 'Formateur',
      orchestratorRoute: '/admin/conversation/trainer',
    },
    meta: { layout: 'tester', requiresOrgAdmin: true },
  },
  {
    path: '/admin/conversation/trainer',
    name: 'AdminTrainerOrchestrator',
    component: () => import('../views/admin/TrainerOrchestratorAdminView.vue'),
    meta: { layout: 'tester', requiresOrgAdmin: true },
  },
  {
    path: '/tutor-prompts',
    name: 'TutorPrompts',
    component: () => import('../views/TutorPromptsView.vue'),
    meta: { layout: 'tester', requiresOrgAdmin: true },
  },
  {
    path: '/conduct-profiles',
    name: 'ConductProfiles',
    component: () => import('../views/ConductProfilesView.vue'),
    meta: { layout: 'tester', requiresOrgAdmin: true },
  },
  {
    path: '/ovh-llms',
    name: 'OvhLlms',
    component: () => import('../views/OvhLlmView.vue'),
    meta: { layout: 'tester', requiresOrgAdmin: true },
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('../views/UsersView.vue'),
    meta: { layout: 'tester', requiresOrgAdmin: true },
  },
  {
    path: '/users/:userId',
    name: 'UserDetail',
    component: () => import('../views/UserDetailView.vue'),
    meta: { layout: 'tester', requiresOrgAdmin: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

function redirectForRole(user, to) {
  if (to.meta.requiresSuperAdmin && !isSuperAdmin(user)) {
    return '/dashboard'
  }
  if (to.meta.requiresOrgAdmin && !isOrgAdminLike(user)) {
    return '/app'
  }
  if (to.meta.requiresTrainerLike && !isTrainerLike(user)) {
    return '/app'
  }
  if (to.meta.requiresTutorLike && !isTutorLike(user)) {
    return '/app'
  }
  if (to.meta.requiresEncadrant && isLearnerOnly(user)) {
    return '/app'
  }
  return null
}

router.beforeEach(async (to, _from, next) => {
  const access = localStorage.getItem('access')
  const auth = (await import('../stores/auth.js')).useAuthStore()

  if (to.meta.public && access) {
    if (!auth.user) {
      try {
        await auth.fetchMe()
      } catch {
        auth.logout()
        return next()
      }
    }
    const redirect = typeof to.query.redirect === 'string'
      ? to.query.redirect
      : resolveAuthenticatedHome(auth.user)
    return next(redirect)
  }

  if (!to.meta.public && !access) {
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }

  if (access && !auth.user) {
    try {
      await auth.fetchMe()
    } catch {
      auth.logout()
      return next({ path: '/login', query: { session: 'expired', redirect: to.fullPath } })
    }
  }

  if (auth.user) {
    const roleRedirect = redirectForRole(auth.user, to)
    if (roleRedirect) {
      return next(roleRedirect)
    }
    const roleHome = resolveAuthenticatedHome(auth.user)
    if (to.path === '/dashboard' && roleHome !== '/dashboard') {
      return next(roleHome)
    }
  }

  next()
})

export default router
