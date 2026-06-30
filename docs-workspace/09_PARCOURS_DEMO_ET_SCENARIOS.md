# Parcours démo et scénarios — Workspace Hugo

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Public :** CTO, animateur de démo, QA — pas un guide développeur backend seul.  
**Comptes et données :** `11_FICHE_COMPTES_ET_DONNEES_DEMO.md` (fiche complète).

---

## 0. Démarrage rapide — baseline B locale (`localhost:5173`)

Stack **validée** sur l'instance courante (juin 2026) :

| Couche | Réglage |
|--------|---------|
| Back | `cd hugo_back && python manage.py runserver 8000` |
| Front | `cd hugo-hugolucia/frontend_1.8` puis `npm run dev` avec `.env.local` : `VITE_API_URL=/api`, `VITE_FRONTEND_MODE=tester` |
| URL | `http://localhost:5173` |
| API | Proxy `/api` → `http://127.0.0.1:8000` (`vite.config.js`) |

**Comptes « essayer maintenant » (confiance haute) :**

| Objectif | Compte | Mot de passe | Première URL |
|----------|--------|--------------|--------------|
| Admin / onboarding | `demo.superadmin` | `demo-superadmin-2026` | `/dashboard` |
| Apprenant | `smoke_learner` | `smoke-pass-2026` | `/app` |
| Tuteur | `smoke_tutor` | `smoke-pass-2026` | `/app/tutor` |
| Formateur | `smoke_trainer` | `smoke-pass-2026` | `/app/trainer/knowledge` |

Si login échoue : `python manage.py bootstrap_smoke_playwright` puis réessayer les comptes `smoke_*`.  
Détail complet : doc **11** §3–5.

**Parcours bêta testeurs externes (`OF_test_2`) :** `python manage.py bootstrap_demo_test_2` → comptes `*_test_2` / `demo123` — voir doc **11** §4.4 et `seed-strategies.md`.

**Vérification automatisée :** `npm run test:protocol` dans `frontend_1.8` (rapport : `docs-workspace/e2e-protocol-runtime/RAPPORT_E2E_PROTOCOL.md`).

---

## 1. Objet du document

Ce document propose un **catalogue de parcours de démo réalistes**, alignés sur `hugo-hugolucia/frontend_1.8` et les contrats API de `hugo_back`.

Chaque scénario indique :

- **route**, **endpoints**, **actions** ;
- ce qu'il est pertinent de **montrer et de dire** ;
- ce qu'il vaut mieux **ne pas sur-vendre**.

Patron de lecture (méthodo convergence) :

| Rubrique | Contenu |
|----------|---------|
| **Réel confirmé** | Observé code + runtime local documenté |
| **Cible 2.0** | Hors périmètre sauf mention explicite |
| **À VÉRIFIER** | Distant Encoors, prod, ou données non prouvées |

Références techniques : `02_ETAT_MOTEUR_REEL.md`, `03_ETAT_PRODUIT_REEL.md`, `05_ECARTS_DOC_CODE_PRODUIT.md`, `07`–`08`, `11`.

---

## 2. Carte des parcours par rôle

### 2.1 Mode `prod_showable` (démo client — surface produit)

| Rôle | Redirect login | Routes clés | Layout |
|------|----------------|-------------|--------|
| LEARNER | `/app` | `/app`, `/app/session/:id` | `ProdLearnerLayout` |
| TUTOR, COORDO | `/app/tutor` (navigation) | `/app/tutor`, `/app/tutor/group/…/learner/…` | prod |
| TRAINER | `/app/trainer/knowledge` | `/app/trainer/knowledge`, `/app/trainer/library`, `/app/trainer/referentials`, `/app/trainer/elicitation` | prod |

Source : `router/index.js`, `frontendConfig.js` (`resolveAuthenticatedHome` — TRAINER pur → `/app/trainer/knowledge`).

### 2.2 Mode `tester` (démo technique / admin / calibration)

