/**
 * Runtime QA — wizard org-scoped + sélection groupe.
 */
import { chromium } from 'playwright'
import fs from 'node:fs'
import path from 'node:path'

const OUT = path.resolve('../../docs-workspace/wizard-org-group-2026-06-26')
const BASE = 'http://localhost:5173'
const GROUP_ID = '29e5cdb9-de89-49b3-a36e-53b4b9bbbc50'
fs.mkdirSync(OUT, { recursive: true })

const results = { checks: [] }

async function check(name, fn) {
  try {
    results.checks.push({ name, ok: true, ...(await fn()) })
    console.log('OK', name)
  } catch (e) {
    results.checks.push({ name, ok: false, error: String(e) })
    console.error('FAIL', name, e.message)
  }
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

await check('dashboard-org-banner', async () => {
  await page.goto(`${BASE}/dashboard`)
  await page.waitForTimeout(1500)
  const text = await page.locator('main').textContent()
  if (!text?.includes('Organisation active :')) throw new Error('Bandeau org absent')
  if (!text?.includes('Demo Hugo Org')) throw new Error('Nom org absent')
  return {}
})

await check('wizard-group-select-visible', async () => {
  await page.goto(`${BASE}/admin/onboarding`)
  await page.waitForTimeout(3000)
  const sel = page.getByTestId('wizard-group-select')
  if (!(await sel.isVisible())) throw new Error('Sélecteur groupe absent')
  const options = await sel.locator('option').allTextContents()
  const mainText = await page.locator('main').textContent()
  if (options.length < 2) throw new Error(`Attendu plusieurs groupes, vu: ${options.length}`)
  if (mainText?.includes('Groupe de référence')) {
    throw new Error('Libellé "Groupe de référence" encore présent')
  }
  return { optionCount: options.length, options }
})

await check('wizard-scope-message', async () => {
  const text = await page.locator('.admin-onboarding-wizard').textContent()
  if (!text?.includes('Ce parcours concerne cette organisation')) throw new Error('Message scope absent')
  return {}
})

await check('wizard-query-groupId', async () => {
  await page.goto(`${BASE}/admin/onboarding?groupId=${GROUP_ID}`)
  await page.waitForTimeout(3000)
  const val = await page.getByTestId('wizard-group-select').inputValue()
  if (val !== GROUP_ID) throw new Error(`groupId query non appliqué: ${val}`)
  const text = await page.locator('.admin-onboarding-wizard').textContent()
  if (!text?.includes('bac pro melec')) throw new Error('Groupe bac pro melec non sélectionné')
  return { selectedId: val }
})

await check('wizard-change-group-recalculates', async () => {
  await page.goto(`${BASE}/admin/onboarding`)
  await page.waitForTimeout(3000)
  const sel = page.getByTestId('wizard-group-select')
  const options = await sel.locator('option').all()
  if (options.length < 2) return { skipped: true }
  const secondVal = await options[1].getAttribute('value')
  const secondLabel = await options[1].textContent()
  await sel.selectOption(secondVal)
  await page.waitForTimeout(2000)
  const summary = await page.locator('.onboarding-step').nth(1).textContent()
  if (!summary?.includes(secondLabel?.trim() || '')) {
    throw new Error('Étape groupe non recalculée après changement')
  }
  return { secondLabel: secondLabel?.trim() }
})

await page.screenshot({ path: path.join(OUT, 'wizard-group-select.png'), fullPage: true })

fs.writeFileSync(path.join(OUT, 'results.json'), JSON.stringify(results, null, 2))
await browser.close()
console.log('done', OUT)
