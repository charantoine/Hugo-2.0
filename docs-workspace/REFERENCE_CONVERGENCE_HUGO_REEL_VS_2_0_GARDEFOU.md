
# Référence convergence Hugo réel ↔ cible 2.0

## Garde‑fou domaines / specs / clusters

**Version :** clôture globale — clusters 1–14 + campagne tests pré‑prod (2026-06-18)

## 0. Objet du document

Ce document sert de **référence transversale** pour piloter la fin de la convergence entre **Hugo réel local** et la **cible Hugo 2.0**.
Il vise à :

- rappeler les **domaines** à couvrir (10, 20, 30, 31, 40, 50, 60, 70, 80, 90, 100, 110, 120) ;
- fixer, pour chacun, les **sources à lire**, l’**état actuel** et les **restes à traiter** ;
- structurer ces restes en **clusters** et **couronne 2.0+** pour une mise en œuvre test‑driven ;
- verrouiller les **invariants garde‑fou** avant mise en ligne.

Ce n’est pas une spec fonctionnelle exhaustive, mais un **garde‑fou** pour ne laisser passer aucun domaine ni aucune spec dans les derniers cycles.

**Documents compagnons :**

- Inventaire détaillé : `inventaire_convergence_hugo_reel_vs_cible_2_0.md`
- Plan de tests : `plan_tests_global_hugo.md`
- Checklist opérationnelle pré‑prod : `checklist_pre_prod_hugo_2_0.md`
- Handover board : `handover_hugo_reel_vs_2_0.md`

***

## 1. Règles de vérité et de lecture (rappel)

- **CIBLE 2.0**
    - `spec_canonique_hugo_2_0.md`
    - `complements_spec_2_0_depuis_anterieurs.md`
    - `specs interface 2.0.md`
    - `specs Orchestrateur diagnostic 2.0.md`
    - `specs formateur + tuteur 2.0.md`
- **RÉEL OBSERVÉ**
    - corpus 00–10 (moteur, produit, demo, Encoors, écarts doc/code),
    - `cluster2_matrice_runtime_vs_cible.md` (V3),
    - livrables clusters 8–14 (tests, ADR, notes de domaine, inventaire),
    - campagne pré‑prod : `run_preprod_suite.sh`, Playwright `test:smoke`, oracles Encoors.
- **Écarts de domaine**
    - 10 : `ecarts —10_runtime_p0_progression_uistate.md`
    - 20 : `ecarts — 20_memoire_gouvernee.md`
    - 30 : `ecarts — 30_referentiel_documentaire_rag.md`
    - 31 : `ecarts — 31_front_apprenant_postures_et_bascule.md`
    - 40 : `ecarts — 40_base_connaissances_formateur.md`
    - 50 : `ecarts — 50_orchestrateur_formateur.md`
    - 60 : `ecarts — 60_orchestrateur_tuteur.md`
    - 70 : `ecarts — 70_evaluation_traces_preuves.md`
    - 80 : `ecarts — 80_observabilite_qualite_conversationnelle.md`
    - 90 : `ecarts — 90_confidentialite_partage_multitenant_roles.md`
    - 100 : `ecarts — 100_exports_preuves_qualiopi_lite.md`
    - 110 : `ecarts — 110_interfaces_formateur_tuteur.md`
    - 120 : `ecarts — 120_intercalaires_v1.md`
- **Glossaire**
    - `glossaire_alignement_hugo_reel_vs_spec.md` — pont vocabulaire, jamais preuve d’implémentation.

**Invariants :**

- La spec 2.0 décrit la **CIBLE**, jamais une preuve de livraison.
- Le **code + tests + audits récents** décrivent le **RÉEL OBSERVÉ**.
- UIState, memory‑summary, traces, signaux sont des **états dérivés backend**, jamais la logique moteur elle‑même.
- Tout ce qui dépend du **runtime Encoors / prod / flags** reste **A_VÉRIFIER** tant qu’un oracle ou audit ops dédié n’est pas passé.

**Légende statuts (§2) :**

| Statut | Signification |
|--------|---------------|
| **RÉEL CONVERGÉ** | Lot courant local prouvé (pytest et/ou Playwright) |
| **PARTIEL** | Fondations OK, UX ou doc incomplets — non bloquant noyau |
| **COURONNE 2.0+** | Cible future explicite, hors périmètre lot courant |
| **A_VÉRIFIER** | Point infra/ops (Encoors, RLS prod, flags) — pas un trou Hugo local |

