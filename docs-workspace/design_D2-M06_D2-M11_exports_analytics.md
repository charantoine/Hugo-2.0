# Design Cluster 7 — D2‑M06 (D9bis) + D2‑M11 (taxonomie exports & analytique)

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Date :** 2026-06-18  
**Lots :** D2‑M06 (D9bis artefacts analytiques LLM) · D2‑M11 (taxonomie exports)  
**Domaines matrice :** 70 (évaluation/traces), 80 (observabilité), 100 (exports Qualiopi lite)  
**Méthode :** backend-first, réel local audité, prod Encoors **A_VÉRIFIER**

---

## Sources mobilisées

| Source | Usage |
|--------|--------|
| `cluster2_matrice_runtime_vs_cible.md` | §0 taxonomie transversale, §4.2 EvaluationTrace, §7 domaine 100, backlog D2‑M06/M11 |
| `mapping_EvaluationTrace_runtime_local.md` | Photo endpoints exports, `trace_rich_v1`, bundles |
| `ecarts — 100_exports_preuves_qualiopi_lite.md` | Doctrine exports / preuves |
| `ecarts — 70_evaluation_traces_preuves.md` | Branche terminale, traces |
| `design_D2-M07_D2-M08_profils_grammaires_matrice_roles.md` | Matrice rôles de référence |
| `test_d2_m07_confidentiality_oracles.py` | Garde-fous déjà posés (bundle tenant, absence LLM analysis) |
| `apps/exports/views.py`, `apps/quality/views.py` | ExportRun, EvidenceBundle |
| `apps/hugo/views_trainer.py`, `views_internal.py`, `views_learners.py` | Exports métier, debug, historique apprenant |
| `apps/hugo/services/tracing.py` | turn-review, `llm_*_payload` |

---

## Synthèse exécutive

| Volet | Réel local | Décision lot Cluster 7 |
|-------|------------|----------------------|
| **Exports métier** (traces/preuves apprenant, eval formateur) | **IMPLÉMENTÉ** partiel | Documenter + tests rôle/contenu |
| **EvidenceBundle Qualiopi lite** | **IMPLÉMENTÉ** — métadonnées traces | Verrouiller tenant + absence P0/LLM analysis (déjà amorcé D2‑M07) |
| **ExportRun CSV/JSON** | **IMPLÉMENTÉ** — `trace_rich_v1` + `payload_structured` | Idem + tests négatifs P0 dans export ORGADMIN |
| **Exports techniques debug** | **PARTIEL** — `turn-review`, `pilotage`, pas `export-md` | Classer comme surface technique ; pas d’élargissement |
| **D9bis** (`ConversationTurnLLMAnalysis` / `ConversationLLMAnalysis`) | **ABSENT** comme modèles/exports dédiés | **Décision : rester CIBLE** — verrouillage par tests d’absence + frontière explicite avec debug tracing |

**Prochain move recommandé (fil d’exécution séparé) :** pack pytest `test_d2_m06_d2_m11_exports_and_analytics.py` + durcissement optionnel des permissions rôle sur `EvidenceBundleView` / `ExportRunView` (sans nouveau endpoint).

---

## 1. Photo des exports actuels (réel local)

### 1.1 Cartographie des routes

