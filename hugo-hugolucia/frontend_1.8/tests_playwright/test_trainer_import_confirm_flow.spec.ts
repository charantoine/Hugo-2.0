/** TRAINER — import chat avec confirmation humaine. */
import { expect, test } from '@playwright/test'
import { expectNoLearnerWorkspaceBlocks, loadFixtures, login, trainerChatUrl } from './helpers'

test.describe('TRAINER_IMPORT_CONFIRM_FLOW', () => {
  test('explication import modal confirm writes knowledge item', async ({ page }) => {
    const fx = loadFixtures()
    const sessionId = fx.trainer_session_id
    test.skip(!sessionId, 'trainer_session_id missing')

    await login(page, fx.users.smoke_trainer, fx.password, trainerChatUrl(sessionId))

    await expectNoLearnerWorkspaceBlocks(page)

    const importBtn = page.getByTestId('import-from-chat-trainer_explication')
    await expect(importBtn).toBeVisible({ timeout: 15_000 })
    await importBtn.click()

    const modal = page.getByTestId('trainer-import-confirm-modal')
    await expect(modal).toBeVisible()
    await modal.getByTestId('trainer-import-confirm-btn').click()

    await expect(page.getByText(/Import enregistré/i)).toBeVisible({ timeout: 10_000 })
  })
})