***

## 2. Vue d’ensemble des domaines — état final

| Dom | Label | RÉEL CONVERGÉ (local) | PARTIEL / doc | COURONNE 2.0+ | A_VÉRIFIER (infra/ops) |
| :-- | :-- | :-- | :-- | :-- | :-- |
| **10** | P0, progression, UIState | P0 interne, UIState, CTA backend-driven, tests cluster3/4 | CTA libellés × posture ; double builder UIState | Flag v17 comportement avancé | `HUGO_P0_V17_ENABLED` prod ; ui-state Encoors |
| **20** | Mémoire gouvernée | SessionMemoryContract, memory-summary sans verbatim, tests | Endpoint intra+inter sans `?scope=` ; pas injection prompt LLM | Mémoire inter-session au tour ; injection LTM | M1 Encoors authentifié |
| **30** | RAG / référentiel | RAG lexical gouverné, gating posture, citations badge Appui | Hiérarchie contexte v1 doc (cluster 13) | **RAG vectoriel pgvector OFF** | Pipeline TrainerKnowledge→RAG apprenant |
| **31** | Front apprenant, postures | UIState consommé, CTA, banner conversation_mode, profil youth | **Sélecteur posture G2-02 absent** ; adult/pro partiels | Matrice SW-xx complète ; 3 grammaires UX finales | Parcours posture E2E prod |
| **40** | Base connaissances formateur | List/validate knowledge prod, guards rôle | Ingest/elicitation dialogique UI | Orchestration formateur riche | Encoors knowledge |
| **50** | Orchestrateur formateur | Context builder, calibration tests | Cockpit formateur complet spec 2.0 | Orchestrateur diagnostic avancé | — |
| **60** | Orchestrateur tuteur | Timeline, traces, validation, guards verbatim | Recommandations tuteur enrichies | Pilotage moteur encadrant | Encoors timeline |
| **70** | Évaluation, traces, preuves | Chaîne EVAL1, pivot v1, disclaimer non certifiant | Pivot ≠ EvaluationTrace doctrinal complet | Agrégat doctrinal unifié | EVAL1 Encoors authentifié |
| **80** | Observabilité & qualité | Signaux persistés, obs base v3 API, D9bis backend v4 | Catalogue signaux canonique | Dashboards produit ; D9bis UI | Routes obs Encoors (404 sans auth) |
| **90** | Confidentialité, multi-tenant | RLS locale, isolation API, verbatim protégé, matrice v2 | COORDO = héritage tuteur (pas UI dédiée) | Cockpit COORDO cohorte | **RLS prod** ; EXIF prod |
| **100** | Exports, preuves Qualiopi lite | ExportRun JSON/CSV, EvidenceBundle, pivot v1, guards | Taxonomie E1–E6 doc (cluster 14) | Export debug-md superadmin | O1 Encoors ; Felix v3 |
| **110** | Interfaces encadrants | `/app/tutor`, `/app/trainer/knowledge`, smokes Playwright | Stabilisation doc surfaces | Dashboards encadrants Couronne | UI Encoors non auditée navigateur |
| **120** | Intercalaires v1 | — | — | Dossiers/intercalaires complets | — |

***

## 3. État des tests pré‑prod (2026-06-18)

Campagne documentée dans `checklist_pre_prod_hugo_2_0.md` et `plan_tests_global_hugo.md`.

### 3.1 Backend — `bash hugo_back/scripts/run_preprod_suite.sh`

| Métrique | Résultat |
|----------|----------|
| Tests exécutés | **113 passed**, **2 skipped** |
| Exit code | **0 (PASS)** |

**Fichiers clés :** `test_cluster3_oracles.py`, `test_memory_summary_smoke.py`, `test_evaluation_trace_minimal.py`, `test_preprod_garde_fou.py`, `test_rls_postgres_minimal.py`, `test_vague5_e2e_scenarios.py`, exports D2-M06/M11, encadrants guards.

**2 skips observés** (`test_rls_postgres_minimal.py`) :

