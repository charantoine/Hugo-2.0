# Parcours démo et scénarios — Workspace Hugo

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Public :** CTO, personne qui prépare ou anime une démo — pas un guide développeur backend seul.

---

## 1. Objet du document

Ce document **ne refait pas la spec produit** ni le détail du moteur : il propose un **petit ensemble de parcours de démo réalistes**, alignés sur `hugo-hugolucia/frontend_1.8` et les contrats API existants.

Chaque scénario indique ce qu'il est pertinent de **montrer et de dire** à un client, et ce qu'il vaut mieux **ne pas sur-vendre** (mémoire inter-session non injectée au tour, RAG lexical, etc.). Pour le détail technique : `02_ETAT_MOTEUR_REEL.md`, `03_ETAT_PRODUIT_REEL.md`, `05_ECARTS_DOC_CODE_PRODUIT.md`, `07_RUNTIME_DEMO_REFERENCE.md`, `08_FLAGS_ET_ENVIRONNEMENT_DEMO.md`.

---

## 2. Parcours de démo principal « Apprenant »

### Contexte

**Baseline par défaut (observée) :** front `frontend_1.8` + API `https://hugoback.encoors.com` (doc 07, baseline A).  
**Mode UI :** `prod_showable` (défaut si `VITE_FRONTEND_MODE` absent).  
**Durée indicative :** 12–20 minutes pour un happy path complet.

### Prérequis avant d'ouvrir le navigateur

| Prérequis | Détail | Si manquant |
|-----------|--------|-------------|
| Compte **learner** | Utilisateur connecté = **learner** des sessions créées (`learner=request.user` côté API — `views_sessions.py`) | Sessions 404 ou liste vide si mauvais compte |
| Groupe | **Membre** d'au moins un groupe (`GET /groups/` via `GroupMembership` — `views_groups.py`) | `GET /groups/` vide → création session bloquée |
| Tutor prompt | Liste `GET /hugo/tutor-prompts/` non vide, ou acceptation de créer sans `tutor_prompt_id` | Sélection prompt à l'accueil dégradée |
| Backend cible | Distant (défaut `.env`) ou local (baseline B — §5) | Voir doc 07 / 08 |
| Réseau | Sortant vers l'API si baseline A | Timeouts, login KO |
| LLM (local uniquement) | Ollama ou OVH configuré si baseline B avec chat | Réponses assistant absentes ou lentes |

**Recommandation :** tester login + une session la veille ; consigner le « profil de démo » (doc 08 §5).

### Scénario suggéré (thème AFEST)

Situation type : un technicien décrit un incident sur site, explore les causes, fait le point, puis demande une synthèse. Adapter les formulations au métier du client sans promettre des réponses LLM mot pour mot.

---

#### Étape 1 — Connexion

| | |
|--|--|
| **Route front** | `/login` → redirect `/app` |
| **Endpoints** | `POST /auth/login/` ; `GET /auth/me/` (guard router) |
| **Actions** | Saisir identifiants du compte démo ; vérifier l'arrivée sur l'accueil « Hugo 1.8 - Lucia » |
| **À dire au client** | Hugo s'authentifie en JWT ; l'apprenant n'accède qu'à son parcours, sans écrans d'administration |
| **Ne pas sur-vendre** | Isolation multi-tenant (RLS Postgres) non démontrable depuis le front seul — **À VÉRIFIER** en prod |

---

#### Étape 2 — Accueil et liste des sessions

| | |
|--|--|
| **Route front** | `/app` (`ProdLearnerHomeView.vue`) |
| **Endpoints** | `GET /groups/` ; `GET /hugo/sessions/` ; `GET /hugo/tutor-prompts/` |
| **Actions** | Montrer l'historique des sessions, filtres date/favoris ; optionnel : rouvrir une session existante |
| **À dire au client** | L'apprenant retrouve ses conversations ; le groupe contextualise le parcours (formation, équipe) |
| **Ne pas sur-vendre** | Les libellés de phase dans la liste (`opening` → « Raconter », `exploration` → « Comprendre », etc.) sont un **résumé** ; le panneau de progression utilise un autre découpage visuel (§ étape 4) |

