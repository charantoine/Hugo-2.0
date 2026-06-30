# Cluster 9 — Mémoire intra-conv · Évaluation/traces · Confidentialité/observabilité

> Consolidation transverse post-cluster 8 — contrats minimaux, écarts, backlog DOC/CODE/OPS  
> Date : 2026-06-18  
> Périmètre : domaines **20**, **70**, **80**, **90**, **100** (110 en lecture transverse)

---

## Sources mobilisées

### Code backend (`hugo_back`)

| Zone | Fichiers / services |
|------|---------------------|
| Mémoire intra-conv | `services/session_memory.py`, `domain/schemas.py` (`SessionMemoryContract`, `SessionMemorySummary`), `views_sessions.SessionMemorySummaryView`, `services/memory_consolidator.py`, modèle `LearnerThemeMemory` |
| Orchestration tour | `services/hugo_orchestrator.py`, `services/ui_state_builder.py`, `services/tracing.py` |
| Évaluation / traces | `views_sessions` (readiness, request/finalize evaluation, generate-trace), `services/evaluation_trace_pivot.py`, modèles `LearnerEvaluationRecord`, `Trace`, `Evidence` |
| Exports Qualiopi lite | `exports/views.py` (`ExportRun`), `quality/views.py` (`EvidenceBundleView`) |
| Observabilité | `services/session_observability.py`, `views_internal.py`, `views_internal_analytics.py` |
| Confidentialité | `referentials/access_control.py`, `views_dashboard.py` (timeline), `app_core/middleware.py` (RLS), migrations RLS |

### Tests

| Fichier | Couverture |
|---------|------------|
| `test_session_memory_contract.py` | Contrat, verbatim exclu, endpoint memory-summary (5 tests) |
| `test_memory_consolidation.py` | Consolidation inter-session `LearnerThemeMemory` |
| `test_evaluation_trace_minimal.py`, `test_vague5_e2e_scenarios.py` | Pivot v1, chaîne EVAL1/O1 |
| `test_d2_m06_d2_m11_exports_and_analytics.py`, `test_d2_m07_confidentiality_oracles.py` | Exports, bundle, matrice rôles |
| `test_rls_postgres_minimal.py` | Policies RLS, isolation API (cluster 8) |

### Front (`hugo-hugolucia/frontend_1.8`)

| Zone | Fichiers |
|------|----------|
| Rôles / exports UI | `utils/roleGuards.js`, `views/GroupView.vue`, surfaces `/app/tutor/*`, `/app/trainer/knowledge` |
| Smokes cluster 8 | `tests_playwright/*` (4/4 PASS) |

### Documentation & audits

- `ecarts — 20_memoire_gouvernee.md`, `70`, `80`, `90`, `100`, `110`
- `cluster2_matrice_runtime_vs_cible.md`
- `cluster_ops_smoke_ui_encoors_rls_resultats.md`, `cluster_retex_ops_cluster8.md`
- `plan_documentation_cto_convergence_hugo.md`
- `spec_canonique_hugo_2_0.md`, `specs interface 2.0.md`, `complements_spec_2_0_depuis_anterieurs.md`

---

## RÉEL OBSERVÉ (synthèse transverse)

### Axe 1 — Mémoire gouvernée intra-conversation (domaine 20)

**Endpoints**

| Méthode | Path | Rôle | Comportement observé |
|---------|------|------|----------------------|
| GET | `/hugo/sessions/{id}/memory-summary/` | Session owner (learner) | Retourne `session_memory` (contrat intra-conv) + `theme_memories` (jusqu’à 10 `LearnerThemeMemory`) |

Pas d’endpoint POST dédié à la mémoire intra-conversation : la mémoire est **produite** par `build_session_memory` / `build_session_memory_contract` à partir de `conversation_progress`, `turn_state` (via payloads messages) et métadonnées session.

**Objets et services**

