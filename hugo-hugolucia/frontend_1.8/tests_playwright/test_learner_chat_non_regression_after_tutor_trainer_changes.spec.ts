/** LEARNER — non-régression chat après changements tuteur/formateur. */
import { expect, test } from '@playwright/test'
import { loadFixtures, login } from './helpers'

test.describe('LEARNER_CHAT_NON_REGRESSION', () => {
  test('learner session loads without P0 leak in DOM', async ({ page }) => {
    const fx = loadFixtures()
    await login(page, fx.users.smoke_learner, fx.password, `/app/session/${fx.session_id}`)

    await expect(page.getByRole('heading', { name: /Conversation/i })).toBeVisible()
    const body = await page.locator('body').innerText()
    expect(body).not.toMatch(/turn_state|episode_clarity|cognitive_load/i)
    expect(body).not.toContain('llm_request_payload')
  })

  test('learner home still accessible', async ({ page }) => {
    const fx = loadFixtures()
    await login(page, fx.users.smoke_learner, fx.password, '/app')
    await expect(page.getByRole('link', { name: /Chat apprenant|sessions|Hugo/i }).first()).toBeVisible()
  })
})
