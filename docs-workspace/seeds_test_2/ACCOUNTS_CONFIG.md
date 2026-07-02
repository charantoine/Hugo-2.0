# ACCOUNTS_CONFIG — seeds_test_2

Date de generation : 2026-07-02

| Compte / Tenant | Role | Email | Prompts mk1 associes | Notes |
|---|---|---|---|---|
| Demo Hugo Org / demo.superadmin | SUPERADMIN | demo.superadmin@demo.local | N/A | superadmin recurrent observe dans scripts |
| OF_test_2 / apprenant_test_2 | LEARNER | (vide) | profil_conversationnel_mk1 (`diagnostic_mk1`, `reflexif_mk1`, `buchage_mk1`) | seed `demo_test_2` |
| OF_test_2 / tuteur_test_2 | TUTOR | (vide) | profil_conversationnel_mk1 (`diagnostic_mk1`, `reflexif_mk1`, `buchage_mk1`) | lien tuteur-apprenant sur `bac_pro__test_2` |
| OF_test_2 / formateur_test_2 | TRAINER | (vide) | profil_conversationnel_mk1 (`diagnostic_mk1`, `reflexif_mk1`, `buchage_mk1`) | membre du groupe `bac_pro__test_2` |
| orga_test_2 / superadmin_test_2 | SUPERADMIN | (vide) | N/A | seed `personas_test_2` |
| orga_test_2 / orgadmin_test_2 | ORGADMIN | (vide) | N/A | seed `personas_test_2` |
| orga_test_2 / coordo_test_2 | COORDO | (vide) | N/A | seed `personas_test_2` |
| orga_test_2 / trainer_test_2 | TRAINER | (vide) | N/A | seed `personas_test_2` |
| orga_test_2 / tutor_test_2 | TUTOR | (vide) | N/A | seed `personas_test_2` |
| orga_test_2 / learner_test_2_a | LEARNER | (vide) | N/A | seed `personas_test_2` |
| orga_test_2 / learner_test_2_b | LEARNER | (vide) | N/A | groupe secondaire inclus |

## Champs structurants confirms
- `User.username` (unique)
- `User.role` (`SUPERADMIN`, `ORGADMIN`, `COORDO`, `TRAINER`, `TUTOR`, `LEARNER`)
- `User.is_superuser`, `User.is_staff`, `User.is_active`
- `User.organisation` (tenant via `Organisation`)
- `GroupMembership` et `TutorLearnerLink` pour les relations de groupe

## Password seed
- Tous les scripts du kit utilisent :
  - `os.environ.get("SEED_PASSWORD", "hugo_test_2!")`
