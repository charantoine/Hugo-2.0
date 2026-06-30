import { expect, test } from '@playwright/test'
import { DEMO_ENV } from '../../helpers/demo-env'
import { login } from '../../helpers'

test.describe('LOT 3 — Dashboard testeur / démo séparé', () => {
  test('L3-raccourci démo distinct du wizard', async ({ page }) => {
    await login(page, DEMO_ENV.superadmin.username, DEMO_ENV.superadmin.password, '/dashboard')
    const main = await page.locator('main').innerText()

    expect(main).toMatch(/Raccourci démo|raccourci de démonstration/i)
    expect(main).not.toMatch(/Groupe de référence/i)
    expect(main).toContain('Assistant de mise en route')

    await expect(page.getByTestId('dashboard-tester-canonical')).toBeVisible()
    await expect(page.getByTestId('dashboard-tester-exports')).toBeVisible()

    await page.getByTestId('dashboard-tester-canonical').click()
    await page.waitForURL(/\/group\/.*focus=calibration/, { timeout: 10_000 })
    expect(page.url()).toMatch(/\/group\//)
    expect(page.url()).toContain('focus=calibration')
    expect(page.url()).not.toContain('/admin/onboarding')

    await page.getByRole('heading', { name: /Apprenants du groupe/i }).scrollIntoViewIfNeeded()
    const learnersPanel = page.locator('#group-learners-panel')
    const exportsPanel = page.locator('#group-exports-panel')
    await expect(learnersPanel).toBeVisible()
    await expect(exportsPanel).not.toHaveAttribute('open')

    await page.goto('/dashboard')
    await page.getByTestId('dashboard-tester-exports').click()
    await page.waitForURL(/\/group\/.*focus=exports/, { timeout: 10_000 })
    await expect(page.locator('#group-exports-panel.card')).toBeVisible()

    await page.goto('/admin/onboarding')
    await page.waitForTimeout(2000)
    expect(await page.locator('.admin-onboarding-wizard').innerText()).not.toMatch(
      /Raccourci démo/i,
    )
  })
})
