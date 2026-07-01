/** ADMIN — surfaces formateur distinctes des prompts tuteur. */
import { expect, test } from '@playwright/test'
import { apiFetchWithAuth, loadFixtures, login } from './helpers'

test.describe('SUPERADMIN_EDIT_TRAINER_PROMPT_SCOPED', () => {
  test('superadmin trainer knowledge API separate from tutor prompts', async ({ page }) => {
    const fx = loadFixtures()
    await login(page, fx.users.smoke_superadmin, fx.password, '/admin/conversation/trainer')

    const knowledge = await apiFetchWithAuth(page, '/hugo/trainer/knowledge-items/')
    expect(knowledge.status).toBe(200)
    const tutorPrompts = await apiFetchWithAuth(page, '/hugo/tutor-prompts/')
    expect(tutorPrompts.status).toBe(200)
    const promptCodes = (Array.isArray(tutorPrompts.body) ? tutorPrompts.body : [])
      .map((p: { code?: string }) => p.code)
    expect(promptCodes).not.toContain('trainer_explication')
  })
})
