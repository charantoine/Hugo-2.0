# État moteur réel — Hugo

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Périmètre :** `hugo_back/` uniquement — backend Django, API, services P0, persistence.  
**S'appuie sur :** `00_HIERARCHIE_DOCUMENTAIRE.md`, `01_CARTOGRAPHIE_WORKSPACE_REEL.md`  
**Ne couvre pas :** UX front (→ doc 03), runtime `hugoback.encoors.com` (→ **À VÉRIFIER**), Hugo & Cie, backlog 1.9.

---

## 1. Périmètre et limites

**Couvert :** code Python exécutable dans `hugo_back/` — configuration, routes, orchestration conversationnelle, sous-systèmes métier, modèles, tâches Celery, tests pytest.

**Exclu volontairement :**

- Parcours et affichage utilisateur (`hugo-hugolucia/frontend_1.8/`) → doc 03
- Équivalence avec l'API distante de production → **À VÉRIFIER** (non inspectée ici)
- Assistants POST-POC (Julia, Felix bot, Hector, Jérémy) → extension design, hors moteur actuel
- Divergences doc ↔ code → doc 05

---

## 2. Stack et configuration runtime

**Stack** (`requirements.txt`, `Dockerfile`) : Python 3.11, Django ≥5.2, DRF, SimpleJWT, PostgreSQL (psycopg), pgvector, Celery/Redis, django-storages/S3 (MinIO), pypdf, pytest. Image Docker : `runserver` sur port 8000, settings `config.settings.dev` par défaut.

**Settings et flags clés** (`config/settings/base.py`) :

| Variable | Défaut | Effet |
|----------|--------|-------|
| `DEBUG` | `False` | Mode debug global |
| `LLM_BASE_URL` | `http://localhost:11434` | Endpoint Ollama |
| `LLM_MODEL` | `mistral` | Modèle Ollama |
| `LLM_PROVIDER_DEFAULT` | `ollama` | Provider par défaut (`ollama` ou `ovh_ai`) |
| `ENABLE_EXTERNAL_LLM` | `true` | Autorise appels LLM externes |
| `HUGO_DEBUG_TRACING` | `true` si DEBUG | Traçage prompt / LLM |
| `HUGO_PHASE_CLASSIFIER_ENABLED` | `true` | Classifieur de phase LLM |
| `HUGO_P0_CLASSIFIER_ENABLED` | **`false`** | Surclassement P0 par LLM |
| `HUGO_P0_V17_ENABLED` | **`false`** | Pipeline P0 v17 (TurnState/decision/prompt v17) |
| `HUGO_P0_CLASSIFIER_MAX_TOKENS` | `180` | Limite tokens classifieur P0 |
| `HUGO_P0_CLASSIFIER_MIN_CONFIDENCE` | `0.60` | Seuil confiance classifieur P0 |
| `OVH_AI_BASE_URL` / `OVH_AI_MODEL` | endpoints OVH | Provider OVH AI |
| `OVH_AI_TOKEN` | JWT en dur dans base.py | Token OVH — **risque config** |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Broker Celery |

**Providers LLM** (`apps/hugo/llm_client.py`) : `complete_with_provider` / `stream_with_provider` routent vers Ollama (`/api/generate`) ou OVH AI selon provider session/groupe ou défaut settings.

**Note config :** `config/settings/production.py` a `DEBUG = True` (L5) — **AMBIGU** pour un déploiement prod réel.

---

## 3. Surface API

**Préfixes racine** (`config/urls.py`) :

| Préfixe | App | Rôle apparent |
|---------|-----|---------------|
| `/auth/` | accounts | Login JWT, refresh, me |
| `/users/`, `/admin/organisations/`, `/admin/users/` | accounts | Admin utilisateurs/orgs |
| `/groups/` | referentials | Groupes, membres, bibliothèque groupe |
| `/hugo/` | hugo | Sessions, messages, prompts, analytics |
| `/traces/`, `/learners/`, `/dashboard/`, `/evidence/` | hugo | Traces, vues apprenant/tuteur |
| `/documents/` | library | Upload / indexation documents |
| `/referentials/` | referentials | Import référentiel v2 |
| `/exports/` | exports | Export CSV/JSON synchrone |
| `/quality/` | quality | Bundle evidence Qualiopi |
| `/internal/` | hugo | Debug, RAG search, turn-review, pilotage |

**Endpoints Hugo critiques** (`apps/hugo/urls.py`) :

