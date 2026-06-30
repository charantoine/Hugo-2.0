# Stratégies de seed — Workspace Hugo

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Dernière révision :** 30 juin 2026  
**Public :** dev, QA, animateur de démo, CTO  
**Complète :** `11_FICHE_COMPTES_ET_DONNEES_DEMO.md`, `hugo_back/apps/accounts/seeds/README.md`

---

## 1. Contexte

Le backend Hugo (`hugo_back`) ne repose **pas** sur un jeu de fixtures Django unique chargé au démarrage. Les données de démo et de test sont produites par des **commandes de management** idempotentes (`bootstrap_*`), chacune ciblant un scénario précis (E2E Playwright, multi-tenant, bêta testeurs externes, etc.).

**Principe de vérité :** le modèle relationnel réel prime sur toute hypothèse « user lié directement au groupe ». Voir §3.

**Hypothèse documentaire :** ce fichier consolide l’état observé dans le code au **30/06/2026**. Dernier dépôt GitHub confirmé : **20/06/2026** — la commande `bootstrap_demo_test_2` et les helpers associés sont **post-push** (voir `memo-cto-depuis-dernier-push.md`). Les UUID générés varient selon la base ; seuls les **noms stables** (org, groupe, usernames) sont garantis par les seeds.

---

## 2. Modèle relationnel réel (rattachements)

| Lien | Mécanisme | Table / champ |
|------|-----------|----------------|
| Utilisateur → organisation | FK directe, obligatoire | `accounts.User.organisation` |
| Utilisateur → groupe | **Indirect** | `referentials.GroupMembership` — unique `(group, user)` |
| Tuteur → apprenant (dans un groupe) | **Indirect** | `referentials.TutorLearnerLink` — `(organisation, group, tutor, learner)` |
| Groupe → référentiel | Config | `referentials.ReferentialConfig` |
| Groupe → profil conversationnel | FK | `Group.default_learner_conversation_profile` |

### Règles API liées (hors seed)

| Endpoint / comportement | Règle observée |
|-------------------------|----------------|
| `POST /users/` (admin) | Crée `User.organisation` ; **ne crée pas** de `GroupMembership` |
| `POST /groups/{id}/members/` | Crée le membership (miroir seed) |
| `GET /groups/` — apprenant | Groupes où `GroupMembership` existe |
| `GET /groups/` — tuteur / coordo | Intersection membership **et** `TutorLearnerLink` actif |
| `GET /groups/` — formateur | Tous les groupes de l’organisation tenant (aligné lecture biblio org-wide) |
| `GET /groups/` — admin | Tous les groupes de l’organisation |

**Source code :** `apps/referentials/views_groups.py`, `apps/accounts/serializers.py`, `apps/library/views.py` (`_can_read_group_library`).

**Helpers seed canoniques :** `hugo_back/apps/accounts/seeds/group_attachments.py`

- `ensure_group_membership(organisation, group, user)`
- `ensure_tutor_learner_link(organisation, group, tutor, learner)`

---

## 3. Mécanismes existants

### 3.1 Commandes `bootstrap_*` (actives)

| Commande | Scénario | Mot de passe | Fixtures JSON générées |
|----------|----------|--------------|------------------------|
| `bootstrap_smoke_playwright` | E2E Playwright, org **Smoke Playwright Org**, comptes `smoke_*` | `smoke-pass-2026` | `tests_playwright/smoke-fixtures.json`, `docs-workspace/smoke-fixtures.generated.json` |
| `bootstrap_profile_migration_smoke` | Profils conversationnels / migration (réutilise `smoke_learner`) | `smoke-pass-2026` | `tests_playwright/profile-smoke-fixtures.json` |
| `bootstrap_multitenant_smoke` | Tests multi-tenant (2 orgs, comptes `tenant_*`) | `tenant-smoke-2026` | `tests_playwright/tenant-smoke-fixtures.json` |
| `bootstrap_orgadmin` | Org + admin ad hoc (CLI) | argument `--password` | — |
| `bootstrap_demo_test_2` | Bêta testeurs externes — org **OF_test_2** | `demo123` | `docs-workspace/demo-test-2-fixtures.generated.json` (avec `--write-fixtures`) |

**Emplacement :** `hugo_back/apps/accounts/management/commands/`