---

#### Étape 3 — Création d'une nouvelle session

| | |
|--|--|
| **Route front** | `/app` → navigation vers `/app/session/:sessionId` |
| **Endpoints** | `POST /hugo/sessions/` (`group` + `tutor_prompt_id` optionnel) |
| **Actions** | Choisir le groupe ; sélectionner un tutor prompt (défaut auto si `is_default`) ; cliquer créer |
| **À dire au client** | Chaque session est ancrée dans un groupe et peut être personnalisée par un prompt tuteur (ton, contexte métier) |
| **Ne pas sur-vendre** | Le choix du prompt n'est pas un « profil conducteur » complet visible côté apprenant — les `TutorConductProfiles` sont surtout côté moteur / mode testeur |

---

#### Étape 4 — Échanges conversationnels (3 à 4 messages)

| | |
|--|--|
| **Route front** | `/app/session/:sessionId` (`ProdLearnerWorkspace.vue` + `HugoProgressPanel.vue`) |
| **Endpoints** | `GET /hugo/sessions/{id}/` ; `GET .../messages/` ; `POST .../messages/stream/` (SSE) ou fallback `POST .../messages/` ; après chaque tour : `GET .../ui-state/?gamification_profile=…` |
| **Actions** | Envoyer 3 à 4 messages progressifs ; après chaque réponse, montrer le panneau de progression |

**Exemple de fil (à adapter) :**

1. **Raconter** — « Hier sur chantier, une armoire a déclenché une alarme alors que le test de continuité était bon la veille. »
2. **Explorer / Comprendre** — « J'ai vérifié les bornes : la terre semblait correcte mais le serrage du conducteur PE était desserré. »
3. **Approfondir / Décider** — « Je me demande si c'est un défaut de serrage récurrent ou un problème de vibration. Qu'est-ce que je devrais contrôler en priorité ? »
4. **Faire le point** — « En résumé, je retiens qu'il faut contrôler le couple de serrage et refaire une mesure après remise en service. »

| | |
|--|--|
| **À dire au client** | Hugo accompagne par étapes ; le panneau reflète la progression via le contrat `ui-state` (scène, quêtes, maturité, boutons synthèse/évaluation) — **calculé côté serveur**, pas recalculé par heuristiques P0 dans le front prod |
| **Ne pas sur-vendre** | Le panneau affiche **3 macro-scènes** (Raconter / Explorer / Synthétiser — `progressionLabels.js`) ; le moteur suit en interne **5 jalons** (Raconter → Comprendre → Décider → Retenir → Transmettre — `ui_state_builder.py`). Ne pas promettre une progression identique à chaque essai : elle dépend du LLM et des flags P0 (legacy par défaut). Mémoire **inter-session** : consolidée après les tours mais **non réinjectée** dans l'orchestrateur au message suivant (doc 02, 05). RAG : sélection **lexicale**, pas vectorielle. |

**Streaming :** si le flux SSE fonctionne, montrer la réponse qui arrive par morceaux ; sinon le fallback POST est silencieux — ne pas insister sur « streaming temps réel » sans vérifier l'API cible (**À VÉRIFIER** sur distant).

---

#### Étape 5 — Synthèse

| | |
|--|--|
| **Route front** | Même session ; bouton dans `HugoProgressPanel` (état `synthesis_button_state` depuis `ui-state`) |
| **Endpoints** | `POST /hugo/sessions/{id}/request-synthesis/` |
| **Actions** | Attendre que le bouton passe de « Continuer la conversation » à « Faire une synthèse » / « Synthèse disponible » ; lancer la synthèse ; lire le résultat dans le workspace |
| **À dire au client** | La synthèse est déclenchée quand le parcours le permet ; le bouton est piloté par le back, pas décoratif |
| **Ne pas sur-vendre** | Qualité et latence dépendent du LLM (Ollama/OVH) ; contenu distant **À VÉRIFIER** vs local. Ne pas citer l'ancien MEMO CTO (« stub synthesis_queued ») — obsolète côté code local (doc 05) |