| Route | Méthode | Fichier | Rôle attendu doctrine | Garde rôle code | Niveau vérité |
|-------|---------|---------|----------------------|-----------------|---------------|
| `/quality/qualiopi/evidence-bundle/` | POST | `quality/views.py` | ORGADMIN / auditeur | `IsAuthenticated` seul (**tenant via `organisation_id`**) | **IMPLÉMENTÉ** — permissions rôle **PARTIEL** |
| `/exports/run/` | POST | `exports/views.py` | ORGADMIN | `IsAuthenticated` seul | **IMPLÉMENTÉ** — idem |
| `/exports/download/{run_id}/` | GET | `exports/views.py` | ORGADMIN | `IsAuthenticated` + filtre org sur `ExportRun` | **IMPLÉMENTÉ** |
| `/hugo/trainer/evaluation-records/export/` | GET | `views_trainer.py` | TRAINER / ORGADMIN / SUPERADMIN | `_can_manage_evaluations` | **IMPLÉMENTÉ** |
| `/learners/traces/` | GET | `views_learners.py` | LEARNER (ses traces) | `session__learner=request.user` | **IMPLÉMENTÉ** |
| `/learners/evidence/` | GET | `views_learners.py` | LEARNER (ses preuves) | filtre learner | **IMPLÉMENTÉ** |
| `/hugo/sessions/{id}/generate-trace/` | POST | `views_sessions.py` | LEARNER propriétaire | `learner=request.user` | **IMPLÉMENTÉ** |
| `/internal/hugo/sessions/{id}/turn-review/` | GET | `views_internal.py` | Admin / self learner | `is_admin_like` ou self + `HUGO_DEBUG_TRACING` | **IMPLÉMENTÉ** surface technique |
| `/internal/hugo/sessions/{id}/pilotage/` | GET | `views_internal.py` | Learner / tuteur lié / admin | RBAC + lien tuteur | **IMPLÉMENTÉ** |
| `/internal/learners/{id}/verbatim-window/` | GET | `views_internal.py` | Self / tuteur / admin + `share_verbatim` | RBAC partage | **IMPLÉMENTÉ** |
| `/hugo/sessions/{id}/debug/export-md/` | GET | — | SUPERADMIN technique | **Route absente** | **CIBLE** |
| Export D9bis analytique | — | — | SUPERADMIN testeur | **Absent** | **CIBLE** |

**Écart confirmé (permissions exports org) :** `EvidenceBundleView` et `ExportRunView` n’appliquent pas de contrôle explicite `Role.ORGADMIN`. Tout utilisateur authentifié du tenant peut théoriquement déclencher l’export. Le scoping **données** est correct (filtre `organisation_id`) ; le scoping **rôle** reste **PARTIEL / à durcir** dans le fil d’exécution (patch minimal sur permissions, pas nouveau contrat).

---

### 1.2 EvidenceBundle Qualiopi lite

**Endpoint :** `POST /quality/qualiopi/evidence-bundle/`  
**Réponse :** ZIP `qualiopi_evidence_bundle.zip`

| Fichier ZIP | Contenu observé | P0 / verbatim / LLM analysis |
|-------------|-----------------|------------------------------|
| `traces.json` | Liste `{trace_id, session_id, learner_id, validated_at, created_at}` | **Non** — métadonnées uniquement |
| `audit_log.json` | 1000 dernières entrées `{action, resource_type, resource_id, created_at}` | **Non** |
| `referentials.json` | `{id, name}` | **Non** |
| `active_documents.json` | `{id, document_id}` | **Non** |
| `summary.txt` | Compteurs traces / audit | **Non** |

**Filtres supportés :** `period.from`, `period.to`, `group_ids[]` (body JSON).

**Preuves existantes :**
- `test_cluster3_oracles.py::test_d1_02_*` — tenant isolation
- `test_d2_m07_confidentiality_oracles.py::test_d1_02_g3_02_*`, `test_f1_02_*`

**Niveau vérité :** **IMPLÉMENTÉ** (forme minimale locale) · richesse prod **A_VÉRIFIER**

**Manques vs cible 2.0 :** pas de `LearnerEvaluationRecord`, pas de `payload_structured`, pas de preuves binaires dans le ZIP, pas de lien explicite EvaluationTrace doctrinal.

---

### 1.3 ExportRun (CSV / JSON ORGADMIN)

**Endpoints :**
- `POST /exports/run/` — export synchrone ou `?metadata_only=true` (201 + métadonnées)
- `GET /exports/download/{run_id}/` — rejoue les paramètres stockés dans `ExportRun`

**Schéma JSON :** `trace_rich_v1`

```json
{
  "run_id": "<uuid>",
  "schema": "trace_rich_v1",
  "generated_at": "<iso>",
  "traces": [
    {
      "trace_id": "<uuid>",
      "session_id": "<uuid>",
      "payload_structured": { }
    }
  ]
}
```