| Rôle | Redirect login | Routes clés | Layout |
|------|----------------|-------------|--------|
| SUPERADMIN, ORGADMIN | `/dashboard` | `/dashboard`, `/users`, `/groups-admin`, `/admin/onboarding`, `/admin/conversation/*`, `/admin/organisations`, `/referentials` (navbar testeur) | `TesterLayout` |
| TUTOR, COORDO | `/dashboard` | `/group/:id`, `/group/:id/learner/:id` (calibration / exports) | tester |
| **TRAINER** | **`/app/trainer/knowledge`** (shell **prod**, pas dashboard) | Hub formateur + `/app/trainer/library`, `/app/trainer/referentials` ; `/dashboard` et `/group/*` restent accessibles manuellement (legacy testeur) | prod (entrée) + tester (legacy) |

**Séparation produit / calibration :** le parcours `/app` est la **surface apprenant** ; le dashboard + `/group/…` est l'**atelier testeur** — ne pas les confondre en démo client (`DOC_RUNTIME_UPDATE_2026-06.md`, wizard juin 2026).

### 2.3 Matrice scénarios ↔ documents

| ID | Scénario | Durée | Compte(s) | Doc § |
|----|----------|-------|-----------|-------|
| **S1** | Apprenant — happy path complet | 12–20 min | `smoke_learner` | §3 |
| **S2** | Apprenant — reprise session préparée | 5–8 min | `smoke_learner` | §4 |
| **S3** | Tuteur — timeline et confidentialité | 8–12 min | `smoke_tutor` + données S1/S2 | §5 |
| **S4** | Formateur — knowledge | 5–10 min | `smoke_trainer` | §6 |
| **S5** | Superadmin — onboarding org (wizard) | 15–20 min | `demo.superadmin` | §7 |
| **S6** | Dashboard testeur vs admin | 5 min | `demo.superadmin` | §8 |
| **S7** | Switch multi-tenant | 5 min | `demo.superadmin` | §9 |
| **S8** | Calibration P0 (équipe technique) | 15–25 min | `demo.superadmin` | §10 |

---

## 3. Scénario S1 — Apprenant happy path (AFEST)

**Réel confirmé :** parcours `/app` implémenté ; contrat `ui-state` consommé côté front prod.  
**Compte :** `smoke_learner` / `smoke-pass-2026` (org Smoke) — ou compte métier **si mot de passe connu** (doc 11 §3.3 : `apprenant_melec_*` sans MDP repo).  
**Mode front :** `prod_showable` (désactiver `tester` pour démo client).  
**Durée :** 12–20 min.

### Prérequis

| Prérequis | Détail | Si manquant |
|-----------|--------|-------------|
| Compte learner | `learner=request.user` sur sessions API | Sessions vides / 404 |
| Groupe | Membre via `GroupMembership` | `GET /groups/` vide |
| Tutor prompt | `GET /hugo/tutor-prompts/` non vide ou création sans `tutor_prompt_id` | Sélection dégradée |
| LLM | Ollama ou OVH selon settings | Réponses assistant absentes |

### Étapes

#### S1.1 — Connexion

| | |
|--|--|
| **Route** | `/login` → `/app` |
| **Endpoints** | `POST /auth/login/` ; `GET /auth/me/` |
| **Actions** | Login `smoke_learner` ; vérifier accueil apprenant |
| **À dire** | JWT, parcours sans écrans admin |
| **Ne pas sur-vendre** | RLS Postgres non démontrable depuis le seul front |

#### S1.2 — Accueil et sessions

| | |
|--|--|
| **Route** | `/app` |
| **Endpoints** | `GET /groups/` ; `GET /hugo/sessions/` ; `GET /hugo/tutor-prompts/` |
| **Actions** | Historique, filtres ; optionnel : rouvrir une session |
| **À dire** | Conversations par groupe de formation |

#### S1.3 — Nouvelle session

| | |
|--|--|
| **Route** | `/app` → `/app/session/:sessionId` |
| **Endpoints** | `POST /hugo/sessions/` |
| **Actions** | Choisir groupe ; posture / prompt ; « Lancer une nouvelle session » |
| **Preuve branchement** | POST 2xx + navigation vers nouvel ID session (E2E : création session) |
| **À dire** | Session ancrée groupe + prompt tuteur |

