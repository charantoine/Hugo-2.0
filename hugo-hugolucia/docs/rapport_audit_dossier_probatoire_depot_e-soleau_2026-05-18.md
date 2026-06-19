# Rapport d'audit dossier probatoire — version dépôt e-Soleau
**Date : 18 mai 2026**

## Résumé exécutif
Le présent audit de cohérence entre les pièces techniques du dossier probatoire et l'état réel du code source du dépôt audité fait apparaître une **concordance globale satisfaisante**, avec des **écarts mineurs de localisation documentaire et de qualification de certains éléments techniques**.

Les constats principaux sont les suivants :

1. Les fichiers sources annoncés en Pièce 04 existent bien dans le dépôt, aux chemins déclarés.
2. Le contrat d'état `TurnState` contient l'ensemble des champs attendus.
3. Le contrat `ConversationDecision` contient l'ensemble des champs attendus, et les gestes pédagogiques listés sont bien implémentés.
4. La hiérarchie principale de décision de `decide_conversation()` est conforme à l'ordre annoncé.
5. Le contrat `ConversationProgress` existe bien, mais ses dataclasses et sa fonction de désérialisation sont localisées dans `backend/apps/hugo/domain/conversation_profile.py`, et non dans `backend/apps/hugo/services/conversation_progress_calculator.py`.
6. Les guardrails de sortie existent bien dans le runtime, mais sont appliqués dans `backend/apps/hugo/views_sessions.py` après l'appel LLM, et non directement dans `backend/apps/hugo/services/hugo_orchestrator.py`.
7. Les indicateurs de partage `share_summary`, `share_evidence`, `share_verbatim` existent bien, mais sont portés par `HugoSession`, et non par `Trace`.
8. Le code audité correspond à une implémentation centrée sur **Hugo** ; les noms Julia, Felix, Hector et Jeremy n'apparaissent pas comme des composants runtime réels du backend audité.

**Qualification finale : ÉCARTS MINEURS.**

## Tâche 1 — Vérification des fichiers sources

Les dix fichiers déclarés comme pièces sources ont été vérifiés dans le dépôt.

| Fichier déclaré | Statut | Observation |
|---|---|---|
| `backend/apps/hugo/domain/schemas.py` | PRÉSENT | Conforme |
| `backend/apps/hugo/services/hugo_orchestrator.py` | PRÉSENT | Conforme |
| `backend/apps/hugo/services/turn_state_analyzer.py` | PRÉSENT | Conforme |
| `backend/apps/hugo/services/p0_classifier.py` | PRÉSENT | Conforme |
| `backend/apps/hugo/services/decision_engine.py` | PRÉSENT | Conforme |
| `backend/apps/hugo/services/teaching_plan_builder.py` | PRÉSENT | Conforme |
| `backend/apps/hugo/services/phase_decider.py` | PRÉSENT | Conforme |
| `backend/apps/hugo/services/prompt_renderer.py` | PRÉSENT | Conforme |
| `backend/apps/hugo/services/conversation_progress_calculator.py` | PRÉSENT | Conforme |
| `backend/apps/hugo/views_sessions.py` | PRÉSENT | Conforme |

**Conclusion :** aucun écart de chemin n'a été constaté sur les fichiers explicitement déclarés.

## Tâche 2 — Vérification des contrats d'état

La structure `TurnState`, localisée dans `backend/apps/hugo/domain/schemas.py`, a été vérifiée.

Tous les champs listés au cahier d'audit sont **présents**, sans écart de nommage nécessitant correction.

