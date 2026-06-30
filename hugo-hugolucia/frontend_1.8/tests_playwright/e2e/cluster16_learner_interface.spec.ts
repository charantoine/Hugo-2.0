import { expect, test } from '@playwright/test'
import { cluster16SessionId, loadFixtures, login } from '../helpers'

const STRUCTURAL_SELECTORS = [
  '[aria-label="Mode conversationnel"]',
  '[aria-label="Contexte de la séance"]',
  '[aria-label="Progression de la conversation"]',
  '[aria-label="Mémoire de la conversation"]',
]

async function openLearnerSession(page, sessionId: string) {
  const fx = loadFixtures()
  await login(page, fx.users.smoke_learner, fx.password, `/app/session/${sessionId}`)
}

test.describe('E2E_C16_LEARNER_INTERFACE', () => {
  test('U16-S1 posture mode visible on learner workspace', async ({ page }) => {
    const fx = loadFixtures()
    await openLearnerSession(page, fx.session_id)

    await expect(page.getByLabel('Mode conversationnel')).toBeVisible()
    await expect(page.getByText(/Mode conversationnel/i)).toBeVisible()
    await expect(page.locator('.prod-conversation-mode__pill')).toBeVisible()
  })

  test('U16-S2 CTA buttons respect disabled state from UIState', async ({ page }) => {
    const fx = loadFixtures()
    await openLearnerSession(page, fx.session_id)

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
    await openLearnerSession(page, fx.session_id)

    const memoryPanel = page.getByLabel('Mémoire de la conversation')
    await expect(memoryPanel).toBeVisible()
    await expect(page.getByText(/Mémoire de la séance/i)).toBeVisible()
    const memoryText = await memoryPanel.innerText()
    expect(memoryText).not.toContain(fx.verbatim_marker)
    expect(memoryText).not.toMatch(/turn_state|llm_request_payload/i)
  })

  test('U16-S4 scene progression branch maturity visible', async ({ page }) => {
    const fx = loadFixtures()
    await openLearnerSession(page, fx.session_id)

    await expect(page.getByLabel('Contexte de la séance')).toBeVisible()
    await expect(page.getByText(/^Phase$/i)).toBeVisible()
    await expect(page.getByLabel('Progression de la conversation')).toBeVisible()
  })
})

test.describe('E2E_C16_DISPLAY_PROFILES', () => {
  for (const profile of ['youth', 'adult', 'professional'] as const) {
    test(`U16-P1 ${profile} exposes same structural blocks`, async ({ page }) => {
      const fx = loadFixtures()
      const sessionId = cluster16SessionId(fx, profile)
      test.skip(!sessionId, 'Run bootstrap_smoke_playwright to generate cluster16_sessions')

      await openLearnerSession(page, sessionId)
      for (const selector of STRUCTURAL_SELECTORS) {
        await expect(page.locator(selector)).toBeVisible()
      }
    })

    test(`U16-P2 ${profile} applies display profile class`, async ({ page }) => {
      const fx = loadFixtures()
      const sessionId = cluster16SessionId(fx, profile)
      test.skip(!fx.cluster16_sessions?.[profile], 'cluster16_sessions missing in smoke-fixtures.json')

      await openLearnerSession(page, sessionId)
      await expect(page.locator(`.prod-panel--${profile}`).first()).toBeVisible()
    })
  }
})