| Endpoint | Vue | Statut |
|----------|-----|--------|
| `POST /hugo/sessions/` | `SessionListCreate` | IMPLÉMENTÉ |
| `GET/PATCH /hugo/sessions/{id}/` | `SessionDetail` | IMPLÉMENTÉ |
| `POST /hugo/sessions/{id}/messages/` | `MessageListCreate` | IMPLÉMENTÉ |
| `POST /hugo/sessions/{id}/messages/stream/` | `MessageStreamCreate` | IMPLÉMENTÉ (SSE) |
| `GET /hugo/sessions/{id}/ui-state/` | `SessionUiStateView` | IMPLÉMENTÉ |
| `POST /hugo/sessions/{id}/request-synthesis/` | `SessionRequestSynthesisView` | IMPLÉMENTÉ |
| `GET /hugo/sessions/{id}/evaluation-readiness/` | `SessionEvaluationReadinessView` | IMPLÉMENTÉ |
| `POST /hugo/sessions/{id}/request-evaluation/` | `SessionRequestEvaluationView` | IMPLÉMENTÉ |
| `POST /hugo/sessions/{id}/finalize-evaluation/` | `SessionFinalizeEvaluationView` | IMPLÉMENTÉ |
| `POST /hugo/sessions/{id}/generate-trace/` | `GenerateTraceView` | IMPLÉMENTÉ |
| `GET /hugo/sessions/{id}/memory-summary/` | `SessionMemorySummaryView` | IMPLÉMENTÉ |
| `GET/POST /hugo/conduct-profiles/` | `TutorConductProfileListCreate` | IMPLÉMENTÉ |
| `GET /internal/hugo/sessions/{id}/turn-review/` | `TurnReviewView` | IMPLÉMENTÉ |
| `POST /internal/rag/search/` | `RagSearchView` | IMPLÉMENTÉ |

**Auth / multi-tenant / RLS :**

- JWT via DRF SimpleJWT (`apps/accounts/`)
- `TenantRLSMiddleware` (`app_core/middleware.py`) : `SET LOCAL app.organisation_id` sur PostgreSQL
- Tests : `tests/test_auth.py`, `tests/test_cross_tenant.py` — **IMPLÉMENTÉ** en environnement test ; efficacité RLS sous Postgres réel **À VÉRIFIER**

---

## 4. Pipeline conversationnel (vue d'ensemble)

**Point d'entrée HTTP :** `views_sessions.py` → `build_hugo_turn()` (`apps/hugo/services/hugo_orchestrator.py`).

**Flux ordonné (stack legacy active par défaut) :**

```
1. build_hugo_context(session)
2. resolve_posture + resolve_conduct_profile (TutorConductProfile ou fallback statique)
3. analyze_turn_state()           → TurnState heuristique
4. classify_p0_turn_state()       → surclassement LLM si HUGO_P0_CLASSIFIER_ENABLED
5. [si HUGO_P0_V17_ENABLED] reconcile_turn_state_v17 + decide_conversation_v17
   [sinon] decide_conversation()
6. build_teaching_plan()
7. decide_next_phase()
8. select_rag_chunks()
9. build_session_memory()
10. build_conversation_progress() + build_conversation_progress_contract()
11. build_ui_state()
12. render_with_tutor_prompt() ou _build_afest_prompts_legacy() ou render_tutor_prompt_v17()
→ LLM (views_sessions) → guardrails → persistance message
→ _post_conversation_hooks() : consolidate_session + record_session_signal
```

**Stack P0 active par défaut :** legacy (`decision_engine.py`, `prompt_renderer.py`, guardrails `_apply_output_guardrails` dans `views_sessions.py`). Tests forcent legacy : `apps/hugo/tests/conftest.py` L6 `HUGO_P0_V17_ENABLED=false`.

**Stack v17 (derrière flag) :** `turn_state_v17`, `decision_engine_v17`, `teaching_plan_builder_v17`, `prompt_renderer_v17`, `output_guardrails_v17` — code présent, tests opt-in `test_p0_v17_flow.py` avec `@override_settings(HUGO_P0_V17_ENABLED=True)`.

**Modules impliqués :**

