# Matrice endpoint × rôle — baseline B

**Version :** 1.0  
**Date :** 2026-07-01  
**Baseline :** B locale — `config.settings.sqlite_test`, `test.sqlite3`, `HUGO_P0_V17_ENABLED=false` (P0 legacy)  
**Stack :** `frontend_1.8` + `hugo_back` (`localhost:5173` → proxy `/api` → `:8000`)  
**Statut :** **doctrine provisoire** pour la colonne « Interdit produit » sur `/ui-state/` persona (**Décision B**, 01/07/2026)

**Sources :** `hugo_back` urls/views (lecture 01/07), front prod (`useHugoSessionChat`, workspaces), R2/R3/R4, `addendum_exploration_baseline_B_2026_07_01.md`, rejeux pytest/Playwright 01/07.

**Ne remplace pas** R4 (contrats détaillés) ; sert de **vue croisée** endpoint × rôle pour specs, tests et revues d’architecture.

---

## Légende des statuts

| Statut | Signification |
|--------|----------------|
| **OK** | Consommation normale et attendue pour ce rôle (front prod ou parcours métier confirmé). |
| **Owner-only** | Callable en API si `HugoSession.learner = request.user` ; pas d’usage produit cross-session / cross-rôle. |
| **Interdit produit** | Ne doit pas piloter l’UI ou la régulation de ce rôle (garde front et/ou backend 404). |
| **Écart produit ouvert** | Comportement API figé mais écart documenté (décision produit en attente). |
| **Non concerné** | Hors périmètre du rôle. |

**Tags preuve (colonne Notes) :** REL OBSERV = code + test 01/07 ; PARTIEL = code sans E2E récent ; À VÉRIFIER = non rejeu.

**Modèle ACL session :** la plupart des routes `/hugo/sessions/{id}/*` filtrent `learner=request.user`. Les sessions **persona** tuteur/formateur ont `session.learner` = le compte tuteur/formateur connecté (pas l’apprenant accompagné).

---

## Décision B — `GET /hugo/sessions/{id}/ui-state/`

| Niveau | Règle |
|--------|--------|
| API | **Owner-only** pour toute session dont l’utilisateur est propriétaire (apprenant **ou** persona). Pas de 404 persona documenté. |
| Produit | **Contract d’engagement apprenant** : consommé par `ProdLearnerWorkspace` (`loadUiState: true`). |
| Persona | **Interdit produit** côté workspaces tuteur/formateur (`loadUiState: false`, `buildPersonaConversationFeedModel`). |

---

## 1. Runtime session — tour conversationnel

Préfixe : `/hugo/` sauf mention contraire.

| Endpoint | Apprenant | Tuteur persona | Formateur persona | Admin | Notes |
|----------|-----------|----------------|-------------------|-------|-------|
| `GET/POST /hugo/sessions/` | **OK** | **OK** (création session persona) | **OK** (idem) | **Non concerné** | POST : `learner=request.user`. Tuteur : `openTutorWorkspaceChat` + profils workspace. REL OBSERV |
| `GET/PATCH /hugo/sessions/{id}/` | **OK** | **Owner-only** | **Owner-only** | **Non concerné** | Favoris apprenant ; persona owner sur sa session. PARTIEL |
| `GET/POST /hugo/sessions/{id}/messages/` | **OK** | **OK** | **OK** | **Non concerné** | Même orchestrateur `build_hugo_turn` ; prompt différencié persona. REL OBSERV |
| `POST /hugo/sessions/{id}/messages/stream/` | **OK** | **OK** | **OK** | **Non concerné** | Idem. REL OBSERV PARTIEL (E2E stream) |
| `GET /hugo/sessions/{id}/ui-state/` | **OK** | **Interdit produit** | **Interdit produit** | **Non concerné** | **Décision B** : API owner possible ; front persona ne consomme pas. Apprenant : REL OBSERV (cluster3, cluster16 PW) |
| `POST /hugo/sessions/{id}/set-posture/` | **OK** | **OK** (bootstrap workspace) | **Non concerné**¹ | **Non concerné** | Formateur : posture via création session seulement si appelé ; pas dans chat workspace courant. REL OBSERV |
| `GET /hugo/sessions/{id}/progress/` | **Non concerné**² | **Non concerné**² | **Non concerné**² | **Non concerné** | Non appelé front prod observé 01/07. PARTIEL |
| `PATCH /hugo/sessions/{id}/phase/` | **Non concerné**² | **Non concerné**² | **Non concerné**² | **Non concerné** | Override phase ; pas de consommation front prod `/app*`. PARTIEL |
| `PATCH /hugo/sessions/{id}/classifier-config/` | **Non concerné**² | **Non concerné**² | **Non concerné**² | **Non concerné** | Idem. PARTIEL |

¹ Formateur persona : pas d’appel `set-posture` observé dans `ProdTrainerChatWorkspace` ; création session possible depuis home.  
² Apprenant : endpoints existants ; non branchés au front prod UI v2 observé — régulation via `/ui-state/` + POST tour.

