# Rapport de campagne de test — 30 juin 2026

> **Périmètre :** convergence Hugo local — tenant actif, groupes, memberships, rôles, cohérence API ↔ UI.  
> **Base auditée :** `postgresql://localhost:5432/hugo_poc` (`config.settings.dev`).  
> **Méthodo :** réel observé > spec ; divergences classées **corrigée** / **documentée** / **A_VÉRIFIER**.

---

## 1. Inventaire de l’environnement de test

### 1.1 Lancement applicatif

| Couche | Commande / config | Notes |
|--------|-------------------|-------|
| **Backend dev** | `cd hugo_back && DJANGO_SETTINGS_MODULE=config.settings.dev .venv/bin/python manage.py runserver 8000` | DB par défaut `hugo_poc` |
| **Backend smoke script** | `./run_local_hugo.sh` | `config.settings.sqlite_test` + `bootstrap_smoke_playwright` — **≠** `hugo_poc` |
| **Frontend** | `cd hugo-hugolucia/frontend_1.8 && npm run dev -- --port 5173` | `.env.local` : `VITE_API_URL=/api`, `VITE_FRONTEND_MODE=tester` |
| **Proxy** | Vite `/api` → `localhost:8000` | Playwright force `VITE_API_URL=/api` |

### 1.2 Suites de tests existantes

| Suite | Commande | Résultat campagne 30/06 |
|-------|----------|-------------------------|
| Backend ciblé | `manage.py test apps.accounts.tests.test_demo_test_2_seed apps.accounts.tests.test_tenant_isolation apps.referentials.tests.test_trainer_group_list apps.hugo.tests.test_tutor_access_control` | **14/14 PASS** |
| Backend campagne | `manage.py test apps.accounts.tests.test_tenant_ui_campaign` | **8/8 PASS** (nouveau) |
| Front unit | `cd frontend_1.8 && npm test` | **52/52 PASS** |
| Playwright trainer | `npx playwright test test_smoke_trainer.spec.ts -c tests_playwright/playwright.config.ts` | **1/1 PASS** (après correction sélecteur) |
| Playwright protocole L1 | sans `-c playwright.config.ts` | **ÉCHEC** — URL invalide (config manquante) |
| Playwright protocole L1 complet | non relancé (prérequis `demo.superadmin` + org smoke) | **A_VÉRIFIER** manuellement |

### 1.3 Comptes et seeds

| Jeu | Comptes | Mot de passe | Org | Seed |
|-----|---------|--------------|-----|------|
| **OF_test_2** | `apprenant_test_2`, `tuteur_test_2`, `formateur_test_2` | `demo123` | OF_test_2 | `python manage.py bootstrap_demo_test_2` |
| **Smoke Playwright** | `smoke_learner`, `smoke_tutor`, `smoke_trainer`, `smoke_coordo`, `smoke_orgadmin`, `smoke_superadmin` | `smoke-pass-2026` | Smoke Playwright Org | `bootstrap_smoke_playwright` |
| **Admin démo** | `demo.superadmin` | `demo-superadmin-2026` | Demo Hugo Org (home) | Base préexistante (non créé par smoke) |

**Groupe OF_test_2 :** `bac_pro__test_2` — 3 `GroupMembership`, 1 `TutorLearnerLink` (tuteur↔apprenant).

### 1.4 Zones fonctionnelles couvertes

| Zone | Routes clés | Personas |
|------|-------------|----------|
| Apprenant | `/app`, `/app/session/:id` | LEARNER |
| Tuteur / coordo | `/app/tutor`, `/app/tutor/group/:id` | TUTOR, COORDO |
| Formateur | `/app/trainer/knowledge`, `library`, `elicitation`, `referentials` | TRAINER |
| Admin testeur | `/dashboard`, `/users`, `/groups-admin` | ORGADMIN, SUPERADMIN |
| Superadmin | switch org navbar, `X-Organisation-Id` | SUPERADMIN |
| Référentiels | `/referentials` (tester), `/app/trainer/referentials` (prod) | encadrants, admin |

---

## 2. Plan de test détaillé (rôles × organisations × groupes × écrans)

### 2.1 Matrice multi-tenant (SUPERADMIN)

