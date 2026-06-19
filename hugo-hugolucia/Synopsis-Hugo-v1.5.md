# Hugo, Julia, Felix et Hector — Synopsis v1.5

**Document de communication** — orienté développeur·e sénior  
**Version** : 1.5  
**Date** : 26 février 2026  
**Source de vérité (SoT)** : `SPEC_POC_v1.5.md`

> En cas de divergence, la **source de vérité** est `SPEC_POC_v1.5.md`.
> Le POC livré en mars 2026 reste **centré sur Hugo** (AFEST, RAG bibliothèque de classe, exports Felix-ready). La v1.5 introduit des éléments de **design POST-POC** pour Julia, Felix, Hector et Jérémy (planning séances/ressources).
---

## 1. Vue d'ensemble produit

On construit une **plateforme multi-tenant** (plusieurs OF dans une même instance) qui regroupe plusieurs assistants sous une marque commune (ex. FamilleIA / CompagnIA).

| **Assistant** | **Rôle métier** | **Statut POC** |
|--------------|----------------|---------------|
| **Hugo** | Assistant réflexif AFEST centré apprenant : 1 question à la fois, relances métier situées via RAG + référentiel RNCP/RS + historique structuré. | **IN POC** |
| **Julia** | Gestion avancée des classes/cohortes, variantes référentielles, parcours partiels, analytics. | POST-POC |
| **Felix** | Exports financeurs / Qualiopi / suivi + API d'export. POC : exports Felix-ready (CSV/JSON) sans bot. | Exports IN POC, bot POST-POC |
| **Hector** | Assistant ressources/cours (support documentaire sur la bibliothèque). | POST-POC |
| **Jérémy** | Assistant de planification séances/ressources sous contraintes (cohortes, sites, formateurs, salles), propositions de planning et réparations, validation humaine obligatoire, audit complet (snapshots immuables). | POST-POC |

**Applis externes** :
- **inSitu** : hors POC, mais payload `trace_rich_v1` conservé, export JSON pour branchement ultérieur.
- **LMS / SIRH** : intégrations prévues post-POC (SSO, SCIM, xAPI, LTI), décrites dans la SPEC.

---

## 2. Objectif POC (cible : 20 mars 2026)

Livrer un **POC bêta CPU-only** avec :

### 2.1 Contrainte infra

- Pas d'OpenAI : **Mistral 7B self-hosted** (Ollama ou llama.cpp), CPU-only.
- **1 VM** docker-compose (nginx, web, api, postgres RLS + pgvector, minio, llm, worker async).
- Latence cible **3 s**, pointes acceptables jusqu'à **15 s**.
- Accès public, protégé par HTTPS + **HTTP Basic Nginx** + rate limiting.

### 2.2 Fonctionnel POC

