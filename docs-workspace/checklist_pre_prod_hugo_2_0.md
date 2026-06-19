# Checklist prêt mise en ligne — Hugo 2.0 (runtime local + oracles distants)

> **Usage CTO :** rejouer la séquence avant déploiement contrôlé.  
> **Légende statut :** **OK** = vert local confirmé ; **A_VÉRIFIER** = prod/Encoors non exécuté ou partiel ; **N/A** = hors périmètre lot courant.

**Date de référence :** 2026-06-18  
**Sources :** `plan_tests_global_hugo.md`, garde-fou convergence, clusters 10–14.

---

## Prérequis environnement local

```bash
# Backend
cd hugo_back
source .venv/bin/activate   # si présent
export DJANGO_SETTINGS_MODULE=config.settings.test

# Front Playwright — IMPORTANT : proxy local, pas Encoors
# playwright.config.ts force VITE_API_URL=/api
```

---

## Commande unique — backend preprod

```bash
cd hugo_back
bash scripts/run_preprod_suite.sh
```

**Critère PASS :** exit code 0, ~113 tests passed, 2 skipped (RLS Postgres si SQLite).

**Critère FAIL :** tout échec pytest garde-fou, cluster3, memory-summary, evaluation pivot, RLS (si Postgres), exports guards.

---

## Playwright — surfaces produit

```bash
# 1. Fixtures déterministes
cd hugo_back
python manage.py bootstrap_smoke_playwright

# 2. Smokes + e2e persona
cd ../hugo-hugolucia/frontend_1.8
VITE_API_URL=/api npm run test:smoke
```

**Specs exécutées :**

- `tests_playwright/test_smoke_tutor.spec.ts`
- `tests_playwright/test_smoke_trainer.spec.ts`
- `tests_playwright/test_smoke_orgadmin_exports.spec.ts`
- `tests_playwright/e2e/learner_a1.spec.ts`
- `tests_playwright/e2e/tutor_b1.spec.ts`
- `tests_playwright/e2e/coordo_c14.spec.ts`

**Critère PASS :** tous les tests verts ; aucun `turn_state` / verbatim marker dans DOM tuteur.

**Critère FAIL :** redirect login bloqué, exports visibles pour learner, P0 dans body.

---

## Oracles Encoors (distant — A_VÉRIFIER sans credentials)

```bash
export ENCOORS_BASE_URL=https://hugoback.encoors.com
export ENCOORS_USERNAME=<secret>
export ENCOORS_PASSWORD=<secret>
# optionnel : export ENCOORS_SESSION_ID=<uuid>

bash hugo_back/scripts/run_encoors_preprod_oracle.sh
# → docs-workspace/encoors_oracle_preprod.generated.json
```

**Scénarios :** M1, EVAL1, O1, OBS_BASE, D9BIS + probes non-auth (404 attendu routes internes).

**Critère PASS (avec auth) :** M1 200 + `memory_scope=intra_conversation` ; EVAL1 endpoints 200/403 cohérents ; O1 export contient pivot ; pas de 500.

**Critère PASS (sans auth) :** JSON généré, `authenticated: false`, probes documentés — **A_VÉRIFIER** pour parité auth.

---

## RLS production (SQL — A_VÉRIFIER)

```bash
psql -U <ROLE_APPLICATIF> -h <HOST> -d <DB> \
  -f hugo_back/scripts/audit_rls_prod_template.sql
```

**Critère PASS :** policies RLS listées pour tables sensibles ; pas de bypass applicatif détecté.

---

## Matrice domaine × tests × statut attendu