#### S1.4 — Conversation (3–4 messages)

| | |
|--|--|
| **Route** | `/app/session/:sessionId` |
| **Endpoints** | `GET/POST …/messages/` ; `POST …/messages/stream/` ou fallback POST ; `GET …/ui-state/?gamification_profile=…` |
| **Actions** | Messages progressifs ; montrer panneau progression après chaque tour |

**Exemple de fil (métier melec / AFEST) :**

1. « Hier sur chantier, une armoire a déclenché une alarme… »
2. « J'ai vérifié les bornes : serrage PE desserré. »
3. « Est-ce un défaut récurrent ou vibration ? Que contrôler en priorité ? »
4. « Je retiens : contrôler le couple de serrage après remise en service. »

| | |
|--|--|
| **À dire** | Progression **calculée serveur** (`ui-state`), pas heuristique front prod |
| **Ne pas sur-vendre** | UI = 3 macro-scènes ; moteur = 5 jalons internes. Mémoire inter-session **non injectée** au tour suivant. RAG **lexical** seulement. |

#### S1.5 — Mémoire intra-conversation

| | |
|--|--|
| **UI** | Bouton / panneau « mémoire » si visible |
| **Endpoint** | `GET …/memory-summary/` |
| **Preuve** | E2E lot 8 — appel réseau au clic |
| **À dire** | Résumé gouverné intra-session |
| **Ne pas sur-vendre** | Pas un verbatim complet ; pas mémoire inter-sessions active |

#### S1.6 — Synthèse

| | |
|--|--|
| **UI** | Bouton panneau progression (`synthesis_button_state` depuis `ui-state`) |
| **Endpoint** | `POST …/request-synthesis/` |
| **Actions** | Attendre état « Faire une synthèse » / « Synthèse disponible » ; lancer |
| **Ne pas sur-vendre** | Bouton peut rester `locked` si parcours insuffisant — **ne pas promettre** en démo courte |

#### S1.7 — Évaluation, trace, partage (optionnel)

| Action | Endpoint | Montrer si |
|--------|----------|------------|
| Évaluation | `POST …/request-evaluation/` | Bouton « possible » / « recommandée » |
| Trace | `POST …/generate-trace/` | Temps disponible ; payload encore minimal |
| Partage | `POST …/share/` + flags | Gouvernance tuteur |

#### S1.8 — Retour accueil

| | |
|--|--|
| **Route** | `/app` |
| **À dire** | Continuité historique |
| **Ne pas sur-vendre** | Reprise ≠ mémoire thématique auto-injectée |

---

## 4. Scénario S2 — Apprenant reprise session (démo courte)

**Objectif :** prouver session, posture, `ui-state`, mémoire **sans** créer une session live.  
**Durée :** 5–8 min.  
**Compte :** `smoke_learner` / `smoke-pass-2026`.

| Étape | Action | Preuve |
|-------|--------|--------|
| 1 | Login | `/app` |
| 2 | Ouvrir directement `/app/session/deecbacc-d0b3-4f3c-9cfe-e8bbeb88d0e6` | ID : `smoke-fixtures.json` L7 |
| 3 | Observer bandeau scène + panneau progression | `GET /ui-state/` 200 (E2E lot 8) |
| 4 | Ouvrir panneau mémoire | `GET /memory-summary/` si bouton visible |

**Variantes cluster16 (profils affichage jeune/adulte/pro) :** sessions dans `smoke-fixtures.json` → `cluster16_sessions` (posture `reflective_afest`, `synthesis_eligible: true` sur certaines).

---

## 5. Scénario S3 — Tuteur

**Compte :** `smoke_tutor` / `smoke-pass-2026`.  
**Durée :** 8–12 min.  
**Prérequis :** association `smoke_tutor` ↔ `smoke_learner` (bootstrap L139-144).

