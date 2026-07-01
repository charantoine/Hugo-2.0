/** ADMIN — liste profils conversation globaux. */
import { expect, test } from '@playwright/test'
import { apiFetchWithAuth, loadFixtures, login } from './helpers'

test.describe('ADMIN_PROFILES_LIST_FILTER', () => {
  test('orgadmin lists learner conversation profiles including workspace tutor', async ({ page }) => {
    const fx = loadFixtures()
    await login(page, fx.users.smoke_orgadmin, fx.password, '/admin/conversation/learner/profiles')

    const list = await apiFetchWithAuth(page, '/hugo/learner-conversation-profiles/')
    expect(list.status).toBe(200)
    const profiles = Array.isArray(list.body) ? list.body : (list.body as { results?: { name: string }[] })?.results || []
    const names = profiles.map((p) => p.name)
    expect(names.some((n) => n.startsWith('tutor_workspace_'))).toBe(true)
  })
})
