# Cluster 11 — Verrouillage runtime vs Encoors

> Date : 2026-06-18  
> Scope : domaines **20, 70, 80, 90, 100** (runtime & OPS)  
> Garde-fou : `REFERENCE_CONVERGENCE_HUGO_REEL_VS_2_0_GARDEFOU.md`

---

## 1. Introduction

Le cluster 11 verrouille la **convergence runtime** entre Hugo réel **local** (post-clusters 1–10) et la cible Hugo 2.0 côté **runtime distant Encoors / prod**. Il ne couvre pas les chantiers UX lourds (31, 110), le RAG vectoriel (30), COORDO ni D9bis avancé — sauf pour confirmer que les gardes-fous (404 routes internes, pas de fuite verbatim/P0) tiennent côté distant.

Le document de garde-fou `REFERENCE_CONVERGENCE_HUGO_REEL_VS_2_0_GARDEFOU.md` fixe les invariants : spec 2.0 = CIBLE ; code + tests = RÉEL ; Encoors/prod/flags = **A_VÉRIFIER** tant qu’un oracle dédié n’a pas passé. Ce rapport consolide photo local vs Encoors, écarts classés, et backlog DOC/CODE/OPS minimal pour clôturer la vague runtime.

**Sources mobilisées :** garde-fou, inventaire convergence, cluster 10, contrats C9-DOC, ADR C9-CODE-02/03, écarts 20/70/80/90/100, `encoors_oracle.py` (cluster 11), `audit_rls_prod_template.sql`, tests pytest locaux (2026-06-18).

---

## 2. Domaine 20 — Mémoire gouvernée

### CIBLE 2.0

Mémoire **intra-conversation** gouvernée (`SessionMemoryContract`) sans verbatim ; endpoint dérivé `memory-summary` pour surfaces encadrantes ; mémoire inter-session (`LearnerThemeMemory`) préparée doctrinalement mais hors injection runtime immédiate ; jamais d’historique brut au front.

### RÉEL LOCAL (post-cluster 10)

- `SessionMemoryContract` testé (`test_session_memory_contract.py` — 5/5 dans vague antérieure).
- `GET /hugo/sessions/{id}/memory-summary/` — smoke **PASS** (`test_memory_summary_smoke.py`).
- Contrat DOC : `contrat_api_memory_summary_v1.md` ; ADR Option A `?scope=intra` recommandée (`adr_c9_code02_memory_summary_scope.md`) — **non implémentée**.
- Mémoire **non injectée** dans prompts LLM (réel confirmé clusters 9–10).
- Endpoint mélange encore `session_memory` + `theme_memories` (inter-session exposé côté API, pas au tour).

### RÉEL ENCOORS

**Non audité authentifié — A_VÉRIFIER.**

Probes cluster 11 (sans credentials) : pas de scénario M1 exécutable. Protocole prêt :

```bash
export ENCOORS_BASE_URL=https://hugoback.encoors.com
export ENCOORS_USERNAME="..."
export ENCOORS_PASSWORD="..."
export ENCOORS_SESSION_ID="<uuid>"   # optionnel
export ENCOORS_ORACLE_OUT=docs-workspace/encoors_oracle_cluster11.generated.json
cd hugo_back && python scripts/encoors_oracle.py
```

Attendu authentifié : scénario **M1** → `GET .../memory-summary/` status 200, `session_memory.memory_scope=intra_conversation`, absence de verbatim dans payload.

### ÉCARTS

| Écart | Local | Encoors | Cible | Interprétation |
|-------|-------|---------|-------|----------------|
| `theme_memories` dans memory-summary | Présent | A_VÉRIFIER | Option A scope intra | **Acceptable documenté** — ADR en attente arbitrage CTO |
| Injection LLM mémoire session | Absente | A_VÉRIFIER | Non-objectif lot courant | **Acceptable** — doc à verrouiller |
| Parité endpoint distant | OK local | A_VÉRIFIER | Aligné | **À confirmer** oracle auth |

### ACTIONS cluster 11

| Type | Action |
|------|--------|
| **DOC** | Refléter ADR scope dans `ecarts — 20_memoire_gouvernee.md` § cluster 11 ; lier garde-fou §3.2 |
| **CODE** | Aucun patch requis (Option A = couronne si arbitrage) |
| **OPS** | Conserver `test_memory_summary_smoke.py` en CI ; oracle M1 Encoors quand credentials disponibles |

---

## 3. Domaine 70 — Évaluation, traces, pivot v1

### CIBLE 2.0

