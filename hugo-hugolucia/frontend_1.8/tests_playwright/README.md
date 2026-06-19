# Playwright smoke tests (cluster 8)

Smoke navigateur pour surfaces prod convergées : TUTOR, TRAINER, ORGADMIN exports.

## Prérequis

1. Postgres + migrations : `cd hugo_back && python manage.py migrate`
2. Fixtures : `python manage.py bootstrap_smoke_playwright`
3. Backend : `python manage.py runserver 8000`
4. Front avec API locale : `VITE_API_URL=/api npm run dev`  
   (`.env.development` pointe vers Encoors — ne pas l’utiliser tel quel pour les smokes.)

## Exécution

```bash
npm run test:smoke
```

La config Playwright force `VITE_API_URL=/api` si elle démarre Vite via `webServer`.

## Fichiers

- `smoke-fixtures.json` — généré par bootstrap (gitignored)
- `test_smoke_tutor.spec.ts` — timeline sans verbatim
- `test_smoke_trainer.spec.ts` — knowledge list + validate
- `test_smoke_orgadmin_exports.spec.ts` — CTA exports ORGADMIN vs LEARNER