- `SessionMemoryContract` : champs stables `session_id`, `updated_at`, `theme`, `learning_objective`, `facts_confirmed[]`, `open_points[]`, `pending_actions[]`, `memory_scope="intra_conversation"`.
- `SessionMemorySummary` : résumé gouverné + compteurs traces validées ; exposé dans **UIState** (`session_memory` dict) à chaque tour via `build_hugo_turn`.
- `LearnerThemeMemory` + `memory_consolidator.consolidate_session` : stockage **inter-session** post-conversation ; **non injecté** dans `render_with_tutor_prompt` / `prompt_renderer` (grep code : absence de `session_memory` dans les renderers LLM).
- **Injection prompt LLM** : `session_memory` est attachée au `HugoTurn`, persistée dans tracing / `llm_request_payload` pilotage, **mais pas concaténée** aux prompts système/user du renderer tutor prompt standard.

**Tests** : 5/5 `test_session_memory_contract.py` — verbatim marker absent du JSON endpoint ; filtrage messages limité à la session courante.

**Front** : aucune consommation directe de `/memory-summary/` repérée dans `frontend_1.8/src` (mémoire consommée via UIState tour, non via endpoint dédié).

### Axe 2 — Évaluation / traces / preuves + Qualiopi lite (70 + 100)

**Flux nominal observé (local, pytest E2E EVAL1)**

1. `GET .../evaluation-readiness/` — éligibilité CTA (blocking reasons).
2. `POST .../request-evaluation/` — crée/met à jour `LearnerEvaluationRecord`, preview dans UIState ; compteurs analytics.
3. `POST .../generate-trace/` — produit `trace_rich_v1` + **`evaluation_trace_pivot_v1`**.
4. `POST .../finalize-evaluation/` — persiste `evaluation_output` dans le record (validation humaine côté flux, pas auto-certification).
5. `POST /exports/run/` (ORGADMIN) — JSON `trace_rich_v1` incluant pivot.
6. `POST /quality/qualiopi/evidence-bundle/` (ORGADMIN) — ZIP métadonnées traces, audit_log, référentiels, docs actifs.

**Objets**

| Objet | Rôle observé |
|-------|--------------|
| `LearnerEvaluationRecord` | OneToOne session ; items, recap, flags tutor validation |
| `Trace` | Payload structuré ; assessments critères ; validation tuteur |
| `Evidence` | Preuves liées session/trace ; meta sans verbatim obligatoire |
| `evaluation_trace_pivot_v1` | Agrégat JSON stable (record + trace + evidence + disclaimer non certifiant) |
| `ExportRun` | Traçabilité exports org ; CSV/JSON |
| `EvidenceBundle` | ZIP Qualiopi **lite** — preuve documentaire, pas label |

**Exports de référence lot courant**

1. **JSON org** — `POST /exports/run/` format `json` → traces enrichies pivot v1.
2. **EvidenceBundle** — `POST /quality/qualiopi/evidence-bundle/` → ZIP audit + traces metadata.

Export trainer : `trainer/evaluation-records/export/` (hors bundle org).

### Axe 3 — Confidentialité / multi-tenant / observabilité (80 + 90)

**RLS (cluster 8, Postgres local)**

- Policies actives : `hugo_session`, `trace`, `evidence`, `export_run` (`organisation_id = current_setting('app.organisation_id')`).
- Isolation API : user org A → `GET /hugo/sessions/{session_org_b}/` → **404** (test pass).
- SQL cross-tenant direct : **skip** avec rôle `postgres` superuser (bypass RLS attendu).

**Verbatim / timeline (backend + Playwright cluster 8)**

- `DashboardTimelineView` : si `share_verbatim=false` → `messages=[]`, `first_learner_message=""` ; traces listées (id, dates, validation).
- Smoke TUTOR : marker verbatim absent du DOM.

**Exports / rôles**

| Rôle | Exports org (ExportRun / Bundle) | Timeline tuteur | Knowledge trainer |
|------|----------------------------------|-----------------|-------------------|
| LEARNER | 403 / CTA absents UI | N/A (guard encadrant) | 403 |
| TUTOR | 403 | Oui si lien tuteur-apprenant | Non |
| TRAINER | 403 | Non (sauf admin-like) | Oui |
| ORGADMIN | Oui | Oui (org) | Oui (admin-like) |
| SUPERADMIN | Oui (admin-like backend) | Oui | Oui |

