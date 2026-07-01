import { expect, test } from '@playwright/test'
import { loadFixtures, login } from './helpers'

test.describe('SMOKE_TRAINER_CHAT_LABELS', () => {
  test('pure trainer sees Mon chat entry points', async ({ page }) => {
    const fx = loadFixtures()
    await login(page, fx.users.smoke_trainer, fx.password, '/app/trainer/knowledge')

    await expect(page.getByTestId('trainer-mon-chat-link')).toHaveText('Mon chat')
    await page.getByTestId('trainer-mon-chat-link').click()
    await expect(page).toHaveURL(/\/app\/trainer\/chat\/?$/)

    await expect(page.getByRole('banner').getByRole('link', { name: 'Mon chat' })).toBeVisible()
    await expect(page.getByText('Espace conversationnel formateur')).toBeVisible()
  })
})
