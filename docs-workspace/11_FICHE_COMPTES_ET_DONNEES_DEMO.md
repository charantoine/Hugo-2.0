# Fiche comptes et données de démo — Workspace Hugo

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Public :** personne qui prépare ou anime une démo locale ou distante  
**Complète :** `09_PARCOURS_DEMO_ET_SCENARIOS.md`, `07_RUNTIME_DEMO_REFERENCE.md`, `08_FLAGS_ET_ENVIRONNEMENT_DEMO.md`

---

## 1. Objet

Cette fiche recense les **comptes humains**, **organisations**, **groupes** et **données de test** utilisables pour une démo, avec pour chaque élément :

- la **source** exacte dans le repo ;
- le **niveau de confiance** (prouvé sur instance / documenté bootstrap / présent sans mot de passe / à vérifier).

Elle ne remplace pas la spec produit ni le détail moteur (`02`, `03`).

---

## 2. Stack locale de référence (baseline B — instance courante)

| Élément | Valeur | Source | Confiance |
|---------|--------|--------|-----------|
| Front | `http://localhost:5173` | `.env.local`, `tests_playwright/helpers/demo-env.ts` | **Haute** |
| API effective | `VITE_API_URL=/api` → proxy Vite → `http://127.0.0.1:8000` | `.env.local`, `vite.config.js` L8-9 | **Haute** |
| Mode UI | `VITE_FRONTEND_MODE=tester` | `.env.local` | **Haute** |
| Redirect post-login (mode tester) | `/dashboard` | `frontendConfig.js` L30-31 | **Haute** |
| Redirect post-login (mode prod) | `/app` | idem | **Haute** |

**Important :** `.env.development` commité pointe vers `https://hugoback.encoors.com`. Pour la baseline B, **`.env.local` prime** et force l'API locale.

**Démarrage documenté :**

```bash
# Option A — script tout-en-un (sqlite_test + smoke) — ≠ hugo_poc
./run_local_hugo.sh

# Option B — stack dev classique (PostgreSQL hugo_poc)
cd hugo_back && python manage.py runserver 8000
cd hugo-hugolucia/frontend_1.8 && VITE_API_URL=/api VITE_FRONTEND_MODE=tester npm run dev

# Diagnostic : quelle base / settings sont actifs ?
./scripts/which-hugo-stack.sh
# ou : cd hugo_back && python manage.py print_runtime_stack
```

| Stack | Settings | Base | Seeds typiques |
|-------|----------|------|----------------|
| **Dev / OF_test_2** | `config.settings.dev` | PostgreSQL `hugo_poc` | `bootstrap_demo_test_2` |
| **Smoke script** | `config.settings.sqlite_test` | `test.sqlite3` | `bootstrap_smoke_playwright` |

**Superadmin multi-org :** pour voir `OF_test_2` et `*_test_2`, sélectionner l’org dans la navbar (header `X-Organisation-Id`). Voir `memo_cto_2026-06-30.md`.

**E2E Playwright :** `cd frontend_1.8 && npm run test:e2e` (alias canonique avec `-c tests_playwright/playwright.config.ts`).

Sources : `run_local_hugo.sh` ; `tests_playwright/README.md` ; `07_RUNTIME_DEMO_REFERENCE.md` §2 baseline B.

---

## 3. Comptes utilisables immédiatement

### 3.1 Groupe A — confiance **haute** (mot de passe documenté + login prouvé sur `localhost:5173` / API locale)

Preuve runtime : protocole E2E Playwright du **2026-06-29** — `docs-workspace/e2e-protocol-runtime/protocol-preconditions.json` (`loginStatus: 200`), 23 tests PASS (`RAPPORT_E2E_PROTOCOL.md`).

| Compte | Mot de passe | Rôle | Organisation | Parcours principal | Source mot de passe |
|--------|--------------|------|--------------|-------------------|---------------------|
| `demo.superadmin` | `demo-superadmin-2026` | SUPERADMIN | **Demo Hugo Org** | `/dashboard`, switch org, `/admin/onboarding`, `/users`, `/groups-admin` | `tests_playwright/helpers/demo-env.ts` L8-9 ; audits `audit-ui-runtime-front-admin-2026-06-26.md` L16 |
| `smoke_superadmin` | `smoke-pass-2026` | SUPERADMIN | **Smoke Playwright Org** | idem (org smoke) | `bootstrap_smoke_playwright.py` L10, L224 |
| `smoke_orgadmin` | `smoke-pass-2026` | ORGADMIN | Smoke Playwright Org | `/users`, `/groups-admin` (sans switch multi-org) | idem |
| `smoke_learner` | `smoke-pass-2026` | LEARNER | Smoke Playwright Org | `/app`, session préparée (§4.2) | idem ; `run_local_hugo.sh` L88 |
| `smoke_tutor` | `smoke-pass-2026` | TUTOR | Smoke Playwright Org | `/app/tutor` | idem |
| `smoke_trainer` | `smoke-pass-2026` | TRAINER | Smoke Playwright Org | `/app/trainer/knowledge` | idem |
| `smoke_coordo` | `smoke-pass-2026` | COORDO | Smoke Playwright Org | `/app/tutor` | idem |

