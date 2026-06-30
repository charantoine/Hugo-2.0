import { expect, test } from '@playwright/test'
import {
  loadFixtures,
  login,
  logout,
  selectActiveTenant,
  uniqueE2eUsername,
} from '../helpers'

test.describe('Admin TRAINER creation (/users)', () => {
  test('superadmin creates TRAINER, attaches to group, trainer accesses knowledge', async ({ page }) => {
    const fx = loadFixtures()
    const username = uniqueE2eUsername('e2e_trainer')
    const email = `${username}@smoke.local`

    // 1. Connexion superadmin
    await login(page, fx.users.smoke_superadmin, fx.password, '/dashboard')
    await expect(page.getByText('SUPERADMIN')).toBeVisible()

    // 2. Sélection du tenant actif (org smoke Playwright)
    await selectActiveTenant(page, fx.organisation_id)

    // 3. Ouverture /users
    await page.getByRole('link', { name: 'Utilisateurs' }).click()
    await expect(page.getByRole('heading', { name: 'Création de comptes' })).toBeVisible()
    await expect(page.locator('#tenant-switcher')).toHaveValue(fx.organisation_id)
    await expect(page.getByRole('main').getByText(fx.organisation_name)).toBeVisible()

    // 4. Création compte TRAINER
    await page.locator('#role').selectOption('TRAINER')
    await expect(page.getByRole('button', { name: 'Créer le formateur' })).toBeVisible()

    await page.getByLabel('Identifiant').fill(username)
    await page.getByLabel('Email').fill(email)
    await page.getByLabel('Prénom').fill('E2E')
    await page.getByLabel('Nom', { exact: true }).fill('Formateur')
    await page.getByLabel('Mot de passe', { exact: true }).fill(fx.password)

    const createResponse = page.waitForResponse(
      (response) => response.url().includes('/users/') && response.request().method() === 'POST',
    )
    await page.getByRole('button', { name: 'Créer le formateur' }).click()
    const response = await createResponse
    expect(response.status()).toBe(201)

    await expect(page.getByRole('alert').filter({ hasText: 'Compte formateur créé' })).toBeVisible()

    // 5. Vérification dans la liste (filtre Formateurs pour réduire le bruit)
    await page.locator('#role-filter').selectOption('TRAINER')
    const userRow = page.getByRole('listitem').filter({ hasText: email })
    await expect(userRow).toBeVisible()
    await expect(userRow.locator('span.badge.text-uppercase')).toHaveText('TRAINER')

    // 6. Rattachement au groupe existant (flux UserDetail)
    await userRow.getByRole('link').first().click()
    await expect(page.getByRole('heading', { name: 'Détail utilisateur' })).toBeVisible()
    await expect(page.locator('span.badge.text-uppercase')).toHaveText('TRAINER')

    await page.locator('#group').selectOption({ label: fx.group_name })
    const membershipResponse = page.waitForResponse(
      (res) => res.url().includes('/members/') && res.request().method() === 'POST',
    )
    await page.getByRole('button', { name: /Associer l.utilisateur au groupe/ }).click()
    expect((await membershipResponse).status()).toBe(201)
    await expect(page.getByRole('alert').filter({ hasText: 'Utilisateur associé au groupe' })).toBeVisible()

    // 7. Déconnexion superadmin
    await logout(page)

    // 8. Connexion avec le compte formateur créé
    await login(page, username, fx.password, '/app/trainer/knowledge')

    // 9–10. Surface formateur accessible (pas de rejet par guard de rôle)
    await expect(page).toHaveURL(/\/app\/trainer\/knowledge/)
    await expect(page.getByRole('heading', { name: 'Orchestrateur de connaissance' })).toBeVisible({
      timeout: 15_000,
    })
    await expect(page.getByRole('navigation').getByRole('link', { name: 'Espace formateur' })).toBeVisible()
    await expect(page.getByText('Smoke knowledge item for Playwright')).toBeVisible()
  })
})
