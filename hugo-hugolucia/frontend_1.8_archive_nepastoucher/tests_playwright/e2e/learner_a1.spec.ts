import { expect, test } from '@playwright/test'
import { loadFixtures, login } from '../helpers'

/** Persona A1 — apprenant prod : UIState, pas de fuite P0/verbatim encadrant. */
test.describe('E2E_A1_LEARNER', () => {
  test('A1-01 opens learner session without internal fields in DOM', async ({ page }) => {
    const fx = loadFixtures()
    const sessionPath = `/app/session/${fx.session_id}`
    await login(page, fx.users.smoke_learner, fx.password, sessionPath)

    await expect(page.getByRole('heading', { name: /Conversation|conversation/i })).toBeVisible()
    const body = await page.locator('body').innerText()
    expect(body).not.toMatch(/turn_state|episode_clarity|cognitive_load|interaction_risk/i)
    expect(body).not.toContain('llm_request_payload')
  })

  test('A1-02 learner home loads without export CTAs', async ({ page }) => {
    const fx = loadFixtures()
    await login(page, fx.users.smoke_learner, fx.password, '/app')

    await expect(page.getByRole('heading', { name: /Hugo|sessions|accueil/i }).first()).toBeVisible()
    await expect(page.getByRole('button', { name: /JSON trace_rich_v1/i })).toHaveCount(0)
    await expect(page.getByRole('button', { name: /CSV principal/i })).toHaveCount(0)
  })

  test('A1-03 learner blocked from groups-admin', async ({ page }) => {
    const fx = loadFixtures()
    await login(page, fx.users.smoke_learner, fx.password, `/groups-admin/${fx.group_id}`)

    await page.waitForURL(/\/app/, { timeout: 15_000 })
    expect(page.url()).toMatch(/\/app/)
  })
})