| Module | Fichier | Rôle |
|--------|---------|------|
| TurnState | `domain/schemas.py`, `turn_state_analyzer.py` | Signaux heuristiques P0 |
| Classifieur P0 | `p0_classifier.py` | Surclassement LLM partiel (off par défaut) |
| Décision | `decision_engine.py` / `decision_engine_v17.py` | `ConversationDecision` |
| Phase | `phase_decider.py` | Progression phase (+ classifieur phase si enabled) |
| Teaching plan | `teaching_plan_builder.py` | Plan pédagogique par tour |
| Prompt | `prompt_renderer.py` / `prompt_renderer_v17.py` | Rendu prompt final |
| Guardrails | `views_sessions._apply_reply_guardrails`, `output_guardrails_v17.py` | Post-traitement réponse LLM |
| UI contract | `ui_state_builder.py` | Objet `UiState` pour le front |

---

## 5. Sous-systèmes moteur

| Zone | Fichiers clés | Statut | Preuve / test | Limite connue |
|------|---------------|--------|---------------|---------------|
| **RAG runtime** | `rag_support.py` | IMPLÉMENTÉ | `test_rag_support_tracing.py` | Sélection **lexicale** (tokens/métadonnées) ; pas de recherche vectorielle dans `select_rag_chunks` |
| **Bibliothèque** | `apps/library/`, `library/tasks.py` | IMPLÉMENTÉ | `test_library_ingestion.py` | `index_document` : chunks texte 500 car. ; **pas de calcul d'embeddings** malgré champ `embedding` (pgvector) |
| **Mémoire session** | `session_memory.py` | IMPLÉMENTÉ | utilisé dans orchestrateur L338 | Résumé intra-session (messages, traces) ; pas `LearnerThemeMemory` |
| **Mémoire inter-session** | `memory_consolidator.py`, `LearnerThemeMemory` | PARTIEL | `test_memory_consolidation.py` | **Écriture** via `_post_conversation_hooks` après message (L1274, L1347, L1359) ; **pas d'injection** dans `build_hugo_turn` |
| **Évaluation** | `evaluation_service.py`, `evaluation_workflow_engine.py` | IMPLÉMENTÉ | endpoints session + trainer views | Workflow LLM ; validation tuteur via `views_trainer.py` |
| **Synthèse** | `synthesis_service.py` | IMPLÉMENTÉ | `test_conversation_progress.py` (generate_synthesis) | LLM + fallback heuristique ; pas stub |
| **Exports** | `apps/exports/views.py` | IMPLÉMENTÉ | `test_exports_run.py` | CSV/JSON synchrone, traces Felix-ready |
| **Quality / Qualiopi** | `apps/quality/views.py` | IMPLÉMENTÉ | `EvidenceBundleView` | ZIP evidence bundle ; périmètre POC |
| **TutorConductProfiles** | `conduct_profile_resolver.py`, `views_conduct_profiles.py` | IMPLÉMENTÉ | routes CRUD + resolver dans orchestrateur L228 | Fallback `domain/tutor_profiles.py` si pas de profil DB |
| **Analytics** | `analytics/cohort_dashboard.py`, `quality_tracker.py` | IMPLÉMENTÉ | routes `/hugo/analytics/` | Signaux `ConversationQualitySignal` |
| **Traces / evidence** | `models.Trace`, `views_traces`, `views_evidence` | IMPLÉMENTÉ | `GenerateTraceView` | Trace `generate-trace` : payload minimal (L1380–1387) |
| **Trainer knowledge** | `views_trainer.py` | IMPLÉMENTÉ | `test_trainer_knowledge.py` | Ingest document formateur, élicitation |
| **Internal / debug** | `urls_internal.py`, `views_internal.py` | IMPLÉMENTÉ | turn-review, rag search, pilotage | Réservé calibration |

---

## 6. Modèles et persistence

**Modèles Hugo principaux** (`apps/hugo/models.py`) :

| Modèle | Rôle |
|--------|------|
| `HugoSession` | Session conversationnelle (phase, posture, progress, analytics) |
| `HugoMessage` | Messages learner/assistant + payload LLM |
| `TutorPrompt` | Personnalisation textuelle contextuelle |
| `TutorConductProfile` | Paramètres comportementaux par posture/org |
| `Trace` / `TraceCriterionAssessment` | Traces compétences |
| `Evidence` | Preuves attachées session |
| `LearnerState` | Cache compétences apprenant (souvent vide) |
| `LearnerThemeMemory` | Mémoire thématique inter-session |
| `TrainerKnowledgeItem` | Base connaissances formateur |
| `ConversationQualitySignal` | Signaux qualité / analytics |
| `EvaluationPolicy` / `LearnerEvaluationRecord` | Workflow évaluation |
| `EvaluationPromptProfile` | Profils prompt évaluation |
| `OvhLlm` / `StarterPrompt` | Config LLM OVH, prompts démarrage |

