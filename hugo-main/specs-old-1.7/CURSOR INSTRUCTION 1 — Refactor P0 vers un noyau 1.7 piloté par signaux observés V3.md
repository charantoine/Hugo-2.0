# CURSOR INSTRUCTION 1 — Refactor P0 vers un noyau 1.7 piloté par signaux observés

Contexte

Tu interviens sur le backend Hugo P0 existant, sans réécrire toute l’architecture.

Pipeline à conserver tel quel :
1. `build_hugo_context`
2. `analyze_turn_state`
3. `classify_p0_turn_state`
4. `decide_conversation`
5. `derive_next_phase_from_state` / `phase_decider`
6. `build_teaching_plan`
7. `render_tutor_prompt`
8. `call_llm_response`
9. `apply_output_guardrails`

Objectif

Implémenter une évolution P0 1.7 minimale mais robuste, en continuité avec le P0 actuel, pour améliorer :
- la lecture des demandes d’aide explicites ;
- la consommation des signaux de répétition et de clôture ;
- le passage vers récap / bilan / compétences quand la scène est suffisamment mûre ;
- l’alignement entre décision locale backend et forme réelle de sortie ;
- la réduction des réponses qui rouvrent un chantier malgré une bonne décision locale.

Contraintes de conception

- Ne pas remplacer le backend déterministe par un agent autonome.
- Le backend garde la main sur le but régulatoire du tour.
- Le LLM ne doit pas décider seul la posture.
- Toute nouvelle logique 1.7 doit être testable unitairement.
- Tout nouveau nom de variable Python doit être en `snake_case`.
- Si le code courant expose encore des labels historiques non `snake_case`, créer un adaptateur de compatibilité au lieu de propager ces noms dans le nouveau domaine 1.7.
- Ne pas supposer l’existence d’informations externes au repo ou à cette instruction.

Do this

## Étape 1 — Créer les schémas métier 1.7

Créer :
- `backend/apps/hugo/domain/turn_state_v17.py`
- `backend/apps/hugo/domain/conversation_decision_v17.py`

### `TurnStateV17`

Créer un modèle structuré avec 4 sous-blocs :
- `core_signals`
- `derived_signals`
- `conversation_signals`
- `debug_signals`

Le modèle doit au minimum couvrir les champs suivants en `snake_case` :

Core / derived
- `episode_clarity`
- `has_concrete_actions`
- `problem_salience`
- `reflection_phase`
- `affect_valence`
- `cognitive_load`
- `interaction_risk`
- `reflective_depth`
- `evidence_strength`
- `session_phase`
- `session_maturity`
- `need_recap`
- `need_encouragement`
- `can_close_for_now`
- `conversation_goal`

Conversation
- `learner_speech_act`
- `last_learner_act`
- `learner_help_request`
- `requested_output`
- `closure_signal`
- `repetition_signal`
- `covered_points`
- `remaining_open_points`
- `coverage_status`
- `loop_risk`
- `reopen_risk`
- `overquestion_risk`
- `last_tutorial_move`
- `consecutive_clarify_turns`
- `sticky_has_concrete_actions`
- `tech_representation_level`
- `technical_criterion_focus`
- `safety_or_quality_risk_level`

Booleans calculés
- `reflective_minimum_reached`
- `needs_diagnostic_help`
- `needs_reframe`
- `needs_recap`
- `needs_competency_elicitation`
- `recap_eligible`
- `recap_evaluation_eligible`
- `evaluation_eligible`
- `closure_eligible`

Debug
- `debug_signals`
- `source_by_field`
- `override_fields`
- `reason_trace`

Important :
- Ne pas casser les signatures externes tout de suite.
- Ajouter un adaptateur depuis l’ancien `TurnState` vers `TurnStateV17`.
- Ne pas supprimer les anciens champs tant que le pipeline n’a pas été migré.

### `ConversationDecisionV17`

Créer un modèle avec au minimum :

