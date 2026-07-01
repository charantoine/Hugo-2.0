import { expect, test } from '@playwright/test'
import { loadFixtures, login, trainerChatUrl } from './helpers'

test.describe('SMOKE_TRAINER_CHAT_RATIONALE_IMPORT', () => {
  test('trainer attaches draft justification to existing knowledge item', async ({ page }) => {
    const fx = loadFixtures()
    const trainerSessionId = fx.trainer_session_id
    const knowledgeItemId = fx.knowledge_item_id
    test.skip(!trainerSessionId || !knowledgeItemId, 'fixtures missing — rerun bootstrap_smoke_playwright')

    await login(
      page,
      fx.users.smoke_trainer,
      fx.password,
      trainerChatUrl(trainerSessionId),
    )

    const rationaleBtn = page.getByTestId('import-from-chat-trainer_decision_rationale')
    await expect(rationaleBtn).toBeVisible({ timeout: 15_000 })
    await rationaleBtn.click()

    const modal = page.getByTestId('trainer-import-confirm-modal')
    await expect(modal).toBeVisible()
    await expect(modal.getByText(/justification d'arbitrage/i)).toBeVisible()
    await expect(modal.getByText(/brouillon d’aide à la décision/i)).toBeVisible()
    await expect(modal.getByText(/ne modifie pas le statut/i)).toBeVisible()

    await modal.getByTestId('rationale-target-item').selectOption(String(knowledgeItemId))
    await modal.locator('#rationale-decision').fill('Laisser provisoire')
    await modal.locator('#rationale-reasons').fill('Relecture collective nécessaire')

    await Promise.all([
      page.waitForResponse(
        (response) => response.url().includes(`/hugo/trainer/knowledge-items/${knowledgeItemId}/`)
          && response.request().method() === 'PATCH'
          && response.status() === 200,
      ),
      modal.getByTestId('trainer-import-confirm-btn').click(),
    ])

    await expect(page.getByText(/Import enregistré/i)).toBeVisible({ timeout: 10_000 })

    await page.goto('/app/trainer/knowledge')
    await expect(page.getByTestId('trainer-decision-rationale-summary')).toBeVisible({ timeout: 10_000 })
    await expect(page.getByText('Laisser provisoire')).toBeVisible()
    await expect(page.getByText('Relecture collective nécessaire')).toBeVisible()
  })
})
