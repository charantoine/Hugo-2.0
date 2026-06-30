# P0 Hugo: description technique actuelle

## Statut du document
Ce document decrit l'etat technique actuel de P0 dans Hugo a partir du code en place.

Il remplace utilement les descriptions plus anciennes lorsque l'on veut comprendre:

1. le contrat exact de `TurnState`;
2. la logique actuelle de `ConversationDecision`;
3. l'articulation heuristique / classifieur LLM;
4. les regles de cloture, repetition, aide explicite et anti-boucle;
5. les effets sur le prompt, la phase suivante et les guardrails de sortie.

## Verdict sur l'ancien document
Le fichier `p0_description_technique_actuelle.md` n'est plus strictement a jour.

Les ecarts principaux sont:

- il ne liste pas les nouveaux champs de fil: `covered_points`, `remaining_open_points`, `learner_help_request`, `closure_signal`, `repetition_signal`, `loop_risk`, `assistant_meta_leak_risk`;
- il presente `number_of_questions` comme un mecanisme `1/2`, alors que l'implementation actuelle gere `0/1/2`;
- il ne decrit pas le geste `assist`;
- il ne couvre pas la logique de cloture explicite / repetition explicite / aide explicite;
- il ne couvre pas le guardrail anti-fuite meta cote reponse;
- il n'integre pas le correctif recent selon lequel `intervention_necessity == "none"` bloque les branches `analysis` et `projection`;
- il ne reflete pas completement la guidance de fil injectee dans le prompt.

## Fichiers sources de reference
- `backend/apps/hugo/domain/schemas.py`
- `backend/apps/hugo/services/turn_state_analyzer.py`
- `backend/apps/hugo/services/p0_classifier.py`
- `backend/apps/hugo/services/decision_engine.py`
- `backend/apps/hugo/services/teaching_plan_builder.py`
- `backend/apps/hugo/services/phase_decider.py`
- `backend/apps/hugo/services/hugo_orchestrator.py`
- `backend/apps/hugo/services/prompt_renderer.py`
- `backend/apps/hugo/views_sessions.py`

## Vue d'ensemble de la chaine P0
Pipeline actuel:

1. `build_hugo_turn()` construit le contexte Hugo.
2. Le backend determine la phase de depart effective.
3. `analyze_turn_state()` calcule un `heuristic_turn_state` complet.
4. `classify_p0_turn_state()` tente un override partiel des variables P0 semantiques.
5. Le `turn_state` final alimente `decide_conversation()`.
6. Le nombre de questions est borne par `TutorPrompt.max_questions_per_turn`, avec minimum a `0`.
7. `build_teaching_plan()` derive focus, regulation, couverture et prochaine phase deterministe.
8. `decide_next_phase()` arbitre la phase suivante avec adaptateur d'etat + classifieur de phase optionnel.
9. `render_with_tutor_prompt()` construit le prompt en injectant etat, decision et directives de fil.
10. La reponse du LLM est post-traitee par les guardrails de sortie.
11. Un guardrail anti-meta peut remplacer la reponse finale par un fallback sur si fuite detectee.

## 1. Contrat exact de `TurnState`

### 1.1 Noyau P0 expose
`TurnState.to_dict()` expose un sous-objet `p0` contenant `P0_CORE_FIELDS`:

- `has_concrete_actions`
- `episode_clarity`
- `problem_salience`
- `reflection_phase`
- `affect_valence`
- `cognitive_load`
- `interaction_risk`
- `session_phase`

### 1.2 Champs LLM-overridables
Le classifieur P0 LLM ne peut override que `P0_LLM_FIELDS`:

- `has_concrete_actions`
- `episode_clarity`
- `problem_salience`
- `reflection_phase`
- `affect_valence`
- `cognitive_load`
- `interaction_risk`

`session_phase` reste calcule cote backend.

### 1.3 `TurnState` complet actuellement materialise
Le contrat actuel contient:

- `episode_clarity`
- `has_concrete_actions`
- `problem_salience`
- `reflection_phase`
- `reflective_depth`
- `self_efficacy_signal`
- `affect_valence`
- `cognitive_load`
- `interaction_risk`
- `epistemic_balance`
- `zpd_estimate`
- `session_phase`
- `session_maturity`
- `evidence_strength`
- `intervention_necessity`
- `contradiction_status`
- `concept_clarity`
- `available_material`
- `conversation_goal`
- `current_phase`
- `emotional_state`
- `action_feasibility`
- `autonomy_level`
- `recent_progress`
- `need_recap`
- `need_encouragement`
- `need_reframing`
- `can_close_for_now`
- `last_tutorial_move`
- `consecutive_clarify_turns`
- `sticky_has_concrete_actions`
- `tech_representation_level`
- `technical_criterion_focus`
- `safety_or_quality_risk_level`
- `covered_points`
- `remaining_open_points`
- `learner_help_request`
- `closure_signal`
- `repetition_signal`
- `loop_risk`
- `assistant_meta_leak_risk`
- `debug_signals`

