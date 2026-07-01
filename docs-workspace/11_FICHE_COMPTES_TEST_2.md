# Fiche comptes `*_test_2` — baseline B locale

> Fiche **dédiée** aux comptes suffixés `*_test_2` (et personas associés `learner_test_2_*`).
> Ne pas confondre avec la fiche comptes démo globale (`11_FICHE_COMPTES_ET_DONNEES_DEMO.md`) ni avec Encoors.

**Dernière inspection :** 2026-07-01  
**Méthode :** requêtes Django sur les deux bases locales + `check_password` / `authenticate` + `POST /auth/login/` sur backend `:8000` (sqlite).

---

## Contexte

- Deux seeds `*_test_2` coexistent en local, sur **deux bases distinctes** :
  - **`config.settings.dev` → PostgreSQL `hugo_poc`** : campagne bêta externe **OF_test_2** (3 comptes, noms français).
  - **`config.settings.sqlite_test` → `test.sqlite3`** : personas baseline B **orga_test_2** (7 comptes, noms anglais pour les rôles staff).
- La base **qui fait foi pour le dev campagne / postgres** est `hugo_poc` (`config.settings.dev`).
- Le stack lancé par `./run_local_hugo.sh` utilise **`sqlite_test`** : les comptes OF_test_2 ne sont **pas** visibles sur ce backend tant qu’on n’utilise pas `config.settings.dev`.
- Mots de passe : convention unique documentée dans le code — **`demo123`** (`demo_test_2_constants.py`, `personas_test_2_constants.py`). Réinitialisables sans impact prod.
- **Ne pas extrapoler** ces identifiants à Encoors ou à un autre environnement.

---

## Inventaire — PostgreSQL `hugo_poc` (`config.settings.dev`)

Organisation : **OF_test_2**  
Seed : `python manage.py bootstrap_demo_test_2`  
Constantes : `hugo_back/apps/accounts/seeds/demo_test_2_constants.py`  
Fixtures générées : `docs-workspace/demo-test-2-fixtures.generated.json`

| username | role | organisation | mot_de_passe | preuve |
|----------|------|--------------|--------------|--------|
| `apprenant_test_2` | LEARNER | OF_test_2 | `demo123` | constante seed + `check_password` + `authenticate` OK |
| `tuteur_test_2` | TUTOR | OF_test_2 | `demo123` | idem |
| `formateur_test_2` | TRAINER | OF_test_2 | `demo123` | idem |

**Pattern SQL :** `username LIKE '%_test_2'` → 3 lignes (2026-07-01).

---

## Inventaire — SQLite baseline B (`config.settings.sqlite_test`)

Organisation : **orga_test_2**  
Seed : `scripts/bootstrap_personas_test_2.sh` ou `python manage.py bootstrap_personas_test_2`  
Constantes : `hugo_back/apps/accounts/seeds/personas_test_2_constants.py`  
Fixtures générées : `docs-workspace/personas-test-2-fixtures.generated.json`

| username | role | organisation | mot_de_passe | preuve |
|----------|------|--------------|--------------|--------|
| `superadmin_test_2` | SUPERADMIN | orga_test_2 | `demo123` | constante seed + `check_password` OK |
| `orgadmin_test_2` | ORGADMIN | orga_test_2 | `demo123` | idem |
| `coordo_test_2` | COORDO | orga_test_2 | `demo123` | idem |
| `trainer_test_2` | TRAINER | orga_test_2 | `demo123` | idem + `POST /auth/login/` 200 |
| `tutor_test_2` | TUTOR | orga_test_2 | `demo123` | idem + `POST /auth/login/` 200 |
| `learner_test_2_a` | LEARNER | orga_test_2 | `demo123` | idem + `POST /auth/login/` 200 |
| `learner_test_2_b` | LEARNER | orga_test_2 | `demo123` | idem |

**Note :** `learner_test_2_a` / `learner_test_2_b` font partie du seed personas mais ne matchent pas `LIKE '%_test_2'` (suffixe `_a` / `_b`). Ils sont inclus ici car définis dans `personas_test_2_constants.py`.

**Attention homonymes partiels :** `tutor_test_2` / `trainer_test_2` (sqlite, orga_test_2) ≠ `tuteur_test_2` / `formateur_test_2` (postgres, OF_test_2).

---

## Procédure de régénération des mots de passe

Les seeds sont **idempotents** : chaque relance remet le mot de passe à `demo123` pour les comptes du périmètre seed uniquement.

### OF_test_2 (postgres `hugo_poc`)

```bash
cd hugo_back
DJANGO_SETTINGS_MODULE=config.settings.dev python manage.py bootstrap_demo_test_2
# optionnel : régénérer le JSON fixtures
DJANGO_SETTINGS_MODULE=config.settings.dev python manage.py bootstrap_demo_test_2 --write-fixtures
```

### orga_test_2 (sqlite baseline B)

```bash
./scripts/bootstrap_personas_test_2.sh
# ou
cd hugo_back
DJANGO_SETTINGS_MODULE=config.settings.sqlite_test python manage.py bootstrap_personas_test_2 --write-fixtures
```

Aucun script de reset dédié n’a été nécessaire lors de l’inspection du 2026-07-01 : les mots de passe en base correspondaient déjà à `demo123`.

### Vérification rapide

```bash
# Auth HTTP (backend sqlite sur :8000 si ./run_local_hugo.sh actif)
curl -s -X POST http://127.0.0.1:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"tutor_test_2","password":"demo123"}'

# Vérification Django (postgres)
cd hugo_back
DJANGO_SETTINGS_MODULE=config.settings.dev python manage.py shell -c "
from django.contrib.auth import authenticate
print(authenticate(username='apprenant_test_2', password='demo123'))
"
```

---

## À VÉRIFIER

| Point | Statut |
|-------|--------|
| Couverture de tous les comptes `*_test_2` connus en local | **OK** pour les deux seeds documentés (10 comptes au total, sans doublon inter-DB) |
| Fiche comptes démo **globale** (smoke, tenant, Encoors) | **Hors périmètre** — reste partielle (cf. `R6_PREUVES_MANQUANTES_ET_PLAN_DE_RECALAGE.md`) |
| Auth HTTP des comptes OF_test_2 sur postgres | **AVERIFIER** si le backend tourne uniquement en `sqlite_test` (`run_local_hugo.sh`) — preuve Django `authenticate` OK, pas de curl postgres au moment de l’inspection |
| Comptes `*_test_2` sur Encoors / prod | **Non couvert** — ne pas réutiliser ces mots de passe ailleurs |
| Superadmin multi-org et switch navbar vers OF_test_2 | Voir `memo_cto_2026-06-30.md` — comportement UI, pas re-audité ici |

---

## Sources mobilisées

- `docs-workspace/recalage_actualisation_2026_07_01/R0_README_ACTUALISATION_ET_MODE_D_EMPLOI.md`
- `docs-workspace/recalage_actualisation_2026_07_01/R1_ETAT_REEL_ACTUALISE.md` (via `print_runtime_stack`)
- `docs-workspace/recalage_actualisation_2026_07_01/R6_PREUVES_MANQUANTES_ET_PLAN_DE_RECALAGE.md`
- `hugo_back/apps/accounts/seeds/demo_test_2_constants.py`
- `hugo_back/apps/accounts/seeds/personas_test_2_constants.py`
- `hugo_back/apps/accounts/management/commands/bootstrap_demo_test_2.py`
- `hugo_back/apps/accounts/management/commands/bootstrap_personas_test_2.py`
- Requêtes DB locales 2026-07-01
