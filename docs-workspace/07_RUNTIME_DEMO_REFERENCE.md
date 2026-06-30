# Runtime démo — référence

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Fichier :** `docs-workspace/07_RUNTIME_DEMO_REFERENCE.md`  
**Objet :** décrire uniquement la ou les stack(s) **réellement utilisables pour les démos** Hugo — pas la cible idéale, pas le backlog 1.9.

---

## 1. Titre et objet

Ce document fixe quelle combinaison front/back sert de référence quand on « montre Hugo » : il sépare ce qui est **observé** dans le workspace (fichiers, `.env`, code) de ce qui est **supposé** ou **non inspecté** (API distante).

Il explicite la distinction **démo produit** (parcours `/app`, UX, contrats `ui-state`) vs **preuve moteur** (P0, flags, RLS, comportement `hugo_back` local). Il ne remplace pas la description du moteur ou du produit : voir `02_ETAT_MOTEUR_REEL.md` et `03_ETAT_PRODUIT_REEL.md`. Les flags et variables d'environnement détaillés sont dans `08_FLAGS_ET_ENVIRONNEMENT_DEMO.md`.

Tout ce qui relève de `https://hugoback.encoors.com` reste **À VÉRIFIER** (runtime non inspecté dans le workspace local).

---

## 2. Baselines possibles pour les démos

| Baseline | Description | Avantages | Risques / inconnues | Statut |
|----------|-------------|-----------|---------------------|--------|
| **A — Front 1.8 + API distante** | `hugo-hugolucia/frontend_1.8` en `npm run dev` ou build prod ; `VITE_API_URL=https://hugoback.encoors.com` | Lançable **sans** `hugo_back` local ; correspond aux `.env` commités ; démo rapide si compte valide sur l'API distante | État moteur **non prouvé** localement ; version P0, flags, synthèse/éval, RLS, CORS/SSE → **À VÉRIFIER** ; dépendance réseau et disponibilité Encoors | **RECOMMANDÉ** pour démo **produit** publique (sous réserve comptes) |
| **B — Front 1.8 + `hugo_back` local** | Front avec `VITE_API_URL=/api` (proxy Vite) ou URL locale ; API via `python manage.py runserver` (settings `dev`) | Preuve alignée sur le code du workspace ; contrôle flags P0, données, logs | Prérequis : PostgreSQL, Redis, MinIO, LLM selon parcours ; **pas** documenté comme stack « officielle » unique ; CORS/proxy à configurer ; comptes/groupes à créer manuellement | **OPTIONNEL** pour démo **moteur** / calibration ; baseline technique, pas encore cadrée deploy |
| **C — Combiné** | A pour démos externes / stakeholders ; B pour validation dev / écarts doc-code | Sépare « ce qu'on montre » et « ce qu'on développe » | Risque de **double vérité** si on ne dit pas quelle baseline est en jeu ; écarts local ↔ distant non documentés (doc 05 §6) | **RECOMMANDÉ** comme **stratégie d'usage**, pas comme une seule stack technique |

**Décision humaine requise :** quelle baseline est la **référence officielle** pour dire « Hugo aujourd'hui » (doc 06 §3) — ce document recommande **A pour la démo produit**, **B pour la preuve moteur**, sans les fusionner sans fiche d'écarts.

---

## 3. Stack « front démo » (`hugo-hugolucia/frontend_1.8`)

### Observé dans le workspace

| Élément | Détail | Source |
|---------|--------|--------|
| Lancement dev | `npm run dev` (Vite, port 5173 typique) | `package.json`, `03_ETAT_PRODUIT_REEL.md` |
| Lancement build | `npm run build` → `dist/` | `package.json` |
| API par défaut | `VITE_API_URL=https://hugoback.encoors.com` | `.env.development`, `.env.production` |
| Mode UI | `VITE_FRONTEND_MODE` absent → `prod_showable` ; redirect `/app` | `frontendConfig.js` |
| Flags engagement | `VITE_ENGAGEMENT_UI_ENABLED`, `VITE_SCENE_PROGRESS_ENABLED`, `VITE_GAMIFICATION_PROFILE` (défauts `true` / `B`) | `frontendConfig.js` |
| Layout prod | `meta.layout: 'prod'` → `ProdLearnerLayout` | `router/index.js`, `App.vue` |
| Fichiers clés | `src/router/index.js`, `src/utils/frontendConfig.js`, `src/components/learner/ProdLearnerWorkspace.vue`, `src/api/client.js` | doc 03 |

