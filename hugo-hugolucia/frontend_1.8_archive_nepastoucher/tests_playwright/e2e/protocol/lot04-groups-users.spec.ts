import { expect, test } from '@playwright/test'
import { DEMO_ENV } from '../../helpers/demo-env'
import { trackApi } from '../../helpers/protocol'
import { login } from '../../helpers'

test.describe('LOT 4 — Groupes / users (wire + persistance légère)', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, DEMO_ENV.superadmin.username, DEMO_ENV.superadmin.password)
    await page.evaluate((id) => localStorage.setItem('hugo_active_organisation_id', id), DEMO_ENV.org.id)
  })

  test('L4-users list wired to GET /users/', async ({ page }) => {
    const api = trackApi(page)
    await page.goto('/users')
    await page.waitForTimeout(2000)
    expect(api.find('/users/', 'GET').some((c) => c.status === 200)).toBeTruthy()
    await expect(page.getByRole('heading', { name: /Création de comptes/i })).toBeVisible()
  })

  test('L4-groups-admin list wired to GET /groups/', async ({ page }) => {
    const api = trackApi(page)
    await page.goto('/groups-admin')
    await page.waitForTimeout(2000)
    expect(api.find('/groups/', 'GET').some((c) => c.status === 200)).toBeTruthy()
  })

  test('L4-create group persists in list', async ({ page }) => {
    const groupName = `e2e_grp_${Date.now()}`
    const api = trackApi(page)
    await page.goto('/groups-admin')
    await page.waitForTimeout(1500)
    await page.getByLabel('Nom du groupe').fill(groupName)
    const createPromise = api.waitFor('/groups/', 'POST')
    await page.getByRole('button', { name: 'Créer le groupe' }).click()
    const created = await createPromise
    expect(created.status).toBeGreaterThanOrEqual(200)
    expect(created.status).toBeLessThan(300)
    await page.waitForTimeout(1500)
    await expect(page.getByRole('link', { name: new RegExp(groupName) })).toBeVisible()
  })

  test('L4-group detail members section loads', async ({ page }) => {
    const api = trackApi(page)
    await page.goto(`/groups-admin/${DEMO_ENV.groupBacPro.id}`)
    await page.waitForTimeout(3000)
    expect(api.find('/members/', 'GET').some((c) => c.status === 200)).toBeTruthy()
    await expect(page.getByRole('heading', { name: 'Cohorte' })).toBeVisible()
  })
})
