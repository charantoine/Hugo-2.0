# ADR — Clarifier memory-summary intra / inter (C9-CODE-02)

> Statut : **PROPOSÉ** — non implémenté cluster 10  
> Date : 2026-06-18

---

## Contexte

`GET /hugo/sessions/{id}/memory-summary/` retourne aujourd’hui :

- `session_memory` — contrat **intra-conversation** ;
- `theme_memories` — jusqu’à 10 `LearnerThemeMemory` (**inter-session**).

Le cluster 9 a identifié un **écart documentaire** : un seul endpoint mélange deux périmètres mémoire.

---

## Option A — Paramètre `scope` (recommandée court terme)

**Comportement**

- `GET .../memory-summary/?scope=intra` → `{ "session_memory": {...} }` seulement.
- `GET .../memory-summary/?scope=all` (défaut rétrocompatible) → comportement actuel.

**JSON exemple (`scope=intra`)**

```json
{
  "session_memory": {
    "session_id": "...",
    "memory_scope": "intra_conversation",
    "facts_confirmed": [],
    "open_points": []
  }
}
```

**Impact code minimal**

- `SessionMemorySummaryView.get` : lire `request.query_params.get("scope", "all")`.
- Tests : 2 cas dans `test_memory_summary_smoke.py`.
- Doc : `contrat_api_memory_summary_v1.md` (déjà livré).

**Avantages** : rétrocompatible, patch ~15 lignes, pas de nouvelle route.

---

## Option B — Deux endpoints

| Endpoint | Contenu |
|----------|---------|
| `GET .../memory-summary/` | Intra uniquement |
| `GET .../theme-memories/` | Liste `LearnerThemeMemory` learner |

**Impact** : nouvelle vue + url + tests + **breaking change** si clients consomment déjà `theme_memories` sur memory-summary (front : aucun consommateur repéré).

**Avantages** : séparation nette doctrinale.  
**Inconvénients** : migration clients, plus de surface API.

---

## Décision recommandée

**Option A** pour le lot suivant si le CTO valide — P2, non bloquant runtime/OPS.

**Ne pas implémenter** sans arbitrage explicite (cluster 10 = doc + OPS seulement).

---

## Références

- `views_sessions.SessionMemorySummaryView`
- `contrat_api_memory_summary_v1.md`
