# Flags et environnement démo — Workspace Hugo

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`

---

## 1. Objet du document

Cette fiche recense les **flags et variables d'environnement** qui modifient le comportement observable en **démo** (backend Django `hugo_back`, front `frontend_1.8`). Elle vise à rendre les démos **reproductibles** : savoir quoi activer, quoi éviter, et quel effet attendre sur le parcours apprenant ou testeur.

Ce n'est **pas** une spec Hugo 1.9 ni un guide d'installation : c'est un **état réel** déduit du code et des `.env` commités, complété par `02_ETAT_MOTEUR_REEL.md`, `03_ETAT_PRODUIT_REEL.md` et `05_ECARTS_DOC_CODE_PRODUIT.md`. Pour le choix de stack (local vs distant), voir `07_RUNTIME_DEMO_REFERENCE.md`.

Tout ce qui concerne l'API déployée `https://hugoback.encoors.com` est marqué **À VÉRIFIER** : runtime non inspecté dans ce workspace.

---

## 2. Tableau des flags BACKEND pertinents

**Référence locale par défaut :** `manage.py` → `config.settings.dev` (`dev.py` : `DEBUG=True`, `CORS_ALLOW_ALL_ORIGINS=True`).  
**Valeurs « défaut local »** = `base.py` si non surchargées par env, avec module **dev** actif.

| Nom | Fichier source | Défaut local (observé) | Effet concret en démo | Risque si mal configuré | Démo recommandé |
|-----|----------------|------------------------|------------------------|-------------------------|-----------------|
| `HUGO_P0_V17_ENABLED` | `config/settings/base.py` L182 | `false` | `false` → pipeline P0 **legacy** ; `true` → stack v17 (TurnState/decision/prompt/guardrails v17) | Comportement conversationnel différent, tests non alignés par défaut | **OFF** (stable, = code testé par défaut) — **À DÉCIDER** si démo « v17 » |
| `HUGO_P0_CLASSIFIER_ENABLED` | `base.py` L178 | `false` | `false` → heuristique seule ; `true` → surclassement LLM partiel des champs P0 | Latence, coût LLM, variabilité des tours | **OFF** pour démo prévisible |
| `HUGO_PHASE_CLASSIFIER_ENABLED` | `base.py` L174 | `true` | Classifieur LLM pour progression de **phase** | Appels LLM supplémentaires ; échec silencieux → fallback phase | **ON** (défaut code) — **À DÉCIDER** si démo sans LLM |
| `HUGO_PHASE_CLASSIFIER_MAX_TOKENS` | `base.py` L175 | `48` | Limite tokens classifieur phase | Réponses tronquées si trop bas | Laisser défaut |
| `HUGO_PHASE_CLASSIFIER_MIN_CONFIDENCE` | `base.py` L176 | `0.60` | Seuil d'acceptation classifieur phase | Phase instable si trop bas | Laisser défaut |
| `HUGO_P0_CLASSIFIER_MAX_TOKENS` | `base.py` L179 | `180` | Limite tokens classifieur P0 (si activé) | — | N/A si classifieur OFF |
| `HUGO_P0_CLASSIFIER_MIN_CONFIDENCE` | `base.py` L180 | `0.60` | Seuil classifieur P0 (si activé) | — | N/A si classifieur OFF |
| `DEBUG` | `base.py` L50 ; **`dev.py` L4 = `True`** | `True` en dev | Pages d'erreur détaillées, `HUGO_DEBUG_TRACING` peut suivre | Fuite d'infos en démo publique | **OFF** en prod ; **ON** acceptable en local privé |
| `HUGO_DEBUG_TRACING` | `base.py` L171 | `true` si `DEBUG` else `false` | Traçage prompt/LLM dans payloads debug | Verbosité, données sensibles dans traces | **OFF** démo client |
| `ENABLE_EXTERNAL_LLM` | `base.py` L170 | `true` | Autorise appels LLM externes | Chat/synthèse/éval inopérants si `false` sans fallback | **ON** si démo conversationnelle |
| `LLM_PROVIDER_DEFAULT` | `base.py` L169 | `ollama` | Provider par défaut (`ollama` ou `ovh_ai`) | Mauvais endpoint si Ollama absent | **ollama** en local si Ollama up — **À DÉCIDER** |
| `LLM_BASE_URL` | `base.py` L167 | `http://localhost:11434` | URL Ollama | Pas de réponse assistant si service down | Vérifier service avant démo |
| `LLM_MODEL` | `base.py` L168 | `mistral` | Modèle Ollama | Qualité/latence variables | Laisser défaut ou documenter |
| `OVH_AI_BASE_URL` | `base.py` L185 | endpoint OVH Kepler | Base URL API OVH | — | Si provider OVH |
| `OVH_AI_MODEL` | `base.py` L186 | `Llama-3.1-8B-Instruct` | Modèle OVH | — | Si provider OVH |
| `OVH_AI_TOKEN` | `base.py` L187 | **JWT en dur** (fallback) | Auth OVH AI | **Sécurité** ; quota ; révocation | **Ne pas** s'appuyer sur le défaut — env prod propre |
| `SECRET_KEY` | `base.py` L49 | `change-me-in-production` | Sessions JWT | Compromission si défaut en prod | Env unique par environnement |
| `CORS_ALLOW_ALL_ORIGINS` | `dev.py` L6 | `True` (dev) | Autorise front `:5173` → API | Trop permissif en prod | **ON** dev local ; liste blanche en prod |
| `CORS_ALLOWED_ORIGINS` | `production.py` L7–10 | `http://localhost:8080` (défaut prod file) | Origines autorisées | Front bloqué si URL démo absente | Inclure origine front réelle |
| `DJANGO_SETTINGS_MODULE` | `manage.py`, `Dockerfile` | `config.settings.dev` | Jeu de settings chargé | `production.py` a encore `DEBUG=True` (L5) — écart doc 05 | **dev** pour local ; prod **à revoir** |
| `DATABASE_URL` | `base.py` L107 | `postgresql://…localhost…` | Persistence | Démo vide ou erreur 500 | DB + migrations OK |
| `CELERY_BROKER_URL` | `base.py` L160 | `redis://localhost:6379/0` | Tâches async (index docs) | Indexation biblio lente/échouée | Redis si démo RAG upload |
| `MINIO_*` / `AWS_*` | `base.py` L147–157 | MinIO local | Stockage evidence/exports | Upload preuves KO | MinIO si démo evidence |

