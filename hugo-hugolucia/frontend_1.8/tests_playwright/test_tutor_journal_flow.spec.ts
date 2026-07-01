/** TUTOR — flux journal point-clé (brouillon session). */
import { expect, test } from '@playwright/test'
import { expectNoLearnerWorkspaceBlocks, loadFixtures, login, tutorChatUrl } from './helpers'

test.describe('TUTOR_JOURNAL_FLOW', () => {
  test('journal import saves in-session draft', async ({ page }) => {
    const fx = loadFixtures()
    const sessionId = fx.tutor_workspace_session_id
    test.skip(!sessionId, 'tutor_workspace_session_id missing — rerun bootstrap_smoke_playwright')

    await login(
      page,
      fx.users.smoke_tutor,
      fx.password,
      tutorChatUrl(sessionId, fx, 'tutor_workspace_journal'),
    )

    await expectNoLearnerWorkspaceBlocks(page)

    await page.getByTestId('tutor-import-from-chat-tutor_journal_entry').click()
    const modal = page.getByTestId('tutor-import-confirm-modal')
    await expect(modal).toBeVisible()
    await modal.locator('#tutor-journal-summary').fill('Journal flow smoke')
    await modal.getByTestId('tutor-import-confirm-btn').click()

    await expect(page.getByText(/Brouillon enregistré/i)).toBeVisible()
    await expect(page.getByTestId('tutor-session-drafts-panel')).toBeVisible()
    await expect(page.getByText('Journal flow smoke')).toBeVisible()
  })
})
