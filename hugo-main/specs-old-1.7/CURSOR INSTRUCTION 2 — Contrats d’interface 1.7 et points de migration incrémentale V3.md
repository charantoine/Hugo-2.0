# CURSOR INSTRUCTION 2 — Contrats d’interface 1.7 et points de migration incrémentale

Objectif

Stabiliser des interfaces minimales pour implémenter Hugo P0 1.7 sans réécriture totale, avec une migration incrémentale et traçable.

Contraintes générales

- Cette instruction est autoportante.
- Ne pas supposer l’existence de conventions ou de ressources externes non présentes dans le repo.
- Utiliser `snake_case` pour tous les nouveaux champs et helpers Python.
- Garder le moteur de décision lisible en Python explicite.
- Un framework d’orchestration éventuel peut être utilisé comme outillage, mais la logique métier doit rester testable indépendamment.

## 1. Interfaces cibles

### 1.1 `analyze_turn_state_v17`

Fichier cible :
`backend/apps/hugo/services/turn_state_analyzer_v17.py`

Signature cible :

```python
def analyze_turn_state_v17(
    context: HugoContext,
    learner_message: str,
    requested_phase: str | None = None,
) -> TurnStateV17:
    ...
```

Obligations :
- remplir tous les champs core / derived / conversation / debug ;
- renseigner `covered_points`, `remaining_open_points`, `learner_help_request`, `closure_signal`, `repetition_signal`, `loop_risk`, `sticky_has_concrete_actions`, `last_tutorial_move`, `consecutive_clarify_turns`, `last_learner_act` ;
- ne jamais laisser les nouveaux champs critiques absents ou à `None` ;
- utiliser des valeurs enum explicites plutôt que du texte libre.

### 1.2 `classify_p0_turn_state_v17`

Fichier cible :
`backend/apps/hugo/services/p0_classifier_v17.py`

Signature cible :

```python
def classify_p0_turn_state_v17(
    state: TurnStateV17,
    context: HugoContext,
    config: P0RuntimeConfig,
) -> TurnStateV17:
    ...
```

Règles :
- conserver la philosophie actuelle d’override partiel ;
- ne surclasser que les champs réellement autorisés ;
- recalculer les signaux dérivés après override ;
- logguer proprement `source_by_field`, `override_fields`, `p0_classifier_confidence`.

### 1.3 `classify_learner_speech_act`

Fichier cible :
`backend/apps/hugo/services/learner_speech_act_classifier.py`

Signature cible :

```python
def classify_learner_speech_act(
    learner_message: str,
    recent_history: list[str] | None = None,
) -> LearnerSpeechActResult:
    ...
```

### 1.4 `apply_speech_act_overrides`

Fichier cible :
`backend/apps/hugo/services/apply_speech_act_overrides.py`

Signature cible :

```python
def apply_speech_act_overrides(
    state: TurnStateV17,
) -> dict[str, Any]:
    ...
```

Le résultat doit pouvoir forcer ou suggérer :
- `primary_intent`
- `pedagogical_move`
- `response_mode`
- `target_question_count`
- `number_of_questions`
- `response_constraints`
- `reason_codes`
- `metadata`

Important :
- `target_question_count` est la cible décidée backend ;
- `number_of_questions` est le nombre effectivement conservé après rendu final et guardrails ;
- `number_of_questions` ne doit jamais dépasser `target_question_count`.

### 1.5 `decide_conversation_v17`

Fichier cible :
`backend/apps/hugo/services/decision_engine_v17.py`

Signature cible :

```python
def decide_conversation_v17(
    state: TurnStateV17,
) -> ConversationDecisionV17:
    ...
```

### 1.6 `build_teaching_plan_v17`

Fichier cible :
`backend/apps/hugo/services/teaching_plan_builder_v17.py`

Signature cible :

```python
def build_teaching_plan_v17(
    state: TurnStateV17,
    decision: ConversationDecisionV17,
    session_phase: str,
) -> TeachingPlan:
    ...
```

Obligations :
- refléter `conversation_goal`
- refléter `response_mode`
- refléter `target_question_count`
- garder cohérence avec `session_phase`

### 1.7 `render_tutor_prompt_v17`

