# Rapport d'audit dossier probatoire — 18 mai 2026

## Résumé exécutif
**ÉCARTS MINEURS — 5 écarts trouvés**

Le repo est globalement cohérent avec le dossier sur les points structurants demandés : les 10 fichiers déclarés existent bien, les champs `TurnState` demandés sont tous présents, les champs de `ConversationDecision` sont présents, les gestes attendus existent, et l'ordre principal de `decide_conversation()` est conforme.

Les écarts relevés portent surtout sur la localisation réelle de certains contrats et sur un décalage d'implémentation entre le pipeline décrit et le runtime réel :

1. `ConversationDecision` est défini dans `backend/apps/hugo/domain/schemas.py`, pas dans `decision_engine.py`.
2. `ConversationProgress`, `ConversationBranch` et `deserialize_conversation_progress()` sont définis dans `backend/apps/hugo/domain/conversation_profile.py`, pas dans `conversation_progress_calculator.py`.
3. Les guardrails de sortie ne sont pas dans `hugo_orchestrator.py` ; ils sont appliqués dans `backend/apps/hugo/views_sessions.py` après la réponse LLM.
4. Les flags `share_summary`, `share_evidence`, `share_verbatim` sont portés par `HugoSession`, pas par `Trace`.
5. Les noms Julia / Felix / Hector / Jeremy ne correspondent pas à des apps ou modèles réels dans le code audité ; le runtime est centré sur Hugo.

## Tâche 1 — Fichiers sources

| Fichier déclaré | Existe ? | Chemin réel |
|---|---|---|
| `backend/apps/hugo/domain/schemas.py` | OUI | `backend/apps/hugo/domain/schemas.py` |
| `backend/apps/hugo/services/hugo_orchestrator.py` | OUI | `backend/apps/hugo/services/hugo_orchestrator.py` |
| `backend/apps/hugo/services/turn_state_analyzer.py` | OUI | `backend/apps/hugo/services/turn_state_analyzer.py` |
| `backend/apps/hugo/services/p0_classifier.py` | OUI | `backend/apps/hugo/services/p0_classifier.py` |
| `backend/apps/hugo/services/decision_engine.py` | OUI | `backend/apps/hugo/services/decision_engine.py` |
| `backend/apps/hugo/services/teaching_plan_builder.py` | OUI | `backend/apps/hugo/services/teaching_plan_builder.py` |
| `backend/apps/hugo/services/phase_decider.py` | OUI | `backend/apps/hugo/services/phase_decider.py` |
| `backend/apps/hugo/services/prompt_renderer.py` | OUI | `backend/apps/hugo/services/prompt_renderer.py` |
| `backend/apps/hugo/services/conversation_progress_calculator.py` | OUI | `backend/apps/hugo/services/conversation_progress_calculator.py` |
| `backend/apps/hugo/views_sessions.py` | OUI | `backend/apps/hugo/views_sessions.py` |

**Conclusion Tâche 1 :** aucun écart de chemin sur les 10 fichiers listés.

## Tâche 2 — Champs TurnState

Source réelle vérifiée : `backend/apps/hugo/domain/schemas.py` (`TurnState`).