**Override par session/groupe (observé, pas env global) :**

| Mécanisme | Source | Effet démo |
|-----------|--------|------------|
| `Group.llm_backend` | `apps/referentials/models.py` | `OLLAMA` vs `OVH_AI` pour le groupe de la session |
| `p0_classifier_*` sur session | `p0_classifier.py` `resolve_p0_classifier_runtime_config` | Peut activer classifieur P0 **par session** même si flag global off — **risque démo** si session héritée d'une config de calibration |

**Attention démo :** même avec `HUGO_P0_CLASSIFIER_ENABLED=false`, une session ou un groupe peut activer le classifieur P0 ou forcer `OVH_AI` via `Group.llm_backend` — vérifier la session utilisée pour la démo.

---

## 3. Tableau des variables FRONTEND pertinentes

**Référence :** `hugo-hugolucia/frontend_1.8/src/utils/frontendConfig.js`  
**`.env` commités (observé) :** seule `VITE_API_URL=https://hugoback.encoors.com` — autres vars = **défauts code**.

| Nom | Fichier source | Défaut (si absent .env) | Effet démo apprenant (`prod_showable`) | Effet mode `tester` | Démo client recommandé |
|-----|----------------|-------------------------|----------------------------------------|---------------------|------------------------|
| `VITE_API_URL` | `.env.development`, `.env.production` ; `api/client.js` L7 | **`https://hugoback.encoors.com`** (fichier) ; sinon `/api` | Cible de toutes les requêtes API | Idem | **Distant** = défaut repo ; **local** = `/api` + proxy ou URL `:8000` |
| `VITE_FRONTEND_MODE` | `frontendConfig.js` L21 | `prod_showable` | Redirect `/` → `/app`, layout prod | `tester` → `/dashboard`, layout testeur, écrans admin | **`prod_showable`** ou absent |
| `VITE_ENGAGEMENT_UI_ENABLED` | L22 | `true` | Affiche panneau progression (`HugoProgressPanel`) | Idem si routes prod | **ON** |
| `VITE_SCENE_PROGRESS_ENABLED` | L23 | `true` | Barre / étapes de scène | Idem | **ON** |
| `VITE_PERSISTENT_OBJECTS_ENABLED` | L24 | `true` | Objets persistants depuis `ui-state` | Idem | **ON** |
| `VITE_SYMBOLIC_REWARDS_ENABLED` | L25 | `true` | Récompenses symboliques cosmétiques | Idem | **ON** (ou OFF si démo sobre) |
| `VITE_P0_DEBUG_ENABLED` | L26 | `false` | Sans effet en prod | `true` + `tester` → modales TurnState (`LearnerDetailView.vue`) | **OFF** démo client |
| `VITE_GAMIFICATION_PROFILE` | L27 | `B` | Thème A/B/C (barres, badges, quêtes) ; passé à `GET .../ui-state/` | Idem | **`B`** (équilibre) — **À DÉCIDER** |
| `VITE_LEARNER_UI_V2` | L23 | `true` | Layout apprenant v2 (fil central, sidebar droite, sélecteurs groupe/profil masqués) | Idem sur `/app*` | **`true`** (défaut juin 2026) — `false` = layout legacy |

**Proxy Vite (local back, non .env) :** `frontend_1.8/vite.config.js` — `/api` → `http://localhost:8000` (utile seulement si `VITE_API_URL=/api`). Le front **testeur** (`frontend/`) a `.env.development` avec `VITE_API_URL=/api` ; **frontend_1.8** commité pointe **distant**.

**Paramètre requête (observé) :** `gamification_profile` envoyé à `GET /hugo/sessions/{id}/ui-state/` depuis `ProdLearnerWorkspace.vue` — aligné sur `VITE_GAMIFICATION_PROFILE`.

