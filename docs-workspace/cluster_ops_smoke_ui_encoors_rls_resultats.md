# Cluster 8 — OPS / smoke UI / Encoors / RLS

> Vague OPS du plan de convergence — Playwright local, oracle Encoors, audit RLS Postgres  
> Date : 2026-06-18

---

## Sources mobilisées

| Source | Usage |
|--------|--------|
| `plan_documentation_cto_convergence_hugo.md` | Périmètre cluster 8 |
| `cluster2_matrice_runtime_vs_cible.md` | Photo runtime vs cible |
| `10_FICHE_RUNTIME_PROD_ENCOORS.md` | URL, auth JWT, CORS Encoors |
| `cluster_tests_e2e_et_encoors_vague5_resultats.md` | Baseline E2E API + probes non auth |
| `test_vague5_e2e_scenarios.py` | Scénarios EVAL1 / O1 rejouables |
| `hugo-hugolucia/frontend_1.8/tests_playwright/*` | Smoke UI navigateur |
| `hugo_back/scripts/encoors_oracle.py` | Oracle Encoors authentifié |
| `hugo_back/apps/hugo/tests/test_rls_postgres_minimal.py` | Audit RLS Postgres |
| Écarts 90/100/70/80/110/60 | Marquage niveau de preuve OPS |

---

## Synthèse exécutive

| Bloc | Méthode | Statut local | Encoors / prod |
|------|---------|--------------|----------------|
| Smoke UI TUTOR | Playwright `SMOKE_TUTOR` | **ALIGNE** (4/4 tests) | **A_VÉRIFIER** |
| Smoke UI TRAINER | Playwright `SMOKE_TRAINER` | **ALIGNE** | **A_VÉRIFIER** |
| Smoke UI ORGADMIN exports | Playwright `SMOKE_ORGADMIN_EXPORTS` | **ALIGNE** | **A_VÉRIFIER** |
| Oracle EVAL1 / O1 | `encoors_oracle.py` + JWT | **ALIGNE** (pytest E2E) | **A_VÉRIFIER** (pas de credentials) |
| RLS policies Postgres | pytest migrations | **ALIGNE** (4 tables) | **A_VÉRIFIER** (rôle app prod) |
| RLS cross-tenant SQL | `SET LOCAL app.organisation_id` | **SKIP** (superuser bypass) | **A_VÉRIFIER** |
| RLS cross-tenant API | GET session org B en user org A | **ALIGNE** (404) | **A_VÉRIFIER** |

**Bilan cluster 8 :** 4/4 Playwright smoke + 2/4 pytest RLS (2 skip documentés) + oracle Encoors probes non auth confirmées.

---

## 1. Résultats Playwright (local)

### Infrastructure

| Élément | Détail |
|---------|--------|
| Dossier | `hugo-hugolucia/frontend_1.8/tests_playwright/` |
| Config | `playwright.config.ts` — Chromium, `workers: 1`, `VITE_API_URL=/api` via webServer |
| Fixtures | `python manage.py bootstrap_smoke_playwright` → `smoke-fixtures.json` |
| Commande | `npm run test:smoke` (backend `:8000` + Vite `:5173` requis) |
| Piège connu | `.env.development` pointe vers Encoors — **obligatoire** `VITE_API_URL=/api` pour smoke local |

### Tests exécutés (2026-06-18)

| Test | Rôle | Surface | Preuve |
|------|------|---------|--------|
| `SMOKE_TUTOR` | TUTOR | `/app/tutor` → timeline | Timeline visible ; marker verbatim absent |
| `SMOKE_TRAINER` | TRAINER | `/app/trainer/knowledge` | Item smoke listé ; validation possible |
| `SMOKE_ORGADMIN_EXPORTS` | ORGADMIN | `/group/{id}` | CTA JSON + CSV visibles |
| `SMOKE_ORGADMIN_EXPORTS` | LEARNER | `/group/{id}` | CTA exports absents |

**Résultat : 4 passed (7.0s).**

### Ce que ces tests prouvent

- Surfaces prod convergées vagues 2–5 **se chargent sans erreur** en navigateur pour TUTOR / TRAINER / ORGADMIN.
- Guards exports visibles côté UI (`canRunExports` / absence pour LEARNER).
- Timeline tuteur **n’affiche pas** le marker verbatim quand `share_verbatim=false`.

### Ce qui reste PARTIEL

- Pas de clic export réel (téléchargement blob) — couvert par pytest O1.
- Ingest formateur dialogique non testé navigateur.
- Pas de parcours apprenant complet, CTA synthèse/évaluation, observabilité ORGADMIN.
- Encoors / prod : **A_VÉRIFIER** (CORS localhost interdit sur API distante).

---

## 2. Résultats Encoors

### Configuration

| Paramètre | Valeur |
|-----------|--------|
| Base URL | `https://hugoback.encoors.com` |
| Auth | JWT via `POST /auth/login/` |
| Credentials | **Non fournis** dans le workspace → `ENCOORS_USERNAME` / `ENCOORS_PASSWORD` requis |
| Exemple | `docs-workspace/encoors_config.example.json` |
| Script | `hugo_back/scripts/encoors_oracle.py` |

### Tableau Endpoint × Local × Encoors

