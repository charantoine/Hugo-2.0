/** TUTOR — panneau mémoire lecture seule, non injectée LLM. */
import { expect, test } from '@playwright/test'
import { loadFixtures, login } from './helpers'

test.describe('TUTOR_MEMORY_READONLY_PANEL', () => {
  test('context panel states non-injection and ACL boundary', async ({ page }) => {
    const fx = loadFixtures()
    await login(
      page,
      fx.users.smoke_tutor,
      fx.password,
      `/app/tutor/group/${fx.group_id}/learner/${fx.learner_id}`,
    )

    await page.getByTestId('tutor-cta-tutor_workspace_prep').click()
    await expect(page).toHaveURL(/\/app\/session\//, { timeout: 15_000 })

    const panel = page.getByTestId('tutor-workspace-context-panel')
    await expect(panel).toBeVisible()
    await expect(panel.getByText(/non injecté dans le prompt LLM/i)).toBeVisible()
    await expect(panel.getByText(/memory-summary|session apprenant liée/i)).toBeVisible()
  })
})