| Org active | Écran | Endpoint(s) | Attendu | Risque régression |
|------------|-------|-------------|---------|-------------------|
| Demo Hugo Org (défaut) | `/users` | `GET /users/` | Users org démo uniquement | `*_test_2` absents |
| Demo Hugo Org | `/groups-admin` | `GET /groups/` | Groupes démo (ex. bac pro melec) | OF_test_2 invisible |
| Demo Hugo Org | `/groups-admin/:id` membres | `GET /groups/{of2}/members/` | **0 membre** (filtrage tenant) | Faux « groupe vide » |
| **OF_test_2** (switcher) | `/users` | `GET /users/` + header | `*_test_2` visibles | — |
| **OF_test_2** | `/groups-admin` | `GET /groups/` | `bac_pro__test_2` seul | — |
| **OF_test_2** | `/groups-admin/:id` | `GET …/members/` | 3 memberships | — |
| **OF_test_2** | `/users/:id` | `GET /users/{id}/` + résolution groupes | Memberships affichés (post-fix UserDetailView) | — |

### 2.2 Matrice groupes par rôle (OF_test_2)

| Rôle | `GET /groups/` | `GET …/members/` | `GET …/learners/` (dashboard) | `GET /users/` |
|------|----------------|------------------|-------------------------------|---------------|
| LEARNER | `bac_pro__test_2` | N/A (self) | self only | 403 |
| TUTOR | `bac_pro__test_2` | 3 (UUID) | `apprenant_test_2` | 403 |
| TRAINER | `bac_pro__test_2` | 3 (UUID) | **[]** (écart ACL) | 403 |
| ORGADMIN OF_test_2 | tous groupes org | 3 + usernames via admin | tous learners | liste org |
| SUPERADMIN + header OF_test_2 | idem | 3 | selon ACL | liste org |

### 2.3 Matrice écrans formateur (API vs UI)

| Écran | Endpoints | Données API (formateur_test_2) | UI attendue (post-fix juin) | Contrôle régression |
|-------|-----------|--------------------------------|-----------------------------|---------------------|
| Knowledge | `/groups/`, `/referential-config/`, `/members/`, `/knowledge-items/` | 1 groupe, RNCP38878, 3 membres, 0 items | Panneau **Contexte groupe** | `data-testid=trainer-group-context` |
| Library | idem + `/library/`, `/documents/` | 0 doc lié | Sélecteur groupe + référentiel + effectif | — |
| Élicitation | atelier endpoints | — | Panneau contexte + **Retour orchestrateur** | — |
| Référentiels | `/referentials/` | 1 référentiel | Liste + contexte groupe + retour hub | — |

### 2.4 Matrice écrans tuteur (Smoke / OF_test_2)

| Écran | API | UI |
|-------|-----|-----|
| `/app/tutor` | `GET /groups/` | Cartes groupes |
| `/app/tutor/group/:id` | `GET …/learners/` | Liste usernames si TutorLearnerLink |

### 2.5 Cas limites à surveiller

- Superadmin sans switch org sur données OF_test_2.
- Formateur avec memberships en DB mais cohorte dashboard vide.
- Groupe sans documents library (0 items — état normal post-seed).
- Référentiel sans items knowledge (0 items — normal).
- `localStorage` `hugo_active_organisation_id` stale après changement de seed.

---

## 3. Scénarios persona exécutés

### 3.1 Automatisés (API — base `hugo_poc` live)

Script shell `manage.py shell` — sondage `APIClient.force_authenticate` :

| Persona | `/groups/` | `/groups/{of2}/members/` | `/dashboard/…/learners/` |
|---------|------------|--------------------------|--------------------------|
| `apprenant_test_2` | `['bac_pro__test_2']` | — | — |
| `tuteur_test_2` | idem | 3 UUID | `['apprenant_test_2']` |
| `formateur_test_2` | idem | 3 UUID | **`[]`** |
| `demo.superadmin` (sans header) | 9 groupes démo | **0** sur of2 | — |
| `demo.superadmin` + `X-Organisation-Id: OF_test_2` | `['bac_pro__test_2']` | **3** | — |
| `demo.superadmin` + header | `/users/` → 3 comptes `*_test_2` | — | — |