| Champ | Statut | Remarque |
|---|---|---|
| `has_concrete_actions` | PRÉSENT | `TurnState` |
| `episode_clarity` | PRÉSENT | `TurnState` |
| `problem_salience` | PRÉSENT | `TurnState` |
| `reflection_phase` | PRÉSENT | `TurnState` |
| `affect_valence` | PRÉSENT | `TurnState` |
| `cognitive_load` | PRÉSENT | `TurnState` |
| `interaction_risk` | PRÉSENT | `TurnState` |
| `session_phase` | PRÉSENT | `TurnState` |
| `reflective_depth` | PRÉSENT | `TurnState` |
| `self_efficacy_signal` | PRÉSENT | `TurnState` |
| `epistemic_balance` | PRÉSENT | `TurnState` |
| `zpd_estimate` | PRÉSENT | `TurnState` |
| `session_maturity` | PRÉSENT | `TurnState` |
| `evidence_strength` | PRÉSENT | `TurnState` |
| `intervention_necessity` | PRÉSENT | `TurnState` |
| `contradiction_status` | PRÉSENT | `TurnState` |
| `need_recap` | PRÉSENT | `TurnState` |
| `need_encouragement` | PRÉSENT | `TurnState` |
| `need_reframing` | PRÉSENT | `TurnState` |
| `can_close_for_now` | PRÉSENT | `TurnState` |
| `last_tutorial_move` | PRÉSENT | `TurnState` |
| `consecutive_clarify_turns` | PRÉSENT | `TurnState` |
| `sticky_has_concrete_actions` | PRÉSENT | `TurnState` |
| `tech_representation_level` | PRÉSENT | `TurnState` |
| `technical_criterion_focus` | PRÉSENT | `TurnState` |
| `safety_or_quality_risk_level` | PRÉSENT | `TurnState` |
| `covered_points` | PRÉSENT | `TurnState` |
| `remaining_open_points` | PRÉSENT | `TurnState` |
| `learner_help_request` | PRÉSENT | `TurnState` |
| `closure_signal` | PRÉSENT | `TurnState` |
| `repetition_signal` | PRÉSENT | `TurnState` |
| `loop_risk` | PRÉSENT | `TurnState` |
| `assistant_meta_leak_risk` | PRÉSENT | `TurnState` |
| `debug_signals` | PRÉSENT | `TurnState` |

**Conclusion Tâche 2 :** les champs demandés sont tous présents, sans renommage.

## Tâche 3 — ConversationDecision

**Localisation réelle du contrat :** `ConversationDecision` est défini dans `backend/apps/hugo/domain/schemas.py`.
`backend/apps/hugo/services/decision_engine.py` l'importe et l'instancie, mais ne porte pas la définition de la classe.

### Champs

- `primary_intent` — PRÉSENT
- `pedagogical_move` — PRÉSENT
- `number_of_questions` — PRÉSENT
- `question_style` — PRÉSENT
- `should_explain_briefly` — PRÉSENT
- `should_recap` — PRÉSENT
- `should_encourage` — PRÉSENT
- `should_reframe` — PRÉSENT
- `should_close` — PRÉSENT
- `response_constraints` — PRÉSENT
- `reason_codes` — PRÉSENT
- `metadata` — PRÉSENT

### Gestes `pedagogical_move`

- `clarify` — PRÉSENT
- `elicit_action` — PRÉSENT
- `problematize` — PRÉSENT
- `analyze` — PRÉSENT
- `contrast_gently` — PRÉSENT
- `project` — PRÉSENT
- `reassure` — PRÉSENT
- `reformulate` — PRÉSENT
- `repair` — PRÉSENT
- `pace` — PRÉSENT
- `close` — PRÉSENT
- `assist` — PRÉSENT

**Remarque :** ces gestes existent comme valeurs littérales utilisées par la logique, pas comme enum séparée.

## Tâche 4 — Hiérarchie de décision

### Ordre déclaré

1. `protected_mode`
2. `explicit_closure_case`
3. `explicit_repetition_case`
4. `explicit_help_request_case`
5. `safety_or_quality_risk_level`
6. `contradiction`
7. `closeable_case`
8. `clarify_frontier_reached`
9. `analysis_case`
10. `projection_case`

### Ordre réel dans `decide_conversation()`

1. `protected_mode`
2. `explicit_closure_case`
3. `explicit_repetition_case`
4. `explicit_help_request_case`
5. `state.safety_or_quality_risk_level in {"medium", "high"}`
6. `state.contradiction_status == "suspected" and state.episode_clarity in {"medium", "high"}`
7. `closeable_case`
8. `clarify_frontier_reached`
9. `analysis_case`
10. `projection_case`

### Écarts

- Aucun écart d'ordre sur les 10 branches demandées.
- Différence mineure de formulation : la branche 5 teste explicitement `{"medium", "high"}`.
- Différence mineure de formulation : la branche 6 s'appuie sur `contradiction_status == "suspected"` plutôt qu'un label nommé simplement `contradiction`.

**Conclusion Tâche 4 :** ordre conforme.

## Tâche 5 — ConversationProgress

### Vérifications

- `deserialize_conversation_progress()` — **PRÉSENT**
- `ConversationProgress` dataclass — **PRÉSENT**
- `ConversationBranch` dataclass — **PRÉSENT**

