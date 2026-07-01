import { expect, test } from '@playwright/test'
import { loadFixtures, login } from './helpers'

test.describe('SMOKE_TRAINER', () => {
  test('trainer sees knowledge list and can validate item', async ({ page }) => {
    const fx = loadFixtures()
    await login(page, fx.users.smoke_trainer, fx.password, '/app/trainer/knowledge')

    await expect(page.getByRole('heading', { name: 'Orchestrateur de connaissance' })).toBeVisible()
    await expect(page.getByTestId('trainer-group-context')).toBeVisible()
    await expect(page.getByText('Smoke knowledge item for Playwright')).toBeVisible()

    const smokeRow = page.getByRole('row').filter({ hasText: 'Smoke knowledge item for Playwright' })
    await expect(smokeRow).toBeVisible()

    const validateBtn = smokeRow.getByRole('button', { name: /^Valider$/ })
    if (await validateBtn.isVisible()) {
      await validateBtn.click()
      await expect(page.getByText('Action enregistrée.')).toBeVisible({ timeout: 10_000 })
    }
    await expect(smokeRow.getByText('Validé formateur')).toBeVisible()
  })
})