- `primary_intent`
- `pedagogical_move`
- `response_mode`
- `target_question_count`
- `number_of_questions`
- `question_style`
- `question_bundling_allowed`
- `micro_explanation_allowed`
- `should_explain_briefly`
- `should_recap`
- `should_encourage`
- `should_reframe`
- `should_close`
- `should_acknowledge_repetition`
- `should_acknowledge_closure`
- `blocked_question_topics`
- `response_constraints`
- `reason_codes`
- `metadata`
- `effective_max_questions_this_turn`

Enums / valeurs minimales à couvrir :

`primary_intent`
- `diagnostic_help`
- `clarify_scene`
- `surface_problem`
- `deepen_analysis`
- `support_projection`
- `produce_recap`
- `elicit_competencies`
- `close_safely`
- `repair_interaction`

`pedagogical_move`
- `assist`
- `clarify`
- `reformulate`
- `analyze`
- `micro_explain`
- `project`
- `consolidate`
- `recap`
- `evaluation`
- `close`
- `repair`
- `pace`

`response_mode`
- `assist`
- `reflect`
- `recap`
- `evaluation`
- `closure`

Important :
- `response_mode` décrit le type principal de sortie attendu. 
- Les variantes fines éventuelles doivent passer par `metadata` ou `response_constraints`, pas par une deuxième famille concurrente de modes.
- `target_question_count` est la cible décidée backend.
- `number_of_questions` est le nombre effectivement conservé après rendu final et guardrails.
- `number_of_questions` ne doit jamais contredire `target_question_count`.

Précision sémantique sur `response_mode` :
- `assist` = aide diagnostique ou clarification courte, concrète, orientée vers une hypothèse, un repère ou une vérification prioritaire ;
- `reflect` = mode interactif standard hors aide diagnostique forte, utilisé pour faire avancer une élaboration brève sans basculer en récap, évaluation ou clôture ;
- `recap` = mini-bilan ou trace brève orientée apprenant ou formateur selon `metadata` ;
- `evaluation` = mini-récap structuré enrichi, de façon prudente, par les compétences mobilisées ou plausibles ;
- `closure` = réponse de clôture, brève, sans réouverture d’un nouveau chantier.

## Étape 2 — Ajouter le classifieur d’actes de langage

Créer :
- `backend/apps/hugo/services/learner_speech_act_classifier.py`

Fonction cible :
- `classify_learner_speech_act(last_learner_message: str, recent_history: list[str] | None = None) -> LearnerSpeechActResult`

Le classifieur doit détecter au minimum :
- `describe_situation`
- `ask_help_diagnostic`
- `ask_how_to`
- `ask_recap`
- `ask_report_for_tutor`
- `ask_competencies_view`
- `signal_closure`
- `express_confusion`
- `express_tension_or_fatigue`
- `negotiate_next_step`

Ajouter aussi une couche compacte de routage local `last_learner_act` avec au minimum :
- `none`
- `ask_help`
- `ask_priority`
- `ask_recap`
- `ask_report_for_tutor`
- `ask_competencies`
- `signal_repetition`
- `signal_confusion`
- `signal_closure`
- `negotiate_next_step`
- `other`

Important :
- `learner_speech_act` est la catégorisation conversationnelle riche du dernier message apprenant.
- `last_learner_act` est un signal compact de routage local, dérivé du dernier message, utilisé pour simplifier certains arbitrages backend.
- Ces deux champs sont liés mais ne doivent pas être implémentés comme des synonymes stricts.

Règles obligatoires :
- si le message contient une demande explicite du type “tu m’aides à comprendre”, “par quoi commencer”, “quoi vérifier en premier”, ne jamais sortir `learner_help_request = "none"`
- si le message contient une demande explicite de bilan, récap, compétences, évaluation prudente ou texte pour formateur, l’acte de langage doit être prioritaire
- si le message contient un signal de fin ou de déplacement à plus tard, ne pas rouvrir un nouveau chantier

## Étape 3 — Réconcilier l’état

Créer :
- `backend/apps/hugo/services/state_reconciler_v17.py`

Fonction cible :
- `reconcile_turn_state_v17(...) -> TurnStateV17`

Responsabilités :
- fusionner heuristiques existantes, classifieur P0 actuel, classifieur `learner_speech_act`, historique récent ;
- recalculer les booléens dérivés après override ;
- garantir la cohérence suivante :
  - `learner_help_request` doit être cohérent avec `learner_speech_act` et `last_learner_act`
  - `conversation_goal` et `session_phase` ne doivent plus être déterminés uniquement par des heuristiques lexicales globales
  - `recap_evaluation_eligible` doit être un calcul backend explicite