**Celery tasks :**

| Task | Fichier | Statut | Détail |
|------|---------|--------|--------|
| `recalc_learner_state` | `apps/hugo/tasks.py` | PARTIEL | Placeholder : `skills_matrix: {}` vide (L16–19) |
| `index_document` | `apps/library/tasks.py` | IMPLÉMENTÉ | Découpe texte en chunks ; pas d'embedding |

---

## 7. Couverture tests

**Total :** 30 fichiers `test_*.py` hors `venv/`.

| Zone | Fichiers | Couverture |
|------|----------|------------|
| P0 engine / calibration | `test_hugo_p0_engine.py`, `test_hugo_calibration_scenarios.py`, `test_p0_non_regression.py` | **Forte** |
| Classifieur P0 | `test_p0_classifier.py`, `test_classifier_runtime_validation.py` | **Forte** (flags on en override) |
| P0 v17 | `test_p0_v17_flow.py` | **Partielle** (opt-in flag) |
| Phase / progression | `test_phase_decider.py`, `test_phase_progression.py`, `test_conversation_progress.py` | **Forte** |
| RAG / tracing | `test_rag_support_tracing.py` | **Moyenne** |
| Posture / guardrails | `test_posture_modes.py`, `test_views_sessions_guardrails.py` | **Moyenne** |
| Mémoire | `test_memory_consolidation.py` | **Moyenne** (consolidation seule) |
| Trainer / tutor | `test_trainer_knowledge.py`, `test_tutorprompt.py`, `test_tutor_access_control.py` | **Moyenne** |
| Auth / RLS | `tests/test_auth.py`, `tests/test_cross_tenant.py` | **Moyenne** (SQLite test) |
| Referentials / library / exports | 4 fichiers | **Ciblée** |
| Évaluation end-to-end API | — | **Faible** (pas de test dédié request-evaluation vue) |
| Playwright / E2E | — | **Absente** |

**Tests conditionnés par flags :** `conftest.py` force `HUGO_P0_V17_ENABLED=false` ; v17 et classifier activés via `@override_settings` dans les modules concernés.

---

## 8. Écarts internes au moteur (sans backlog)

| Point | Statut | Détail |
|-------|--------|--------|
| Double stack P0 legacy + v17 | **AMBIGU** | Coexistence complète ; pas de stratégie migration documentée dans le code |
| P0 classifieur LLM off par défaut | **PARTIEL** | Code prêt, désactivé (`HUGO_P0_CLASSIFIER_ENABLED=false`) |
| RAG vectoriel | **CIBLE** | pgvector en modèle ; sélection runtime lexicale uniquement |
| `LearnerThemeMemory` non injectée au tour | **PARTIEL** | Consolidation post-message OK ; lecture absente de l'orchestrateur |
| `recalc_learner_state` placeholder | **PARTIEL** | Task présente, contenu vide |
| Token OVH en dur | **AMBIGU** | `base.py` L187 — risque sécurité / placeholder |
| `production.py` DEBUG=True | **AMBIGU** | Config prod incohérente |
| Trace `generate-trace` minimale | **PARTIEL** | Payload structuré peu rempli (L1380–1387) |

**Reporté au doc 05 :** écarts entre `MEMO_CTO_Hugo1.9_v2.md`, `p0_description_technique_actuelle.md` et ce constat code local.

---

## 9. Renvoi

- **Produit montrable (contrats API consommés) :** `03_ETAT_PRODUIT_REEL.md`
- **Écarts doc / code / prod :** `05_ECARTS_DOC_CODE_PRODUIT.md`
- **Préparation cible 1.9 :** `06_PREPARATION_CIBLE_1_9.md`
- **Runtime et flags démo :** `07_RUNTIME_DEMO_REFERENCE.md`, `08_FLAGS_ET_ENVIRONNEMENT_DEMO.md`, `10_FICHE_RUNTIME_PROD_ENCOORS.md` (Encoors)
- **Parcours démo :** `09_PARCOURS_DEMO_ET_SCENARIOS.md`
- **Règles de lecture :** `00_HIERARCHIE_DOCUMENTAIRE.md`

---

*Document 02 — état moteur `hugo_back` juin 2026. Sources : code et tests locaux ; prod distante non interrogée.*