1. **`test_rls_cross_tenant_hugo_session_blocked`** — skip si le rôle DB courant bypass RLS (superuser/owner). L’isolation cross-tenant reste prouvée par **`test_api_cross_tenant_session_blocked`** (403/404 API).
2. **`test_rls_audit_skipped_documentation_on_sqlite`** — skip volontaire quand PostgreSQL est disponible (test de documentation SQLite non pertinent).

> En environnement **SQLite pur**, les tests RLS Postgres sont skipif’és en bloc — RLS prod reste **A_VÉRIFIER** via `audit_rls_prod_template.sql`.

### 3.2 Playwright — `VITE_API_URL=/api npm run test:smoke`

| Métrique | Résultat |
|----------|----------|
| Specs | 10 tests (smokes cluster 8 + e2e A1/B1/COORDO) |
| Résultat | **10 passed** |

**Personae couverts :** A1 apprenant, B1 tuteur, C1 formateur (smoke), D1 ORGADMIN (exports), COORDO (héritage tuteur).

**Bootstrap :** `python manage.py bootstrap_smoke_playwright` → `smoke-fixtures.json`

### 3.3 Oracles Encoors — `bash hugo_back/scripts/run_encoors_preprod_oracle.sh`

| Métrique | Résultat |
|----------|----------|
| Sans credentials | Probes non-auth → **404** routes internes (comportement attendu : protection) |
| Avec credentials | M1, EVAL1, O1, OBS_BASE, D9BIS — **A_VÉRIFIER** |
| Artefact | `docs-workspace/encoors_oracle_preprod.generated.json` |

**Parité Encoors complète = A_VÉRIFIER** tant que `ENCOORS_USERNAME` / `ENCOORS_PASSWORD` non fournis.

### 3.4 RLS production (ops)

```bash
psql -U <ROLE_APPLICATIF> -d <DB_PROD> -f hugo_back/scripts/audit_rls_prod_template.sql
```

Statut : **A_VÉRIFIER** — distinct du vert local pytest.

***

## 4. Garde‑fous opérationnels G1–G8

Implémentation détaillée et commandes de rejeu : **`checklist_pre_prod_hugo_2_0.md`**.

| # | Invariant | Vérification | Bloquant |
|---|-----------|--------------|----------|
| **G1** | Pas de champs P0/TurnState dans UIState API | `test_cluster3_oracles` INV-01 | Oui |
| **G2** | memory-summary sans verbatim brut | `test_memory_summary_smoke`, `test_preprod_garde_fou` | Oui |
| **G3** | RAG vectoriel OFF — lexical only | `test_preprod_garde_fou`, `test_rag_support_tracing` | Oui |
| **G4** | EVAL1 = pivot v1, **non certifiant** | `test_evaluation_trace_minimal` | Oui |
| **G5** | TRAINER/LEARNER **403** ExportRun org | `test_encadrants_role_guards`, `test_preprod_garde_fou` | Oui |
| **G6** | Verbatim non partagé invisible tuteur | `test_vague5_e2e_scenarios` + Playwright tutor | Oui |
| **G7** | Routes observabilité internes non exposées front | revue front + pytest obs | Oui |
| **G8** | Smokes Playwright sur API locale (`VITE_API_URL=/api`) | `playwright.config.ts` | Oui |

**Règles transverses non négociables :**

- Mémoire **inter-session non injectée** au tour (lot courant).
- Pas de certification autonome par le moteur.
- Pas d’historique verbatim comme « mémoire » produit.
- D9bis / analytics LLM **hors exports métier** apprenant/ORGADMIN.

**Échec G1–G7 = NO-GO mise en ligne** (cf. checklist § critères CTO).

***

## 5. Check‑list domaine par domaine

### 5.1 Domaine 10 – runtime P0, progression, UIState

**Statut final :** **RÉEL CONVERGÉ** local ; **A_VÉRIFIER** flags prod.

**Ne pas oublier de lire :** spec canonique § P0 ; `cluster2_matrice_runtime_vs_cible.md` ; cluster 12 (CTA×posture).

**Doit rester vrai :** P0/TurnState internes ; UIState contrat unique front ; CTA alignés ConversationProgress.

**Restes :** DOC D2-M02 CTA×posture×RAG ; sélecteur posture → domaine 31 ; flags v17 prod **A_VÉRIFIER**.