**Note :** `demo.superadmin` **n'est pas créé** par `bootstrap_smoke_playwright` — il provient d'une base préexistante (seed / import manuel). Script d'inspection seulement : `hugo_back/scripts/check_demo_superadmin.py`.

### 3.2 Groupe B — confiance **moyenne** (bootstrap documenté, fichier fixtures présent, pas tous re-testés individuellement le 2026-06-29)

| Compte | Mot de passe | Rôle | Organisation | Source |
|--------|--------------|------|--------------|--------|
| `tenant_superadmin` | `tenant-smoke-2026` | SUPERADMIN | Tenant Smoke Org A | `bootstrap_multitenant_smoke.py` L13 ; `tenant-smoke-fixtures.json` |
| `tenant_orgadmin_a` | `tenant-smoke-2026` | ORGADMIN | Tenant Smoke Org A | idem |
| `tenant_orgadmin_b` | `tenant-smoke-2026` | ORGADMIN | Tenant Smoke Org B | idem |
| `tenant_tutor_a` | `tenant-smoke-2026` | TUTOR | Org A | idem |
| `tenant_learner_a` | `tenant-smoke-2026` | LEARNER | Org A | idem |
| `tenant_learner_b` | `tenant-smoke-2026` | LEARNER | Org B | idem |

Activation tests : `SMOKE_RUN_TENANT=1` (`e2e/tenant_multi_org.spec.ts`).

### 3.3 Groupe C — **noms présents en base, mot de passe non documenté dans le repo**

Liste observée sur l'instance locale via `GET /users/` (org Demo Hugo Org) — `protocol-preconditions.json` L15-33.

| Compte | Rôle | Mot de passe | Confiance login |
|--------|------|--------------|-----------------|
| `apprenant_melec_1`, `_2`, `_3` | LEARNER | **Non documenté** | **Nulle** |
| `tuteur_melec_1`, `_2`, `_3` | TUTOR | **Non documenté** | **Nulle** |
| `formateur_melec_test` | TRAINER | **Non documenté** | **Nulle** |
| `demo.formateur` | TRAINER | **Non documenté** (hypothèse `DemoHugo123!` dans `tenant_multi_org.spec.ts` L7-8 — test skip, **non prouvé**) | **Nulle** |

**Recommandation démo :** utiliser les comptes **smoke_*** pour parcours apprenant / tuteur / formateur ; réserver **demo.superadmin** + données **Demo Hugo Org** pour l'onboarding admin (bac pro melec, profils globaux, référentiel).

---

## 4. Organisations et groupes

### 4.1 Demo Hugo Org (parcours admin / melec)

| Élément | Valeur | Source | Confiance |
|---------|--------|--------|-----------|
| Nom | Demo Hugo Org | `demo-env.ts` L13 ; audits juin 2026 | **Haute** |
| ID | `dc1e8465-0ff2-4d66-bfbb-a0f8e7a23b3d` | `demo-env.ts` L12 | **Haute** (IDs peuvent diverger si autre DB) |
| Groupe démo principal | **bac pro melec** | `demo-env.ts` L20-22 | **Haute** |
| ID groupe bac pro melec | `29e5cdb9-de89-49b3-a36e-53b4b9bbbc50` | `demo-env.ts` L21 | **Haute** sur instance auditée |
| Référentiel attendu | RNCP38878 | `demo-env.ts` L24 ; scripts `restore_rncp38878_smoke.py` | **Moyenne** — présence **À VÉRIFIER** par run |
| Profil conversationnel fixture | `profil_conversationnel_mk1` (suffixe interne) | `03_ETAT_PRODUIT_REEL.md`, audits admin | **Haute** (nom technique visible UI) |
| ORGADMIN démo | **Aucun** listé | `protocol-preconditions.json` L19 | **Haute** (constat API) |

### 4.2 Smoke Playwright Org (parcours E2E / smoke)

