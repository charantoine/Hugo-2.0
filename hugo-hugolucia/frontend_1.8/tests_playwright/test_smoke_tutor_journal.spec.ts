import { expect, test } from '@playwright/test'
import { loadFixtures, login, tutorChatUrl } from './helpers'

test.describe('SMOKE_TUTOR_JOURNAL', () => {
  test('tutor saves journal draft in current session', async ({ page }) => {
    const fx = loadFixtures()
    const sessionId = fx.tutor_workspace_session_id
    test.skip(!sessionId, 'tutor_workspace_session_id missing — rerun bootstrap_smoke_playwright')

    await login(
      page,
      fx.users.smoke_tutor,
      fx.password,
      tutorChatUrl(sessionId, fx, 'tutor_workspace_journal'),
    )

    const journalBtn = page.getByTestId('tutor-import-from-chat-tutor_journal_entry')
    await expect(journalBtn).toBeVisible({ timeout: 15_000 })
    await journalBtn.click()

    const modal = page.getByTestId('tutor-import-confirm-modal')
    await expect(modal).toBeVisible()
    await modal.locator('#tutor-journal-summary').fill('Point-clé smoke journal tuteur')
    await modal.getByTestId('tutor-import-confirm-btn').click()

    await expect(page.getByText(/Brouillon enregistré/i)).toBeVisible({ timeout: 10_000 })
    await expect(page.getByTestId('tutor-session-drafts-panel')).toBeVisible()
    await expect(page.getByText('Point-clé smoke journal tuteur')).toBeVisible()
  })
})