### Ce que le front attend de l'API

| Besoin | Endpoints / comportement | Obligatoire démo ? |
|--------|--------------------------|-------------------|
| Auth JWT | `POST /auth/login/`, `GET /auth/me/`, refresh sur 401 | **Oui** |
| Groupes / session | `GET /groups/`, `POST /hugo/sessions/`, `GET/PATCH /hugo/sessions/{id}/` | **Oui** |
| Chat | `GET/POST .../messages/` ; préférence `POST .../messages/stream/` (SSE) avec fallback POST | **Oui** (fallback si stream indisponible) |
| Contrat produit | `GET .../ui-state/?gamification_profile=…` | **Oui** pour panneau progression non dégradé |
| Actions | `POST .../request-synthesis/`, `request-evaluation/`, `generate-trace/`, `share/` | Non bloquant démo minimale ; attendus démo « complète » |
| Tutor prompts | `GET /hugo/tutor-prompts/` (création session) | **Oui** si sélection prompt à l'accueil |
| CORS | Front sur autre origine que l'API (distant ou `:5173` → `:8000`) | **Oui** — config côté API **À VÉRIFIER** pour distant |
| SSE | `Content-Type: text/event-stream` ; nginx timeout si prod (route présente dans hugolucia `deploy/nginx`, absente main) | **À VÉRIFIER** sur API distante ; fallback POST documenté front |

### Prérequis métier pour une démo qui ne casse pas

- Compte **apprenant** (ou rôle autorisé sur parcours `/app`) valide sur l'API cible.
- Au moins un **groupe** associé à l'utilisateur.
- **Tutor prompts** accessibles (liste non vide ou création session sans `tutor_prompt_id`).
- Réseau sortant si baseline A.

**Non observé dans le repo :** comptes de démo documentés, seed, `.env.example` front avec profils préremplis.

---

## 4. Stack « back démo » locale (`hugo_back`)

### Observé

| Élément | Détail |
|---------|--------|
| Exposition API minimale | `python manage.py runserver` ; `DJANGO_SETTINGS_MODULE=config.settings.dev` par défaut (`manage.py`, `Dockerfile`) |
| Image Docker | `Dockerfile` : `runserver 0.0.0.0:8000`, settings `dev` |
| Settings prod fichier | `config/settings/production.py` existe mais `DEBUG = True` (écart doc 05) — **non recommandé** comme référence démo sans revue |
| Flags P0 (défaut local) | `HUGO_P0_V17_ENABLED=false`, `HUGO_P0_CLASSIFIER_ENABLED=false` — détail dans `02_ETAT_MOTEUR_REEL.md` et `08_FLAGS_ET_ENVIRONNEMENT_DEMO.md` |
| Surface API | Préfixes `/auth/`, `/hugo/`, `/groups/`, etc. — `config/urls.py` |

### Pourquoi `DEPLOY_S0.md` et `docker-compose.yml` (monorepos) ne suffisent pas

| Doc / fichier | Problème pour baseline démo |
|---------------|----------------------------|
| `hugo-hugolucia/docker-compose.yml` | `build: context: ./backend` alors que `backend/` est **vide** (doc 01, 05) |
| `DEPLOY_S0.md` | Suppose stack Django dans `./backend` + `frontend/dist`, pas `hugo_back` ni `frontend_1.8/dist` |
| Nginx monorepo | Monte `./frontend/dist`, pas `frontend_1.8/dist` (doc 01) |
| Moteur réel | Code dans `hugo_back/`, **découplé** des monorepos |

### Ce qui manque pour une baseline locale « officielle »

- Procédure unique documentée : DB + env + `hugo_back` + front avec `VITE_API_URL=/api` (`frontend_1.8/vite.config.js` expose déjà un proxy `/api` → `:8000` ; il faut **changer `.env`** — observé : 1.8 commité pointe distant, pas `/api`).
- Alignement **front 1.8 → back local** : non configuré par défaut dans les `.env` commités de `frontend_1.8`.
- Comptes seed, MinIO, Redis, Celery, LLM : dépend du parcours démo (chat seul vs RAG vs uploads).
- Décision CTO : rattacher `hugo_back` au monorepo ou garder 3 dossiers (doc 06 §3).

