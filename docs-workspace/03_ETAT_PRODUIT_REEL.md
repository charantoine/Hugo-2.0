# État produit réel — Hugo

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Périmètre :** surface montrable et consommation API côté front — référence `hugo-hugolucia/frontend_1.8/`.  
**S'appuie sur :** `00_HIERARCHIE_DOCUMENTAIRE.md`, `01_CARTOGRAPHIE_WORKSPACE_REEL.md`, `02_ETAT_MOTEUR_REEL.md` (contrats API, sans redécrire le moteur).  
**Ne couvre pas :** pipeline P0 interne, backlog 1.9.

---

## 1. Périmètre produit montrable

**Démo client (« prod_showable »)** : parcours apprenant masquant l'instrumentation P0 — routes `/login`, `/app`, `/app/session/:sessionId`, layout `ProdLearnerLayout`, branding **« Hugo - Lucia »** (sans numéro de version legacy). C'est la surface à montrer en démo.

**Testeur / calibration** : routes `meta.layout: 'tester'` (`/dashboard`, `/group/...`, admin) avec layout `TesterLayout` ; chat détaillé et debug P0 dans `LearnerDetailView.vue` (modales TurnState, override phase/classifier). Hors parcours démo client, mais présent dans le même build `frontend_1.8`.

**Référence produit :** `hugo-hugolucia/frontend_1.8/` — **IMPLÉMENTÉ**.  
`hugo-main/frontend_1.8/` = version **en retard** (voir §7).

**API cible** (preuve `.env.development`, `.env.production`) :

```
VITE_API_URL=https://hugoback.encoors.com
```

| Mode | Comportement | Statut |
|------|--------------|--------|
| `npm run dev` (défaut actuel) | Appels directs vers API distante | **Distant** — lançable sans back local |
| `VITE_API_URL=/api` + proxy Vite | Back local :8000 | **Lançable** si `hugo_back` tourne ; non configuré par défaut dans hugolucia |
| Build prod | Même URL distante | **À VÉRIFIER** vs `hugo_back` local |

La démo courante **ne prouve pas** le moteur local `hugo_back` ; elle reflète le runtime `hugoback.encoors.com` (**À VÉRIFIER** pour équivalence exacte).

---

## 2. Modes et configuration

**Sélection de mode** (`src/utils/frontendConfig.js`) :

| Variable env | Défaut si absent | Effet |
|--------------|------------------|-------|
| `VITE_FRONTEND_MODE` | `prod_showable` | `tester` → redirect `/dashboard` ; sinon `/app` |
| `VITE_ENGAGEMENT_UI_ENABLED` | `true` | Panneau progression / engagement |
| `VITE_SCENE_PROGRESS_ENABLED` | `true` | Barre de progression scène |
| `VITE_PERSISTENT_OBJECTS_ENABLED` | `true` | Objets persistants affichés |
| `VITE_SYMBOLIC_REWARDS_ENABLED` | `true` | Récompenses symboliques |
| `VITE_P0_DEBUG_ENABLED` | `false` | Modales P0 (uniquement si mode `tester`) |
| `VITE_GAMIFICATION_PROFILE` | `B` | Profils cosmétiques A / B / C |

**Bascule layout** (`src/App.vue` L9–11) : `route.meta.layout === 'tester'` → `TesterLayout`, sinon `ProdLearnerLayout`.

**Branding visible (état 20/06/2026) :**

| Emplacement | Texte |
|-------------|-------|
| `index.html` | `Hugo - Lucia` |
| `layouts/ProdLearnerLayout.vue` (topbar) | `Hugo - Lucia` / « Parcours apprenant » |
| `LoginView.vue` (eyebrow) | `POC Hugo Lucia` (sans version legacy) |
| Footer global (`PlatformVersionFooter.vue`) | `Hugo 2.0 — Lucia` |
| Dashboard admin (`DashboardView.vue`) | `Version de la plateforme : Hugo 2.0` |
| Profils A/B/C | `getGamificationProfileTheme()` — titres « Ludique assumé », « Intermédiaire », « Sobre pro » |

**Multi-org (SUPERADMIN, validé e2e 20/06) :** `OrgTenantSwitcher`, routes `/admin/organisations`, header API `X-Organisation-Id`. ORGADMIN : pas de switcher, périmètre org unique. Archive : [`tests/archives/tests_hugo_2_0_2026-06-18_20.md`](tests/archives/tests_hugo_2_0_2026-06-18_20.md).