**CSV :** colonnes métier (org, group, learner, trace, item référentiel…) — **sans** champs P0 ni payloads LLM.

**Filtres :** `period`, `group_ids`, `format` (`csv`|`json`), `separator`, `include_bom`.

**Scoping :** `Trace.objects.filter(organisation_id=request.user.organisation_id)` — tests cross-tenant dans `test_exports_run.py`.

**Contenu `payload_structured` :** tel que persisté sur `Trace` — souvent **minimal** après `generate-trace` (voir §1.5). Peut contenir des clés métier (`session_id`, `messages_count`, listes vides) mais **pas** de `turn_state` / P0 brut dans le squelette standard.

**Niveau vérité :** **IMPLÉMENTÉ** · richesse payload trace **PARTIEL**

---

### 1.4 Export métier formateur — `TrainerEvaluationRecordExportView`

**Route :** `GET /hugo/trainer/evaluation-records/export/?format=csv|json&group_id=`  
**Permission :** `_can_manage_evaluations` → `TRAINER`, `ORGADMIN`, `SUPERADMIN`  
**Filtre données :** `LearnerEvaluationRecord` avec `shared_with_tutor=True` uniquement

**Colonnes / champs :** statuts, recap, items count, profil éval, validation tuteur — **pas** de verbatim session, **pas** de P0.

**Niveau vérité :** **IMPLÉMENTÉ** (export agrégé records partagés)

---

### 1.5 Surfaces apprenant (non export fichier, mais sorties gouvernées)

| Surface | Contenu | P0 / LLM |
|---------|---------|----------|
| `GET /learners/traces/` | `TraceSerializer` inclut `payload_structured` | Pas P0 si payload minimal |
| `GET /learners/evidence/` | Métadonnées preuve + `file_path` | EXIF strip à l’upload (**A_VÉRIFIER** prod) |
| `POST .../generate-trace/` | Crée trace squelette | Pas P0 dans payload fixe |
| `GET .../ui-state/` | UIState filtré | **Non** (INV-01) |

---

### 1.6 Surfaces techniques (debug / calibration)

| Surface | Flag / garde | Contenu sensible |
|---------|--------------|------------------|
| `GET /internal/.../turn-review/` | `HUGO_DEBUG_TRACING` + admin ou self | **`llm_request_payload` complet**, `llm_response_payload`, contenu messages |
| `GET /internal/.../pilotage/` | RBAC tuteur/learner | Agrégats dérivés (pas export fichier) |
| `GET /internal/learners/.../verbatim-window/` | `share_verbatim` si tuteur | IDs + rôles messages (pas contenu dans réponse actuelle) |

**Important :** `turn-review` **n’est pas** D9bis — c’est du **debug tracing** existant. Il peut exposer des structures proches du moteur (y compris éléments dérivés de P0 dans `llm_request_payload`) **uniquement** sur surface technique bornée.

**`export-md` :** **CIBLE** — aucune route dans `urls.py` (test négatif D2‑M07 : 404).

---

### 1.7 Précurseurs LLM (≠ D9bis)

| Objet / mécanisme | Présent ? | Rôle |
|-------------------|-----------|------|
| `ConversationTurnLLMAnalysis` (modèle) | **Non** | D9bis doctrinal |
| `ConversationLLMAnalysis` (agrégat) | **Non** | D9bis doctrinal |
| `HugoMessage.llm_request_payload` | **Oui** | Stockage tour (interne + turn-review) |
| `HugoMessage.llm_response_payload` | **Oui** | Métadonnées réponse LLM |
| `build_turn_review_payload` | **Oui** | Debug review, pas export bundle |
| `ConversationQualitySignal` | **Oui** (modèle) | **Non exporté** dans bundles/ExportRun |

---

## 2. Taxonomie des exports (D2‑M11)

### 2.1 Catégories doctrine → runtime

