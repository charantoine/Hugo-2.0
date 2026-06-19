# Referential Import MVP (Activities and Tasks)

This document describes the import payload supported by `POST /referentials/import-v2/` for the MVP data model:

- Blocks and competencies (existing)
- Criteria (existing durable model)
- Activities and tasks (new)
- Competency-task links (new)

## Conceptual model

- `ReferentialItem` = competency (`C1`, `C2`, ...)
- `ReferentialCriterion` = criterion (`C1.1`, `C1.2`, ...)
- `ReferentialActivity` = activity (`A1`, `A2`, ...)
- `ReferentialTask` = task (`T1-1`, `T2-3`, ...)
- `ReferentialCompetencyTask` = many-to-many link between competency and task

## Accepted payload (top-level keys)

- `name` (string, required)
- `source_ref` (string, optional)
- `items` (array, required)
- `activities` (array, optional)
- `tasks` (array, optional)
- `competency_tasks` (array, optional)

## Item format

Each item supports:

- `code`, `title`, `block_code`, `block_label`
- `evaluation_criteria`, `evaluation_modalities`, `expected_evidence`, `source_ref`
- `criteria` (array; creates `ReferentialCriterion`)
- `tasks` (array of task codes or `{code}` objects; inline competency-task link helper)

## Activity and task format

### Activities (recommended)

Activities can embed tasks directly:

```json
{
  "activities": [
    {
      "code": "A1",
      "label": "Preparation",
      "order_index": 1,
      "tasks": [
        { "code": "T1-1", "label": "Lire le dossier", "order_index": 1 }
      ]
    }
  ]
}
```

### Tasks (alternative)

Tasks can also be provided in a separate top-level list:

```json
{
  "tasks": [
    {
      "code": "T1-1",
      "label": "Lire le dossier",
      "activity_code": "A1",
      "order_index": 1
    }
  ]
}
```

## Competency-task links

Links can be provided via:

- inline `item.tasks`
- and/or top-level `competency_tasks`

```json
{
  "competency_tasks": [
    { "competency_code": "C1", "task_code": "T1-1" }
  ]
}
```

## Validation and uniqueness rules

- activity unique by `(referential, code)`
- task unique by `(activity, code)`
- competency-task link unique by `(referential_item, task)`
- unknown links are ignored during import (MVP behavior)

## Read APIs (MVP)

- `GET /referentials/`
- `GET /referentials/{ref_id}/items/`
- `GET /referentials/{ref_id}/activities/`
- `GET /referentials/{ref_id}/activities/{activity_id}/tasks/`
- `GET /referentials/{ref_id}/items/{item_id}/tasks/`

## Full example

See:

- `backend/docs/referential_import_mvp_example.json`
