import { expect, test } from '@playwright/test'
import { loadTenantFixtures, login } from '../helpers'

const skip = !process.env.SMOKE_RUN_TENANT

test.describe('Admin learner conversation profiles', () => {
  test.skip(skip, 'Set SMOKE_RUN_TENANT=1')

  test.beforeEach(async ({ page }) => {
    const fx = loadTenantFixtures()
    await login(page, fx.users.orgadmin_a, fx.password, '/admin/conversation/learner/profiles')
  })

  test('create button opens editor and saves a new profile', async ({ page }) => {
    await expect(page.getByTestId('learner-profiles-page')).toBeVisible()

    await page.getByTestId('learner-profile-create-btn').click()
    await expect(page.getByTestId('learner-profile-editor')).toBeVisible()

    const profileName = `Profil E2E ${Date.now()}`
    await page.getByTestId('learner-profile-name-input').fill(profileName)
    await page.getByTestId('learner-profile-save-btn').click()

    await expect(page.getByRole('heading', { name: 'Édition du profil' })).toBeVisible({ timeout: 15_000 })
    await expect(page.getByTestId('learner-profile-list-item').filter({ hasText: profileName })).toBeVisible()
  })

  test('legacy create opens editor', async ({ page }) => {
    await page.getByTestId('learner-profile-create-legacy-btn').click()
    await expect(page.getByTestId('learner-profile-editor')).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Nouveau profil global' })).toBeVisible()
  })
})