***

### 5.2 Domaine 20 – mémoire gouvernée

**Statut final :** **RÉEL CONVERGÉ** intra-conversation ; **COURONNE** injection inter-session au tour.

**Doit rester vrai :** SessionMemoryContract sans verbatim ; memory-summary = résumés gouvernés uniquement.

**Restes :** Option `?scope=intra` (P2) ; ADR injection prompt LLM ; M1 Encoors **A_VÉRIFIER**.

**Clusters :** 9 (mémoire/eval/confidentialité), 10 (smoke), 11 (oracle M1).

***

### 5.3 Domaine 30 – référentiel documentaire / RAG

**Statut final :** **RÉEL CONVERGÉ** lexical ; **COURONNE** pgvector.

**Doit rester vrai :** RAG question-driven, renfort situé, pas moteur de cours.

**Restes :** aucun vectoriel lot courant (décision cluster 13). Contrat hiérarchie contexte v1 documenté.

**Cluster 13 :** clôture lot lexical.

***

### 5.4 Domaine 31 – front apprenant, postures et bascule

**Statut final :** **PARTIEL** — backend-first OK, UX posture **non livrée**.

**Doit rester vrai :** front consomme UIState ; set-posture API sans contrôle moteur brut.

**Restes :** sélecteur G2-02, 3 profils UX, Playwright B1-01→B1-06 (cluster 12 plan).

**Cluster 12 :** plan UX, non implémenté runtime.

***

### 5.5 Domaines 40 / 50 / 60 – formateur & tuteur (moteur + surfaces)

| Dom | Statut | Réel local | Couronne |
|-----|--------|------------|----------|
| **40** | **RÉEL CONVERGÉ** list/validate | `test_trainer_knowledge`, smoke trainer | Ingest dialogique, elicitation |
| **50** | **PARTIEL** | context_builder, calibration | Orchestrateur formateur complet spec 2.0 |
| **60** | **RÉEL CONVERGÉ** API | timeline, traces, validation, vague5 T1 | Recommandations tuteur avancées |

**Cluster 14 :** surfaces encadrants doc ; COORDO = héritage tuteur.

***

### 5.6 Domaine 70 – évaluation, traces, preuves

**Statut final :** **RÉEL CONVERGÉ** EVAL1/pivot v1 ; **A_VÉRIFIER** Encoors.

**Doit rester vrai :** validation humaine ; pas certification auto ; pivot = trace minimale exploitable.

**Restes :** mapping doctrinal EvaluationTrace ↔ pivot v1 ; oracle EVAL1 auth.

**Clusters :** 9, 11.

***

### 5.7 Domaine 80 – observabilité & qualité

**Statut final :** **RÉEL CONVERGÉ** backend base + D9bis ; **COURONNE** dashboards produit.

**Doit rester vrai :** pas de scoring opaque apprenant ; D9bis hors exports métier.

**Restes :** catalogue signaux ; UI observabilité ; Encoors routes v3/v4 **A_VÉRIFIER**.

**Clusters :** 11, 14.

***

### 5.8 Domaine 90 – confidentialité, multi-tenant, rôles

**Statut final :** **RÉEL CONVERGÉ** local ; **A_VÉRIFIER** RLS prod.

**Doit rester vrai :** verbatim privé par défaut ; RLS contrainte produit ; matrice v2.

**Restes :** RLS prod SQL ; COORDO sans UI dédiée (rôle + guard OK) ; frontière ORGADMIN/SUPERADMIN exports (ADR).

**Clusters :** 9, 10, 11, 14.

***

### 5.9 Domaine 100 – exports, preuves, Qualiopi lite

**Statut final :** **RÉEL CONVERGÉ** ExportRun/bundle local ; **A_VÉRIFIER** Encoors.

**Doit rester vrai :** exports rattachés session/trace ; Qualiopi lite ≠ certification complète.

**Restes :** taxonomie E1–E6 doc ; export debug-md Couronne ; oracle O1 auth.

**Clusters :** 9, 10, 11, 14.

***

### 5.10 Domaine 110 – interfaces formateur / tuteur

**Statut final :** **RÉEL CONVERGÉ** surfaces prod ; **COURONNE** dashboards encadrants.

**Doit rester vrai :** surfaces métier gouvernées ; pas cockpit pilotage moteur brut.

