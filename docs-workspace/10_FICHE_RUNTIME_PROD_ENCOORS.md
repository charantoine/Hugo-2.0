# Fiche runtime prod — `https://hugoback.encoors.com`

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Cible :** API distante Encoors — complète `07_RUNTIME_DEMO_REFERENCE.md` et `08_FLAGS_ET_ENVIRONNEMENT_DEMO.md`.  
**Inspection :** 2026-06-12, ~14:09–14:10 **UTC** (requêtes `curl` en lecture seule depuis le workspace local).  
**Ne remplace pas :** `02_ETAT_MOTEUR_REEL.md`, `03_ETAT_PRODUIT_REEL.md` (vérité code local).

---

## 1. Objet et limites

Cette fiche répond à : **que sait-on d'Encoors au moment de l'inspection**, par preuves HTTP directes — pas par le code `hugo_back` du workspace.

Elle ne prouve pas : flags d'environnement non exposés (`HUGO_P0_*`, `LLM_PROVIDER_DEFAULT`, secrets), version git ou commit déployé, efficacité RLS Postgres, comportement LLM (qualité/latence), ni le parcours complet authentifié sans compte de démo (non fourni). Les flags prod restent **VRIFIER** sauf déduction explicite.

---

## 2. Méthode d'inspection

| Action | Détail | Résultat |
|--------|--------|----------|
| Résolution DNS / TLS | `curl` vers `https://hugoback.encoors.com` | **OBSERVÉ** — IP `213.32.25.22`, certificat Let's Encrypt valide (expire 2026-08-10) |
| `HEAD` / `GET /` | Racine API | **OBSERVÉ** — HTTP **404** (pas de health public à la racine) |
| `OPTIONS` + `POST` `/auth/login/` | CORS preflight et login sans / avec corps | **OBSERVÉ** — voir §3 |
| `GET` `/auth/me/`, `/groups/`, `/hugo/sessions/`, `/hugo/tutor-prompts/` | Sans JWT | **OBSERVÉ** — HTTP **401** JSON DRF |
| `POST` `/auth/login/` | Corps `{}` puis identifiants invalides | **OBSERVÉ** — **400** (champs requis FR), **401** `Invalid credentials` |
| `POST` `/auth/refresh/` | Corps `{}` | **OBSERVÉ** — **400** (`refresh` requis) |
| `GET` `/admin/` | Admin Django | **OBSERVÉ** — **302** → `/admin/login/` |
| `GET` `/internal/.../turn-review/` | Endpoint internal | **OBSERVÉ** — **401** (route présente, auth requise) |
| `GET` chemins OpenAPI (`/api/schema/`, etc.) | Schéma exposé | **OBSERVÉ** — tous **404** |
| `GET` `/hugo/nonexistent-probe/` | Page 404 Django | **OBSERVÉ** — `DEBUG = True` affiché dans le footer ; liste complète `config.urls` |
| CORS | `OPTIONS /auth/login/` avec divers `Origin` | **OBSERVÉ** — voir §3 |
| SSE `/messages/stream/` | Sans session/auth valide | **VRIFIER** — route listée dans urlconf ; flux non testé |
| Login avec compte réel | — | **Non tenté** (pas de credentials dans le workspace) |

**Légende :** **OBSERVÉ** = réponse HTTP directe ; **DÉDUIT** = inférence à partir d'observations ; **VRIFIER** = non inspecté ou incomplet.

---

## 3. Résumé exécutif

| Critère | Statut | Commentaire |
|---------|--------|-------------|
| **Disponibilité API** | **OBSERVÉ — OK** | HTTPS répond ; endpoints DRF sous `/auth/`, `/hugo/`, etc. |
| **Auth JWT** | **OBSERVÉ — OK** | `/auth/login/` actif ; validation FR ; `/auth/me/` exige JWT |
| **SSE `/messages/stream/`** | **DÉDUIT — route présente** | Listée dans urlconf 404 ; comportement stream **VRIFIER** |
| **CORS depuis `http://localhost:5173`** | **OBSERVÉ — non autorisé** | Pas de `Access-Control-Allow-Origin` pour localhost (preflight ni POST) |
| **CORS depuis `https://hugo.encoors.com`** | **OBSERVÉ — autorisé** | `access-control-allow-origin: https://hugo.encoors.com` |
| **Équivalence avec `hugo_back` local** | **DÉDUIT — partielle** | Urlconf proche ; écarts de routes **OBSERVÉS** (§4) |
| **Baseline A (démo produit)** | **Conditionnelle** | OK si front servi depuis origine CORS autorisée ; **risque** si `npm run dev` local → API distante |

---

## 4. Ce qui est OBSERVÉ sur Encoors

### Infrastructure