| Dom | Jeux pytest | Playwright | Oracle / SQL | Statut local | Statut Encoors |
|-----|-------------|------------|--------------|--------------|----------------|
| **10** | cluster3, cta_*, phase_progression, posture_modes | learner_a1 (P0) | — | **OK** | **A_VÉRIFIER** |
| **20** | memory_summary_smoke, session_memory, preprod_garde_fou | — | M1 | **OK** | **A_VÉRIFIER** |
| **30** | rag_support_tracing, preprod_garde_fou | B1-06 backlog | — | **OK** lexical | **A_VÉRIFIER** |
| **31** | posture_modes (API) | B1-01→06 backlog | — | **PARTIEL** | **A_VÉRIFIER** |
| **40** | trainer_knowledge, vague5 F1 | smoke_trainer | — | **OK** list | **A_VÉRIFIER** |
| **50** | calibration, context_builder | — | — | **PARTIEL** | **N/A** |
| **60** | tutor_access, vague5 T1 | smoke_tutor, tutor_b1 | — | **OK** API | **A_VÉRIFIER** |
| **70** | evaluation_trace_minimal, cluster3 | B1-05 backlog | EVAL1 | **OK** | **A_VÉRIFIER** |
| **80** | observabilite_base, d9bis | — | OBS_BASE, D9BIS | **OK** API | **404** distant documenté |
| **90** | rls, d2_m07, encadrants, preprod | learner/tutor guards | probes + SQL RLS | **OK** local | **A_VÉRIFIER** |
| **100** | d2_m06, analytics_absence, vague5 O1 | smoke_orgadmin | O1 | **OK** | **A_VÉRIFIER** |
| **110** | encadrants, cluster4 | smokes encadrants | — | **OK** | **A_VÉRIFIER** |
| **120** | — | — | — | **N/A** | **N/A** |

---

## Invariants garde-fou (bloquants)

| # | Invariant | Vérification |
|---|-----------|--------------|
| G1 | Pas de champs P0 dans UIState API | pytest cluster3 INV-01 |
| G2 | memory-summary sans verbatim brut | pytest memory + preprod |
| G3 | RAG vectoriel OFF (lexical only) | pytest preprod RAG |
| G4 | EVAL1 = pivot v1, non certifiant | pytest evaluation_trace |
| G5 | TRAINER/LEARNER 403 ExportRun org | pytest encadrants + preprod |
| G6 | Verbatim non partagé invisible tuteur | pytest vague5 + Playwright tutor |
| G7 | Routes internes observabilité non exposées front | revue front + pytest |
| G8 | `VITE_API_URL=/api` en smokes (pas Encoors accidentel) | playwright.config.ts |

**Échec sur G1–G7 = non prêt mise en ligne.**

---

## Séquence complète recommandée (ordre)

```bash
# Étape 1 — Backend
cd hugo_back && bash scripts/run_preprod_suite.sh

# Étape 2 — Bootstrap + Playwright
python manage.py bootstrap_smoke_playwright
cd ../hugo-hugolucia/frontend_1.8 && VITE_API_URL=/api npm run test:smoke

# Étape 3 — Encoors (optionnel)
bash ../../hugo_back/scripts/run_encoors_preprod_oracle.sh

# Étape 4 — RLS prod (optionnel, ops)
# psql ... -f hugo_back/scripts/audit_rls_prod_template.sql
```

---

## Tests hors suite preprod (optionnels / flaky)

```bash
# LLM-dependent — peut échouer sans provider
pytest apps/hugo/tests/test_conversation_progress.py -q

# P0 engine complet
pytest apps/hugo/tests/test_p0_non_regression.py apps/hugo/tests/test_hugo_p0_engine.py -q
```

---

## Critères de décision CTO

| Décision | Condition |
|----------|-----------|
| **GO local** | Backend preprod + Playwright PASS ; garde-fou G1–G7 OK |
| **GO Encoors** | Oracle auth PASS + parité M1/EVAL1/O1 vs local ; **A_VÉRIFIER** jusqu’à exécution |
| **NO-GO** | Fuite P0/verbatim UI ; export org accessible learner/trainer ; memory-summary expose verbatim |
| **GO partiel** | Local OK, Encoors non testé → déploiement demo/staging uniquement |

---

## Artefacts générés

| Fichier | Contenu |
|---------|---------|
| `docs-workspace/plan_tests_global_hugo.md` | Cartographie complète |
| `docs-workspace/encoors_oracle_preprod.generated.json` | Dernier oracle Encoors |
| `docs-workspace/smoke-fixtures.generated.json` | Fixtures bootstrap |
| `frontend_1.8/tests_playwright/smoke-fixtures.json` | Idem (Playwright) |

---

## AVERIFIER post-déploiement

- Parité Encoors authentifiée (clusters 10–11).
- RLS prod exécuté sur rôle applicatif réel.
- Flags prod (`10_FICHE_RUNTIME_PROD_ENCOORS.md`).
- Sélecteur posture apprenant (cluster 12) — non bloquant preprod actuel.