Chaîne EVAL1 : readiness → request-evaluation → generate-trace ; validation **humaine** explicite ; pivot v1 = trace minimale exploitable, **≠** EvaluationTrace doctrinale complète ; pas de certification autonome.

### RÉEL LOCAL

- Chaîne EVAL1 **ALIGNE** — E2E vague 5 + `test_evaluation_trace_minimal.py` (3/3 PASS cluster 11).
- Pivot `evaluation_trace_pivot_v1` dans generate-trace et ExportRun JSON.
- Fiche : `fiche_trace_exploitable_pivot_v1.md`.
- Critères/modalités legacy generate-trace : **PARTIEL** (hors blocage runtime).

### RÉEL ENCOORS

**Non audité authentifié — A_VÉRIFIER.**

Probes non auth (2026-06-18) : routes internes observabilité/D9bis → **404** (comportement attendu sans JWT).

Protocole EVAL1 authentifié (oracle) :

1. Login JWT
2. Découverte `session_id`
3. `GET .../evaluation-readiness/`
4. `POST .../request-evaluation/`
5. `POST .../generate-trace/` → vérifier clé `evaluation_trace_pivot_v1`

Sortie : `encoors_oracle_cluster11.generated.json` (probes seuls tant que credentials absents).

### ÉCARTS

| Écart | Local | Encoors | Interprétation |
|-------|-------|---------|----------------|
| Chaîne EVAL1 complète | OK | A_VÉRIFIER | **À confirmer** — protocole prêt |
| Pivot v1 dans generate-trace | OK | A_VÉRIFIER | Idem |
| EvaluationTrace 2.0 complète | CIBLE | CIBLE | **Couronne** — pivot suffit lot courant |

### ACTIONS cluster 11

| Type | Action |
|------|--------|
| **DOC** | § cluster 11 dans `ecarts — 70_evaluation_traces_preuves.md` ; mapping pivot ↔ doctrine stabilisé (fiche C9) |
| **CODE** | Aucun |
| **OPS** | Oracle EVAL1 auth P0 ; conserver tests pivot locaux en CI |

---

## 4. Domaine 80 — Observabilité base vs D9bis

### CIBLE 2.0

Observabilité **base** backend-first, post-conversation, sans P0/verbatim brut ; D9bis = canal SUPERADMIN séparé (v4) ; pas de scoring opaque apprenant ; catalogue signaux = couronne.

### RÉEL LOCAL

- Observabilité base ORGADMIN : `GET /internal/hugo/sessions/{id}/observability/` — E2E local OK.
- D9bis + conversation-summary : SUPERADMIN only — local OK.
- Frontière doc : `note_frontiere_observabilite_base_vs_d9bis.md`.

### RÉEL ENCOORS

**Probes non authentifiés — 404 confirmés (2026-06-18) :**

| Route | Status | Note |
|-------|--------|------|
| `/internal/hugo/analytics/conversation-summary/` | 404 | Attendu sans auth / ou non déployé |
| `/internal/hugo/sessions/.../observability/` | 404 | Idem |
| `/internal/hugo/sessions/.../d9bis/export/` | 404 | Idem |

**Authentifié SUPERADMIN/ORGADMIN — A_VÉRIFIER** (oracle scénarios OBS_BASE, D9BIS ajoutés cluster 11).

Interprétation prudente : 404 sans JWT est **acceptable et documenté** (routes internes protégées). Parité fonctionnelle avec local reste **A_VÉRIFIER** avec compte encadrant réel.

### ÉCARTS

| Écart | Interprétation |
|-------|----------------|
| Routes v3/v4 absentes sans auth | **Acceptable** — garde-fou respecté |
| Parité contenu observability base | **A_VÉRIFIER** auth |
| Catalogue signaux v1 exhaustif | **Couronne** |
| Dashboards produit | **Couronne** |

### ACTIONS cluster 11

| Type | Action |
|------|--------|
| **DOC** | § cluster 11 écarts 80 ; noir sur blanc : 404 probes = attendu |
| **CODE** | Aucun |
| **OPS** | Oracle OBS_BASE + D9BIS avec JWT SUPERADMIN ; smoke UI observabilité = couronne |

---

## 5. Domaine 90 — Confidentialité, multi-tenant, RLS, rôles

### CIBLE 2.0

Verbatim non partagé privé par défaut ; aucun P0/TurnState brut au front ; RLS contrainte produit ; matrice rôles v2 ; COORDO = cible non livrée.

### RÉEL LOCAL

