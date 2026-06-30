# Écarts doc / code / produit — Workspace Hugo

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Objet :** divergences factuelles entre documentation, `hugo_back`, `hugo-hugolucia/frontend_1.8`, et API distante supposée — sans solutions techniques.  
**S'appuie sur :** docs `00` à `04` dans `docs-workspace/`.  
**Limite :** `https://hugoback.encoors.com` **non interrogée** dans cet audit → écarts prod marqués **À VÉRIFIER**.

---

## 1. Périmètre

### Comparé

| Couche A | Couche B |
|----------|----------|
| Docs à risque (MEMO CTO, audits 1.9, `p0_description*`, SPEC 1.6.2, `docker-compose`, LOTs) | Code `hugo_back/` |
| Docs produit 1.8 / audits front | Code `hugo-hugolucia/frontend_1.8/` |
| `hugo-main` | `hugo-hugolucia` |
| Code local (`hugo_back` + front hugolucia) | Runtime API distante (`.env` → `hugoback.encoors.com`) |

### Exclu

- Backlog ou tickets 1.9
- Comportement détaillé du moteur (déjà dans doc 02)
- Parcours UX détaillé (déjà dans doc 03)
- Fichiers `.docx`, `shell-heredoc-v1.5.txt`
- Équivalence git / historique des branches

---

## 2. Écarts structure workspace

| Écart | Doc / attente | Réalité filesystem | Gravité | Statut |
|-------|---------------|-------------------|---------|--------|
| Monorepo « complet » | `docker-compose.yml` L40–41 : `build: context: ./backend` ; `DEPLOY_S0.md` suppose stack Django | `hugo-main/backend/` et `hugo-hugolucia/backend/` **vides** (0 fichier) | **Bloquante** | CONFIRMÉ |
| Emplacement moteur | Docs : `backend/apps/hugo/…` (`p0_description_technique_actuelle.md` L17–25) | Moteur dans `hugo_back/apps/hugo/…` | **Bloquante** | CONFIRMÉ |
| Lien back ↔ monorepos | README monorepo `# hugo_poc` seul | Aucun lien documenté ; 3 dossiers séparés | **Majeure** | AMBIGU |
| Stack docker locale | `docker compose up` dans monorepos | Échoue sans rattacher `hugo_back` à `backend/` | **Bloquante** | CONFIRMÉ |
| Nginx prod monorepo | `docker-compose.yml` L108 : `./frontend/dist` | Prod montrable = `frontend_1.8/` ; pas monté dans compose | **Majeure** | CONFIRMÉ |
| Duplication documentaire | Une spec par chemin | ~41 copies `hugo-main` ↔ `hugo-hugolucia` (doc 04) | **Majeure** | CONFIRMÉ |
| Bibliothèque recalage | Anciennes specs = vérité | `docs-workspace/02` et `03` recalent moteur/produit | Informatif | CONFIRMÉ |
| Index `04` sous-déclare `docs-workspace` | §2.9 listait 5 fichiers alors que la bibliothèque compte 00–09 | Écart **méta-documentaire** — corrigé dans `04` (juin 2026) | Faible | CONFIRMÉ → corrigé |

---

## 3. Écarts moteur (doc ↔ `hugo_back`)

