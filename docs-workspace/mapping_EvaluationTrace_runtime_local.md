# Mapping EvaluationTrace — runtime local Hugo

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Date :** 2026-06-16  
**Lot :** D2-M05 — stabilisation vocabulaire post-clusters 1–4  
**Statut :** document de mapping (lecture seule — **aucune modification de code**)

---

## 0. Objet et méthode

Ce document stabilise le **mapping** entre l’objet doctrinal **EvaluationTrace** (Hugo 2.0) et les **objets réels** du backend local `hugo_back`, conformément au retex clusters 1–4 (`Retex_cluster_1-4.md`) :

- ne pas promouvoir un contrat sans preuve code/tests ;
- ne pas multiplier des représentations concurrentes sans les nommer ;
- lever le statut **AMBIGU** de la matrice cluster 2 (domaines 70 et 100, ligne D2-M05).

**Posture de lecture :**

| Tag | Usage dans ce document |
|-----|------------------------|
| **CIBLE 2.0** | Spec canonique, matrice cluster 2, note lot CTA |
| **RÉEL OBSERVÉ** | Modèles, vues, services et tests `hugo_back` (runtime local) |
| **ÉCART CONFIRMÉ** | Divergence recoupée doc ↔ code |
| **A_VÉRIFIER** | Prod Encoors, RLS Postgres, richesse ZIP Qualiopi non auditée ici |

**Hors périmètre explicite :** D9bis (`ConversationTurnLLMAnalysis`, `ConversationLLMAnalysis`), refonte chaîne d’évaluation, nouveaux exports.

**Sources mobilisées :**

- `cluster2_matrice_runtime_vs_cible.md` — §4 domaine 70, §7 domaine 100
- `10_runtime_p0_progression_uistate_note_lot_courant_cta_synthese_evaluation.md`
- `ecarts — 70_evaluation_traces_preuves.md`
- `Retex_cluster_1-4.md`
- Code : `apps/hugo/models.py`, `views_sessions.py`, `services/evaluation_service.py`, `views_traces.py`, `views_trainer.py`, `views_learners.py`, `views_evidence.py`, `apps/quality/views.py`, `apps/exports/views.py`
- Tests : `test_request_evaluation_guard.py`, `test_cta_evaluation_contract.py`, `test_conversation_progress.py`, `test_cluster3_oracles.py`, `apps/exports/tests/test_exports_run.py`

---

## 1. Photo du réel local

### 1.1 Vue d’ensemble

**RÉEL OBSERVÉ :** la branche terminale est **utilisable** mais **dispersée** sur plusieurs objets Django. Il n’existe **pas** de modèle ni d’endpoint nommé `EvaluationTrace`. La continuité produit repose sur :

1. une **évaluation calculée** persistée (`LearnerEvaluationRecord`) ;
2. une ou plusieurs **traces structurées** (`Trace`, parfois enrichies par `TraceCriterionAssessment`) ;
3. des **preuves** optionnelles (`Evidence`) ;
4. des **actions de partage et validation humaine** distinctes selon le rôle.

La **synthèse** (`request-synthesis`) est une action terminale **voisine** mais **hors objet EvaluationTrace** : elle n’alimente pas directement `LearnerEvaluationRecord` ni le schéma `trace_rich_v1` dans le flux standard apprenant.

---

### 1.2 Endpoints — branche évaluation et traces

Préfixe API Hugo : `/hugo/sessions/{session_id}/` sauf mention contraire.