- **Hugo** : chat AFEST + historique apprenant + génération de trace structurée (`trace_rich_v1`).
- Partage **confidentialité-first** : `share_summary=false`, `share_evidence=false`, `share_verbatim=false` par défaut.
- Bibliothèque de **classe** uniquement (docs `ACTIVE`) pour le RAG.
- Import manuel de référentiels RNCP/RS via `referential_import_v2` (items + critères d'évaluation + modalités + preuves attendues) + **overlay par classe**.
- Preuves photo smartphone : resize + thumbnail, **EXIF supprimé**, **GPS opt-in** individuel.
- Dashboard classe minimal : classe → apprenant → timeline → compétences.
- Exports : **CSV principal** (Felix-ready, 1 ligne = trace × item) + **JSON** (`trace_rich_v1`).
- Qualiopi : **pack audit "lite" IN POC** (ZIP minimal exploitable) ; pack complet RNQ (32 indicateurs) post-POC.

---

## 3. Doctrine technique (non-négociables)

### 3.1 Multi-tenant & RLS Postgres

- `organisation_id` sur toutes les tables métier.
- À chaque requête : `SET LOCAL app.organisation_id = :org_id` (clé PostgreSQL avec underscore).
- RLS policies (pattern "safe") :
  ```sql
  organisation_id = current_setting('app.organisation_id', true)::uuid
  ```
- Tests d'acceptation obligatoires : **cross-tenant** (org A ne lit/écrit jamais org B).

### 3.2 Confidentialité-first & partage

- Verbatim **privé par défaut** : TUTOR / TRAINER / COORDO ne voient que ce qui est explicitement partagé.
- Partage segmenté (synthèse / preuves / verbatim) via flags `share_*`.
- Logs applicatifs : aucune donnée de verbatim (seulement IDs, timestamps, statuts, erreurs).

### 3.3 CPU-only & embeddings

- Inference LLM : **Mistral 7B quantisé CPU** (Ollama ou llama.cpp), ou API OVH AI Endpoints.
- Embeddings : modèle **Sentence-Transformers static-similarity-mrl-multilingual-v1**, local CPU, dim=512 (config 256/512), stockés dans pgvector.

---

## 4. Hugo : historique, RAG, référentiels

### 4.1 Historique & LearnerState

**Niveau A (POC)** : Hugo ne voit que l'historique **structuré**, pas le verbatim brut.

- **Source** : dernières traces validées (ou dernières traces tout court), couverture d'items, niveaux par item, critères couverts/manquants, plans d'action, présence de preuves.

- **`learner_state`** = cache recalculé à chaque validation de trace :
  1. `skills_matrix` (dernier niveau + date par item)
  2. `missing_coverage_item_ids`
  3. `open_action_items`
  4. résumé court (≤ 25 lignes)

- **Préparation niveau B** : endpoint interne `internal/learners/{id}/verbatim-window` (désactivé en prod POC), RBAC + respect des règles de partage.

### 4.2 RAG (bibliothèque de classe)

Pipeline RAG "question-driven" sur la bibliothèque de **classe**, avec quelques choix importants pour la réutilisation :

**Scope RAG**
1. POC Hugo : uniquement les documents `ACTIVE` liés à la **classe** (`group_document` sur le groupe de classe).
2. Bibliothèque personnelle formateur stockée mais non utilisée au POC (seule la bibliothèque de classe compte).
3. POST-POC (Jérémy) : la bibliothèque « effective » d’une cohorte est définie, côté SPEC, comme la réunion des docs `ACTIVE` du groupe parent (site/programme) et du groupe cohorte, avec une règle d’override cohorte basée sur (`purpose`, `key`) sur `group_document` (détail dans SPEC_POC_v1.5, section 10.4).

**Indexation docs**
- **Extraction** best-effort (PDF texte OK, PDF scanné sans OCR → statut `LOW_TEXT`).
- **Chunking différencié** :
  1. **Cours** : chunks longs (~1200 tokens, overlap ~150).
  2. **Procédures / sécurité** : chunks courts (~350 tokens, overlap ~50), en conservant la structure par étapes.
- **Embeddings** : modèle statique multi-lingue (cf. 3.3), stockage dans `document_chunk.embedding` (pgvector) + meta (page/slide).

**Retrieval & guardrails "anti-absurde"**
1. Filtre par classe + statut `ACTIVE`.
2. **Préférence forte** pour les docs taggés `procedure`, `checklist`, `securite`, `qualite` si la question contient des signaux de risque.
3. `top_k ~ 20`, rerank lexical léger, injection de 1-3 chunks dans le prompt.
4. **Traçabilité** via `rag_citation` (doc, chunk, score, meta).
5. **Test** : **≥ 8/10** requêtes "procédure" doivent remonter au moins un chunk de procédure/sécurité dans le top-5.

### 4.3 Référentiels RNCP/RS & overlay

**Import manuel via `referential_import_v2` (JSON)**
1. Items hiérarchisés (code, label, description, parent).
2. `evaluation_criteria`, `evaluation_modalities`, `expected_evidence` (types `PHOTO`/`DOC`/`OBS` + hints).
3. `source_ref` optionnel (RNCPxxxx, RSyyyy...).

**Overlay par classe (`referential_item_overlay`)**
1. enabled/disabled par item
2. exemples de situations
3. exemples de preuves
4. erreurs fréquentes
5. questions de relance coach
6. docs de classe liés
7. Échelle par défaut "apprécie / participe / réalise / maîtrise" (modifiable par classe).

---

## 5. Exports, Qualiopi & tests d'acceptation

### 5.1 Exports (Felix-ready)

**JSON** : téléchargement du `trace.payload_structured` (schéma `trace_rich_v1`, stable pour intégrations futures).

**CSV** :
1. 1 ligne = (trace × item référentiel)
2. séparateur `;` (Excel FR)
3. encodage UTF-8 avec BOM (configurable)
4. dates ISO, prêt pour ingestion par Felix / Excel / SIRH.

### 5.2 Qualiopi (AFEST) — POC

**POC** : **pack audit lite** générable (ZIP) avec :
1. exports CSV/JSON des traces, validations, preuves sur une période
2. `audit_log` filtré (validations, partages, exports)
3. référentiels + overlays actifs
4. liste des docs `ACTIVE` utilisés en RAG

**POST-POC** : cartographie complète des 32 indicateurs RNQ, module réclamations, enquêtes satisfaction, livret apprenant PDF.

### 5.3 Tests d'acceptation minimaux

1. **Multi-tenant** : RLS cross-tenant (org A ne lit/écrit jamais org B).
2. **Partage** : tuteur / formateur ne voient rien sans partage explicite.
3. **Hugo** : 1 question max par message ; trace générée ; validation ; exports JSON/CSV OK.
4. **RAG anti-absurde procédures** : ≥ 8/10 requêtes "procédure" → chunk de procédure/sécurité dans le top-5.
5. **Indexation** : PDF scanné sans OCR flaggé `LOW_TEXT`.
6. **Historique apprenant** : accessible et filtrable (dates, compétences).

---

## 6. Stack technique

| **Service** | **Rôle** | **Tech** |
|------------|---------|---------|
| `nginx` | TLS, HTTP Basic gate, rate limit, upload limits, headers | Nginx |
| web | Frontend webapp responsive + PWA | Next.js + TypeScript |
| `api` | FastAPI monolithe modulaire | FastAPI + SQLAlchemy 2.0 Async + Alembic |
| `postgres` | RLS + pgvector | PostgreSQL 15+ |
| `minio` | Uploads + exports | MinIO S3-compatible |
| `llm` | Inference CPU | Mistral 7B quantisé (Ollama ou llama.cpp) |
| `worker` | Tâches async (indexation, exports, recalcul `learner_state`) | Worker async Python |

---

## 7. Rôles & visibilité

| **Rôle** | **Accès** |
|---------|----------|
| **Apprenant** | Accès complet à son historique (verbatim + traces + preuves) |
| **Tuteur/Formateur/Coordo** | Accès uniquement aux éléments **partagés** par l'apprenant (synthèse / preuves / verbatim selon flags) |

**Verbatim privé par défaut** : partage explicite séparé.

---

## 8. Plan d'exécution (3 semaines)

| **Semaine** | **Slices** | **Livrables** |
|------------|-----------|-------------|
| **Semaine 1** | S0 infra + gate, S1 DB + RLS + Auth, S2 classes + liens | Infra + RLS + auth + groupes + tuteurs |
| **Semaine 2** | S3 Hugo chat, S4 trace + partage + validation, S6 référentiels | Hugo fonctionnel + traces + `learner_state` |
| **Semaine 3** | S5 preuves photo, S7 RAG complet, S8 exports + dashboard | RAG + preuves + exports + dashboard |

**Priorité P1 (si marge)** : situations templates (`situation_template`)

---

## 9. Où trouver le détail

1. **`SPEC_POC_v1.5.md`** : spécification technique complète (source de vérité)
2. **`.cursorrules`** + **`docs/*`** : règles d'implémentation dans le repo
3. **`prompts/*`** : prompt Hugo (SoT du comportement conversationnel)
4. **Section 18 SPEC** : schémas JSON complets (`referential_import_v2`, `trace_rich_v1`, `referential_item_overlay`)
5. **Section 19 SPEC** : conformité Qualiopi RNQ (cartographie 32 indicateurs, pack audit POC lite + design complet)
6. **Section 20 SPEC** : personas & cas d'usage métier détaillés (8 personas)
7. **Section 21 SPEC** : intégrations LMS/SIRH, effets de bord, stratégie post-POC (incluant Jérémy côté planning)

---

## Changelog

### v1.5 — 26 février 2026

- Alignement sur `SPEC_POC_v1.5.md` (SoT mise à jour, références sections 18–21).
- Ajout de Jérémy dans la vue d’ensemble produit (assistant planning POST-POC, pas dans le POC).
- Précision sur la bibliothèque : POC Hugo = bibliothèque de classe, design POST-POC Jérémy = bibliothèque effective parent+cohorte (règle `purpose`/`key` détaillée dans SPEC).
- Clarification du scope : POC toujours centré sur Hugo (AFEST, RAG, exports Felix-ready), les autres assistants restent au stade design.

### v1.4 — 19 février 2026

- **Alignement SPEC v1.4** : références mises à jour (sections 3, 13, 18-21).
- **Vocabulaire** : "confidentialité-first" (au lieu de "privacy-first"), `SUPERADMIN` (sans underscore).
- **RLS** : clé Postgres normalisée `app.organisation_id` (avec underscore).
- **Partage par défaut** : tous flags `share_*` à `false`, opt-in guidé explicite.
- **Bibliothèque RAG** : précisions chunking différencié, test anti-absurde procédures (≥ 8/10).
- **Qualiopi** : pack audit "lite" IN POC, pack complet RNQ POST-POC.

---

**FIN DU DOCUMENT — Synopsis Hugo v1.5**
