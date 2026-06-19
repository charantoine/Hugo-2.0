import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import type { Page } from '@playwright/test'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export type SmokeFixtures = {
  group_id: string
  learner_id: string
  password: string
  verbatim_marker: string
  session_id: string
  users: Record<string, string>
  cluster16_sessions?: Record<'youth' | 'adult' | 'professional', string>
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