| Endpoint / scénario | Local (vague 5) | Encoors (cluster 8) | Commentaire | Statut |
|---------------------|-----------------|---------------------|-------------|--------|
| `POST /auth/login/` | 200 smoke users | **Non testé** (no creds) | JWT requis pour EVAL1/O1 | **A_VÉRIFIER** |
| `GET /internal/.../observability/` | 403 ORGADMIN+ | **404** sans auth | Route absente ou urlconf divergent | **ABSENT** |
| `GET /internal/.../d9bis/export/` | 403 non-SUPERADMIN | **404** sans auth | Vague 4 non déployée | **ABSENT** |
| `GET /internal/.../conversation-summary/` | 403 non-SUPERADMIN | **404** sans auth | Vague 4 non déployée | **ABSENT** |
| `POST /exports/run/` | 200 ORGADMIN | **401** sans auth (v5) | Route présente | **PARTIEL** |
| EVAL1 chain (readiness → trace → export) | **ALIGNE** pytest | **A_VÉRIFIER** auth | Rejouer avec oracle + session_id | **A_VÉRIFIER** |
| O1 EvidenceBundle | **ALIGNE** pytest | **A_VÉRIFIER** auth | Idem | **A_VÉRIFIER** |

**Artefact :** `docs-workspace/encoors_oracle_cluster8.generated.json` (probes non authentifiées).

### Recommandations OPS

1. **Staging aligné local** : déployer routes v3/v4 (observabilité, D9bis) sur Encoors ou créer un environnement staging avec le noyau vagues 3–4.
2. **Compte démo Encoors** : fournir credentials ORGADMIN + session avec traces pour rejouer EVAL1/O1 via `encoors_oracle.py`.
3. **Front distant** : utiliser `https://hugo.encoors.com` (CORS autorisé) — pas `localhost:5173` contre API Encoors.

---

## 3. Résultats RLS Postgres

### Tables vérifiées (policies actives)

| Table | RLS enabled | Policy |
|-------|-------------|--------|
| `hugo_session` | oui | `hugo_session_tenant_isolation` |
| `trace` | oui | `trace_tenant_isolation` |
| `evidence` | oui | `evidence_tenant_isolation` |
| `export_run` | oui | `export_run_tenant_isolation` |

**Migration source :** `0002_enable_rls.py` (hugo) + `exports/0002_enable_rls.py`.

### Scénario cross-tenant minimal

| Niveau | Méthode | Résultat |
|--------|---------|----------|
| SQL direct | `SET LOCAL app.organisation_id = org_a` puis SELECT org B | **SKIP** — rôle `postgres` superuser bypass RLS |
| API applicative | User org A → `GET /hugo/sessions/{session_b}/` | **404** — isolation confirmée couche app |
| Middleware | `TenantRLSMiddleware` → `app.organisation_id` | **Présent** — efficacité SQL en prod **A_VÉRIFIER** avec rôle non-superuser |

### Ce qui reste A_VÉRIFIER

- Rôle DB applicatif prod (non superuser, sans BYPASSRLS).
- `FORCE ROW LEVEL SECURITY` sur tables sensibles si owner = superuser.
- Autres tables (referentials, library, quality, accounts.user).
- Perf et policies sur variantes clients / multi-org SUPERADMIN.

---

## 4. Synthèse OPS / exploitation par domaine

| Domaine | Preuve locale navigateur | Preuve Encoors | Preuve RLS | Statut OPS |
|---------|---------------------------|----------------|------------|------------|
| **90** Confidentialité / rôles | TUTOR sans verbatim marker | A_VÉRIFIER | API 404 cross-tenant | **ALIGNE local** |
| **100** Exports | ORGADMIN CTA ; LEARNER sans CTA | 401 route ; auth A_VÉRIFIER | `export_run` RLS on | **ALIGNE local UI** |
| **70** Traces / éval | Timeline traces visible | EVAL1 A_VÉRIFIER auth | `trace`/`evidence` RLS on | **ALIGNE local UI** |
| **80** Observabilité | Non couvert Playwright | 404 routes v3/v4 | — | **ABSENT Encoors** |
| **110** Surfaces encadrants | `/app/tutor`, `/app/trainer/knowledge` | A_VÉRIFIER | — | **ALIGNE local UI** |
| **60** Orchestrateur tuteur | Timeline + traces smoke | A_VÉRIFIER | — | **ALIGNE local UI** |

---

## 5. Artefacts livrés (cluster 8)

| Artefact | Chemin |
|----------|--------|
| Bootstrap smoke | `hugo_back/.../bootstrap_smoke_playwright.py` |
| Playwright config + 3 specs | `hugo-hugolucia/frontend_1.8/tests_playwright/` |
| Oracle Encoors | `hugo_back/scripts/encoors_oracle.py` |
| Config exemple Encoors | `docs-workspace/encoors_config.example.json` |
| Tests RLS | `hugo_back/apps/hugo/tests/test_rls_postgres_minimal.py` |
| Retex OPS | `cluster_retex_ops_cluster8.md` |

---

## 6. Prochaine sortie utile

1. Credentials Encoors + rerun `encoors_oracle.py` → compléter tableau EVAL1/O1 authentifié.
2. Rôle Postgres applicatif dédié + test SQL cross-tenant sans bypass.
3. CI : job `test:smoke` avec `VITE_API_URL=/api` + services Postgres/backend/Vite.
4. Couronne : intercalaires v1, dashboards analytics, parité Encoors post-deploy v3/v4.