---

#### Étape 6 — Évaluation, trace et partage (optionnel selon temps)

| Action | Route / UI | Endpoint | Pertinent de montrer ? |
|--------|------------|----------|------------------------|
| **Évaluation** | Bouton panneau progression | `POST .../request-evaluation/` | Oui si le bouton passe à « possible » / « recommandée » |
| **Génération trace** | Bouton dans le workspace prod | `POST .../generate-trace/` | Sur demande — payload trace encore **minimal** côté moteur (doc 05) |
| **Partage tuteur** | Cases à cocher (résumé, preuves, verbatim) | `POST .../share/` + `PATCH` flags | Oui pour montrer la gouvernance du partage |
| **Preuves / traces historiques** | Onglets ou sections si visibles | `GET /learners/traces/`, `GET /learners/evidence/` | Secondaire en démo courte |

| | |
|--|--|
| **À dire au client** | Hugo prépare une trace et peut partager des éléments au tuteur humain, avec contrôle de ce qui est transmis |
| **Ne pas sur-vendre** | Trace `generate-trace` ≠ dossier Qualiopi complet ; exports Felix-ready existent côté back mais **pas** dans le parcours `/app` prod. Évaluation : workflow réel mais validation tuteur hors écran apprenant |

---

#### Étape 7 — Retour accueil

| | |
|--|--|
| **Route front** | `/app` |
| **Actions** | Retour via navigation layout ; montrer la session dans l'historique (éventuellement favori via `PATCH .../sessions/{id}/`) |
| **À dire au client** | Continuité entre sessions ; reprise possible plus tard |
| **Ne pas sur-vendre** | Reprise ≠ mémoire thématique injectée automatiquement dans le prochain tour |

---

## 3. Parcours « Mode testeur / back-office » (optionnel)

### Activation

```bash
# Variables à définir avant npm run dev (non commitées dans le repo)
VITE_FRONTEND_MODE=tester
# Optionnel, pour debug P0 :
VITE_P0_DEBUG_ENABLED=true
```

Redirect après login : `/dashboard` (`TesterLayout`). **Ne pas** laisser ces variables actives pour une démo client standard.

### Scénario technique (15–25 min)

| # | Étape | Route | Endpoints / composants | Intérêt démo |
|---|-------|-------|------------------------|--------------|
| 1 | Dashboard groupes | `/dashboard` | `GET /groups/` ou vues dashboard | Vue d'ensemble organisation |
| 2 | Groupe | `/group/:groupId` | Liste apprenants | Navigation tuteur / admin |
| 3 | Espace apprenant testeur | `/group/:groupId/learner/:learnerId` | `LearnerDetailView.vue` | Chat **sans** masquage prod ; onglets traces, evidence, documents |
| 4 | Debug P0 (si activé) | Même vue | Réponses message avec `turn_state` / `conversation_decision` ; modales si `p0_debug_enabled` | Montrer la **profondeur moteur** — risque de surcharge |
| 5 | Override phase / classifieur | `LearnerDetailView` | `PATCH .../phase/` ; `PATCH .../classifier-config/` | Calibration — **réservé** équipe technique |
| 6 | Tutor prompts | `/tutor-prompts` | CRUD `/hugo/tutor-prompts/` | Personnalisation prompts |
| 7 | Conduct profiles | `/conduct-profiles` | CRUD `/hugo/conduct-profiles/` | Paramètres comportementaux (absent du parcours `/app`) |
| 8 | Référentiels | `/referentials`, `/referentials/import` | `/referentials/` | Import RNCP / référentiel v2 |
| 9 | Admin groupes / biblio | `/groups-admin`, `/groups-admin/:groupId` | Groupes + documents RAG | Upload et indexation (Celery) |
| 10 | Utilisateurs | `/users` | `/users/`, `/admin/users/` | Création / édition — **pas** de suppression complète (doc 05) |
| 11 | Exports | `GroupView` ou `GroupAdminDetailView` | `POST /exports/run/` via `runExportAndDownload()` | CSV/JSON traces — preuve data, pas UX apprenant |
| 12 | Config OVH LLM | `/ovh-llms` | Routes OVH côté back | Admin infra LLM |

