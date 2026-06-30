/**
 * One-shot admin UI audit captures — local front + /api proxy.
 * Mode testeur : uniquement le chemin canonique bac pro melec (dashboard ou route directe).
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

const OUT = process.env.AUDIT_OUT_DIR
  ? path.resolve(process.env.AUDIT_OUT_DIR)
  : path.resolve('../../docs-workspace/audit-ui-runtime-2026-06/screenshots')
const BASE = process.env.AUDIT_BASE_URL || 'http://localhost:5173'
const GROUP_ID = REFERENCE_GROUP_ID
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

const browser = await chromium.launch({ headless: true })
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })

await page.goto(`${BASE}/login`)
await page.getByLabel('Identifiant').fill(LOGIN)
await page.getByLabel('Mot de passe', { exact: true }).fill(PASS)
await Promise.all([
  page.waitForURL((u) => !u.pathname.includes('/login'), { timeout: 20000 }),
  page.getByRole('button', { name: 'Se connecter' }).click(),
])
await page.waitForTimeout(5000)

const manifest = []
for (const item of PAGES) {
  await page.goto(`${BASE}${item.path}`, { waitUntil: 'networkidle', timeout: 30000 })
  await page.waitForTimeout(5000)
  const file = path.join(OUT, `${item.slug}.png`)
  await page.screenshot({ path: file, fullPage: !!item.fullPage })
  const heading = await page.locator('h1').first().textContent().catch(() => '')
  const tenant = await page.locator('#tenant-switcher').inputValue().catch(() => '')
  const tenantLabel = await page.locator('#tenant-switcher option:checked').textContent().catch(() => '')
  manifest.push({
    slug: item.slug,
    path: item.path,
    heading: (heading || '').trim(),
    tenantId: tenant,
    tenantLabel: (tenantLabel || '').trim(),
    url: page.url(),
  })
  console.log('captured', item.slug)
}

// Smoke : bouton testeur canonique unique sur le dashboard
await page.goto(`${BASE}/dashboard`)
await page.waitForTimeout(2000)
const canonicalButtons = page.getByTestId(DASHBOARD_TESTER_CANONICAL_TEST_ID)
const canonicalCount = await canonicalButtons.count()
if (canonicalCount !== 1) {
  console.warn('WARN: attendu 1 bouton testeur canonique, vu:', canonicalCount)
}
await canonicalButtons.click()
await page.waitForURL(new RegExp(`/group/${GROUP_ID}`), { timeout: 10000 })
console.log('OK dashboard-tester-canonical →', page.url())

fs.writeFileSync(
  path.join(OUT, 'manifest.json'),
  JSON.stringify(
    {
      baseline: {
        referenceGroupName: REFERENCE_GROUP_NAME,
        referenceGroupId: GROUP_ID,
        canonicalTesterPath: canonicalTesterPath(GROUP_ID),
      },
      pages: manifest,
    },
    null,
    2,
  ),
)
await browser.close()
console.log('done', OUT)
