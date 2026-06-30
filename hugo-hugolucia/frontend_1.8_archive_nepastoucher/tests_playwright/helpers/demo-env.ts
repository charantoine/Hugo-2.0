/**
 * Configuration runtime démo locale (override via env).
 */
export const DEMO_ENV = {
  baseURL: process.env.SMOKE_BASE_URL || 'http://localhost:5173',
  apiOrigin: process.env.SMOKE_API_ORIGIN || 'http://127.0.0.1:8000',
  superadmin: {
    username: process.env.DEMO_SUPERADMIN_USER || 'demo.superadmin',
    password: process.env.DEMO_SUPERADMIN_PASS || 'demo-superadmin-2026',
  },
  org: {
    id: process.env.DEMO_ORG_ID || 'dc1e8465-0ff2-4d66-bfbb-a0f8e7a23b3d',
    name: process.env.DEMO_ORG_NAME || 'Demo Hugo Org',
  },
  /** Deuxième org pour switch multi-tenant (Smoke Playwright Org par défaut). */
  altOrg: {
    id: process.env.DEMO_ALT_ORG_ID || 'e4b3e984-9794-438f-924d-366dfeb0cd4b',
    name: process.env.DEMO_ALT_ORG_NAME || 'Smoke Playwright Org',
  },
  groupBacPro: {
    id: process.env.DEMO_GROUP_BAC_PRO_ID || '29e5cdb9-de89-49b3-a36e-53b4b9bbbc50',
    name: 'bac pro melec',
  },
  referentialSourceRef: 'RNCP38878',
}

export type ApiCallRecord = {
  method: string
  url: string
  status: number
  path: string
}

export function apiPath(url: string): string {
  try {
    const u = new URL(url)
    return u.pathname.replace(/^\/api/, '') || u.pathname
  } catch {
    return url
  }
}
