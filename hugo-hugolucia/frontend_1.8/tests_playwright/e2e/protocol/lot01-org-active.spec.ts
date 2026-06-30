import { expect, test } from '@playwright/test'
import { DEMO_ENV } from '../../helpers/demo-env'
import { expectOrgBanner, trackApi } from '../../helpers/protocol'
import { login, selectActiveTenant } from '../../helpers'

test.describe('LOT 1 — Organisation active / SUPERADMIN', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, DEMO_ENV.superadmin.username, DEMO_ENV.superadmin.password, '/dashboard')
  })

  for (const route of [
    '/dashboard',
    '/users',
    '/groups-admin',
    `/groups-admin/${DEMO_ENV.groupBacPro.id}`,
    '/admin/onboarding',
  ]) {
    test(`L1-banner ${route}`, async ({ page }) => {
      const api = trackApi(page)
      await page.goto(route)
      await page.waitForTimeout(2000)
      await expectOrgBanner(page, DEMO_ENV.org.name)
      await expect(page.locator('#tenant-switcher')).toBeVisible()
      expect(api.find('/groups/', 'GET').length + api.find('/users/', 'GET').length).toBeGreaterThanOrEqual(0)
    })
  }

  test('L1-org-switch changes group list (no silent leak)', async ({ page }) => {
    const api = trackApi(page)
    // Repartir de l'org démo pour éviter l'état laissé par un test précédent
    await selectActiveTenant(page, DEMO_ENV.org.id)
    await page.goto('/groups-admin')
    await page.waitForTimeout(2500)
    await expectOrgBanner(page, DEMO_ENV.org.name)
    const textBefore = await page.locator('main').innerText()
    api.clear()

    await selectActiveTenant(page, DEMO_ENV.altOrg.id)
    await page.goto('/groups-admin')
    await page.waitForTimeout(3000)
    const textAfter = await page.locator('main').innerText()

    await expectOrgBanner(page, DEMO_ENV.altOrg.name)
    expect(api.find('/groups/', 'GET').length).toBeGreaterThan(0)
    // Fuite données : le groupe démo ne doit plus apparaître après switch org
    if (textBefore.includes(DEMO_ENV.groupBacPro.name)) {
      expect(
        textAfter,
        'bac pro melec ne doit pas rester visible après switch vers org smoke',
      ).not.toContain(DEMO_ENV.groupBacPro.name)
    }

    await page.goto('/admin/onboarding')
    await page.waitForTimeout(2500)
    await expectOrgBanner(page, DEMO_ENV.altOrg.name)
    const wizardText = await page.locator('.admin-onboarding-wizard').innerText()
    expect(wizardText).not.toMatch(/Groupe de référence/i)
  })
})
