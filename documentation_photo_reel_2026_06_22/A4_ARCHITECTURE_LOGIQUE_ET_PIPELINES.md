# A4 — Architecture logique et pipelines

**Date :** 22 juin 2026

---

## 1. Architecture logique générale

```
┌─────────────────────────────────────────────────────────────────┐
│                    SURFACES PRODUIT                              │
│  /app (apprenant)  │  /app/tutor  │  /app/trainer  │  tester    │
└────────────┬────────────────────────────────────────────────────┘
             │ HTTP JSON / SSE
┌────────────▼────────────────────────────────────────────────────┐
│              API Django (hugo_back)                                │
│  /auth/  /hugo/  /groups/  /documents/  /exports/  /quality/    │
│  /internal/ (debug, observability, rag search)                    │
└────────────┬────────────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────────────┐
│           ORCHESTRATEUR (hugo_orchestrator.py)                     │
│  P0 → décision → plan → phase → RAG → mémoire → progression     │
│  → UIState → prompt → LLM → guardrails → hooks                  │
└────────────┬────────────────────────────────────────────────────┘
             │
┌────────────▼──────────┬──────────────────┬─────────────────────┐
│ PostgreSQL + RLS      │ Redis/Celery     │ MinIO/S3            │
│ (sessions, traces…)   │ (index docs)     │ (evidence, exports) │
└───────────────────────┴──────────────────┴─────────────────────┘
             │
┌────────────▼────────────────────────────────────────────────────┐
│ LLM (Ollama / OVH AI) — classifieurs auxiliaires + tuteur        │
└─────────────────────────────────────────────────────────────────┘
```

**Doctrine :** backend-first ; front = consommation d'états dérivés.

---

## 2. Backend Django

### Couches

| Couche | Emplacement | Rôle |
|--------|-------------|------|
| HTTP | `views_sessions.py`, `views_*.py` | Auth, validation, streaming |
| Services | `apps/hugo/services/` | Orchestration métier |
| Domaine | `apps/hugo/domain/` | Schémas, règles pures |
| Persistence | `models.py` | ORM |
| Tâches | `tasks.py`, `library/tasks.py` | Async indexation |

### Multi-tenant

- `TenantRLSMiddleware` : `SET LOCAL app.organisation_id`.
- Tests cross-tenant sur SQLite — **A_VERIFIER** Postgres prod.

---

## 3. Front produit

- Vue 3 + Vite (`frontend_1.8`).
- `api/client.js` : JWT, refresh, `fetchWithAuth` pour SSE.
- `engagementUiModel.js` : mapping ui-state → affichage.
- Séparation layouts : `ProdLearnerLayout` vs `TesterLayout`.

**Règle :** aucune heuristique P0 en parcours `/app`.

---

## 4. Séparation surfaces métier / techniques

| Surface | Exemples | Public |
|---------|----------|--------|
| Métier apprenant | `/app`, ui-state, CTA | Learner |
| Métier encadrants | `/app/tutor`, `/app/trainer` | Tuteur, formateur |
| Admin | `/dashboard`, conduct-profiles, users | Testeur, ORGADMIN |
| Technique | turn-review, observability, P0 debug | Calibration, SUPERADMIN |

---

## 5. Pipeline conversationnel détaillé

### Phase entrée

1. **HTTP** : `MessageListCreate` ou `MessageStreamCreate`
2. **Contexte** : `build_hugo_context(session)` — référentiel, traces, docs groupe, profil apprenant

### Phase posture

3. **Posture** : `resolve_posture` — code posture actif
4. **Conduct** : `resolve_conduct_profile` — DB ou fallback statique

### Phase P0

5. **Heuristique** : `analyze_turn_state(message, context)` → `TurnState`
6. **Classifieur** (si `HUGO_P0_CLASSIFIER_ENABLED` ou config session) : `classify_p0_turn_state` → surclassement JSON partiel
7. **v17** (si flag) : `reconcile_turn_state_v17` → `decide_conversation_v17`
8. **Legacy** (défaut) : `decide_conversation(state)` → `ConversationDecision`

### Phase pédagogique

9. **Plan** : `build_teaching_plan(decision, state, context)`
10. **Phase session** : `decide_next_phase` (+ classifieur phase LLM si enabled)

### Phase enrichissement

11. **RAG** : `select_rag_chunks` — lexical, gating posture/profil
12. **Mémoire session** : `build_session_memory` — intra-conversation
13. **Progression** : `build_conversation_progress` + contrat branches/maturité

### Phase produit

14. **UIState** : `build_contract_ui_state` — CTA, scène, mode conversation
15. **Prompt** : `render_with_tutor_prompt` (ou legacy/v17)
16. **LLM** : `complete_with_provider` / stream
17. **Guardrails** : `_apply_reply_guardrails` ou `output_guardrails_v17`
18. **Persistance** : `HugoMessage` assistant

### Phase post-tour

19. **Hooks** : `consolidate_session` (LearnerThemeMemory), `record_session_signal`

---

## 6. Construction du contexte