---

## 4. Matrice LOCAL vs PROD DISTANTE

| Dimension | Backend local (`hugo_back`, settings **dev**) | API distante `https://hugoback.encoors.com` |
|-----------|-----------------------------------------------|---------------------------------------------|
| **P0 legacy vs v17** | Legacy ON, v17 OFF (`HUGO_P0_V17_ENABLED=false`) | **Inconnu — À VÉRIFIER** |
| **Classifieur P0 LLM** | OFF global (`HUGO_P0_CLASSIFIER_ENABLED=false`) | **Inconnu — À VÉRIFIER** |
| **Classifieur phase** | ON (`HUGO_PHASE_CLASSIFIER_ENABLED=true`) | **Inconnu — À VÉRIFIER** |
| **LLM provider** | Défaut `ollama` ; groupe peut forcer `OVH_AI` | **Inconnu — À VÉRIFIER** |
| **Synthèse / évaluation** | LLM implémenté (`synthesis_service.py`) + fallback | **Inconnu — À VÉRIFIER** |
| **SSE `/messages/stream/`** | Endpoint présent (`views_sessions.py`) | **Inconnu — À VÉRIFIER** (CORS, nginx, timeout) |
| **DEBUG** | `True` en `dev.py` | **Inconnu — À VÉRIFIER** |
| **CORS** | `CORS_ALLOW_ALL_ORIGINS=True` en dev | **Inconnu — À VÉRIFIER** (origine front distant) |
| **RLS Postgres** | Middleware présent ; tests SQLite | **Inconnu — À VÉRIFIER** |
| **OVH token** | Fallback en dur dans `base.py` si env absent | **Inconnu — À VÉRIFIER** |
| **Front par défaut** | `.env` → distant (pas local sans changement) | Cible **observée** des `.env` commités |

---

## 5. Recommandations de configuration pour la démo

### Profil recommandé — démo client (baseline A, doc 07)

| Couche | Réglage |
|--------|---------|
| Front | `VITE_FRONTEND_MODE` absent ou `prod_showable` ; `VITE_API_URL=https://hugoback.encoors.com` ; engagement ON ; `VITE_P0_DEBUG_ENABLED` absent/false ; `VITE_GAMIFICATION_PROFILE=B` |
| Back (si distant) | Aucun réglage local — **documenter** que P0/LLM sont **À VÉRIFIER** sur Encoors |
| À éviter | Présenter la démo comme preuve du code `hugo_back` local sans fiche d'écarts |

### Profil recommandé — démo moteur local (baseline B)

| Couche | Réglage |
|--------|---------|
| Front | `VITE_API_URL=/api` (non commité aujourd'hui) ; `npm run dev` avec proxy Vite ; `prod_showable` pour parcours client |
| Back | `config.settings.dev` ; `HUGO_P0_V17_ENABLED=false` ; `HUGO_P0_CLASSIFIER_ENABLED=false` ; Ollama up ou `LLM_PROVIDER_DEFAULT` + credentials OVH **via env**, pas token par défaut |
| Prérequis | PostgreSQL, compte apprenant, groupe, tutor-prompts |

### Ce qu'il faut éviter en démo

1. **`DEBUG=True`** exposé publiquement (dev local OK en privé ; `production.py` a aussi `DEBUG=True` — ne pas assumer prod saine).
2. **Token OVH** par défaut dans `base.py` — fuite et dépendance non maîtrisée.
3. **Activer v17 + classifieur P0** sans script de démo — comportement difficile à expliquer.
4. **Mélanger** démo distante et affirmations sur flags locaux sans le dire.
5. **Mode `tester` + `VITE_P0_DEBUG_ENABLED=true`** pour une démo « client » — expose TurnState et admin.

### Documenter le choix final — mini « profil de démo »

Consigner en 5 lignes avant chaque démo importante :

```
Date :
Baseline : A (distant) / B (local) / C (mixte)
Front : commit ou branche hugolucia, VITE_* effective
Back : hugoback.encoors.com (À VÉRIFIER) ou hugo_back + DJANGO_SETTINGS_MODULE + HUGO_P0_*
Comptes : utilisateur / groupe utilisés
Ce qu'on démontre : produit / moteur / les deux
```

---

## Renvois

| Sujet | Document |
|-------|----------|
| Stacks démo possibles | `07_RUNTIME_DEMO_REFERENCE.md` |
| Détail flags P0 / pipeline | `02_ETAT_MOTEUR_REEL.md` |
| Variables front / parcours | `03_ETAT_PRODUIT_REEL.md` |
| Écarts DEBUG prod, token OVH | `05_ECARTS_DOC_CODE_PRODUIT.md` |
| Décisions runtime référence | `06_PREPARATION_CIBLE_1_9.md` |
| Inspection HTTP Encoors (colonne distante) | `10_FICHE_RUNTIME_PROD_ENCOORS.md` |

---

*Document 08 — flags et env démo, juin 2026. API distante non inspectée.*