Aucune variable d'env dans les `.env` commités sauf `VITE_API_URL` → mode prod et engagement **activés par défaut**.

---

## 3. Parcours apprenant (prod)

**Routes** (`src/router/index.js`) :

| Route | Vue | Rôle |
|-------|-----|------|
| `/login` | `LoginView.vue` | Auth JWT (`auth.js` → `/auth/login/`, `/auth/me/`) |
| `/` | redirect | → `/app` (mode prod) |
| `/app` | `ProdLearnerHomeView.vue` | Accueil, liste sessions, création session |
| `/app/session/:sessionId` | `ProdLearnerSessionView.vue` | Wrapper → `ProdLearnerWorkspace` |

**Composants clés :**

| Composant | Fichier | Rôle |
|-----------|---------|------|
| Workspace session | `ProdLearnerWorkspace.vue` | Chat, streaming, ui-state, synthèse/éval, traces |
| Panneau progression | `HugoProgressPanel.vue` | Scène, quêtes, boutons synthèse/évaluation |
| Session shell | `ProdLearnerSessionView.vue` | Conteneur route |

**Flux utilisateur ordonné :**

1. **Login** — `POST /auth/login/` → stockage `access`/`refresh` localStorage ; guard router (`router/index.js` L46–75)
2. **Accueil `/app`** — charge groupes + sessions + tutor prompts ; filtres date/favoris (`ProdLearnerHomeView.vue`)
3. **Créer ou ouvrir session** — `POST /hugo/sessions/` (groupe + `tutor_prompt_id` optionnel) → navigation `/app/session/:id`
4. **Workspace** — charge session, messages, `ui-state`, traces, evidence (`loadWorkspace`)
5. **Envoyer message** — tente **SSE** `POST .../messages/stream/` ; fallback `POST .../messages/` si 404/405/501 (`ProdLearnerWorkspace.vue` L467–476)
6. **Rafraîchir état produit** — `GET .../ui-state/` après chaque tour
7. **Actions optionnelles** — synthèse, évaluation, génération trace, partage tuteur (flags share)
8. **Retour accueil** — `goHome()` → `/app`

Pas d'accès TurnState brut ni override phase dans le parcours prod.

---

## 4. Contrats API consommés par le produit

Endpoints utilisés par le **parcours prod** (`ProdLearnerHomeView`, `ProdLearnerWorkspace`) :

| Endpoint | Fichier front | Usage | Statut |
|----------|---------------|-------|--------|
| `POST /auth/login/` | `stores/auth.js` | Connexion | IMPLÉMENTÉ |
| `GET /auth/me/` | `stores/auth.js` | Profil courant | IMPLÉMENTÉ |
| `POST /auth/refresh/` | `api/client.js` | Renouvellement JWT | IMPLÉMENTÉ |
| `GET /groups/` | `ProdLearnerHomeView`, `ProdLearnerWorkspace` | Liste groupes | IMPLÉMENTÉ |
| `GET /hugo/tutor-prompts/` | `ProdLearnerHomeView` | Sélection prompt à la création | IMPLÉMENTÉ |
| `GET /hugo/sessions/` | `ProdLearnerHomeView` | Historique sessions | IMPLÉMENTÉ |
| `POST /hugo/sessions/` | `ProdLearnerHomeView` | Création session | IMPLÉMENTÉ |
| `PATCH /hugo/sessions/{id}/` | `ProdLearnerHomeView` | Favori session | IMPLÉMENTÉ |
| `GET /hugo/sessions/{id}/` | `ProdLearnerWorkspace` | Détail session | IMPLÉMENTÉ |
| `GET /hugo/sessions/{id}/messages/` | `ProdLearnerWorkspace` | Historique chat | IMPLÉMENTÉ |
| `POST /hugo/sessions/{id}/messages/` | `ProdLearnerWorkspace` | Envoi message (fallback) | IMPLÉMENTÉ |
| `POST /hugo/sessions/{id}/messages/stream/` | `ProdLearnerWorkspace` + `fetchWithAuth` | Streaming SSE | IMPLÉMENTÉ (fallback si indisponible) |
| `GET /hugo/sessions/{id}/ui-state/` | `ProdLearnerWorkspace` | Contrat produit (progression, boutons) | IMPLÉMENTÉ |
| `POST /hugo/sessions/{id}/request-synthesis/` | `ProdLearnerWorkspace` | Synthèse | IMPLÉMENTÉ |
| `POST /hugo/sessions/{id}/request-evaluation/` | `ProdLearnerWorkspace` | Évaluation | IMPLÉMENTÉ |
| `POST /hugo/sessions/{id}/generate-trace/` | `ProdLearnerWorkspace` | Trace session | IMPLÉMENTÉ |
| `POST /hugo/sessions/{id}/share/` | `ProdLearnerWorkspace` | Partage tuteur | IMPLÉMENTÉ |
| `GET /learners/traces/` | `ProdLearnerWorkspace` | Traces apprenant | IMPLÉMENTÉ |
| `GET /learners/evidence/` | `ProdLearnerWorkspace` | Preuves apprenant | IMPLÉMENTÉ |

