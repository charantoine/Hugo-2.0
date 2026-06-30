import { expect, test } from '@playwright/test'
import { DEMO_ENV } from '../../helpers/demo-env'
import { expectOrgBanner, trackApi } from '../../helpers/protocol'
import { login } from '../../helpers'

test.describe('LOT 2 — Wizard admin généralisé', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, DEMO_ENV.superadmin.username, DEMO_ENV.superadmin.password)
    await page.evaluate((orgId) => {
      localStorage.setItem('hugo_active_organisation_id', orgId)
    }, DEMO_ENV.org.id)
  })

  test('L2-scope org + groupe à configurer + pas de référence démo', async ({ page }) => {
    const api = trackApi(page)
    await page.goto('/admin/onboarding')
    await page.waitForTimeout(3000)

    const text = await page.locator('.admin-onboarding-wizard').innerText()
    expect(text).toContain('Ce parcours concerne cette organisation')
    expect(text).not.toMatch(/Groupe de référence/i)
    await expectOrgBanner(page, DEMO_ENV.org.name)
    await expect(page.getByTestId('wizard-group-select')).toBeVisible()
    expect(api.find('/groups/', 'GET').length).toBeGreaterThan(0)
    expect(api.find('/users/', 'GET').length).toBeGreaterThan(0)
  })

  test('L2-query groupId pré-sélectionne le groupe', async ({ page }) => {
    await page.goto(`/admin/onboarding?groupId=${DEMO_ENV.groupBacPro.id}`)
    await page.waitForTimeout(3000)
    const val = await page.getByTestId('wizard-group-select').inputValue()
    expect(val).toBe(DEMO_ENV.groupBacPro.id)
    const stepText = await page.locator('.onboarding-step').nth(1).innerText()
    expect(stepText.toLowerCase()).toContain('bac pro melec')
  })

  test('L2-changer groupe recalcule étape Groupe', async ({ page }) => {
    await page.goto('/admin/onboarding')
    await page.waitForTimeout(3000)
    const sel = page.getByTestId('wizard-group-select')
    const options = await sel.locator('option').all()
    if (options.length < 2) {
      test.skip(true, 'Moins de 2 groupes — skip recalcul')
      return
    }
    const secondVal = await options[1].getAttribute('value')
    const secondLabel = (await options[1].textContent())?.trim() || ''
    await sel.selectOption(secondVal!)
    await page.waitForTimeout(2000)
    const stepText = await page.locator('.onboarding-step').nth(1).innerText()
    expect(stepText).toContain(secondLabel)
  })

  test('L2-CTA conversation -> fiche groupe admin', async ({ page }) => {
    await page.goto(`/admin/onboarding?groupId=${DEMO_ENV.groupBacPro.id}`)
    await page.waitForTimeout(3000)

    const cta = page.getByTestId('wizard-conversation-cta')
    await expect(cta).toBeVisible()
    const href = await cta.getAttribute('href')
    expect(href).toContain(`/groups-admin/${DEMO_ENV.groupBacPro.id}`)
    expect(href).toContain('section=conversation')

    await cta.click()
    await page.waitForURL(new RegExp(`/groups-admin/${DEMO_ENV.groupBacPro.id}`), { timeout: 10_000 })
    await expect(page.locator('#conversation-apprenant')).toBeVisible()
    await expect(page.locator('#default-learner-profile')).toBeVisible()

    const secondary = page.getByTestId('wizard-conversation-profiles-secondary')
    await expect(secondary).toBeVisible()
    const secondaryHref = await secondary.getAttribute('href')
    expect(secondaryHref).toContain('/admin/conversation/learner/profiles')
    expect(secondaryHref).toContain(`groupId=${DEMO_ENV.groupBacPro.id}`)
  })

  test('L2-CTA créer groupe -> /groups-admin', async ({ page }) => {
    await page.goto('/admin/onboarding')
    await page.waitForTimeout(1500)
    const createLink = page.getByRole('link', { name: /Créer un groupe|Gérer les groupes/i }).first()
    if (await createLink.isVisible()) {
      const href = await createLink.getAttribute('href')
      expect(href).toContain('/groups-admin')
    }
  })
})
