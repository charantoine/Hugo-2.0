# Seeds de démonstration / test (hors smoke Playwright)

**Documentation workspace :** `docs-workspace/seed-strategies.md` (vue consolidée — stratégies, commandes, vigilances).

## Modèle relationnel (réel, backend)

| Lien | Mécanisme | Table / champ |
|------|-----------|----------------|
| Utilisateur → organisation | FK directe | `accounts.User.organisation` (obligatoire) |
| Utilisateur → groupe | **Indirect** | `referentials.GroupMembership` (`group` + `user`, unique) |
| Tuteur → apprenant (dans un groupe) | **Indirect** | `referentials.TutorLearnerLink` (`group`, `tutor`, `learner`) |
| Groupe → référentiel | Config | `referentials.ReferentialConfig` (`group` → `referential`) |
| Groupe → profil conversationnel | FK | `referentials.Group.default_learner_conversation_profile` |

**Règles API confirmées :**

- `POST /users/` (admin) crée l’utilisateur avec `organisation` mais **pas** de `GroupMembership` — rattachement groupe = `POST /groups/{id}/members/` ou seed.
- `GET /groups/` :
  - **apprenant** : groupes où il a une `GroupMembership` ;
  - **tuteur / coordo** : intersection membership **et** `TutorLearnerLink` vers au moins un apprenant ;
  - **formateur** : tous les groupes de l’organisation (aligné avec la lecture bibliothèque org-wide) ;
  - **admin** : tous les groupes de l’organisation.

Helpers partagés : `apps/accounts/seeds/group_attachments.py` (`ensure_group_membership`, `ensure_tutor_learner_link`).

## `bootstrap_demo_test_2`

Jeu de comptes liés pour bêta testeurs externes :

| Élément | Valeur |
|---------|--------|
| Organisation | `OF_test_2` |
| Groupe | `bac_pro__test_2` |
| Apprenant | `apprenant_test_2` |
| Tuteur | `tuteur_test_2` |
| Formateur | `formateur_test_2` |
| Mot de passe | `demo123` |
| Référentiel | `RNCP38878` (fixture enrichie) |
| Profil conversationnel | clone de `profil_conversationnel_mk1` (suffixe interne mk1) |

### Source de vérité « mk1 »

`mk1` n’est **pas** un concept métier : c’est un **suffixe de version** sur les fixtures de `Demo Hugo Org`
(`profil_conversationnel_mk1`, `diagnostic_mk1`, etc.). Voir `docs-workspace/VERIF_SUFFIXE_MK1_MK2_2026-06-26.md`.

Le seed clone le profil global et ses prompts/conduites depuis :

1. `profil_conversationnel_mk1` dans l’org source, sinon
2. profil par défaut du groupe `bac pro melec`, sinon
3. profil de la dernière session de `apprenant_melec_1` (alias documenté ; `apprenant_test_1` n’existe pas en repo).

### Rattachements créés

1. `User.organisation` = `OF_test_2` pour les 3 comptes.
2. `GroupMembership` pour apprenant, tuteur et formateur sur `bac_pro__test_2`.
3. `TutorLearnerLink` tuteur ↔ apprenant (le formateur n’a pas de lien tuteur — accès groupe via règle formateur).
4. `ReferentialConfig` groupe → `RNCP38878`.
5. Clone profil conversationnel + `group.default_learner_conversation_profile`.

### Idempotence

- Org / groupe / users : `get_or_create` + `set_password(demo123)` à chaque run.
- Référentiel : réutilise le premier `RNCP38878` de l’org, sauf `--force-reimport-referential`.
- Profil / prompts : `update_or_create` par clés stables (`organisation` + `code` / `name`).

### Seeds existants (ne pas confondre)

| Commande | Usage |
|----------|--------|
| `bootstrap_smoke_playwright` | E2E Playwright (`smoke_*`, org Smoke) |
| `bootstrap_multitenant_smoke` | Tests multi-tenant |
| `bootstrap_profile_migration_smoke` | Migration profils conversationnels |
| `bootstrap_orgadmin` | Création ad hoc org + admin |
| `bootstrap_demo_test_2` | **Ce scénario** — démo test_2 liée |
