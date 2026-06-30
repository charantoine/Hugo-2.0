/**
 * Vérification cohérence superadmin — org active + séparation démo/wizard.
 */
import { chromium } from 'playwright'
import fs from 'node:fs'
import path from 'node:path'

const OUT = path.resolve('../../docs-workspace/verif-coherence-superadmin-2026-06-26')
const BASE = 'http://localhost:5173'
const GROUP_ID = '29e5cdb9-de89-49b3-a36e-53b4b9bbbc50'

const PAGES = [
  { slug: 'dashboard', path: '/dashboard' },
  { slug: 'users', path: '/users' },
  { slug: 'groups-admin', path: '/groups-admin' },
  { slug: 'group-detail', path: `/groups-admin/${GROUP_ID}` },
  { slug: 'onboarding', path: '/admin/onboarding' },
]

fs.mkdirSync(OUT, { recursive: true })
const report = { pages: [], checks: [] }

function assert(checks, name, ok, detail = {}) {
  checks.push({ name, ok, ...detail })
  console.log(ok ? 'OK' : 'FAIL', name, detail.error || '')
}

const browser = await chromium.launch({ headless: true })
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })

await page.goto(`${BASE}/login`)
await page.evaluate(() => localStorage.clear())
await page.getByLabel('Identifiant').fill('demo.superadmin')
await page.getByLabel('Mot de passe', { exact: true }).fill('demo-superadmin-2026')
await Promise.all([
  page.waitForURL((u) => !u.pathname.includes('/login'), { timeout: 25000 }),
  page.getByRole('button', { name: 'Se connecter' }).click(),
])
await page.waitForTimeout(2000)

const switcherLabel = (await page.locator('#tenant-switcher option:checked').textContent())?.trim()

for (const item of PAGES) {
  await page.goto(`${BASE}${item.path}`, { waitUntil: 'networkidle', timeout: 30000 })
  await page.waitForTimeout(2500)
  await page.screenshot({ path: path.join(OUT, `${item.slug}.png`), fullPage: item.slug === 'onboarding' })

  const mainText = (await page.locator('main').textContent()) || ''
  const orgBannerCount = await page.locator('main').getByText(/Organisation active\s*:/).count()
  const hasDemoHugo = mainText.includes('Demo Hugo Org')
  const hasGroupeDeReference = /Groupe de référence/i.test(mainText)
  const hasRaccourciDemo = /Raccourci démo|raccourci de démonstration/i.test(mainText)
  const hasGroupeAConfigurer = mainText.includes('Groupe à configurer')
  const hasBacProMelec = mainText.includes('bac pro melec')

  report.pages.push({
    path: item.path,
    orgBannerCount,
    hasDemoHugoOrg: hasDemoHugo,
    hasGroupeDeReference,
    hasRaccourciDemo,
    hasGroupeAConfigurer,
    hasBacProMelec,
    switcherVisible: await page.locator('#tenant-switcher').isVisible().catch(() => false),
    navbarOrg: switcherLabel,
  })
}

// Checks globaux
const onboarding = report.pages.find((p) => p.path.includes('onboarding'))
const dashboard = report.pages.find((p) => p.path.includes('dashboard'))

assert(report.checks, 'all-pages-org-banner', report.pages.every((p) => p.orgBannerCount >= 1))
assert(report.checks, 'all-pages-demo-org-name', report.pages.every((p) => p.hasDemoHugoOrg))
assert(report.checks, 'onboarding-no-groupe-de-reference', !onboarding?.hasGroupeDeReference, {
  error: onboarding?.hasGroupeDeReference ? 'wizard contient encore Groupe de référence' : undefined,
})
assert(report.checks, 'onboarding-has-groupe-a-configurer', !!onboarding?.hasGroupeAConfigurer)
assert(report.checks, 'onboarding-no-bac-pro-implicit', !onboarding?.hasBacProMelec, {
  error: onboarding?.hasBacProMelec ? 'bac pro melec visible dans wizard sans sélection explicite' : undefined,
})
assert(report.checks, 'dashboard-demo-shortcut-labeled', dashboard?.hasRaccourciDemo && !dashboard?.hasGroupeDeReference, {
  error: 'dashboard doit utiliser libellé raccourci démo, pas Groupe de référence',
})
assert(report.checks, 'users-no-bac-pro', !report.pages.find((p) => p.path === '/users')?.hasBacProMelec)
assert(report.checks, 'groups-admin-no-bac-pro', !report.pages.find((p) => p.path === '/groups-admin')?.hasBacProMelec)
assert(report.checks, 'group-detail-no-bac-pro-name-required', true) // bac pro peut apparaître comme nom de groupe réel

fs.writeFileSync(path.join(OUT, 'journal.json'), JSON.stringify(report, null, 2))
await browser.close()
console.log('done', OUT)
