/**
 * Full admin UI runtime audit — captures + functional smoke checks.
 */
import { chromium } from 'playwright'
import fs from 'node:fs'
import path from 'node:path'

import {
  REFERENCE_GROUP_ID,
  REFERENCE_GROUP_NAME,
  canonicalTesterPath,
  DASHBOARD_TESTER_CANONICAL_TEST_ID,
} from './auditConstants.mjs'

const OUT = path.resolve(
  process.env.AUDIT_OUT_DIR ||
    '../../docs-workspace/audit-ui-runtime-front-admin-2026-06-26/screenshots',
)
const BASE = process.env.AUDIT_BASE_URL || 'http://localhost:5173'
const GROUP_ID = REFERENCE_GROUP_ID
const GROUP_NAME = REFERENCE_GROUP_NAME
const USER_ID = process.env.AUDIT_USER_ID || '4c1b14e6-d990-44b1-ac85-67851ae099c7'
const LOGIN = process.env.AUDIT_LOGIN || 'demo.superadmin'
const PASS = process.env.AUDIT_PASS || 'demo-superadmin-2026'

const PAGES = [
  { slug: '01-dashboard', path: '/dashboard', fullPage: false },
  { slug: '02-users', path: '/users', fullPage: true },
  { slug: '03-user-detail', path: `/users/${USER_ID}`, fullPage: false },
  { slug: '04-groups-admin', path: '/groups-admin', fullPage: false },
  { slug: '05-group-detail-viewport', path: `/groups-admin/${GROUP_ID}`, fullPage: false },
  { slug: '05-group-detail-full', path: `/groups-admin/${GROUP_ID}`, fullPage: true },
  { slug: '06-admin-conversation', path: '/admin/conversation', fullPage: true },
  { slug: '07-learner-profiles', path: '/admin/conversation/learner/profiles', fullPage: true },
  { slug: '08-diagnostic', path: '/admin/conversation/learner/diagnostic', fullPage: true },
  { slug: '09-reflective_afest', path: '/admin/conversation/learner/reflective_afest', fullPage: true },
  { slug: '10-knowledge_review', path: '/admin/conversation/learner/knowledge_review', fullPage: true },
  { slug: '11-closing', path: '/admin/conversation/learner/closing', fullPage: true },
  { slug: '12-tutor-prompts', path: '/tutor-prompts', fullPage: true },
  { slug: '13-conduct-profiles', path: '/conduct-profiles', fullPage: true },
  { slug: '14-referentials', path: '/referentials', fullPage: false },
  { slug: '15-group-referential', path: `/group/${GROUP_ID}/referential`, fullPage: true },
]

fs.mkdirSync(OUT, { recursive: true })

const journal = { baseline: {}, manifest: [], functional: [], errors: [] }

const browser = await chromium.launch({ headless: true })
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })

async function login() {
  await page.goto(`${BASE}/login`)
  await page.evaluate(() => localStorage.clear())
  await page.getByLabel('Identifiant').fill(LOGIN)
  await page.getByLabel('Mot de passe', { exact: true }).fill(PASS)
  await Promise.all([
    page.waitForURL((u) => !u.pathname.includes('/login'), { timeout: 25000 }),
    page.getByRole('button', { name: 'Se connecter' }).click(),
  ])
}

await login()
await page.waitForTimeout(2000)

const tenantLabel = await page.locator('#tenant-switcher option:checked').textContent().catch(() => '')
journal.baseline = {
  base: BASE,
  login: LOGIN,
  tenantLabel: (tenantLabel || '').trim(),
  postLoginUrl: page.url(),
  capturedAt: new Date().toISOString(),
}

for (const item of PAGES) {
  try {
    await page.goto(`${BASE}${item.path}`, { waitUntil: 'networkidle', timeout: 30000 })
    await page.waitForTimeout(5000)
    const file = path.join(OUT, `${item.slug}.png`)
    await page.screenshot({ path: file, fullPage: !!item.fullPage })
    const heading = (await page.locator('h1').first().textContent().catch(() => ''))?.trim() || ''
    const orgBanner = await page.locator('.alert:has-text("Organisation")').first().isVisible().catch(() => false)
    const breadcrumb = (await page.locator('.breadcrumb').first().textContent().catch(() => ''))?.replace(/\s+/g, ' ').trim() || ''
    journal.manifest.push({
      slug: item.slug,
      path: item.path,
      heading,
      orgBannerVisible: orgBanner,
      breadcrumb,
      url: page.url(),
      screenshot: `${item.slug}.png`,
      fullPage: !!item.fullPage,
    })
    console.log('captured', item.slug)
  } catch (e) {
    journal.errors.push({ slug: item.slug, error: String(e) })
    console.error('fail', item.slug, e.message)
  }
}

