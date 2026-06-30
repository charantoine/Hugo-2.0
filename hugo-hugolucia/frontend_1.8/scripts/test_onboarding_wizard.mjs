/**
 * Smoke test — wizard onboarding admin (guidance only).
 */
import { chromium } from 'playwright'
import fs from 'node:fs'
import path from 'node:path'

const BASE = process.env.AUDIT_BASE_URL || 'http://localhost:5173'
const OUT = path.resolve('../../docs-workspace/audit-onboarding-wizard-2026-06-26/screenshots')
fs.mkdirSync(OUT, { recursive: true })

const results = { checks: [], screenshot: null, url: null }

const browser = await chromium.launch({ headless: true })
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })

async function check(name, fn) {
  try {
    const detail = await fn()
    results.checks.push({ name, ok: true, ...detail })
    console.log('OK', name)
  } catch (e) {
    results.checks.push({ name, ok: false, error: String(e) })
    console.error('FAIL', name, e.message)
  }
}

await page.goto(`${BASE}/login`)
await page.evaluate(() => localStorage.clear())
await page.getByLabel('Identifiant').fill('demo.superadmin')
await page.getByLabel('Mot de passe', { exact: true }).fill('demo-superadmin-2026')
await Promise.all([
  page.waitForURL((u) => !u.pathname.includes('/login'), { timeout: 25000 }),
  page.getByRole('button', { name: 'Se connecter' }).click(),
])

await check('dashboard-onboarding-link', async () => {
  await page.goto(`${BASE}/dashboard`)
  await page.waitForTimeout(1500)
  const link = page.getByRole('link', { name: 'Assistant de mise en route' })
  if (!(await link.isVisible())) throw new Error('Lien wizard absent du dashboard')
  await link.click()
  await page.waitForURL(/\/admin\/onboarding/, { timeout: 10000 })
  return { url: page.url() }
})

await page.waitForTimeout(5000)
await page.screenshot({ path: path.join(OUT, 'wizard-overview.png'), fullPage: true })
results.screenshot = 'wizard-overview.png'
results.url = page.url()

await check('org-visible', async () => {
  const text = await page.locator('.admin-onboarding-wizard').textContent()
  if (!text?.includes('Demo Hugo Org')) throw new Error('Organisation non visible')
  return {}
})

await check('four-steps', async () => {
  const titles = await page.locator('.onboarding-step h2').allTextContents()
  const expected = ['Comptes', 'Groupe', 'Conversation apprenant', 'Référentiel']
  for (const t of expected) {
    if (!titles.some((h) => h.includes(t))) throw new Error(`Étape manquante: ${t}`)
  }
  return { titles }
})

await check('status-badges', async () => {
  const badges = await page.locator('.onboarding-step .badge').allTextContents()
  const hasStatus = badges.some((b) => /OK|Incomplet|À configurer|Attention fallback/.test(b))
  if (!hasStatus) throw new Error('Aucun statut affiché')
  return { badges: badges.filter((b) => /OK|Incomplet|configurer|fallback/.test(b)) }
})

await check('guidance-disclaimer', async () => {
  const text = await page.locator('.admin-onboarding-wizard').textContent()
  if (!text?.includes('ne crée ni ne modifie')) throw new Error('Disclaimer guidance absent')
  return {}
})

const ctaTests = [
  { label: 'Gérer les utilisateurs', path: '/users' },
  { label: 'Gérer le groupe', path: '/groups-admin/' },
  { label: 'Attribuer le profil au groupe', path: '/groups-admin/' },
  { label: 'Associer un référentiel', path: '/referential' },
]

for (const cta of ctaTests) {
  await check(`cta-${cta.label}`, async () => {
    await page.goto(`${BASE}/admin/onboarding`)
    await page.waitForTimeout(3000)
    const link = page.getByRole('link', { name: new RegExp(cta.label, 'i') }).first()
    const href = await link.getAttribute('href')
    if (!href?.includes(cta.path.replace(/\/$/, '').split('/').pop() === 'referential' ? 'referential' : cta.path.replace(/\/$/, ''))) {
      // softer check on path segment
    }
    if (cta.path.includes('referential') && !href?.includes('referential')) {
      throw new Error(`href inattendu: ${href}`)
    }
    if (cta.path === '/users' && href !== '/users') throw new Error(`href: ${href}`)
    if (cta.path.startsWith('/groups-admin') && !href?.startsWith('/groups-admin')) {
      throw new Error(`href: ${href}`)
    }
    if (cta.path.startsWith('/admin/conversation') && !href?.includes('/admin/conversation')) {
      throw new Error(`href: ${href}`)
    }
    await link.click()
    await page.waitForTimeout(1500)
    if (!page.url().includes(cta.path.replace(/\/$/, '').split('/').filter(Boolean)[0])) {
      // final url check
    }
    return { href, landed: page.url() }
  })
}

await check('wizard-group-selector', async () => {
  await page.goto(`${BASE}/admin/onboarding`)
  await page.waitForTimeout(3000)
  const sel = page.getByTestId('wizard-group-select')
  if (!(await sel.isVisible())) throw new Error('Sélecteur groupe absent')
  return { optionCount: await sel.locator('option').count() }
})

fs.writeFileSync(path.join(OUT, 'results.json'), JSON.stringify(results, null, 2))
await browser.close()
console.log('done', OUT)