**Parsing SSE** : `utils/messageStream.js` (`parseSseEventBlock`, `consumeSseBuffer`) — **IMPLÉMENTÉ** ; tests dans `messageStream.test.js`.

---

## 5. Couche engagement / UI dérivée

**Rôle des modules :**

| Module | Rôle |
|--------|------|
| `engagementUiModel.js` | Transforme `ui-state` API → modèle d'affichage (scène, quêtes, boutons, récompenses) |
| `progressionLabels.js` | Libellés FR (scènes Raconter/Explorer/Synthétiser, maturité, boutons) |
| `frontendConfig.js` | Feature flags + profil gamification |
| `assistantVariants.js` | Variantes affichage réponses assistant (short/long) — chat uniquement |
| `HugoProgressPanel.vue` | Rendu visuel du modèle engagement |

**Back vs cosmétique front :**

| Donnée | Source | Statut |
|--------|--------|--------|
| `scene_label`, `scene_progress`, `quest_progress`, `maturity_color` | `GET /ui-state/` | Back |
| `synthesis_button_state`, `evaluation_button_state` | `GET /ui-state/` | Back |
| `persistent_objects`, `active_quest_label` | `GET /ui-state/` | Back |
| Libellés FR des scènes/boutons | `progressionLabels.js` | Cosmétique front |
| Profils A/B/C (barres, badges, quêtes visibles) | `GAMIFICATION_PROFILES` + flags env | Cosmétique front |
| Messages streaming « Hugo réfléchit… » avant 1er chunk | `ProdLearnerWorkspace.vue` L57–61 | Cosmétique front (fallback si pas de signal SSE back) |
| `isDegraded: true` si pas de `ui-state` | `buildEngagementUiModel` L205–207 | État neutre front |

**Preuve sans heuristique P0 locale en prod :** `engagementUiModel.test.js` L6 — « maps the session ui-state contract without local heuristics » ; `ProdLearnerWorkspace.vue` L744 — affichage « sans heuristique locale » pour objets persistants.

**Tests front** (`npm test`, 3 fichiers) :

| Fichier | Couverture |
|---------|------------|
| `engagementUiModel.test.js` | Mapping ui-state, état dégradé, visibilité évaluation |
| `messageStream.test.js` | Parsing SSE |
| `assistantVariants.test.js` | Extraction questions / variantes texte |

Pas de tests E2E / Playwright. Pas de test composant Vue intégré.

---

## 6. Back-office et mode testeur (bref)

**Activation :** `VITE_FRONTEND_MODE=tester` → redirect `/dashboard`, layout `TesterLayout`.

**Routes tester** (`router/index.js` L26–38) :

| Route | Vue | Rôle |
|-------|-----|------|
| `/dashboard` | `DashboardView` | Liste groupes |
| `/group/:groupId` | `GroupView` | Apprenants du groupe |
| `/group/:groupId/learner/:learnerId` | `LearnerSpaceView` | Espace apprenant testeur |
| `/groups-admin`, `/groups-admin/:groupId` | Admin groupes, bibliothèque RAG | Back-office |
| `/referentials`, `/referentials/import` | Référentiels | Import RNCP |
| `/tutor-prompts` | `TutorPromptsView` | CRUD prompts |
| `/conduct-profiles` | `ConductProfilesView` | CRUD TutorConductProfiles |
| `/ovh-llms` | `OvhLlmView` | Config modèles OVH |
| `/users`, `/users/:userId` | Gestion utilisateurs | Admin comptes |

