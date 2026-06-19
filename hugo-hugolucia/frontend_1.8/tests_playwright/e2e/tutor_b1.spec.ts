import { expect, test } from '@playwright/test'
import { loadFixtures, login } from '../helpers'

/** Persona B1 — tuteur prod : timeline sans verbatim, pas de champs internes. */
test.describe('E2E_B1_TUTOR', () => {
  test('B1-T1 tutor space loads without internal diagnostics', async ({ page }) => {
    const fx = loadFixtures()
    await login(page, fx.users.smoke_tutor, fx.password, '/app/tutor')

    await expect(page.getByRole('heading', { name: 'Espace tuteur' })).toBeVisible()
    const body = await page.locator('body').innerText()
    expect(body).not.toMatch(/turn_state|llm_request_payload|episode_clarity/i)
    expect(body).not.toContain(fx.verbatim_marker)
  })

  test('B1-T2 tutor blocked from org exports UI', async ({ page }) => {
    const fx = loadFixtures()
    await login(page, fx.users.smoke_tutor, fx.password, `/group/${fx.group_id}`)

    await expect(page.getByRole('button', { name: /JSON trace_rich_v1/i })).toHaveCount(0)
  })
})