| Étape | Route | Endpoints | À montrer | Preuve / limite |
|-------|-------|-----------|-----------|-----------------|
| 1 | `/login` → `/app/tutor` | auth | Liste apprenants liés | E2E lot 10 : heading « Espace tuteur » |
| 2 | Ouvrir apprenant associé | `/app/tutor/group/…/learner/…` | Timeline | Éléments **partagés** visibles |
| 3 | Confidentialité | — | — | Verbatim `VERBATIM_SECRET_SMOKE_DO_NOT_SHOW` **absent** pour le tuteur (E2E lot 10) |
| 4 | Synthèses / traces partagées | GET learners traces | Si flags `share_*` activés côté apprenant | Non partagé = caché |

**Ne pas sur-vendre :** le tuteur ne voit pas les apprenants non associés ; pas d'accès admin IAM.

**Comptes melec (`tuteur_melec_*`) :** utilisables seulement si mot de passe fourni hors repo (doc 11 §3.3).

---

## 6. Scénario S4 — Formateur

**Compte :** `smoke_trainer` / `smoke-pass-2026`.  
**Durée :** 5–10 min.

| Étape | Route | Actions | Endpoints |
|-------|-------|---------|-----------|
| 1 | Login → `/app/trainer/knowledge` | Vérifier **absence** d'atterrissage sur dashboard testeur / bac pro melec | — |
| 2 | Hub knowledge | Liens **Bibliothèque**, **Référentiels**, **Atelier d'élicitation** | — |
| 3 | `/app/trainer/referentials` | Liste + import (shell prod) ; **« Retour orchestrateur »** → hub | GET `/referentials/` |
| 4 | Topbar | **« Chat apprenant »** à droite → `/app` ; **« Espace formateur »** → hub | — |
| 5 | Validation item | Valider un critère déclaré | POST validate (smoke item id `1`) |
| 6 | (Optionnel) `/app/trainer/library` ou `/app/trainer/elicitation` | Bibliothèque / élicitation ; **« Retour orchestrateur »** visible | GET `/groups/`, library |

**Limite connue :** config référentiel **par groupe** (`/group/:id/referential`) — shell testeur uniquement ; non démontrée dans ce scénario prod.

**Réel confirmé :** smoke Playwright `test_smoke_trainer.spec.ts` ; `resolveAuthenticatedHome` (`frontendConfig.test.js`). Commande E2E canonique : `npm run test:e2e`.

---

## 7. Scénario S5 — Superadmin onboarding (wizard + admin)

**Compte :** `demo.superadmin` / `demo-superadmin-2026`.  
**Organisation :** Demo Hugo Org.  
**Groupe pivot démo données :** bac pro melec (`29e5cdb9-de89-49b3-a36e-53b4b9bbbc50`).  
**Mode :** `tester`.  
**Durée :** 15–20 min.

### Fil conducteur recommandé (post-refonte juin 2026)

```text
/dashboard  →  /admin/onboarding  →  /users  →  /groups-admin  →  /groups-admin/:id
     →  /admin/conversation/learner/profiles  →  /group/:id/referential
```

| Étape | Route | Libellé / action à prouver | Endpoint / effet | Statut runtime |
|-------|-------|---------------------------|------------------|----------------|
| 1 | `/dashboard` | Cartes admin vs « Raccourci démo » séparé | `GET /groups/` | **OK** — E2E lot 3 |
| 2 | `/admin/onboarding` | « Organisation active : Demo Hugo Org » ; « Groupe à configurer » | `GET /groups/`, `GET /users/` | **OK** — E2E lot 2 |
| 2b | `?groupId=` | Pré-sélection groupe | query param | **OK** |
| 2c | Lien « Créer un groupe » | → `/groups-admin` | navigation | **OK** |
| 3 | `/users` | Création compte | `POST /users/` | **OK** QA 23/06 |
| 4 | `/groups-admin` | Création groupe | `POST /groups/` | **OK** E2E lot 4 |
| 5 | `/groups-admin/:id` | Cohorte, profil global, référentiel | `GET /members/` | **OK** E2E lot 4 |
| 6 | `/admin/conversation/learner/profiles` | Profils globaux apprenant | CRUD profils | **Partiel** — scaffold lot 6 |
| 7 | `/group/:id/referential` | Rattachement RNCP38878 | référentiels | **À VÉRIFIER** lot 7 |