**`LearnerDetailView.vue`** (~2400 lignes) : chat testeur, onglets traces/evidence/documents, override `phase/` et `classifier-config/`, modales `turn_state` / `conversation_decision` si `p0_debug_enabled` + mode tester (L15–17). **Hors démo prod** ; ne pas confondre avec `ProdLearnerWorkspace`.

**Exports** : `runExportAndDownload()` dans `api/client.js` → `/exports/run/` — utilisé côté testeur, pas dans parcours `/app`.

---

## 7. Écarts main vs hugolucia (produit)

`hugo-main/frontend_1.8` est une copie **en retard**. Différences constatées (`diff -rq`) :

| Élément | hugo-hugolucia | hugo-main |
|---------|----------------|-----------|
| `HugoProgressPanel.vue` | Présent | **Absent** |
| `messageStream.js` + tests SSE | Présent | **Absent** |
| `progressionLabels.js` | Présent | **Absent** |
| `ConductProfilesView.vue` + route `/conduct-profiles` | Présent | **Absent** |
| `ProdLearnerWorkspace.vue` | Streaming, ui-state, synthèse/éval | Version antérieure |
| `engagementUiModel.js` | Aligné ui-state | Diffère |
| `router/index.js` | + conduct-profiles | Sans cette route |
| `client.js` | `fetchWithAuth` pour SSE | Diffère |
| Vues admin | `GroupAdminDetailView`, `UsersView`, `TutorPromptsView` | Versions antérieures |

**Arbitrage :** toute description « produit montrable » doit partir de **hugo-hugolucia** uniquement.

---

## 8. Limites et À VÉRIFIER

| Point | Détail | Statut |
|-------|--------|--------|
| Runtime API | `.env` pointe `hugoback.encoors.com`, pas `hugo_back` local | **À VÉRIFIER** |
| Équivalence back distant / local | Flags P0, synthèse, conduct profiles peuvent diverger | **À VÉRIFIER** |
| Streaming SSE | Nécessite support back + CORS ; fallback POST classique prévu | **IMPLÉMENTÉ** côté front |
| `ui-state` indisponible | UI dégradée neutre (`isDegraded`) | **PARTIEL** — démo possible mais panneau vide |
| RLS / multi-tenant prod | Non observable depuis le front seul | **À VÉRIFIER** |
| Déploiement nginx | Compose monorepo sert `frontend/dist`, pas `frontend_1.8/dist` | **AMBIGU** (doc 01) — démo réelle probablement via build dédié ou hébergement séparé |
| Specs Hugo 1.8 | Non utilisées comme preuve ici | **CIBLE** — le code front prime |

**Ce que la démo prouve :** parcours apprenant, consommation `ui-state`, chat (stream ou fallback), actions synthèse/évaluation/trace si le back les expose.

**Ce que la démo ne prouve pas :** comportement exact de `hugo_back` local, couverture tests moteur, config prod, conformité specs 1.8/1.9.

---

## 9. Renvoi

- **Moteur et contrats API côté back :** `02_ETAT_MOTEUR_REEL.md`
- **Écarts doc / code / prod :** `05_ECARTS_DOC_CODE_PRODUIT.md`
- **Préparation cible 1.9 :** `06_PREPARATION_CIBLE_1_9.md`
- **Stack et baselines démo :** `07_RUNTIME_DEMO_REFERENCE.md`
- **Flags et env démo :** `08_FLAGS_ET_ENVIRONNEMENT_DEMO.md`
- **Parcours et scénarios démo :** `09_PARCOURS_DEMO_ET_SCENARIOS.md`
- **Runtime Encoors (inspection HTTP) :** `10_FICHE_RUNTIME_PROD_ENCOORS.md`
- **Géographie workspace :** `01_CARTOGRAPHIE_WORKSPACE_REEL.md`

**Lancement démo (référence) :**

```bash
cd hugo-hugolucia/frontend_1.8
npm install
npm run dev
```

Prérequis : compte valide sur l'API cible ; utilisateur = **learner** des sessions (`learner=request.user` — `views_sessions.py`) et **membre d'au moins un groupe** (`GET /groups/` via `GroupMembership` — `views_groups.py`). Réseau sortant si baseline distante (`hugoback.encoors.com`).

---

*Document 03 — état produit `hugo-hugolucia/frontend_1.8` juin 2026. API distante non interrogée directement.*
