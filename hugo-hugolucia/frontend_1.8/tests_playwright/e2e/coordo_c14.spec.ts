import { expect, test } from '@playwright/test'
import { loadFixtures, login } from '../helpers'

/** Persona COORDO (cluster 14) — héritage surfaces tuteur. */
test.describe('E2E_COORDO_C14', () => {
  test('C14-C1 coordo accesses tutor space', async ({ page }) => {
    const fx = loadFixtures()
    if (!fx.users.smoke_coordo) {
      test.skip(true, 'smoke_coordo not in fixtures — run bootstrap_smoke_playwright')
    }
    await login(page, fx.users.smoke_coordo, fx.password, '/app/tutor')

    await expect(page.getByRole('heading', { name: 'Espace tuteur' })).toBeVisible()
    await expect(page.getByText('sans verbatim non partagé')).toBeVisible()
  })
})
