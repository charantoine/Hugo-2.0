/** TUTOR — flux aide au diagnostic. */
import { expect, test } from '@playwright/test'
import { loadFixtures, openTutorWorkspaceCta } from './helpers'

test.describe('TUTOR_DIAGNOSTIC_FLOW', () => {
  test('diagnostic CTA opens workspace chat', async ({ page }) => {
    const fx = loadFixtures()
    await openTutorWorkspaceCta(page, fx, 'tutor_workspace_diagnostic')
    await expect(page.getByTestId('tutor-workspace-context-panel')).toBeVisible()
    await expect(page.getByText(/Aide au diagnostic/i)).toBeVisible()
  })
})
