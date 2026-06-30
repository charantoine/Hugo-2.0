import { expect, test } from '@playwright/test'
import { loadTenantFixtures, login, setTenantOrg } from '../helpers'

const skip = !process.env.SMOKE_RUN_TENANT

test.describe('Conversation pipeline admin E2E', () => {
  test.skip(skip, 'Set SMOKE_RUN_TENANT=1')

  test('SUPERADMIN creates profile in tenant org and assigns to group', async ({ page }) => {
    const fx = loadTenantFixtures()
    const profileName = `Pipe E2E ${Date.now()}`

    await login(page, fx.users.superadmin, fx.password, '/admin/conversation/learner/profiles')
    await setTenantOrg(page, fx.org_a.id)
    await page.reload()

    await page.getByTestId('learner-profile-create-btn').click()
    await page.getByTestId('learner-profile-name-input').fill(profileName)
    await page.getByTestId('learner-profile-save-btn').click()
    await expect(page.getByRole('heading', { name: 'Édition du profil' })).toBeVisible({ timeout: 15_000 })

    await page.goto(`/groups-admin/${fx.group_a_id}`)
    await expect(page.getByRole('heading', { name: 'Détail du groupe' })).toBeVisible()

    const select = page.locator('#default-learner-profile')
    await select.selectOption({ label: profileName })
    await expect(select).not.toHaveValue('')

    await page.reload()
    await expect(select.locator('option:checked')).toContainText(profileName)
  })

  test('admin hub exposes learner profile and legacy LLM routes', async ({ page }) => {
    const fx = loadTenantFixtures()
    await login(page, fx.users.orgadmin_a, fx.password, '/admin/conversation')

    await expect(page.getByRole('heading', { name: 'Profils conversationnels' })).toBeVisible()
    await expect(page.getByRole('link', { name: /Catalogue LLM/i })).toBeVisible()
    await expect(page.getByRole('link', { name: /Prompts apprenant/i })).toBeVisible()
  })
})