Fichier cible :
`backend/apps/hugo/services/prompt_renderer_v17.py`

Signature cible :

```python
def render_tutor_prompt_v17(
    context: HugoContext,
    state: TurnStateV17,
    decision: ConversationDecisionV17,
    profile: TutorPromptProfile,
) -> RenderedPrompt:
    ...
```

Important :
- ne pas injecter une multitude de placeholders fins ;
- injecter surtout des blocs robustes et les signaux critiques résolus ;
- inclure `response_mode`, `target_question_count` et les contraintes de sortie dans les métadonnées prompt.

### 1.8 `apply_output_guardrails_v17`

Fichier cible :
`backend/apps/hugo/services/output_guardrails_v17.py`

Signature cible :

```python
def apply_output_guardrails_v17(
    raw_response: str,
    decision: ConversationDecisionV17,
    profile: TutorPromptProfile,
) -> str:
    ...
```

## 2. Matrice minimale d’arbitrage

Coder une matrice explicite qui priorise, dans cet ordre :
1. demande explicite d’aide / récap / compétences / rapport / clôture ;
2. sécurité / qualité ;
3. répétition / risque de boucle ;
4. maturité de couverture ;
5. opportunité pédagogique latente.

Cette hiérarchie est obligatoire. Elle remplace la dépendance trop forte aux seules heuristiques de phase et de description.

## 3. Contrat anti-redondance

Ajouter une fonction pure :

```python
def is_redundant_question_candidate(
    candidate_question: str,
    covered_points: list[str],
    remaining_open_points: list[str],
    last_tutorial_move: str,
    blocked_question_topics: list[str] | None = None,
) -> bool:
    ...
```

But :
- empêcher qu’une même question soit reposée sur un point déjà stabilisé ;
- augmenter `loop_risk` si le système insiste malgré couverture suffisante ;
- respecter `blocked_question_topics` jusqu’au rendu final.

## 4. Contrat de maturité

Ajouter une fonction pure :

```python
def compute_maturity_flags(state: TurnStateV17) -> dict[str, bool]:
    ...
```

Elle doit au minimum produire :
- `reflective_minimum_reached`
- `recap_eligible`
- `recap_evaluation_eligible`
- `evaluation_eligible`
- `closure_eligible`
- `recap_evaluation_offer_pending`

Règles minimales :
- `reflective_minimum_reached` si faits + cause probable + action future plausible sont présents
- `closure_eligible` si `reflective_minimum_reached` et faible risque, ou signal explicite compatible
- `recap_evaluation_eligible` selon les conditions formalisées dans l’instruction 1
- `recap_evaluation_offer_pending` si `recap_evaluation_eligible` est vrai et qu’aucun pivot bilan / trace n’a encore été proposé dans la séquence courante
- ces booléens doivent être utilisés réellement dans la décision, pas seulement loggés

Précision métier obligatoire sur `recap_evaluation_offer_pending` :
- `recap_evaluation_offer_pending` ne force jamais à lui seul un basculement automatique en `response_mode = "recap"` ou `response_mode = "evaluation"` ;
- ce signal impose seulement qu’un pivot bref, léger et optionnel soit proposé au moins une fois dans la séquence courante, si aucune demande plus prioritaire ne domine ;
- si une demande d’aide explicite, un besoin de clarification, un risque sécurité / qualité, une confusion ou une répétition domine le tour, ce pivot doit être différé ;
- une fois le pivot déjà proposé dans la séquence courante, il ne doit pas être reproposé mécaniquement à chaque tour.

## 5. Logging et reason codes

Le nouveau code doit tracer clairement :
- pourquoi `response_mode` a été choisi ;
- pourquoi `target_question_count` a été choisi ou réduit ;
- pourquoi une clôture a été autorisée ou refusée ;
- pourquoi une demande explicite de bilan / compétences / rapport a été reconnue ;
- pourquoi un cas a été marqué redondant.
- pourquoi un pivot bilan / trace a été proposé, différé, ou considéré comme déjà offert

Utiliser des `reason_codes` courts et stables.

## 6. Backward compatibility

Ne pas casser les appels existants.

