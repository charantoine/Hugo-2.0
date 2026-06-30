import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/LoginView.vue'), meta: { public: true } },
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'Dashboard', component: () => import('../views/DashboardView.vue') },
  { path: '/group/:groupId', name: 'Group', component: () => import('../views/GroupView.vue') },
  { path: '/group/:groupId/learner/:learnerId', name: 'LearnerSpace', component: () => import('../views/LearnerSpaceView.vue') },
  { path: '/group/:groupId/referential', name: 'GroupReferentialConfig', component: () => import('../views/GroupReferentialConfigView.vue') },
  { path: '/referentials', name: 'ReferentialList', component: () => import('../views/ReferentialListView.vue') },
  { path: '/referentials/import', name: 'ReferentialImport', component: () => import('../views/ReferentialImportView.vue') },
  { path: '/groups-admin', name: 'GroupsAdmin', component: () => import('../views/GroupsAdminListView.vue') },
  { path: '/groups-admin/:groupId', name: 'GroupAdminDetail', component: () => import('../views/GroupAdminDetailView.vue') },
  { path: '/tutor-prompts', name: 'TutorPrompts', component: () => import('../views/TutorPromptsView.vue') },
  { path: '/ovh-llms', name: 'OvhLlms', component: () => import('../views/OvhLlmView.vue') },
  { path: '/users', name: 'Users', component: () => import('../views/UsersView.vue') },
  { path: '/users/:userId', name: 'UserDetail', component: () => import('../views/UserDetailView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, _from, next) => {
  const access = localStorage.getItem('access')
  if (!to.meta.public && !access) return next('/login')
  const auth = (await import('../stores/auth.js')).useAuthStore()
  if (access && !auth.user) {
    try {
      await auth.fetchMe()
    } catch {
      auth.logout()
      return next({ path: '/login', query: { session: 'expired' } })
    }
  }
  next()
})

export default router
