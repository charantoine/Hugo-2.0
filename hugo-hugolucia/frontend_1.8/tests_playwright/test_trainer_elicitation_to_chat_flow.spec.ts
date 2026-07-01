/** TRAINER — élicitation puis accès chat formateur. */
import { expect, test } from '@playwright/test'
import { loadFixtures, login } from './helpers'

test.describe('TRAINER_ELICITATION_TO_CHAT_FLOW', () => {
  test('trainer opens elicitation then mon chat', async ({ page }) => {
    const fx = loadFixtures()
    await login(page, fx.users.smoke_trainer, fx.password, '/app/trainer/elicitation')

    await expect(page.getByRole('heading', { name: /Élicitation|elicitation/i })).toBeVisible()
    await page.goto('/app/trainer/knowledge')
    await page.getByTestId('trainer-mon-chat-link').click()
    await expect(page).toHaveURL(/\/app\/trainer\/chat\/?$/)
    await expect(page.getByRole('link', { name: 'Mon chat' })).toBeVisible()
  })
})