| Catégorie | Description | Exports réels locaux | Certification |
|-----------|-------------|----------------------|---------------|
| **E1 — Métier apprenant** | Actions terminale / historique personnel | `generate-trace`, `/learners/traces`, `/learners/evidence`, synthèse/éval preview API | **Non certifiant** |
| **E2 — Métier encadrant** | Records partagés, validation | `trainer/evaluation-records/export/`, `/traces/{id}/validate/` | Validation humaine requise |
| **E3 — EvidenceBundle Qualiopi lite** | ZIP audit tenant, métadonnées | `POST /quality/qualiopi/evidence-bundle/` | **Lite / non certifiant** |
| **E4 — ExportRun ORGADMIN** | CSV/JSON traces enrichies (`trace_rich_v1`) | `POST /exports/run/`, `/exports/download/` | **Non certifiant** |
| **E5 — Export technique debug** | Review tour, pilotage, verbatim window | `/internal/.../turn-review`, `pilotage`, `verbatim-window` | Hors produit apprenant/tuteur |
| **E6 — Export analytique LLM (D9bis)** | Artefacts qualité conversationnelle structurés | **Absent** | Réservé superadmin/testeur **CIBLE** |

---

### 2.2 Matrice type d’export → rôle → contenu

| Cat. | Export / surface | LEARNER | TUTOR | TRAINER | ORGADMIN | SUPERADMIN | Contenu autorisé | Interdit |
|------|------------------|---------|-------|---------|----------|------------|------------------|----------|
| E1 | `/learners/traces/` | **V** (sien) | — | — | — | T | `payload_structured` trace propre | P0, données autrui |
| E1 | `generate-trace` | **V** (sien) | — | — | — | T | Squelette trace | P0 |
| E2 | `evaluation-records/export` | — | **V**¹ | **V** | **V** | **V** | Records `shared_with_tutor=true` | Verbatim, P0 |
| E3 | EvidenceBundle ZIP | **A_VERIFIER**² | **A_VERIFIER**² | **A_VERIFIER**² | **V**³ | T | Métadonnées traces, audit, référentiels | `payload_structured`, P0, LLM analysis, verbatim |
| E4 | ExportRun CSV/JSON | **A_VERIFIER**² | **A_VERIFIER**² | **A_VERIFIER**² | **V**³ | T | Traces tenant + `payload_structured` | P0 brut, LLM analysis, cross-tenant |
| E5 | `turn-review` | Self only | — | — | **V**⁴ | **V** | Debug payload tour | Surface produit standard |
| E5 | `export-md` | — | — | — | — | **CIBLE** | — | Toute surface non technique |
| E6 | D9bis export | — | — | — | — | **CIBLE** | Artefacts analytiques dédiés | Toute surface E1–E4 |

¹ TUTOR via rôle TRAINER dans `_can_manage_evaluations` (pas de rôle TUTOR seul sur cet export — **nuance doc**).  
² Code actuel : `IsAuthenticated` seul — **écart permissions** à traiter en exécution.  
³ Doctrine : ORGADMIN ; réel : tout membre du tenant peut appeler tant que non corrigé.  
⁴ `is_admin_like` — ORGADMIN / SUPERADMIN.

---

### 2.3 Garanties de non-fuite (cible Cluster 7)

| Risque | E3 Bundle | E4 ExportRun | E1/E2 métier | E5 debug | E6 D9bis |
|--------|-----------|--------------|--------------|----------|----------|
| P0 / TurnState brut | **Absent** (réel OK) | **Absent** dans CSV ; **A_VERIFIER** si payload enrichi manuellement | UIState filtré | **Présent** dans turn-review (volontaire) | N/A |
| Verbatim non partagé | **Absent** | **Absent** | Partage gouverné | verbatim-window gated | N/A |
| LLM analysis D9bis | **Absent** | **Absent** | **Absent** | ≠ D9bis | **CIBLE** |
| Cross-tenant | Filtré org | Filtré org + tests | Filtré org | Filtré org | Tests requis |

---