| Élément | Valeur | Source | Confiance |
|---------|--------|--------|-----------|
| Nom | Smoke Playwright Org | `smoke-fixtures.json` L3 | **Haute** |
| ID | `e4b3e984-9794-438f-924d-366dfeb0cd4b` | `smoke-fixtures.json` L2 ; `demo-env.ts` altOrg | **Haute** |
| Groupe | Smoke Group | `smoke-fixtures.json` L4-5 | **Haute** |
| ID groupe | `0ff5014c-ff9b-4363-b613-e03bbdc033b8` | `smoke-fixtures.json` L5 | **Haute** |
| Session apprenant | `deecbacc-d0b3-4f3c-9cfe-e8bbeb88d0e6` | `smoke-fixtures.json` L7 | **Haute** |
| Sessions cluster16 (profils affichage) | youth / adult / professional — IDs dans `cluster16_sessions` | `smoke-fixtures.json` L20-24 | **Haute** |
| Association tuteur ↔ apprenant | `smoke_tutor` ↔ `smoke_learner` | `bootstrap_smoke_playwright.py` L139-144 | **Haute** |
| Verbatim secret (test confidentialité) | marqueur `VERBATIM_SECRET_SMOKE_DO_NOT_SHOW` | `smoke-fixtures.json` L19 | **Haute** |

### 4.3 Multi-tenant (switch SUPERADMIN)

| Élément | Valeur | Source | Confiance |
|---------|--------|--------|-----------|
| Org alternative pour switch | Smoke Playwright Org | `demo-env.ts` altOrg ; E2E lot 1 PASS | **Haute** |
| Nombre d'organisations (instance courante) | 6 | `protocol-preconditions.json` L10 | **Haute** (snapshot date) |
| Groupes org démo (Demo Hugo Org) | 7+ | `protocol-preconditions.json` L12 | **Haute** (snapshot ; lot 4 crée des `e2e_grp_*`) |

### 4.4 OF_test_2 (bêta testeurs externes — juin 2026)

| Élément | Valeur | Source | Confiance |
|---------|--------|--------|-----------|
| Nom org | `OF_test_2` | `demo_test_2_constants.py` ; `demo-test-2-fixtures.generated.json` | **Haute** (noms stables) |
| ID org (snapshot local) | `444cc40a-dd56-49e0-8776-3b1273e3c2de` | `demo-test-2-fixtures.generated.json` | **Moyenne** — varie si autre DB |
| Groupe | `bac_pro__test_2` | idem | **Haute** |
| Comptes | `apprenant_test_2`, `tuteur_test_2`, `formateur_test_2` | idem | **Haute** |
| Mot de passe | `demo123` | `bootstrap_demo_test_2` | **Haute** |
| Référentiel | RNCP38878 | seed `referential_rncp38878.py` | **Haute** sur instance seedée |
| Rattachements | `User.organisation` + `GroupMembership` + `TutorLearnerLink` (tuteur↔apprenant) | `group_attachments.py` ; tests `test_demo_test_2_seed.py` | **Haute** |
| Profil conversationnel | clone `profil_conversationnel_mk1` | `clone_conversation_profile.py` | **Moyenne** — requiert Demo Hugo Org source |

**Commande :** `python manage.py bootstrap_demo_test_2 [--write-fixtures]`  
**Doc détaillée :** `seed-strategies.md` §5.2 ; `hugo_back/apps/accounts/seeds/README.md`.

---

## 5. Scripts bootstrap et régénération des données

| Commande | Effet | Mot de passe imposé | Fichier fixtures généré |
|----------|-------|---------------------|-------------------------|
| `python manage.py bootstrap_smoke_playwright` | Crée/met à jour org Smoke + 6 comptes `smoke_*` + session + trace + knowledge item + sessions cluster16 | `smoke-pass-2026` | `tests_playwright/smoke-fixtures.json`, `docs-workspace/smoke-fixtures.generated.json` |
| `python manage.py bootstrap_profile_migration_smoke` | Groupes/profils migration (réutilise `smoke_learner`) | `smoke-pass-2026` | `tests_playwright/profile-smoke-fixtures.json` |
| `python manage.py bootstrap_multitenant_smoke` | 2 orgs tenant + 6 comptes `tenant_*` | `tenant-smoke-2026` | `tests_playwright/tenant-smoke-fixtures.json` |
| `python manage.py bootstrap_orgadmin --org-name … --username … --password …` | Crée org + ORGADMIN/SUPERADMIN ad hoc | argument CLI | — |
| `python manage.py bootstrap_demo_test_2` | Org **OF_test_2** + groupe `bac_pro__test_2` + comptes `*_test_2` + RNCP38878 + clone profil mk1 | `demo123` | `docs-workspace/demo-test-2-fixtures.generated.json` (option `--write-fixtures`) |

