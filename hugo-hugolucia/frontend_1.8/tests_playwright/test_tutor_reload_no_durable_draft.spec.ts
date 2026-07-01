/** TUTOR — P1 brouillon non durable après reload. */
import { expect, test } from '@playwright/test'
import { loadFixtures, login, tutorChatUrl } from './helpers'

test.describe('TUTOR_RELOAD_NO_DURABLE_DRAFT', () => {
  test('journal draft disappears after page reload', async ({ page }) => {
    const fx = loadFixtures()
    const sessionId = fx.tutor_workspace_session_id
    test.skip(!sessionId, 'tutor_workspace_session_id missing')

    const url = tutorChatUrl(sessionId, fx, 'tutor_workspace_journal')
    await login(page, fx.users.smoke_tutor, fx.password, url)

    await page.getByTestId('tutor-import-from-chat-tutor_journal_entry').click()
    const modal = page.getByTestId('tutor-import-confirm-modal')
    await modal.locator('#tutor-journal-summary').fill('Draft volatile reload test')
    await modal.getByTestId('tutor-import-confirm-btn').click()
    await expect(page.getByText('Draft volatile reload test')).toBeVisible()

    await page.reload()
    await expect(page.getByText('Draft volatile reload test')).toHaveCount(0)
    await expect(page.getByTestId('tutor-session-drafts-panel')).toHaveCount(0)
  })
})