| Endpoint | Méthode | Rôle | **RÉEL OBSERVÉ** |
|----------|---------|------|------------------|
| `evaluation-readiness/` | GET | Indique maturité déclenchement (`trigger_state`, message prudent) | `SessionEvaluationReadinessView` → `resolve_evaluation_readiness(progress)` |
| `request-evaluation/` | POST | Génère payload éval (LLM ou fallback), persiste `LearnerEvaluationRecord`, renvoie preview + `ui_state` | Garde `can_request_evaluation` ; `generate_evaluation_payload` ; `save_evaluation_record` ; `build_evaluation_preview` |
| `finalize-evaluation/` | POST | Persiste un `evaluation_output` fourni par le client | `save_evaluation_record` ; expose statut record et politique tuteur |
| `generate-trace/` | POST | Crée une `Trace` avec payload minimal | `GenerateTraceView` — apprenant propriétaire de la session |
| `share/` | POST | Flags `share_summary`, `share_evidence`, `share_verbatim` | `ShareView` — gouverne visibilité tuteur |
| `ui-state/` | GET | CTA `cta_evaluation` / `cta_synthesis` | `build_contract_ui_state` — lot 1 / cluster 4 |
| `request-synthesis/` | POST | Synthèse terminale (hors EvaluationTrace) | Service synthèse — voisin métier, objet distinct |

**Encadrants / historique apprenant :**

| Endpoint | Méthode | Rôle | **RÉEL OBSERVÉ** |
|----------|---------|------|------------------|
| `/traces/{trace_id}/validate/` | POST | Validation humaine d’une trace | `ValidateTraceView` — contrôle d’accès tuteur/groupe ; met à jour `validated_by` / `validated_at` ; réinitialise `LearnerState` |
| `/learners/traces/` | GET | Liste des traces de l’apprenant connecté | `LearnerTraceList` |
| `/learners/evidence/` | GET | Liste des preuves rattachées session ou trace | `LearnerEvidenceList` |
| `/evidence/` | POST | Upload preuve (trace_id ou session_id) | `EvidenceCreateView` — EXIF strip, GPS opt-in dans `meta` |
| `/hugo/trainer/evaluation-records/` | GET | Liste records org (formateur/tuteur autorisé) | `TrainerEvaluationRecordListView` |
| `/hugo/trainer/evaluation-records/{id}/validate/` | POST | Validation / rejet / commentaire tuteur sur record | `TrainerEvaluationRecordValidationView` — `tutor_validated`, statuts items |
| `/hugo/trainer/evaluation-records/export/` | GET | Export CSV/JSON des records partagés | `TrainerEvaluationRecordExportView` |

**Exports Qualiopi / analytiques :**

| Endpoint | Méthode | Rôle | **RÉEL OBSERVÉ** |
|----------|---------|------|------------------|
| `/quality/qualiopi/evidence-bundle/` | POST | ZIP bundle audit | `EvidenceBundleView` |
| `/exports/run/` | POST | Export CSV ou JSON `trace_rich_v1` | `ExportRunView` — persiste `ExportRun` |

---

### 1.3 Objets persistés et relations

```
HugoSession (1) ──(OneToOne)──► LearnerEvaluationRecord
     │
     ├──(1:N)──► Trace ──(1:N)──► TraceCriterionAssessment ──► ReferentialCriterion
     │              │
     │              └──(1:N)──► Evidence
     │
     └──(1:N)──► Evidence (direct session_id autorisé)

EvaluationPolicy ──(org, group)──► règles share_with_tutor, tutor_validation_required, allow_early_trigger
```

#### `LearnerEvaluationRecord` (`learner_evaluation_record`)

**RÉEL OBSERVÉ** — table `apps/hugo/models.py` :

| Champ | Rôle |
|-------|------|
| `session` | OneToOne — une session → au plus un record courant (upsert via `update_or_create`) |
| `learner`, `group`, `organisation` | Scoping multi-tenant |
| `overall_status` | `partial` \| `complete` \| `early_trigger` |
| `items` | JSON — liste critères positionnés (`target_item_id`, `label`, `positioning_level`, `evidence_basis`, `confidence`, `missing_evidence`, `status` draft/tutor_validated…) |
| `recap_text` | Texte récapitulatif affichable |
| `evaluation_profile_used` | Profil prompt évaluation (`default`, `early_trigger`, etc.) |
| `shared_with_tutor` | Dérivé de `EvaluationPolicy.share_with_tutor` à la sauvegarde |
| `tutor_validated`, `tutor_comment`, `tutor_validated_at`, `tutor_validated_by` | Validation humaine côté encadrant |
| `trigger_maturity` | Maturité `ConversationProgress` au moment de l’évaluation (`red`/`orange`/`green`) |