---

## 2. Régulation engagement apprenant (CTA, mémoire, traces, partage)

| Endpoint | Apprenant | Tuteur persona | Formateur persona | Admin | Notes |
|----------|-----------|----------------|-------------------|-------|-------|
| `POST .../request-synthesis/` | **OK** | **Interdit produit** | **Interdit produit** | **Non concerné** | Backend **404** si `is_persona_session`. REL OBSERV |
| `GET .../evaluation-readiness/` | **OK** | **Interdit produit** | **Interdit produit** | **Non concerné** | 404 persona. PARTIEL |
| `POST .../request-evaluation/` | **OK** | **Interdit produit** | **Interdit produit** | **Non concerné** | 404 persona. REL OBSERV |
| `POST .../finalize-evaluation/` | **OK** | **Interdit produit** | **Interdit produit** | **Non concerné** | 404 persona. PARTIEL |
| `GET .../memory-summary/` | **OK** (sa session) | **Interdit produit**³ | **Non concerné** | **Non concerné** | Session **apprenant** tierce : **Owner-only** apprenant ; probe tuteur → 403/404 attendu. REL OBSERV |
| `POST .../generate-trace/` | **OK** | **Non concerné** | **Non concerné** | **Non concerné** | Workspace apprenant uniquement. REL OBSERV |
| `POST .../share/` | **OK** | **Non concerné** | **Non concerné** | **Non concerné** | Flags `share_*` ; conditionne timeline tuteur. PARTIEL |
| `GET /learners/sessions/` | **Non concerné**² | **Non concerné** | **Non concerné** | **Non concerné** | Doublon liste ; front utilise `/hugo/sessions/`. PARTIEL |
| `GET /learners/traces/` | **OK** | **Non concerné** | **Non concerné** | **Non concerné** | `ProdLearnerWorkspace`. PARTIEL |
| `GET /learners/evidence/` | **OK** | **Non concerné** | **Non concerné** | **Non concerné** | Idem. PARTIEL |
| `POST /evidence/` | **OK** | **Non concerné** | **Non concerné** | **Non concerné** | Création preuve liée session apprenant. PARTIEL |

³ `TutorWorkspaceContextPanel` : probe documenté sur session **source apprenant** ; échec ACL attendu — pas de régulation tuteur via memory-summary.

---

## 3. Dashboard encadrement (lecture apprenant tiers)

Préfixe : `/dashboard/`

| Endpoint | Apprenant | Tuteur persona | Formateur persona | Admin | Notes |
|----------|-----------|----------------|-------------------|-------|-------|
| `GET /dashboard/groups/{g}/learners/` | **Non concerné** | **OK** (si `TutorLearnerLink`) | **Écart produit ouvert** | **OK** | **INC-02** : TRAINER → `[]` sans lien. Tuteur lié : OK. REL OBSERV |
| `GET /dashboard/.../learners/{l}/timeline/` | **Non concerné** | **OK** (apprenant lié) | **Owner-only**⁴ | **OK** | Messages si `share_verbatim`. Pilotage compact sur messages learner. REL OBSERV |
| `GET /dashboard/groups/{g}/competences/` | **Non concerné** | **OK** | **OK** | **OK** | Fiche tuteur. PARTIEL |
| `POST /traces/{id}/validate/` | **Non concerné** | **OK** | **OK** | **OK** | `TutorLearnerView`. REL OBSERV |

⁴ Formateur : même ACL que tuteur (`can_access_learner_in_group`) ; accès timeline si lien — pas de liste learners dashboard (INC-02).

---

## 4. Trainer — knowledge & orchestrateur formateur

Préfixe : `/hugo/trainer/`

| Endpoint | Apprenant | Tuteur persona | Formateur persona | Admin | Notes |
|----------|-----------|----------------|-------------------|-------|-------|
| `GET/POST /trainer/knowledge-items/` | **Non concerné** | **Non concerné** | **OK** | **OK** | `can_manage_trainer_knowledge`. REL OBSERV |
| `PATCH /trainer/knowledge-items/{id}/` | **Non concerné** | **Non concerné** | **OK** | **OK** | Import chat + knowledge UI. REL OBSERV |
| `POST /trainer/knowledge-items/{id}/validate/` | **Non concerné** | **Non concerné** | **OK** | **OK** | REL OBSERV |
| `GET .../elicitation-questions/` | **Non concerné** | **Non concerné** | **OK** | **OK** | REL OBSERV |
| `POST .../elicitation-answers/` | **Non concerné** | **Non concerné** | **OK** | **OK** | REL OBSERV |
| `POST /trainer/ingest-document/` | **Non concerné** | **Non concerné** | **OK** | **OK** | Route backend ; front élicitation peut appeler variante proxy — À VÉRIFIER alignement URL front. PARTIEL |
| `GET /trainer/evaluation-records/` | **Non concerné** | **Non concerné** | **OK** | **OK** | Gestion validations (rôles trainer/admin). PARTIEL |
| `POST .../evaluation-records/{id}/validate/` | **Non concerné** | **Non concerné** | **OK** | **OK** | Nom « tutor_validated » ; consommé trainer/admin. PARTIEL |

