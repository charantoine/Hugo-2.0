/** TUTOR — flux préparation entretien. */
import { expect, test } from '@playwright/test'
import { loadFixtures, openTutorWorkspaceCta } from './helpers'

test.describe('TUTOR_PREP_FLOW', () => {
  test('prep CTA opens workspace chat with profile title', async ({ page }) => {
    const fx = loadFixtures()
    await openTutorWorkspaceCta(page, fx, 'tutor_workspace_prep')
    await expect(page.getByTestId('tutor-workspace-context-panel')).toBeVisible()
    await expect(page.getByText(/Préparation d'entretien/i)).toBeVisible()
  })
})