**Producteur :** `context_builder.py` (via `build_hugo_context`).

**Contenu typique :**
- Référentiel groupe (items, compétences)
- Traces apprenant
- Documents groupe / chunks RAG candidats
- État session (phase, posture, progress)
- Profil conversationnel résolu

**Hiérarchie contexte 2.0 :** ordre état → mémoire → verbatim → référentiel → documentaire — **PARTIEL** contractualisé (voir ecarts-30).

---

## 7. Posture

- Codes : diagnostic, réflexif, bûchage (et variantes résolution).
- Source : session + `set-posture` + profil global slots.
- `conversation_mode` exposé dans UIState avec `allowed_posture_transitions`.

---

## 8. P0 et TurnState

- **TurnState** : ~30+ champs heuristiques (clarté épisode, charge cognitive, points couverts, signaux fermeture/répétition/aide).
- **P0** = couche analyse + décision ; pas exposée front prod.
- **Flags** : `HUGO_P0_V17_ENABLED`, `HUGO_P0_CLASSIFIER_ENABLED`.

---

## 9. Décision conversationnelle

- Entrée : `TurnState` fusionné.
- Sortie : `ConversationDecision` (intent, move, nb questions, flags, reason_codes).
- Moteur : règles if/elif dans `decision_engine.py` — **formules explicites observées dans le code**, pas inférées.

---

## 10. Teaching plan

- `build_teaching_plan` : focus compétence, regulation targets, plafond questions.
- Variables consommables prompt : `focus_guidance_block`, `max_questions_this_turn`, etc.

---

## 11. Mémoire

| Type | Producteur | Consommation tour | UI |
|------|------------|-------------------|-----|
| Intra-session | `build_session_memory` | Orchestrateur (objet) ; **pas prompt** | memory-summary, panneau |
| Inter-session | `memory_consolidator` | **Non** orchestrateur | memory-summary theme_memories |

---

## 12. Progression

- Branches avec `branch_key`, `stage_index`, `percent`.
- Maturité : `SessionMaturityLevel` RED/ORANGE/GREEN.
- Éligibilités : `can_summarize`, `evaluation_eligible`, `closure_eligible`.
- `reason_codes` : `synthesis_eligible`, `evaluation_blocked_maturity`, etc.

---

## 13. UIState

- Double chemin historique : `build_ui_state` (engagement) vs `build_contract_ui_state` (contrat spec 2.0 / cluster 4).
- Endpoint unique consommé front : contrat.
- Paramètre `gamification_profile` (A/B/C) — cosmétique front + hints back.

---

## 14. SSE / fallback

- **Back** : `MessageStreamCreate` — `text/event-stream`.
- **Front** : tente stream, fallback POST sur 404/405/501.
- **Nginx** hugolucia : route stream présente ; **A_VERIFIER** Encoors (CORS, timeout).

---

## 15. Synthèse et évaluation (hors tour principal)

- **Synthèse** : service dédié `synthesis_service.py` — déclenché par CTA.
- **Évaluation** : `evaluation_service.py`, `evaluation_workflow_engine.py` — branche terminale.
- Éligibilité pilotée par progression + reason_codes, pas par front.

---

## 16. Partage

- Flags session : partage résumé, preuves, verbatim au tuteur.
- `ShareView` — gouvernance confidentialité B1-01.

---

## 17. RAG

- Indexation : Celery `index_document` — chunks texte sans embedding.
- Runtime : matching lexical tokens/métadonnées dans `rag_support.py`.
- Injection prompt : `rag_chunks_block`, `documents_block`.

---

## 18. Analytics qualité

- Post-message : `ConversationQualitySignal`.
- Admin : observability internal, conversation-summary SUPERADMIN.
- D9bis : modèles analyse LLM — export technique, pas produit.

---

## 19. Flags structurants (résumé)

Voir `08_FLAGS_ET_ENVIRONNEMENT_DEMO.md` — tableau complet.

Critiques pour le pipeline :
- `HUGO_P0_V17_ENABLED` — bascule stack entière v17
- `HUGO_P0_CLASSIFIER_ENABLED` — écriture LLM partielle TurnState
- `HUGO_PHASE_CLASSIFIER_ENABLED` — phase session
- `ENABLE_EXTERNAL_LLM` — coupe LLM si false

---

## 20. Dualité legacy / v17

| Composant | Legacy (défaut) | v17 (flag) |
|-----------|-----------------|------------|
| TurnState | heuristique seul | reconcile v17 |
| Décision | `decision_engine.py` | `decision_engine_v17.py` |
| Prompt | `prompt_renderer.py` | `prompt_renderer_v17.py` |
| Guardrails | views_sessions | `output_guardrails_v17.py` |
| Tests | conftest force legacy off v17 | opt-in `test_p0_v17_flow.py` |

**Statut :** **RÉEL OBSERVÉ** coexistence — **A_VERIFIER** prod ; pas de migration documentée.

---

*Sources : 02_ETAT_MOTEUR_REEL.md, hugo_orchestrator.py, variables_prompting.md, cluster2 domaine 10.*