### Prudence en démo non technique

| Utile pour | À éviter en démo client |
|------------|-------------------------|
| Prouver que le moteur expose TurnState, décisions, overrides | Ouvrir les modales `turn_state` / `conversation_decision` |
| Montrer CRUD prompts et profils conducteur | Enchaîner 5 écrans admin |
| Démontrer exports et imports référentiels | Parler RAG « vectoriel » ou pgvector |
| Comparer chat testeur vs prod | Laisser `VITE_P0_DEBUG_ENABLED=true` par erreur |

**Message clé :** le parcours `/app` est la **surface produit** ; le mode testeur est l'**atelier de calibration** — même build, layouts différents (`App.vue`).

---

## 4. Ce que la démo prouve / ne prouve pas

| Ce que la démo démontre vraiment | Ce que la démo NE démontre pas |
|-----------------------------------|--------------------------------|
| Parcours apprenant bout-en-bout : login, sessions, chat, retour accueil | Équivalence stricte entre `hugo_back` local et `hugoback.encoors.com` |
| Consommation du contrat `GET /ui-state/` (scène, quêtes, maturité, boutons) | Les 5 jalons internes affichés tous explicitement dans le panneau (3 macro-scènes côté UI) |
| Progression scénique **pilotée par le serveur** ; front prod sans heuristique P0 locale | Stack P0 v17 ou classifieur LLM (flags off par défaut en local ; distant **À VÉRIFIER**) |
| Messagerie avec tentative SSE + fallback POST documenté | Garantie SSE en prod (nginx, CORS, timeouts — **À VÉRIFIER** distant) |
| Boutons synthèse et évaluation **branchés** (`request-synthesis`, `request-evaluation`) | Qualité pédagogique constante des réponses LLM |
| Génération trace et partage tuteur (flags share) | Trace riche type portfolio Qualiopi (payload minimal — doc 05) |
| UX engagement (profil gamification A/B/C, objets persistants cosmétiques) | Que la gamification change la logique pédagogique (cosmétique + contrat back) |
| Consolidation mémoire **écrite** après les tours (effet indirect) | Injection `LearnerThemeMemory` dans le tour suivant (absente — doc 02, 05) |
| RAG utilisé si documents indexés dans le groupe | Recherche **vectorielle** ou embeddings à l'indexation (lexical seulement — doc 02, 05) |
| Exports CSV/JSON en mode testeur | Parcours exports dans `/app` prod |
| Présence middleware RLS dans le code | RLS Postgres effectif en production (**À VÉRIFIER**) |
| Tests unitaires front (3 fichiers utils) | Couverture E2E / Playwright (absente — doc 05) |
| Stack docker monorepo « one command » | `docker-compose` des monorepos sans rattacher `hugo_back` (doc 05) |

---

## 5. Variante « Démo contre API locale » (baseline B)

Si le CTO retient une preuve moteur sur `hugo_back` local (doc 07, baseline B), rejouer le **même parcours §2** avec les ajustements suivants.

### Configuration minimale

