# Cartographie du workspace réel — Hugo

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Objet :** géographie du dépôt — où se trouve quoi, points d'entrée, relations entre dossiers.  
**Ne couvre pas :** comportement P0 (→ doc 02), UX produit (→ doc 03).  
**S'appuie sur :** `docs-workspace/00_HIERARCHIE_DOCUMENTAIRE.md`

---

## 1. Vue d'ensemble du workspace

**Racine** : quatre éléments utiles — `hugo_back/`, `hugo-hugolucia/`, `hugo-main/`, `docs-workspace/` (bibliothèque de recalage en cours).

| Dossier | Rôle en une phrase |
|---------|-------------------|
| **`hugo_back`** | Seul dépôt contenant le backend Python Django (moteur, API, tests). |
| **`hugo-hugolucia`** | Monorepo front + infra + docs ; référence produit (`frontend_1.8`) et specs 1.9 v2 ; `backend/` vide. |
| **`hugo-main`** | Snapshot antérieur du monorepo, centré specs 1.8 ; `backend/` vide ; `frontend_1.8` en retard sur hugolucia. |

| Dimension | `hugo_back` | `hugo-hugolucia` | `hugo-main` |
|-----------|-------------|------------------|-------------|
| **Moteur** | IMPLÉMENTÉ | Absent (`backend/` vide) | Absent (`backend/` vide) |
| **Produit montrable** | — | IMPLÉMENTÉ (`frontend_1.8/`) | PARTIEL (même base, moins avancé) |
| **Docs actives** | 4 fichiers techniques | Specs 1.9 v2 + archives unifiées | Specs 1.8 à la racine `specs/` |
| **Déploiement** | `Dockerfile` seul | `docker-compose.yml` + `deploy/nginx/` | idem hugolucia (nginx sans SSE) |
| **Tests** | 30 fichiers `test_*.py` (pytest) | `npm test` sur `frontend_1.8` uniquement | idem |

---

## 2. Carte par dossier racine

### `hugo_back/`

**Arborescence utile (niveau 2–3, hors `venv/`) :**

```
hugo_back/
├── manage.py, requirements.txt, Dockerfile, pytest.ini, README.md
├── config/           → urls.py, wsgi.py, asgi.py, celery.py, settings/
├── app_core/         → middleware tenant RLS
├── app_db/           → migrations/utilitaires RLS
├── apps/
│   ├── accounts/     → JWT, orgs, users
│   ├── hugo/         → sessions, messages, services P0, modèles métier
│   ├── referentials/ → groupes, RNCP, import v2
│   ├── library/      → documents, chunks, indexation
│   ├── quality/      → bundle evidence
│   └── exports/      → export traces CSV/JSON
├── tests/            → auth, RLS cross-tenant, referentials
├── docs/             → P0, guide testeurs, import MVP
└── evidence/         → fichiers uploadés (ex. preuves)
```

**Stack** (preuve `requirements.txt`, `Dockerfile`) : Django ≥5.2, DRF, JWT, PostgreSQL/psycopg, pgvector, Celery/Redis, MinIO/S3, pytest.

**Points d'entrée :**

| Type | Fichier | Détail |
|------|---------|--------|
| CLI | `manage.py` | Settings par défaut : `config.settings.dev` |
| HTTP | `config/wsgi.py` | Port 8000 via `Dockerfile` CMD |
| Async | `config/celery.py` | Worker Celery |
| API | `config/urls.py` | Préfixes : `/auth/`, `/hugo/`, `/groups/`, `/documents/`, `/exports/`, `/quality/`, `/internal/`, etc. |

**Apps Django — rôle apparent :**

| App | Rôle apparent |
|-----|---------------|
| `accounts` | Auth JWT, multi-tenant, admin org/users |
| `hugo` | Cœur conversationnel, sessions, traces, dashboard, conduct profiles |
| `referentials` | Groupes, référentiels, import activités/tâches |
| `library` | Bibliothèque documentaire, chunks |
| `exports` | Export synchrone traces |
| `quality` | Bundle evidence Qualiopi |

