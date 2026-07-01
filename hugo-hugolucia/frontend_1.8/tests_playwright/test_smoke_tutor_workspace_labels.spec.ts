/** TUTOR — alias workspace labels (baseline B). */
import { expect, test } from '@playwright/test'
import { loadFixtures, login } from './helpers'

test.describe('SMOKE_TUTOR_WORKSPACE_LABELS', () => {
  test('pure tutor home invites learner selection', async ({ page }) => {
    const fx = loadFixtures()
    await login(page, fx.users.smoke_tutor, fx.password, '/app/tutor')
    await expect(page.getByText(/Choisissez un groupe et un apprenant/i)).toBeVisible()
    await expect(page.getByRole('banner').getByRole('link', { name: 'Mon espace de réflexion' })).toBeVisible()
  })
})
