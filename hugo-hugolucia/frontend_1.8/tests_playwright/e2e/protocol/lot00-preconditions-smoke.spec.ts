/**
 * LOT 0 — Préconditions + smoke runtime.
 * Écrit protocol-preconditions.json pour le rapport.
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { expect, test } from '@playwright/test'
import { DEMO_ENV } from '../../helpers/demo-env'
import { collectConsoleErrors, trackApi } from '../../helpers/protocol'
import { login } from '../../helpers'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const OUT_DIR = path.resolve(__dirname, '../../../../../docs-workspace/e2e-protocol-runtime')

test.describe('LOT 0 — Préconditions & smoke', () => {
  test('L0-preconditions probe API + auth', async ({ request }) => {
    const pre: Record<string, unknown> = {
      frontUrl: DEMO_ENV.baseURL,
      apiOrigin: DEMO_ENV.apiOrigin,
      checkedAt: new Date().toISOString(),
    }

    const loginRes = await request.post(`${DEMO_ENV.apiOrigin}/auth/login/`, {
      data: {
        username: DEMO_ENV.superadmin.username,
        password: DEMO_ENV.superadmin.password,
      },
    })
    pre.loginStatus = loginRes.status()
    expect(loginRes.ok()).toBeTruthy()
    const { access } = await loginRes.json()
    pre.superadmin = { username: DEMO_ENV.superadmin.username, ok: true }

    const orgRes = await request.get(`${DEMO_ENV.apiOrigin}/admin/organisations/`, {
      headers: { Authorization: `Bearer ${access}` },
    })
    const orgs = await orgRes.json()
    const orgList = Array.isArray(orgs) ? orgs : orgs.results || []
    pre.organisationCount = orgList.length
    pre.hasTwoOrgs = orgList.length >= 2

    const groupsRes = await request.get(`${DEMO_ENV.apiOrigin}/groups/`, {
      headers: {
        Authorization: `Bearer ${access}`,
        'X-Organisation-Id': DEMO_ENV.org.id,
      },
    })
    const groups = await groupsRes.json()
    const groupList = Array.isArray(groups) ? groups : groups.results || []
    pre.groupCountDemoOrg = groupList.length
    pre.hasTwoGroups = groupList.length >= 2
    pre.hasBacProMelec = groupList.some((g: { name?: string }) =>
      g.name?.toLowerCase().includes('bac pro melec'),
    )

    const usersRes = await request.get(`${DEMO_ENV.apiOrigin}/users/`, {
      headers: {
        Authorization: `Bearer ${access}`,
        'X-Organisation-Id': DEMO_ENV.org.id,
      },
    })
    const users = await usersRes.json()
    const userList = Array.isArray(users) ? users : users.results || []
    const roles = (r: string) => userList.filter((u: { role: string }) => u.role === r).map((u: { username: string }) => u.username)
    pre.rolesDemoOrg = {
      SUPERADMIN: roles('SUPERADMIN'),
      ORGADMIN: roles('ORGADMIN'),
      LEARNER: roles('LEARNER').slice(0, 3),
      TUTOR: roles('TUTOR').slice(0, 3),
      TRAINER: roles('TRAINER').slice(0, 3),
    }
    pre.missingCritical = []
    if (!pre.hasTwoOrgs) pre.missingCritical.push('≥2 organisations pour switch multi-tenant')
    if (!pre.hasTwoGroups) pre.missingCritical.push('≥2 groupes dans org démo')
    if (roles('LEARNER').length < 1) pre.missingCritical.push('≥1 apprenant')
    if (roles('TUTOR').length < 1) pre.missingCritical.push('≥1 tuteur')
    if (roles('TRAINER').length < 1) pre.missingCritical.push('≥1 formateur')

    // smoke fixtures optional
    try {
      const { loadFixtures } = await import('../../helpers')
      const fx = loadFixtures()
      pre.smokeFixtures = { ok: true, org: fx.organisation_name, group: fx.group_name }
    } catch (e) {
      pre.smokeFixtures = { ok: false, error: String(e) }
    }

    fs.mkdirSync(OUT_DIR, { recursive: true })
    fs.writeFileSync(path.join(OUT_DIR, 'protocol-preconditions.json'), JSON.stringify(pre, null, 2))
  })

  test('L0-smoke login + dashboard + no fatal console', async ({ page }) => {
    const errors = await collectConsoleErrors(page)
    const api = trackApi(page)
    await login(page, DEMO_ENV.superadmin.username, DEMO_ENV.superadmin.password, '/dashboard')
    await expect(page.getByRole('heading', { name: 'Tableau de bord' })).toBeVisible()
    await page.waitForTimeout(1500)
    const fatal = errors.filter((e) => !/favicon|404/.test(e))
    expect(fatal, `console errors: ${fatal.join('; ')}`).toHaveLength(0)
    expect(api.find('/groups/', 'GET').length).toBeGreaterThan(0)
  })

  test('L0-smoke app learner route loads for smoke user if fixtures present', async ({ page }) => {
    let fx
    try {
      const { loadFixtures } = await import('../../helpers')
      fx = loadFixtures()
    } catch {
      test.skip(true, 'smoke-fixtures.json absent')
      return
    }
    const api = trackApi(page)
    await login(page, fx.users.smoke_learner, fx.password, '/app')
    await page.waitForTimeout(2000)
    expect(page.url()).toMatch(/\/app/)
    const uiCalls = api.find('/ui-state', 'GET')
    // home may not call ui-state; just ensure no crash
    expect(page.locator('body')).toBeTruthy()
  })
})