---

## 5. Configuration conversationnelle (admin / lecture bootstrap)

| Endpoint | Apprenant | Tuteur persona | Formateur persona | Admin | Notes |
|----------|-----------|----------------|-------------------|-------|-------|
| `GET /hugo/learner-conversation-profiles/` | **OK** (home) | **OK** (bootstrap workspace) | **OK** (home chat) | **OK** (CRUD) | GET tous auth ; POST/PATCH admin. REL OBSERV |
| `POST/PATCH .../learner-conversation-profiles/` | **Non concerné** | **Non concerné** | **Non concerné** | **OK** | REL OBSERV |
| `GET /hugo/tutor-prompts/` | **Non concerné** | **Non concerné** | **Non concerné** | **OK** (lecture + write) | Runtime résolveur ; admin UI. PARTIEL |
| `GET/POST/PATCH /hugo/conduct-profiles/` | **Non concerné** | **Non concerné** | **Non concerné** | **OK** | Posture/conduct config. PARTIEL |
| `GET/POST/PATCH /hugo/persona-conversation-profiles/` | **Non concerné** | **Non concerné** | **Non concerné** | **OK** | Pass 2 persona ; preview sans LLM. REL OBSERV (HTTP 201/200 sqlite) |
| `POST .../persona-conversation-profiles/{id}/preview-render/` | **Non concerné** | **Non concerné** | **Non concerné** | **OK** | REL OBSERV |
| `GET/POST/PATCH /hugo/evaluation-prompt-profiles/` | **Non concerné** | **Non concerné** | **Non concerné** | **OK** | Config évaluation apprenant. PARTIEL |
| `GET/POST/PATCH /hugo/evaluation-policies/` | **Non concerné** | **Non concerné** | **Non concerné** | **OK** | Idem. PARTIEL |
| `GET/POST /hugo/ovh-llms/`, `/starter-prompts/` | **Non concerné** | **Non concerné** | **Non concerné** | **OK** | Admin prompts. PARTIEL |

---

## 6. Référentiels, groupes, documents (périmètre formateur / apprenant)

| Endpoint | Apprenant | Tuteur persona | Formateur persona | Admin | Notes |
|----------|-----------|----------------|-------------------|-------|-------|
| `GET /groups/` | **OK** | **OK** | **OK** | **OK** | REL OBSERV |
| `GET /groups/{id}/referential-config/` | **OK** | **Non concerné** | **OK** | **OK** | Apprenant workspace + library trainer. PARTIEL |
| `GET /groups/{id}/members/` | **Non concerné** | **Non concerné** | **OK** | **OK** | Contexte formateur. PARTIEL |
| `GET/POST /referentials/`, import | **Non concerné** | **Non concerné** | **OK** | **OK** | Shell trainer. PARTIEL |
| `GET/POST /documents/*`, `/groups/{id}/library/` | **Non concerné** | **Non concerné** | **OK** | **OK** | Library formateur. PARTIEL |

---

## 7. Synthèse par rôle (régulation conversationnelle)

| Rôle | Canaux principaux | Endpoints à ne pas mélanger |
|------|-------------------|-----------------------------|
| **Apprenant** | `/hugo/sessions/*` owner + **`/ui-state/`** + CTA + memory-summary + traces | Dashboard, `/hugo/trainer/*` |
| **Tuteur persona** | `/hugo/sessions/*` owner (chat) + `/dashboard/*` + `/traces/validate` | **`/ui-state/`** (Décision B), CTA apprenant, memory-summary apprenant tierce |
| **Formateur persona** | `/hugo/sessions/*` owner (chat) + `/hugo/trainer/*` + library/référentiels | **`/ui-state/`**, CTA apprenant ; liste learners dashboard (**INC-02**) |
| **Admin** | CRUD configs `/hugo/*-profiles`, prompts, persona | Runtime tour (sauf superadmin en test) ; pas de shell prod dédié |

---

## 8. Dettes et risques (matrice)

| Point | Statut | Action doc / test |
|-------|--------|-------------------|
| Persona pourrait appeler `/ui-state/` (API owner) | **À surveiller** | Décision B ; pas de garde backend 01/07 |
| `LearnerConversationFeed` partagé L/T/Tr | **À surveiller** | Voir addendum exploration §4 |
| INC-02 dashboard learners TRAINER | **Écart produit ouvert** | Pas de patch sans ADR CTO |
| Endpoints phase/classifier/progress non branchés front prod | **PARTIEL** | Ne pas speculer comme surface apprenant |

---

## 9. Références croisées

- Contrats détaillés : **R4** §2–3  
- Pipelines : **R3** §2  
- Décision B : `addendum_exploration_baseline_B_2026_07_01.md` §3  
- Plan tests : `plan_tests_chats_tuteur_formateur.md`

---

*Matrice v1.0 — 2026-07-01 — baseline B sqlite_test — doctrine provisoire Décision B.*
