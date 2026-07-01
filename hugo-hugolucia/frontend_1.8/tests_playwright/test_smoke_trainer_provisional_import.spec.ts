import { expect, test } from '@playwright/test'
import { loadFixtures, login, trainerChatUrl } from './helpers'

test.describe('SMOKE_TRAINER_CHAT_PROVISIONAL_IMPORT', () => {
  test('trainer opens provisional resource import modal and confirms', async ({ page }) => {
    const fx = loadFixtures()
    const trainerSessionId = fx.trainer_session_id
    test.skip(!trainerSessionId, 'trainer_session_id missing — rerun bootstrap_smoke_playwright')

    await login(
      page,
      fx.users.smoke_trainer,
      fx.password,
      trainerChatUrl(trainerSessionId),
    )

    const provisionalBtn = page.getByTestId('import-from-chat-trainer_resource_provisional')
    await expect(provisionalBtn).toBeVisible({ timeout: 15_000 })
    await provisionalBtn.click()

    const modal = page.getByTestId('trainer-import-confirm-modal')
    await expect(modal).toBeVisible()
    await expect(modal.getByText(/ressource provisoire/i)).toBeVisible()
    await expect(modal.getByText(/Créé depuis chat/i)).toBeVisible()

    await modal.locator('#import-draft-title').fill('Cas-type audit provisoire')
    await modal.locator('#import-draft-body').fill('Contenu ressource provisoire depuis chat.')

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
