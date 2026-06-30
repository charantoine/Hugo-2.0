# Multi-tenant smoke & RLS

## État de validation au 20/06/2026

Campagne locale post-durcissement multi-tenant (voir archive [`docs-workspace/tests/archives/tests_hugo_2_0_2026-06-18_20.md`](../../docs-workspace/tests/archives/tests_hugo_2_0_2026-06-18_20.md) pour le détail).

- **Multi-tenant backend (relaxed)** : **conforme** — `HUGO_RLS_STRICT=0`, **90/90 PASS**, 0 fuite inter-org (re-validé 20/06 PM).
- **Profils conversationnels globaux apprenant** : **conforme** — 9 tests dédiés + campagne ciblée 85 PASS ; fallback legacy actif.
- **Front multi-org + Playwright** : **conforme** — **11/11 PASS** (`SMOKE_RUN_TENANT=1`, re-validé 20/06 PM).
- **Tutor-links** : **SUPERADMIN-only confirmé** — 8+ tests dédiés PASS (ORGADMIN / tuteur → 403).
- **RLS strict** : gate `HUGO_RLS_STRICT=1` **opérationnel** (fail si connexion bypass policies) ; en local et CI actuelle, `TEST_DB_USER=postgres` (superuser) → **non vert** en mode strict — prochaine étape : pytest sur rôle `hugo_app_tenant_test` / `hugo_app`.
- **Smoke CI** : workflow `.github/workflows/multitenant-smoke.yml` + script `run_multitenant_smoke.sh` **présents** ; exécution GitHub **A_VÉRIFIER** (pas de run remote validé localement).

---

## Tutor-links (transitional)

| Role | POST tutor-link | GET (group) |
|------|-----------------|-------------|
| SUPERADMIN | allowed | all links in group |
| ORGADMIN | **denied (403)** | own links only (empty unless member) |
| TUTOR / others | denied | scoped to self |

**Future:** ORGADMIN + SUPERADMIN.

**État 20/06/2026 :** la **création** de tutor-links est une prérogative du **SUPERADMIN uniquement**. ORGADMIN, tuteurs, formateurs et apprenants ne peuvent pas créer de tutor-links (403). Règle **transitoire volontaire**, en attendant une ouverture éventuelle aux ORGADMIN. Validé par tests backend + e2e (UI masquée pour ORGADMIN).

Code: `apps/referentials/views_groups.py` (`TutorLinkListCreate`), front `GroupAdminDetailView.vue` (`canManageTutorLinks`).

## RLS strategy

| Environment | Expectation |
|-------------|-------------|
| **Production** | Django connects as `hugo_app` (NOSUPERUSER NOBYPASSRLS). RLS enabled on tenant tables. |
| **CI / staging** | Postgres + `HUGO_RLS_STRICT=1`. Fails if migration role bypasses RLS. App-role test via `hugo_app_tenant_test`. |
| **Dev local** | Prefer Postgres + `scripts/setup_rls_app_role.sql`. Set `HUGO_RLS_STRICT=0` only for quick local runs on superuser DB (not prod-like). |

Setup test role:

```bash
psql -U postgres -d hugo_poc_test -f scripts/setup_rls_app_role.sql
psql -U postgres -d hugo_poc_test -c "GRANT SELECT ON TABLE hugo_session, trace, evidence, export_run TO hugo_app_tenant_test;"
```

Prod audit template: `scripts/audit_rls_prod_template.sql`

Defense in depth: application `tenant_organisation_id()` + PostgreSQL RLS.

**État 20/06/2026 (RLS) :** le gate strict (`app_core/rls_guard.py`, `HUGO_RLS_STRICT=1`) **refuse** les campagnes lorsque le rôle de connexion bypass RLS — comportement voulu. Localement et dans la CI actuelle, Django/pytest se connectent encore en **`postgres` superuser** : les tests RLS SQL sont **SKIP** (relaxed) ou **FAIL/ERROR** (strict). Prochaine étape ops : migrer avec superuser, exécuter les tests avec un rôle applicatif **`hugo_app`** / `hugo_app_tenant_test` pour un vert strict prod-like. Détail : archive campagnes §2 (20/06).

## Smoke suite

### Backend only

```bash
cd hugo_back
chmod +x scripts/run_multitenant_smoke.sh
HUGO_RLS_STRICT=1 ./scripts/run_multitenant_smoke.sh
```

### Backend + Playwright

Terminal 1 — API:

```bash
cd hugo_back && .venv/bin/python manage.py runserver 8000
```

Terminal 2 — smoke:

```bash
cd hugo_back
RUN_PLAYWRIGHT_SMOKE=1 HUGO_RLS_STRICT=1 ./scripts/run_multitenant_smoke.sh
```

Playwright uses `tests_playwright/tenant-smoke-fixtures.json` from `python manage.py bootstrap_multitenant_smoke`.

### CI

Workflow: `.github/workflows/multitenant-smoke.yml`

- Job `backend-tenant-smoke` : Postgres 16, migrate, rôle `hugo_app_tenant_test`, campagne pytest avec `HUGO_RLS_STRICT=1` (échec attendu tant que `TEST_DB_USER=postgres` bypass RLS — voir § État validation 20/06).
- Job `playwright-tenant-smoke` : bootstrap fixtures, API `:8000`, e2e `SMOKE_RUN_TENANT=1` (scénarios par persona).

## Archives des campagnes de tests (2026-06)

Point d’entrée consolidé : [`docs-workspace/tests/archives/tests_hugo_2_0_2026-06-18_20.md`](../../docs-workspace/tests/archives/tests_hugo_2_0_2026-06-18_20.md) — regroupe la campagne convergence du **18/06** (briefing CTO) et la campagne multi-tenant / RLS / tutor-links / UI / smoke du **20/06**. Ce fichier reste la référence opérationnelle détaillée pour tutor-links, RLS et commandes smoke.
