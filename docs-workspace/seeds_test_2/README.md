# seeds_test_2 — Kit CTO Hugo

Date de generation : 2026-07-02
Baseline de reference : seeds *_test_2 extraites du code source

## Contenu du dossier
- `seed_superadmin.py` -> script standalone, cree le superadmin
- `seed_accounts_test_2.py` -> comptes, tenants, users issus des seeds _test_2
- `seed_prompts_mk1.py` -> prompts "mk1" + liaison aux comptes
- `seed_all.py` -> script maitre qui appelle les trois dans l'ordre
- `fixtures/` -> fichiers JSON Django equivalents (optionnel)
- `ACCOUNTS_CONFIG.md` -> doc lisible des comptes et leurs parametrages

## Comment rejouer
```bash
cd hugo_back
python manage.py shell < ../docs-workspace/seeds_test_2/seed_all.py
# OU
python manage.py loaddata ../docs-workspace/seeds_test_2/fixtures/*.json
```

## Notes d'audit
- Le prompt `mk1` a ete collecte via code + inspection DB locale (`config.settings.dev`).
- Les comptes `_test_2` proviennent des seeds `demo_test_2` et `personas_test_2`.