**Lien doctrinal :** c’est l’ancrage réel le plus proche d’une « trace terminale d’évaluation calculée », mais le nom runtime **n’est pas** `EvaluationTrace`.

#### `Trace` (`trace`)

**RÉEL OBSERVÉ** :

| Champ | Rôle |
|-------|------|
| `session` | FK — plusieurs traces possibles par session |
| `payload_structured` | JSON — schéma déclaré `trace_rich_v1` côté exports, **souvent minimal** à la création |
| `referential_item_id` | Optionnel |
| `validated_by`, `validated_at` | Validation humaine trace (endpoint `/traces/{id}/validate/`) |

**Deux chemins de création :**

1. **Action apprenant** — `POST .../generate-trace/` : payload fixe minimal (voir §1.4).
2. **Runtime dialogue** — `_get_or_create_runtime_trace()` pendant un tour message : même squelette minimal ; peut recevoir des `TraceCriterionAssessment` si critère focalisé dans le plan d’enseignement.

#### `TraceCriterionAssessment`

**RÉEL OBSERVÉ** — qualification critère référentiel sur une trace :

- créé/mis à jour pendant le flux message (`_apply_focus_competence_trace`) ;
- consommé par `context_builder.py` pour enrichir le contexte ;
- **non** alimenté par `request-evaluation` ni par `generate-trace` seul.

#### `Evidence`

**RÉEL OBSERVÉ** — preuve fichier (`file_path`, `meta`) liée à `trace` **ou** `session` (contrainte DB : au moins l’un des deux).

#### `EvaluationPolicy`

**RÉEL OBSERVÉ** — par `(organisation, group)` : partage tuteur, validation requise, déclenchement anticipé.

---

### 1.4 Payload `generate-trace` et `trace_rich_v1` (niveau RÉEL OBSERVÉ)

Structure créée par `GenerateTraceView` et `_get_or_create_runtime_trace` :

```json
{
  "session_id": "<uuid>",
  "learner_id": "<uuid>",
  "messages_count": <int>,
  "evaluation_criteria": [],
  "evaluation_modalities": [],
  "expected_evidence": []
}
```

**ÉCART CONFIRMÉ** par rapport à une **CIBLE 2.0** plus riche : pas de critères remplis, pas de lien explicite vers `LearnerEvaluationRecord`, pas d’agrégation des `items` d’évaluation dans `payload_structured` au moment de la génération apprenant.

L’export JSON ORGADMIN (`apps/exports/views.py`) enveloppe les traces existantes :

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

**Tests associés :** `apps/exports/tests/test_exports_run.py` (`test_json_export_returns_trace_rich_payloads`).

---

### 1.5 Payload `request-evaluation` (réponse API)

**RÉEL OBSERVÉ** — corps principal renvoyé au front apprenant :

| Clé | Contenu |
|-----|---------|
| `status` | `"evaluation_ready"` |
| `evaluation` | Preview : `title`, `text`, `competence_items[]`, `validation_candidates[]`, `record_id`, `overall_status`, `warning`, `profile_name` |
| `evaluation_record_id` | UUID `LearnerEvaluationRecord` |
| `trigger_state` | `red` \| `orange` \| `green` |
| `warning` | Message prudence si maturité non verte |
| `ui_state` | Contrat UIState complet (CTA à jour) |

Génération interne (`generate_evaluation_payload`) : appel LLM JSON structuré avec fallback déterministe à partir de `ConversationProgress.active_branches`.

**Garde d’éligibilité :** `can_request_evaluation` dans `evaluation_blocking_reasons.py` — messages lisibles, filtrage tokens P0 (`test_request_evaluation_guard.py`).

---

### 1.6 Bundles Qualiopi (`EvidenceBundleView`)

**RÉEL OBSERVÉ** — ZIP `qualiopi_evidence_bundle.zip` contenant :