**Tests / configs / docs :** `pytest.ini` → `config.settings.test` ; 30 tests hors venv ; docs dans `hugo_back/docs/` (4 fichiers .md + 1 JSON exemple).

**Absent vs monorepos :** pas de `docker-compose.yml`, pas de `deploy/nginx/`, pas de front, pas de `.env.example` dans ce dossier.

---

### `hugo-hugolucia/`

**Arborescence utile :**

```
hugo-hugolucia/
├── backend/              → VIDE (0 fichier)
├── frontend/             → Vue 3 testeur/admin (13 vues)
├── frontend_1.8/         → Vue 3 prod montrable + testeur (16 vues)
├── deploy/nginx/         → reverse proxy (inclut route SSE stream)
├── docs/                 → deploy + audits probatoires mai 2026
├── specs/                → docs actives v2 (1.9, juin 2026)
├── specs-old/            → archives 1.6 → 1.9 + pack audit
├── RAG Melec/            → 9 fichiers corpus démo
├── docker-compose.yml    → postgres, minio, redis, api, worker, llm, nginx
├── .env, .env.example
└── *.md racine           → SPEC_POC, Synopsis, p0_description*, etc.
```

**`backend/` :** vide — `docker-compose.yml` L40–41 référence `build: context: ./backend` → **cassé** sans rattacher `hugo_back`.

**`frontend/` vs `frontend_1.8/` :**

| | `frontend/` | `frontend_1.8/` |
|---|-------------|-----------------|
| Rôle | Testeur / admin minimal | Prod montrable (`/app*`) + mode testeur |
| Layouts | Navbar dans les vues | `ProdLearnerLayout.vue`, `TesterLayout.vue` |
| API dev | `VITE_API_URL=/api` (proxy local) | `VITE_API_URL=https://hugoback.encoors.com` |
| Tests | — | `npm test` (node --test) |

**Infra :** `deploy/nginx/conf.d/api.conf` — proxy `/api/` → Django, SPA sur `/` ; route SSE `messages/stream/` (absente dans `hugo-main`). Nginx sert `frontend/dist`, pas `frontend_1.8/dist` → **AMBIGU** pour démo 1.8 en prod docker.

**Docs :** `specs/` = actif (MEMO 1.9, LOT7, SPEC v2…) ; `specs-old/` = archives (`specs-old-1.6` … `specs_audit_1.9`). `docs/` = deploy + 2 rapports audit e-Soleau.

**`RAG Melec/` :** 9 fichiers `.md`/`.yaml.md` — corpus métier Bac Pro MELEC ; **données**, pas runtime.

**API cible des fronts** (preuve `.env`) :

| Front | Dev | Prod |
|-------|-----|------|
| `frontend/` | `/api` → proxy `localhost:8000` (`vite.config.js`) | `hugoback.encoors.com` |
| `frontend_1.8/` | `hugoback.encoors.com` | `hugoback.encoors.com` |

---

### `hugo-main/`

Structure quasi identique à hugolucia au niveau racine (mêmes dossiers `frontend/`, `frontend_1.8/`, `deploy/`, `docker-compose.yml`, `RAG Melec/`, docs racine dupliquées).

**Différences constatées :**

| Élément | `hugo-main` | `hugo-hugolucia` |
|---------|-------------|------------------|
| `backend/` | Vide | Vide |
| `frontend/` | Identique (hors `.DS_Store`) | Référence |
| `frontend_1.8/` | Version intermédiaire | **Référence produit** |
| Specs actives | `specs/` = Hugo 1.8 (7 fichiers) | `specs/` = 1.9 v2 |
| Archives | `specs-old-1.6/`, `specs-old-1.7/` à la racine | `specs-old/` unifié (1.6→1.9) |
| `docs/` | 4 fichiers deploy/RAG | + 2 rapports audit probatoire |
| Nginx | Pas de route SSE stream | Route SSE présente |

