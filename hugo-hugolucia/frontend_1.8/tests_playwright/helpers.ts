import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import type { Page } from '@playwright/test'
import { expect } from '@playwright/test'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export type SmokeFixtures = {
  organisation_id: string
  organisation_name: string
  group_id: string
  group_name: string
  learner_id: string
  password: string
  verbatim_marker: string
  session_id: string
  users: Record<string, string>
  cluster16_sessions?: Record<'youth' | 'adult' | 'professional', string>
  trainer_session_id?: string
  tutor_workspace_session_id?: string
  tutor_workspace_profiles?: Record<string, string>
}

export type TenantSmokeFixtures = {
  password: string
  org_a: { id: string; name: string }
  org_b: { id: string; name: string }
  group_a_id: string
  group_b_id: string
  session_a_id: string
  session_b_id: string
  users: Record<string, string>
}

export function loadFixtures(): SmokeFixtures {
  const fixturePath = path.join(__dirname, 'smoke-fixtures.json')
  if (!fs.existsSync(fixturePath)) {
    throw new Error(
      'Missing smoke-fixtures.json — run: cd hugo_back && python manage.py bootstrap_smoke_playwright',
    )
  }
  return JSON.parse(fs.readFileSync(fixturePath, 'utf-8')) as SmokeFixtures
}

export function loadTenantFixtures(): TenantSmokeFixtures {
  const fixturePath = path.join(__dirname, 'tenant-smoke-fixtures.json')
  if (!fs.existsSync(fixturePath)) {
    throw new Error(
      'Missing tenant-smoke-fixtures.json — run: cd hugo_back && python manage.py bootstrap_multitenant_smoke',
    )
  }
  return JSON.parse(fs.readFileSync(fixturePath, 'utf-8')) as TenantSmokeFixtures
}

export function cluster16SessionId(
  fixtures: SmokeFixtures,
  profile: 'youth' | 'adult' | 'professional',
): string {
  return fixtures.cluster16_sessions?.[profile] || fixtures.session_id
}

export async function login(page: Page, username: string, password: string, redirect?: string) {
  const url = redirect ? `/login?redirect=${encodeURIComponent(redirect)}` : '/login'
  await page.goto(url)
  await page.evaluate(() => {
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
    localStorage.removeItem('hugo_active_organisation_id')
  })
  await page.getByLabel('Identifiant').fill(username)
  await page.getByLabel('Mot de passe', { exact: true }).fill(password)
  await Promise.all([
    page.waitForResponse(
      (response) => response.url().includes('/auth/login/') && response.status() === 200,
    ),
    page.getByRole('button', { name: 'Se connecter' }).click(),
  ])
  await page.waitForURL((u) => !u.pathname.includes('/login'), { timeout: 15_000 })
}

export async function setTenantOrg(page: Page, orgId: string) {
  await page.evaluate((id) => {
    localStorage.setItem('hugo_active_organisation_id', id)
  }, orgId)
}

export async function logout(page: Page) {
  const toggle = page.locator('.navbar .dropdown-toggle').first()
  if (await toggle.isVisible()) {
    await toggle.click()
    await page.getByRole('link', { name: 'Déconnexion' }).click()
  } else {
    await page.evaluate(() => {
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      localStorage.removeItem('hugo_active_organisation_id')
    })
    await page.goto('/login')
  }
  await page.waitForURL(/\/login/, { timeout: 15_000 })
}

/** Sélectionne le tenant actif via le switcher superadmin (recharge la page). */
export async function selectActiveTenant(page: Page, orgId: string) {
  const switcher = page.locator('#tenant-switcher')
  await switcher.waitFor({ state: 'visible', timeout: 15_000 })
  const current = await switcher.inputValue()
  if (current === orgId) return
  await Promise.all([
    page.waitForLoadState('load'),
    switcher.selectOption(orgId),
  ])
}

export function uniqueE2eUsername(prefix: string): string {
  const stamp = `${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
  return `${prefix}_${stamp}`.slice(0, 150)
}

/** Appel API via proxy Vite (/api → backend local baseline B). */
export async function apiFetchWithAuth(
  page: Page,
  path: string,
  init: RequestInit = {},
): Promise<{ status: number; body: unknown }> {
  return page.evaluate(async ({ apiPath, requestInit }) => {
    const token = localStorage.getItem('access')
    const headers = {
      ...(requestInit.headers as Record<string, string> | undefined),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    }
    const response = await fetch(`/api${apiPath}`, { ...requestInit, headers })
    let body: unknown = null
    try {
      body = await response.json()
    } catch {
      body = null
    }
    return { status: response.status, body }
  }, { apiPath: path, requestInit: init })
}

export function tutorChatUrl(
  sessionId: string,
  fx: SmokeFixtures,
  profileCode = 'tutor_workspace_journal',
): string {
  const params = new URLSearchParams({
    learner_id: fx.learner_id,
    group_id: fx.group_id,
    profile_code: profileCode,
  })
  return `/app/tutor/chat/${sessionId}?${params.toString()}`
}

export function trainerChatUrl(sessionId: string): string {
  return `/app/trainer/chat/${sessionId}`
}

export async function openTutorWorkspaceCta(
  page: Page,
  fx: SmokeFixtures,
  profileCode: string,
) {
  await login(
    page,
    fx.users.smoke_tutor,
    fx.password,
    `/app/tutor/group/${fx.group_id}/learner/${fx.learner_id}`,
  )
  const cta = page.getByTestId(`tutor-cta-${profileCode}`)
  await expect(cta).toBeVisible({ timeout: 15_000 })
  await cta.click()
  await expect(page).toHaveURL(/\/app\/tutor\/chat\//, { timeout: 15_000 })
}

/** Vérifie l'absence des blocs legacy apprenant sur un chat persona. */
export async function expectNoLearnerWorkspaceBlocks(page: Page) {
  await expect(page.getByTestId('session-posture-badge')).toHaveCount(0)
  await expect(page.getByRole('button', { name: /synthèse/i })).toHaveCount(0)
  await expect(page.getByRole('button', { name: /évaluation/i })).toHaveCount(0)
  await expect(page.locator('.prod-quest-card')).toHaveCount(0)
}
