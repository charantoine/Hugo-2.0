# SPEC_POC_v1.4 — Plateforme multi-tenant "FamilleIA/CompagnIA" (POC centré Hugo)

**Date cible : 20 mars 2026**
**Contrainte : CPU-only** (pas de GPU avant mai/juin). **Latence cible : 3 s**. **Latence occasionnelle acceptable en POC : jusqu'à 15 s** (usage ponctuel).
**Principe : confidentialité-first**, pas d'OpenAI, **Mistral self-hosted** uniquement.
**Version : 1.4** — Clarification rôles Julia/Felix, évolutivité GPU, priorisation objet métier.

***

## Sources de vérité (SoT) — Hiérarchie stricte

1. **Ce fichier `SPEC_POC_v1.4.md`** = périmètre produit/technique POC (source unique).
2. **Règles Cursor + docs d'implémentation** (`.cursorrules` + `docs/*`) = dérivés de SPEC, committés dans le repo.
3. **Prompt Hugo** (`prompts/`) = SoT du comportement conversationnel.
4. **Document `.docx`** = synopsis communication (non-SoT) ; en cas de conflit, `.md` prime.

**Important** : Toute modification de SPEC nécessite la regénération des fichiers dérivés via `shell-heredoc-v1.4.txt`.


***

## Conventions de nommage

- **API \& DB** : `snake_case` (ex. `payload_structured`, `share_summary`, `organisation_id`).
- **Contexte tenant (RLS)** : clé PostgreSQL **unique** `app.organisation_id` fixée via `SET LOCAL`.
- **Exports** : CSV = livrable métier POC ; JSON = export technique du payload `trace_rich_v1` (interop/branchages).

***

## Table des matières