Calcul minimal de `recap_evaluation_eligible` :
true si
- `episode_clarity == "high"`
- et (`has_concrete_actions is True` ou `sticky_has_concrete_actions is True`)
- et `evidence_strength in {"medium", "high"}`
- et `cognitive_load != "high"`
- et `safety_or_quality_risk_level != "high"`

Créer aussi une fonction pure :

```python
def compute_maturity_flags(state: TurnStateV17) -> dict[str, bool]:
    ...
```

Elle doit produire au minimum :
- `reflective_minimum_reached`
- `recap_eligible`
- `recap_evaluation_eligible`
- `evaluation_eligible`
- `closure_eligible`

Règles minimales :
- `reflective_minimum_reached` si faits + cause probable + action future plausible sont présents
- `recap_eligible` si `reflective_minimum_reached` et `cognitive_load != "high"`
- `evaluation_eligible` si `recap_eligible` et contexte compatible
- `closure_eligible` si `reflective_minimum_reached` et faible risque, ou signal explicite de clôture, ou boucle élevée
- Ajouter aussi un booléen dérivé ou une information de suivi équivalente, par exemple : `recap_evaluation_offer_pending`

Règle métier obligatoire :
- dès que `recap_evaluation_eligible` devient `True`, le système doit prévoir de proposer au moins une fois un pivot vers mini-récap, bilan prudent, ou texte pour formateur, sauf si l’apprenant a explicitement refusé, reporté, ou demandé autre chose de prioritaire ;
- cette obligation ne doit pas rester un simple commentaire de prompt : elle doit être visible dans l’état, la décision ou les métadonnées de suivi ;
- si ce pivot a déjà été proposé dans la séquence courante, l’état doit permettre de ne pas le reproposer mécaniquement à chaque tour.
- `recap_evaluation_offer_pending` ne force jamais à lui seul un basculement automatique en `response_mode = "recap"` ou `response_mode = "evaluation"` ; ce signal impose seulement qu’un pivot bref, léger et optionnel soit proposé au moins une fois dans la séquence courante, si aucune demande plus prioritaire ne domine ; si une demande d’aide explicite, un besoin de clarification, un risque sécurité / qualité, une confusion ou une répétition domine le tour, ce pivot doit être différé ; une fois le pivot déjà proposé dans la séquence courante, il ne doit pas être reproposé mécaniquement à chaque tour.

## Étape 4 — Implémenter le pré-routage speech act first

Créer :
- `backend/apps/hugo/services/apply_speech_act_overrides.py`

Fonction cible :
- `apply_speech_act_overrides(state: TurnStateV17) -> dict[str, Any]`

Le résultat doit pouvoir forcer ou suggérer :
- `primary_intent`
- `pedagogical_move`
- `response_mode`
- `target_question_count`
- `number_of_questions`
- `response_constraints`
- `reason_codes`
- `metadata`

Règles obligatoires :

1. Si `learner_speech_act == "ask_report_for_tutor"` ou `last_learner_act == "ask_report_for_tutor"` :
- forcer `primary_intent = "produce_recap"`
- forcer `pedagogical_move = "recap"`
- forcer `response_mode = "recap"`
- `metadata["audience"] = "tutor"`
- `target_question_count = 0`

Important :
- il n’existe pas de `response_mode` séparé pour le formateur ;
- la distinction d’audience passe par `metadata`, par exemple `metadata["audience"] = "tutor"`.

2. Si `learner_speech_act == "ask_recap"` ou `last_learner_act == "ask_recap"` :
- forcer `response_mode = "recap"`
- `target_question_count = 0` par défaut

3. Si `learner_speech_act == "ask_competencies_view"` ou `last_learner_act == "ask_competencies"` :
- si `evidence_strength in {"medium", "high"}` ou `recap_evaluation_eligible is True` :
  - forcer `primary_intent = "elicit_competencies"`
  - forcer `pedagogical_move = "recap"`
  - forcer `response_mode = "evaluation"`
  - `metadata["evaluation_kind"] = "recap_with_competencies"`
  - `target_question_count = 0` par défaut