| Champ | Statut | Observation |
|---|---|---|
| `has_concrete_actions` | PRÉSENT | Conforme |
| `episode_clarity` | PRÉSENT | Conforme |
| `problem_salience` | PRÉSENT | Conforme |
| `reflection_phase` | PRÉSENT | Conforme |
| `affect_valence` | PRÉSENT | Conforme |
| `cognitive_load` | PRÉSENT | Conforme |
| `interaction_risk` | PRÉSENT | Conforme |
| `session_phase` | PRÉSENT | Conforme |
| `reflective_depth` | PRÉSENT | Conforme |
| `self_efficacy_signal` | PRÉSENT | Conforme |
| `epistemic_balance` | PRÉSENT | Conforme |
| `zpd_estimate` | PRÉSENT | Conforme |
| `session_maturity` | PRÉSENT | Conforme |
| `evidence_strength` | PRÉSENT | Conforme |
| `intervention_necessity` | PRÉSENT | Conforme |
| `contradiction_status` | PRÉSENT | Conforme |
| `need_recap` | PRÉSENT | Conforme |
| `need_encouragement` | PRÉSENT | Conforme |
| `need_reframing` | PRÉSENT | Conforme |
| `can_close_for_now` | PRÉSENT | Conforme |
| `last_tutorial_move` | PRÉSENT | Conforme |
| `consecutive_clarify_turns` | PRÉSENT | Conforme |
| `sticky_has_concrete_actions` | PRÉSENT | Conforme |
| `tech_representation_level` | PRÉSENT | Conforme |
| `technical_criterion_focus` | PRÉSENT | Conforme |
| `safety_or_quality_risk_level` | PRÉSENT | Conforme |
| `covered_points` | PRÉSENT | Conforme |
| `remaining_open_points` | PRÉSENT | Conforme |
| `learner_help_request` | PRÉSENT | Conforme |
| `closure_signal` | PRÉSENT | Conforme |
| `repetition_signal` | PRÉSENT | Conforme |
| `loop_risk` | PRÉSENT | Conforme |
| `assistant_meta_leak_risk` | PRÉSENT | Conforme |
| `debug_signals` | PRÉSENT | Conforme |

**Conclusion :** le contrat `TurnState` est cohérent avec le descriptif probatoire sur les champs audités.

## Tâche 3 — Vérification de `ConversationDecision`

Le contrat `ConversationDecision` a été vérifié.

### Champs
Tous les champs demandés sont présents :

- `primary_intent`
- `pedagogical_move`
- `number_of_questions`
- `question_style`
- `should_explain_briefly`
- `should_recap`
- `should_encourage`
- `should_reframe`
- `should_close`
- `response_constraints`
- `reason_codes`
- `metadata`

### Gestes pédagogiques
Les valeurs suivantes de `pedagogical_move` sont bien implémentées dans la logique décisionnelle :

- `clarify`
- `elicit_action`
- `problematize`
- `analyze`
- `contrast_gently`
- `project`
- `reassure`
- `reformulate`
- `repair`
- `pace`
- `close`
- `assist`

### Observation documentaire
Le contrat `ConversationDecision` est **défini dans** `backend/apps/hugo/domain/schemas.py` et **utilisé par** `backend/apps/hugo/services/decision_engine.py`.

**Conclusion :** conformité fonctionnelle, avec une précision documentaire à apporter sur la localisation exacte de la classe.

## Tâche 4 — Vérification de la hiérarchie de décision

La fonction `decide_conversation()` a été auditée.

L'ordre de priorité réel observé est le suivant :

1. `protected_mode`
2. `explicit_closure_case`
3. `explicit_repetition_case`
4. `explicit_help_request_case`
5. `safety_or_quality_risk_level`
6. `contradiction_status == "suspected"`
7. `closeable_case`
8. `clarify_frontier_reached`
9. `analysis_case`
10. `projection_case`

**Conclusion :** la hiérarchie réelle est conforme à l'ordre approximatif déclaré.  
Seule une légère différence de formulation apparaît sur la branche de contradiction, qui repose techniquement sur `contradiction_status == "suspected"`.

## Tâche 5 — Vérification de `ConversationProgress`

Les éléments suivants ont été vérifiés :

- `deserialize_conversation_progress()` : **PRÉSENT**
- `ConversationProgress` : **PRÉSENT**
- `ConversationBranch` : **PRÉSENT**

Les champs suivants de `ConversationProgress` sont présents :

- `session_id`
- `posture`
- `active_branches`
- `active_branches_count`
- `priority_branch_id`
- `dispersion_risk`
- `overall_maturity`
- `synthesis_eligible`
- `evaluation_eligible`
- `missing_for_next_level`
- `reason_codes`

### Observation documentaire
Ces éléments sont localisés dans `backend/apps/hugo/domain/conversation_profile.py`.  
Le fichier `backend/apps/hugo/services/conversation_progress_calculator.py` assure le calcul et la mise à jour de ce contrat, mais n'en porte pas la définition.

**Conclusion :** conformité substantielle, avec correction documentaire de localisation à prévoir.

## Tâche 6 — Vérification du pipeline orchestrateur

Le pipeline réel observé est le suivant :

`build_hugo_turn`  
→ `analyze_turn_state`  
→ `classify_p0_turn_state`  
→ `decide_conversation`  
→ `build_teaching_plan`  
→ `decide_next_phase`  
→ `render_with_tutor_prompt`