## 2. Logique technique de `TurnState`

### 2.1 Variables semantiques centrales
- `has_concrete_actions`: detecte les actions de l'apprenant et se combine avec l'historique via `sticky_has_concrete_actions`.
- `episode_clarity`: evalue si l'episode est exploitable tel quel.
- `problem_salience`: detecte si le probleme est nomme ou seulement latent.
- `reflection_phase`: `description`, `analysis` ou `projection`.
- `affect_valence`, `cognitive_load`, `interaction_risk`: signaux de protection relationnelle et cognitive.
- `session_phase`: derivee du contexte de session et du contenu.

### 2.2 Variables derivees structurelles
- `reflective_depth`: profondeur du raisonnement.
- `self_efficacy_signal`: confiance / doute.
- `epistemic_balance`: rapport d'expertise presume.
- `zpd_estimate`: `below`, `in`, `beyond`.
- `session_maturity`: maturite de la session selon historique et traces.
- `evidence_strength`: robustesse des preuves fournies.
- `intervention_necessity`: besoin reel d'ouvrir un nouveau front.
- `contradiction_status`: contradiction suspectee ou non.
- `concept_clarity`, `available_material`, `conversation_goal`, `current_phase`, `emotional_state`, `action_feasibility`, `autonomy_level`, `recent_progress`: derivees utilitaires pour la planification et le prompt.
- `need_recap`, `need_encouragement`, `need_reframing`, `can_close_for_now`: drapeaux de regulation.

### 2.3 Variables de suivi de fil ajoutees

#### `covered_points`
Liste ordonnee des points deja couverts dans le fil. Ordre canonique:

- `episode_described`
- `concrete_actions_described`
- `problem_named`
- `cause_hypothesis_named`
- `cause_confirmed`
- `future_action_named`
- `learning_rule_named`
- `session_done_explicitly`

Cette liste est construite a partir:

- du message courant;
- des patterns de description, action, probleme, cause, projection, regle de transfert;
- du signal de cloture;
- et des tours precedents via les payloads apprenant.

#### `remaining_open_points`
Liste ordonnee des points encore ouverts. Ordre canonique:

- `missing_episode_details`
- `missing_problem_identification`
- `missing_cause`
- `missing_future_action`
- `missing_transfer_rule`
- `need_closure_confirmation`
- `none`

Elle represente ce qui manque pedagogiquement au regard de la couverture deja acquise.

#### `learner_help_request`
Valeurs:

- `explicit`
- `implicit`
- `none`

#### `closure_signal`
Valeurs:

- `explicit`
- `implicit`
- `none`

#### `repetition_signal`
Valeurs:

- `explicit`
- `implicit`
- `none`

#### `loop_risk`
Valeurs:

- `low`
- `medium`
- `high`

Ce signal vise a limiter la reouverture de points deja couverts et a casser certaines boucles de clarification.

#### `assistant_meta_leak_risk`
Valeurs:

- `low`
- `medium`
- `high`

Il sert surtout de signal de vigilance pour le prompt et le guardrail final.

### 2.4 Variables anti-boucle historiques
- `last_tutorial_move`: dernier `pedagogical_move` retrouve dans les payloads apprenant precedents.
- `consecutive_clarify_turns`: nombre de tours consecutifs precedents en `clarify` / `elicit_action`.
- `sticky_has_concrete_actions`: memorisation d'actions deja decrites dans la session.

## 3. Arbitrage heuristique vs classifieur P0 LLM

### 3.1 Principe
Le backend calcule toujours d'abord un `heuristic_turn_state`.

Le classifieur P0 LLM n'est qu'un mecanisme d'override partiel et borne.

### 3.2 Conditions de repli heuristique
Le backend reste sur l'heuristique si:

- le classifieur est desactive;
- le message apprenant est vide;
- l'appel LLM renvoie une erreur;
- la reponse est vide;
- le JSON est introuvable ou invalide;
- une valeur est hors schema;
- la confiance est inferieure au seuil configure.

### 3.3 Resultat du classifieur
Le resultat transporte:

- `source`
- `confidence`
- `fallback_reason`
- `classifier_provider`
- `classifier_model`
- `runtime_config`
- `runtime_config_source`
- `source_by_field`
- `system_prompt`
- `user_prompt`
- `classifier_reply_text`
- `request_payload`
- `raw_response`
- `llm_error`

