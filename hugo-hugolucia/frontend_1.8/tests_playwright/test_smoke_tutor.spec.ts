import { expect, test } from '@playwright/test'
import { loadFixtures, login } from './helpers'

test.describe('SMOKE_TUTOR', () => {
  test('tutor sees timeline without private verbatim', async ({ page }) => {
    const fx = loadFixtures()
    await login(page, fx.users.smoke_tutor, fx.password, '/app/tutor')

    await expect(page.getByRole('heading', { name: 'Espace tuteur' })).toBeVisible()
    await expect(page.getByText('sans verbatim non partagé')).toBeVisible()

    await page.getByRole('button', { name: 'Voir les apprenants' }).first().click()
    await expect(page.getByRole('heading', { name: /Apprenants/ })).toBeVisible()

    await page.getByRole('button', { name: 'Timeline' }).first().click()
    await expect(page.getByText('Timeline (sessions & traces)')).toBeVisible()

    const body = await page.locator('body').innerText()
    expect(body).not.toContain(fx.verbatim_marker)

    await expect(page.getByText('Traces').or(page.getByText('Validé')).first()).toBeVisible()
  })
})