### Observation sur les guardrails de sortie
Les guardrails de sortie existent bien dans le runtime, mais ils ne sont pas exécutés dans `hugo_orchestrator.py`.  
Ils sont appliqués ultérieurement, dans `backend/apps/hugo/views_sessions.py`, via `_apply_reply_guardrails()`, après production de la réponse LLM.

### Observation complémentaire
Le runtime comporte également une branche conditionnelle `v17` activable par configuration (`HUGO_P0_V17_ENABLED`).

**Conclusion :** pipeline conforme dans sa chaîne principale, avec une précision à apporter sur l'emplacement d'application des guardrails de sortie.

## Tâche 7 — Vérification du modèle de données (RLS)

### Présence de `organisation_id`
La présence effective de la colonne DB `organisation_id` a été vérifiée, via les FK Django `organisation`, sur les entités métier principales auditées :

| Entité métier | Équivalent réel | Statut |
|---|---|---|
| Session | `HugoSession` | Conforme |
| Trace | `Trace` | Conforme |
| Document | `Document` | Conforme |
| Learner | `accounts.User` rôle `LEARNER` | Conforme |
| Group | `Group` | Conforme |

### Présence des flags de partage
Les flags suivants sont présents :

- `share_summary`
- `share_evidence`
- `share_verbatim`

### Observation documentaire
Ces trois flags sont portés par `HugoSession`, et non par `Trace`.

**Conclusion :** cohérence fonctionnelle RLS et partage ; une correction documentaire est nécessaire sur la localisation des flags de partage.

## Tâche 8 — Identification des noms commerciaux réels

Les noms réellement présents dans le code et la configuration sont les suivants :

| Référence documentaire | Réalité observée |
|---|---|
| Hugo | `apps.hugo`, `HugoSession`, `HugoMessage`, URLs `/hugo/` et `/api/hugo/` |
| Plateforme | `POC Hugo` |
| Base technique associée | `hugo_poc`, `hugo-poc` |
| Postures métier | `diagnostic`, `reflective_afest`, `knowledge_review` |

Les noms Julia, Felix, Hector et Jeremy n'ont pas été retrouvés comme composants backend, URLs, apps Django ou modèles métiers du runtime Python audité.

**Conclusion :** le code audité correspond à une implémentation commercialement et techniquement centrée sur Hugo.

## Corrections à apporter au dossier probatoire

1. **Pièce 04** — préciser que `ConversationDecision` est défini dans `backend/apps/hugo/domain/schemas.py` et utilisé par `backend/apps/hugo/services/decision_engine.py`.
2. **Pièce 04** — préciser que `ConversationProgress`, `ConversationBranch` et `deserialize_conversation_progress()` sont définis dans `backend/apps/hugo/domain/conversation_profile.py`, tandis que `backend/apps/hugo/services/conversation_progress_calculator.py` calcule et met à jour ce contrat.
3. **Pièce 04** — remplacer toute mention indiquant que les guardrails de sortie sont dans `hugo_orchestrator.py` par une formulation exacte indiquant leur application dans `backend/apps/hugo/views_sessions.py`, après l'appel LLM.
4. **Pièce 03 ou Pièce 04** — corriger la localisation des flags `share_summary`, `share_evidence`, `share_verbatim`, en indiquant qu'ils sont portés par `HugoSession`.
5. **Pièce 01, 02 ou 04 selon le cas** — préciser que Julia, Felix, Hector et Jeremy sont des désignations génériques documentaires et que le périmètre runtime audité est centré sur Hugo.
6. **Pièce 03 ou Pièce 04** — si le dossier mentionne un modèle `Learner` autonome, préciser que l'équivalent réel est `accounts.User` avec rôle `LEARNER`.
7. **Pièce 03 ou Pièce 04** — si le dossier décrit un champ ORM littéral `organisation_id`, préciser qu'en Django la colonne `organisation_id` est matérialisée via une clé étrangère `organisation`.

## Conclusion générale
Au vu des vérifications effectuées, le dossier probatoire apparaît **globalement cohérent** avec l'état réel du code source audité. Les écarts constatés sont de nature **documentaire et descriptive**, sans remise en cause de la présence effective des principaux composants techniques ni des contrats fonctionnels attendus.

En l'état, le dossier peut être rapproché du code réel sous réserve d'intégrer les corrections de formulation et de localisation ci-dessus avant dépôt final.
