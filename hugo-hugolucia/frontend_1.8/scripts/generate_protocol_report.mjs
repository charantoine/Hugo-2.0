/**
 * Génère RAPPORT_E2E_PROTOCOL.md depuis les résultats Playwright JSON.
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const OUT_DIR = path.resolve(__dirname, '../../../docs-workspace/e2e-protocol-runtime')
const FALLBACK_JSON = path.resolve(__dirname, '../tests_playwright/playwright-results.json')
const RESULT_JSON =
  process.argv[2] ||
  (fs.existsSync(path.join(OUT_DIR, 'playwright-results.json'))
    ? path.join(OUT_DIR, 'playwright-results.json')
    : FALLBACK_JSON)
const PRECOND = path.join(OUT_DIR, 'protocol-preconditions.json')

function lotFromTitle(title) {
  const m = title.match(/^L(\d+)/)
  return m ? `LOT ${m[1]}` : 'AUTRE'
}

function classify(status, title, error) {
  if (status === 'skipped') return 'SKIP (données / scaffold)'
  if (status === 'passed') return 'PASS'
  if (error?.includes('timeout')) return 'FAIL (fragilité runtime)'
  return 'FAIL'
}

if (!fs.existsSync(RESULT_JSON)) {
  console.error('Missing', RESULT_JSON)
  process.exit(1)
}

const data = JSON.parse(fs.readFileSync(RESULT_JSON, 'utf-8'))
const pre = fs.existsSync(PRECOND) ? JSON.parse(fs.readFileSync(PRECOND, 'utf-8')) : null

const rows = []

for (const suite of data.suites || []) {
  for (const sub of suite.suites || []) {
    for (const spec of sub.specs || []) {
      const title = spec.title
      const testObj = spec.tests?.[0]
      const result = testObj?.results?.[0]
      const status = result?.status || testObj?.status || 'unknown'
      const error = result?.error?.message
      rows.push({
        lot: lotFromTitle(title),
        test: title,
        status,
        class: classify(status, title, error),
        error: error?.slice(0, 200),
      })
    }
  }
}

const pass = rows.filter((r) => r.class === 'PASS').length
const fail = rows.filter((r) => r.class.startsWith('FAIL')).length
const skip = rows.filter((r) => r.class.startsWith('SKIP')).length

const md = `# Rapport d'exécution — protocole E2E Playwright Hugo

**Date :** ${new Date().toISOString().slice(0, 10)}  
**Front :** ${pre?.frontUrl || 'http://localhost:5173'}  
**API :** ${pre?.apiOrigin || 'http://127.0.0.1:8000'}  
**Résultats bruts :** [\`playwright-results.json\`](playwright-results.json)  
**Préconditions :** [\`protocol-preconditions.json\`](protocol-preconditions.json)

---

## Synthèse

| PASS | FAIL | SKIP |
|------|------|------|
| ${pass} | ${fail} | ${skip} |

---

## Préconditions (${pre?.missingCritical?.length ? '⚠ manques' : 'OK'})

${pre ? `
- Organisations : ${pre.organisationCount} (2+ requis pour switch : ${pre.hasTwoOrgs ? 'oui' : 'non'})
- Groupes org démo : ${pre.groupCountDemoOrg}
- bac pro melec : ${pre.hasBacProMelec ? 'oui' : 'non'}
- Rôles démo : ${JSON.stringify(pre.rolesDemoOrg)}
- Smoke fixtures : ${pre.smokeFixtures?.ok ? 'oui' : 'non'}
${pre.missingCritical?.length ? `- **Manques :** ${pre.missingCritical.join('; ')}` : ''}
` : '_Fichier préconditions absent_'}

---

## Résultats par lot

| Lot | Test | Statut | Classification |
|-----|------|--------|----------------|
${rows.map((r) => `| ${r.lot} | ${r.test} | ${r.status} | ${r.class} |`).join('\n')}

---

## Écarts classés

| Type | Détail |
|------|--------|
| Bug confirmé | ${rows.filter((r) => r.class === 'FAIL' && !r.error?.includes('skip')).map((r) => r.test).join(', ') || '—'} |
| Scaffold / données manquantes | Lots 5–7, 9, 11 (skip volontaire) + tests skip fixtures |
| Fonctionnalité non couverte auto | Synthèse/évaluation bout-en-bout sans session préparée |

---

## Arborescence suite

\`\`\`
tests_playwright/
  helpers.ts, helpers/demo-env.ts, helpers/protocol.ts
  e2e/protocol/
    lot00-preconditions-smoke.spec.ts
    lot01-org-active.spec.ts
    lot02-wizard.spec.ts
    lot03-dashboard-demo.spec.ts
    lot04-groups-users.spec.ts
    lot05-07-09-11-scaffold.spec.ts
    lot08-12-learner-tutor.spec.ts
\`\`\`

Commande : \`npm run test:protocol\`
`

fs.mkdirSync(OUT_DIR, { recursive: true })
fs.writeFileSync(path.join(OUT_DIR, 'RAPPORT_E2E_PROTOCOL.md'), md)
console.log('Wrote', path.join(OUT_DIR, 'RAPPORT_E2E_PROTOCOL.md'))