Stratégie recommandée :
- conserver les services historiques ;
- créer des wrappers v17 ;
- activer le nouveau flux derrière un feature flag ;
- comparer les sorties old vs v17 sur des scénarios de test définis dans le repo.

## 7. Rendu prompt et guardrails

Le renderer et les guardrails doivent être strictement subordonnés à la décision backend.

Règles obligatoires :
- `ConversationDecisionV17.response_mode` est prioritaire sur tout mode de sortie dérivé plus ancien ;
- `target_question_count` est la contrainte principale sur le nombre de questions ;
- si `target_question_count == 0`, la sortie finale ne doit contenir aucune question ;
- si `target_question_count == 1`, garder au plus une question ;
- si `target_question_count == 2`, garder au plus deux questions sur le même micro-objectif ;
- si `response_mode in {"recap", "evaluation", "closure"}`, supprimer les questions parasites sauf exception explicitement autorisée ;
- si `response_mode in {"recap", "evaluation", "closure"}`, supprimer aussi les listes à puces, checklists et batteries de questions, sauf exception explicitement autorisée dans `response_constraints` ;
- si `should_acknowledge_repetition is True`, conserver ou injecter une courte reconnaissance au début ;
- si `should_acknowledge_closure is True`, conserver ou injecter une courte reconnaissance de fin ;
- ne pas laisser un ancien format de type trop interrogatif contredire la décision locale.

Important :
- il n’existe pas de `response_mode` séparé pour le formateur ;
- une demande de texte pour formateur utilise `response_mode = "recap"` avec `metadata["audience"] = "tutor"` ;
- la vue compétences utilise `response_mode = "evaluation"` au sens d’un mini-récap structuré enrichi par une mise en mots prudente et crédible des compétences mobilisées ou plausibles, pas d’un verdict scolaire ;
- si `metadata["evaluation_kind"] == "recap_with_competencies"`, le renderer doit privilégier une forme : mini-récap d’abord, compétences ensuite.
- si `recap_evaluation_offer_pending is True` et qu’aucune demande plus prioritaire ne domine, la décision finale doit proposer au moins une fois un pivot bref et optionnel vers mini-récap, bilan prudent ou trace pour formateur ;
- ce pivot ne doit pas être reproposé mécaniquement s’il a déjà été offert dans la séquence courante.

## 8. Tests obligatoires

Créer au moins les tests suivants :

1. `test_explicit_help_request_routes_to_diagnostic_help`
2. `test_priority_question_does_not_return_checklist`
3. `test_repetition_signal_blocks_same_question_again`
4. `test_closure_signal_prevents_reopening`
5. `test_explicit_recap_request_forces_recap_mode`
6. `test_explicit_report_request_forces_recap_with_tutor_audience`
7. `test_explicit_competency_request_forces_evaluation_mode_with_recap_with_competencies_kind`
8. `test_mature_scene_triggers_recap_or_closure_instead_of_exploration`
9. `test_target_question_count_zero_removes_questions_in_guardrails`
10. `test_response_mode_priority_over_legacy_output_mode`
11. `test_new_v17_fields_are_snake_case`
12. `test_recap_evaluation_eligible_triggers_one_offer_of_recap_or_trace`
13. `test_offer_pending_does_not_force_recap_when_help_request_is_more_urgent`
    - setup : `recap_evaluation_eligible = True` et `recap_evaluation_offer_pending = True`
    - input : message contenant une demande d’aide explicite de type diagnostic
    - attendu : `primary_intent = "diagnostic_help"` ou posture d’aide équivalente
    - attendu : pas de bascule forcée en `response_mode = "recap"` ou `response_mode = "evaluation"`
    - attendu : le pivot récap / bilan peut être différé à un tour ultérieur

## 9. Definition of done

La migration v17 est acceptable si :
- toutes les nouvelles interfaces compilent ;
- tous les noms 1.7 sont en `snake_case` ;
- les tests passent ;
- `response_mode` est calculé backend-side et consommé jusqu’aux guardrails ;
- `target_question_count` est respecté jusqu’à la sortie finale ;
- les sorties `recap` / `evaluation` / `closure` sont sans listes de questions parasites ;
- les demandes explicites de l’apprenant priment vraiment sur la logique générique de description.