| Écart | Source doc | Constat code | Preuve | Gravité |
|-------|------------|--------------|--------|---------|
| Synthèse = stub `synthesis_queued` | `MEMO_CTO_Hugo1.9_v2.md` écart #3 L25 | `generate_synthesis()` appelle LLM + fallback | `synthesis_service.py` L123–152 ; `test_conversation_progress.py` | **Bloquante** si MEMO pris pour vérité — **écart doc obsolète** | CONFIRMÉ |
| Consolidation mémoire seulement sur `generate-trace` | MEMO écart #5 L27 | `_post_conversation_hooks()` appelle `consolidate_session` après **chaque message** | `views_sessions.py` L634–638, L1274, L1347, L1359 | **Majeure** — **écart doc obsolète** | CONFIRMÉ |
| Injection `LearnerThemeMemory` dans orchestrateur | MEMO écart #4 ; `LOT4_memoire_inter_session.md` L218 | Aucune référence dans `hugo_orchestrator.py` ni `context_builder.py` | `grep LearnerThemeMemory` → uniquement `memory_consolidator.py`, `views_sessions.py` | **Majeure** | CONFIRMÉ |
| Snapshot qualité non post-session | MEMO écart #6 L28 | `record_session_signal()` dans `_post_conversation_hooks` | `views_sessions.py` L638 ; `test_quality_signals.py` | **Majeure** — **écart doc obsolète** | CONFIRMÉ |
| TutorConductProfiles « codés en dur seulement » | MEMO §3 L40–41, écart #8 L30 | Modèle + CRUD API + `conduct_profile_resolver.py` dans orchestrateur L228 | `views_conduct_profiles.py`, `hugo_orchestrator.py` L228–229 | **Majeure** — **écart doc partiellement obsolète** (admin UI séparée) | PARTIEL |
| P0 v17 = état cible / gel | SPEC 1.6.2 ; audits 1.9 (gel P0) | P0 **legacy** actif ; v17 derrière flag `false` | `base.py` L182 ; `conftest.py` L6 | **Majeure** | CONFIRMÉ |
| Classifieur P0 LLM actif | `p0_description*` (selon version) | Désactivé par défaut | `HUGO_P0_CLASSIFIER_ENABLED=false` `base.py` L178 | Majeure | CONFIRMÉ |
| RAG vectoriel | `docker-compose` pgvector ; modèle `embedding` | Sélection **lexicale** uniquement | `rag_support.py` `select_rag_chunks` ; pas de `embedding` dans ce fichier | Majeure | CONFIRMÉ |
| Indexation calcule embeddings | Specs infra / library | `index_document` découpe texte seulement | `library/tasks.py` L22–26 | Majeure | CONFIRMÉ |
| `recalc_learner_state` fonctionnel | Implicite POC | Placeholder `skills_matrix: {}` | `apps/hugo/tasks.py` L15–19 | Majeure | CONFIRMÉ |
| Trace `generate-trace` riche | Specs traces / Felix | Payload minimal (messages_count, listes vides) | `views_sessions.py` L1380–1387 | Majeure | CONFIRMÉ |
| `production.py` sécurisé | Attente settings prod | `DEBUG = True` | `config/settings/production.py` L5 | Majeure | CONFIRMÉ |
| Token OVH en dur | — | JWT default dans settings | `base.py` L187 | Majeure | CONFIRMÉ |
| RLS cross-tenant Postgres réel | MEMO écart #10 ; SPEC POC | Tests sur SQLite ; middleware présent | `test_cross_tenant.py` ; pas de preuve Postgres prod | **Bloquante** infra | **À VÉRIFIER** |
| Playwright / E2E | MEMO écart #9 ; `PLAN_TESTS_API_CHROMIUM.md` | Aucune config Playwright dans repo | `grep playwright` → docs seulement | Majeure | CONFIRMÉ |
| Chemins `backend/apps/` | `p0_description_technique_actuelle.md` L17+ | Arborescence `hugo_back/apps/` | Chemins document | **Bloquante** lecture | CONFIRMÉ |
| Suppression utilisateurs admin | MEMO écart #7 (admin incomplet) | `UsersView` : `POST` + `PATCH` seulement ; pas de `DELETE` visible côté API accounts | `UsersView.vue` L46, L74 ; pas de Destroy dans `apps/accounts` | Majeure | CONFIRMÉ |

---

## 4. Écarts produit (doc ↔ front hugolucia)

