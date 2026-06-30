# Matrice rôle × visibilité v2 (C9-DOC-03)

> Domaines 90 + 100 + 110 (lecture transverse)  
> Basée sur code backend, tests D2-M07, smokes Playwright cluster 8, cluster 10  
> Date : 2026-06-18

---

## Tableau principal

| Rôle | Verbatims session | Traces / preuves | Exports org (JSON / CSV / bundle) | Observabilité |
|------|-------------------|------------------|-----------------------------------|---------------|
| **LEARNER** | Voit **sa** session (messages complets en workspace apprenant) | Voit ses traces/évidences via parcours apprenant | **Non** — 403 API, pas de CTA UI | **Non** — signaux qualité non exposés UI |
| **TUTOR** | **Non** si `share_verbatim=false` (timeline : messages vides, preview vide) | Timeline : id trace, dates, validation ; validation trace si autorisé | **Non** — 403 | **Non** — pas d’endpoint internal org |
| **TRAINER** | **Non** (pas d’accès timeline apprenant non lié) | Knowledge items org ; pas lecture libre verbatim apprenant | **Non** — 403 | **Non** |
| **ORGADMIN** | **Non** si non partagé (même doctrine B1-01) | Exports + observabilité session org | **Oui** — ExportRun, EvidenceBundle | **Oui** — `/internal/.../observability/` (session org) |
| **SUPERADMIN** | Idem ORGADMIN sur périmètre org | Idem + analytics techniques | **Oui** (via `is_admin_like`) | **Oui** + D9bis build/export, conversation-summary (internal) |
| **COORDO** | **CIBLE 2.0** — non implémenté | — | — | — |

---

## Détail exports (RÉEL OBSERVÉ)

| Endpoint | Guard backend | ORGADMIN | SUPERADMIN | TUTOR / TRAINER / LEARNER |
|----------|---------------|----------|------------|---------------------------|
| `POST /exports/run/` | `is_admin_like` | 200 | 200 | 403 |
| `POST /quality/qualiopi/evidence-bundle/` | `is_admin_like` | 200 | 200 | 403 |
| `GET /internal/.../d9bis/*` | `is_superadmin` | 403 | 200 | 403 |
| `GET /internal/.../conversation-summary/` | `is_superadmin` | 403 | 200 | 403 |
| `GET /internal/.../observability/` | ORGADMIN+ / tuteur lié | 200 (org) | 200 | 403 ou 404 selon lien |

Front : `GroupView.canRunExports` → `isOrgAdminLike` (smoke cluster 8 : LEARNER sans CTA).

---

## RLS / multi-tenant

| Niveau | RÉEL OBSERVÉ local | A_VÉRIFIER |
|--------|-------------------|------------|
| Policies Postgres | Actives sur `hugo_session`, `trace`, `evidence`, `export_run` | Prod avec rôle applicatif dédié |
| Isolation API | User org A → session org B → **404** | Encoors |
| Isolation SQL rôle `hugo_app_tenant_test` | **PASS** (cluster 10, SET ROLE) | Prod (mot de passe / rôle réel) |

---

## Limites de cette matrice

- **Encoors** : parité non authentifiée au moment cluster 10 ; surfaces UI distantes **A_VÉRIFIER**.
- **RLS prod** : test SQL local avec rôle dédié ≠ preuve sur l’instance Encoors.
- **COORDO** : personae cible specs interface 2.0, absent du code.
- **D2-M12** : ORGADMIN et SUPERADMIN partagent `is_admin_like` sur exports org — voir ADR `adr_c9_code03_exports_orgadmin_superadmin.md`.

---

## Références

- `access_control.py`, `views_dashboard.py`, `exports/views.py`, `quality/views.py`
- `test_d2_m07_confidentiality_oracles.py`, `test_rls_postgres_minimal.py`
- `ecarts — 90_confidentialite_partage_multitenant_roles.md`

---

## Annexe cluster 14 — écrans front ↔ rôles (RÉEL OBSERVÉ)

| Route | Layout | Rôles guard | Données sensibles |
|-------|--------|-------------|-------------------|
| `/app/tutor/*` | prod | `isTutorLike` (TUTOR, TRAINER, COORDO, admin) | Timeline ; pas verbatim non partagé |
| `/app/trainer/knowledge` | prod | `isTrainerLike` | Knowledge items |
| `/groups-admin/*` | tester | `isOrgAdminLike` | Exports E4, gestion groupe |
| `/dashboard`, `/group/*` | tester | encadrant | Timeline legacy |
| Observabilité session | — | **Aucune UI** | API `/internal/.../observability/` seulement |

Voir `cluster14_interfaces_encadrants_observabilite_plan_resultats.md`.