## 3. Décision D9bis (D2‑M06)

### 3.1 Analyse du code

**Réel confirmé :**
- Aucun modèle `ConversationTurnLLMAnalysis` ni `ConversationLLMAnalysis` (grep vide).
- Aucun endpoint d’export analytique LLM dédié.
- Précurseurs techniques : `llm_request_payload`, `llm_response_payload`, `turn-review` (debug), `ConversationQualitySignal` (non exporté).

**Ce qui existe n’est pas D9bis :**
- `turn-review` = outil de calibration/debug sous flag `HUGO_DEBUG_TRACING`, pas un artefact produit exportable.
- `llm_response_payload` sur message = traçage technique runtime, pas un contrat d’analyse conversationnelle 2.0.

### 3.2 Décision lot courant (Cluster 7)

> **D9bis reste CIBLE** pour ce cycle de convergence.  
> **Ne pas créer** de modèles `ConversationTurnLLMAnalysis` / `ConversationLLMAnalysis` ni d’export analytique dédié dans le fil d’exécution immédiat.

**Justification :**
- Le noyau apprenant + confidentialité vient d’être verrouillé ; ouvrir D9bis implémentation maintenant risquerait une fuite sur E3/E4 avant permissions rôle corrigées.
- Les besoins métier ORGADMIN sont couverts partiellement par E3/E4 (traces) sans analytique LLM.
- La doctrine 2.0 place D9bis en surface **strictement technique** — mieux vaut un contrat d’absence prouvé qu’un artefact minimal mal borné.

**Alternative documentée (hors lot immédiat) :** si priorisation CTO ultérieure, premier incrément D9bis minimal =
1. Modèle lecture seule ou vue matérialisée **sans** exposition API produit ;
2. Export JSON sous `/internal/...` ou admin Django uniquement ;
3. Flag `HUGO_DEBUG_TRACING` ou rôle SUPERADMIN explicite ;
4. **Jamais** dans EvidenceBundle / ExportRun / UIState.

### 3.3 Contrat d’absence D9bis (à tester)

Les exports et surfaces **E1–E4** ne doivent **pas** contenir :
- clés `ConversationTurnLLMAnalysis`, `ConversationLLMAnalysis`, `llm_analysis` ;
- dumps complets `llm_request_payload` / prompts système ;
- champs P0 bruts (`turn_state`, `episode_clarity`, etc.).

**Exception volontaire :** E5 `turn-review` (hors taxonomie export métier).

---

## 4. Articulation avec D2‑M07 (matrice rôles)

| Garde-fou D2‑M07 | Extension Cluster 7 |
|------------------|---------------------|
| B1‑01 verbatim timeline | Inchangé — hors exports |
| D1‑02 / G3‑02 bundle tenant | Compléter tests ExportRun cross-tenant explicites |
| G3‑03 export-md 404 | Maintenir |
| F1‑02 absence LLM analysis bundle | Étendre à ExportRun JSON |
| INV‑01 UIState sans P0 | Ne pas rouvrir |

**Nouveau point Cluster 7 :** tests négatifs **LEARNER → EvidenceBundle / ExportRun** (403 attendu après patch permissions) ou documentation explicite si décision de laisser ouvert temporairement.

---

## 5. Plan d’exécution (fil séparé — backend + tests)

### 5.1 Patchs backend proposés (ordre)

| # | Fichier | Modification | Priorité |
|---|---------|--------------|----------|
| 1 | `apps/hugo/tests/test_d2_m06_d2_m11_exports_and_analytics.py` | **Créer** — pack pytest (§5.2) | P0 |
| 2 | `apps/quality/views.py` | Ajouter garde rôle `ORGADMIN` (± `SUPERADMIN`) sur `EvidenceBundleView` | P1 |
| 3 | `apps/exports/views.py` | Idem sur `ExportRunView` / `ExportDownloadView` | P1 |
| 4 | `apps/hugo/tests/test_d2_m07_confidentiality_oracles.py` | Factoriser helpers bundle si duplication | P3 |
| — | Pas de nouveau endpoint | — | — |
| — | Pas de modèle D9bis | — | — |