| Élément | Valeur | Statut |
|---------|--------|--------|
| URL | `https://hugoback.encoors.com` | OBSERVÉ |
| Serveur proxy | `nginx/1.22.1` | OBSERVÉ |
| Framework | Django (`config.urls`, pages 404 debug) | OBSERVÉ |
| `DEBUG` | **True** (message explicite page 404) | OBSERVÉ |
| OpenAPI / schema public | Absent (404) | OBSERVÉ |

### Headers de sécurité (échantillon)

**OBSERVÉ** sur plusieurs réponses : `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: same-origin`, `Cross-Origin-Opener-Policy: same-origin`, `Vary: Cookie, origin`.

### Endpoints sans authentification

| Chemin | Méthode | Code | Corps / comportement |
|--------|---------|------|----------------------|
| `/` | GET | 404 | Page HTML Django |
| `/auth/login/` | POST `{}` | 400 | `username` / `password` obligatoires (FR) |
| `/auth/login/` | POST identifiants invalides | 401 | `{"detail":"Invalid credentials"}` |
| `/auth/refresh/` | POST `{}` | 400 | `refresh` obligatoire |
| `/auth/me/` | GET | 401 | JWT requis |
| `/groups/` | GET | 401 | JWT requis |
| `/hugo/sessions/` | GET | 401 | JWT requis |
| `/hugo/tutor-prompts/` | GET | 401 | JWT requis |
| `/admin/` | GET | 302 | Redirect login admin |

### CORS (preflight `OPTIONS /auth/login/`)

| Origin testée | `Access-Control-Allow-Origin` | Statut |
|---------------|-------------------------------|--------|
| `http://localhost:5173` | Absent | OBSERVÉ |
| `http://127.0.0.1:5173` | Absent | OBSERVÉ |
| `http://localhost:8080` | Absent | OBSERVÉ |
| `https://hugo.encoors.com` | `https://hugo.encoors.com` | OBSERVÉ |
| `https://hugoback.encoors.com` | `https://hugoback.encoors.com` | OBSERVÉ |
| `https://encoors.com` | Absent | OBSERVÉ |

**DÉDUIT :** la démo front en `npm run dev` sur `:5173` avec `VITE_API_URL=https://hugoback.encoors.com` peut être **bloquée par le navigateur** (CORS). La démo depuis un front hébergé sur `https://hugo.encoors.com` est **cohérente** avec la politique CORS observée (**VRIFIER** en conditions réelles avec login).

### Surface API (depuis page 404 Django)

**OBSERVÉ** — préfixes et routes alignés sur `hugo_back/config/urls.py` local, dont notamment :

- `/auth/`, `/users/`, `/groups/`, `/hugo/sessions/…`, `/hugo/sessions/…/messages/stream/`, `/hugo/sessions/…/ui-state/`, `/hugo/sessions/…/request-synthesis/`, `/hugo/sessions/…/request-evaluation/`, `/hugo/tutor-prompts/`, `/internal/`, `/exports/`, etc.

**OBSERVÉ — absent sur Encoors** (présent dans `hugo_back/apps/hugo/urls.py` local) :

| Route locale | Test Encoors | Statut |
|--------------|--------------|--------|
| `/hugo/conduct-profiles/` | 404 Django (non listée dans urlconf distante) | **OBSERVÉ — absent** |
| `/hugo/sessions/{id}/evaluation-readiness/` | 404 Django | **OBSERVÉ — absent** |
| `/hugo/sessions/{id}/finalize-evaluation/` | Non testé individuellement ; absent de la liste 404 | **DÉDUIT — probablement absent** |

**VRIFIER** : `/hugo/conduct-profiles/` côté mode testeur front ; impact démo parcours `/app` seul limité.

### Version / commit

| Indicateur | Résultat |
|------------|----------|
| Header `X-API-Version` | Absent |
| Endpoint version dédié | Non trouvé |
| Hash git | **VRIFIER** |

---

## 5. Matrice LOCAL (`hugo_back`) vs DISTANT (Encoors)

Référence locale : settings **dev** par défaut (`08_FLAGS_ET_ENVIRONNEMENT_DEMO.md`). Colonne Encoors = inspection 2026-06-12 sauf mention.

