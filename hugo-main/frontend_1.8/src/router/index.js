import { createRouter, createWebHistory } from 'vue-router'
import { getDefaultAuthenticatedPath } from '../utils/frontendConfig'

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
  { path: '/dashboard', name: 'Dashboard', component: () => import('../views/DashboardView.vue'), meta: { layout: 'tester' } },
  { path: '/group/:groupId', name: 'Group', component: () => import('../views/GroupView.vue'), meta: { layout: 'tester' } },
  { path: '/group/:groupId/learner/:learnerId', name: 'LearnerSpace', component: () => import('../views/LearnerSpaceView.vue'), meta: { layout: 'tester' } },
  { path: '/group/:groupId/referential', name: 'GroupReferentialConfig', component: () => import('../views/GroupReferentialConfigView.vue'), meta: { layout: 'tester' } },
  { path: '/referentials', name: 'ReferentialList', component: () => import('../views/ReferentialListView.vue'), meta: { layout: 'tester' } },
  { path: '/referentials/import', name: 'ReferentialImport', component: () => import('../views/ReferentialImportView.vue'), meta: { layout: 'tester' } },
  { path: '/groups-admin', name: 'GroupsAdmin', component: () => import('../views/GroupsAdminListView.vue'), meta: { layout: 'tester' } },
  { path: '/groups-admin/:groupId', name: 'GroupAdminDetail', component: () => import('../views/GroupAdminDetailView.vue'), meta: { layout: 'tester' } },
  { path: '/tutor-prompts', name: 'TutorPrompts', component: () => import('../views/TutorPromptsView.vue'), meta: { layout: 'tester' } },
  { path: '/ovh-llms', name: 'OvhLlms', component: () => import('../views/OvhLlmView.vue'), meta: { layout: 'tester' } },
  { path: '/users', name: 'Users', component: () => import('../views/UsersView.vue'), meta: { layout: 'tester' } },
  { path: '/users/:userId', name: 'UserDetail', component: () => import('../views/UserDetailView.vue'), meta: { layout: 'tester' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

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
    const redirect = typeof to.query.redirect === 'string' ? to.query.redirect : defaultAuthenticatedPath
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
  next()
})

export default router