### 3.2 Automatisés (tests Django)

- `test_demo_test_2_seed` : memberships + `GET /groups/` par rôle.
- `test_tenant_ui_campaign` : tenant superadmin, trainer learners vide, tutor learners OK.
- `test_tutor_access_control` : isolation timeline / liens.
- `test_trainer_group_list` : TRAINER voit tous les groupes org.

### 3.3 E2E Playwright

- `test_smoke_trainer.spec.ts` : login → knowledge → item smoke → validation — **PASS** après alignement titre « Orchestrateur de connaissance » + panneau contexte.

### 3.4 Non exécutés automatiquement (manuels recommandés)

- Parcours complet `demo.superadmin` : switch Demo Hugo Org ↔ OF_test_2 sur `/users`, `/groups-admin`, wizard onboarding.
- Parcours `formateur_test_2` : library → retour orchestrateur → référentiels.
- Parcours `smoke_coordo` vs `smoke_tutor` sur `/app/tutor`.
- Protocole E2E lots 00–12 sur stack sqlite smoke.

---

## 4. Résultats API vs UI (divergences)

| ID | Persona / rôle | Org / tenant | Écran | API | UI (avant fixes) | UI (après fixes juin) | Statut |
|----|----------------|--------------|-------|-----|------------------|----------------------|--------|
| D1 | SUPERADMIN | Demo Hugo Org | `/groups-admin` (of2) | members **0** | « Aucun membre » | Idem si mauvaise org — **bandeau org** rappelle le contexte | **Comportement attendu** — doc + tests |
| D2 | SUPERADMIN | Demo Hugo Org | `/users` | pas de `*_test_2` | liste vide pour test_2 | `ActiveOrganisationBanner` + switcher | **Comportement attendu** |
| D3 | SUPERADMIN | OF_test_2 | `/users/:id` | memberships existent | pas affichés | liste groupes via `userGroupMemberships` | **CORRIGÉ** |
| D4 | TRAINER | OF_test_2 | `/app/trainer/knowledge` | groupe + réf + 3 membres | **rien** | `TrainerGroupContextPanel` | **CORRIGÉ** |
| D5 | TRAINER | OF_test_2 | cohorte apprenants | members 3 UUID ; learners **[]** | pas de noms | effectif **count** seulement | **Écart résiduel** (ACL + serializer) |
| D6 | TUTOR | OF_test_2 | `/app/tutor` | 1 groupe | carte groupe | OK | **ALIGNE** |
| D7 | LEARNER | OF_test_2 | `/app` | 1 groupe | sélecteur groupe | OK | **ALIGNE** |
| D8 | TRAINER | Smoke | Playwright smoke | knowledge item | titre obsolète test | titre + testid contexte | **CORRIGÉ** (test) |

---

## 5. Corrections simples appliquées (front / tests)

### 5.1 Sessions précédentes (contexte campagne)

| Fichier | Correction |
|---------|------------|
| `UserDetailView.vue` + `userGroupMemberships.js` | Affichage memberships + bandeau org superadmin |
| `TrainerGroupContextPanel.vue` + `useTrainerGroupContext.js` | Contexte groupe/référentiel/effectif formateur |
| `TrainerBackToOrchestratorLink.vue` | Navigation « Retour orchestrateur » |

### 5.2 Campagne 30/06

| Fichier | Pourquoi |
|---------|----------|
| `hugo_back/apps/accounts/tests/test_tenant_ui_campaign.py` | Verrouille tenant superadmin, trainer/tutor learners, memberships |
| `tests_playwright/test_smoke_trainer.spec.ts` | Aligné sur UI réelle (titre orchestrateur + `trainer-group-context`) |

---

## 6. Incohérences majeures détectées

### INC-01 — Tenant superadmin silencieux

- **Symptôme :** données OF_test_2 « absentes » pour superadmin.
- **Cause :** `tenant_organisation_id()` = org home sauf header superadmin.
- **Correctif 30/06 PM :** bandeau `ActiveOrganisationBanner` — texte explicite OF_test_2 / `*_test_2` + `X-Organisation-Id` (INC-01 quick win). Tests inchangés (`test_tenant_ui_campaign`).