- Verbatim protégé — Playwright + E2E API confirmés (clusters 8–10).
- RLS policies sur `hugo_session`, `trace`, `evidence`, `export_run` — migrations OK.
- Test rôle applicatif **PASS** (`test_rls_cross_tenant_session_isolation_app_role`) — cluster 10.
- API cross-tenant → 404 — **ALIGNE**.
- Matrice : `matrice_role_visibilite_v2.md`.

### RÉEL ENCOORS (RLS prod)

**Non audité — A_VÉRIFIER.**

Template SQL livré : `hugo_back/scripts/audit_rls_prod_template.sql`

Protocole prod :

1. Connexion Postgres avec rôle applicatif **non superuser** (pas postgres).
2. Exécuter requêtes §1–2 du template (RLS enabled, policies list).
3. `SET app.organisation_id = '<ORG_A>'` puis tenter lecture session org B → attendu **0 lignes**.
4. Vérifier `rolbypassrls = false` pour le rôle courant.

Impossible sans accès DB prod — marqué **A_VÉRIFIER** avec protocole prêt.

### ÉCARTS

| Écart | Local | Encoors prod | Interprétation |
|-------|-------|--------------|----------------|
| RLS isolation tenant | PASS app role | A_VÉRIFIER | **À confirmer** OPS |
| Routes v3/v4 404 | N/A | 404 probes | **Acceptable** |
| COORDO | Absent | N/A | **Couronne** |
| ORGADMIN vs SUPERADMIN exports | ADR C9 | A_VÉRIFIER | **Acceptable documenté** |

### ACTIONS cluster 11

| Type | Action |
|------|--------|
| **DOC** | § cluster 11 écarts 90 ; référencer template RLS prod |
| **CODE** | Aucun |
| **OPS** | Conserver `test_rls_postgres_minimal.py` + setup SQL en CI ; exécuter `audit_rls_prod_template.sql` sur prod quand accès |

---

## 6. Domaine 100 — Exports, preuves, Qualiopi lite

### CIBLE 2.0

ExportRun JSON + EvidenceBundle lite rattachés session/trace ; pivot v1 dans exports métier ; bundle ≠ certification complète ; export debug-md = couronne/D9bis.

### RÉEL LOCAL

- ExportRun JSON avec `evaluation_trace_pivot_v1` — E2E O1/EVAL1 OK.
- EvidenceBundle lite — métadonnées traces, pas de pivot (by design).
- Playwright smoke exports ORGADMIN — PASS cluster 8.
- ADR : `adr_c9_code03_exports_orgadmin_superadmin.md` — maintenir `is_admin_like`.

### RÉEL ENCOORS

**Non audité authentifié — A_VÉRIFIER.**

Probes non auth : `/exports/run/` → comportement non testé sans JWT (cluster 8 : 401 attendu).

Protocole oracle O1 authentifié :

1. `POST /exports/run/?metadata_only=true` body `{"format":"json"}` → `has_pivot: true`
2. `POST /quality/qualiopi/evidence-bundle/` → status 200/201

### ÉCARTS

| Écart | Interprétation |
|-------|----------------|
| Parité ExportRun + pivot | **A_VÉRIFIER** auth |
| Parité EvidenceBundle | **A_VÉRIFIER** auth |
| Taxonomie E1–E6 | **Couronne** DOC |
| Export debug-md | **Couronne** |

### ACTIONS cluster 11

| Type | Action |
|------|--------|
| **DOC** | § cluster 11 écarts 100 ; taxonomie E1–E6 → backlog couronne |
| **CODE** | Aucun (ADR exports maintenu) |
| **OPS** | Oracle O1 auth ; smoke Playwright exports en CI (P1 backlog C10) |

---

## 7. Tableau de synthèse cluster 11

| Domaine | Local OK ? | Encoors audité ? | Actions CODE | Actions DOC | Actions OPS | A_VÉRIFIER |
|---------|------------|------------------|--------------|-------------|-------------|------------|
| **20** Mémoire | **Oui** (smoke + contrat) | **Non** (M1 auth) | 0 — Option A scope = couronne | ADR scope → écarts 20 | smoke memory-summary CI ; oracle M1 | Parité memory-summary Encoors ; scope intra |
| **70** Évaluation | **Oui** (EVAL1 + pivot) | **Non** (EVAL1 auth) | 0 | Mapping pivot → écarts 70 | oracle EVAL1 ; tests pivot CI | Chaîne EVAL1 + pivot prod |
| **80** Observabilité | **Oui** (base + D9bis local) | **Partiel** (404 probes) | 0 | 404 = attendu → écarts 80 | oracle OBS_BASE/D9BIS auth | Contenu observability auth ; deploy v3/v4 |
| **90** RLS / rôles | **Oui** (RLS app role + API) | **Non** (RLS prod) | 0 | Template RLS → écarts 90 | RLS pytest CI ; audit prod SQL | RLS prod rôle applicatif ; EXIF prod |
| **100** Exports | **Oui** (ExportRun + bundle) | **Non** (O1 auth) | 0 | ADR exports → écarts 100 | oracle O1 ; Playwright exports CI | ExportRun pivot prod ; bundle prod |