**Messages clés :**

- Le wizard est **scoped organisation** ; le dropdown « Groupe à configurer » change la cible réelle (plus de « Groupe de référence » implicite bac pro).
- Le **raccourci démo** dashboard (`data-testid="dashboard-tester-canonical"`) mène vers `/group/:id` — **pas** le wizard.

Sources : `WIZARD_ORG_GROUP_UPDATE_2026-06-26.md`, `VERIF_COHERENCE_SUPERADMIN_2026-06-26.md`, E2E lots 1–4.

---

## 8. Scénario S6 — Dashboard testeur vs logique produit

**Compte :** `demo.superadmin`.  
**Durée :** 5 min.  
**Objectif :** montrer la **séparation** calibration / produit.

| Zone UI | Rôle réel | Route au clic | Ne pas dire |
|---------|-----------|---------------|-------------|
| Section Administration | IAM, groupes, wizard | `/users`, `/groups-admin`, `/admin/onboarding` | « C'est l'apprenant » |
| Section « Raccourci démo » | Accès rapide testeur chat debug | `/group/:groupId` | « C'est l'onboarding admin » |
| Carte bac pro melec (canonique) | Groupe réel + pivot testeur | `/group/29e5cdb9-…` | « Groupe unique implicite du wizard » |

**Preuve :** E2E lot 3 — texte « Raccourci démo », clic → URL `/group/`, pas `/admin/onboarding`.

---

## 9. Scénario S7 — Multi-tenant (SUPERADMIN)

**Compte :** `demo.superadmin`.  
**Durée :** 5 min.

| Étape | Action | Assertion |
|-------|--------|-----------|
| 1 | `/groups-admin` avec Demo Hugo Org | Liste contient bac pro melec |
| 2 | Switch `#tenant-switcher` → Smoke Playwright Org | Bannière « Organisation active : Smoke Playwright Org » |
| 3 | Recharger `/groups-admin` | bac pro melec **absent** (pas de fuite données) |
| 4 | `/admin/onboarding` | Wizard scoped nouvelle org ; pas de « Groupe de référence » |

**Preuve :** E2E lot 1 PASS.  
**Données :** 6 orgs sur instance courante (`protocol-preconditions.json`).

---

## 10. Scénario S8 — Mode testeur / calibration P0

**Activation (équipe technique uniquement) :**

```bash
VITE_FRONTEND_MODE=tester
VITE_P0_DEBUG_ENABLED=true   # optionnel — modales TurnState
```

**Compte :** `demo.superadmin` → `/group/:groupId/learner/:learnerId`.

| Étape | Route | Intérêt | Risque démo client |
|-------|-------|---------|-------------------|
| Chat sans masquage prod | `/group/…/learner/…` | Voir payloads debug | Surcharge cognitive |
| Modales P0 | idem si flag | TurnState, décisions | Expose internes |
| Overrides phase | PATCH phase / classifier | Calibration | Hors produit |
| Exports | `POST /exports/run/` | Preuve data | Hors parcours `/app` |
| Tutor prompts / conduct | `/tutor-prompts`, `/conduct-profiles` | Expert | Navbar masquée — accès hub |

**Réel confirmé :** pas de debug P0 sur `/app` apprenant standard (E2E lot 12).  
**Ne jamais** laisser `VITE_P0_DEBUG_ENABLED=true` pour une démo client.

---

## 11. Matrice « libellé → fonction » (démo)

