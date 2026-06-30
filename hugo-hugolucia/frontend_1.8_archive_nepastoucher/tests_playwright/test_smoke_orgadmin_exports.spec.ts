import { expect, test } from '@playwright/test'
import { loadFixtures, login } from './helpers'

test.describe('SMOKE_ORGADMIN_EXPORTS', () => {
  test('orgadmin sees export CTAs on group page', async ({ page }) => {
    const fx = loadFixtures()
    const groupPath = `/group/${fx.group_id}`
    await login(page, fx.users.smoke_orgadmin, fx.password, groupPath)

    await expect(page.getByRole('button', { name: /JSON trace_rich_v1/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /CSV principal/i })).toBeVisible()
    await expect(page.getByText('Exports Felix-ready')).toBeVisible()
  })

  test('learner does not see export CTAs', async ({ page }) => {
    const fx = loadFixtures()
    const groupPath = `/group/${fx.group_id}`
    await login(page, fx.users.smoke_learner, fx.password, groupPath)

    await expect(page.getByRole('button', { name: /JSON trace_rich_v1/i })).toHaveCount(0)
    await expect(page.getByRole('button', { name: /CSV principal/i })).toHaveCount(0)
  })
})
