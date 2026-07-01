import { expect, test } from '@playwright/test'
import { loadFixtures, login } from './helpers'

test.describe('SMOKE_TUTOR_CHAT_LABELS', () => {
  test('pure tutor topbar chat link targets tutor home not learner app', async ({ page }) => {
    const fx = loadFixtures()
    await login(page, fx.users.smoke_tutor, fx.password, '/app/tutor')

    const chatLink = page.getByRole('banner').getByRole('link', { name: 'Mon espace de réflexion' })
    await expect(chatLink).toBeVisible()
    await chatLink.click()
    await expect(page).toHaveURL(/\/app\/tutor\/?$/)
    await expect(page.getByText('Espace tuteur')).toBeVisible()
  })
})
