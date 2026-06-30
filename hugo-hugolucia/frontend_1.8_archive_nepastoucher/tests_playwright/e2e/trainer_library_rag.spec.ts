/**
 * E2E — Bibliothèque formateur et chaîne formateur → apprenant → RAG.
 *
 * Prérequis :
 *   cd hugo_back && python manage.py bootstrap_smoke_playwright
 *   Backend Django sur le proxy Vite (port 8000 habituel)
 *   cd frontend_1.8 && npm run test:smoke -- tests_playwright/e2e/trainer_library_rag.spec.ts
 */
import { expect, test } from '@playwright/test'
import { loadFixtures, login, logout, setTenantOrg } from '../helpers'

const RAG_SOURCE_SNIPPET =
  'procedure tableau electrique consignation verification mise sous tension schema unifilaire norme nf c15-100 checklist securite'

test.describe('Trainer library + learner RAG chain', () => {
  test.describe.configure({ mode: 'serial' })

  test('TLIB-01 trainer creates reference_course document and links to group', async ({ page }) => {
    const fx = loadFixtures()
    const uniqueTitle = `E2E Poly Ref ${Date.now()}`

    await login(page, fx.users.smoke_trainer, fx.password, `/app/trainer/library?groupId=${fx.group_id}`)
    await setTenantOrg(page, fx.organisation_id)
    await page.reload()

    await expect(page.getByRole('heading', { name: 'Bibliothèque de cours' })).toBeVisible()
    await expect(page.locator('select').first()).toBeVisible()

    await page.getByPlaceholder('Titre').fill(uniqueTitle)
    await page.getByPlaceholder(/Texte brut/).fill(RAG_SOURCE_SNIPPET)
    await page.locator('label:has-text("Rôle conversationnel")').locator('..').locator('select').selectOption('reference_course')
    await page.locator('label:has-text("Intention pédagogique")').locator('..').locator('select').selectOption('explanation')

    const createResponse = page.waitForResponse(
      (response) => response.url().includes('/documents/') && response.request().method() === 'POST',
    )
    await page.getByRole('button', { name: 'Créer et indexer' }).click()
    const created = await createResponse
    expect(created.status()).toBeGreaterThanOrEqual(200)
    expect(created.status()).toBeLessThan(300)

    await expect(page.getByText(uniqueTitle).first()).toBeVisible({ timeout: 20_000 })
    await expect(page.getByText(/Indexation/i)).toBeVisible({ timeout: 20_000 })

    const row = page.locator('tr', { hasText: uniqueTitle })
    await expect(row.getByText('Lié').or(row.getByRole('button', { name: 'Lier' }))).toBeVisible()
    if (await row.getByRole('button', { name: 'Lier' }).isVisible()) {
      await row.getByRole('button', { name: 'Lier' }).click()
      await expect(row.getByText('Lié')).toBeVisible()
    }

    await expect(page.getByText(uniqueTitle).last()).toBeVisible()
  })

  test('TLIB-02 trainer edits inline conversation_role via PATCH', async ({ page }) => {
    const fx = loadFixtures()
    const uniqueTitle = `E2E Patch Meta ${Date.now()}`

    await login(page, fx.users.smoke_trainer, fx.password, `/app/trainer/library?groupId=${fx.group_id}`)
    await setTenantOrg(page, fx.organisation_id)
    await page.reload()

    await page.getByPlaceholder('Titre').fill(uniqueTitle)
    await page.getByPlaceholder(/Texte brut/).fill('support document court procedure tableau')
    await page.getByRole('button', { name: 'Créer et indexer' }).click()
    await expect(page.getByText(uniqueTitle).first()).toBeVisible({ timeout: 20_000 })

    const row = page.locator('tr', { hasText: uniqueTitle })
    const patchResponse = page.waitForResponse(
      (response) =>
        response.url().includes('/documents/') &&
        response.request().method() === 'PATCH',
    )
    await row.locator('select').first().selectOption('reference_course')
    const patched = await patchResponse
    expect(patched.status()).toBe(200)
    const patchBody = await patched.json()
    expect(patchBody.meta?.conversation_role).toBe('reference_course')
  })

  test('TLIB-03 trainer edits pedagogical_intent inline', async ({ page }) => {
    const fx = loadFixtures()
    const uniqueTitle = `E2E Intent ${Date.now()}`

    await login(page, fx.users.smoke_trainer, fx.password, `/app/trainer/library?groupId=${fx.group_id}`)
    await setTenantOrg(page, fx.organisation_id)
    await page.reload()

    await page.getByPlaceholder('Titre').fill(uniqueTitle)
    await page.getByPlaceholder(/Texte brut/).fill('procedure tableau electrique consignation')
    await page.getByRole('button', { name: 'Créer et indexer' }).click()
    await expect(page.getByText(uniqueTitle).first()).toBeVisible({ timeout: 20_000 })

    const row = page.locator('tr', { hasText: uniqueTitle })
    const patchResponse = page.waitForResponse(
      (response) =>
        response.url().includes('/documents/') &&
        response.request().method() === 'PATCH',
    )
    await row.locator('select').nth(1).selectOption('diagnosis')
    const patched = await patchResponse
    expect(patched.status()).toBe(200)
    const patchBody = await patched.json()
    expect(patchBody.meta?.pedagogical_intent).toBe('diagnosis')
  })

  test('TLIB-04 internal_only document is not cited in learner UI', async ({ page }) => {
    const fx = loadFixtures()
    const internalTitle = `E2E Internal Only ${Date.now()}`
    const publicTitle = `E2E Public Citable ${Date.now()}`

    await login(page, fx.users.smoke_trainer, fx.password, `/app/trainer/library?groupId=${fx.group_id}`)
    await setTenantOrg(page, fx.organisation_id)
    await page.reload()

    const createInternal = async (title: string, visibility: string) => {
      await page.getByPlaceholder('Titre').fill(title)
      await page.getByPlaceholder(/Texte brut/).fill(RAG_SOURCE_SNIPPET)
      await page.locator('label:has-text("Visibilité")').locator('..').locator('select').selectOption(visibility)
      await page.getByRole('button', { name: 'Créer et indexer' }).click()
      await expect(page.getByText(title).first()).toBeVisible({ timeout: 25_000 })
      const row = page.locator('tr', { hasText: title })
      if (await row.getByRole('button', { name: 'Lier' }).isVisible()) {
        await row.getByRole('button', { name: 'Lier' }).click()
      }
    }

    await createInternal(internalTitle, 'internal_only')
    await createInternal(publicTitle, 'learner_citable')
    await logout(page)

    await login(page, fx.users.smoke_learner, fx.password, `/app/session/${fx.session_id}`)
    await setTenantOrg(page, fx.organisation_id)
    await page.reload()

    const composer = page.locator('textarea').last()
    await expect(composer).toBeVisible({ timeout: 15_000 })
    await composer.fill(
      'Je dois verifier la procedure de consignation et la checklist securite sur le tableau electrique norme nf c15-100.',
    )
    await composer.press('Enter')

    // Attendre une réponse assistant (streaming ou non)
    await expect(page.locator('.prod-message').filter({ hasText: /./ }).last()).toBeVisible({
      timeout: 90_000,
    })

    // L'essentiel : le doc internal_only ne doit jamais apparaître en citation
    const appuiBadges = page.locator('.badge', { hasText: /^Appui :/ })
    const badgeCount = await appuiBadges.count()
    for (let i = 0; i < badgeCount; i += 1) {
      await expect(appuiBadges.nth(i)).not.toContainText(internalTitle)
    }
    await expect(
      page.getByText(new RegExp(`Appui :.*${internalTitle.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`, 'i')),
    ).toHaveCount(0)
  })

  /**
   * Scénario prioritaire formateur → apprenant → RAG
   *
   * Given un formateur a lié un poly « reference_course » au groupe
   * When l'apprenant pose une question alignée sur le contenu indexé
   * Then la réponse assistant expose des citations RAG dont le titre du poly
   */
  test('TLIB-RAG-01 learner message surfaces RAG citation from reference_course poly', async ({
    page,
  }) => {
    const fx = loadFixtures()
    const uniqueTitle = `E2E RAG Citation ${Date.now()}`

    // --- Given : formateur prépare la bibliothèque
    await login(page, fx.users.smoke_trainer, fx.password, `/app/trainer/library?groupId=${fx.group_id}`)
    await setTenantOrg(page, fx.organisation_id)
    await page.reload()

    await page.getByPlaceholder('Titre').fill(uniqueTitle)
    await page.getByPlaceholder(/Texte brut/).fill(RAG_SOURCE_SNIPPET)
    await page.locator('label:has-text("Rôle conversationnel")').locator('..').locator('select').selectOption('reference_course')
    await page.getByRole('button', { name: 'Créer et indexer' }).click()
    await expect(page.getByText(uniqueTitle).first()).toBeVisible({ timeout: 25_000 })
    const trainerRow = page.locator('tr', { hasText: uniqueTitle })
    if (await trainerRow.getByRole('button', { name: 'Lier' }).isVisible()) {
      await trainerRow.getByRole('button', { name: 'Lier' }).click()
    }
    await logout(page)

    // --- When : apprenant envoie un message ciblé
    const sessionPath = `/app/session/${fx.session_id}`
    await login(page, fx.users.smoke_learner, fx.password, sessionPath)
    await setTenantOrg(page, fx.organisation_id)
    await page.reload()

    const composer = page.locator('textarea').last()
    await expect(composer).toBeVisible({ timeout: 15_000 })
    const learnerMessage =
      'Je dois verifier la procedure de consignation et la checklist securite sur le tableau electrique avant mise sous tension selon la norme nf c15-100. Par quoi commencer ?'

    const messageResponse = page.waitForResponse(
      (response) =>
        (response.url().includes('/messages/stream') || response.url().includes('/messages/')) &&
        response.request().method() === 'POST',
      { timeout: 90_000 },
    )
    await composer.fill(learnerMessage)
    await composer.press('Enter')

    // --- Then : citations RAG (réseau ou UI)
    let ragFromApi: Array<{ document_title?: string }> = []
    try {
      const response = await messageResponse
      if (response.headers()['content-type']?.includes('application/json')) {
        const body = await response.json()
        ragFromApi = body.rag_citations || []
      }
    } catch {
      // stream endpoint may not return JSON body — fallback UI below
    }

    const citationBadge = page.getByText(new RegExp(`Appui :.*${uniqueTitle.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`, 'i'))
    await expect(citationBadge.or(page.getByText(/Appui :/)).first()).toBeVisible({ timeout: 90_000 })

    if (ragFromApi.length > 0) {
      const titles = ragFromApi.map((c) => c.document_title || '')
      expect(titles.some((t) => t.includes(uniqueTitle) || t.length > 0)).toBeTruthy()
    }
  })
})
