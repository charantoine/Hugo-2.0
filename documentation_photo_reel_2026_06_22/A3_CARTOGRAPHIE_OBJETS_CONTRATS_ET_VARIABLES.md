# A3 — Cartographie objets, contrats et variables

**Date :** 22 juin 2026  
**Légende statut :** RÉEL OBSERVÉ | RÉEL OBSERVÉ PARTIEL | CIBLE | ÉCART CONFIRMÉ | A_VERIFIER

---

## 1. HugoSession

| Attribut | Valeur |
|----------|--------|
| Nom doctrinal | Session conversationnelle |
| Nom réel | `HugoSession` (`apps/hugo/models.py`) |
| Rôle | Conteneur tour, phase, posture, progress, analytics, flags partage |
| Couche | Persistence Django |
| Exposition | API session ; champs techniques partiels en testeur |
| Statut | **RÉEL OBSERVÉ** |
| Preuves | `02_ETAT_MOTEUR_REEL.md`, modèles, `views_sessions.py` |
| Ambiguïtés | Lien `learner_conversation_profile` : résolveur sans API PATCH session dédiée |
| Cible 2.0 | Aligné conceptuellement ; contrats fins ouverts |

---

## 2. HugoMessage

| Attribut | Valeur |
|----------|--------|
| Nom réel | `HugoMessage` |
| Rôle | Messages learner/assistant + payload LLM (debug) |
| Couche | Persistence |
| Exposition | `GET/POST .../messages/` ; verbatim partiel selon share flags |
| Statut | **RÉEL OBSERVÉ** |
| Ambiguïtés | Contenu assistant soumis guardrails post-LLM |
| Cible 2.0 | Verbatim interne borné, non mémoire principale |

---

## 3. TurnState

| Attribut | Valeur |
|----------|--------|
| Nom doctrinal | TurnState / noyau P0 |
| Nom réel | `TurnState` (`domain/schemas.py`), `analyze_turn_state()` |
| Rôle | Signaux heuristiques du tour (clarté, charge, risque, points couverts, etc.) |
| Couche | Domaine moteur — **non persisté tel quel** en prod apprenant |
| Exposition | Testeur + turn-review internal ; **absent** `/app` |
| Statut | **RÉEL OBSERVÉ** |
| Preuves | `turn_state_analyzer.py`, tests P0 |
| Champs P0 structurants | `episode_clarity`, `cognitive_load`, `interaction_risk`, `covered_points`, `reflection_phase`, `closure_signal`, `learner_help_request`, etc. |
| Variante v17 | `turn_state_v17`, `reconcile_turn_state_v17` — flag `HUGO_P0_V17_ENABLED` |
| Cible 2.0 | Aligné ; coexistence legacy/v17 à documenter |

---

## 4. ConversationDecision

| Attribut | Valeur |
|----------|--------|
| Nom doctrinal | Contrat de décision / DecisionContract |
| Nom réel | `ConversationDecision`, `decide_conversation()` |
| Rôle | Sortie structurée P0 : intent, move, questions, flags pédagogiques |
| Couche | Domaine moteur |
| Exposition | Interne ; testeur si debug |
| Statut | **RÉEL OBSERVÉ** |
| Mapping doctrinal | `primary_goal` → `primary_intent` ; `tutorial_move` → `pedagogical_move` |
| Variables clés | `number_of_questions`, `should_explain_briefly`, `reason_codes`, `response_constraints` |
| Cible 2.0 | **RENOMMER_DANS_DOC** — concept aligné, noms différents |

---

## 5. ConversationProgress

| Attribut | Valeur |
|----------|--------|
| Nom doctrinal | ConversationProgress / branches |
| Nom réel | `ConversationProgress` dataclass ; `build_conversation_progress_contract()` |
| Rôle | Branches, maturité, éligibilité synthèse/éval, RAG allowed |
| Couche | Dérivé inter-tours, persisté partiellement sur session |
| Exposition | Via `ui-state` (traduit) ; objet brut non exposé front prod |
| Statut | **RÉEL OBSERVÉ** |
| Champs | `branch_key`, `maturity`, `can_summarize`, `evaluation_eligible`, `reason_codes`, `dispersion_risk` (via contrat élargi) |

