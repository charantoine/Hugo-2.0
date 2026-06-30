import { test, expect } from '@playwright/test'
import { login } from '../helpers'

const SUPERADMIN_USER = process.env.SMOKE_SUPERADMIN_USER || 'demo.superadmin'
const SUPERADMIN_PASS = process.env.SMOKE_SUPERADMIN_PASS || 'DemoHugo123!'
const TRAINER_USER = process.env.SMOKE_TRAINER_USER || 'demo.formateur'
const TRAINER_PASS = process.env.SMOKE_TRAINER_PASS || 'DemoHugo123!'

test.describe('Multi-tenant admin UI', () => {
  test.skip(!process.env.SMOKE_RUN_TENANT, 'Set SMOKE_RUN_TENANT=1 with backend + demo accounts')

  test('SUPERADMIN sees organisations nav and tenant switcher', async ({ page }) => {
    await login(page, SUPERADMIN_USER, SUPERADMIN_PASS, '/groups-admin')
    await expect(page.getByRole('link', { name: 'Organisations' })).toBeVisible()
    await expect(page.locator('#tenant-switcher')).toBeVisible()
    await expect(page.getByText('SUPERADMIN')).toBeVisible()
  })

  test('SUPERADMIN can open organisations list', async ({ page }) => {
    await login(page, SUPERADMIN_USER, SUPERADMIN_PASS, '/admin/organisations')
    await expect(page.getByRole('heading', { name: 'Organisations' })).toBeVisible()
    await expect(page.getByText('Vue multi-organisation')).toBeVisible()
  })

  test('non-SUPERADMIN does not see organisations nav or tenant switcher', async ({ page }) => {
    await login(page, TRAINER_USER, TRAINER_PASS, '/groups-admin')
    await expect(page.getByRole('link', { name: 'Organisations' })).toHaveCount(0)
    await expect(page.locator('#tenant-switcher')).toHaveCount(0)
  })

  test('non-SUPERADMIN direct URL to organisations detail is blocked', async ({ page }) => {
    await login(page, TRAINER_USER, TRAINER_PASS, '/dashboard')
    await page.goto('/admin/organisations/00000000-0000-0000-0000-000000000001')
    await expect(page).not.toHaveURL(/admin\/organisations/)
  })
})
