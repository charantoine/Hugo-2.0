/** ADMIN — édition prompt tuteur scoped org (baseline B). */
import { expect, test } from '@playwright/test'
import { apiFetchWithAuth, loadFixtures, login } from './helpers'

test.describe('SUPERADMIN_EDIT_TUTOR_PROMPT_SCOPED', () => {
  test('superadmin lists tutor prompts scoped to smoke org', async ({ page }) => {
    const fx = loadFixtures()
    await login(page, fx.users.smoke_superadmin, fx.password, '/tutor-prompts')

    const list = await apiFetchWithAuth(page, '/hugo/tutor-prompts/')
    expect(list.status).toBe(200)
    const prompts = Array.isArray(list.body) ? list.body : (list.body as { results?: unknown[] })?.results || []
    expect(prompts.length).toBeGreaterThan(0)
    const workspace = prompts.find((p: { code?: string }) => p.code === 'tutor_workspace_prep')
    expect(workspace).toBeTruthy()
  })
})