### 3.2 Modules seed Python (actifs)

| Module | Rôle |
|--------|------|
| `apps/accounts/seeds/demo_test_2.py` | Orchestration scénario OF_test_2 |
| `apps/accounts/seeds/demo_test_2_constants.py` | Noms stables (org, groupe, users) |
| `apps/accounts/seeds/group_attachments.py` | Memberships et liens tuteur (partagé) |
| `apps/accounts/seeds/referential_rncp38878.py` | Import / réutilisation RNCP38878 |
| `apps/accounts/seeds/clone_conversation_profile.py` | Clone profil global + prompts depuis org source |

### 3.3 Fixtures Django statiques

| Emplacement | Usage |
|-------------|--------|
| `apps/referentials/fixtures/` | Données RNCP enrichies (import référentiel) |
| Fixtures générées `*.generated.json` | **IDs runtime** pour tests E2E — ne pas éditer à la main sauf régénération |

### 3.4 Scripts legacy / fragiles

| Fichier | Statut | Recommandation |
|---------|--------|----------------|
| `hugo_back/scripts/restore_rncp38878_smoke.py` | **Obsolète partiel** — IDs hardcodés, hors commande manage.py | Ne pas utiliser pour un nouveau scénario ; préférer `referential_rncp38878.py` via `bootstrap_demo_test_2` |

### 3.5 Données non seedées (instance locale typique)

| Élément | Source | Confiance |
|---------|--------|-----------|
| `demo.superadmin` | Base préexistante / import manuel | Haute (login documenté) — **non** créé par `bootstrap_smoke_playwright` |
| Comptes `apprenant_melec_*`, `tuteur_melec_*` | Demo Hugo Org historique | Noms en base ; **mots de passe non documentés** |
| Org **Demo Hugo Org** | Seed / import antérieur | Référence pour clone profil mk1 |

---

## 4. Séparation des stratégies

| Type | Commande(s) | Quand l’utiliser |
|------|-------------|------------------|
| **Référence E2E / CI** | `bootstrap_smoke_playwright` (+ `bootstrap_profile_migration_smoke` si profils) | Playwright, protocole E2E, régression interfaces |
| **Référence multi-tenant** | `bootstrap_multitenant_smoke` | Tests `SMOKE_RUN_TENANT=1` |
| **Scénario métier bêta** | `bootstrap_demo_test_2` | Testeurs externes, org isolée OF_test_2 |
| **Ad hoc admin** | `bootstrap_orgadmin` | Création rapide org + ORGADMIN sans jeu complet |
| **Données prod / melec** | Aucun seed repo complet | Parcours onboarding admin avec `demo.superadmin` sur base existante |

**Ne pas mélanger** les mots de passe (`smoke-pass-2026` vs `demo123` vs `tenant-smoke-2026`) dans la même checklist démo sans relabeling explicite.

---

## 5. Stratégie recommandée aujourd’hui

### 5.1 Démo locale / QA (baseline B)

```bash
cd hugo_back
python manage.py migrate
python manage.py bootstrap_smoke_playwright
# Optionnel — parcours profils conversationnels :
python manage.py bootstrap_profile_migration_smoke
```

Comptes : `smoke_*` / `smoke-pass-2026` — détail doc **11** §3.1.

### 5.2 Bêta testeurs externes (org isolée)

```bash
cd hugo_back
python manage.py migrate
python manage.py bootstrap_demo_test_2 --write-fixtures
```

| Élément | Valeur |
|---------|--------|
| Organisation | `OF_test_2` |
| Groupe | `bac_pro__test_2` |
| Apprenant | `apprenant_test_2` |
| Tuteur | `tuteur_test_2` |
| Formateur | `formateur_test_2` |
| Mot de passe | `demo123` |
| Référentiel | `RNCP38878` |
| Profil conversationnel | clone `profil_conversationnel_mk1` (suffixe interne — voir `VERIF_SUFFIXE_MK1_MK2_2026-06-26.md`) |

**Prérequis clone profil :** l’org source **Demo Hugo Org** doit exister en base (profil mk1 ou fallback documenté dans `apps/accounts/seeds/README.md`).

### 5.3 Vérification post-seed