Frontière ORGADMIN vs SUPERADMIN : backend `is_admin_like` partagé pour exports org ; endpoints D9bis / conversation-summary réservés **SUPERADMIN** (internal analytics v4).

**Observabilité**

- `GET /internal/hugo/sessions/{id}/observability/` — ORGADMIN+ ; signaux techniques, compteurs CTA, **sans** verbatim.
- D9bis build/export, conversation-summary — SUPERADMIN ; absents exports métier apprenant/encadrant.
- Encoors : routes v3/v4 → **404** (probes cluster 8).

---

## CIBLE 2.0 (lot courant cluster 9)

Lot courant **raisonnable**, sans sur-promesse :

**Domaine 20** — Mémoire intra-conversation gouvernée, structurée, sans verbatim brut ; projection produit via résumé stable ; inter-session (`LearnerThemeMemory`) préparée doctrinalement mais **hors injection tour immédiate**.

**Domaine 70** — Branche terminale d’évaluation avec validation **humaine** ; trace minimale standardisable (`evaluation_trace_pivot_v1`) ; pas de certification autonome.

**Domaine 100** — Exports et bundle Qualiopi **lite** = artefacts de preuve documentaire et traçabilité, pas équivalence Qualiopi certifiante.

**Domaines 80/90** — Multi-tenant strict ; verbatim non partagé invisible aux encadrants ; observabilité admin technique confinée ; COORDO et dashboards produit = cible future.

---

## ÉCARTS CONFIRMÉS

| Domaine | Écart | Preuve |
|---------|-------|--------|
| 20 | `SessionMemoryContract` **non injecté** dans prompts LLM (`prompt_renderer`) | Code orchestrateur vs renderers |
| 20 | Endpoint memory-summary mélange intra (`session_memory`) et inter (`theme_memories`) | `SessionMemorySummaryView` |
| 20 | UIState `session_memory` ≠ contrat doctrinal UIState mémoire dédié (D2-M04) | Matrice cluster 2 |
| 70 | `EvaluationTrace` doctrinal ≠ pivot v1 seul ; criteria legacy parfois vides | mapping D2-M05, tests |
| 70 | Circuits validation humaine parallèles (tuteur trace vs record) | ecarts-70 |
| 80 | Catalogue signaux canonique absent ; dashboards produit absents | ecarts-80 |
| 80 | Encoors : observabilité / D9bis non déployés (404) | cluster 8 |
| 90 | RLS prod non prouvé SQL avec rôle applicatif | cluster 8 skip |
| 90 | COORDO absent ; D2-M12 ORGADMIN/SUPERADMIN ouvert | specs interface |
| 100 | Export debug md absent (G3-03) ; D9bis hors exports métier | matrice cluster 2 |
| 100 | Encoors : parité exports/bundle non authentifiée | oracle partiel |

---

## Points A_VÉRIFIER

- Encoors authentifié : EVAL1/O1, payloads pivot, bundle ZIP (`ENCOORS_USERNAME/PASSWORD` absents).
- RLS SQL cross-tenant avec rôle DB **non-superuser** en prod/staging.
- Flags runtime prod (`HUGO_P0_*`, variantes LLM) — non inspectés cluster 9.
- Métriques cohorte / `cohort_dashboard` en prod.
- Injection future `LearnerThemeMemory` dans tour LLM — **non observée** aujourd’hui.
- Front distant Encoors vs smokes locaux (CORS, surfaces encadrants).

---

## Contrats minimaux (cluster 9)

### Mémoire intra-conversation — JSON produit autorisé

```json
{
  "session_memory": {
    "session_id": "uuid",
    "updated_at": "ISO8601",
    "theme": "string",
    "learning_objective": "string",
    "facts_confirmed": ["string"],
    "open_points": ["string"],
    "pending_actions": ["string"],
    "memory_scope": "intra_conversation"
  }
}
```