| Dimension | Local (`hugo_back` workspace) | Encoors (distant) |
|-----------|-------------------------------|-------------------|
| **P0 legacy vs v17** | Legacy, `HUGO_P0_V17_ENABLED=false` (défaut code) | **VRIFIER** |
| **Classifieur P0 LLM** | OFF global (`HUGO_P0_CLASSIFIER_ENABLED=false`) | **VRIFIER** |
| **Classifieur phase** | ON par défaut (`HUGO_PHASE_CLASSIFIER_ENABLED=true`) | **VRIFIER** |
| **LLM provider** | Défaut `ollama` ; groupe peut forcer `OVH_AI` | **VRIFIER** |
| **Synthèse / évaluation** | Endpoints présents localement | **OBSERVÉ** — `request-synthesis` / `request-evaluation` dans urlconf ; `evaluation-readiness` / `finalize-evaluation` **absents** |
| **SSE `/messages/stream/`** | Endpoint implémenté | **DÉDUIT** — route dans urlconf ; flux **VRIFIER** |
| **DEBUG** | `True` en `dev.py` ; `production.py` local aussi `True` | **OBSERVÉ — `True`** (page 404) |
| **CORS** | `CORS_ALLOW_ALL_ORIGINS=True` en dev | **OBSERVÉ** — liste blanche (ex. `hugo.encoors.com`) ; **pas** localhost:5173 |
| **RLS Postgres** | Middleware présent ; tests SQLite | **VRIFIER** |
| **`conduct-profiles` API** | Présent (`urls.py` L40–41) | **OBSERVÉ — absent** |
| **Front par défaut repo** | `.env` → Encoors | Cible **OBSERVÉ** |

---

## 6. Risques pour la démo baseline A

1. **CORS localhost** — `npm run dev` (`:5173`) vers Encoors : origine **non** autorisée (**OBSERVÉ**). Prévoir front sur `https://hugo.encoors.com` ou proxy / origine ajoutée côté prod (**VRIFIER** avec équipe infra).
2. **`DEBUG=True` en prod** — fuite d'informations (urlconf complète sur 404) (**OBSERVÉ**). Risque gouvernance et image client.
3. **Divergence de routes** — `conduct-profiles`, `evaluation-readiness` absents vs code local récent (**OBSERVÉ**). Démo testeur / éval avancée peut différer.
4. **Équivalence moteur non prouvée** — flags P0, LLM, mémoire, RAG : **VRIFIER** ; ne pas vendre la démo comme preuve du workspace local sans baseline B.
5. **SSE** — route exposée mais non validée (timeouts nginx, CORS sur stream) ; fallback POST front possible (**VRIFIER**).
6. **Comptes démo** — aucun identifiant testé dans cette inspection ; parcours authentifié complet **VRIFIER** (→ fiche `11` à produire).
7. **Latence / LLM** — non mesurée ; démo conversationnelle dépend du provider distant (**VRIFIER**).
8. **Version déployée inconnue** — commit / date de déploiement **VRIFIER** ; écarts doc 05 peuvent être résolus en local mais pas en prod.

---

## 7. Recommandations CTO

**Garder Encoors comme référence démo produit ?** **Oui, avec réserves** — l'API est en ligne, le contrat DRF et les routes cœur (`/app`) sont **OBSERVÉS** compatibles avec le front 1.8, et CORS autorise au moins `https://hugo.encoors.com`. En revanche : ne pas supposer que `npm run dev` local + API distante fonctionne sans vérifier CORS dans le navigateur ; documenter l'**origine front réelle** de chaque démo.

**Avant chaque démo importante, revérifier :**

1. Login + `GET /groups/` + création session avec le **compte démo** prévu (fiche 11).
2. Origine front utilisée vs politique CORS (localhost vs `hugo.encoors.com`).
3. Un échange chat + `GET …/ui-state/` (boutons synthèse/éval).
4. Si SSE est mis en avant : un message avec stream ou constat du fallback POST.
5. Formulation publique : « démo sur runtime Encoors » vs « code `hugo_back` local » — ne pas fusionner sans fiche d'écarts.

**Actions infra suggérées (hors scope doc) :** passer `DEBUG=False` en prod ; documenter commit déployé ; aligner routes manquantes ou assumer écart ; ajouter `http://localhost:5173` à CORS **si** les démos dev distant restent requises.

---

## 8. Renvois

| Sujet | Document |
|-------|----------|
| Baselines démo A/B/C | `07_RUNTIME_DEMO_REFERENCE.md` |
| Flags locaux et matrice théorique | `08_FLAGS_ET_ENVIRONNEMENT_DEMO.md` |
| Parcours et scénarios | `09_PARCOURS_DEMO_ET_SCENARIOS.md` |
| Moteur local | `02_ETAT_MOTEUR_REEL.md` |
| Produit / endpoints front | `03_ETAT_PRODUIT_REEL.md` |
| Écarts doc-code | `05_ECARTS_DOC_CODE_PRODUIT.md` |
| Comptes démo | `11_FICHE_COMPTES_ET_DONNEES_DEMO.md` (**à produire**) |

---

*Document 10 — inspection Encoors 2026-06-12 UTC. Sans credentials : parcours authentifié complet et flags env non lus.*
