import { expect, test } from '@playwright/test'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { login } from '../helpers'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

type ProfileMigrationFixtures = {
  password: string
  learner: string
  profiles: { single: string; alpha: string; beta: string }
  groups: {
    one: { group_id: string; default_profile_id: string | null }
    multi: { group_id: string; default_profile_id: string | null }
    none: { group_id: string; default_profile_id: string | null }
  }
  legacy_session_id: string
}

function loadProfileFixtures(): ProfileMigrationFixtures {
  const testsRoot = path.join(__dirname, '..')
  const dedicated = path.join(testsRoot, 'profile-smoke-fixtures.json')
  const smoke = path.join(testsRoot, 'smoke-fixtures.json')
  if (fs.existsSync(dedicated)) {
    return JSON.parse(fs.readFileSync(dedicated, 'utf-8')) as ProfileMigrationFixtures
  }
  if (fs.existsSync(smoke)) {
    const base = JSON.parse(fs.readFileSync(smoke, 'utf-8')) as { profile_migration?: ProfileMigrationFixtures }
    if (base.profile_migration) return base.profile_migration
  }
  throw new Error('Run: cd hugo_back && DJANGO_SETTINGS_MODULE=config.settings.sqlite_test python manage.py bootstrap_smoke_playwright && python manage.py bootstrap_profile_migration_smoke')
}

test.describe('Profile migration smoke (F1/F2)', () => {
  const fx = loadProfileFixtures()

  test.beforeEach(async ({ page }) => {
    await login(page, fx.learner, fx.password, '/app')
  })

  test('network: home does not call tutor-prompts', async ({ page }) => {
    const tutorPromptCalls: string[] = []
    page.on('request', (request) => {
      if (request.url().includes('/hugo/tutor-prompts')) {
        tutorPromptCalls.push(request.url())
      }
    })
    await page.reload()
    await expect(page.getByTestId('conversation-profile-selector')).toBeVisible()
    expect(tutorPromptCalls).toEqual([])
  })

  test('case 1: single active profile on group — auto selection', async ({ page }) => {
    await page.getByLabel('Groupe').selectOption(fx.groups.one.group_id)
    await expect(page.getByTestId('conversation-profile-single')).toContainText('Smoke Profil Unique')
    await expect(page.getByTestId('conversation-profile-select')).toHaveCount(0)

    const sessionPromise = page.waitForResponse((response) => (
      response.url().includes('/hugo/sessions/') && response.request().method() === 'POST'
    ))
    await page.getByTestId('create-session-btn').click()
    const sessionResponse = await sessionPromise
    const payload = sessionResponse.request().postDataJSON() as Record<string, string>
    expect(payload.learner_conversation_profile_id).toBe(fx.profiles.single)
    expect(payload.tutor_prompt_id).toBeUndefined()

    await page.waitForURL(/\/app\/session\//)
    await expect(page.getByTestId('session-global-profile-badge')).toContainText('Smoke Profil Unique')
    await expect(page.getByTestId('session-posture-badge')).toBeVisible()
  })

  test('case 2: multiple profiles — learner chooses', async ({ page }) => {
    await page.getByLabel('Groupe').selectOption(fx.groups.multi.group_id)
    await expect(page.getByTestId('conversation-profile-select')).toBeVisible()
    await page.getByTestId('conversation-profile-select').selectOption(fx.profiles.beta)

    const sessionPromise = page.waitForResponse((response) => (
      response.url().includes('/hugo/sessions/') && response.request().method() === 'POST'
    ))
    await page.getByTestId('create-session-btn').click()
    const sessionResponse = await sessionPromise
    const payload = sessionResponse.request().postDataJSON() as Record<string, string>
    expect(payload.learner_conversation_profile_id).toBe(fx.profiles.beta)
  })

  test('case 3: no active profile — create blocked', async ({ page }) => {
    await page.route('**/hugo/learner-conversation-profiles/**', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
    })
    await page.reload()
    await expect(page.locator('.alert-warning')).toContainText('Aucun profil conversationnel actif')
    await expect(page.getByTestId('create-session-btn')).toBeDisabled()
  })

  test('case 4: legacy session remains readable', async ({ page }) => {
    await page.goto(`/app/session/${fx.legacy_session_id}`)
    await expect(page.getByTestId('session-legacy-profile-badge')).toBeVisible()
    await expect(page.getByTestId('session-posture-badge')).toBeVisible()
    await expect(page.getByTestId('session-global-profile-badge')).toHaveCount(0)
  })
})