### INC-02 — Formateur : cohorte dashboard vide malgré memberships

- **Statut :** **OUVERT — non modifié** (décision CTO). Voir `memo_cto_2026-06-30.md`.

### INC-03 — Serializer memberships sans profil utilisateur

- **Correctif 30/06 PM :** champs `user_username`, `user_role` sur `GroupMembershipSerializer` ; roster visible formateur + fallback `GroupAdminDetailView`. Test `test_membership_payload_includes_username_and_role`.

### INC-04 — Deux bases locales (hugo_poc vs sqlite_test)

- **Correctif 30/06 PM :** log `hugo.runtime` au démarrage ; `manage.py print_runtime_stack` ; `scripts/which-hugo-stack.sh` ; bandeau `run_local_hugo.sh`. Doc fiche 11.

### INC-05 — Playwright protocole : config obligatoire

- **Correctif 30/06 PM :** `npm run test:e2e` dans `package.json`. Doc fiche 11.

---

## 7. Tests ajoutés / adaptés

| Fichier | Couverture |
|---------|------------|
| `apps/accounts/tests/test_tenant_ui_campaign.py` | 9 tests : tenant, memberships serializer, trainer/tutor learners |
| `app_core/tests/test_runtime_stack.py` | **Nouveau** — descriptor postgres/sqlite |
| `tests_playwright/test_smoke_trainer.spec.ts` | **Adapté** — titre + panneau contexte |
| `src/utils/trainerGroupContext.test.js` | 6 tests (+ roster) |

**Bilan exécution (post quick wins PM) :**

- Backend campagne + runtime_stack : **12 PASS**
- Front unit : **53 PASS**
- Playwright trainer smoke : **1 PASS** (`npm run test:e2e -- test_smoke_trainer`)

---

## 8. Vérifications manuelles restantes

Checklist pour validation humaine :

- [ ] `demo.superadmin` : switch **OF_test_2** → `/users` montre les 3 `*_test_2` ; `/groups-admin` → `bac_pro__test_2` → 3 membres.
- [ ] `demo.superadmin` : switch retour **Demo Hugo Org** → pas de fuite `bac_pro__test_2` (cf. lot01 Playwright).
- [ ] `formateur_test_2` : knowledge affiche panneau contexte (groupe, RNCP38878, 3 comptes).
- [ ] `formateur_test_2` : library + élicitation + référentiels — bouton **Retour orchestrateur** → `/app/trainer/knowledge`.
- [ ] `tuteur_test_2` : `/app/tutor` → voir apprenant lié.
- [ ] `apprenant_test_2` : `/app` → groupe sélectionnable.
- [ ] Relancer protocole E2E complet : `npm run test:protocol` avec backend + `bootstrap_smoke_playwright`.
- [ ] Confirmer quelle DB est active avant démo (`hugo_poc` vs sqlite_test).

---

## Checklist finale campagne

| Critère | Statut |
|---------|--------|
| Effets tenant actif sur vues admin testés et compris | **OUI** — tests + doc INC-01 |
| Groupes et rattachements vérifiés par rôle | **OUI** — seed tests + campagne API |
| Espaces formateur / tuteur / apprenant vs API | **PARTIEL+** — formateur voit roster memberships (username/role) ; dashboard learners TRAINER toujours vide (INC-02) |
| Incohérences groupes / org / rôles détectées | **OUI** — INC-01 à INC-05 |
| Erreurs front simples corrigées | **OUI** — contexte formateur, user detail, navigation, test smoke |
| Problèmes structurels documentés | **OUI** — ACL trainer, serializer, dual DB |

---

## Prochaine sortie utile

1. **Décision CTO INC-02** — voir `memo_cto_2026-06-30.md`.
2. **E2E P2 :** spec Playwright `formateur_test_2` + switch superadmin OF_test_2.
3. ~~OPS stacks locales~~ — quick wins INC-04 appliqués (`which-hugo-stack.sh`, `print_runtime_stack`).

---

*Généré le 30/06/2026 — mis à jour 30/06/2026 PM (quick wins INC-01/03/04/05).*
