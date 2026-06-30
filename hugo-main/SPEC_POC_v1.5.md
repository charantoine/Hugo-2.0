# SPEC_POC_v1.5 (patch Hugo 1.6.2) — Plateforme multi-tenant "FamilleIA/CompagnIA" (POC centré Hugo)

**Date cible : 20 mars 2026**
**Contrainte : CPU-only ou OVH AI Endpoints** (pas de GPU dédié dans le POC). **Latence cible : 3 s**. **Latence occasionnelle acceptable en POC : jusqu'à 15 s** (usage ponctuel).
**Principe : confidentialité-first**, pas d'OpenAI, **Mistral self-hosted ou OVH AI Endpoints** dans un cadre RGPD acceptable.
**Version : 1.5 patchée (alignement Django + TutorPrompt + Hugo 1.6.2, recentrée POC Hugo)** — réalignement backend existant et orchestration conversationnelle pilotée par état.

***

## Sources de vérité (SoT) — Hiérarchie stricte

1. **Ce fichier `SPEC_POC_v1.5.md` patché** = périmètre produit/technique POC (source unique).
2. **Règles Cursor + docs d'implémentation + tests** (`.cursorrules`, `docs/*`, `tests/*`) = dérivés de la SPEC, committés dans le repo.
3. **Contrats backend d’orchestration** (services Django) = implémentation de référence du runtime conversationnel.
4. **`TutorPrompt` + fichiers `prompts/` éventuels** = templates et profils de rendu du tuteur, pas unique source de stratégie conversationnelle.
5. **Document `.docx`** = synopsis communication (non-SoT) ; en cas de conflit, `.md` prime.

**Important** : toute modification de SPEC nécessite la mise à jour des fichiers dérivés et des tests associés. La hiérarchie opérationnelle est : **SPEC > `.cursorrules` > docs/tests > services backend > templates `TutorPrompt`**.

**Scope v1.5** : le POC livré en mars 2026 est **strictement centré sur Hugo** : AFEST, RAG bibliothèque de classe, traces structurées, preuves photo, exports et pack Qualiopi lite.  
Aucune projection normative vers d'autres assistants ou développements post-POC n'est incluse dans cette version patchée.

***

## Conventions de nommage

- **API \& DB** : `snake_case` (ex. `payload_structured`, `share_summary`, `organisation_id`).
- **Contexte tenant (RLS)** : clé PostgreSQL **unique** `app.organisation_id` fixée via `SET LOCAL`.
- **Exports** : CSV = livrable métier POC ; JSON = export technique du payload `trace_rich_v1` (interop/branchages).

***

## Table des matières

