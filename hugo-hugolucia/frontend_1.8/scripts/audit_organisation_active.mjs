/**
 * Audit organisation active — captures + API smoke.
 */
import { chromium } from 'playwright'
import fs from 'node:fs'
import path from 'node:path'

const OUT = path.resolve('../../docs-workspace/audit-organisation-active-2026-06-26/screenshots')
const BASE = process.env.AUDIT_BASE_URL || 'http://localhost:5173'
const API = process.env.AUDIT_API_URL || 'http://127.0.0.1:8000'
const LOGIN = 'demo.superadmin'
const PASS = 'demo-superadmin-2026'
const DEMO_ORG_ID = 'dc1e8465-0ff2-4d66-bfbb-a0f8e7a23b3d'
const GROUP_ID = '29e5cdb9-de89-49b3-a36e-53b4b9bbbc50'

const PAGES = [
  { slug: '01-dashboard', path: '/dashboard' },
  { slug: '02-users', path: '/users' },
  { slug: '03-groups-admin', path: '/groups-admin' },
  { slug: '04-group-detail', path: `/groups-admin/${GROUP_ID}` },
  { slug: '05-onboarding', path: '/admin/onboarding' },
]

fs.mkdirSync(OUT, { recursive: true })
const journal = { pages: [], api: [], orgSwitcher: null }

async function apiLogin() {
  const res = await fetch(`${API}/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: LOGIN, password: PASS }),
  })
  const data = await res.json()
  return data.access
}

async function apiGet(token, path, orgId) {
  const res = await fetch(`${API}${path}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      'X-Organisation-Id': orgId,
    },
  })
  const body = await res.json().catch(() => null)
  return { status: res.status, body }
}

const token = await apiLogin()

for (const [label, path] of [
  ['groups-demo-org', '/groups/'],
  ['users-demo-org', '/users/'],
  ['members-demo-org', `/groups/${GROUP_ID}/members/`],
  ['referential-demo-org', `/groups/${GROUP_ID}/referential-config/`],
]) {
  const r = await apiGet(token, path, DEMO_ORG_ID)
  const list = Array.isArray(r.body) ? r.body : r.body?.results
  journal.api.push({
    label,
    path,
    orgHeader: DEMO_ORG_ID,
    status: r.status,
    count: Array.isArray(list) ? list.length : null,
    sampleNames: Array.isArray(list)
      ? list.slice(0, 5).map((x) => x.name || x.username || x.id)
      : null,
  })
}

const browser = await chromium.launch({ headless: true })
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })

await page.goto(`${BASE}/login`)
await page.evaluate(() => localStorage.clear())
await page.getByLabel('Identifiant').fill(LOGIN)
await page.getByLabel('Mot de passe', { exact: true }).fill(PASS)
await Promise.all([
  page.waitForURL((u) => !u.pathname.includes('/login'), { timeout: 25000 }),
  page.getByRole('button', { name: 'Se connecter' }).click(),
])
await page.waitForTimeout(2000)

journal.orgSwitcher = {
  visible: await page.locator('#tenant-switcher').isVisible().catch(() => false),
  selectedLabel: (await page.locator('#tenant-switcher option:checked').textContent().catch(() => ''))?.trim(),
  selectedId: await page.locator('#tenant-switcher').inputValue().catch(() => ''),
  navbarUserLine: (await page.locator('.navbar .dropdown-toggle').first().textContent())?.replace(/\s+/g, ' ').trim(),
}

for (const item of PAGES) {
  await page.goto(`${BASE}${item.path}`, { waitUntil: 'networkidle', timeout: 30000 })
  await page.waitForTimeout(3000)
  await page.screenshot({ path: path.join(OUT, `${item.slug}.png`), fullPage: item.path.includes('onboarding') })
  const bodyText = await page.locator('main').textContent().catch(() => '')
  const hasOrgInBody = /Organisation|Demo Hugo Org/i.test(bodyText || '')
  const orgBanner = await page.locator('.alert:has-text("Organisation")').first().textContent().catch(() => '')
  journal.pages.push({
    slug: item.slug,
    path: item.path,
    hasOrgMentionInMain: hasOrgInBody,
    orgBannerSnippet: (orgBanner || '').replace(/\s+/g, ' ').trim().slice(0, 120),
    switcherVisible: await page.locator('#tenant-switcher').isVisible().catch(() => false),
  })
}

fs.writeFileSync(path.join(OUT, 'journal.json'), JSON.stringify(journal, null, 2))
await browser.close()
console.log('done', OUT)