### Localisation réelle

Ces éléments ne sont pas définis dans `backend/apps/hugo/services/conversation_progress_calculator.py`.
Ils sont définis dans `backend/apps/hugo/domain/conversation_profile.py`.

`backend/apps/hugo/services/conversation_progress_calculator.py` :

- importe ces dataclasses,
- calcule et met à jour leur contenu,
- expose `build_conversation_progress_contract()`.

### Champs de `ConversationProgress`

| Champ | Statut | Remarque |
|---|---|---|
| `session_id` | PRÉSENT | `ConversationProgress` réel |
| `posture` | PRÉSENT | `ConversationProgress` réel |
| `active_branches` | PRÉSENT | `ConversationProgress` réel |
| `active_branches_count` | PRÉSENT | `ConversationProgress` réel |
| `priority_branch_id` | PRÉSENT | `ConversationProgress` réel |
| `dispersion_risk` | PRÉSENT | `ConversationProgress` réel |
| `overall_maturity` | PRÉSENT | `ConversationProgress` réel |
| `synthesis_eligible` | PRÉSENT | `ConversationProgress` réel |
| `evaluation_eligible` | PRÉSENT | `ConversationProgress` réel |
| `missing_for_next_level` | PRÉSENT | `ConversationProgress` réel |
| `reason_codes` | PRÉSENT | `ConversationProgress` réel |

**Conclusion Tâche 5 :** contrat conforme, mais localisation différente de celle suggérée.

## Tâche 6 — Pipeline orchestrateur

### Chaîne déclarée

`build_hugo_turn` → `analyze_turn_state` → `classify_p0_turn_state` → `decide_conversation` → `build_teaching_plan` → `decide_next_phase` → `render_with_tutor_prompt` → guardrails de sortie

### Chaîne réelle

| Étape déclarée | Réalité dans le code | Statut |
|---|---|---|
| `build_hugo_turn` | `build_hugo_turn()` dans `hugo_orchestrator.py` | CONFORME |
| `analyze_turn_state` | `analyze_turn_state(...)` | CONFORME |
| `classify_p0_turn_state` | `classify_p0_turn_state(...)` | CONFORME |
| `decide_conversation` | `decide_conversation(...)` si v17 désactivé, sinon `decide_conversation_v17(...)` + conversion legacy | CONFORME AVEC VARIANTE |
| `build_teaching_plan` | `build_teaching_plan(...)` | CONFORME |
| `decide_next_phase` | `decide_next_phase(...)` | CONFORME |
| `render_with_tutor_prompt` | `render_with_tutor_prompt(...)` en chemin principal | CONFORME |
| `guardrails de sortie` | appliqués plus tard dans `views_sessions.py` via `_apply_reply_guardrails()` après l'appel LLM | ÉCART |

### Écarts

- Le pipeline principal de l'orchestrateur est conforme jusqu'au rendu.
- Les guardrails de sortie ne font pas partie de `hugo_orchestrator.py` : ils sont exécutés dans `backend/apps/hugo/views_sessions.py` au moment de persister et rendre la réponse assistant.
- Il existe en plus une branche runtime v17 conditionnée par `HUGO_P0_V17_ENABLED`.

## Tâche 7 — RLS et flags de partage

### Tables vérifiées

| Entité demandée | Équivalent réel | `organisation_id` présent ? | Remarque |
|---|---|---|---|
| Session | `apps.hugo.models.HugoSession` | OUI | via FK Django `organisation`, donc colonne DB `organisation_id` |
| Trace | `apps.hugo.models.Trace` | OUI | via FK Django `organisation` |
| Document | `apps.library.models.Document` | OUI | via FK Django `organisation` |
| Learner | `apps.accounts.models.User` avec rôle `LEARNER` | OUI | pas de modèle `Learner` séparé |
| Group | `apps.referentials.models.Group` | OUI | via FK Django `organisation` |

### Flags de partage

| Flag | Trouvé ? | Localisation réelle |
|---|---|---|
| `share_summary` | OUI | `apps.hugo.models.HugoSession` |
| `share_evidence` | OUI | `apps.hugo.models.HugoSession` |
| `share_verbatim` | OUI | `apps.hugo.models.HugoSession` |

### Écart