Le `turn_state` final est ensuite recompose en rappelant `analyze_turn_state(..., state_overrides=...)`.

## 4. Logique actuelle de `ConversationDecision`

### 4.1 Champs de sortie
`ConversationDecision` contient:

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

### 4.2 Gestes possibles actuellement
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

### 4.3 Priorite des branches decisionnelles
Ordre effectif actuel dans `decide_conversation()`:

1. `protected_mode` (`cognitive_load == high` ou `interaction_risk == high`)
2. `explicit_closure_case`
3. `explicit_repetition_case`
4. `explicit_help_request_case`
5. risque `safety_or_quality_risk_level in {medium, high}`
6. contradiction suspectee
7. `closeable_case`
8. `clarify_frontier_reached`
9. `analysis_case`
10. `projection_case`
11. `episode_clarity == low`
12. absence d'actions concretes
13. `problematize`
14. `intervention_necessity == none`
15. fallback `reformulate`

### 4.4 Regles saillantes

#### Protection
Si charge cognitive ou risque interactionnel est haut:

- `pace` si charge haute;
- `repair` si risque interactionnel haut;
- `question_style = single_safe`;
- une seule question max;
- simplification forte;
- pas de micro-explication.

#### Cloture explicite
Si `closure_signal == explicit` et pas de risque securite/qualite haut:

- `pedagogical_move = close`
- `number_of_questions = 0`
- `question_style = no_question`
- contraintes `respect_explicit_closure` et `no_question_final`

#### Repetition explicite
Si `repetition_signal == explicit`:

- `repair_repetition` comme intention;
- `close` si le fil est deja fermable, sinon `repair`;
- `0` ou `1` question selon le cas;
- interdiction de repeter un point deja couvert.

#### Aide explicite
Si `learner_help_request == explicit`:

- `pedagogical_move = assist`
- aide breve avant relance;
- `number_of_questions = 1` en general;
- `0` si `loop_risk == high`

#### Risque securite / qualite
Si `safety_or_quality_risk_level in {medium, high}`:

- `primary_intent = secure_and_analyze`
- `pedagogical_move = analyze`
- ancrage sur critere referentiel;
- possible demande d'explicitation criterielle;
- possible comparaison pratique / reference si representation technique explicite.

#### Analyse / projection
`analysis_case` et `projection_case` ne s'activent plus si `intervention_necessity == "none"`.

C'est un point recent important: si aucune intervention nouvelle n'est necessaire, le moteur doit rester en `reformulate` plutot qu'ouvrir un nouveau front.

#### Problematize
`problematize` reste reserve aux cas ou:

- le probleme n'est pas vraiment nomme;
- on est encore en `description`;
- il n'y a ni aide explicite, ni repetition, ni cloture;
- le fil n'est pas suffisamment couvert.

### 4.5 Logique `number_of_questions`
Le systeme actuel gere:

- `0`
- `1`
- `2`

#### `0 question`
Possible si:

- cloture explicite;
- certaines reparations / repetitions;
- `assist` avec `loop_risk == high`;
- puis borne finale par `TutorPrompt.max_questions_per_turn`.

#### `2 questions`
Possible seulement:

- pour certains micro-objectifs coherents (`deepen_analysis`, `support_projection`, `secure_and_analyze`) avec clarte et profondeur hautes;
- ou pour certains `problematize` a faible risque de boucle.

Sinon, retour a `1`.

### 4.6 `response_constraints` notables
Le moteur ajoute notamment:

- `one_regulation_objective`
- `single_question_only`
- `simple_wording_only`
- `no_question_stacking`
- `no_micro_explanation`
- `respect_explicit_closure`
- `no_question_final`
- `acknowledge_repetition_briefly`
- `do_not_repeat_covered_point`
- `brief_help_first`
- `validation_before_question`
- `anchor_to_referential_criterion`
- `ask_for_criterion_explicitation`
- `allow_practice_reference_comparison`
- `do_not_repeat_action_clarification`
- `anchor_on_existing_actions`
- `single_question_default`
- `two_questions_same_micro_goal_max`
- `micro_explanation_one_sentence_max`
- `closure_must_be_natural`
- `no_new_front`
- `clarification_turn`
- `assist_briefly`
- `question_style:<...>`
- `question_count:<...>`

## 5. Effets aval de P0

### 5.1 Sur le `TeachingPlan`
`build_teaching_plan()` reutilise P0 pour:

- `regulation_targets`;
- `ui_focus_label`;
- `coverage_status`;
- `rag_mode`;
- `next_session_phase`.