| Écart | Source doc | Constat front | Preuve | Gravité |
|-------|------------|---------------|--------|---------|
| Front prod recalcule signaux P0 | MEMO écart #1 L23 ; audit LOT2 « le front ne calcule rien » | `ProdLearnerWorkspace` : `buildEngagementUiModel(sessionUiState)` — pas de `turn_state` | `ProdLearnerWorkspace.vue` L119–122, L224–227 ; `engagementUiModel.js` sans `turn_state` | **Bloquante** si MEMO pris pour prod — **écart doc obsolète** (parcours `/app`) | CONFIRMÉ |
| Boutons synthèse / évaluation non branchés | MEMO écart #2 L24 | `requestSynthesis()` / `requestEvaluation()` POST branchés | `ProdLearnerWorkspace.vue` L505–549, L638–639 | **Bloquante** si MEMO pris pour vérité — **écart doc obsolète** | CONFIRMÉ |
| Fallback TurnState en prod | Audit mai 2026 (risque front) | Fallback `turn_state` **uniquement** dans `LearnerDetailView` mode testeur + `p0_debug` | `LearnerDetailView.vue` L15–17, L164, L850+ | Majeure — **hors parcours démo** | CONFIRMÉ |
| ConductProfiles non administrables | MEMO écart #8 | `ConductProfilesView.vue` + route `/conduct-profiles` en mode **tester** | `router/index.js` L35 ; `ConductProfilesView.vue` | Majeure — **écart doc partiel** (UI existe, pas en prod) | PARTIEL |
| Admin comptes incomplet | MEMO écart #7 | Création / édition users ; pas de suppression UI | `UsersView.vue` | Majeure | CONFIRMÉ |
| Streaming SSE prod | Specs / nginx hugolucia | Implémenté avec fallback POST | `ProdLearnerWorkspace.vue` L327–476 ; `messageStream.js` | Informatif si back supporte SSE | IMPLÉMENTÉ local front |
| API distante par défaut | Docs deploy = local | `.env` → `hugoback.encoors.com` | `.env.development`, `.env.production` | **Bloquante** recalage | CONFIRMÉ |
| Tests E2E front | Audit 1.9 | `npm test` = 3 tests unitaires utils seulement | `package.json` ; pas Playwright | Majeure | CONFIRMÉ |

---

## 5. Écarts main ↔ hugolucia

| Zone | `hugo-hugolucia` | `hugo-main` | Gravité |
|------|------------------|-------------|---------|
| **Référence produit** | `frontend_1.8` avancé (SSE, `HugoProgressPanel`, `ConductProfiles`) | Version intermédiaire | **Bloquante** si main utilisé pour démo |
| Route `/conduct-profiles` | Présente | **Absente** (`router/index.js`) | Majeure |
| `messageStream.js` | Présent | Absent | Majeure |
| `progressionLabels.js` | Présent | Absent | Majeure |
| Specs 1.9 actives | `specs/` (MEMO, LOT7, SPEC v2) | **Absent** | Majeure doc |
| Specs 1.8 actives | Archivées `specs-old/specs-old-1.8/` | `specs/` actif | Majeure doc |
| Audits probatoires | `docs/rapport_audit_*` | Absent | Informatif |
| Nginx SSE | Route stream dans `api.conf` | Absent | Majeure deploy |
| `frontend/` testeur | Identique | Identique | — |
| Racine docs (SPEC_POC, Synopsis…) | Copie canonique | Doublon identique | Informatif |

