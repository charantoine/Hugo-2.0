import { expect, test } from '@playwright/test'
import { loadFixtures, login } from './helpers'

test.describe('SMOKE_TUTOR_PREP', () => {
  test('tutor opens prep chat from learner fiche', async ({ page }) => {
    const fx = loadFixtures()
    test.skip(!fx.group_id || !fx.learner_id, 'fixtures missing')

    await login(
      page,
      fx.users.smoke_tutor,
      fx.password,
      `/app/tutor/group/${fx.group_id}/learner/${fx.learner_id}`,
    )

    const prepBtn = page.getByTestId('tutor-cta-tutor_workspace_prep')
    await expect(prepBtn).toBeVisible({ timeout: 15_000 })
    await prepBtn.click()

    await expect(page).toHaveURL(/\/app\/session\//, { timeout: 15_000 })
    await expect(page.getByTestId('tutor-workspace-context-panel')).toBeVisible()
    await expect(page.getByText(/Préparation d'entretien/i)).toBeVisible()
  })
})