**Interdits exposition produit** : contenu verbatim message, `llm_request_payload` brut, `turn_state` P0, embeddings.

**Par rôle** : LEARNER lit son endpoint ; encadrants reçoivent résumés/pilotage filtrés (timeline), pas le contrat brut sauf evolution doc explicitée.

### Trace d’évaluation exploitable — pivot v1 (champs actuels)

Schéma `evaluation_trace_pivot_v1` : `schema`, `generated_at`, `session_id`, `organisation_id`, `learner_id`, `group_id`, `evaluation_record`, `trace`, `evidence[]`, `human_validation`, `certification_disclaimer`.

Exports référence : **JSON ExportRun** + **EvidenceBundle ZIP**.

### Rôle → visibilité (lot courant)

| Rôle | Voit | Ne voit pas |
|------|------|-------------|
| LEARNER | Sa session, UIState, CTA, memory-summary | Données autre org ; exports org |
| TUTOR | Timeline métadonnées + traces si lien ; synthèses/évals partagées | Verbatim si `share_verbatim=false` ; exports org ; P0 brut |
| TRAINER | Knowledge items org ; pas timeline apprenant non autorisée | Exports org ; verbatim non partagé |
| ORGADMIN | Exports, bundle, observabilité session org | Verbatim non partagé ; D9bis SUPERADMIN |
| SUPERADMIN | Internal analytics D9bis, conversation-summary | — (canal technique, hors produit apprenant) |

**Limites** : tableau basé sur code local + smokes cluster 8 ; Encoors et RLS prod rôle applicatif **A_VÉRIFIER**.

---

## Backlog cluster 9 (DOC / CODE / OPS)

| ID | Type | Domaine | Priorité | Source | Intitulé | Livrable attendu |
|----|------|---------|----------|--------|----------|------------------|
| C9-DOC-01 | DOC | 20 | P0 | § RÉEL mémoire, ecarts-20 | Contrat API `memory-summary` v1 | Note 1 page : champs autorisés, séparation intra vs `theme_memories`, interdits verbatim |
| C9-DOC-02 | DOC | 70/100 | P0 | § pivot, mapping D2-M05 | Fiche « trace exploitable » produit | Schéma pivot v1 + disclaimer validation humaine + lien exports |
| C9-DOC-03 | DOC | 90 | P0 | § tableau rôles, D2-M07 | Matrice rôle × visibilité v2 | Tableau LEARNER→SUPERADMIN validé CTO, limites Encoors/RLS |
| C9-DOC-04 | DOC | 80 | P1 | § observabilité, ecarts-80 | Note frontière observabilité base vs D9bis | ORGADMIN vs SUPERADMIN, hors UI apprenant |
| C9-CODE-01 | CODE | 20 | P2 | Écart injection prompt | Décision documentée injection `SessionMemoryContract` | ADR : injecter ou non au prochain lot ; pas d’impl sans décision |
| C9-CODE-02 | CODE | 20 | P2 | Endpoint mixte intra/inter | Query param ou split endpoint theme memories | Réduction ambiguïté memory-summary (petit patch) |
| C9-CODE-03 | CODE | 90 | P1 | D2-M12 | Affiner guard exports SUPERADMIN-only si requis | Patch minimal `is_admin_like` si décision CTO |
| C9-OPS-01 | OPS | 90 | P0 | cluster 8 RLS skip | Rôle Postgres applicatif + test SQL cross-tenant | Script/test rejouable hors superuser |
| C9-OPS-02 | OPS | 70/100 | P0 | Encoors A_VÉRIFIER | Oracle Encoors auth EVAL1/O1 | JSON résultats dans docs-workspace |
| C9-OPS-03 | OPS | 90/110 | P1 | Playwright cluster 8 | Smoke memory-summary LEARNER (sans verbatim) | 1 spec Playwright ou pytest API |

---

## Prochaine sortie utile

Valider les 4 notes DOC (C9-DOC-01 à 04) en revue CTO, puis enchaîner OPS-01/02 avant tout nouveau code mémoire inter-sessions ou dashboards Couronne.