| Fichier | Contenu local |
|---------|---------------|
| `traces.json` | Liste **métadonnées** : `trace_id`, `session_id`, `learner_id`, `validated_at`, `created_at` — **sans** `payload_structured` ni `LearnerEvaluationRecord` |
| `audit_log.json` | 1000 dernières entrées `AuditLog` org |
| `referentials.json` | Id + nom référentiels org |
| `active_documents.json` | Documents actifs bibliothèque groupe |
| `summary.txt` | Compteurs texte |

Filtres POST : `period.from`, `period.to`, `group_ids[]`.

**A_VÉRIFIER :** équivalence du ZIP sur `hugoback.encoors.com` ; RLS effective en prod ; présence éventuelle de fichiers additionnels non observés localement.

---

### 1.7 Synthèse vs évaluation (frontière lot courant)

| Dimension | Synthèse (`request-synthesis`) | Évaluation (`request-evaluation`) |
|-----------|-------------------------------|-----------------------------------|
| Objet persisté principal | Artefact synthèse (session / analytics) | `LearnerEvaluationRecord` |
| CTA UIState | `cta_synthesis` | `cta_evaluation` |
| Rôle dans EvaluationTrace 2.0 | **CIBLE** — voisin, pas composant de l’agrégat doctrinal | **RÉEL OBSERVÉ** — cœur de la branche terminale calculée |
| Tests | `test_cta_synthesis_contract.py`, `test_conversation_progress.py` | `test_cta_evaluation_contract.py`, `test_cluster3_oracles` A1-04 |

---

## 2. Rappel doctrinal 2.0 — EvaluationTrace

### 2.1 Ce que la cible attend (**CIBLE 2.0**)

D’après la spec canonique, le complément 2.0, `ecarts — 70_evaluation_traces_preuves.md` et la matrice cluster 2 :

**EvaluationTrace** est un **objet doctrinal** (pas encore un modèle Django) qui **agrège** de façon lisible :

- le **résultat d’évaluation** calculé (positionnement par critère, statut global, prudence si déclenchement anticipé) ;
- la **trace structurée** partageable (liens référentiel, critères couverts, modalités) ;
- les **preuves** rattachées (photos, documents) avec gouvernance EXIF/GPS ;
- les **statuts de validation humaine** (tuteur / formateur) et le partage explicite ;
- le **rôle dans les exports** Qualiopi lite ou de suivi pédagogique.

L’évaluation reste une **branche terminale** — pas une quatrième posture — activable selon maturité `ConversationProgress`, avec CTA pilotés par UIState.

### 2.2 Garde-fous non négociables (**CIBLE 2.0**)

| Garde-fou | Implication |
|---------|-------------|
| Pas de certification autonome | Hugo prépare, ne certifie pas seul |
| Validation humaine obligatoire | Tuteur/formateur tranche ; champs `tutor_validated*` côté réel |
| Pas de dump technique produit | Pas de P0 / TurnState dans UIState ni dans raisons de blocage CTA |
| Partage explicite | `share_*` session + `shared_with_tutor` sur record |
| Backend-first | Éligibilité et preview via API ; front lit `cta_*` |

### 2.3 Ce que la cible laisse ouvert (**CIBLE 2.0**)

- Format JSON canonique unique d’**EvaluationTrace** (schéma unique vs dispersion actuelle).
- Mapping fin entre validation **trace** (`/traces/validate/`) et validation **record** (`trainer/.../validate/`).
- Richesse obligatoire du `payload_structured` dans les bundles Qualiopi.

---

## 3. Table de mapping §4.2 (remplacement matrice cluster 2)

Table prête à remplacer `cluster2_matrice_runtime_vs_cible.md` §4.2.

