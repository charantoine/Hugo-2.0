import { defineStore } from 'pinia'
import api from '../api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    access: localStorage.getItem('access') || null,
    refresh: localStorage.getItem('refresh') || null,
  }),
  getters: {
    isAuthenticated: (s) => !!s.access,
    isAdminLike: (s) => {
      const u = s.user || {}
      const role = (u.role || u.user_role || '').toUpperCase()
      return (
        !!u &&
        (u.is_superuser ||
          u.is_staff ||
          role === 'ADMIN' ||
          role === 'ORGADMIN' ||
          role === 'SUPERADMIN' ||
          role === 'TRAINER' ||
          role === 'TUTOR_ADMIN')
      )
    },
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
      // Après refresh JWT dans l’intercepteur axios, l’access peut être renouvelé dans localStorage seulement.
      this.access = localStorage.getItem('access') || this.access
      return data
    },
  },
})