**Fichiers présents uniquement dans hugolucia `frontend_1.8/`** (preuve `diff -rq`) : `HugoProgressPanel.vue`, `messageStream.js`, `progressionLabels.js`, `ConductProfilesView.vue` ; diffs sur `ProdLearnerWorkspace.vue`, router, `engagementUiModel.js`, vues admin.

**Redondant :** docs racine (`SPEC_POC_v1.5.md`, `p0_description*`, `Synopsis`, `RAG Melec/`) — doublons entre main et hugolucia.

---

## 3. Relations entre les trois dossiers

```
                    ┌─────────────────────────────────┐
                    │  Zone de travail Hugo (racine)   │
                    └─────────────────────────────────┘
           ┌────────────────┬────────────────┬────────────────┐
           ▼                ▼                ▼
      hugo_back      hugo-hugolucia      hugo-main
      MOTEUR         PRODUIT + DOCS      SNAPSHOT 1.8
      IMPLÉMENTÉ     référence           en retard
           │                │                │
           │    backend/ vide dans les deux monorepos
           │                │                │
           └────couplage HTTP API uniquement────┘
                    (pas d'import Python croisé)
```

| Question | Réponse | Statut |
|----------|---------|--------|
| Où est le moteur ? | `hugo_back/` uniquement | IMPLÉMENTÉ |
| Où est le produit de référence ? | `hugo-hugolucia/frontend_1.8/` | IMPLÉMENTÉ |
| Où sont les specs actives 1.9 ? | `hugo-hugolucia/specs/` | CRÉDIBLE (à croiser code) |
| Où sont les specs 1.8 ? | `hugo-main/specs/` + archivées dans `hugo-hugolucia/specs-old/specs-old-1.8/` | ARCHIVE / CIBLE |
| Lien `hugo_back` ↔ monorepos ? | Backend extrait ou copié parallèle ; chemins docs disent `backend/apps/…` | **AMBIGU** |
| Runtime prod des fronts ? | `https://hugoback.encoors.com` | **À VÉRIFIER** vs `hugo_back` local |

**Duplications connues :** `SPEC_POC_v1.5.md`, `p0_description_technique_actuelle*.md`, `Synopsis-Hugo-v1.5.md`, `RAG Melec/` (×2), `docs/DEPLOY_*.md`, `docs/RAG_GROUP_LIBRARY.md`.

**Arbitrage documenté :** produit montrable = **`hugo-hugolucia/frontend_1.8`** (cf. doc 00).

---

## 4. Points d'entrée opérationnels

| Action | Dossier | Commande / fichier | Prérequis | Statut |
|--------|---------|-------------------|-----------|--------|
| Lancer API Django local | `hugo_back` | `python manage.py runserver` | venv, PostgreSQL, `.env` | **Lançable** (si DB configurée) |
| Build image API seule | `hugo_back` | `Dockerfile` | Docker | **Lançable** |
| Tests backend | `hugo_back` | `pytest` | DB test (`pytest.ini`) | **Lançable** |
| Front testeur dev (proxy local) | `hugo-hugolucia/frontend` | `npm run dev` | API sur :8000 | **Lançable** si back local |
| Front prod montrable dev | `hugo-hugolucia/frontend_1.8` | `npm run dev` | Réseau (API distante) | **Lançable** (API distante) |
| Tests front 1.8 | `hugo-hugolucia/frontend_1.8` | `npm test` | node | **Lançable** |
| Stack docker complète | `hugo-hugolucia` ou `hugo-main` | `docker compose up` | `./backend` peuplé | **Cassé** (backend vide) |
| Démo sans back local | `hugo-hugolucia/frontend_1.8` | `npm run dev` + `.env` | `hugoback.encoors.com` | **Distant** |
| Nginx prod (compose) | monorepos | `deploy/nginx/` | `frontend/dist` buildé | **Partiel** (sert `frontend/`, pas `frontend_1.8/`) |

