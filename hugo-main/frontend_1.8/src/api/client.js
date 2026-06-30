/**
 * API client — JWT in header, refresh on 401.
 * Base URL: VITE_API_URL (e.g. http://localhost:8000 or /api when behind nginx).
 */
import axios from 'axios'

const baseURL = import.meta.env.VITE_API_URL || '/api'

export const api = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
})

let refreshPromise = null

function isAuthRefreshRequest(config) {
  const path = String(config?.url || '')
  return path.includes('/auth/refresh/')
}

function isAuthLoginRequest(config) {
  const path = String(config?.url || '')
  return path.includes('/auth/login/')
}

api.interceptors.request.use((config) => {
  // Ne pas envoyer un access expiré sur login/refresh : évite des rejets inutiles côté DRF.
  if (!isAuthRefreshRequest(config) && !isAuthLoginRequest(config)) {
    const token = localStorage.getItem('access')
    if (token) config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config
    if (err.response?.status === 401 && isAuthRefreshRequest(original)) {
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      window.location.href = '/login'
      return Promise.reject(err)
    }
    if (err.response?.status === 401 && !original._retry) {
      original._retry = true
      const refresh = localStorage.getItem('refresh')
      if (!refresh) {
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        window.location.href = '/login'
        return Promise.reject(err)
      }
      if (!refreshPromise) {
        refreshPromise = api.post('/auth/refresh/', { refresh })
          .then((r) => {
            localStorage.setItem('access', r.data.access)
            if (r.data.refresh) localStorage.setItem('refresh', r.data.refresh)
            refreshPromise = null
            return r.data.access
          })
          .catch(() => {
            localStorage.removeItem('access')
            localStorage.removeItem('refresh')
            refreshPromise = null
            window.location.href = '/login'
            return Promise.reject(err)
          })
      }
      const access = await refreshPromise
      original.headers.Authorization = `Bearer ${access}`
      return api(original)
    }
    return Promise.reject(err)
  }
)

function filenameFromDisposition(disposition, fallbackName) {
  const value = String(disposition || '')
  const match = value.match(/filename="?([^"]+)"?/)
  if (!match?.[1]) return fallbackName
  return match[1]
}

function triggerBrowserDownload(blob, filename) {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

/**
 * Run export in metadata mode, then download generated file.
 * Returns metadata useful for UI messages.
 */
export async function runExportAndDownload({
  format,
  payload,
  csvFallbackName = 'felix_ready_export.csv',
  jsonFallbackName = 'trace_rich_v1.json',
}) {
  const { data: runMeta } = await api.post('/exports/run/?metadata_only=true', payload)
  const downloadUrl = runMeta?.download_url
  if (!downloadUrl) {
    throw new Error('URL de téléchargement introuvable.')
  }

  const fileResponse = await api.get(downloadUrl, { responseType: 'blob' })
  const fallbackName = format === 'csv' ? csvFallbackName : jsonFallbackName
  const filename = filenameFromDisposition(fileResponse.headers['content-disposition'], fallbackName)
  triggerBrowserDownload(fileResponse.data, filename)

  return { runMeta, filename }
}

export default api