**Restes :** doc stabilisation ; smoke Playwright OK (cluster 8 + e2e).

**Cluster 14 :** plan interfaces + obs produit Couronne.

***

### 5.11 Domaine 120 – intercalaires v1

**Statut final :** **COURONNE 2.0+** — hors lot courant ; **N/A** tests preprod.

**Restes :** contrat minimal intercalaires avant implémentation.

***

## 6. Plan de mise en œuvre par clusters (historique)

| Cluster | Domaines | Livrable | Statut |
|---------|----------|----------|--------|
| **8–10** | 20, 70, 80, 90, 100 | runtime ops, RLS locale, smokes UI | **Livré** |
| **9** | 20, 70, 90 | mémoire/eval/confidentialité | **Livré** |
| **11** | 20, 70, 80, 90, 100 | verrouillage Encoors, oracles, RLS template | **Livré** |
| **12** | 31, 10, 30 | plan UX postures (pas de code) | **Plan** |
| **13** | 30 | RAG lexical clôturé, pgvector Couronne | **Livré doc** |
| **14** | 110, 80, 90, 100 | encadrants, COORDO, obs produit Couronne | **Plan doc** |
| **Preprod** | tous | `run_preprod_suite.sh`, Playwright, oracles | **Livré** |

***

## 7. Zones A_VÉRIFIER — infra / ops (pas des trous Hugo local)

Ces points concernent l’**environnement distant** ou l’**infra**, pas l’absence du noyau en local :

| Zone | Méthode | Statut |
|------|---------|--------|
| **Encoors prod** — CTA, ui-state, memory-summary, EVAL1, exports, observabilité | `run_encoors_preprod_oracle.sh` + credentials | **A_VÉRIFIER** |
| **RLS prod** — rôle applicatif Postgres réel | `audit_rls_prod_template.sql` | **A_VÉRIFIER** |
| **Flags prod** — `HUGO_P0_V17_ENABLED`, tracing, demo | `08_FLAGS`, `10_FICHE_RUNTIME_PROD_ENCOORS.md` | **A_VÉRIFIER** |
| **D9bis / obs v3 Encoors** | oracle JWT SUPERADMIN | **404** sans auth documenté |
| **EXIF strip Evidence** prod | audit manuel | **A_VÉRIFIER** |
| **UI Encoors navigateur** | Playwright contre base distante | **A_VÉRIFIER** |

Le vert local (113 + 10 tests) autorise un **GO local encadré** ; le **GO release Encoors** exige ces vérifications ops.

***

## 8. Check‑list finale “ne rien oublier”

- [x] Domaines 10–110 ont une section écarts à jour (clusters 9–14 référencés).
- [x] Domaine 120 positionné **Couronne**, N/A preprod.
- [x] ADR C9 (mémoire, exports) reflétées dans contrats et tests.
- [x] Tests OPS critiques passés localement :
    - [x] RLS locale (+ skip documentés),
    - [x] smoke memory-summary,
    - [x] smokes UI + e2e persona (10 PASS),
    - [x] oracle Encoors script prêt (parité auth **A_VÉRIFIER**).
- [x] Inventaire final : statuts CIBLE / RÉEL / COURONNE / A_VÉRIFIER dans §2.
- [x] Couronne listée distinctement : RAG vectoriel, D9bis UI, COORDO cockpit, intercalaires 120, orchestrateurs avancés, export debug-md, mémoire inter-session au tour.
- [x] Handover board : `handover_hugo_reel_vs_2_0.md`.

***

## 9. Référence opérationnelle — rejeu pré‑prod

```bash
# Backend (113 PASS, 2 SKIP)
cd hugo_back && bash scripts/run_preprod_suite.sh

# Playwright (10 PASS)
python manage.py bootstrap_smoke_playwright
cd ../hugo-hugolucia/frontend_1.8 && VITE_API_URL=/api npm run test:smoke

# Encoors (optionnel)
bash hugo_back/scripts/run_encoors_preprod_oracle.sh

# RLS prod (optionnel, ops)
# psql ... -f hugo_back/scripts/audit_rls_prod_template.sql
```

Détail complet, critères PASS/FAIL et matrice domaine × tests : **`checklist_pre_prod_hugo_2_0.md`**.

***