| Libellé visible | Action attendue | Endpoint / preuve | Verdict attendu |
|-----------------|-----------------|-------------------|-----------------|
| Organisation active : {nom} | Scope données liste | `GET /groups/` header org | OK si listes changent au switch |
| Groupe à configurer | Change cible wizard | sélecteur `wizard-group-select` | OK |
| Créer un groupe | Navigation admin | href `/groups-admin` | OK |
| Raccourci démo | Testeur groupe | `/group/:id` | OK — séparé wizard |
| Lancer une nouvelle session | Crée session | `POST /hugo/sessions/` | OK |
| Faire une synthèse | Lance synthèse | `POST …/request-synthesis/` | OK si bouton non locked |
| Évaluation possible / recommandée | Lance évaluation | `POST …/request-evaluation/` | OK si état métier |
| Préparer une trace | Génère trace | `POST …/generate-trace/` | OK si disponible |
| Options partage | Flags share | `POST …/share/` | OK |

Source protocole : `tests_playwright/e2e/protocol/`, rapport `e2e-protocol-runtime/`.

---

## 12. Ce que la démo prouve / ne prouve pas

| Démontre vraiment | Ne démontre pas |
|-------------------|-----------------|
| Parcours apprenant login → session → chat → `ui-state` | Équivalence stricte local ↔ Encoors |
| Boutons synthèse / évaluation **branchés** si état ready | Qualité pédagogique LLM constante |
| Mémoire intra-session via `memory-summary` | Injection mémoire inter-session au tour suivant |
| Confidentialité tuteur (non partagé caché) | Portfolio Qualiopi complet |
| Wizard org-scoped + switch multi-tenant | RAG vectoriel |
| Séparation raccourci démo / admin | Comptes melec sans MDP documenté |
| RAG lexical si docs indexés | SSE garanti en prod distante |

---

## 13. Variante baseline A — API distante Encoors

Si `VITE_API_URL=https://hugoback.encoors.com` (défaut `.env.development` commité) :

| Aspect | Statut |
|--------|--------|
| Comptes | **À VÉRIFIER** — pas de fiche centralisée ; comptes locaux non garantis |
| CORS `localhost:5173` | **Bloqué** selon doc 10 |
| Flags P0 / LLM | **À VÉRIFIER** |
| Usage | Démo produit **si** comptes valides sur Encoors + front déployé autorisé |

Rejouer scénarios S1–S7 en **nommant explicitement** la baseline A. Ne pas présenter comme preuve du `hugo_back` local.

---

## 14. Recommandations CTO

### Démo client 10–15 min

1. Mode `prod_showable`.
2. **S2** (reprise session smoke) ou **S1** étapes 1–4 sans promettre synthèse.
3. Comptes : `smoke_learner` (+ optionnel `smoke_tutor` pour S3 en fin).
4. Ne pas ouvrir dashboard testeur ni modales P0.

### Démo onboarding admin 15–20 min

1. Mode `tester`.
2. **S5** + **S7** si temps.
3. Compte `demo.superadmin`, org Demo Hugo Org, groupe bac pro melec.

### Démo technique 25–40 min

1. Enchaîner **S5** → **S1** (créer session apprenant smoke) → **S3** → **S8** (extrait calibration).

### Avant toute démo à froid

1. Checklist doc **11** §7.
2. `npm run test:protocol` ou login manuel superadmin + learner.
3. Documenter baseline (B locale vs A distant) dans le compte-rendu.
4. Vérifier Ollama si chat live.

---

## 15. Renvois

| Sujet | Document |
|-------|----------|
| Comptes, MDP, IDs, bootstrap | **`11_FICHE_COMPTES_ET_DONNEES_DEMO.md`** |
| Routes et composants | `03_ETAT_PRODUIT_REEL.md` |
| Moteur P0, mémoire, RAG | `02_ETAT_MOTEUR_REEL.md` |
| Écarts | `05_ECARTS_DOC_CODE_PRODUIT.md` |
| Baselines | `07_RUNTIME_DEMO_REFERENCE.md` |
| Flags | `08_FLAGS_ET_ENVIRONNEMENT_DEMO.md` |
| Encoors | `10_FICHE_RUNTIME_PROD_ENCOORS.md` |
| Preuves E2E | `e2e-protocol-runtime/RAPPORT_E2E_PROTOCOL.md` |

---

*Document 09 — parcours démo et scénarios complets. Dernière révision : juin 2026 — complété avec fiche 11, scénarios S1–S8, baseline locale `localhost:5173`.*