---

## 5. Zones fonctionnelles — où chercher quoi

| Zone | Emplacement | Confiance | Statut |
|------|-------------|-----------|--------|
| Moteur / API | `hugo_back/apps/hugo/`, `config/urls.py` | FORT | IMPLÉMENTÉ |
| Auth / multi-tenant | `hugo_back/apps/accounts/`, `app_core/middleware.py` | FORT | IMPLÉMENTÉ |
| Front debug / calibration | `*/frontend/`, `*/frontend_1.8` mode tester — `LearnerDetailView.vue` | FORT | IMPLÉMENTÉ |
| Front montrable | `hugo-hugolucia/frontend_1.8/` — routes `/app*` | FORT | IMPLÉMENTÉ |
| Infra docker / nginx | `hugo-hugolucia/deploy/`, `docker-compose.yml` | MOYEN | PARTIEL (backend manquant) |
| Corpus RAG démo | `RAG Melec/` (×2) | FORT | CRÉDIBLE (données) |
| Specs cible 1.9 | `hugo-hugolucia/specs/` | MOYEN | CIBLE |
| Specs prod 1.8 | `hugo-main/specs/`, `hugo-hugolucia/specs-old/specs-old-1.8/` | MOYEN | ARCHIVE / CIBLE |
| Archives / audits | `hugo-hugolucia/specs-old/`, `docs/rapport_audit_*` | FORT | ARCHIVE |
| Hugo & Cie (extensions) | `Synopsis-Hugo-v1.5.md`, `Integrations-LMS-SIRH-v1.5.md` | MOYEN | CIBLE (POST-POC) |
| Bibliothèque recalage | `docs-workspace/` | FORT | EN COURS |

---

## 6. Ambiguïtés et limites

**Non tranché dans ce workspace :**

- Équivalence `hugo_back` local ↔ `hugoback.encoors.com` (**À VÉRIFIER**).
- Stratégie d'intégration : réinjecter `hugo_back` dans `backend/` des monorepos ou garder 3 dossiers séparés (**AMBIGU**).
- Quel build nginx sert en prod réelle : `frontend/` ou `frontend_1.8/` (**AMBIGU** — compose pointe `frontend/dist`).
- Historique git / branche officielle entre `hugo-main` et `hugo-hugolucia` (**À VÉRIFIER** hors filesystem).

**Hors périmètre volontaire :**

- Détail du pipeline P0, TurnState, flags v17 → `02_ETAT_MOTEUR_REEL.md`
- Parcours UX, engagement UI, contrats `ui-state` → `03_ETAT_PRODUIT_REEL.md`
- Catalogue qualifié de tous les .md → `04_INDEX_DOCUMENTAIRE_QUALIFIE.md`
- Backlog 1.9

---

## 7. Renvoi

- **Règles de lecture :** `docs-workspace/00_HIERARCHIE_DOCUMENTAIRE.md`
- **Lecture suivante :**
  - `02_ETAT_MOTEUR_REEL.md` — comportement réel de `hugo_back`
  - `03_ETAT_PRODUIT_REEL.md` — démo montrable `hugo-hugolucia/frontend_1.8`
  - `07_RUNTIME_DEMO_REFERENCE.md`, `08_FLAGS_ET_ENVIRONNEMENT_DEMO.md`, `09_PARCOURS_DEMO_ET_SCENARIOS.md`, `10_FICHE_RUNTIME_PROD_ENCOORS.md` — préparation démo

---

*Document 01 — cartographie filesystem juin 2026. Sources : arborescence locale, `config/urls.py`, `docker-compose.yml`, `.env`, `diff -rq` main/hugolucia.*
