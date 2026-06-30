# Retex cluster 8 — OPS / smoke UI / Encoors / RLS

> Recette audit → impl → tests → doc — vague OPS du plan CTO  
> Date : 2026-06-18

---

## 1. Ce qui a fonctionné (recettes vagues 2–5)

| Étape | Application cluster 8 |
|-------|----------------------|
| Audit court | Reprise fiche Encoors v5 + gap Playwright identifié |
| Plan borné | 3 smokes UI + oracle 2 scénarios + RLS minimal — pas de nouvelles features |
| Backend-first | Bootstrap Django `bootstrap_smoke_playwright` ; RLS vérifié via migrations + pytest |
| Tests massifs ciblés | 4 Playwright + 4 pytest RLS (2 pass, 2 skip documentés) |
| Doc + retex | Rapport OPS + mises à jour plan/matrice/écarts |

---

## 2. Découvertes OPS importantes

### Playwright vs `.env.development`

Le front dev pointe par défaut vers `https://hugoback.encoors.com`. Les smoke tests **doivent** forcer `VITE_API_URL=/api` (config Playwright `webServer.env` ou export manuel). Sans cela, login smoke échoue avec « Identifiants incorrects » (users locaux absents sur Encoors).

### RLS Postgres vs superuser

Les policies sont **actives** sur les tables sensibles, mais un test SQL cross-tenant avec le rôle `postgres` (superuser) **bypass** RLS. La preuve retenue pour cluster 8 :

- présence policies (pytest) ;
- isolation API 404 cross-tenant ;
- prod SQL **A_VÉRIFIER** avec rôle applicatif dédié.

### Encoors inchangé vs local

Probes non auth confirmées (404 v3/v4). Authentification requise pour EVAL1/O1 — credentials hors workspace.

---

## 3. Bilan par objectif cluster 8

| Objectif | Livré | Reste |
|----------|-------|-------|
| Smoke UI multi-rôles | **Oui** — 4/4 | Export click, parcours riches |
| Oracle Encoors auth | **Partiel** — script + config exemple | Credentials + comparaison EVAL1/O1 |
| Audit RLS minimal | **Partiel** — policies + API | SQL prod non-superuser |
| Photo OPS CTO | **Oui** | — |

---

## 4. Ce qui reste pour la Couronne

- Intercalaires v1, dashboards analytics produit, D2-M12 ORGADMIN/SUPERADMIN.
- Parité Encoors post-déploiement vagues 3–4.
- Playwright E2E riches (CTA éval, observabilité ORGADMIN, 5 rôles × parcours complets).
- Gate prod : oracle Encoors authentifié + RLS sur rôle DB réel.

---

## 5. Commandes de reproduction

```bash
# Backend + DB
createdb hugo_poc  # si absent
cd hugo_back && .venv/bin/python manage.py migrate
.venv/bin/python manage.py bootstrap_smoke_playwright
.venv/bin/python manage.py runserver 8000

# Front (autre terminal)
cd hugo-hugolucia/frontend_1.8
VITE_API_URL=/api npm run dev

# Smoke UI
npm run test:smoke

# RLS
cd hugo_back && .venv/bin/pytest apps/hugo/tests/test_rls_postgres_minimal.py -q

# Encoors (credentials requis)
export ENCOORS_USERNAME=... ENCOORS_PASSWORD=...
.venv/bin/python scripts/encoors_oracle.py
```