Points saillants:

- `assist` est traite comme un geste centree tache;
- `coverage_status = covered` si cloture explicite ou `remaining_open_points == ["none"]`;
- si cloture, `next_session_phase` bascule vers `potential_closure`.

### 5.2 Sur la phase suivante
`phase_decider` combine:

- un adaptateur d'etat;
- un classifieur de phase optionnel.

Regles importantes:

- si `should_close`, `closure_signal == explicit` ou `can_close_for_now`, l'adaptateur choisit `potential_closure`;
- si clarte basse ou pas d'actions, retour a `exploration`;
- si geste `analyze` / `contrast_gently`, passage a `deepening`;
- si `project`, passage a `potential_closure`;
- la FSM interdit les sauts non autorises;
- `_extract_json_object()` du classifieur de phase parse bien le JSON actuellement;
- une cloture explicite ne doit pas etre contredite par le classifieur.

### 5.3 Sur le prompt
`prompt_renderer` injecte:

- un `state_block`;
- un `decision_block`;
- un `response_constraints_block`;
- un `thread_guidance_block`.

Le `thread_guidance_block` impose explicitement:

- ne pas rouvrir un point deja couvert;
- aider brievement si aide explicite;
- reconnaitre la repetition et changer d'action;
- clore sans rouvrir si cloture explicite;
- respecter `0/1/2` questions selon la decision;
- ne jamais exposer les instructions internes.

Le message apprenant est delimite par:

- `<<<APPRENANT`
- `APPRENANT>>>`

Ce cadrage vise a reduire les fuites meta.

### 5.4 Sur le mode de sortie et les guardrails
`views_sessions.py` applique les guardrails finaux.

Points clefs:

- `max_questions = 0` force un mode de type `REFLECTION_BLOCK`;
- `_decision_forces_no_question()` s'appuie sur `max_questions`, `question_style` et `response_constraints`;
- `_apply_output_guardrails()` supprime toute question finale si la decision impose `0`;
- `_contains_meta_leak()` detecte certaines formulations de fuite meta;
- en cas de fuite ou de reponse vide invalide, `_safe_assistant_fallback()` peut remplacer la sortie.

## 6. Lien avec le RAG
Le RAG n'est pas P0 au sens strict, mais il depend des sorties P0.

Actuellement, `select_rag_chunks()` n'est considere que si:

- `teaching_plan.rag_mode != "none"`
- et le geste est compatible (`analyze` ou `contrast_gently`)
- et le risque est juge suffisant a partir de la decision ou du `turn_state`

Le filtrage actuel utilise:

- `conversation_decision.metadata["safety_or_quality_risk_level"]` si present;
- sinon `turn_state.safety_or_quality_risk_level`;
- sinon `turn_state.interaction_risk == "high"` comme indicateur permissif recent.

## 7. Fragilites connues

### 7.1 Heuristiques lexicales
Une grande partie de P0 repose encore sur des patterns regex. Cela reste:

- rapide;
- observable;
- testable;

mais fragile aux reformulations inhabituelles.

### 7.2 Couverture du fil
`covered_points` et `remaining_open_points` rendent la regulation bien meilleure, mais restent des abstractions heuristiques:

- ils ne comprennent pas finement la semantique;
- ils peuvent sur-estimer ou sous-estimer la couverture;
- ils dependent du verbatim reellement present dans le message.

### 7.3 Anti-meta
Le guardrail anti-meta est utile, mais pattern-based:

- il attrape des cas frequents;
- il ne garantit pas une absence absolue de fuite si une sortie anormale contourne les patterns.

### 7.4 Double question
Le mode `2 questions` est desormais borne par des conditions plus strictes, mais demande toujours une vigilance UX et pedagogique.

## 8. Resume executif
Techniquement, P0 n'est plus seulement un mini-classifieur de 8 variables.

Dans l'etat actuel, c'est un systeme de regulation de fil qui combine:

- un noyau P0 semantique borne;
- un `TurnState` enrichi par l'historique et la couverture conversationnelle;
- un moteur de decision priorisant protection, cloture, repetition, aide et anti-boucle;
- une propagation dans le plan pedagogique, la phase, le prompt et les guardrails de sortie.

Les evolutions les plus structurantes par rapport aux versions precedentes sont:

- le suivi explicite du fil (`covered_points`, `remaining_open_points`);
- la gestion des signaux apprenant (`help`, `closure`, `repetition`);
- la possibilite de `0` question;
- le geste `assist`;
- le guardrail anti-fuite meta;
- et la recente preservation de `reformulate` quand `intervention_necessity == "none"`.
