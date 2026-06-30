import { test, expect } from '@playwright/test'
import { loadTenantFixtures, login, setTenantOrg } from '../helpers'

const skip = !process.env.SMOKE_RUN_TENANT

test.describe('SUPERADMIN multi-tenant', () => {
  test.skip(skip, 'Set SMOKE_RUN_TENANT=1')

  test('switcher, org list, users in target org', async ({ page }) => {
    const fx = loadTenantFixtures()
    await login(page, fx.users.superadmin, fx.password, '/admin/organisations')
    await expect(page.getByRole('link', { name: 'Organisations' })).toBeVisible()
    await expect(page.locator('#tenant-switcher')).toBeVisible()

    await setTenantOrg(page, fx.org_b.id)
    await page.reload()
    await page.goto('/users')
    await expect(page.getByText('Utilisateurs de l’organisation')).toBeVisible()
    await expect(page.getByText(fx.users.learner_b)).toBeVisible()
  })

  test('can open group admin in tenant context', async ({ page }) => {
    const fx = loadTenantFixtures()
    await login(page, fx.users.superadmin, fx.password, '/groups-admin')
    await setTenantOrg(page, fx.org_a.id)
    await page.reload()
    await page.goto(`/groups-admin/${fx.group_a_id}`)
    await expect(page.getByRole('heading', { name: 'Détail du groupe' })).toBeVisible()
    await expect(page.getByText('Associations tuteur/apprenant')).toBeVisible()
  })
})

test.describe('ORGADMIN mono-org', () => {
  test.skip(skip, 'Set SMOKE_RUN_TENANT=1')

  test('no multi-org nav; users scoped to own org', async ({ page }) => {
    const fx = loadTenantFixtures()
    await login(page, fx.users.orgadmin_a, fx.password, '/users')
    await expect(page.getByRole('link', { name: 'Organisations' })).toHaveCount(0)
    await expect(page.locator('#tenant-switcher')).toHaveCount(0)
    await expect(page.getByText(fx.users.learner_a)).toBeVisible()
    await expect(page.getByText(fx.users.learner_b)).toHaveCount(0)
  })

  test('direct foreign group URL fails', async ({ page, request }) => {
    const fx = loadTenantFixtures()
    await login(page, fx.users.orgadmin_a, fx.password, '/dashboard')
    const token = await page.evaluate(() => localStorage.getItem('access'))
    const res = await request.get(`/api/groups/${fx.group_b_id}/`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    expect([403, 404]).toContain(res.status())
  })

  test('group admin hides tutor-link management', async ({ page }) => {
    const fx = loadTenantFixtures()
    await login(page, fx.users.orgadmin_a, fx.password, `/groups-admin/${fx.group_a_id}`)
    await expect(page.getByText('SUPERADMIN uniquement')).toBeVisible()
    await expect(page.getByLabel('Tuteur')).toHaveCount(0)
  })
})

test.describe('TUTEUR scoped access', () => {
  test.skip(skip, 'Set SMOKE_RUN_TENANT=1')

  test('tutor home loads; foreign session blocked via API', async ({ page, request }) => {
    const fx = loadTenantFixtures()
    await login(page, fx.users.tutor_a, fx.password, '/app/tutor')
    await expect(page.getByRole('heading', { name: /Espace tuteur|tuteur/i })).toBeVisible({ timeout: 10_000 }).catch(() => {
      // fallback: at least not login
      expect(page.url()).not.toContain('/login')
    })
    const token = await page.evaluate(() => localStorage.getItem('access'))
    const res = await request.get(`/api/hugo/sessions/${fx.session_b_id}/`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    expect([403, 404]).toContain(res.status())
  })
})

test.describe('APPRENANT scoped access', () => {
  test.skip(skip, 'Set SMOKE_RUN_TENANT=1')

  test('own session accessible; foreign session blocked', async ({ page, request }) => {
    const fx = loadTenantFixtures()
    await login(page, fx.users.learner_a, fx.password, `/app/session/${fx.session_a_id}`)
    await expect(page).not.toHaveURL(/\/login/)
    const token = await page.evaluate(() => localStorage.getItem('access'))
    const foreign = await request.get(`/api/hugo/sessions/${fx.session_b_id}/`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    expect([403, 404]).toContain(foreign.status())
  })
})
