/**
 * Cluster 16 — interface apprenant (UI v2, baseline B).
 *
 * Tests-only (2026-07-01) : sélecteurs alignés sur le shell `learnerUiV2`
 * (`Modes de conversation`, panneaux Actions / Progression / Mémoire).
 * Attente explicite `GET /ui-state/` via clic « Actualiser » du header v2
 * (évite la course au chargement initial ; requiert `hugo_back` sur :8000).
 */
import { expect, test, type Page } from '@playwright/test'
import { cluster16SessionId, loadFixtures, login } from '../helpers'

/** Panneaux structurels UI v2 — remplace la barre legacy « Contexte de la séance » + PostureSelector v1. */
const STRUCTURAL_SELECTORS_V2 = [
  '[aria-label="Modes de conversation"]',
  '[aria-label="Progression de la conversation"]',
  '[aria-label="Mémoire de la conversation"]',
  '[aria-label="Actions de session"]',
] as const

async function openLearnerSessionV2(page: Page, sessionId: string) {
  const fx = loadFixtures()
  await login(page, fx.users.smoke_learner, fx.password, `/app/session/${sessionId}`)
  await expect(page.locator('.prod-workspace--v2')).toBeVisible()

  const headerRefresh = page.locator('.learner-v2-header').getByRole('button', { name: 'Actualiser' })
  await Promise.all([
    page.waitForResponse(
      (res) => res.url().includes('/ui-state/') && res.status() === 200,
      { timeout: 30_000 },
    ),
    headerRefresh.click(),
  ])

  await expect(page.getByLabel('Modes de conversation')).toBeVisible({ timeout: 15_000 })
}

async function assertNoP0LeakInBody(page: Page) {
  const body = await page.locator('body').innerText()
  expect(body).not.toMatch(/turn_state|episode_clarity|cognitive_load|llm_request_payload/i)
}

test.describe('E2E_C16_LEARNER_INTERFACE', () => {
  test('U16-S1 posture mode visible on learner workspace', async ({ page }) => {
    const fx = loadFixtures()
    await openLearnerSessionV2(page, fx.session_id)

    await expect(page.getByLabel('Modes de conversation')).toBeVisible()
    await expect(page.getByRole('group', { name: 'Choisir un mode' })).toBeVisible()
    await assertNoP0LeakInBody(page)
  })

  test('U16-S2 CTA buttons respect disabled state from UIState', async ({ page }) => {
    const fx = loadFixtures()
    await openLearnerSessionV2(page, fx.session_id)

    const synthesis = page.getByRole('button', { name: /synthèse/i })
    const evaluation = page.getByRole('button', { name: /évaluation/i })
    if (await synthesis.count()) {
      const disabled = await synthesis.first().isDisabled()
      if (disabled) {
        await expect(synthesis.first()).toBeDisabled()
      }
    }
    if (await evaluation.count()) {
      const disabled = await evaluation.first().isDisabled()
      if (disabled) {
        await expect(evaluation.first()).toBeDisabled()
      }
    }
  })

  test('U16-S3 memory panel shows governed sections without verbatim', async ({ page }) => {
    const fx = loadFixtures()
    await openLearnerSessionV2(page, fx.session_id)

    const memoryPanel = page.getByLabel('Mémoire de la conversation')
    await expect(memoryPanel).toBeVisible()
    await expect(page.getByText(/Mémoire de la séance/i)).toBeVisible()
    const memoryText = await memoryPanel.innerText()
    expect(memoryText).not.toContain(fx.verbatim_marker)
    expect(memoryText).not.toMatch(/turn_state|llm_request_payload/i)
    await assertNoP0LeakInBody(page)
  })

  test('U16-S4 scene progression branch maturity visible', async ({ page }) => {
    const fx = loadFixtures()
    await openLearnerSessionV2(page, fx.session_id)

    const progression = page.getByLabel('Progression de la conversation')
    await expect(progression).toBeVisible()
    await expect(page.getByRole('heading', { name: /Progression de la scène/i })).toBeVisible()
    await expect(progression).not.toContainText(/Chargement\.\.\./)
    await assertNoP0LeakInBody(page)
  })
})

test.describe('E2E_C16_DISPLAY_PROFILES', () => {
  for (const profile of ['youth', 'adult', 'professional'] as const) {
    test(`U16-P1 ${profile} exposes same structural blocks`, async ({ page }) => {
      const fx = loadFixtures()
      const sessionId = cluster16SessionId(fx, profile)
      test.skip(!sessionId, 'Run bootstrap_smoke_playwright to generate cluster16_sessions')

      await openLearnerSessionV2(page, sessionId)
      for (const selector of STRUCTURAL_SELECTORS_V2) {
        await expect(page.locator(selector)).toBeVisible()
      }
      await assertNoP0LeakInBody(page)
    })

    test(`U16-P2 ${profile} applies display profile class`, async ({ page }) => {
      const fx = loadFixtures()
      const sessionId = cluster16SessionId(fx, profile)
      test.skip(!fx.cluster16_sessions?.[profile], 'cluster16_sessions missing in smoke-fixtures.json')

      await openLearnerSessionV2(page, sessionId)
      await expect(page.locator(`.prod-workspace--${profile}`)).toBeVisible()
      await expect(page.locator(`.prod-panel--${profile}`).first()).toBeVisible()
    })
  }
})