---

## 6. UIState

| Attribut | Valeur |
|----------|--------|
| Nom doctrinal | UIState |
| Nom réel | `build_contract_ui_state`, endpoint `GET .../ui-state/` |
| Rôle | Traduction produit backend-first |
| Couche | Dérivé post-tour |
| Exposition | Front `/app` via `engagementUiModel.js` |
| Statut | **RÉEL OBSERVÉ** |
| Contenu typique | `scene_label`, `scene_progress`, `quest_progress`, `maturity_color`, `synthesis_button_state`, `evaluation_button_state`, `persistent_objects`, `conversation_mode`, `learner_display_profile`, `ui.advisory` |
| ÉCART CONFIRMÉ | Double builder `build_ui_state` vs `build_contract_ui_state` |
| Cible 2.0 | Ne jamais exposer TurnState/P0 brut — **aligné réel** |

---

## 7. TutorPrompt

| Attribut | Valeur |
|----------|--------|
| Rôle | Pivot rendu prompt (system/user templates) |
| Couche | Persistence + `prompt_renderer.py` |
| Exposition | Sélection création session ; CRUD testeur |
| Statut | **RÉEL OBSERVÉ** |
| Coexistence | `render_with_tutor_prompt`, legacy AFEST, `render_tutor_prompt_v17` |
| Fallback | Profil global `LearnerConversationGlobalProfile` avec fallback legacy |

---

## 8. TutorConductProfile

| Attribut | Valeur |
|----------|--------|
| Rôle | Paramètres comportementaux par posture/org |
| Couche | Persistence + `conduct_profile_resolver.py` |
| Exposition | API `/hugo/conduct-profiles/` ; admin testeur |
| Statut | **RÉEL OBSERVÉ** local — **A_VERIFIER** Encoors (route absente 12/06) |
| Fallback | `domain/tutor_profiles.py` statique |

---

## 9. LearnerThemeMemory

| Attribut | Valeur |
|----------|--------|
| Nom doctrinal | Mémoire thématique inter-session |
| Nom réel | `LearnerThemeMemory` + `memory_consolidator.py` |
| Rôle | Stockage thématique post-conversation |
| Couche | Persistence |
| Exposition | `GET .../memory-summary/` (projection) |
| Statut | **RÉEL OBSERVÉ PARTIEL** — écriture oui, injection tour **non** |
| ÉCART CONFIRMÉ | Non référencé dans `hugo_orchestrator.py` |
| Lot courant | Hors périmètre injection immédiate |

---

## 10. SessionMemoryContract

| Attribut | Valeur |
|----------|--------|
| Rôle | Mémoire gouvernée intra-conversation |
| Producteur | `build_session_memory()` |
| Champs | `theme`, `learning_objective`, `facts_confirmed`, `open_points`, `pending_actions`, `memory_scope=intra_conversation` |
| Exposition | API memory-summary ; panneau `LearnerMemoryPanel` |
| Statut | **RÉEL OBSERVÉ** |
| ÉCART CONFIRMÉ | Non injectée dans `prompt_renderer` vars_dict |

---

## 11. LearnerEvaluationRecord

| Attribut | Valeur |
|----------|--------|
| Rôle | Enregistrement évaluation OneToOne session |
| Couche | Persistence |
| Exposition | Workflow request/finalize ; export trainer |
| Statut | **RÉEL OBSERVÉ** |
| Cible 2.0 | Fragment de `EvaluationTrace` doctrinal — mapping via pivot |

---

## 12. Trace / Evidence

| Objet | Rôle | Statut |
|-------|------|--------|
| `Trace` | Trace compétences session | **RÉEL OBSERVÉ PARTIEL** (payload minimal) |
| `TraceCriterionAssessment` | Critères | **RÉEL OBSERVÉ** |
| `Evidence` | Preuves attachées | **RÉEL OBSERVÉ** |

---

## 13. ConversationQualitySignal

