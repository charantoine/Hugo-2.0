# Comptes test — 1 juillet 2026

**Inspection :** 2026-07-01  
**Stack Firefox observée :** `http://localhost:5173` → proxy `/api` → backend `http://127.0.0.1:8000`  
**Base active :** `config.settings.sqlite_test` → `hugo_back/test.sqlite3` (`REL OBSERV` via `print_runtime_stack`)  
**Tag global :** `REL OBSERV` (baseline B locale) — ne pas extrapoler à Encoors / postgres `hugo_poc`

---

## Contexte Firefox

Onglets ouverts sur `localhost:5173` (formateur, apprenant, login).  
Le backend local tourne en **sqlite_test** (script `./run_local_hugo.sh`), **pas** en PostgreSQL `hugo_poc`.

Les UUID de session visibles dans l’URL Firefox (`288537cc-…`, `8f0c4727-…`) **ne sont pas présents** dans `test.sqlite3` au moment de l’inspection → onglets probablement issus d’une session antérieure ou d’une autre base. Seuls les comptes ci-dessous sont **authentifiables** sur le stack actuel.

**Login :** `http://localhost:5173/login`

---

## Inventaire — comptes actifs (`is_active=True`) sur le stack Firefox actuel

19 comptes · 3 organisations.

### Organisation `Smoke Playwright Org` — mot de passe commun `smoke-pass-2026`

Seed : `bootstrap_smoke_playwright` · documenté dans `run_local_hugo.sh`

| Utilisateur | Rôle | Mot de passe | Auth vérifiée |
|-------------|------|--------------|---------------|
| `smoke_superadmin` | SUPERADMIN | `smoke-pass-2026` | Oui |
| `smoke_orgadmin` | ORGADMIN | `smoke-pass-2026` | Oui |
| `smoke_coordo` | COORDO | `smoke-pass-2026` | Oui |
| `smoke_trainer` | TRAINER | `smoke-pass-2026` | Oui |
| `smoke_tutor` | TUTOR | `smoke-pass-2026` | Oui |
| `smoke_learner` | LEARNER | `smoke-pass-2026` | Oui |

**Usage typique :** smoke Playwright, démo rapide (`run_local_hugo.sh` affiche `smoke_learner / smoke-pass-2026`).

---

### Organisation `orga_test_2` — mot de passe commun `demo123`

Seed : `bootstrap_personas_test_2` · constantes `personas_test_2_constants.py`

| Utilisateur | Rôle | Mot de passe | Auth vérifiée |
|-------------|------|--------------|---------------|
| `superadmin_test_2` | SUPERADMIN | `demo123` | Oui |
| `orgadmin_test_2` | ORGADMIN | `demo123` | Oui |
| `coordo_test_2` | COORDO | `demo123` | Oui |
| `trainer_test_2` | TRAINER | `demo123` | Oui |
| `tutor_test_2` | TUTOR | `demo123` | Oui |
| `learner_test_2_a` | LEARNER | `demo123` | Oui |
| `learner_test_2_b` | LEARNER | `demo123` | Oui |

**Groupes seed :** `groupe_test_2_principal`, `groupe_test_2_secondaire`

---

### Organisation `Audit Pass1 Org` — mot de passe commun `morning-reconf-pass`

Seed : fixtures pytest `morning_reconf_fixtures.py` (créés lors des runs de tests)

| Utilisateur | Rôle | Mot de passe | Auth vérifiée |
|-------------|------|--------------|---------------|
| `morning_superadmin` | SUPERADMIN | `morning-reconf-pass` | Oui |
| `morning_orgadmin` | ORGADMIN | `morning-reconf-pass` | Oui |
| `morning_coordo` | COORDO | `morning-reconf-pass` | Oui |
| `morning_trainer` | TRAINER | `morning-reconf-pass` | Oui |
| `morning_tutor` | TUTOR | `morning-reconf-pass` | Oui |
| `morning_learner` | LEARNER | `morning-reconf-pass` | Oui |

---

## Comptes **non** accessibles sur le stack Firefox actuel

Ces comptes existent sur **PostgreSQL `hugo_poc`** (`config.settings.dev`) mais **pas** sur `sqlite_test` tant que `./run_local_hugo.sh` est utilisé :

| Utilisateur | Rôle | Organisation | Mot de passe (si seed présent) |
|-------------|------|--------------|--------------------------------|
| `apprenant_test_2` | LEARNER | OF_test_2 | `demo123` |
| `tuteur_test_2` | TUTOR | OF_test_2 | `demo123` |
| `formateur_test_2` | TRAINER | OF_test_2 | `demo123` |

Voir `docs-workspace/11_FICHE_COMPTES_TEST_2.md` pour le détail postgres.

---

## Vérification rapide

```bash
curl -s -X POST http://127.0.0.1:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"trainer_test_2","password":"demo123"}'
```

```bash
cd hugo_back
DJANGO_SETTINGS_MODULE=config.settings.sqlite_test python manage.py shell -c "
from django.contrib.auth import authenticate
print(authenticate(username='smoke_learner', password='smoke-pass-2026'))
"
```

---

## Régénération des mots de passe

| Périmètre | Commande |
|-----------|----------|
| Smoke | `DJANGO_SETTINGS_MODULE=config.settings.sqlite_test python manage.py bootstrap_smoke_playwright` |
| orga_test_2 | `DJANGO_SETTINGS_MODULE=config.settings.sqlite_test python manage.py bootstrap_personas_test_2` |
| morning_* | recréés par les tests pytest utilisant `morning_reconf_fixtures` |

---

## Sources mobilisées

- `run_local_hugo.sh` (`REL OBSERV`)
- Requête DB `test.sqlite3` + `authenticate()` — 2026-07-01 (`REL OBSERV`)
- `POST /auth/login/` HTTP 200 sur `trainer_test_2`, `smoke_trainer`, `morning_trainer` (`REL OBSERV`)
- Onglets Firefox `localhost:5173` (`REL OBSERV PARTIEL` — sessions URL non retrouvées en base)

## À VÉRIFIER

- Identité exacte de l’utilisateur connecté dans chaque onglet Firefox (cookies non inspectés) — se reconnecter via `/login` avec les comptes ci-dessus.
- Parité si le backend est relancé en `config.settings.dev` (postgres) : la liste des comptes change.