- Les flags existent bien, mais sur `HugoSession` et non sur `Trace`.

## Tâche 8 — Noms réels vs noms génériques du dossier

| Nom générique du dossier | Réalité dans le code/config | Remarque |
|---|---|---|
| Hugo | `apps.hugo`, URL `hugo/`, `/api/hugo/...`, modèles `HugoSession`, `HugoMessage` | nom réellement utilisé |
| Julia | Aucun app/modèle/URL Python trouvé | absent du runtime audité |
| Felix / Félix | Aucun app/modèle/URL Python trouvé | absent du runtime audité |
| Hector | Aucun app/modèle/URL Python trouvé | absent du runtime audité |
| Jeremy / Jérémy | Aucun app/modèle/URL Python trouvé | absent du runtime audité |
| Plateforme | `POC Hugo` | visible dans `backend/config/settings/base.py`, `config/urls.py`, commentaires nginx |
| Base de données / bucket | `hugo_poc`, `hugo-poc` | cohérents avec une plateforme Hugo seule |
| Postures métier réelles | `diagnostic`, `reflective_afest`, `knowledge_review` | noms métier présents dans le code |

**Conclusion Tâche 8 :** le code et la config audités portent une identité Hugo-only / POC Hugo. Les autres prénoms du dossier apparaissent comme des noms génériques documentaires, pas comme des noms commerciaux ou runtime implémentés.

## Corrections à apporter au dossier probatoire

Hypothèse : la **Pièce 04** est la pièce technique qui inventorie les fichiers, contrats et pipelines. Là où la répartition exacte entre pièces 01-04 n'est pas visible ici, la pièce la plus probable est indiquée.

1. **Pièce 04** — corriger la localisation de `ConversationDecision` : remplacer toute formulation laissant entendre que la classe est définie dans `backend/apps/hugo/services/decision_engine.py` par :  
   **"`ConversationDecision` est défini dans `backend/apps/hugo/domain/schemas.py` et instancié par `backend/apps/hugo/services/decision_engine.py`."**

2. **Pièce 04** — corriger la localisation de `ConversationProgress`, `ConversationBranch` et `deserialize_conversation_progress()` : remplacer toute formulation les rattachant à `backend/apps/hugo/services/conversation_progress_calculator.py` par :  
   **"Les dataclasses `ConversationProgress` et `ConversationBranch`, ainsi que `deserialize_conversation_progress()`, sont définies dans `backend/apps/hugo/domain/conversation_profile.py` ; `backend/apps/hugo/services/conversation_progress_calculator.py` calcule et met à jour ce contrat."**

3. **Pièce 04** — corriger la description du pipeline runtime : remplacer **"guardrails de sortie dans l'orchestrateur"** par :  
   **"guardrails de sortie appliqués après l'appel LLM dans `backend/apps/hugo/views_sessions.py` (`_apply_reply_guardrails()`), et non dans `hugo_orchestrator.py`."**

4. **Pièce 03 ou Pièce 04** — corriger la localisation des flags de partage : remplacer toute formulation du type **"flags de partage sur Trace"** par :  
   **"Les flags `share_summary`, `share_evidence`, `share_verbatim` sont portés par `HugoSession`."**

5. **Pièce 01 / 02 / 04 selon l'endroit où les noms sont exposés** — clarifier les noms génériques vs noms réels : ajouter une mention explicite du type :  
   **"Les noms Julia, Felix, Hector et Jeremy sont utilisés ici comme désignations génériques documentaires ; le code audité implémente un périmètre runtime centré sur Hugo (`apps.hugo`, `/api/hugo/`, `HugoSession`)."**

6. **Pièce 03 ou Pièce 04** — clarifier le modèle `Learner` : si le dossier parle d'une table ou d'un modèle `Learner`, remplacer par :  
   **"`Learner` correspond dans le code réel à `accounts.User` avec rôle `LEARNER` ; il n'existe pas de modèle Django séparé nommé `Learner`."**

7. **Pièce 03 ou Pièce 04** — clarifier le champ RLS côté Django : si le dossier affirme un champ ORM littéral `organisation_id` sur tous les modèles, reformuler en :  
   **"Dans les modèles Django, la colonne DB `organisation_id` est portée par une FK `organisation` vers `accounts.Organisation`."**