```bash
# Tests ciblés rattachements OF_test_2
python manage.py test apps.accounts.tests.test_demo_test_2_seed

# ACL formateur GET /groups/
python manage.py test apps.referentials.tests.test_trainer_group_list
```

---

## 6. Idempotence et rejouabilité

| Mécanisme | Comportement |
|-----------|--------------|
| Org / groupe / users | `get_or_create` ; `set_password` à chaque run |
| `GroupMembership` | `update_or_create(group, user)` — resynchronise `organisation_id` |
| `TutorLearnerLink` | `get_or_create` sur clé complète |
| `ReferentialConfig` | `update_or_create` par `group` |
| RNCP38878 | Réutilise le premier `RNCP38878` de l’org sauf `--force-reimport-referential` |
| Profil / prompts clonés | `update_or_create` par clés stables (`organisation` + `code` / `name`) |

**Réexécution :** toutes les commandes `bootstrap_*` ci-dessus sont **safe** à relancer sur la même base.

---

## 7. Points de vigilance

| Sujet | Risque | Mitigation |
|-------|--------|------------|
| User admin sans membership | UI « non rattaché au groupe » | `POST /groups/{id}/members/` ou seed |
| Tuteur sans `TutorLearnerLink` | `GET /groups/` vide pour tuteur | Créer le lien (seed ou superadmin) |
| Superadmin inspecte OF_test_2 | Listes vides sans switch org | Sélecteur navbar → **OF_test_2** (header `X-Organisation-Id`) — voir `memo_cto_2026-06-30.md` |
| Stack locale incorrecte | Comptes `*_test_2` absents | Vérifier `python manage.py print_runtime_stack` ou `./scripts/which-hugo-stack.sh` — dev = `hugo_poc` |
| Formateur avant correction ACL (juin 2026) | Dropdown groupe vide malgré membership | Code actuel : formateur voit tous les groupes org — **A_VÉRIFIER** sur Encoors |
| UUID fixtures JSON | Divergence si autre DB | Régénérer avec `--write-fixtures` ou bootstrap smoke |
| `demo.superadmin` | Absent sur DB vierge | Import manuel ou autre seed — pas le smoke |
| Org source mk1 absente | Clone profil skippé | Message `profile_clone_source: skipped_*` dans la sortie commande |
| `restore_rncp38878_smoke.py` | IDs obsolètes | Ne pas réutiliser |

---

## 8. Tests associés

| Fichier | Couverture |
|---------|------------|
| `apps/accounts/tests/test_demo_test_2_seed.py` | Rattachements OF_test_2 + `GET /groups/` par rôle |
| `apps/accounts/tests/test_tenant_ui_campaign.py` | Tenant superadmin, serializer memberships, trainer/tutor learners |
| `apps/referentials/tests/test_trainer_group_list.py` | Formateur sans tutor-link |
| `apps/referentials/tests/test_group_visibility_by_tutor_links.py` | Tuteur filtré par liens |
| Tests Playwright | Consomment `smoke-fixtures.json` — voir `tests_playwright/README.md` |

---

## 9. Prochaines améliorations recommandées

| Priorité | Action |
|----------|--------|
| DOC | Aligner `bootstrap_smoke_playwright` sur `group_attachments.py` (même helper que demo_test_2) |
| DOC / OPS | Documenter procédure création `demo.superadmin` sur DB vierge |
| CODE | Déprécier formellement `scripts/restore_rncp38878_smoke.py` |
| OPS | Vérifier seeds sur baseline Encoors (**A_VÉRIFIER**) |
| CODE | Membership automatique optionnel à la création user admin — **hors périmètre actuel** (changement métier) |

---

## 10. Renvois

| Sujet | Document / code |
|-------|-----------------|
| Comptes et parcours | `11_FICHE_COMPTES_ET_DONNEES_DEMO.md` |
| Détail technique seed test_2 | `hugo_back/apps/accounts/seeds/README.md` |
| Suffixe mk1 / mk2 | `VERIF_SUFFIXE_MK1_MK2_2026-06-26.md` |
| Mémo CTO récent | `memo-cto-depuis-dernier-push.md` |
| Passe doc juin 2026 | `DOC_RUNTIME_UPDATE_2026-06-30.md` |

---

*Stratégies de seed — ancrage code `hugo_back` juin 2026.*
