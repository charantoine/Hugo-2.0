/** TUTOR — flux co-réflexion assistée. */
import { expect, test } from '@playwright/test'
import { loadFixtures, openTutorWorkspaceCta } from './helpers'

test.describe('TUTOR_COREFLEX_FLOW', () => {
  test('coreflex CTA opens workspace chat', async ({ page }) => {
    const fx = loadFixtures()
    await openTutorWorkspaceCta(page, fx, 'tutor_workspace_coreflex')
    await expect(page.getByTestId('tutor-workspace-context-panel')).toBeVisible()
    await expect(page.getByText(/Co-réflexion assistée/i)).toBeVisible()
  })
})