- sinon :
  - ne pas ouvrir une exploration longue ;
  - produire au plus une formulation prudente indiquant que la scène n’est pas encore assez mûre pour une vue compétences solide ;
  - proposer de consolider d’abord les faits, la cause probable et la règle d’action future.

Important :
- ici, `response_mode = "evaluation"` doit être compris comme un bilan structuré enrichi par les compétences mobilisées ou plausibles, et non comme un verdict autonome ;
- la sortie attendue est d’abord un mini-récap crédible de la scène, puis une mise en mots prudente des compétences, en langage simple ;
- ce mode ne doit pas produire un ton scolaire, un verdict professoral, ni une évaluation autonome dure.

4. Si `learner_speech_act == "signal_closure"` ou `last_learner_act == "signal_closure"` :
- si `closure_eligible is True` ou `can_close_for_now is True`, forcer `primary_intent = "close_safely"` et `response_mode = "closure"` avec `target_question_count = 0`
- si risque sécurité / qualité élevé, autoriser au plus une réponse courte de sécurisation, puis retour à la clôture

5. Si `learner_speech_act == "express_confusion"` ou `last_learner_act == "signal_confusion"` :
- forcer `pedagogical_move in {"repair", "clarify", "assist"}`
- forcer réponse très courte
- `target_question_count <= 1`

6. Si `learner_speech_act == "negotiate_next_step"` ou `last_learner_act == "negotiate_next_step"` :
- ne pas ouvrir de projection lourde
- basculer vers `close_safely` ou consolidation courte

## Étape 5 — Refactor du decision engine

Créer :
- `backend/apps/hugo/services/decision_engine_v17.py`

À faire :
- copier la logique du decision engine actuel ;
- l’enrichir avec les champs 1.7 ;
- conserver un comportement backward-compatible sur les cas non couverts.

Obligations :
- consommer explicitement :
  - `learner_help_request`
  - `learner_speech_act`
  - `last_learner_act`
  - `repetition_signal`
  - `closure_signal`
  - `covered_points`
  - `remaining_open_points`
  - `need_recap`
  - `can_close_for_now`
  - `recap_evaluation_eligible`
  - `safety_or_quality_risk_level`
  -  `evaluation_eligible`
  - `recap_evaluation_offer_pending`

Hiérarchie métier obligatoire dans `decide_conversation_v17` :
1. demande explicite d’aide / récap / compétences / rapport / clôture ;
2. sécurité / qualité ;
3. répétition / risque de boucle ;
4. maturité de couverture ;
5. logique P0 historique en fallback.

Loi proactive obligatoire liée à la maturité :
- si `recap_evaluation_eligible is True`
- et qu’aucune demande explicite plus prioritaire ne domine le tour
- et que le pivot bilan / trace n’a pas encore été proposé dans la séquence courante,
alors `decide_conversation_v17` doit choisir une décision qui propose au moins une fois un pivot bref vers :
- un mini-récap,
- un bilan prudent,
- ou un texte pour formateur si cela devient pertinent.

Cette proposition doit rester légère, non scolaire, non obligatoire, et compatible avec la possibilité pour l’apprenant de refuser ou reporter.

Invariants métier :
- un seul objectif de régulation par tour
- `target_question_count in {0, 1, 2}`
- `number_of_questions in {0, 1, 2}`
- si `response_mode == "closure"`, alors `target_question_count == 0` par défaut
- si `response_mode in {"recap", "evaluation", "closure"}`, alors ne pas choisir `pedagogical_move = "analyze"` sauf exception explicitement justifiée
- si `learner_help_request != "none"`, ne pas faire une clôture sèche immédiate
- si `repetition_signal != "none"`, augmenter `loop_risk` et interdire la re-question sur un point déjà couvert
- `number_of_questions` doit être dérivé de la décision finale et du post-traitement, sans dépasser `target_question_count`

## Étape 6 — Anti-redondance

Créer une fonction pure :

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