1. [Vision produit : architecture \& assistants](#1-vision-produit--architecture--assistants)
2. [Objectif POC](#2-objectif-poc)
3. [Doctrine technique (RLS, confidentialite, CPU-only)](#3-doctrine-technique-rls-confidentialite-cpu-only)
4. [Arbitrages validés](#4-arbitrages-valid%C3%A9s)
5. [Architecture technique](#5-architecture-technique)
6. [Rôles et visibilité](#6-r%C3%B4les-et-visibilit%C3%A9)
7. [Hugo : comportement et contexte](#7-hugo--comportement-et-contexte)
8. [Historique : A maintenant, B plus tard](#8-historique--a-maintenant-b-plus-tard)
9. [Référentiels RNCP/RS : import v2 + overlay](#9-r%C3%A9f%C3%A9rentiels-rncprs--import-v2--overlay)
10. [Bibliothèque de classe : RAG question-driven](#10-biblioth%C3%A8que-de-classe--rag-question-driven)
11. [Preuves photo : GPS opt-in](#11-preuves-photo--gps-opt-in)
12. [Exports Felix-ready](#12-exports-felix-ready)
13. [Multi-tenant : RLS Postgres](#13-multi-tenant--rls-postgres)
14. [Modèle de données : tables MVP](#14-mod%C3%A8le-de-donn%C3%A9es--tables-mvp)
15. [API endpoints MVP](#15-api-endpoints-mvp)
16. [Tests d'acceptation minimaux](#16-tests-dacceptation-minimaux)
17. [Plan d'exécution : chemin critique](#17-plan-dex%C3%A9cution--chemin-critique)
18. [Annexes : schémas JSON](#18-annexes--sch%C3%A9mas-json)
19. [Conformité Qualiopi (RNQ)](#19-conformit%C3%A9-qualiopi-rnq)
20. [Personas \& cas d'usage métier](#20-personas--cas-dusage-m%C3%A9tier)
21. [Intégrations \& effets de bord (LMS/SIRH)](#21-int%C3%A9grations--effets-de-bord-lmssirh)
22. [Changelog](#22-changelog)

***

## 1. Vision produit : architecture \& assistants

### 1.1 Plateforme multi-tenant

On construit une **plateforme multi-tenant** (plusieurs OF dans la même instance) regroupant plusieurs assistants sous une marque commune (ex. "CompagnIA", "FamilleIA").

### 1.2 Les quatre assistants — Statut POC vs POST-POC

| Assistant | Rôle | Statut | Impact SI |
| :-- | :-- | :-- | :-- |
| **Hugo** | Assistant réflexif AFEST centré apprenant. Conduit entretien, pose 1 question à la fois, relances situées via RAG (référentiel RNCP/RS + critères d'évaluation + historique niveau A), traces structurées. | **IN POC** | Cœur du POC |
| **Julia** | Gestion avancée cohortes/sous-groupes/variantes référentiels/parcours partiels + analytics. | **POST-POC** (hors POC) | Pilotage multi-cohortes |
| **Felix** | Exports financeurs/qualité/suivi + API d'export. Au POC : exports CSV/JSON Felix-ready **sans bot**. | Exports **IN POC**, bot **POST-POC** | Reporting externe |
| **Hector** | Assistant ressources/cours + support technique. Les docs existent déjà via bibliothèque de classe. | **POST-POC** (hors POC) | Support documentaire |

#### 1.2.1 Principe POC manuel → POST-POC assisté

**POC (Hugo V1)** : approche "manuelle outillée"

- Import référentiels : fichiers JSON préparés à la main (`referential_import_v2`), pas d'appel API France Compétences.
- Overlay référentiel : formulaires/écrans classiques pour activer/désactiver items, saisir exemples, erreurs fréquentes, questions coach.
- Pack Qualiopi : génération ZIP via endpoint, pas d'assistance conversationnelle.
- Exports : templates CSV/JSON configurables, déclenchés manuellement.

**POST-POC (Julia V1 + Felix bot)** : assistance progressive

- **Julia V1** : import semi-automatisé référentiels (recherche API France Compétences, normalisation, questionnaire overlay, mapping SIRH/LMS).
- **Julia V2+** : fonctions avancées (variantes automatiques, séquences optimisées, analytics cohortes) — réservées à GPU ou modèles plus puissants.
- **Felix bot** : diagnostic interactif Qualiopi (guidage indicateurs, vérification complétude, recommandations), planification exports financeurs.
- **Hector** : support documentaire conversationnel (RAG étendu, recommandations ressources).

**Objectif design** : rester compatible future évolution GPU (latence <1s, modèles 13B+, capacités raisonnement avancé) **sans casser l'architecture objet**.

### 1.3 Applications externes

- **inSitu** : Hors POC (connexion retirée), mais `payload_trace_rich_v1` conservé, export JSON pour branchement ultérieur.
- **LMS/SIRH** : Intégrations planifiées (voir section 21).

***

## 2. Objectif POC

Livrer un **POC bêta CPU-only** (cible 20 mars 2026) avec :

### Périmètre fonctionnel

- **Multi-OF cloisonné** : multi-tenant RLS Postgres (obligatoire)
- **Hugo** : chat + historique apprenant + trace structurée
- **RAG question-driven** sur bibliothèque de classe (docs `ACTIVE`)
- **Référentiel RNCP/RS** : import manuel incluant critères d'évaluation
- **Preuves photo** smartphone (EXIF supprimés par défaut, GPS opt-in individuel)
- **Vue suivi classe** minimaliste (classe/apprenant/temps/compétences)
- **Exports** : `trace_rich_v1.json` + CSV optimisé Felix-ready
- **Qualiopi** : pack audit lite **IN POC** (ZIP minimal exploitable)


### Hors périmètre POC → POST-POC

- Livret texte/PDF (optionnel si marge, sinon POST-POC)
- Pack Qualiopi complet (32 indicateurs RNQ + modules réclamations/enquêtes)
- Julia, Felix bot, Hector
- SSO, SCIM, xAPI, LTI
- Rôle **AUDITOR** + parcours d’audit interactif


***

## 3. Doctrine technique (RLS, confidentialite, CPU-only)

Ces principes sont **non-négociables** et structurent toute l'architecture.

### 3.1 Confidentialité-first

- **Verbatim privé par défaut** (partage explicite distinct : synthèse ≠ preuves ≠ verbatim)
- **Partage par défaut** : `share_summary=false`, `share_evidence=false`, `share_verbatim=false`
- **Workflow guidé POC** : message apprenant au moment validation : _"Votre tuteur a besoin de la synthèse, partagez-vous ?"_
- **Aucun log du contenu brut** `hugo_message.content` → uniquement métadonnées (IDs, timestamps, statuts, erreurs)


### 3.2 Multi-tenant : RLS Postgres (isolation stricte)

- `organisation_id` sur **toutes** tables métiers
- **chaque requête** : `SET LOCAL app.organisation_id = '{organisation_id}'` (transaction-scoped)
- **RLS policies** (pattern safe) :

```sql
ALTER TABLE my_table ENABLE ROW LEVEL SECURITY;
CREATE POLICY my_table_tenant_isolation ON my_table
  USING (organisation_id = current_setting('app.organisation_id', true)::uuid)
  WITH CHECK (organisation_id = current_setting('app.organisation_id', true)::uuid);
```

- **Tests cross-tenant obligatoires** : org A ne lit/écrit **jamais** org B


### 3.3 CPU-only (pas de GPU avant mai-juin)

- **Inference LLM** : Mistral 7B quantisé (Ollama ou llama.cpp), **pas d'OpenAI**
- **Embeddings** : local CPU (open-source, `sentence-transformers/static-similarity-mrl-multilingual-v1`, `truncate_dim=512` → config 256/512)
- **Latence cible** : 3 s (pointes jusqu'à 15 s acceptables en POC / usage ponctuel)


### 3.4 Best effort extraction docs

- PDF texte : OK
- PDF scanné : **sans OCR** (non garanti) → statut `LOW_TEXT`
- Extraction via `pypdf` ou équivalent

***

## 4. Arbitrages validés

- **Déploiement** : 1 VM + docker-compose, DB non exposée
- **Comptes** : création manuelle (pas d'invitations email)
- **Acteurs** : un acteur = 1 OF au POC (extensible)
- **Tuteur/apprenant** : relation N-N
- **Sous-groupes imbriqués** : hors POC, `parent_group_id` prévu
- **Vector store** : Postgres `pgvector` (migration Qdrant anticipée via interface)
- **Exports** : CSV = principal ; JSON = `trace_rich_v1`
- API orientée objets métier; pas d'endpoints dédiés `/julia/*` `/felix/*` `/hector/*` tant que les besoins externes ne sont pas stabilisés; Julia/Felix/Hector appellent les endpoints métier existants.

***

## 5. Architecture technique

### 5.1 Services (docker-compose)

| Service | Rôle | Tech |
| :-- | :-- | :-- |
| **nginx** | TLS, HTTP Basic (gate), rate limit, upload limits, headers | Nginx |
| **api** | FastAPI monolithe modulaire | FastAPI + SQLAlchemy 2.0 (Async) + Alembic |
| **postgres** | RLS + pgvector | PostgreSQL 15+ |
| **minio** | Uploads + exports | MinIO (S3-compatible) |
| **llm** | Inference CPU | Mistral 7B quantisé (Ollama ou llama.cpp) |
| **worker** | Tâches async (indexation, exports, recalcul `learner_state`) | Worker async Python |

### 5.2 Stack technique (fix)

- **Backend** : FastAPI
- **ORM** : SQLAlchemy 2.0 (Async)
- **Migrations** : Alembic
- **Auth** : JWT (access+refresh tokens)
- **DB** : PostgreSQL (RLS + `pgvector`)
- **Storage** : MinIO (S3-compatible)
- **Reverse proxy** : Nginx (TLS, HTTP Basic, rate limit)
- **Background jobs** : Worker async simple (pas de Kubernetes, pas de Kafka)

***

## 6. Rôles et visibilité

### 6.1 Rôles

`LEARNER`, `TUTOR`, `TRAINER`, `COORDO`, `ORGADMIN`, `SUPERADMIN`, AUDITOR (POST-POC)
Persona Qualité : compte ORGADMIN (POST-POC)
Rôle AUDITOR : compte possible mais hors périmètre POC ; accès lecture seule à des bundles/export dédiés, jamais d’accès direct au verbatim.

### 6.2 Visibilité — règles strictes

- **LEARNER** : accès complet à son historique (verbatim + traces + preuves).
- **TUTOR / TRAINER / COORDO** : accès uniquement à ce que l’apprenant a partagé (synthèse / preuves / verbatim selon flags).
- **ORGADMIN (Qualité)** : mêmes règles de confidentialité sur contenu apprenant (ne voit que le partagé), mais peut administrer (users, groupes) et déclencher exports / pack Qualiopi.
- **SUPERADMIN** : administration technique globale (à cadrer), doit respecter l’isolation multi-tenant et éviter toute lecture applicative du contenu apprenant.
- **AUDITOR (POST-POC)** : lecture seule, accès à des artefacts “auditables” (exports/bundles), pas de consultation interactive des timelines apprenants.
**Verbatim privé par défaut** (partage explicite séparé).

***

## 7. Hugo : comportement et contexte

### 7.1 Prompt AFEST = SoT conversationnelle

- Fourni par le porteur produit
- **versionner** dans `prompts/`
- **Source de vérité** du comportement conversationnel


### 7.2 Guardrails

- **1 question par message** (obligatoire)
- **Longueur limitée**


### 7.3 RAG : rôle situé

- Formuler des relances situées, **pas faire un cours**
- Retrieval **question-driven** sur bibliothèque classe


### 7.4 Référentiel : couverture \& évaluation

- Sert couverture critères + structure d'évaluation
- Inclut **critères d'évaluation**, **modalités**, **preuves attendues**

***

## 8. Historique : A maintenant, B plus tard

### 8.1 Niveau A (POC) : traces structurées uniquement

Hugo utilise l'**historique** via **traces structurées**, pas de verbatim historique.

**LearnerState (cache)** : Créer table `learner_state` (recalculée chaque validation de trace)

- `skills_matrix` : `{item_id: {last_level, last_date, trend}}`
- `missing_coverage` : `[item_ids]`
- `open_action_items`
- `summary` (≤ 25 lignes)


### 8.2 Niveau B : préparation POST-POC (verbatim-window)

Créer endpoint interne **non utilisé par défaut** :

- `GET /internal/learners/{learner_id}/verbatim-window?limit_messages=...`
- RBAC : respect du partage
- **Prêt** injecter plus tard si besoin

***

## 9. Référentiels RNCP/RS : import v2 + overlay

### 9.1 Import manuel (POC)

Importer 2 RNCP + 2 RS via JSON `referential_import_v2` (pour 2 démos / 2 formations).

Inclure **obligatoirement** :

- `evaluation_criteria` (critères d'évaluation)
- `evaluation_modalities` (modalités d'évaluation)
- `expected_evidence` (preuves attendues : `PHOTO`/`DOC`/`OBS`)
- `source_ref` (optionnel, ex. `RNCP38565`, `RS6543`)


### 9.2 Overlay par classe

Table `referential_item_overlay` (par `group_id`) :

- `enabled` / `disabled`
- `example_situations`
- `example_evidence` (type + hint)
- `common_mistakes`
- `coach_questions`
- `linked_documents` (`document_id` + `reason`)


### 9.3 Échelle d'évaluation

Par défaut : **"apprécie / participe / réalise / maîtrise"** (modifiable par classe via `scale`).

### 9.4 Julia V1 puis V2+ (POST-POC)

#### Julia V1 (import référentiels \& normalisation, POST-POC)

- **Recherche interactive API France Compétences** : dialogue ("Je cherche RNCP Électricien") → proposition fiches
- **Normalisation automatique** : extraction critères évaluation, modalités, preuves attendues
- **Questionnement guidé overlay** : assistant pose questions formateur pour enrichir overlay (exemples situations, erreurs fréquentes, questions coach)
- **Mapping nomenclature interne** : aide au mapping référentiel vers SIRH/LMS client
- **Interface** : wizard/checklist (recherche → preview → mapping → import → questionnaire overlay)


#### Julia V2+ (fonctions avancées, update ultérieur)

- Variantes automatiques parcours par profil apprenant (débutant/confirmé, métier A/B)
- Suggestions séquences pédagogiques adaptées AFEST
- Détection mises à jour référentiels (veille automatique)
- Analytics cohortes avancés
- **Pré-requis** : GPU ou modèles plus puissants (latence <1s, capacités raisonnement avancé)

**Note design** : Julia V1 reste compatible CPU-only (heuristiques + règles + RAG + petites suggestions LLM). V2+ nécessite capacités calcul/données accrues.

***

## 10. Bibliothèque de classe : RAG question-driven

### 10.1 Deux bibliothèques distinctes

- **Bibliothèque personnelle formateur** : stockée, **non utilisée** par Hugo au POC
- **Bibliothèque de classe** : docs `ACTIVE` utilisés par Hugo (RAG)


### 10.2 Indexation

**Extraction best effort** :

- PDF texte : OK
- PDF scanné : **sans OCR** → statut `LOW_TEXT`

| Type doc | Chunk size | Overlap | Structuration |
| :-- | --: | --: | :-- |
| Cours | 1200 tokens | 150 | Standard |
| Procédure/sécurité | 350 tokens | 50 | Structuré (étapes) |

**Embeddings** :

- Local CPU (`static-similarity-mrl-multilingual-v1`)
- Dimension : `dim=512` par défaut (configurable 256/512)
- Stockage : `document_chunk.embedding` (`pgvector`) + meta (page/slide)


### 10.3 Retrieval policy (question-driven)

1. Filtrer docs `ACTIVE` de la classe
2. Préférer tags `procedure`/`checklist`/`securite`/`qualite` si signaux de risque
3. Vector search (`top_k=20`)
4. Rerank lexical léger
5. Inject 1–3 chunks dans le prompt Hugo
6. Enregistrer `rag_citation` (`doc_id`, `chunk_id`, `score`, `meta`)

**Test anti-absurde obligatoire** : 8–10 requêtes "procédure" → chunk "procédure/sécurité" dans top-5.

***

## 11. Preuves photo : GPS opt-in

### 11.1 Workflow upload

1. Upload photo (smartphone)
2. Resize + thumbnail
3. **EXIF supprimés** par défaut
4. **GPS conservé** seulement si opt-in individuel (meta structuré)

### 11.2 Stockage

- MinIO (`evidence`) + table liens
- Meta GPS : `{gps_opt_in: true, gps_lat: ..., gps_lon: ...}` si opt-in

***

## 12. Exports Felix-ready

### 12.1 Format JSON

- **Download** : `trace.payload_structured` (schéma `trace_rich_v1`)
- **Export technique** du payload (interop/branchages)


### 12.2 Format CSV

| Paramètre | Défaut POC | Configurable via |
| :-- | :-- | :-- |
| Séparateur | `;` (Excel France) | `separator` |
| Encodage | UTF-8 avec BOM | `include_bom` |
| Dates | ISO (YYYY-MM-DD) | - |

**Structure** : 1 ligne = trace + item + compétence

**Pivot Excel simple** permet analyse directe dans Excel (par formateur/coordinateur).

### 12.3 Felix V1 (POST-POC) : assistance Qualiopi \& exports

#### Felix V1 (guidage Qualiopi \& planification exports)

- **Pack audit Qualiopi** :
    - Dialogue guidé : "Quel type d'audit ? Initial/Surveillance/Renouvellement ?"
    - Sélection indicateurs RNQ pertinents
    - Vérification automatique complétude dossier (alertes : "Il manque des preuves pour l'indicateur 11")
    - Recommandations amélioration : "Vos traces manquent de justifications pour 30% des évaluations"
    - Génération ZIP structuré par indicateur
- **Exports financeurs** :
    - Questionnaire besoins : "Quel financeur ? OPCO / Région / Pôle Emploi ?"
    - Documentation formats attendus par financeur
    - Alertes deadlines reporting (configurées lors création formations)
- **Interface** : wizard/checklist (type audit → indicateurs → diagnostic → génération) + mini-chat optionnel "aide" pour expliquer alertes/recommandations


#### Felix V2+ (exports avancés \& automatisation, update ultérieur)

- Génération automatique exports spécifiques OPCO/Région/Pôle Emploi (formats attendus)
- Remplissage semi-automatique formulaires bilan pédagogique/financier
- Suivi automatisé conformité multi-financeurs

**Note design** : Felix V1 reste centré processus (wizard déterministe, auditabilité Qualiopi). Interaction conversationnelle optionnelle (explainers contextuels). Templates d'export et planification/relances en POST-POC.

***

## 13. Multi-tenant : RLS Postgres

### 13.1 Règle stricte

Toutes tables métiers doivent avoir `organisation_id` (`UUID NOT NULL`) **sauf** tables globales explicites comme enums statiques (éviter au POC).

### 13.2 Pattern RLS safe

```sql
ALTER TABLE my_table ENABLE ROW LEVEL SECURITY;
CREATE POLICY my_table_tenant_isolation ON my_table
  USING (organisation_id = current_setting('app.organisation_id', true)::uuid)
  WITH CHECK (organisation_id = current_setting('app.organisation_id', true)::uuid);
```

**Important** : forme `current_setting(..., true)` pour éviter exception si variable non définie (retourne NULL).

### 13.3 Contexte tenant (par transaction)

**chaque requête** (après authentification) :

```sql
SET LOCAL app.organisation_id = '{organisation_id}';
```


### 13.4 Tests obligatoires

**Tests cross-tenant A→B** : org A ne doit **jamais** lire/écrire données org B.

***

## 14. Modèle de données : tables MVP

### 14.1 Tables POC

**Core** :

- `organisation`, `user`, `audit_log`

**Groupes \& liens** :

- `group`, `group_membership`, `tutor_learner_link`

**Hugo + traces** :

- `hugo_session`, `hugo_message`
- `trace`, `evidence`

**Documents + RAG** :

- `document`, `group_document`, `document_chunk`, `rag_citation`

**Référentiels** :

- `referential`, `referential_item`, `scale`, `scale_level`, `referential_config`, `referential_item_overlay`

**Cache + exports** :

- `learner_state`
- `export_template`, `export_run`

**Optionnel** :

- `situation_template` (P1 si marge)


### 14.2 Tables POST-POC

**Qualiopi** :

- `qualiopi_indicator_mapping` (`indicator_id` + table/schamps sources + requête SQL)
- `qualiopi_evidence_bundle` (`run_id`, `params`, `created_at`, `minio_path`)

**Intégrations** (voir section 21.7) :

- `referential_mapping` (harmonisation RNCP/RS ↔ LMS/SIRH)
- `export_template` (enrichi `column_mapping` JSONB)
- `external_identity` (SCIM provisioning)

***

## 15. API endpoints MVP

### 15.1 Auth/admin

- `POST /auth/login`
- `POST /admin/organisations`
- `POST /admin/users`
- `GET /me`
**Note (POC)** : il n’existe **pas** d’endpoint de lecture directe de `audit_log`.
L’accès à la traçabilité se fait via :
- les exports (`POST /exports/run` + `GET /exports/download/{run_id}`)
- le pack Qualiopi lite (`POST /quality/qualiopi/evidence-bundle`) qui inclut des extraits de `audit_log` filtrés.


### 15.2 Classes/liens

- `POST /groups`, `GET /groups`
- `POST /groups/{group_id}/members`
- `POST /groups/{group_id}/tutor-links`


### 15.3 Hugo

- `POST /hugo/sessions`
- `GET /hugo/sessions/{session_id}`
- `POST /hugo/sessions/{session_id}/messages`
- `POST /hugo/sessions/{session_id}/generate-trace`
- `POST /traces/{trace_id}/validate`
- `POST /hugo/sessions/{session_id}/share`...


### 15.4 Historique apprenant

- `GET /learners/sessions?from=&to=&competence_item_ids=`
- `GET /learners/traces?from=&to=&competence_item_ids=`
- `GET /learners/evidence`

### 15.4bis Preuves

- `POST /evidence` (upload photo + métadonnées, EXIF supprimés, GPS opt-in).
+**Lien (anti-preuve orpheline)** :
- Toute `evidence` doit être rattachée à **une `trace` ou une `hugo_session`** (au minimum l’un des deux).
- Une `evidence` non rattachée (ni trace, ni session) est refusée (validation API) 

### 15.5 Docs/RAG

- `POST /documents`
- `POST /documents/{document_id}/index`
- `POST /groups/{group_id}/library`
- `GET /groups/{group_id}/library`
- `PUT /groups/{group_id}/library/{group_document_id}`


### 15.6 Référentiels

- `POST /referentials/import-v2`
- `PUT /groups/{group_id}/referential-config`
- `PUT /groups/{group_id}/referentials/{ref_id}/items/{item_id}/overlay`


### 15.7 Exports

- `POST /exports/run`
- `GET /exports/download/{run_id}`


### 15.8 Dashboard

- `GET /dashboard/groups/{group_id}/learners`
- `GET /dashboard/groups/{group_id}/learners/{learner_id}/timeline`
- `GET /dashboard/groups/{group_id}/competences`


### 15.9 Internal (prépa B + debug)

- `POST /internal/rag/search`
- `GET /internal/learners/{learner_id}/verbatim-window` (non utilisé par défaut)


### 15.10 Qualiopi

- **POC** : `POST /quality/qualiopi/evidence-bundle` (pack audit lite, ZIP minimal)
- **POST-POC** : `GET /quality/qualiopi/indicators` (cartographie 32 indicateurs RNQ + couverture)

***

## 16. Tests d'acceptation minimaux

| Test | Critère |
| :-- | :-- |
| **RLS cross-tenant** | Org A ne lit/écrit jamais org B |
| **Partage confidentialité** | Tuteur/formateur ne voient rien sans partage explicite apprenant |
| **Hugo 1 question** | Hugo répond avec 1 question max par message |
| **Trace génération** | Trace générée à partir de la session → validation → exports JSON/CSV |
| **RAG anti-absurde ("procédures")** | 8–10 requêtes "procédure" → chunk "procédure/sécurité" dans top-5 |
| **Indexation LOW_TEXT** | PDF scanné → statut `LOW_TEXT` flaggé |
| **Historique apprenant** | Accessible + filtres fonctionnels (date, compétence) |


***

## 17. Plan d'exécution : chemin critique

### 17.1 Slices POC (3 semaines)

| Semaine | Slices | Livrables |
| :-- | :-- | :-- |
| **Semaine 1** | S0 (infra + gate), S1 (DB + RLS + Auth), S2 (classes/liens) | Infra + RLS + auth + groupes/tuteurs |
| **Semaine 2** | S3 (Hugo chat), S4 (trace/partage/validation), S6 (référentiels) | Hugo fonctionnel + traces + learner_state |
| **Semaine 3** | S5 (preuves photo), S7 (RAG complet), S8 (exports/dashboard) | RAG + preuves + exports + dashboard |

### 17.2 Priorité P1 (si marge)

- Situations templates (`situation_template`)


### 17.3 POST-POC

- Conformité Qualiopi complète (section 19)
- Intégrations LMS/SIRH (section 21)
- SSO, SCIM, xAPI, LTI

***

## 18. Annexes : schémas JSON

*(Contenu technique inchangé)*

***

## 19. Conformité Qualiopi (RNQ)

### 19.1 Principes

Qualiopi = **processus certifié** (RNQ = Référentiel National Qualité, 7 critères, 32 indicateurs).

### 19.2 Cartographie RNQ ↔ Fonctionnalités POC

| Critère RNQ | Indicateurs clés | Fonctionnalités POC existantes | Preuves produites | POST-POC |
| :-- | :-- | :-- | :-- | :-- |
| **Critère 1** : Informations publiques | 1, 2, 3 | Organisation OF (`organisation`), descriptifs formations (hors POC) | Export CSV métadonnées OF | API publique infos OF, catalogue formations |
| **Critère 2** : Objectifs et adaptation | 4, 5, 6 | Référentiels RNCP/RS (`referential_import_v2`), overlay par classe | Export référentiel + overlay par groupe | Analyse besoins, adaptation handicap |
| **Critère 3** : Accompagnement | 7, 8, 9 | Hugo 1 question, liens tuteur/apprenant, partage contrôlé | Historique sessions, traces validées, audit_log | Module accessibilité/handicap, suivi absences |
| **Critère 4** : Adéquation moyens | 10, 11, 12, 13 | Bibliothèque classe `ACTIVE`, RAG, preuves photo | Liste docs `ACTIVE`, logs indexation, preuves attachées | CV formateurs, suivi logistique |
| **Critère 5** : Qualification pros | 14, 15, 16 | Rôles `TUTOR`, `TRAINER`, table `user` | Export liste formateurs/tuteurs avec rôles | CV, diplômes, veille pédagogique |
| **Critère 6** : Investissement | 17, 18, 19, 20, 21 | `audit_log`, exports horodatés, traces validées | Exports CSV/JSON horodatés, audit_log par org | Module réclamations, amélioration continue, enquêtes satisfaction |
| **Critère 7** : Recueil appréciations | 22, 23, 24, 25 | Traces avec auto-évaluation (`learner_self`), validations | Export traces (statut `validated_by`, timeline) | Enquêtes satisfaction, bilans intermédiaires |

**Pour un audit AFEST Qualiopi**, les indicateurs critiques :

- **Indicateurs 7, 11, 18, 20, 22** (traces, accompagnement, évaluations, preuves)


### 19.3 Données produites (POC)

- Export CSV pivot (apprenant × compétence × date × statut)
- Export JSON `trace_rich_v1` (payload structuré interop)
- `audit_log` horodaté par `organisation_id`
- Preuves photo (MinIO + meta GPS opt-in)


### 19.4 Pack audit Qualiopi (POC lite → POST-POC complet)

#### IN POC (lite, ZIP minimal mais exploitable, sans couverture fine des 32 indicateurs)

**Contenu minimum du ZIP (POC)** :

- Exports CSV/JSON (traces, validations, preuves) sur période
- `audit_log` filtré (validations, partages, exports)
- Référentiels + overlays actifs
- Liste documents `ACTIVE` + citations RAG

**POST-POC (complet)** : mapping 32 indicateurs RNQ + modules réclamations, enquêtes, livrets PDF.

**Endpoint** : `POST /quality/qualiopi/evidence-bundle`

**Paramètres** :

```json
{
  "organisation_id": "uuid",
  "indicator_ids": [1, 3, 7, 11, 18, 20, 22],
  "period": {"from": "YYYY-MM-DD", "to": "YYYY-MM-DD"},
  "group_ids": ["uuid"],
  "anonymize": true
}
```

**Réponse** : Archive ZIP contenant, **par indicateur** :

- Liste traces/validations/preuves horodatées
- Export CSV pivot (apprenant × compétence × date × statut)
- Documents `ACTIVE` de la période
- Extraits `audit_log`
- Rapport synthèse (nb apprenants, taux validation, couverture référentiel)

**Tables POST-POC** :

- `qualiopi_indicator_mapping` (`indicator_id` + table/schamps sources + requête SQL)
- `qualiopi_evidence_bundle` (`run_id`, `params`, `created_at`, `minio_path`)


#### Felix V1 POST-POC (guidage Qualiopi)

- Dialogue guidé : choix type audit (Initial/Surveillance/Renouvellement)
- Sélection indicateurs RNQ pertinents
- Vérification automatique complétude dossier (alertes : "Il manque des preuves pour l'indicateur 11")
- Recommandations amélioration ("Vos traces manquent de justifications pour 30% des évaluations")
- Génération ZIP structuré
- Interface : wizard/checklist (parcours audit) + mini-chat optionnel (explainers)


### 19.5 Effort estimé POST-POC

| Action | Effort | Priorité |
| :-- | :-- | :-- |
| Cartographie complète 32 indicateurs → données existantes | 2j | P0 |
| Endpoint `quality/qualiopi/evidence-bundle` (ZIP) | 3j | P0 |
| Module réclamations/incidents | 3j | P1 |
| Module enquêtes satisfaction | 3j | P1 |
| Livret apprenant (organisation parcours AFEST) PDF | 2j | P1 |
| Accessibilité/handicap | 2j | P2 |
| Qualifications formateurs/tuteurs | 2j | P2 |

**Total POST-POC Qualiopi** : 15–17 jours (2–3 semaines sprint dédié).

***

## 20. Personas \& cas d'usage métier

### 20.1 Apprenant — Clara, 28 ans (boulangère AFEST)

**Contexte** : Formation électricien en AFEST sur le chantier, parcours diplômant.

**Cas d'usage** :

1. Installer app Hugo (PWA) sur smartphone
2. Démarrer session après situation de travail ("installer tableau électrique")
3. Répondre questions Hugo (1 question/tour)
4. Prendre photos preuves (GPS désactivé par défaut)
5. Valider trace apprenant → partage synthèse au tuteur (verbatim privé)
6. Consulter son historique compétences validées

**Endpoints** :

- `POST /hugo/sessions`, `POST /hugo/sessions/{session_id}/messages`
- `POST /traces/{trace_id}/validate`
- `POST /hugo/sessions/{session_id}/share`
- `GET /learners/sessions`, `GET /learners/traces`

***

### 20.2 Tuteur terrain — Marc, 45 ans (maître d'apprentissage)

**Contexte** : Suit 3 apprenants sur chantiers, valide compétences AFEST.

**Cas d'usage** :

1. Consulter dashboard classe (3 apprenants)
2. Accéder synthèses traces **partagées** par apprenant (verbatim privé, pas d'accès sans autorisation)
3. Commenter trace → feedback apprenant
4. Valider compétences acquises
5. Exporter CSV pour rapport OF mensuel

**Endpoints** :

- `GET /dashboard/groups/{group_id}/learners`
- `GET /learners/traces?from=&to=`
- `POST /traces/{trace_id}/validate`
- `POST /exports/run`

***

### 20.3 Formateur/coordinateur — Julie, 38 ans (référente pédagogique OF)

**Contexte** : Gère 10 parcours AFEST (50 apprenants), prépare audits Qualiopi.

**Cas d'usage** :

1. Créer classe (groupe) + importer référentiel RNCP
2. Activer/désactiver items référentiel (overlay par classe)
3. Uploader docs classe (procédures sécurité, fiches techniques) → indexation RAG
4. Suivre progression cohorte (dashboard agrégé)
5. Exporter pack Qualiopi (ZIP : traces + preuves + docs + audit_log)
6. Consulter audit_log conformité RGPD

**Endpoints** :

- `POST /groups`, `POST /referentials/import-v2`
- `PUT /groups/{group_id}/referentials/{ref_id}/items/{item_id}/overlay`
- `POST /documents`, `POST /documents/{document_id}/index`
- `GET /dashboard/groups/{group_id}/competences`
- `POST /quality/qualiopi/evidence-bundle`

***

### 20.4 Admin OF — Thomas, 52 ans (directeur OF)

**Contexte** : Multi-sites, gère 5 formateurs, veut piloter activité.

**Cas d'usage** :

1. Créer comptes formateurs/coordo (`ORGADMIN`)
2. Configurer exports CSV pour SIRH (séparateur `;`, encodage UTF-8 BOM)
3. Auditer logs partages/validations (RGPD)
4. Contrôler isolation tenant (tests RLS)

Endpoints :
- `POST /admin/users`
- `POST /exports/run` + `GET /exports/download/{run_id}`
- `POST /quality/qualiopi/evidence-bundle` (inclut `audit_log` filtré)
- Tests RLS cross-tenant (hors API)

***

### 20.5 Apprenant CFA — Léa, 19 ans (apprentie coiffeuse)

**Contexte** : Alternance CFA + salon, parcours CAP coiffure.

**Cas d'usage** :

1. Session Hugo post-pratique ("coupe dégradé homme")
2. Upload photo avant/après (EXIF supprimés, GPS désactivé)
3. Auto-évaluation guidée ("J'ai bien réalisé / J'ai besoin d'aide")
4. Partage synthèse + photo preuve au formateur référent CFA
5. Consulter timeline progression (compétences validées/en cours)

**Endpoints** :

**Endpoints** :

- `POST /hugo/sessions`, `POST /hugo/sessions/{session_id}/messages`
- `POST /evidence` (upload photo)
- `POST /traces/{trace_id}/validate`, `POST /hugo/sessions/{session_id}/share`
- `GET /dashboard/groups/{group_id}/learners/{learner_id}/timeline`

***

### 20.6 Responsable Formation L\&D (entreprise privée)

**Contexte** : Upskilling, onboarding, intégration SI RH, prouver montée en compétences.

**Cas d'usage** :

1. Déployer parcours AFEST sur le poste (réflexivité + preuves probantes)
2. Suivre progression par compétences (matrice, niveaux)
3. Exporter données formation vers SIRH (CSV/API) pour reporting
4. Gérer SSO et provisioning (attendus LMS/SIRH)
5. Centraliser preuves (photos/documents) avec consentements et rétention
6. Alimenter LMS existant via standards xAPI/SCORM (selon contexte)

**Endpoints** :

- `POST /hugo/sessions`, `POST /traces/{id}/validate`
- `GET /dashboard/groups/{id}/learners`
- `POST /exports/run`
- **POST-POC** : SSO (OIDC/SAML), provisioning SCIM, webhooks xAPI, endpoints LTI

***

### 20.7 Admin SI / SIRH/LMS/IT Sec

**Contexte** : Réduire risques données perso, secrets industriels, maîtriser intégrations/accès.

**Cas d'usage** :

1. Mettre en place SSO (SAML/OIDC) + politiques cycle vie comptes (SCIM)
2. Auditer isolation tenant (RLS) et contrôles applicatifs (API)
3. Valider hébergement souverain (pas API LLM externes, Mistral self-hosted CPU)
4. Définir politiques rétention/suppression (preuves, verbatim, exports) + eDiscovery
5. Contrôler effets de bord MinIO (partage liens, durée vie, permissions)
6. Limites anti-fuite (pas logs verbatim, uniquement métadonnées)

Moyens / endpoints :
- Tests cross-tenant RLS (hors API)
- `POST /quality/qualiopi/evidence-bundle` (inclut `audit_log` filtré)
- Exports horodatés (`POST /exports/run`, téléchargement)
- Configuration rétention MinIO (hors API)


***

## 21. Intégrations \& effets de bord (LMS/SIRH)

### 21.1 Écosystème logiciel OF/OFA/Entreprise

| Fonction | Outils typiques (France) | Rôle | Lien avec Hugo |
| :-- | :-- | :-- | :-- |
| **Gestion administrative OF** | Digiforma, Dendreo, TousQuali, Edof | Conventions, émargements, attestations, facturation, dossiers Qualiopi | **Complémentaire** : Hugo produit traces/preuves, ERP gère administratif |
| **LMS** | 360Learning, Moodle, Rise Up, E-TIPI | Contenu e-learning, SCORM, xAPI, parcours digitaux, quiz | **Complémentaire** : Hugo = AFEST réflexif, LMS = contenu/quiz. Intégration xAPI/LTI possible |
| **SIRH** | Workday, SAP SuccessFactors, Talentsoft, Cornerstone | Gestion collaborateurs, compétences, plan formation, reporting RH | **Intégration** : export CSV/API progression Hugo → SIRH |
| **Signature électronique** | DocuSign, Yousign, Universign | Signature conventions, bilans, attestations | **Complémentaire** : validation dans Hugo, signature administrative externe |

**Constat** : Hugo **ne remplace pas** ces outils, mais **s'intègre** en tant que **module AFEST réflexif + preuves**.

Les OF utilisent généralement **plusieurs outils complémentaires**.

### 21.2 Effets de bord identifiés + mitigations

| Effet de bord | Risque | Mitigation POC | Mitigation POST-POC |
| :-- | :-- | :-- | :-- |
| **Double saisie** | Formateur crée apprenants dans Hugo **ET** ERP OF | - | Import CSV apprenants, provisioning SCIM, API sync |
| **Divergence référentiels** | Mêmes compétences nommées différemment Hugo/LMS/SIRH | - | Table `referential_mapping`, import harmonisé RNCP/RS |
| **Conflit confidentialité vs preuve** | Partage trop opt-in → formateur/qualité ne voient rien | Workflow guidé (message explicite apprenant, partage défaut synthèse uniquement) | Profils partage par dispositif |
| **Duplication documents** | Même doc dans Hugo **ET** LMS/Digiforma | MinIO Hugo (docs classe uniquement) | GED centralisée + intégration MinIO ↔ LMS |
| **Incompatibilité exports** | CSV Hugo ≠ CSV SIRH/ERP | CSV configurable (séparateur, encodage) | Templates export (`export_template`, mapping colonnes) |
| **Authentification multiples** | Comptes séparés Hugo/LMS/SIRH | - | SSO (OIDC/SAML), provisioning automatique (SCIM) |

### 21.3 Stratégie d'intégration POST-POC

| Priorité | Intégration | Standard/techno | Effort | Bénéfice |
| :-- | :-- | :-- | :-- | :-- |
| **Principe** | **Hugo = module AFEST intégrable**, pas suite complète. |  |  |  |
| **P0** | Export CSV/JSON flexible | Templates configurables | 2j | Interopérabilité immédiate (Excel, import manuel) |
| **P1** | SSO (authentification) | OIDC (Keycloak, Auth0, Entra ID) | 3–5j | UX fluide, sécurité renforcée |
| **P1** | Import apprenants/groupes | CSV (Endpoint bulk import) | 2j | Évite double saisie manuelle |
| **P2** | Provisioning automatique | SCIM 2.0 | 5j | Cycle vie comptes automatisé |
| **P2** | API synchronisation progression | REST API + webhooks | 3–5j | Temps réel SIRH/LMS |
| **P3** | Standards e-learning | xAPI (statements traces → LRS) | 5–8j | Consolidation LMS/Hugo |
| **P3** | LTI (intégration LMS) | LTI 1.3 (launch Hugo depuis LMS) | 5–8j | UX seamless, contexte apprenant |

**Total POST-POC intégrations** : 25–35 jours (4–5 semaines sprint).

### 21.4 Architecture d'intégration cible

```
Écosystème OF/Entreprise
├── ERP OF (Digiforma)
├── LMS (360Learn)
└── SIRH (Workday)
     ↕ CSV/API  ↕ xAPI/LTI  ↕ CSV/API
     (apprenants, progression, compétences, groupes)
              ↓
┌─────────────────────────────────┐
│ Hugo — Plateforme FamilleIA     │
│ - Multi-tenant (RLS)            │
│ - Hugo AFEST réflexif           │
│   (traces + preuves)            │
│ - RAG bibliothèque classe       │
│ - Exports CSV/JSON + PDF (opt.) │
│ - POST-POC : SSO (OIDC/SAML)    │
│   provisioning SCIM             │
└─────────────────────────────────┘
```


### 21.5 Standards e-learning (LMS)

#### xAPI (Experience API)

Hugo peut émettre **statements xAPI** vers LRS (Learning Record Store) pour tracer progression.

**Exemple statement** :

```json
{
  "actor": {"mbox": "mailto:apprenant@example.com"},
  "verb": {"id": "http://adlnet.gov/expapi/verbs/completed"},
  "object": {
    "id": "https://hugo.example.com/traces/{trace_id}",
    "definition": {"name": {"fr": "Trace AFEST - Compétence X"}}
  },
  "result": {"completion": true, "success": true},
  "context": {"extensions": {"referential_item_id": "uuid"}}
}
```


#### LTI (Learning Tools Interoperability)

Permet **lancer Hugo depuis LMS** (Moodle, 360Learning) avec SSO et contexte (groupe, apprenant).

**Effort POST-POC** :

- xAPI (statements traces → LRS) : 5–8j
- LTI 1.3 (provider) : 5–8j


### 21.6 SSO \& provisioning (SIRH/IT)

#### SSO (Single Sign-On)

- **OIDC** (OpenID Connect) : standard moderne, intégration Keycloak/Auth0/Entra ID
- **SAML 2.0** : standard legacy, grands groupes


#### Provisioning SCIM 2.0

Synchronisation automatique utilisateurs/groupes depuis SIRH/annuaire :

- Création/mise à jour/désactivation comptes
- Attribution rôles (`LEARNER`, `TUTOR`, `TRAINER`)
- Création groupes/classes

**Effort POST-POC** :

- OIDC : 3–5j (librairie FastAPI OAuth2)
- SAML 2.0 : 5j (`python3-saml`)
- SCIM 2.0 : 5j (endpoints `/scim/v2/Users`, `/scim/v2/Groups`)


### 21.7 Impact sur modèle de données (POST-POC)

**Tables ajouter** :

```sql
-- Mapping référentiels (harmonisation RNCP/RS ↔ LMS/SIRH)
CREATE TABLE referential_mapping (
  id UUID PRIMARY KEY,
  organisation_id UUID NOT NULL,
  source_system TEXT NOT NULL, -- 'HUGO', 'LMS', 'SIRH', 'ERP'
  source_ref TEXT NOT NULL,
  target_referential_id UUID REFERENCES referential(id),
  target_item_id UUID REFERENCES referential_item(id),
  mapping_rules JSONB, -- règles transformation
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Templates d'export configurables (enrichi POC)
CREATE TABLE export_template (
  id UUID PRIMARY KEY,
  organisation_id UUID NOT NULL,
  name TEXT NOT NULL,
  target_system TEXT, -- 'SIRH', 'ERP', 'LMS', 'QUALIOPI'
  format TEXT NOT NULL, -- 'CSV', 'JSON', 'XML', 'PDF'
  column_mapping JSONB, -- {"apprenant_nom": "user.last_name", ...}
  separator TEXT DEFAULT ';',
  encoding TEXT DEFAULT 'UTF-8',
  include_bom BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Provisioning externe (SCIM)
CREATE TABLE external_identity (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES user(id),
  external_system TEXT NOT NULL, -- 'AZURE_AD', 'OKTA', 'LDAP'
  external_id TEXT NOT NULL, -- ID utilisateur dans système externe
  sync_status TEXT DEFAULT 'ACTIVE', -- 'ACTIVE', 'SUSPENDED', 'DELETED'
  last_sync_at TIMESTAMPTZ,
  UNIQUE(external_system, external_id)
);
```


### 21.8 Checklist intégration (avant déploiement client)

- [ ] Export CSV configurable (séparateur, colonnes, encodage)
- [ ] SSO OIDC configuré (IdP client)
- [ ] Import CSV apprenants/groupes (test)
- [ ] Mapping référentiels client (RNCP/RS → nomenclature interne)
- [ ] Tests cross-tenant (isolement SI multi-filiales)
- [ ] Politique rétention données validée (RGPD client)
- [ ] Documentation API synchronisation (si SIRH/LMS existant)
- [ ] Webhooks progression configurés (si LMS/SIRH attend notifications)

***

## 22. Changelog

### v1.4 (clarifiée) — 17 février 2026

**Changements majeurs** :

- **Section 1.2.1** : ajout principe "POC manuel → POST-POC assisté" (Julia/Felix hors scope POC initial)
- **Section 9.4** : Julia V1 (import référentiels + normalisation + questionnement overlay + mapping) vs V2+ (fonctions avancées, nécessite GPU)
- **Section 12.3** : Felix V1 (guidage Qualiopi + planification exports, interface wizard/checklist) vs V2+ (automatisation avancée)
- **Section 19.4** : clarification pack audit Qualiopi POC lite (ZIP minimal exploitable) vs POST-POC complet (32 indicateurs + modules)
- **Architecture évolutivité GPU** : note design sections 9.4, 12.3 → approche objet-centric (endpoints référentiels/exports/quality restent stables), Julia/Felix = couches assistance progressives
- **Principe intégration** : Hugo = module AFEST intégrable (section 21.3), API externes consommables à terme (1–2 ans), compatibilité préservée

**Clarifications** :

- Rôles Julia/Felix explicites (V1 CPU-compatible, V2+ GPU-optimisé)
- Interface Felix : wizard/checklist (déterministe, auditabilité Qualiopi) + mini-chat optionnel
- Templates export et planification/relances en POST-POC (section 12.3)
- Approche objet métier (pas d'endpoints agents dédiés avant stabilisation besoins externes)


### v1.3 (révisée) — 17 février 2026

**Améliorations structurelles** :

- Ajout section 1 "Vision produit" (tableau synthétique assistants + statut POC vs POST-POC, impact SI)
- Ajout section 3 "Doctrine technique" (consolidation principes non-négociables : RLS, confidentialité, CPU-only, best effort)
- Réorganisation personas (séparation claire vision métier ↔ endpoints API)
- Harmonisation références sections (numérotation cohérente)
- Clarification priorités POST-POC (synthèse P0/P1/P2/P3 pour Qualiopi et intégrations)
- Consolidation schémas JSON (regroupement annexes)

**Pas de perte d'information** : tout le contenu v1.3 d'origine conservé, restructuré pour meilleure lisibilité.

### v1.3 (originale) — 17 février 2026

- Harmonisation nommage (`SPEC_POC_v1.3` + en-têtes SoT)
- Performance : latence cible 3 s, pointes jusqu'à 15 s acceptables en POC
- Exports : CSV (séparateur `;` par défaut, UTF-8 BOM par défaut) configurable via paramètres d'export
- Qualiopi : pack audit lite **IN POC** (pack complet POST-POC)
- Référentiels : 2 RNCP + 2 RS (pour 2 démos / 2 formations)

***

**FIN SPEC_POC_v1.4**

