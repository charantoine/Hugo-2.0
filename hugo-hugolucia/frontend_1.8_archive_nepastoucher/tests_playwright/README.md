# Playwright smoke tests (cluster 8)

Smoke navigateur pour surfaces prod convergées : TUTOR, TRAINER, ORGADMIN exports.

## Prérequis

1. Postgres + migrations : `cd hugo_back && python manage.py migrate`
2. Fixtures : `python manage.py bootstrap_smoke_playwright`
3. Backend : `python manage.py runserver 8000`
4. Front avec API locale : `VITE_API_URL=/api npm run dev`  
   (`.env.development` pointe vers Encoors — ne pas l’utiliser tel quel pour les smokes.)

## Exécution

```bash
npm run test:smoke
```

La config Playwright force `VITE_API_URL=/api` si elle démarre Vite via `webServer`.

## Protocole E2E 12 lots (`e2e/protocol/`)

Vérification 3 couches : visible / réseau / métier (backend-first).

```bash
# Prérequis identiques aux smokes + bootstrap smoke
python manage.py bootstrap_smoke_playwright   # génère smoke-fixtures.json

npm run test:protocol          # exécution
npm run test:protocol:report   # exécution + RAPPORT_E2E_PROTOCOL.md
```

Rapport : `docs-workspace/e2e-protocol-runtime/RAPPORT_E2E_PROTOCOL.md`

| Lot | Fichier | Couverture |
|-----|---------|------------|
| 0 | `lot00-preconditions-smoke.spec.ts` | préconditions API, smoke login |
| 1 | `lot01-org-active.spec.ts` | org active, switch SUPERADMIN |
| 2 | `lot02-wizard.spec.ts` | wizard généralisé org + groupe |
| 3 | `lot03-dashboard-demo.spec.ts` | raccourci démo séparé |
| 4 | `lot04-groups-users.spec.ts` | groupes/users wire + création |
| 5–7,9,11 | `lot05-07-09-11-scaffold.spec.ts` | scaffold (skip — données/session) |
| 8,10,12 | `lot08-12-learner-tutor.spec.ts` | apprenant, tuteur, P0 |

Helpers : `helpers/demo-env.ts`, `helpers/protocol.ts` (`trackApi`, `expectOrgBanner`).

Variables optionnelles : `SMOKE_BASE_URL`, `SMOKE_API_ORIGIN`, `DEMO_SUPERADMIN_*`, `DEMO_ORG_ID`.

- `test_smoke_tutor.spec.ts` — timeline sans verbatim
- `test_smoke_trainer.spec.ts` — knowledge list + validate
- `e2e/admin_trainer_creation.spec.ts` — création TRAINER depuis `/users` + rattachement groupe + login formateur
- `test_smoke_orgadmin_exports.spec.ts` — CTA exports ORGADMIN vs LEARNER
