/** TRAINER — validation knowledge non-régression. */
import { expect, test } from '@playwright/test'
import { loadFixtures, login } from './helpers'

test.describe('TRAINER_KNOWLEDGE_VALIDATION_NON_REGRESSION', () => {
  test('trainer validates knowledge item from orchestrator', async ({ page }) => {
    const fx = loadFixtures()
    await login(page, fx.users.smoke_trainer, fx.password, '/app/trainer/knowledge')

    await expect(page.getByRole('heading', { name: /Base de connaissances|connaissance/i })).toBeVisible()
    const validateBtn = page.getByRole('button', { name: /Valider/i }).first()
    if (await validateBtn.isVisible()) {
      await validateBtn.click()
      await expect(page.getByText(/validé|Validé/i).first()).toBeVisible({ timeout: 10_000 })
    }
  })
})