| Rôle doctrinal (EvaluationTrace 2.0) | Objet(s) runtime réel(s) | Relation / flux | Niveau vérité | Statut doc | Action documentaire |
|--------------------------------------|--------------------------|-----------------|---------------|------------|---------------------|
| **EvaluationTrace** (agrégat doctrinal unique) | *Aucun modèle unique* — dispersion `LearnerEvaluationRecord` + `Trace` (+ `Evidence`) | Agrégation **conceptuelle** uniquement ; pas d’endpoint `evaluation-trace` | **CIBLE** | **AMBIGU** → **RENOMMER_DANS_DOC** | **Garder le nom doctrinal** ; documenter la dispersion comme **ÉCART CONFIRMÉ** assumé lot courant ; ne pas créer de modèle homonyme sans décision CTO |
| Trace terminale structurée d’évaluation (résultat calculé) | `LearnerEvaluationRecord` | OneToOne `session` ; produit par `request-evaluation` / `finalize-evaluation` | **IMPLÉMENTÉ** | **ALIGNE_DOC_PARTIEL** | Pont glossaire : EvaluationTrace.**evaluation** → `LearnerEvaluationRecord` ; mettre à jour `ecarts — 70` |
| Items / positionnement par critère | `LearnerEvaluationRecord.items[]` | JSON : `positioning_level`, `evidence_basis`, `missing_evidence`, `status` | **IMPLÉMENTÉ** | **ALIGNE** | Documenter enum `positioning_level` dans fiche contrat |
| Preview apprenant post-évaluation | `build_evaluation_preview()` → clé `evaluation` API | Non persisté séparément ; dérivé du record | **IMPLÉMENTÉ** | **ALIGNE_DOC_PARTIEL** | Distinguer preview éphémère vs record persisté |
| Trace structurée référentielle | `Trace` + `TraceCriterionAssessment` | Trace créée à la volée ou via `generate-trace` ; assessments au fil du dialogue | **IMPLÉMENTÉ** / **PARTIEL** | **PARTIEL** | Préciser que assessments ≠ items d’évaluation LLM |
| Payload trace riche `trace_rich_v1` | `Trace.payload_structured` | Souvent **minimal** à la création ; enrichi seulement indirectement | **PARTIEL** | **PARTIEL** | **ÉCART CONFIRMÉ** — ne pas présenter comme trace complète 2.0 |
| Preuves rattachées | `Evidence` | FK `trace` ou `session` ; upload `/evidence/` | **IMPLÉMENTÉ** | **ALIGNE** | Référencer ecarts-100 EXIF/GPS |
| Éligibilité évaluation | `ConversationProgress.evaluation_eligible` + `can_request_evaluation` | Reflété dans `cta_evaluation` UIState | **IMPLÉMENTÉ** | **ALIGNE** | Tests : `test_cta_evaluation_contract`, `test_request_evaluation_guard`, A1-04 |
| Readiness / prudence | `resolve_evaluation_readiness` | `evaluation-readiness/` ; `warning` dans preview | **IMPLÉMENTÉ** | **ALIGNE** | — |
| Validation humaine tuteur (record) | `LearnerEvaluationRecord.tutor_validated*` + `TrainerEvaluationRecordValidationView` | Actions `validate` / `reject` / `comment` | **IMPLÉMENTÉ** | **ALIGNE** | Ne pas confondre avec certification |
| Validation humaine trace | `Trace.validated_by/at` + `ValidateTraceView` | Met à jour `LearnerState` ; **parallèle** au record | **IMPLÉMENTÉ** | **AMBIGU** | **Décision lot courant** : deux circuits de validation coexistants — documenter, ne pas fusionner sans chantier |
| Partage tuteur | `HugoSession.share_*` + `LearnerEvaluationRecord.shared_with_tutor` | Flags indépendants | **IMPLÉMENTÉ** | **ALIGNE_DOC_PARTIEL** | Oracle confidentialité B1-01 / A1-06 |
| Politique d’évaluation groupe | `EvaluationPolicy` | `share_with_tutor`, `allow_early_trigger`, `tutor_validation_required` | **IMPLÉMENTÉ** | **ALIGNE_DOC_PARTIEL** | — |
| EvaluationTrace ↔ export Qualiopi | `EvidenceBundleView` → `traces.json` (métadonnées) | **Ne contient pas** record ni payload complet | **CREDIBLE** | **A_VÉRIFIER** | Auditer ZIP prod ; enrichissement bundle = **hors lot courant** |
| EvaluationTrace ↔ export analytique | `ExportRun` JSON `trace_rich_v1` | Inclut `payload_structured` par trace | **IMPLÉMENTÉ** | **ALIGNE_DOC_PARTIEL** | Distinguer export ORGADMIN vs bundle Qualiopi |
| Export records formateur | `TrainerEvaluationRecordExportView` | CSV/JSON des records `shared_with_tutor=true` | **IMPLÉMENTÉ** | **ALIGNE** | — |
| Artefact LLM qualité (D9bis) | *Absent* | — | **CIBLE** | **ABSENT_NOUVEAU_CONTRAT** | **Ne pas mapper** vers EvaluationTrace dans ce lot |
| Certification autonome | *Absente* | — | **ALIGNE** (doctrine) | **ALIGNE** | Interdit produit — rappel systématique |
| CTA évaluation / synthèse | `cta_evaluation`, `cta_synthesis` dans UIState | Standardisés lot 1 | **IMPLÉMENTÉ** | **ALIGNE** | Note lot CTA ; tests cluster 3/4 |