Sources : `hugo_back/apps/accounts/management/commands/` ; `seed-strategies.md` ; `tests_playwright/README.md`.

**Ordre recommandé avant démo smoke :**

```bash
cd hugo_back
python manage.py migrate
python manage.py bootstrap_smoke_playwright
python manage.py bootstrap_profile_migration_smoke   # si parcours profils
```

---

## 6. Matrice rôle → route → compte recommandé

| Rôle | Mode front | Route d'entrée après login | Compte recommandé | Données |
|------|------------|----------------------------|-------------------|---------|
| SUPERADMIN | `tester` | `/dashboard` | `demo.superadmin` | Demo Hugo Org, bac pro melec |
| SUPERADMIN (org smoke) | `tester` | `/dashboard` | `smoke_superadmin` | Smoke Playwright Org |
| ORGADMIN | `tester` | `/dashboard` ou `/users` | `smoke_orgadmin` | Smoke Playwright Org |
| LEARNER | `prod_showable` | `/app` | `smoke_learner` | session `deecbacc-…` |
| TUTOR | `prod_showable` | `/app/tutor` | `smoke_tutor` | lien vers `smoke_learner` |
| TRAINER | `prod_showable` ou `tester` | `/app/trainer/knowledge` (entrée **prod**, même en mode `tester`) | `smoke_trainer` | knowledge item id `1` (fixture) |
| TRAINER (bêta OF_test_2) | `prod_showable` | `/app/trainer/knowledge` | `formateur_test_2` | org isolée — seed `bootstrap_demo_test_2` |
| COORDO | `prod_showable` | `/app/tutor` | `smoke_coordo` | Smoke Playwright Org |
| Calibration technique | `tester` + option `VITE_P0_DEBUG_ENABLED=true` | `/group/:id/learner/:id` | `demo.superadmin` | bac pro melec + apprenant melec (si MDP connu) |

Pour une **démo client** : mode `prod_showable` + comptes smoke ou comptes métier (si MDP fournis hors repo).

Pour une **démo onboarding admin** : mode `tester` + `demo.superadmin`.

---

## 7. Pré-test obligatoire (checklist 5 min)

| # | Vérification | OK si |
|---|--------------|-------|
| 1 | Front répond | `http://localhost:5173` → 200 |
| 2 | API répond | `http://127.0.0.1:8000/auth/login/` → 405 ou 400 (pas connection refused) |
| 3 | Proxy actif | Login front ne timeout pas ; requêtes vers `/api/…` |
| 4 | Login superadmin | `demo.superadmin` / `demo-superadmin-2026` → `/dashboard` |
| 5 | Login apprenant smoke | `smoke_learner` / `smoke-pass-2026` → `/app` |
| 6 | Groupe démo visible | Superadmin : bac pro melec dans `/groups-admin` |
| 7 | LLM (si chat démo) | Ollama `:11434` ou OVH configuré — sinon messages assistant vides |

Automatisable : `cd hugo-hugolucia/frontend_1.8 && npm run test:protocol` (lots 0–4, 8, 10, 12).

---

## 8. Écarts et limites documentées

| Sujet | Réel confirmé | À ne pas supposer |
|-------|---------------|-------------------|
| Comptes melec | Noms en base Demo Hugo Org | Mots de passe disponibles |
| `demo.formateur` | Présent en base | `DemoHugo123!` sans test |
| RNCP38878 | Attendu sur bac pro melec | Toujours attaché et indexé |
| Baseline A Encoors | `.env.development` par défaut | Comptes locaux valides sur distant |
| Mémoire inter-session | Consolidée après tours | Injectée au tour suivant (**non** — doc 02, 05) |

---

## 9. Renvois

| Sujet | Document |
|-------|----------|
| Scénarios pas à pas | `09_PARCOURS_DEMO_ET_SCENARIOS.md` |
| Baselines A/B/C | `07_RUNTIME_DEMO_REFERENCE.md` |
| Flags env | `08_FLAGS_ET_ENVIRONNEMENT_DEMO.md` |
| Preuves E2E récentes | `e2e-protocol-runtime/RAPPORT_E2E_PROTOCOL.md` |
| Stratégies de seed | `seed-strategies.md` |
| Routes front | `03_ETAT_PRODUIT_REEL.md` |

---

*Document 11 — comptes et données de démo. Dernière révision : juin 2026 — ancrage instance locale `localhost:5173` + protocole E2E 2026-06-29 + seed OF_test_2 2026-06-30.*