**Conclusion :** stack B **techniquement possible** mais **non cadrée** comme référence démo dans le workspace actuel.

---

## 5. Lien avec l'API distante (`https://hugoback.encoors.com`)

### Connu (observé dans le workspace)

| Fait | Preuve |
|------|--------|
| Front 1.8 cible cette URL par défaut | `hugo-hugolucia/frontend_1.8/.env.development`, `.env.production` |
| Client HTTP | `api/client.js` : `baseURL = import.meta.env.VITE_API_URL` |
| Streaming | `fetchWithAuth` vers `/hugo/sessions/.../messages/stream/` |
| Docs 02–06 (avant doc 10) | API distante non interrogée — voir désormais `10_FICHE_RUNTIME_PROD_ENCOORS.md` |

### Inconnu → **À VÉRIFIER**

| Point | Pourquoi ça compte pour la démo |
|-------|-------------------------------|
| Commit / version déployée vs `hugo_back` local | Écarts doc 05 peuvent être résolus en local mais pas en prod |
| `HUGO_P0_V17_ENABLED`, classifieur P0, phase classifier | Comportement conversationnel visible en démo |
| Synthèse / évaluation (LLM réel vs fallback) | Boutons prod branchés côté front ; qualité réponse **À VÉRIFIER** |
| SSE supporté (nginx, CORS, timeouts) | Sinon fallback POST silencieux |
| RLS Postgres effectif | Non observable depuis le front |
| `DEBUG`, token OVH, settings prod | Sécurité / coûts — hors démo fonctionnelle mais gouvernance |
| Données et comptes sur l'instance | Démo reproductible ou non |

### Ce qu'une démo contre l'API distante prouve / ne prouve pas

| Prouve (si parcours OK) | Ne prouve pas |
|-------------------------|---------------|
| Parcours produit `/app` : login, session, chat, `ui-state`, UX engagement | Équivalence avec `hugo_back` local |
| Contrats API consommés par le front (doc 03) | Flags P0, v17, injection mémoire, RAG vectoriel |
| Acceptabilité démo stakeholder « comme en prod » | Stack docker monorepo, `DEPLOY_S0`, chemins `backend/apps/` |
| Disponibilité service Encoors au moment T | Couverture tests, Playwright, RLS audit |

---

## 6. Synthèse et recommandations

**Référence démo produit aujourd'hui :** baseline **A** — `hugo-hugolucia/frontend_1.8` + `https://hugoback.encoors.com`, car c'est la seule stack **observée comme prête à l'emploi** sans monter `hugo_back` (`.env` commités, doc 03).

**Référence preuve moteur :** baseline **B**, mais elle exige travail d'intégration (env front, DB, comptes) non formalisé dans le repo.

Avant de présenter une démo comme preuve de l'**état moteur local**, il faut au minimum : (1) trancher le **runtime de référence** (doc 06) ; (2) produire une **fiche runtime prod** (version, flags) ou exécuter la démo en **B** avec le même front ; (3) ne pas s'appuyer sur `MEMO_CTO` ou audits mai 2026 (doc 05).

**Le CTO doit trancher :** baseline officielle unique vs stratégie **C** ; officialisation de **B** (procédure + `.env` 1.8 local) ; et si la démo vendue engage le **code `hugo_back` du workspace** ou seulement le **service distant**.

---

## Renvois

| Sujet | Document |
|-------|----------|
| Moteur, flags, API | `02_ETAT_MOTEUR_REEL.md` |
| Produit, parcours, endpoints front | `03_ETAT_PRODUIT_REEL.md` |
| Écarts local / distant / monorepo | `05_ECARTS_DOC_CODE_PRODUIT.md` |
| Décisions avant 1.9 | `06_PREPARATION_CIBLE_1_9.md` |
| Flags et variables d'environnement démo | `08_FLAGS_ET_ENVIRONNEMENT_DEMO.md` |
| Parcours et scénarios démo | `09_PARCOURS_DEMO_ET_SCENARIOS.md` |
| Inspection HTTP Encoors | `10_FICHE_RUNTIME_PROD_ENCOORS.md` |
| Géographie workspace | `01_CARTOGRAPHIE_WORKSPACE_REEL.md` |

---

*Document 07 — runtime démo, juin 2026. API distante non inspectée ; statuts À VÉRIFIER inchangés.*
