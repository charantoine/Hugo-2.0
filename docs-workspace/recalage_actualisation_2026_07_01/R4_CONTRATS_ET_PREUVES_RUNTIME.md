# R4 — Contrats et preuves runtime

**Date :** 1er juillet 2026  
**Rôle :** document de vérité sur contrats observés et preuves d'exécution.  
**Complète :** `A3_CARTOGRAPHIE_OBJETS_CONTRATS_ET_VARIABLES.md` (archive) — ne le remplace pas sur le volet variables prompting.

---

## 1. Méthode de qualification des preuves

| Niveau | Critère | Tag doc |
|--------|---------|---------|
| P0 | Code + test pytest nommé PASS | **REL OBSERV** |
| P1 | Code + test Playwright / E2E PASS | **REL OBSERV** |
| P2 | Code seul, sans test dédié récent | **REL OBSERV PARTIEL** |
| P3 | Doc cluster / rapport sans rejeu 01/07 | **REL OBSERV PARTIEL** (dater) |
| P4 | Inspection HTTP sans auth | **À VÉRIFIER** |
| P5 | Spec / glossaire | **CIBLE** — hors tableau |

---

## 2. Inventaire routes observées (local)

### 2.1 Racine API (`config/urls.py`)

| Préfixe | App | Preuve |
|---------|-----|--------|
| `/auth/` | accounts | P0 — tests auth |
| `/users/`, `/admin/organisations/`, `/admin/users/` | accounts | P0 — tenant campaign |
| `/groups/` | referentials | P0 |
| `/hugo/` | hugo | P0 — clusters 3,15,16 |
| `/documents/` | library | P2 |
| `/referentials/` | referentials | P1 — E2E L7 scaffold |
| `/exports/` | exports | P0 — D2-M06 |
| `/dashboard/` | hugo | P0 — tutor/trainer tests |
| `/evidence/` | hugo | P2 |
| `/quality/` | quality | P2 |
| `/internal/` | hugo | P0 — probes 404 sans auth |
| `/traces/`, `/learners/` | hugo | P0 — cluster 3 |

### 2.2 Routes Hugo session (détail)

Source : `apps/hugo/urls.py` (lecture 01/07/2026).

| Route | Méthodes | Tests / preuve | Qualité |
|-------|----------|----------------|---------|
| `sessions/` | GET, POST | test sessions | P0 |
| `sessions/{id}/` | GET, PATCH | — | P2 |
| `sessions/{id}/ui-state/` | GET | cluster 3, 16 | P0 |
| `sessions/{id}/set-posture/` | POST | B16-P2/P3 | P0 |
| `sessions/{id}/messages/` | GET, POST | — | P2 |
| `sessions/{id}/messages/stream/` | POST | front SSE | P1 partiel |
| `sessions/{id}/request-synthesis/` | POST | E2E L9 SKIP | P2 |
| `sessions/{id}/evaluation-readiness/` | GET | cluster 11 | P0 |
| `sessions/{id}/request-evaluation/` | POST | cluster 11 | P0 |
| `sessions/{id}/finalize-evaluation/` | POST | — | P2 |
| `sessions/{id}/generate-trace/` | POST | pivot tests | P0 |
| `sessions/{id}/memory-summary/` | GET | B16-M1/M2, smoke | P0 |
| `sessions/{id}/share/` | POST | — | P2 |
| `learner-conversation-profiles/` | CRUD | global profile tests | P0 |
| `conduct-profiles/` | CRUD | — | P2 |
| `trainer/knowledge-items/` | CRUD + validate | cluster 15 | P0 |
| `trainer/.../elicitation-*` | GET, POST | cluster 15 | P0 |

---

## 3. Contrat UIState (GET `/hugo/sessions/{id}/ui-state/`)

**Producteur :** `build_contract_ui_state` → `ContractUIState.to_dict()`  
**Consommateurs front (produit) :** `ProdLearnerWorkspace.vue`, `PostureSelector`, CTA boutons — **uniquement** avec `loadUiState: true`  
**Consommateurs API (technique) :** propriétaire de session (`HugoSession.learner = request.user`) — inclut sessions persona tuteur/formateur si appel direct  
**Preuve :** B16-P1, INV-01 (pas de P0) ; Playwright cluster16 v2 (01/07)