### 3.1 Légende des statuts doc (alignée matrice cluster 2)

| Statut doc | Signification dans ce mapping |
|------------|-------------------------------|
| **ALIGNE** | Nom doctrinal et réel raccordés sans friction majeure |
| **ALIGNE_DOC_PARTIEL** | Comportement OK ; documentation ou glossaire incomplets |
| **PARTIEL** | Capacité présente mais richesse ou couverture incomplète |
| **AMBIGU** | Plusieurs objets réels pour un rôle doctrinal unique |
| **RENOMMER_DANS_DOC** | Le nom doctrinal se garde ; le pont vers le réel doit être explicite |
| **ABSENT_NOUVEAU_CONTRAT** | Cible identifiée, rien d’équivalent en code |
| **A_VÉRIFIER** | Dépend prod / infra non auditée localement |

---

## 4. Décisions lot courant — EvaluationTrace (D2-M05)

### 4.1 Ce que le produit peut revendiquer (**RÉEL OBSERVÉ**, sans survendre)

| Affirmation produit autorisée | Preuve |
|-------------------------------|--------|
| Branche d’évaluation **utilisable** bout-en-bout (éligibilité → demande → preview → record persisté) | `request-evaluation`, `test_request_evaluation_guard`, A1-04 |
| **CTA standardisés** synthèse / évaluation via UIState | `test_cta_*`, note lot CTA |
| **Validation finale humaine** (tuteur/formateur) sur les records | `TrainerEvaluationRecordValidationView`, champs `tutor_validated*` |
| Traces et preuves **existants** comme objets métier séparés | Modèles `Trace`, `Evidence` ; listes apprenant |
| **Pas de certification autonome** par Hugo | Doctrine + absence de statut « certifié » automatique |
| Export **trace_rich_v1** minimal et export records formateur | `ExportRun`, `TrainerEvaluationRecordExportView` |

### 4.2 Ce qui reste hors lot (**CIBLE** — ne pas livrer ni annoncer)

| Élément | Raison |
|---------|--------|
| Objet unique `EvaluationTrace` en base ou en API | Dispersion assumée ; agrégat = **vue documentaire**, pas modèle |
| Enrichissement automatique du `payload_structured` post-évaluation | Refonte workflow — hors mapping D2-M05 |
| Bundle Qualiopi « riche » (eval + preuves + critères détaillés) | **A_VÉRIFIER** prod ; enrichissement = chantier séparé |
| D9bis / `ConversationTurnLLMAnalysis` | Purement **CIBLE** — ne pas fusionner avec EvaluationTrace |
| Mapping EvaluationTrace ↔ certification Qualiopi | Interdit par doctrine |

### 4.3 Décisions de vocabulaire (convergence)

| Terme doctrinal | Terme runtime à utiliser dans le code et les PR | Règle |
|-----------------|--------------------------------------------------|-------|
| **EvaluationTrace** | *Concept* ; jamais nom de table | Réservé specs 2.0 et docs CTO |
| Trace d’évaluation calculée | `LearnerEvaluationRecord` | Dans les tickets CODE et les APIs |
| Trace structurée / trace_rich_v1 | `Trace` + `payload_structured` | Préciser « minimale » si création apprenant |
| Preuve | `Evidence` | Inchangé |
| Validation | Préciser **record** vs **trace** | Deux endpoints distincts — ne pas fusionner dans la doc |