1. [Vision produit : architecture \& assistants](#1-vision-produit--architecture--assistants)
2. [Objectif POC](#2-objectif-poc)
3. [Doctrine technique (RLS, confidentialite, CPU-only ou OVH AI Endpoints)](#3-doctrine-technique-rls-confidentialite-cpu-only-ou-ovh-ai-endpoints)
4. [Arbitrages validés](#4-arbitrages-valid%C3%A9s)
5. [Architecture technique](#5-architecture-technique)
6. [Rôles et visibilité](#6-r%C3%B4les-et-visibilit%C3%A9)
7. [Hugo : comportement et contexte](#7-hugo--comportement-et-contexte)
8. [Historique : niveau A (POC)](#8-historique--niveau-a-poc)
9. [Référentiels RNCP/RS : import v2 + overlay](#9-r%C3%A9f%C3%A9rentiels-rncprs--import-v2--overlay)
10. [Bibliothèque de classe : RAG question-driven](#10-biblioth%C3%A8que-de-classe--rag-question-driven)
11. [Preuves photo : GPS opt-in](#11-preuves-photo--gps-opt-in)
12. [Exports POC](#12-exports-poc)
13. [Multi-tenant : RLS Postgres](#13-multi-tenant--rls-postgres)
14. [Modèle de données : tables MVP](#14-mod%C3%A8le-de-donn%C3%A9es--tables-mvp)
15. [API endpoints MVP](#15-api-endpoints-mvp)
16. [Tests d'acceptation minimaux](#16-tests-dacceptation-minimaux)
17. [Plan d'exécution : chemin critique](#17-plan-dex%C3%A9cution--chemin-critique)
18. [Annexes : schémas JSON](#18-annexes--sch%C3%A9mas-json)
19. [Conformité Qualiopi (RNQ)](#19-conformit%C3%A9-qualiopi-rnq)
20. [Personas \& cas d'usage métier](#20-personas--cas-dusage-m%C3%A9tier)
21. [Intégrations et effets de bord (POC)](#21-intégrations-et-effets-de-bord-poc)
22. [Changelog](#22-changelog)

***

## 1. Vision produit : architecture \& assistants

### 1.1 Plateforme multi-tenant

On construit une **plateforme multi-tenant** (plusieurs OF dans la même instance) regroupant plusieurs assistants sous une marque commune (ex. "CompagnIA", "FamilleIA").

### 1.2 Hugo dans le POC

Le périmètre de cette SPEC est **Hugo uniquement**.

Hugo est l'assistant réflexif AFEST centré apprenant. Il conduit l'entretien, s'appuie sur le référentiel et la bibliothèque de classe, produit des traces structurées, gère les preuves photo et prépare les exports du POC.

Les autres assistants éventuellement envisagés dans la vision produit globale ne font **pas** partie de cette SPEC patchée et ne doivent pas orienter l'implémentation du POC.

### 1.3 Applications externes

- **inSitu** : Hors POC (connexion retirée), mais `payload_trace_rich_v1` conservé, export JSON pour branchement ultérieur.
- **LMS/SIRH** : Intégrations planifiées (voir section 21).

***

## 2. Objectif POC

Livrer un **POC bêta CPU-only ou OVH AI Endpoints** (cible 20 mars 2026) avec :

### Périmètre fonctionnel

- **Multi-OF cloisonné** : multi-tenant RLS Postgres (obligatoire)
- **Hugo** : chat + historique apprenant + trace structurée
- **RAG question-driven** sur bibliothèque de classe (docs `ACTIVE`)
- **Référentiel RNCP/RS** : import manuel incluant critères d'évaluation
- **Preuves photo** smartphone (EXIF supprimés par défaut, GPS opt-in individuel)
- **Vue suivi classe** minimaliste (classe/apprenant/temps/compétences)
- **Exports** : `trace_rich_v1.json` + CSV POC optimisé reporting
- **Qualiopi** : pack audit lite **IN POC** (ZIP minimal exploitable)

### Hors périmètre POC

- Livret texte/PDF (optionnel si marge)
- Automatisations avancées non nécessaires au POC
- Intégrations SSO, SCIM, xAPI, LTI
- Assistants autres qu'Hugo

***

## 3. Doctrine technique (RLS, confidentialite, CPU-only ou OVH AI Endpoints)

Ces principes sont **non-négociables** et structurent toute l'architecture.

### 3.1 Confidentialité-first

- **Verbatim privé par défaut** (partage explicite distinct : synthèse ≠ preuves ≠ verbatim).
- **Partage par défaut** : `share_summary=false`, `share_evidence=false`, `share_verbatim=false`.
- **Workflow guidé POC** : message apprenant au moment validation : _"Votre tuteur a besoin de la synthèse, partagez-vous ?"_.
- **En phase de développement / sandbox**, l’enregistrement des appels LLM, prompts rendus, payloads fournisseur et réponses brutes est **autorisé** pour faciliter le débogage, les relectures de tours et les tests de non-régression.
- Ces journaux techniques restent **scopés au tenant**, non exposés aux rôles métier standard, et distincts des artefacts explicitement partagés avec les tuteurs/formateurs.
- **La politique de rétention et de purge production** est laissée ouverte à ce stade ; elle n’est pas bloquante pour le POC tant que le besoin principal est le débogage du moteur conversationnel.

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

### 3.3 CPU-only ou OVH AI Endpoints

- **Inference LLM** : Mistral 7B quantisé (Ollama ou llama.cpp), ou OVH AI Endpoints **pas d'OpenAI**
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
- **Sous-groupes imbriqués** : hors périmètre du POC Hugo ; `parent_group_id` peut exister dans le modèle sans devenir structurant dans cette version.
- **Vector store** : Postgres `pgvector` (migration Qdrant anticipée via interface)
- **Exports** : CSV = principal ; JSON = `trace_rich_v1`
- API orientée objets métier ; aucun endpoint dédié à d'autres assistants n'est requis dans le POC Hugo.

### UI-FRONT-01 Webapp unique responsive (POC)

Décision
- Le POC est livré sous forme de webapp unique (même URL, même base front), responsive, couvrant les rôles POC.
- L’expérience est mobile-first pour LEARNER (terrain, smartphone, preuves photo, chat) et desktop-first pour TUTOR/TRAINER/COORDO/ORGADMIN (dashboard, référentiels, bibliothèque, exports).
- La webapp est installable en PWA sur smartphone (icône écran d’accueil), sans promesse de mode hors ligne.

Hors périmètre POC
- Mode hors ligne fonctionnel (les appels API nécessitent du réseau).

***

## 5. Architecture technique

### 5.1 Services (docker-compose)

| Service | Rôle | Tech |
| :-- | :-- | :-- |
| **nginx** | TLS, HTTP Basic (gate), reverse proxy, rate limit, upload limits, headers | Nginx |
| **web** | Frontend webapp responsive + PWA | Next.js + TypeScript |
| **api** | Backend monolithique modulaire | **Django + Django REST Framework** |
| **postgres** | RLS + pgvector | PostgreSQL 15+ |
| **minio** | Uploads + exports | MinIO (S3-compatible) |
| **llm** | Inference CPU / remote | Mistral via Ollama / llama.cpp ou OVH AI Endpoints |
| **worker** | Tâches async (indexation, exports, recalcul `learner_state`) | Worker Python / Celery léger |

### 5.2 Stack technique (fix)

- **Backend** : Django
- **API** : Django REST Framework
- **ORM** : Django ORM
- **Migrations** : migrations Django
- **Auth** : JWT
- **DB** : PostgreSQL (RLS + `pgvector`)
- **Storage** : MinIO (S3-compatible)
- **Reverse proxy** : Nginx (TLS, HTTP Basic, rate limit)
- **Background jobs** : worker Python simple / Celery léger (pas de Kubernetes, pas de Kafka)

### 5.3 Conséquence d’architecture pour Hugo

Le backend réel du POC n’est plus à concevoir comme un simple prompt builder branché sur un endpoint LLM. Il doit être compris comme un **runtime conversationnel orchestré** dans Django :

- sélection du contexte et du `TutorPrompt` effectif ;
- calcul d’un plan pédagogique local ;
- décision de phase / décision tutorale ;
- rendu des templates système/utilisateur ;
- appel LLM ;
- garde-fous de sortie, journalisation technique et génération de traces.

La suite du développement doit donc **étendre l’orchestrateur existant** plutôt que réintroduire une architecture parallèle `FastAPI + hugo_config`.

## 6. Rôles et visibilité

`LEARNER`, `TUTOR`, `TRAINER`, `COORDO`, `ORGADMIN`, `SUPERADMIN`

Persona Qualité : compte ORGADMIN.

### 6.2 Visibilité — règles strictes

- **LEARNER** : accès complet à son historique (verbatim + traces + preuves).
- **TUTOR / TRAINER / COORDO** : accès uniquement à ce que l’apprenant a partagé (synthèse / preuves / verbatim selon flags).
- **ORGADMIN (Qualité)** : mêmes règles de confidentialité sur contenu apprenant (ne voit que le partagé), mais peut administrer (users, groupes) et déclencher exports / pack Qualiopi.
- **SUPERADMIN** : administration technique globale (à cadrer), doit respecter l’isolation multi-tenant et éviter toute lecture applicative du contenu apprenant.
**Verbatim privé par défaut** (partage explicite séparé).

***

## 7. Hugo : comportement et contexte

### 7.1 Source de vérité conversationnelle

Le comportement d’Hugo n’est plus défini par le **prompt seul**.

Le comportement conversationnel résulte de la combinaison suivante :

1. **SPEC** : invariants produit/AFEST/confidentialité.
2. **Moteur d’orchestration backend** : logique qui choisit le focus du tour, la phase, le nombre de questions, et les éventuels garde-fous.
3. **`TutorPrompt`** : templates et paramètres de rendu du tour, configurables par organisation/groupe/session.
4. **RAG / overlay référentiel / learner_state** : renforts contextuels utilisés à bon escient, jamais comme pilote principal du dialogue.

En conséquence, le prompt AFEST reste un artefact important, mais **n’est plus la seule source de stratégie conversationnelle**.

### 7.2 Runtime conversationnel cible (aligné avec le backend existant)

Le runtime Hugo est conçu autour d’un orchestrateur de tour, branché aujourd’hui sur les services Django existants et étendu par Hugo 1.6.2.

Pipeline cible :

1. **Construction de contexte**
   - récupération de la session, du groupe, du référentiel, des traces récentes, du `learner_state`, de la bibliothèque documentaire et du `TutorPrompt` effectif ;
2. **Analyse du tour apprenant**
   - calcul d’un état borné P0/P1 à partir du dernier message apprenant et du contexte utile ;
3. **Décision tutorale locale**
   - choix du geste prioritaire, du mode de réponse, du nombre de questions et des usages autorisés (micro-explication, mémoire thématique, RAG, etc.) ;
4. **Rendu du prompt**
   - génération des prompts système/utilisateur à partir de `TutorPrompt` et du contrat d’orchestration ;
5. **Appel LLM**
   - modèle local ou OVH selon configuration du groupe / du `TutorPrompt` ;
6. **Post-traitement**
   - garde-fous de sortie, journalisation technique, mise à jour de phase et persistance des artefacts du tour.

Le backend existant matérialise déjà une grande partie de cette chaîne via des services tels que :

- `build_hugo_turn()`
- `build_hugo_context()`
- `build_teaching_plan()`
- `decide_next_phase()`
- `render_with_tutor_prompt()`

Le lot Hugo 1.6.2 ajoute au milieu de cette chaîne un **analyseur P0** et un **moteur de décision déterministe**, sans casser `TutorPrompt`.

### 7.3 Invariants conversationnels

Les invariants suivants s’appliquent à Hugo :

- posture **AFEST réflexive** ;
- Hugo n’est **ni un évaluateur autonome**, ni un enseignant magistral, ni un agent de validation ;
- **1 objectif de régulation par message** ;
- **1 question simple par défaut dans le POC**, afin de garder la réponse lisible et robuste ;
- possibilité de **2 questions brèves maximum** seulement si elles servent le **même micro-objectif** et que le mode de sortie configuré l’autorise ;
- fallback automatique vers **une seule question simple** si la charge cognitive ou le risque interactionnel sont élevés ;
- pas de boucle de relance sur un critère déjà couvert sans ambiguïté explicite ;
- pas de cours magistral, pas de liste de conseils détaillés, pas de jugement ;
- micro-explication éventuellement autorisée, mais seulement de manière brève et contrôlée.

### 7.4 RAG et référentiel : rôle situé

- Le référentiel sert à **orienter la couverture**, la focalisation pédagogique et la structuration des traces.
- Le RAG documentaire reste **question-driven** et **situé** : il soutient un tour lorsque cela aide à clarifier, comparer, documenter ou rappeler un point concret.
- Le RAG ne doit jamais devenir la mémoire principale de l’apprenant ni détourner Hugo vers une logique de cours.
- Les overlays référentiels de groupe et l’état de couverture des critères doivent être utilisés pour **éviter les redondances** et réduire les boucles de questionnement.

### 7.5 `TutorPrompt` = configuration dynamique du tuteur

La notion centrale de configuration n’est plus `hugo_config`, mais **`TutorPrompt`**, résolu dynamiquement selon la priorité suivante :

1. `HugoSession.tutor_prompt`
2. `Group.default_tutor_prompt`
3. prompt par défaut de l’organisation
4. fallback legacy si aucun prompt n’est configuré

`TutorPrompt` porte à la fois :

- des **templates** (`system_template`, `user_template`) ;
- des **métadonnées de profil** (`code`, `name`, `description`, `prompt_type`, `sot_profile`) ;
- des **paramètres de sortie** (`output_format_mode`, `max_questions_per_turn`, `max_tokens`, `allow_lists`) ;
- des **préférences de forme** (`language`, `tone`) ;
- des **liaisons d’inférence** (`ovh_llm` éventuel) ;
- des **métadonnées d’extension** (`metadata`).

Les niveaux de réglage complémentaires déjà présents dans le backend doivent être conservés :

- `HugoSession.current_phase`
- `HugoSession.manual_phase_override`
- `HugoSession.phase_classifier_*`
- `Group.phase_classifier_*`
- `Group.llm_backend`

### 7.6 Noyau d’état prioritaire Hugo 1.6.2 (P0)

Le moteur conversationnel doit désormais raisonner à partir d’un **noyau P0 de 16 variables bornées** :

#### Bloc situation / épisode
- `episode_clarity` ∈ {`low`, `medium`, `high`}
- `has_concrete_actions` ∈ {`true`, `false`}
- `problem_salience` ∈ {`none`, `low`, `high`}

#### Bloc métacognitif / réflexif
- `reflection_phase` ∈ {`description`, `analysis`, `projection`}
- `reflective_depth` ∈ {`low`, `medium`, `high`}
- `self_efficacy_signal` ∈ {`low`, `neutral`, `high`}

#### Bloc socio-affectif / relationnel
- `affect_valence` ∈ {`negative`, `neutral`, `positive`}
- `cognitive_load` ∈ {`low`, `medium`, `high`}
- `interaction_risk` ∈ {`low`, `medium`, `high`}

#### Bloc épistémique / ZPD
- `epistemic_balance` ∈ {`tutor_more_expert`, `balanced`, `learner_more_expert`}
- `zpd_estimate` ∈ {`below`, `in`, `beyond`}

#### Bloc trajectoire de séance / parcours
- `session_phase` ∈ {`opening`, `exploration`, `deepening`, `potential_closure`}
- `session_maturity` ∈ {`low`, `medium`, `high`}
- `evidence_strength` ∈ {`low`, `medium`, `high`}

#### Bloc décision locale
- `intervention_necessity` ∈ {`none`, `low`, `high`}
- `contradiction_status` ∈ {`none`, `suspected`, `under_check`, `resolved`}

Les variables P1 peuvent continuer à être calculées ou loggées pour l’expérimentation, mais ne pilotent pas la décision tant qu’elles ne sont pas promues explicitement.

### 7.7 Politique de décision locale

À partir du P0, Hugo doit suivre la logique suivante :

1. **Clarification avant tout**
   - si `episode_clarity=low` → geste de clarification ;
   - si `has_concrete_actions=false` → faire décrire l’action réelle, pas analyser trop tôt.
2. **Problématisation minimale avant analyse**
   - si aucun problème n’émerge et que l’apprenant reste au stade descriptif, Hugo introduit une légère mise en tension ou une question de nud.
3. **Protection relationnelle et cognitive**
   - si `cognitive_load=high` ou `interaction_risk=high` → mode `singlequestion`, sans contrast fort ni micro-explication.
4. **Micro-explication contrôlée**
   - autorisée seulement si `zpd_estimate=in`, `reflective_depth ∈ {medium, high}` et `epistemic_balance != learner_more_expert` ;
   - dans ce cas : une phrase maximum.
5. **Contradiction**
   - si `contradiction_status=suspected` et que la scène est suffisamment claire, Hugo peut ouvrir une vérification douce.
6. **Bilan facultatif**
   - seulement si la séance est mûre, suffisamment étayée, et sans surcharge relationnelle/cognitive.

### 7.8 Sortie attendue du tour Hugo

Le moteur doit produire un contrat de décision explicite, au minimum :

- `primary_goal`
- `tutorial_move`
- `mode`
- `target_question_count`
- `questionbundling_allowed`
- `microexplain_allowed`
- `use_themememory`
- `use_verbatim_retrieval`
- `use_overlay_first`
- `use_rag`
- `optional_evaluation_eligible`
- `reason_codes`

Ce contrat est ensuite consommé par le rendu `TutorPrompt`.

### 7.9 Journalisation technique et debug

Dans cette version patchée, la SPEC **autorise explicitement** la conservation, en environnement de développement et de sandbox, des éléments suivants :

- prompt système rendu ;
- prompt utilisateur rendu ;
- charge utile envoyée au fournisseur LLM ;
- réponse brute du fournisseur ;
- métadonnées de décision (`phase_decision`, futur `decision_trace`, états P0/P1, etc.).

L’objectif est de faciliter :

- le débogage de l’orchestration ;
- la comparaison inter-prompts ;
- l’analyse des boucles de questionnement ;
- la validation des règles P0 ;
- les tests de régression.

### 7.10 Back-office / administration des prompts

Le back-office de gestion des prompts Hugo doit être réaligné sur `TutorPrompt` :

- catalogue des `TutorPrompt` d’une organisation ;
- CRUD contrôlé des prompts ;
- liaison éventuelle à un modèle OVH ;
- choix d’un prompt par défaut ;
- tests sandbox sur session Hugo existante ;
- versionning repo-first des templates importants.

Le périmètre client peut exposer la **sélection** d’un prompt actif selon les droits, mais la stratégie conversationnelle reste gouvernée par la SPEC et le runtime backend.

## 8. Historique : niveau A (POC)

### 8.1 Niveau A (POC) : traces structurées uniquement

Hugo utilise l'**historique** via **traces structurées**, pas de verbatim historique.

**LearnerState (cache)** : Créer table `learner_state` (recalculée chaque validation de trace)

- `skills_matrix` : `{item_id: {last_level, last_date, trend}}`
- `missing_coverage` : `[item_ids]`
- `open_action_items`
- `summary` (≤ 25 lignes)

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

## 10. Bibliothèque de classe : RAG question-driven

### 10.1 Deux bibliothèques distinctes (POC)

- **Bibliothèque personnelle formateur** : stockée, **non utilisée** par Hugo au POC.
- **Bibliothèque de classe** : docs `ACTIVE` liés au groupe de classe et utilisés par Hugo (RAG) **au POC**.

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

## 12. Exports POC

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

Core
- organisation, user, audit_log

Groupes & liens
- group, group_membership, tutor_learner_link
  - `group` (POC) : groupes de classe (cohortes simples, sans hiérarchie).
  - `group.default_tutor_prompt` : prompt Hugo par défaut pour le groupe.
  - `group.phase_classifier_*` : overrides runtime du classifieur de phase.

Hugo & traces
- `hugo_session`, `hugo_message`
- `trace`, `evidence`
- `learner_state`
- `tutor_prompt`
- `ovh_llm`
- `starter_prompt`

Documents & RAG
- `document`, `group_document`, `document_chunk`, `rag_citation`
  - `group_document` : lien document ↔ groupe, avec `status` (`ACTIVE`/`INACTIVE`) utilisé pour filtrer la bibliothèque.

Référentiels
- `referential`, `referential_item`, `scale`, `scale_level`, `referential_config`, `referential_item_overlay`

Cache & contrats d’état
- `learner_state`
- états P0/P1 et décision locale : **contrats logiques** du moteur 1.6.2 ; ils peuvent être stockés dans des champs JSON existants (`hugo_message`, `trace`, métadonnées de session) dans un premier lot, avant éventuelle extraction vers des tables dédiées.

Optionnel
- `situation_template` (P1 si marge)

#### Table `tutor_prompt`

Champs structurants attendus :

- `id` UUID PRIMARY KEY
- `organisation_id` UUID NOT NULL
- `prompt_type` TEXT NOT NULL (`AFEST_HUGO`)
- `code` TEXT NOT NULL
- `name` TEXT NOT NULL
- `description` TEXT NULL
- `system_template` TEXT NOT NULL
- `user_template` TEXT NOT NULL
- `is_default` BOOLEAN NOT NULL DEFAULT false
- `is_active` BOOLEAN NOT NULL DEFAULT true
- `sot_profile` TEXT NULL
- `default_session_phase` TEXT NULL
- `output_format_mode` TEXT NOT NULL DEFAULT `single_question`
- `language` TEXT NOT NULL DEFAULT `fr`
- `tone` TEXT NOT NULL DEFAULT `COACHING`
- `max_questions_per_turn` INTEGER NOT NULL DEFAULT 1
- `max_tokens` INTEGER NOT NULL DEFAULT 150
- `allow_lists` BOOLEAN NOT NULL DEFAULT false
- `ovh_llm_id` UUID NULL
- `metadata` JSONB NOT NULL DEFAULT `{}`
- `created_at` TIMESTAMPTZ DEFAULT NOW()
- `updated_at` TIMESTAMPTZ DEFAULT NOW()

Contraintes :

- unicité logique par (`organisation_id`, `prompt_type`, `code`)
- un prompt inactif n’est jamais sélectionné automatiquement
- la sélection effective suit la priorité : session → groupe → organisation

#### Abandon de `hugo_config` comme pivot

La table / abstraction `hugo_config` n’est plus la pièce centrale du design. Les réglages dynamiques doivent être portés prioritairement par :

- `TutorPrompt`
- `Group.default_tutor_prompt`
- `HugoSession.tutor_prompt`
- les overrides runtime de session / groupe pour le classifieur et la phase

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
- `PATCH /hugo/sessions/{session_id}/phase`
- `PATCH /hugo/sessions/{session_id}/classifier-config`
- `POST /hugo/sessions/{session_id}/messages`
- `POST /hugo/sessions/{session_id}/generate-trace`
- `POST /traces/{trace_id}/validate`
- `POST /hugo/sessions/{session_id}/share`

Ces endpoints exposent la session Hugo, son pilotage de phase, ses overrides runtime et le cycle standard message → trace → partage.

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

### 15.9 Internal (debug)

- `POST /internal/rag/search`

### 15.10 Qualiopi

- `POST /quality/qualiopi/evidence-bundle`

### 15.11 `TutorPrompt` et pilotage runtime

#### Catalogue de prompts Hugo

- `GET /hugo/tutor-prompts`
  - Rôles : tout utilisateur authentifié de l’organisation peut lister les prompts disponibles.
- `POST /hugo/tutor-prompts`
  - Rôles : `ORGADMIN`, `SUPERADMIN`.
  - Effet : création d’un `TutorPrompt` pour l’organisation courante.

- `GET /hugo/tutor-prompts/{id}`
  - Rôles : tout utilisateur authentifié de l’organisation.
- `PATCH /hugo/tutor-prompts/{id}`
  - Rôles : `ORGADMIN`, `SUPERADMIN`.
- `DELETE /hugo/tutor-prompts/{id}`
  - Rôles : `ORGADMIN`, `SUPERADMIN`.

Champs manipulables :

- `code`, `name`, `description`
- `system_template`, `user_template`
- `is_default`, `is_active`
- `language`, `tone`
- `output_format_mode`, `default_session_phase`
- `max_questions_per_turn`, `max_tokens`, `allow_lists`
- `ovh_llm_id`, `metadata`, `sot_profile`

#### Paramétrage de session Hugo

- `PATCH /hugo/sessions/{session_id}/phase`
  - permet de fixer ou vider `manual_phase_override`.

- `PATCH /hugo/sessions/{session_id}/classifier-config`
  - permet de fixer ou vider les overrides runtime :
    - `phase_classifier_enabled`
    - `phase_classifier_max_tokens`
    - `phase_classifier_min_confidence`
    - `phase_classifier_max_input_chars`

#### LLM et prompts annexes

- `GET/POST /hugo/ovh-llms`
- `GET/PATCH/DELETE /hugo/ovh-llms/{id}`
- `GET/POST /hugo/starter-prompts`
- `GET/PATCH/DELETE /hugo/starter-prompts/{id}`

Note : le design patché ne prévoit plus d’endpoint pivot `hugo_config` au niveau groupe. Les variations comportementales passent par `TutorPrompt` et les overrides runtime déjà présents sur la session / le groupe.

## 16. Tests d'acceptation minimaux

| Test | Critère |
| :-- | :-- |
| **RLS cross-tenant** | Org A ne lit/écrit jamais org B |
| **Partage confidentialité** | Tuteur/formateur ne voient rien sans partage explicite apprenant |
| **Sélection TutorPrompt** | Priorité effective : session → groupe → organisation |
| **Phase runtime** | `manual_phase_override` et `classifier-config` modifient bien le comportement de session |
| **Hugo anti-boucle** | Hugo ne repose pas comme question principale un critère déjà couvert sauf ambiguïté explicite |
| **Hugo clarification prioritaire** | Si `episode_clarity=low`, Hugo clarifie avant d’analyser |
| **Hugo accès à l’action réelle** | Si `has_concrete_actions=false`, Hugo demande l’action concrète plutôt qu’une analyse abstraite |
| **Fallback single-question** | Si `cognitive_load=high` ou `interaction_risk=high`, Hugo émet une seule question simple |
| **Micro-explication bornée** | Une micro-explication n’apparaît que si les conditions ZPD / profondeur réflexive / balance épistémique sont remplies |
| **Trace génération** | Trace générée à partir de la session → validation → exports JSON/CSV |
| **RAG anti-absurde ("procédures")** | 8–10 requêtes "procédure" → chunk "procédure/sécurité" dans top-5 |
| **Indexation LOW_TEXT** | PDF scanné → statut `LOW_TEXT` flaggé |
| **Historique apprenant** | Accessible + filtres fonctionnels (date, compétence) |
| **Journalisation debug LLM** | En sandbox/dev, prompts rendus, payloads et réponses brutes sont rejouables et reliés au tour |
| **UI responsive + PWA** | LEARNER (mobile) : session→trace→validate→share→evidence ; TUTOR/TRAINER (desktop) : dashboard/timeline ; app installable (PWA), et en absence réseau afficher “connexion requise” (pas d’offline en POC) |

## 17. Plan d'exécution : chemin critique

### 17.1 Lots d’alignement recommandés

| Lot | Objet | Livrables |
| :-- | :-- | :-- |
| **Lot 0** | Réalignement documentaire | SPEC patchée, `.cursorrules` alignées, prompts/doc interne mis à jour |
| **Lot 1** | Analyseur P0 | module d’analyse du tour produisant les 16 variables P0 |
| **Lot 2** | Décision locale P0 | moteur déterministe des règles 1.6.2 + `decision_trace` |
| **Lot 3** | Intégration orchestrateur | branchement dans `build_hugo_turn()` sans casser `TutorPrompt` |
| **Lot 4** | Tests / calibration | scénarios de non-boucle, fallback single-question, micro-explication, clôture facultative |
| **Lot 5** | Raffinement UX | affichage du focus du tour, starters, réglages de prompt, instrumentation debug |

### 17.2 Ordre de développement imposé

1. **Ne pas recréer une couche `hugo_config` parallèle**.
2. **Conserver `TutorPrompt` comme brique de configuration runtime**.
3. **Insérer Hugo 1.6.2 comme couche d’analyse + décision avant le rendu du prompt**.
4. **Conserver le backend Django et enrichir l’orchestrateur existant**.
5. **Tester d’abord les cas de boucles, de surcharge cognitive et de clarification**.

### 17.3 Priorité P1 (si marge)

- mémoire thématique plus riche
- contradiction gouvernée avec retrieval ciblé
- profilage pédagogique plus fin
- instrumentation analytique P1

## 18. Annexes : schémas JSON

*(Contenu technique inchangé)*

***

## 19. Conformité Qualiopi (RNQ)

### 19.1 Principes

Qualiopi = **processus certifié** (RNQ = Référentiel National Qualité, 7 critères, 32 indicateurs).

### 19.2 Cartographie RNQ ↔ Fonctionnalités POC

| Critère RNQ | Indicateurs clés | Fonctionnalités POC existantes | Preuves produites |
| :-- | :-- | :-- | :-- |
| **Critère 1** : Informations publiques | 1, 2, 3 | Organisation OF (`organisation`), descriptifs formations (hors POC) | Export CSV métadonnées OF |
| **Critère 2** : Objectifs et adaptation | 4, 5, 6 | Référentiels RNCP/RS (`referential_import_v2`), overlay par classe | Export référentiel + overlay par groupe |
| **Critère 3** : Accompagnement | 7, 8, 9 | Hugo piloté par état (1 objectif de régulation, 1 question simple par défaut), liens tuteur/apprenant, partage contrôlé | Historique sessions, traces validées, audit_log |
| **Critère 4** : Adéquation moyens | 10, 11, 12, 13 | Bibliothèque classe `ACTIVE`, RAG, preuves photo | Liste docs `ACTIVE`, logs indexation, preuves attachées |
| **Critère 5** : Qualification pros | 14, 15, 16 | Rôles `TUTOR`, `TRAINER`, table `user` | Export liste formateurs/tuteurs avec rôles |
| **Critère 6** : Investissement | 17, 18, 19, 20, 21 | `audit_log`, exports horodatés, traces validées | Exports CSV/JSON horodatés, audit_log par org |
| **Critère 7** : Recueil appréciations | 22, 23, 24, 25 | Traces avec auto-évaluation (`learner_self`), validations | Export traces (statut `validated_by`, timeline) |

**Pour un audit AFEST Qualiopi**, les indicateurs critiques :

- **Indicateurs 7, 11, 18, 20, 22** (traces, accompagnement, évaluations, preuves)

### 19.3 Données produites (POC)

- Export CSV pivot (apprenant × compétence × date × statut)
- Export JSON `trace_rich_v1` (payload structuré interop)
- `audit_log` horodaté par `organisation_id`
- Preuves photo (MinIO + meta GPS opt-in)

### 19.4 Pack audit Qualiopi (POC lite)

ZIP minimal mais exploitable, sans couverture fine des 32 indicateurs.

**Contenu minimum du ZIP (POC)** :

- Exports CSV/JSON (traces, validations, preuves) sur période
- `audit_log` filtré (validations, partages, exports)
- Référentiels + overlays actifs
- Liste documents `ACTIVE` + citations RAG

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

## 21. Intégrations et effets de bord (POC)

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

| Effet de bord | Risque | Mitigation POC |
| :-- | :-- | :-- |
| **Double saisie** | Formateur crée apprenants dans Hugo **ET** ERP OF | Acceptée provisoirement dans le POC ; à réduire par imports ciblés si nécessaire |
| **Divergence référentiels** | Mêmes compétences nommées différemment Hugo/LMS/SIRH | Overlay par classe et export structuré pour contrôle humain |
| **Conflit confidentialité vs preuve** | Partage trop opt-in → formateur/qualité ne voient rien | Workflow guidé (message explicite apprenant, partage défaut synthèse uniquement) |
| **Duplication documents** | Même doc dans Hugo **ET** LMS/Digiforma | MinIO Hugo (docs classe uniquement) |
| **Incompatibilité exports** | CSV Hugo ≠ CSV SIRH/ERP | CSV configurable (séparateur, encodage) |
| **Authentification multiples** | Comptes séparés Hugo/LMS/SIRH | Comptes créés manuellement dans le POC |

### 21.3 Checklist POC

- [ ] Export CSV configurable (séparateur, colonnes, encodage)
- [ ] Exports JSON `trace_rich_v1` testés
- [ ] Tests cross-tenant RLS exécutés
- [ ] Documentation d'import manuel et d'export disponible
- [ ] Politique de déploiement POC documentée (CPU-only ou OVH AI Endpoints)

## 22. Changelog

### v1.5 patch Hugo 1.6.2 — 26 mars 2026

**Changements majeurs** :

- réalignement de la SPEC sur le backend **Django + DRF** déjà développé ;
- abandon de `FastAPI / SQLAlchemy / Alembic` comme stack de référence ;
- remplacement de `hugo_config` comme pivot comportemental par **`TutorPrompt` + overrides runtime session/groupe** ;
- introduction du **runtime conversationnel orchestré** (contexte → analyse → décision → rendu → appel LLM → post-traitement) ;
- adoption du **noyau d’état P0 Hugo 1.6.2** et de la décision locale pilotée par état ;
- remplacement de la règle rigide "1 question par message" par **1 objectif de régulation par message**, avec **1 question simple par défaut** et possibilité bornée de **2 questions maximum** si même micro-objectif ;
- autorisation explicite de la **journalisation debug des appels/réponses LLM** en phase de développement et de sandbox ;
- remplacement de la contrainte **CPU-only** par **CPU-only ou OVH AI Endpoints** ;
- recentrage intégral du document sur le **POC Hugo**, sans cadrage normatif des développements ultérieurs.

### v1.4 (clarifiée) — 17 février 2026

**Changements majeurs** :

- **Section 19.4** : clarification du pack audit Qualiopi POC lite (ZIP minimal exploitable)
- **Architecture d'évolutivité** : maintien d'une architecture objet-centric compatible avec des évolutions ultérieures sans les normer dans cette SPEC
- **Principe intégration** : Hugo = module AFEST exportable et intégrable par flux simples dans le POC

**Clarifications** :

- Approche objet métier (pas d'endpoints agents dédiés dans le POC)
- Exports et evidence bundle conçus comme artefacts métier auditables

### v1.3 (révisée) — 17 février 2026

**Améliorations structurelles** :

- Ajout section 1 "Vision produit" recentrée sur le périmètre du POC
- Ajout section 3 "Doctrine technique" (consolidation principes non-négociables : RLS, confidentialité, CPU-only ou OVH AI Endpoints, best effort)
- Réorganisation personas (séparation claire vision métier ↔ endpoints API)
- Harmonisation références sections (numérotation cohérente)
- Consolidation schémas JSON (regroupement annexes)

**Pas de perte d'information** : tout le contenu v1.3 d'origine conservé, restructuré pour meilleure lisibilité.

### v1.3 (originale) — 17 février 2026

- Harmonisation nommage (`SPEC_POC_v1.3` + en-têtes SoT)
- Performance : latence cible 3 s, pointes jusqu'à 15 s acceptables en POC
- Exports : CSV (séparateur `;` par défaut, UTF-8 BOM par défaut) configurable via paramètres d'export
- Qualiopi : pack audit lite **IN POC**
- Référentiels : 2 RNCP + 2 RS (pour 2 démos / 2 formations)

***

**FIN SPEC_POC_v1.5**

