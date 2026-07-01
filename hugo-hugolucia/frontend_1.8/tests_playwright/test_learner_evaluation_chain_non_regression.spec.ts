/** LEARNER — chaîne évaluation inchangée (CTA visibles, pas de régression). */
import { expect, test } from '@playwright/test'
import { loadFixtures, login } from './helpers'

test.describe('LEARNER_EVALUATION_CHAIN_NON_REGRESSION', () => {
  test('learner session exposes evaluation CTA surface', async ({ page }) => {
    const fx = loadFixtures()
    await login(page, fx.users.smoke_learner, fx.password, `/app/session/${fx.session_id}`)

    await expect(page.getByRole('button', { name: /Évaluation|évaluation/i }).first()).toBeVisible({
      timeout: 15_000,
    })
    await expect(page.getByRole('button', { name: /Synthèse|synthèse/i }).first()).toBeVisible()
  })
})