### 4.4 A_VÉRIFIER (Encoors / infra)

| Point | Pourquoi |
|-------|----------|
| Contenu réel des ZIP `evidence-bundle` en prod | Local = métadonnées traces seulement |
| Parité endpoints évaluation (`request-evaluation`, etc.) | `10_FICHE_RUNTIME_PROD_ENCOORS` |
| RLS Postgres sur `Trace`, `Evidence`, bundles | Migrations présentes ; efficacité prod non prouvée ici |
| Schéma `payload_structured` si sessions riches en prod | Peut diverger du minimal local |

---

## 5. Tests de référence (non-régression mapping)

Commandes reproductibles — **RÉEL OBSERVÉ** local :

```bash
cd hugo_back
source .venv/bin/activate

# Garde-fous évaluation / CTA / UIState (inclut domaine 70 partiel)
pytest -q \
  apps/hugo/tests/test_request_evaluation_guard.py \
  apps/hugo/tests/test_cta_evaluation_contract.py \
  apps/hugo/tests/test_cta_synthesis_contract.py \
  apps/hugo/tests/test_cluster3_oracles.py::test_a1_04_cta_evaluation_eligible_when_progress_green \
  apps/hugo/tests/test_conversation_progress.py::test_progress_and_ui_state_endpoints_return_contract

# Export trace_rich_v1
pytest -q apps/exports/tests/test_exports_run.py::ExportRunTests::test_json_export_returns_trace_rich_payloads
```

Ces tests **ne prouvent pas** l’existence d’EvaluationTrace agrégé ; ils prouvent la **branche terminale dispersée** décrite ci-dessus.

---

## 6. Prochaines sorties documentaires (sans ouvrir le code)

| Action | Fichier cible | Type |
|--------|---------------|------|
| Remplacer §4.2 par la table §3 de ce document | `cluster2_matrice_runtime_vs_cible.md` | DOC |
| Marquer D2-M05 **documenté** ; statut doc EvaluationTrace → **RENOMMER_DANS_DOC** | Idem §9 backlog | DOC |
| Ajouter pont glossaire EvaluationTrace → objets réels | `ecarts — 70_evaluation_traces_preuves.md` §décisions | DOC |
| Rappeler frontière bundle vs export | `ecarts — 100_exports_preuves_qualiopi_lite.md` | DOC |
| Ne pas créer de double contrat JSON EvaluationTrace avant décision CTO | — | Garde-fou Retex |

---

## 7. Synthèse une page

**CIBLE 2.0 :** EvaluationTrace = agrégat doctrinal riche (évaluation + trace + preuves + validation + exports), sans certification autonome.

**RÉEL OBSERVÉ :** pas d’agrégat unique ; **`LearnerEvaluationRecord`** porte l’évaluation calculée ; **`Trace`** (+ assessments optionnels) porte la trace structurée souvent minimale ; **`Evidence`** porte les preuves ; validations **record** et **trace** sont **deux circuits** ; bundles Qualiopi locaux n’embarquent pas le détail d’évaluation.

**Décision lot D2-M05 :** conserver le nom doctrinal **EvaluationTrace** dans les specs 2.0 ; utiliser exclusivement les noms réels dans le code ; documenter la dispersion comme **écart assumé** jusqu’à un éventuel chantier d’agrégation (hors périmètre actuel).

**A_VÉRIFIER :** prod Encoors, RLS, richesse ZIP Qualiopi.

---

**Références :** `cluster2_matrice_runtime_vs_cible.md` · `10_runtime_p0_progression_uistate_note_lot_courant_cta_synthese_evaluation.md` · `ecarts — 70_evaluation_traces_preuves.md` · `Retex_cluster_1-4.md` · `cluster4_surface_contracts.md`
