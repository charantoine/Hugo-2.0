# Contrat API `memory-summary` v1 (C9-DOC-01)

> Domaine 20 — mémoire gouvernée intra-conversation  
> Statut : contrat produit minimal aligné sur le réel audité (cluster 9–10)  
> Date : 2026-06-18

---

## Endpoint

| Attribut | Valeur |
|----------|--------|
| Méthode | `GET` |
| Path | `/hugo/sessions/{session_id}/memory-summary/` |
| Auth | JWT — propriétaire session (learner) ou accès session équivalent |
| Écriture | **Aucune** — lecture seule |

---

## RÉEL OBSERVÉ (champs assurés aujourd’hui)

### Bloc `session_memory` — intra-conversation

Produit par `build_session_memory_contract` ; `memory_scope` = `"intra_conversation"`.

| Champ | Type | Description |
|-------|------|-------------|
| `session_id` | UUID string | Session courante |
| `updated_at` | ISO8601 | Horodatage session |
| `theme` | string | Libellé fil (progression / branche) |
| `learning_objective` | string | Objectif actif si connu |
| `facts_confirmed` | string[] | Points stabilisés (turn_state / progression) |
| `open_points` | string[] | Points ouverts |
| `pending_actions` | string[] | Actions recommandées |
| `memory_scope` | string | Toujours `"intra_conversation"` |

**Garanties testées** (`test_session_memory_contract.py`, `test_memory_summary_smoke.py`) :

- Pas de contenu verbatim message apprenant dans la réponse JSON.
- Agrégation limitée aux messages **de la session courante**.

### Bloc `theme_memories` — inter-session (lecture seule)

Jusqu’à 10 enregistrements `LearnerThemeMemory` pour le learner de l’organisation.

| Champ | Type | Description |
|-------|------|-------------|
| `theme_key` | string | Thème consolidé |
| `stabilised` | string[] | Points stabilisés |
| `open_loops` | string[] | Boucles ouvertes |
| `difficulties` | string[] | Difficultés persistantes |
| `status` | string | ex. `derived_provisional` |
| `last_session` | UUID string | Dernière session source |
| `updated_at` | ISO8601 | Mise à jour |

**Important** : ce bloc relève de la **préparation inter-session** ; il n’est **pas injecté** dans les prompts LLM au tour courant (réel cluster 9).

---

## CIBLE 2.0 (lot courant)

- Exposer un **résumé gouverné** intra-conversation, jamais un historique brut.
- Séparer clairement intra-conv (`session_memory`) et inter-session (`theme_memories`) dans la doc produit.
- Verbatim non partagé : **absent** de `session_memory` ; doctrine B1-01 pour les encadrants via autres endpoints (timeline).

---

## Champs interdits (non exposables produit)

- Contenu intégral des messages (`HugoMessage.content`).
- `llm_request_payload`, `turn_state` P0 bruts, embeddings, diagnostics classifieur.
- Verbatim complet même pour le learner via cet endpoint (le contrat est structuré, pas transcript).

---

## ÉCART CONFIRMÉ

| Point | Statut |
|-------|--------|
| Endpoint unique mélange intra + inter | **ÉCART** — voir ADR `adr_c9_code02_memory_summary_scope.md` |
| Injection `SessionMemoryContract` dans prompt LLM | **ABSENT** — attaché UIState/tracing uniquement |
| Front consommateur direct de memory-summary | **ABSENT** — UI via UIState tour |

---

## A_VÉRIFIER

- Comportement Encoors sur le même endpoint (auth + shape).
- Évolution future : paramètre `scope` ou endpoint séparé (décision CTO en attente).

---

## Références

- Code : `SessionMemorySummaryView`, `session_memory.py`
- Tests : `test_session_memory_contract.py`, `test_memory_summary_smoke.py`
- Écarts : `ecarts — 20_memoire_gouvernee.md`
