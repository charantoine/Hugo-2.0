import { expect, test } from '@playwright/test'
import { loadFixtures, login, trainerChatUrl } from './helpers'

test.describe('SMOKE_TRAINER_CHAT_EXPLICATION_IMPORT', () => {
  test('trainer opens explication import modal and confirms', async ({ page }) => {
    const fx = loadFixtures()
    const trainerSessionId = fx.trainer_session_id
    test.skip(!trainerSessionId, 'trainer_session_id missing — rerun bootstrap_smoke_playwright')

    await login(
      page,
      fx.users.smoke_trainer,
      fx.password,
      trainerChatUrl(trainerSessionId),
    )

    const explicationBtn = page.getByTestId('import-from-chat-trainer_explication')
    await expect(explicationBtn).toBeVisible({ timeout: 15_000 })
    await explicationBtn.click()

    const modal = page.getByTestId('trainer-import-confirm-modal')
    await expect(modal).toBeVisible()
    await expect(modal.getByText(/explicitation pédagogique/i)).toBeVisible()
    await expect(modal.getByText(/Créé depuis chat/i)).toBeVisible()

    await modal.locator('#explication-objective').fill('Comprendre les risques électriques')
    await modal.locator('#explication-errors').fill('Oublier la coupure générale')

    await Promise.all([
      page.waitForResponse(
        (response) => response.url().includes('/hugo/trainer/knowledge-items/')
          && response.request().method() === 'POST'
          && response.status() === 201,
      ),
      modal.getByTestId('trainer-import-confirm-btn').click(),
    ])

    await expect(page.getByText(/Import enregistré/i)).toBeVisible({ timeout: 10_000 })
  })
})