| Attribut | Valeur |
|----------|--------|
| Rôle | Signaux qualité post-tour / analytics |
| Producteur | `record_session_signal` dans hooks post-message |
| Statut | **RÉEL OBSERVÉ** |
| Cible 2.0 | Catalogue signaux canonique **ABSENT** |

---

## 14. TrainerKnowledgeItem

| Attribut | Valeur |
|----------|--------|
| Rôle | Base connaissances formateur |
| Statuts | declared / derived / validated — enforcement partiel |
| Statut | **RÉEL OBSERVÉ PARTIEL+** |
| Documents | `ecarts — 40_base_connaissances_formateur.md` |

---

## 15. LearnerConversationGlobalProfile (juin 2026)

| Attribut | Valeur |
|----------|--------|
| Rôle | Profil conversationnel global par org, slots par posture |
| Résolution | `learner_profile_resolver.py` (session → groupe → org) |
| Admin | `/admin/conversation/learner/profiles` |
| Statut | **RÉEL OBSERVÉ** (local, tests 12 PASS) |
| Cible 2.0 | Raffine TutorPrompt ; coexiste avec legacy |

---

## 16. Variables de décision P0 (mapping cible ↔ réel)

| Variable cible / glossaire | Réel observé | Statut preuve |
|--------------------------|--------------|---------------|
| `primary_goal` | `primary_intent` (`ConversationDecision`) | **RÉEL OBSERVÉ** |
| `tutorial_move` | `pedagogical_move` | **RÉEL OBSERVÉ** |
| `mode` | Déduit via `protected_mode`, posture, phase | **RÉEL OBSERVÉ PARTIEL** |
| `target_question_count` | `number_of_questions` | **RÉEL OBSERVÉ** |
| `micro_explain_allowed` | `should_explain_briefly` | **RÉEL OBSERVÉ** |
| `use_theme_memory` | Flag décision / metadata — **non injection réelle LTM** | **ÉCART CONFIRMÉ** |
| `use_verbatim_retrieval` | Gouverné share + contexte ; pas mémoire UI | **RÉEL OBSERVÉ PARTIEL** |
| `use_rag` | `rag_allowed` progression + `select_rag_chunks` | **RÉEL OBSERVÉ** |
| `optional_evaluation_eligible` | `evaluation_eligible` progression | **RÉEL OBSERVÉ** |
| `reason_codes` | Présent TurnState, Decision, Progress | **RÉEL OBSERVÉ** |

Source détaillée : `variables_prompting.md`, `glossaire_alignement_hugo_reel_vs_spec.md`.

---

## 17. Objets cibles sans homonyme runtime

| Objet doctrinal | Statut réel | Note |
|-----------------|-------------|------|
| `EvaluationTrace` | **PARTIEL** | Pivot + dispersion records |
| `PersistentObjects` | **AMBIGU** | `persistent_objects` ui-state ≠ modèle dédié |
| `SessionInterstitial` | **CIBLE** | Aucun modèle — domaine 120 |
| `ConversationTurnLLMAnalysis` (produit) | **PARTIEL** | Export debug SUPERADMIN |
| `COORDO` (rôle) | **CIBLE** | Absent |

---

## 18. Index contrats API révélateurs

| Contrat | Endpoint | Statut |
|---------|----------|--------|
| UIState produit | `GET .../ui-state/` | **RÉEL OBSERVÉ** |
| Mémoire | `GET .../memory-summary/` | **RÉEL OBSERVÉ** |
| CTA synthèse | `POST .../request-synthesis/` | **RÉEL OBSERVÉ** |
| CTA évaluation | `POST .../request-evaluation/` | **RÉEL OBSERVÉ** |
| Posture | `POST .../set-posture/` | **RÉEL OBSERVÉ** |
| Partage | `POST .../share/` | **RÉEL OBSERVÉ** |
| Turn review | `GET /internal/.../turn-review/` | **RÉEL OBSERVÉ** |

---

*Sources : models.py, schemas.py, glossaire, cluster2, variables_prompting.md, ecarts domaine.*