**Arbitrage documenté (doc 01/03) :** produit = **hugolucia** ; specs 1.8 actives textuelles = **hugo-main/specs/** (archives dans hugolucia).

---

## 6. Écarts locaux ↔ API distante

La démo courante (`frontend_1.8` + `.env`) cible **`https://hugoback.encoors.com`**. Inspection HTTP partielle : `10_FICHE_RUNTIME_PROD_ENCOORS.md` (2026-06-12). Les points suivants restent **À VÉRIFIER** ou **VRIFIER** (flags env) :

| Point | Code local `hugo_back` | API distante | Statut |
|-------|------------------------|--------------|--------|
| Version déployée du back | Workspace juin 2026 | Inconnue | **À VÉRIFIER** |
| Flags `HUGO_P0_V17_ENABLED` / classifieur prod | `false` par défaut local | Inconnu | **À VÉRIFIER** |
| Synthèse LLM réelle en prod | Implémentée localement | Inconnu | **À VÉRIFIER** |
| Endpoints `request-synthesis` / `request-evaluation` | Présents | Inconnu si même contrat | **À VÉRIFIER** |
| Streaming SSE `/messages/stream/` | Présent | Inconnu (CORS, nginx) | **À VÉRIFIER** |
| TutorConductProfiles en prod | API + resolver locaux | Inconnu | **À VÉRIFIER** |
| Injection mémoire inter-session au tour | Absente localement | Peut diverger | **À VÉRIFIER** |
| RLS Postgres effectif | Middleware + tests SQLite | Inconnu | **À VÉRIFIER** |
| Écarts listés dans MEMO (mai–juin 2026) | Partiellement obsolètes en local | Peut encore refléter prod distante | **À VÉRIFIER** |

**Conséquence :** une démo contre `hugoback.encoors.com` **ne prouve pas** l'état de `hugo_back` local, et inversement.

---

## 7. Docs dangereux confirmés

Documents dont des affirmations sont **contredites par le code local** (juin 2026) :

| Document | Affirmation problématique | Contredit par | Type d'écart |
|----------|---------------------------|---------------|--------------|
| `hugo-hugolucia/specs/MEMO_CTO_Hugo1.9_v2.md` | Écarts #1, #2, #3, #5, #6 (front P0, boutons, synthèse stub, consolidation trace-only, qualité) | `ProdLearnerWorkspace.vue`, `synthesis_service.py`, `views_sessions.py` | Doc **obsolète** sur ces points |
| `hugo-hugolucia/specs/MEMO_CTO_Hugo1.9_v2.md` | Écart #4 injection mémoire | Absence dans `hugo_orchestrator.py` | Doc **encore valide** |
| `hugo-hugolucia/specs/MEMO_CTO_Hugo1.9_v2.md` | Écart #8 conduct profiles « codés en dur » | `TutorConductProfile` + resolver + API | Doc **partiellement obsolète** |
| `hugo-hugolucia/p0_description_technique_actuelle.md` | Chemins `backend/apps/hugo/…` | `hugo_back/apps/hugo/…` | Chemins **invalides** |
| `hugo-hugolucia/docs/DEPLOY_S0.md` | Stack `./backend` complète | `backend/` vide | Deploy **trompeur** |
| `hugo-hugolucia/SPEC Hugo 1.6.2…md` | Doctrine P0 = implémentation | Legacy actif ; v17 off | **CIBLE** lue comme réel |
| `hugo-hugolucia/specs-old/specs-old-1.9/LOT4_memoire_inter_session.md` | Injection orchestrateur requise | Non implémentée | Spec **cible** non atteinte |
| `specs-old/specs_audit_1.9/rapport_audit_hugo_1_9_2026-05-19.md` | État mai 2026 comme actuel | Front/back locaux évolués depuis | Audit **daté** |
| `hugo-main/specs/hugo-1.8-spec-finale.md` | État produit 1.8 | `hugo-hugolucia/frontend_1.8` plus avancé | Produit **dépassé** |

**Non contredits (toujours valides localement) :** absence Playwright ; absence injection mémoire ; RAG non vectoriel ; `backend/` vide dans monorepos.

---

## 8. Synthèse

### Écarts bloquants (recalage Perplexity)

1. **Structure workspace** : moteur dans `hugo_back`, pas dans `backend/` des monorepos — toute doc/deploy qui suppose le contraire est fausse.
2. **MEMO CTO juin 2026** : 5 écarts sur 10 **obsolètes** vis-à-vis du code local ; le garder comme vérité **fausse** le recalage.
3. **Démo = API distante** : comportement prod **non garanti** = copie locale (`À VÉRIFIER`).
4. **hugo-main vs hugolucia** : deux vérités produit si non arbitré — **hugolucia** seul pour la démo.
5. **SPEC 1.6.2 / audits mai** : ne pas en déduire l'état runtime — utiliser docs `02` et `03`.

### Écarts informatifs (ne bloquent pas le recalage documentaire)

- Duplication ~41 fichiers main/hugolucia
- Trace `generate-trace` payload minimal
- `recalc_learner_state` placeholder
- Token OVH / `DEBUG` en production settings
- Absence tests E2E (confirmée doc + code)

### À trancher avant doc 06 (préparation 1.9)

| Décision | Pourquoi |
|----------|----------|
| **Runtime de référence** : `hugo_back` local vs `hugoback.encoors.com` | Tous les écarts prod restent ouverts |
| **P0 prod** : legacy vs v17 vs classifieur | Flags locaux ≠ prod possible |
| **MEMO CTO** : archive ou réécriture | Source Perplexity dangereuse en l'état |
| **Monorepo** : réintégrer `hugo_back` ou garder 3 dossiers | Impact deploy et chemins docs |
| **Injection mémoire LOT4** : écart confirmé — cible 1.9 ou hors scope ? | Spec vs code local aligné sur « absent » |

---

## 9. Renvoi

- **Préparation cible 1.9 :** `06_PREPARATION_CIBLE_1_9.md` (à produire)
- **Vérité moteur :** `02_ETAT_MOTEUR_REEL.md`
- **Vérité produit :** `03_ETAT_PRODUIT_REEL.md`
- **Index sources :** `04_INDEX_DOCUMENTAIRE_QUALIFIE.md`

---

*Document 05 — écarts croisés doc/code/produit juin 2026. API distante non inspectée.*