**Ne pas modifier :** `generate-trace` payload, EvaluationTrace mapping, UIState, orchestrateur P0, RLS migrations.

### 5.2 Pack pytest proposé

**Fichier :** `hugo_back/apps/hugo/tests/test_d2_m06_d2_m11_exports_and_analytics.py`  
*(Peut inclure des imports depuis `apps/exports/tests/` pour ExportRun — ou un fichier sibling `apps/exports/tests/test_d2_m11_export_guards.py`.)*

| Test | Oracle / règle | Type |
|------|----------------|------|
| `test_evidence_bundle_traces_json_shape` | D2‑M11 E3 | Positif — clés autorisées uniquement |
| `test_evidence_bundle_no_payload_structured` | E3 non-fuite | Négatif |
| `test_evidence_bundle_no_p0_tokens` | Confidentialité | Négatif — grep sérialisation |
| `test_export_run_json_includes_payload_structured` | E4 | Positif |
| `test_export_run_json_no_llm_analysis` | F1‑02 / D9bis | Négatif |
| `test_export_run_json_no_p0_in_standard_trace` | E4 garde-fou | Négatif — trace squelette `generate-trace` |
| `test_export_run_cross_tenant` | G3‑02 | Négatif — complète `test_exports_run` |
| `test_learner_forbidden_on_evidence_bundle` | Matrice rôles | Négatif — **après patch P1** |
| `test_learner_forbidden_on_export_run` | Matrice rôles | Négatif — **après patch P1** |
| `test_trainer_eval_export_only_shared_records` | E2 | Positif |
| `test_no_d9bis_models_registered` | D2‑M06 | Négatif — grep apps registry |
| `test_turn_review_not_in_bundle_or_export_run` | Frontière E5/E6 | Négatif |

### 5.3 Commandes de clôture (à intégrer à la suite existante)

```bash
cd hugo_back
.venv/bin/python -m pytest \
  apps/hugo/tests/test_d2_m06_d2_m11_exports_and_analytics.py \
  apps/exports/tests/test_exports_run.py \
  apps/hugo/tests/test_d2_m07_confidentiality_oracles.py \
  apps/hugo/tests/test_cluster3_oracles.py \
  apps/hugo/tests/test_cluster4_surface_contracts.py \
  apps/hugo/tests/test_p0_non_regression.py \
  -q
```

**Front :** aucun changement attendu (backend-first, pas de logique droits front).

---

## 6. Décisions de convergence

| Élément | Statut après Cluster 7 (design) |
|---------|----------------------------------|
| Taxonomie E1–E6 | **LIVRÉ** (ce document) |
| EvidenceBundle forme locale | **IMPLÉMENTÉ** — métadonnées |
| ExportRun `trace_rich_v1` | **IMPLÉMENTÉ** |
| Permissions rôle E3/E4 | **ÉCART** — patch P1 recommandé exécution |
| D9bis modèles/exports | **CIBLE** — absence verrouillée par tests |
| `export-md` | **CIBLE** — 404 confirmé |
| `turn-review` debug | **IMPLÉMENTÉ** — hors D9bis, hors exports métier |
| Prod Encoors / RLS | **A_VÉRIFIER** |

---

## 7. Prochaine sortie utile

1. Lancer le fil d’**exécution Cluster 7** : créer `test_d2_m06_d2_m11_exports_and_analytics.py` + patches permissions E3/E4.
2. Mettre à jour `cluster2_matrice_runtime_vs_cible.md` §0 et §7 (D2‑M06/M11 → **doc livré**, permissions → **PARTIEL**).
3. Ajouter un encart court dans `ecarts — 100_exports_preuves_qualiopi_lite.md` pointant vers la taxonomie E1–E6.

---

**Références :** `mapping_EvaluationTrace_runtime_local.md` · `design_D2-M07_D2-M08_profils_grammaires_matrice_roles.md` · `Retex_cluster_1-4.md`