> **Décision B (2026-07-01, doctrinale provisoire)** — voir `addendum_exploration_baseline_B_2026_07_01.md` §3.  
> - **API :** contract **owner** (pas d'interdiction backend persona documentée).  
> - **Produit :** contract d'**engagement apprenant** — workspaces persona (`loadUiState: false`) **ne doivent pas** consommer cet endpoint pour piloter l'UI.  
> - **Garde-fous persona :** CTA synthèse/évaluation bloqués server-side (404) ; `expectNoLearnerWorkspaceBlocks` côté E2E.

### 3.1 Champs observés (structure)

```json
{
  "scene_label": "Raconter | Explorer | Synthétiser",
  "scene_progress": 0.0,
  "active_quest_label": "string",
  "quest_progress": 0.0,
  "maturity_color": "red | orange | green",
  "synthesis_button_state": "string",
  "evaluation_button_state": "string",
  "evaluation_trigger_state": "string",
  "evaluation_trigger_message": "string | null",
  "persistent_objects": [
    { "id": "branch-...", "kind": "branch", "label": "...", "status": "..." }
  ],
  "gamification_profile": "A | B | C",
  "conversation_mode": {
    "code": "diagnostic | reflective_afest | knowledge_review",
    "label": "string",
    "can_switch": true,
    "switch_warning": "string | null",
    "allowed_posture_transitions": [
      { "code": "...", "label": "...", "allowed": true, "warning": "..." }
    ],
    "switch_locked_reason": "string | null"
  },
  "learner_display_profile": "youth | adult | professional",
  "cta_synthesis": { "eligible": false, "blocked_reason": "...", "...": "..." },
  "cta_evaluation": { "eligible": false, "advisory": false, "...": "..." },
  "dispersion_risk": false,
  "priority_branch_label": "string | null"
}
```

**Note :** clés exactes CTA — voir `cta_ui_state.py` et `test_b16_c1_cta_contracts_main_fields`.

### 3.2 Query params observés

| Param | Effet | Preuve |
|-------|-------|--------|
| `gamification_profile` | Passe au builder | front `ProdLearnerWorkspace` |
| `learner_display_profile` | Override affichage | B16-L1 |

### 3.3 Champs interdits (confirmés absents)

`turn_state`, `episode_clarity`, `cognitive_load`, `interaction_risk`, champs `P0_CORE_FIELDS`, `P0_LLM_FIELDS` — **REL OBSERV** cluster 3.

---

## 4. Contrat memory-summary

**Endpoint :** `GET /hugo/sessions/{id}/memory-summary/`  
**Référence :** `contrat_api_memory_summary_v1.md` (18/06) — **confirmé** 01/07.

### 4.1 Bloc `session_memory`

| Champ | Type | Preuve |
|-------|------|--------|
| `session_id` | UUID | B16-M1 |
| `updated_at` | ISO8601 | B16-M1 |
| `theme` | string | A1 cluster 15 |
| `learning_objective` | string | — |
| `facts_confirmed` | string[] | smoke test |
| `open_points` | string[] | — |
| `pending_actions` | string[] | — |
| `memory_scope` | `"intra_conversation"` | P0 |

**Garantie :** pas de verbatim message — B16-M2.

### 4.2 Bloc `theme_memories`

Tableau (max 10) — champs `theme_key`, `stabilised`, `open_loops`, `difficulties`, `status`, `last_session`, `updated_at`.

**Front apprenant :** **non consommé** — **REL OBSERV** C15.

### 4.3 Exemple minimal (forme, pas données réelles)

```json
{
  "session_memory": {
    "session_id": "uuid",
    "memory_scope": "intra_conversation",
    "facts_confirmed": ["point_stabilise"],
    "open_points": [],
    "pending_actions": []
  },
  "theme_memories": []
}
```

---

## 5. Endpoints synthèse / évaluation / traces

| Endpoint | Request body (observé) | Response (observé) | Preuve |
|----------|------------------------|-------------------|--------|
| `POST .../request-synthesis/` | `{}` ou options session | synthèse texte + metadata | P2 code |
| `GET .../evaluation-readiness/` | — | `{ "ready": bool, ... }` | P0 cluster 11 |
| `POST .../request-evaluation/` | payload policy | évaluation structurée | P0 |
| `POST .../finalize-evaluation/` | validation humaine | statut final | P2 |
| `POST .../generate-trace/` | — | inclut `evaluation_trace_pivot_v1` | P0 |

**E2E :** lot 9 SKIP — pas de capture JSON bout-en-bout récente — **À VÉRIFIER** manuel.

---

## 6. Endpoint partage

`POST /hugo/sessions/{id}/share/` — **REL OBSERV PARTIEL** (code présent ; pas de test E2E récent cité).

---

## 7. Contrat tour (POST message / SSE)

Champs additionnels dans réponse (engagement UIState) — **schéma distinct** de GET ui-state :

- `session_memory` (dict résumé tour)
- `supporting_documents` (RAG top 3)
- `scene_progress.steps`, `quest_cards`, `symbolic_rewards`

**Preuve :** `views_sessions` serialization ; **REL OBSERV PARTIEL**.

---

## 8. POST set-posture

```json
// Request
{ "posture": "reflective_afest" }

// Success → UIState contract rafraîchi
// Error → transition_not_allowed / Invalid posture
```

**Preuve :** B16-P2, B16-P3 — P0.

---

## 9. Headers multi-tenant

| Header | Usage | Preuve |
|--------|-------|--------|
| `Authorization: Bearer <JWT>` | Toutes routes | P0 |
| `X-Organisation-Id: <uuid>` | Superadmin switch org | P0 — campagne 30/06 |

---

## 10. Différentiel local vs distant (Encoors)

Source doc 10 (12/06/2026) + oracle cluster 8/11 (18/06, **sans auth**).

| Élément | Local 01/07 | Encoors dernier état connu | Tag |
|---------|-------------|----------------------------|-----|
| `conduct-profiles/` | Présent | Absent urlconf 12/06 | **À VÉRIFIER** |
| `evaluation-readiness/` | Présent | Absent 12/06 | **À VÉRIFIER** |
| `finalize-evaluation/` | Présent | Probablement absent 12/06 | **À VÉRIFIER** |
| `learner-conversation-profiles/` | Présent | Non testé | **À VÉRIFIER** |
| Routes internal D9bis | 401 sans JWT | 404 probe 18/06 | **À VÉRIFIER** auth |
| CORS localhost:5173 | OK en dev | Refusé 12/06 | **REL OBSERV** (date 12/06) |
| DEBUG | True en dev.py | True 12/06 | **À VÉRIFIER** |

**Règle :** ne pas présumer que le local déployé = Encoors sans oracle authentifié récent.

---

## 11. Qualité de preuve par bloc fonctionnel

| Bloc | Qualité | Date preuve dominante | Lacune |
|------|---------|----------------------|--------|
| Auth JWT | P0 | 30/06 | — |
| UIState contract | P0 | 18/06 | — |
| memory-summary | P0 | 18/06 | Encoors |
| set-posture | P0 | 18/06 | — |
| CTA champs | P0 | 18/06 | E2E boutons |
| P0 non exposé | P0 | 18/06 | — |
| RAG lexical | P0 | garde-fou | vectoriel |
| Synthèse LLM | P2 | code | E2E + Encoors |
| Évaluation LLM | P0 partiel | cluster 11 | Encoors |
| Trainer API | P0 | 18/06 | usage_count |
| Multi-tenant UI | P0 | 30/06 | RLS prod |
| SSE stream | P1 partiel | E2E | Encoors timeout |

---

## 12. Fichiers historiques impactés

| Fichier | Relation à R4 |
|---------|---------------|
| A3 | Archive objets ; R4 = contrats runtime observés |
| `contrat_api_memory_summary_v1.md` | **Confirmé** |
| `cluster4_surface_contracts.md` | **Complété** par cluster 16 |
| doc 10 Encoors | **À VÉRIFIER** — non actualisé depuis 12/06 |

---

*Suite : **R5** (écarts vs baseline 22/06) ou **R6** (preuves à acquérir).*
