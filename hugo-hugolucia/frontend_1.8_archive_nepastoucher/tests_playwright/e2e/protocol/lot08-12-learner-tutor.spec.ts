import { expect, test } from '@playwright/test'
import { loadFixtures, login } from '../../helpers'
import { trackApi } from '../../helpers/protocol'

test.describe('LOT 8 — Parcours apprenant (smoke fixtures)', () => {
  test('L8-session ui-state wired', async ({ page }) => {
    let fx
    try {
      fx = loadFixtures()
    } catch {
      test.skip(true, 'smoke-fixtures.json requis')
      return
    }
    const api = trackApi(page)
    await login(page, fx.users.smoke_learner, fx.password, `/app/session/${fx.session_id}`)
    await page.waitForTimeout(3000)
    const uiCalls = api.find('/ui-state/', 'GET')
    expect(uiCalls.some((c) => c.status === 200)).toBeTruthy()
    await expect(page.getByRole('heading', { name: /Conversation|conversation/i })).toBeVisible()
  })

  test('L8-memory-summary wired when panel open', async ({ page }) => {
    let fx
    try {
      fx = loadFixtures()
    } catch {
      test.skip(true, 'smoke-fixtures.json requis')
      return
    }
    const api = trackApi(page)
    await login(page, fx.users.smoke_learner, fx.password, `/app/session/${fx.session_id}`)
    await page.waitForTimeout(2500)
    const memBtn = page.getByRole('button', { name: /mémoire|memory/i }).first()
    if (await memBtn.isVisible()) {
      await memBtn.click()
      await page.waitForTimeout(1500)
      expect(api.find('/memory-summary/', 'GET').length).toBeGreaterThan(0)
    }
  })
})

test.describe('LOT 10 — Tuteur (smoke fixtures)', () => {
  test('L10-tutor timeline sans verbatim', async ({ page }) => {
    let fx
    try {
      fx = loadFixtures()
    } catch {
      test.skip(true, 'smoke-fixtures.json requis')
      return
    }
    await login(page, fx.users.smoke_tutor, fx.password, '/app/tutor')
    await expect(page.getByRole('heading', { name: 'Espace tuteur' })).toBeVisible()
    const body = await page.locator('body').innerText()
    expect(body).not.toContain(fx.verbatim_marker)
  })
})

test.describe('LOT 12 — Mode testeur / pas de P0 sur /app', () => {
  test('L12-learner app sans debug P0', async ({ page }) => {
    let fx
    try {
      fx = loadFixtures()
    } catch {
      test.skip(true, 'smoke-fixtures.json requis')
      return
    }
    await login(page, fx.users.smoke_learner, fx.password, `/app/session/${fx.session_id}`)
    await page.waitForTimeout(2000)
    const body = await page.locator('body').innerText()
    expect(body).not.toMatch(/turn_state|P0 classifier|llm_request_payload/i)
  })

  test('L12-dashboard testeur séparé', async ({ page }) => {
    const { DEMO_ENV } = await import('../../helpers/demo-env')
    await login(page, DEMO_ENV.superadmin.username, DEMO_ENV.superadmin.password, '/dashboard')
    await expect(page.getByTestId('dashboard-tester-canonical')).toBeVisible()
  })
})