| Couche | Réglage |
|--------|---------|
| Back | `cd hugo_back` ; PostgreSQL + migrations ; `python manage.py runserver` (settings `dev` par défaut) |
| Front | `VITE_API_URL=/api` (non commité dans `frontend_1.8` aujourd'hui) ; `npm run dev` — proxy Vite `5173` → `8000` (`vite.config.js`) |
| LLM | Ollama sur `localhost:11434` ou `LLM_PROVIDER_DEFAULT=ovh_ai` + token en env (pas le défaut en dur — doc 08) |
| Données | Créer org, utilisateur apprenant, groupe, au moins un tutor prompt |

### Pièges spécifiques

| Piège | Symptôme | Mitigation |
|-------|----------|------------|
| `.env` distant par défaut | Front appelle Encoors malgré back local | Forcer `VITE_API_URL=/api` avant `npm run dev` |
| Pas de proxy si URL absolue | CORS ou mauvaise cible | Utiliser `/api` + proxy, ou `http://localhost:8000` + CORS dev (`CORS_ALLOW_ALL_ORIGINS=True` en `dev.py`) |
| LLM absent | Timeout, réponses vides | Vérifier Ollama / OVH avant la démo |
| Pas de compte seed | Login OK mais groupes vides | Préparer compte + groupe documentés |
| Redis / Celery / MinIO | Chat OK ; upload biblio ou indexation KO | Limiter la démo au chat si services non montés |
| Double vérité | Démo hier sur distant, aujourd'hui local sans le dire | Consigner baseline dans le profil de démo (doc 08) |

**Ce que cette variante prouve en plus :** comportement du code `hugo_back` du workspace (P0 legacy, flags connus). **Ce qu'elle ne remplace pas :** une fiche runtime prod sur Encoors.

---

## 6. Recommandations finales pour le CTO

**Démo courte (10–15 min, client) :** garder uniquement le parcours §2 étapes 1 à 5 (login → création session → 3 échanges → synthèse **seulement si** `synthesis_button_state` ≠ `locked`). Ne **pas promettre** synthèse ni évaluation en démo courte : les boutons peuvent rester `locked` tant que le parcours n'a pas assez avancé (`ui-state`). Mentionner le panneau de progression ; éviter trace, partage et évaluation sauf boutons déjà « ready ».

**Sur demande uniquement :** mode testeur, modales TurnState, exports, imports référentiels, admin utilisateurs, config OVH. Ces écrans prouvent la profondeur technique mais **cassent le récit produit** si montrés trop tôt.

**Avant toute démo à froid, stabiliser absolument :** (1) compte + groupe + tutor prompt validés sur l'API cible ; (2) baseline documentée (A ou B) ; (3) test login + un message la veille ; (4) si baseline A — accepter que le moteur distant est **À VÉRIFIER** ou obtenir une fiche version/flags Encoors ; (5) si baseline B — Ollama/DB/comptes prêts et `VITE_API_URL` local confirmé ; (6) ne pas activer `VITE_FRONTEND_MODE=tester` ni `VITE_P0_DEBUG_ENABLED` pour une démo client.

**Arbitrage ouvert (doc 06) :** tant que le runtime de référence n'est pas tranché, toute démo « Hugo aujourd'hui » doit **nommer explicitement** la stack utilisée — sans laisser supposer que le distant reflète le repo local.

---

## Renvois

| Sujet | Document |
|-------|----------|
| Routes, composants, endpoints front | `03_ETAT_PRODUIT_REEL.md` |
| Pipeline P0, mémoire, RAG, synthèse | `02_ETAT_MOTEUR_REEL.md` |
| Écarts doc / limites connues | `05_ECARTS_DOC_CODE_PRODUIT.md` |
| Baselines A / B / C | `07_RUNTIME_DEMO_REFERENCE.md` |
| Flags et profil de démo | `08_FLAGS_ET_ENVIRONNEMENT_DEMO.md` |
| Runtime Encoors (CORS, routes) | `10_FICHE_RUNTIME_PROD_ENCOORS.md` |

**Fiche comptes démo :** `11_FICHE_COMPTES_ET_DONNEES_DEMO.md` (à produire) — en attendant, consigner identifiants et résultats de test hors repo (coffre secrets + profil démo `08` §5). **Baseline A :** vérifier origine front vs CORS (doc 10 — `localhost:5173` non autorisé).

---

*Document 09 — parcours démo et scénarios, juin 2026.*
