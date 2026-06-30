/**
 * E2E UX — fiabilité formateur (* ** *** ****) sur la bibliothèque.
 *
 * Prérequis : bootstrap_smoke_playwright + backend local via proxy Vite.
 */
import { expect, test } from '@playwright/test'
import { loadFixtures, login, setTenantOrg } from '../helpers'

test.describe('Trainer library reliability UX', () => {
  test('TLIB-REL-01 create form shows reliability buttons and sends trainer_reliability', async ({
    page,
  }) => {
    const fx = loadFixtures()
    const uniqueTitle = `E2E Rel Create ${Date.now()}`

    await login(page, fx.users.smoke_trainer, fx.password, `/app/trainer/library?groupId=${fx.group_id}`)
    await setTenantOrg(page, fx.organisation_id)
    await page.reload()

    await expect(page.getByRole('heading', { name: 'Bibliothèque de cours' })).toBeVisible()
    const reliabilityGroup = page.getByRole('group', { name: 'Fiabilité' })
    await expect(reliabilityGroup).toBeVisible()
    const star4 = reliabilityGroup.getByRole('button', { name: '****' })
    await expect(star4).toBeVisible()
    await star4.click()
    await expect(star4).toHaveClass(/btn-primary/)

    await page.getByPlaceholder('Titre').fill(uniqueTitle)
    await page.getByPlaceholder(/Texte brut/).fill('procedure tableau electrique consignation verification')

    const createResponse = page.waitForResponse(
      (response) =>
        response.url().includes('/documents/') &&
        response.request().method() === 'POST' &&
        !response.url().includes('/index/'),
    )
    await page.getByRole('button', { name: 'Créer et indexer' }).click()
    const created = await createResponse
    expect(created.status()).toBeGreaterThanOrEqual(200)
    expect(created.status()).toBeLessThan(300)

    const requestBody = created.request().postDataJSON?.() as { meta?: { trainer_reliability?: string } } | null
    const responseBody = (await created.json()) as { meta?: { trainer_reliability?: string; origin?: string } }
    const reliability =
      requestBody?.meta?.trainer_reliability ?? responseBody.meta?.trainer_reliability
    expect(reliability).toBe('4')
    expect(responseBody.meta?.origin).toBe('trainer')
  })

  test('TLIB-REL-02 inline reliability persists after reload', async ({ page }) => {
    const fx = loadFixtures()
    const uniqueTitle = `E2E Rel Persist ${Date.now()}`

    await login(page, fx.users.smoke_trainer, fx.password, `/app/trainer/library?groupId=${fx.group_id}`)
    await setTenantOrg(page, fx.organisation_id)
    await page.reload()

    await page.getByPlaceholder('Titre').fill(uniqueTitle)
    await page.getByPlaceholder(/Texte brut/).fill('procedure tableau electrique')
    await page.getByRole('group', { name: 'Fiabilité' }).getByRole('button', { name: '***', exact: true }).click()
    await page.getByRole('button', { name: 'Créer et indexer' }).click()
    await expect(page.getByText(uniqueTitle).first()).toBeVisible({ timeout: 25_000 })

    const row = page.locator('tr', { hasText: uniqueTitle })
    const patchResponse = page.waitForResponse(
      (response) =>
        response.url().includes('/documents/') && response.request().method() === 'PATCH',
    )
    const reindexResponse = page.waitForResponse(
      (response) =>
        response.url().includes('/index/') && response.request().method() === 'POST',
    )
    await row.locator('select').filter({ has: page.locator('option[value="4"]') }).selectOption('4')
    await patchResponse
    await reindexResponse

    await page.reload()
    await expect(page.getByText(uniqueTitle).first()).toBeVisible({ timeout: 20_000 })
    const reloadedRow = page.locator('tr', { hasText: uniqueTitle })
    await expect(reloadedRow.locator('select').filter({ has: page.locator('option[value="4"]') })).toHaveValue('4')
  })
})