---

## 8. Outils OPS cluster 11 (reproduction)

### Oracle Encoors (probes + auth)

```bash
cd ~/Desktop/Zone\ de\ travail\ Hugo/hugo_back
source .venv/bin/activate

# Sans credentials — probes 404 uniquement
ENCOORS_ORACLE_OUT=../docs-workspace/encoors_oracle_cluster11.generated.json \
  python scripts/encoors_oracle.py

# Avec credentials — EVAL1, O1, M1, OBS_BASE, D9BIS
export ENCOORS_BASE_URL=https://hugoback.encoors.com
export ENCOORS_USERNAME="..."
export ENCOORS_PASSWORD="..."
export ENCOORS_ORACLE_OUT=../docs-workspace/encoors_oracle_cluster11.generated.json
python scripts/encoors_oracle.py
```

### Tests locaux parité (2026-06-18)

```bash
pytest apps/hugo/tests/test_rls_postgres_minimal.py \
       apps/hugo/tests/test_memory_summary_smoke.py \
       apps/hugo/tests/test_evaluation_trace_minimal.py -q
```

**Résultat observé :** 7 passed, 2 skipped.

### RLS prod (quand accès DB)

```bash
psql -U <ROLE_APPLICATIF> -d <DB_PROD> -f scripts/audit_rls_prod_template.sql
```

---

## 9. Conclusion opérationnelle

### Verrouillé (local)

- Mémoire intra-conversation + memory-summary v1 (smoke PASS).
- Chaîne EVAL1 + pivot v1 (tests PASS).
- Observabilité base vs D9bis documentée et opérationnelle en local.
- RLS tenant isolation prouvée avec rôle applicatif dédié.
- Exports Qualiopi lite + pivot dans ExportRun JSON.

### Verrouillé partiel (Encoors)

- **Garde-fous distants confirmés** : routes internes observabilité/D9bis → **404 sans auth** (comportement attendu, non régression sécurité).
- **Parité fonctionnelle authentifiée** : **non prouvée** — credentials Encoors et accès Postgres prod absents de l’environnement d’audit.

### Explicitement Couronne / vague suivante

- Option A `?scope=intra` memory-summary (ADR C9-CODE-02).
- Catalogue signaux v1 exhaustif, dashboards observabilité, D9bis avancé.
- COORDO, RAG vectoriel (30), sélecteur posture (31), interfaces encadrants stabilisées (110).
- Taxonomie exports E1–E6, export debug-md.
- CI Playwright smokes + oracle Encoors auth en pipeline (backlog C10 P1).

### Recommandation cluster suivant (B — front & postures)

Ouvrir le cluster **31 / front apprenant** : sélecteur posture G2-02, premiers profils UX, couplage CTA×posture documenté (D2-M02). Maintenir les protocoles Encoors/RLS prod documentés ici comme **checklist OPS** à exécuter dès qu’un accès prod est disponible — sans bloquer la clôture du noyau runtime local.

---

## 10. Backlog cluster 11 (6 lignes max)

| ID | Priorité | Type | Action |
|----|----------|------|--------|
| C11-OPS-01 | P0 | OPS | Exécuter oracle Encoors **authentifié** (EVAL1, O1, M1, OBS) — bloqué credentials |
| C11-OPS-02 | P0 | OPS | Exécuter `audit_rls_prod_template.sql` sur prod — bloqué accès DB |
| C11-OPS-03 | P1 | OPS | Intégrer oracle + smokes en CI (hérité C10) |
| C11-DOC-01 | P1 | DOC | Refléter cluster 11 dans écarts 20/70/80/90/100 |
| C11-DOC-02 | P2 | DOC | Taxonomie E1–E6 exports → couronne |
| C11-CODE-01 | P2 | CODE | Option A `?scope=intra` — seulement si arbitrage CTO post-cluster 11 |