Règles :
- empêcher qu’une même question soit reposée sur un point déjà stabilisé ;
- augmenter `loop_risk` si le système insiste malgré couverture suffisante ;
- si `last_learner_act in {"ask_priority", "ask_recap", "ask_competencies", "signal_repetition", "signal_closure"}`, interdire toute question qui change de micro-objectif.

## Étape 7 — Prompt renderer et guardrails

Adapter :
- `prompt_renderer.py`
- `output_guardrails.py`

Sans changer les prompts métiers de fond, injecter :
- `response_mode`
- `target_question_count`
- `number_of_questions`
- `question_style`
- `pedagogical_move`
- `blocked_question_topics`
- interdits de forme

Guardrails obligatoires :
- `assist` : réponse brève, concrète, 0 à 1 question max
- `reflect` : 1 à 2 questions max seulement si elles servent le même micro-objectif
- `recap` : texte continu bref, sans listes, sans checklist, 0 question par défaut
- `evaluation` : texte continu bref, crédible, simple, sans jargon opaque, sans listes, sans checklist, 0 question par défaut ; si `metadata["evaluation_kind"] == "recap_with_competencies"`, produire d’abord un mini-récap de la scène puis une formulation prudente des compétences mobilisées ou plausibles
- `closure` : 2 à 4 phrases, sans question par défaut, sans listes

Règles obligatoires :
- si `target_question_count == 0`, supprimer les questions parasites générées par le LLM
- si `target_question_count == 1`, garder au plus une question
- si `target_question_count == 2`, garder au plus deux questions sur le même micro-objectif
- si `should_acknowledge_repetition is True`, conserver ou injecter une courte reconnaissance au début
- si `should_acknowledge_closure is True`, conserver ou injecter une courte reconnaissance de fin
- si `response_mode in {"recap", "evaluation", "closure"}`, neutraliser tout biais de rendu encore trop interrogatif
- si `response_mode in {"recap", "evaluation", "closure"}`, supprimer les batteries de questions, les listes à puces et les checklists, sauf exception explicitement autorisée dans `response_constraints`

## Étape 8 — Tests d’acceptation

Créer des tests table-driven sans dépendre d’artefacts externes au repo.

Cas obligatoires :
1. demande d’aide explicite :
   - input : “tu m’aides à comprendre ce que je dois vérifier en premier ?”
   - attendu : `learner_help_request != "none"`
   - attendu : `primary_intent = "diagnostic_help"`
   - attendu : pas de checklist multi-étapes

2. demande de priorité :
   - input : “par quoi commencer en priorité ?”
   - attendu : une seule vérification prioritaire
   - attendu : `target_question_count <= 1`

3. signal de répétition :
   - input : “tu me redis la même chose”
   - attendu : `repetition_signal != "none"`
   - attendu : pas de répétition de la même question

4. scène mûre avec cause probable + règle d’action future :
   - attendu : `closure_eligible = True`
   - attendu : `primary_intent in {"produce_recap", "close_safely"}`
   - attendu : pas de réouverture d’exploration

5. demande explicite de récap :
   - attendu : bascule immédiate en mode `recap`
   - attendu : aucune nouvelle exploration avant livraison du récap

6. demande explicite de texte pour formateur :
   - attendu : `response_mode = "recap"`
   - attendu : `metadata["audience"] = "tutor"`

7. demande explicite de compétences :
   - attendu : `response_mode = "evaluation"`
   - attendu : `metadata["evaluation_kind"] = "recap_with_competencies"`
   - attendu : pas de nouvelle exploration avant livraison d’un texte structuré bref
   
8. quand `recap_evaluation_eligible` devient vrai et qu’aucune demande plus prioritaire ne domine :
   - attendu : le système propose au moins une fois un pivot bref vers mini-récap, bilan prudent ou trace
   - attendu : ce pivot n’est pas reproposé mécaniquement à chaque tour s’il a déjà été offert   

Definition of done

Le refactor est accepté si :
- les nouveaux champs sont tous en `snake_case` ;
- le pipeline externe n’est pas cassé ;
- les tests passent ;
- la décision backend pilote réellement la forme de sortie ;
- les demandes explicites d’aide, de bilan, de compétences et de clôture ne sont plus noyées dans une logique générique de description.