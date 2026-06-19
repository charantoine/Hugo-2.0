# Fixtures référentiels (import manuel v2)

Fichiers JSON prêts pour `POST /api/referentials/import-v2/`.

## RNCP38878

BAC PRO « Métiers de l'électricité et de ses environnements connectés » (15 blocs de compétences).  
Source : fiche France Compétences RNCP38878.

## Utilisation

Avec un token JWT (après `POST /api/auth/login/`) :

```bash
curl -X POST http://localhost:8080/api/referentials/import-v2/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d @RNCP38878.json
```

Réponse attendue : `201 Created` avec `{ "id": "<uuid>", "name": "...", "items_count": 15 }`.

Ensuite, lier le référentiel à un groupe via `PUT /api/groups/<group_id>/referential-config/` avec `referential_id` (et optionnellement `scale_id`).
