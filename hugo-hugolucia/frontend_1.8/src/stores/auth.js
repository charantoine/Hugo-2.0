import { defineStore } from 'pinia'
import api from '../api/client'
import { isEncadrantLike, isOrgAdminLike, isTrainerLike, isTutorLike } from '../utils/roleGuards'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    access: localStorage.getItem('access') || null,
    refresh: localStorage.getItem('refresh') || null,
  }),
  getters: {
    isAuthenticated: (s) => !!s.access,
    /** ORGADMIN / SUPERADMIN — matches backend is_admin_like (exports, org admin). */
    isOrgAdminLike: (s) => isOrgAdminLike(s.user),
    /** Legacy alias — now aligned with backend is_admin_like, not TRAINER. */
    isAdminLike: (s) => isOrgAdminLike(s.user),
    isTrainerLike: (s) => isTrainerLike(s.user),
    isTutorLike: (s) => isTutorLike(s.user),
    isEncadrantLike: (s) => isEncadrantLike(s.user),
  },
  actions: {
    async login(username, password) {
      const { data } = await api.post('/auth/login/', { username, password })
      this.access = data.access
      this.refresh = data.refresh
      localStorage.setItem('access', data.access)
      localStorage.setItem('refresh', data.refresh)
      await this.fetchMe()
      return data
    },
    logout() {
      this.user = null
      this.access = null
      this.refresh = null
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
    },
    async fetchMe() {
      if (!this.access) return
      const { data } = await api.get('/auth/me/')
      this.user = data
      this.access = localStorage.getItem('access') || this.access
      return data
    },
  },
})