// Functional checks
async function check(name, fn) {
  try {
    const result = await fn()
    journal.functional.push({ name, ok: true, ...result })
    console.log('OK', name)
  } catch (e) {
    journal.functional.push({ name, ok: false, error: String(e) })
    console.error('FAIL', name, e.message)
  }
}

await check('dashboard-admin-link-users', async () => {
  await page.goto(`${BASE}/dashboard`)
  await page.waitForTimeout(2000)
  const link = page.getByRole('link', { name: /Utilisateurs/i }).first()
  await link.click()
  await page.waitForURL(/\/users/, { timeout: 10000 })
  return { landed: page.url() }
})

await check('dashboard-tester-canonical', async () => {
  await page.goto(`${BASE}/dashboard`)
  await page.waitForTimeout(2000)
  const btn = page.getByTestId(DASHBOARD_TESTER_CANONICAL_TEST_ID)
  const count = await btn.count()
  if (count !== 1) throw new Error(`Attendu 1 bouton testeur canonique, vu: ${count}`)
  await btn.click()
  const expected = canonicalTesterPath(GROUP_ID)
  await page.waitForURL(new RegExp(`/group/${GROUP_ID}`), { timeout: 10000 })
  return { landed: page.url(), expected, canonicalButtonCount: count }
})

await check('group-detail-referential-link', async () => {
  await page.goto(`${BASE}/groups-admin/${GROUP_ID}`)
  await page.waitForTimeout(3000)
  const link = page.getByTestId('group-referential-link')
  await link.click()
  await page.waitForURL(/\/referential/, { timeout: 10000 })
  return { landed: page.url() }
})

await check('hub-compat-tutor-prompts', async () => {
  await page.goto(`${BASE}/admin/conversation`)
  await page.waitForTimeout(2000)
  const link = page.getByRole('link', { name: /Prompts apprenant/i })
  await link.click()
  await page.waitForURL(/\/tutor-prompts/, { timeout: 10000 })
  const inNavbar = await page.locator('.navbar').getByRole('link', { name: /tutor-prompts/i }).count()
  return { landed: page.url(), tutorPromptsInMainNav: inNavbar > 0 }
})

await check('groups-admin-create-form-visible', async () => {
  await page.goto(`${BASE}/groups-admin`)
  await page.waitForTimeout(2000)
  const orgVisible = await page.locator('text=Organisation actuelle').isVisible()
  const createBtn = await page.getByRole('button', { name: /Créer le groupe/i }).isVisible()
  return { orgVisible, createBtn }
})

await check('group-has-name-bac-pro-melec', async () => {
  await page.goto(`${BASE}/groups-admin/${GROUP_ID}`)
  await page.waitForTimeout(3000)
  const text = await page.locator('h1').first().textContent()
  if (!text?.includes(GROUP_NAME)) throw new Error(`Groupe attendu "${GROUP_NAME}", vu: ${text}`)
  const cohortVisible = await page.getByRole('heading', { name: 'Cohorte' }).isVisible()
  const expertCollapsed = await page.locator('#expertExports').isVisible().catch(() => false)
  return { groupHeading: text?.trim(), cohortVisible, exportsAccordionOpenByDefault: expertCollapsed }
})

await check('navbar-no-tutor-prompts-direct', async () => {
  await page.goto(`${BASE}/dashboard`)
  await page.waitForTimeout(1500)
  const count = await page.locator('.navbar-nav').getByRole('link', { name: /tutor-prompts|conduct-profiles/i }).count()
  return { expertRoutesInNavbar: count }
})

fs.writeFileSync(path.join(OUT, 'manifest.json'), JSON.stringify(journal.manifest, null, 2))
fs.writeFileSync(path.join(OUT, 'journal.json'), JSON.stringify(journal, null, 2))
await browser.close()
console.log('done', OUT)
