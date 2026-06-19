# P0 Hugo: description technique actuelle

## Portee du document
Ce document decrit l'etat actuel de l'implementation P0 dans Hugo, tel qu'il est code aujourd'hui.

Il couvre:

1. la liste exhaustive des variables reellement calculees et consommees;
2. leur type, leurs valeurs possibles, leur source, leur regle de calcul et leur effet;
3. l'arbitrage heuristique vs classifieur LLM;
4. la logique de `conversation_decision`;
5. les regles exactes sur `number_of_questions`, changement de phase et cloture;
6. deux exemples complets anonymises;
7. les points fragiles ou provisoires connus.

## Fichiers principaux concernes
- `backend/apps/hugo/domain/schemas.py`
- `backend/apps/hugo/services/turn_state_analyzer.py`
- `backend/apps/hugo/services/p0_classifier.py`
- `backend/apps/hugo/services/decision_engine.py`
- `backend/apps/hugo/services/teaching_plan_builder.py`
- `backend/apps/hugo/services/phase_decider.py`
- `backend/apps/hugo/services/hugo_orchestrator.py`
- `backend/apps/hugo/views_sessions.py`
- `backend/apps/hugo/services/prompt_renderer.py`

## Vue d'ensemble de la chaine

### Pipeline reel
1. Le backend construit un `HugoContext`.
2. Il determine la phase effective de depart.
3. Il calcule un `heuristic_turn_state` via `analyze_turn_state()`.
4. Il tente un surclassement partiel via `classify_p0_turn_state()`.
5. Il obtient un `turn_state` final.
6. Il derive une `conversation_decision` via `decide_conversation()`.
7. Il borne `number_of_questions` par `TutorPrompt.max_questions_per_turn`.
8. Il construit un `TeachingPlan`.
9. Il derive une phase suivante via `decide_next_phase()`.
10. Il rend le prompt final.
11. Le LLM repond.
12. Les guardrails de sortie transforment eventuellement la reponse LLM en `final_response`.

### Point important
P0 n'est pas seulement le noyau minimal de 8 champs.

En implementation, le backend produit un objet `TurnState` beaucoup plus large. C'est cet objet complet qui est effectivement reutilise:

- par le moteur de decision;
- par la gestion de phase;
- par le teaching plan;
- par le prompt renderer;
- par le tracing/debug.

## 1. Variables reellement utilisees

## 1.1 Noyau P0 minimal
Le noyau minimal expose comme `P0_CORE_FIELDS` est:

- `has_concrete_actions`
- `episode_clarity`
- `problem_salience`
- `reflection_phase`
- `affect_valence`
- `cognitive_load`
- `interaction_risk`
- `session_phase`

Le classifieur LLM ne peut surclasser directement que:

- `has_concrete_actions`
- `episode_clarity`
- `problem_salience`
- `reflection_phase`
- `affect_valence`
- `cognitive_load`
- `interaction_risk`

`session_phase` fait partie du noyau P0 expose, mais n'est pas produit par le classifieur LLM dans l'etat actuel.

## 1.2 Variables calculees dans `TurnState`
Voici la liste exhaustive des champs du `TurnState` actuellement materialises:

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
- `debug_signals`

## 1.3 Variables de sortie de decision reellement utilisees
Le backend calcule ensuite une `ConversationDecision` avec les champs suivants:

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

Ces variables influencent:

- le `TeachingPlan`;
- le prompt effectif;
- le mode de sortie;
- le nombre de questions reellement conservees;
- la phase suivante.

## 2. Description exhaustive des variables de `TurnState`

## 2.1 Variables du noyau P0

| Variable | Type | Valeurs possibles | Source | Regle de calcul actuelle | Effet reel |
|---|---|---|---|---|---|
| `has_concrete_actions` | `bool` | `true`, `false` | Heuristique, avec override LLM possible | `true` si le message correspond a des patterns d'action (`j'ai`, `je fais`, `je verifie`, `je branche`, etc.). Ensuite combine avec l'historique via `sticky_session_actions`: `has_concrete_actions = raw_has_concrete_actions or sticky_session_actions`. | Si `false`, pousse vers `elicit_action` ou `exploration`; si `true`, aide a sortir de la clarification et a autoriser 2 questions en `problematize`. |
| `episode_clarity` | `str` | `low`, `medium`, `high` | Heuristique, override LLM possible | `high` si actions concretes + au moins 2 marqueurs de contexte + >= 20 mots. `medium` si actions concretes, ou >= 1 marqueur, ou >= 12 mots. Sinon `low`. | `low` pousse vers `clarify`, `exploration`, `need_reframing`; `medium/high` autorise des gestes plus analytiques. |
| `problem_salience` | `str` | `none`, `low`, `high` | Heuristique, override LLM possible | `high` si patterns `probleme`, `incident`, `panne`, `erreur`, `danger`, etc. `low` si `pas simple`, `hesite`, etc. Sinon `none`. | `none + description` pousse vers `problematize`; `high` peut renforcer une logique d'intervention forte. |
| `reflection_phase` | `str` | `description`, `analysis`, `projection` | Heuristique, override LLM possible | `projection` si patterns `je vais`, `prochaine fois`, `plan d'action`. Sinon `analysis` si `parce que`, `cause`, `raison`, `j'ai choisi`, etc. Sinon `description`. | Oriente le geste (`analyze`, `project`) et la phase (`deepening`, `potential_closure`). |
| `affect_valence` | `str` | `negative`, `neutral`, `positive` | Heuristique, override LLM possible | Patterns emotionnels negatifs ou positifs; sinon `neutral`. | Contribue a `need_encouragement`, influence le ton dans le prompt. |
| `cognitive_load` | `str` | `low`, `medium`, `high` | Heuristique, override LLM possible | `high` si `perdu`, `sature`, `trop d'infos`, `je m'embrouille`. `medium` si `complique`, `beaucoup de choses`, etc. Sinon `low`. | Si `high`, priorite a la protection: 1 question max, `single_safe`, pas d'empilement, pas de micro-explication. |
| `interaction_risk` | `str` | `low`, `medium`, `high` | Heuristique, override LLM possible | `high` si `j'en ai marre`, `laisse tomber`, `ca m'enerve`. `medium` si `bof`, `pas envie`, `je sais pas trop`. Sinon `low`. | Si `high`, priorite a la protection: 1 question max, `repair`, simplification forte. |
| `session_phase` | `str` | `opening`, `exploration`, `deepening`, `potential_closure` | Heuristique backend uniquement dans l'etat actuel | Calcule a partir de `base_phase`, `reflection_phase`, `evidence_strength`. Si `base_phase=opening` => `opening`; si `base_phase=potential_closure` => `potential_closure`; si `analysis` => `deepening`; si `projection` + `evidence_strength in {medium, high}` => `potential_closure`; sinon `exploration`. | Reutilise pour le teaching plan, le prompt, le choix du mode de sortie, la phase suivante. |

## 2.2 Variables derivees de `TurnState`

| Variable | Type | Valeurs possibles | Source | Regle de calcul actuelle | Effet reel |
|---|---|---|---|---|---|
| `reflective_depth` | `str` | `low`, `medium`, `high` | Heuristique derivee | `high` si `reflection_phase=analysis` et >= 2 indices d'analyse. `medium` si phase `analysis` ou `projection` ou >= 1 indice. Sinon `low`. | Permet `number_of_questions=2` dans certains cas; alimente `concept_clarity`; influence micro-explication. |
| `self_efficacy_signal` | `str` | `low`, `neutral`, `high` | Heuristique derivee | Patterns de doute ou de maitrise. | `low` peut activer `reassure` et `need_encouragement`; influence `autonomy_level`. |
| `epistemic_balance` | `str` | `learner_more_expert`, `tutor_more_expert`, `balanced` | Heuristique derivee | `learner_more_expert` si patterns d'experience; `tutor_more_expert` si patterns de debutant; sinon `balanced`. | Freine les micro-explications quand l'apprenant est suppose plus expert. |
| `zpd_estimate` | `str` | `below`, `in`, `beyond` | Heuristique derivee | `below` si `facile`, `simple`; `beyond` si `trop dur`, `impossible` ou `cognitive_load=high`; sinon `in`. | Conditionne `should_explain_briefly`; influence `action_feasibility`. |
| `session_maturity` | `str` | `low`, `medium`, `high` | Historique session + traces | `high` si `message_count >= 8` ou `recent_traces >= 3`; `medium` si `message_count >= 4` ou `recent_traces >= 1`; sinon `low`. | Contribue a `need_recap`, `can_close_for_now`. |
| `evidence_strength` | `str` | `low`, `medium`, `high` | Heuristique derivee | `high` si `episode_clarity=high` + actions concretes + phase `analysis` ou `projection`; `medium` si clarte `medium/high` + actions concretes; sinon `low`. | Sert pour phase, cloture, couverture, recap. |
| `intervention_necessity` | `str` | `none`, `low`, `high` | Heuristique derivee | `high` si clarte basse, pas d'actions, `problem_salience=high`, `cognitive_load=high` ou `interaction_risk=high`. `low` si probleme faible ou profondeur faible. Sinon `none`. | Si `none`, pousse vers `reformulate` plutot que rouvrir un nouveau front. |
| `contradiction_status` | `str` | `none`, `suspected` | Heuristique derivee | `suspected` si patterns `en fait`, `finalement`, `au debut... puis...`. | Peut declencher `contrast_gently`. |
| `concept_clarity` | `str` | `low`, `medium`, `high` | Derive de `reflective_depth` | `high` si profondeur haute; `medium` si phase `analysis`; sinon `low`. | Utilise dans `TeachingPlan.current_level`. |
| `available_material` | `str` | `low`, `medium`, `high` | Contexte | Score +1 si `learner_summary`, +1 si traces recentes, +1 si documents de classe. `high` si score >= 3; `medium` si score >= 1; sinon `low`. | Sert au metadata de decision, au `rag_mode`, a l'interpretation du contexte. |
| `conversation_goal` | `str` | `clarify_episode`, `elicit_concrete_action`, `close_or_project`, `deepen_analysis`, `structure_description` | Derive backend | Si clarte basse => `clarify_episode`; si pas d'actions => `elicit_concrete_action`; si `session_phase=potential_closure` => `close_or_project`; si `reflection_phase=analysis` => `deepen_analysis`; sinon `structure_description`. | Injecte dans le prompt et dans les metadata de decision. |
| `current_phase` | `str` | Meme ensemble que `session_phase` | Copie derivee | `current_phase = session_phase`. | Expose tel quel dans le prompt renderer et les metadata. |
| `emotional_state` | `str` | `negative`, `neutral`, `positive` | Copie derivee | `emotional_state = affect_valence`. | Injecte dans le prompt via `turn_state`, pas consomme directement par `decision_engine`. |
| `action_feasibility` | `str` | `low`, `medium`, `high` | Derive backend | `low` si charge haute ou `zpd=beyond`; `high` si actions concretes + efficacite haute; sinon `medium`. | Injecte dans `turn_state`; pas lu directement par `decision_engine`. |
| `autonomy_level` | `str` | `low`, `medium`, `high` | Derive backend | `high` si efficacite haute et non `tutor_more_expert`; `low` si efficacite basse; sinon `medium`. | Injecte dans `turn_state`; pas lu directement par `decision_engine`. |
| `recent_progress` | `str` | `improving`, `stalled`, `steady`, `unclear` | Message + resume + traces | Priorite au contenu du message (`j'ai progresse`, `je bloque`, etc.), sinon resume/traces. | Injecte dans `turn_state`; pas lu directement par `decision_engine`. |
| `need_recap` | `bool` | `true`, `false` | Derive backend | `true` si `session_maturity=high` et `evidence_strength in {medium, high}`, ou si `reflection_phase=projection` et `evidence_strength=high`. | Devient `should_recap` si charge cognitive non haute. |
| `need_encouragement` | `bool` | `true`, `false` | Derive backend | `true` si efficacite basse ou valence negative. | Peut activer `reassure`; devient `should_encourage`. |
| `need_reframing` | `bool` | `true`, `false` | Derive backend | `true` si clarte basse ou si pas de probleme formule en phase `description`. | Devient `should_reframe`, influence aussi la repartition des regulation targets. |
| `can_close_for_now` | `bool` | `true`, `false` | Derive backend | `true` si `session_phase=potential_closure` ET `session_maturity=high` ET `evidence_strength=high` ET `interaction_risk=low` ET `cognitive_load != high`. | Peut declencher `close`, force la phase `potential_closure`. |
| `last_tutorial_move` | `str` | tout geste precedemment stocke, ou `""` | Historique session | Recupere depuis les `llm_request_payload` precedents. Premier `pedagogical_move` non vide trouve en remontant l'historique. | Sert a la logique anti-boucle (`clarify_frontier_reached`). |
| `consecutive_clarify_turns` | `int` | entier >= 0 | Historique session | Compte les tours consecutifs precedents dont le `pedagogical_move` est dans `{"clarify", "elicit_action"}`. | Si >= 1 avec clarte suffisante et actions concretes, pousse a sortir de la boucle de clarification. |
| `sticky_has_concrete_actions` | `bool` | `true`, `false` | Historique + message courant | `has_concrete_actions and (sticky_session_actions or raw_has_concrete_actions)`. | Memorisent des actions deja acquises, meme si le dernier message est plus elliptique. |
| `tech_representation_level` | `str` | `implicit`, `partial`, `explicit` | Heuristique technique | `explicit` si >= 2 hits techniques et >= 1 hit critere technique; `partial` si >= 1 hit technique; sinon `implicit`. | Visible dans metadata et prompt; peut ajouter `allow_practice_reference_comparison` pour l'analyse. |
| `technical_criterion_focus` | `str` | `none`, `implicit`, `explicit` | Heuristique + contexte referentiel | `explicit` si patterns critere/norme/C1.1/BC01/T1-1. Sinon `implicit` si tokens d'un critere cible apparaissent dans le message. Sinon `none`. | Si `none` avec risque securite/qualite moyen/haut, ajoute `ask_for_criterion_explicitation`. |
| `safety_or_quality_risk_level` | `str` | `low`, `medium`, `high` | Heuristique securite/qualite | `high` si `disjoncte`, `court-circuit`, `electrocution`, `pas de terre`, etc. `medium` si `securite`, `risque`, `protection`, `disjoncteur`, etc. Sinon `low`. | Pousse vers `secure_and_analyze`, peut activer un ancrage criteriel et le RAG borne. |
| `debug_signals` | `dict` | dictionnaire libre | Backend debug | Contient `base_phase`, `message_count`, `recent_traces_count`, `override_fields` et divers signaux. | Pas d'effet direct sur la decision; utile pour tracing et diagnostic. |

## 3. Variables de `ConversationDecision`

| Variable | Type | Valeurs / format | Source | Regle de calcul actuelle | Effet reel |
|---|---|---|---|---|---|
| `primary_intent` | `str` | ex. `clarify_episode`, `secure_and_analyze`, `support_projection` | `decision_engine` | Choisi par cascade de `if/elif` sur le `TurnState`. | Oriente la lecture pedagogique du tour, metadata et some rules de double question. |
| `pedagogical_move` | `str` | `clarify`, `elicit_action`, `problematize`, `analyze`, `contrast_gently`, `project`, `reassure`, `reformulate`, `repair`, `pace`, `close` | `decision_engine` | Derive du contexte de risque, de clarte, de phase reflexive, etc. | Variable la plus structurante pour la suite: prompt, regulation targets, phase adapter, RAG, UI focus label. |
| `number_of_questions` | `int` | `1` ou `2` actuellement | `decision_engine` | Voir section dediee plus bas. | Borne ensuite par `TutorPrompt.max_questions_per_turn`, puis re-filtre par les output guardrails. |
| `question_style` | `str` | `simple_open`, `single_safe`, `double_same_goal` | `decision_engine` | Defini selon le niveau de protection et le nombre de questions. | Peut forcer le mode `single_question`; conditionne la contraction `safe`. |
| `should_explain_briefly` | `bool` | `true`, `false` | `decision_engine` | `true` si ZPD `in`, profondeur `medium/high`, balance non `learner_more_expert`, charge et risque non hauts. | Autorise une micro-explication d'une phrase max dans le prompt. |
| `should_recap` | `bool` | `true`, `false` | `decision_engine` | `state.need_recap and state.cognitive_load != "high"`. | Pousse le prompt vers un recap. |
| `should_encourage` | `bool` | `true`, `false` | `decision_engine` | Copie de `state.need_encouragement`. | Pousse le prompt vers validation/encouragement. |
| `should_reframe` | `bool` | `true`, `false` | `decision_engine` | `state.need_reframing` sauf si move `repair` ou `pace`. | Pousse le prompt vers recadrage doux. |
| `should_close` | `bool` | `true`, `false` | `decision_engine` | `state.can_close_for_now and pedagogical_move == "close"`. | Force la phase `potential_closure` dans l'adapter de phase. |
| `response_constraints` | `list[str]` | liste | `decision_engine` | Enrichie tout au long de la decision. | Reutilisee dans le prompt et par les output guardrails. |
| `reason_codes` | `list[str]` | liste | `decision_engine` | Journalisation explicite des motifs. | Diagnostic et tracing. |
| `metadata` | `dict` | dictionnaire | `decision_engine` | Resume des principaux signaux. | Debug, tracing, UI, audit. |

## 4. Arbitrage heuristique vs classifieur LLM

## 4.1 Ce que fait l'heuristique
`analyze_turn_state()` calcule d'abord un `TurnState` complet a partir:

- du message apprenant;
- de la phase courante ou demandee;
- du contexte (`ctx`);
- de l'historique recent (`llm_request_payload` des tours precedents);
- de quelques signaux de traces et de documents.

Ce calcul heuristique est toujours fait en premier.

## 4.2 Ce que fait le classifieur LLM P0
`classify_p0_turn_state()` peut ensuite demander a un LLM un JSON strict contenant:

- `confidence`
- `episode_clarity`
- `has_concrete_actions`
- `problem_salience`
- `reflection_phase`
- `affect_valence`
- `cognitive_load`
- `interaction_risk`

Le LLM ne produit donc pas le `TurnState` complet.

Il ne fournit qu'un override partiel de 7 champs.

## 4.3 Regle exacte d'arbitrage
La logique actuelle est:

1. Calculer `heuristic_turn_state`.
2. Si `p0_classifier_enabled = false`:
   retourner l'heuristique.
3. Si le message apprenant est vide:
   retourner l'heuristique.
4. Appeler le LLM classifieur.
5. Si erreur provider:
   retourner l'heuristique.
6. Si reponse vide:
   retourner l'heuristique.
7. Si JSON introuvable ou invalide:
   retourner l'heuristique.
8. Si une valeur est hors schema:
   retourner l'heuristique.
9. Si `confidence < p0_classifier_min_confidence`:
   retourner l'heuristique.
10. Sinon:
   recalculer `TurnState` avec `state_overrides=normalized_payload`.

Donc:

- l'heuristique est la base;
- le LLM ne remplace jamais toute la logique;
- le LLM ne surclasse que certains champs;
- tout le reste reste derive par backend a partir de ces overrides.

## 4.4 Cascade de configuration runtime
Pour le classifieur P0, la resolution des parametres se fait par cascade:

1. niveau session;
2. sinon niveau groupe;
3. sinon settings.

Parametres:

- `p0_classifier_enabled`
- `p0_classifier_max_tokens`
- `p0_classifier_min_confidence`
- `p0_classifier_max_input_chars`

Presets references:

- `safe`
- `balanced`
- `aggressive`

## 4.5 Effet concret d'un override LLM
Si le classifieur LLM modifie par exemple:

- `reflection_phase = analysis`
- `episode_clarity = high`

alors les champs derives suivants peuvent changer indirectement lors du recalcul:

- `reflective_depth`
- `evidence_strength`
- `session_phase`
- `conversation_goal`
- `need_reframing`
- `can_close_for_now`
- etc.

Autrement dit:

- le LLM ne remplace pas uniquement 7 champs;
- il peut modifier en cascade le comportement global.

## 5. Pseudo-code de `conversation_decision`

## 5.1 Arbre de decision simplifie
```text
Entrée: TurnState state

Initialiser:
  primary_intent = maintain_progress
  pedagogical_move = clarify
  number_of_questions = 1
  question_style = simple_open

clarify_frontier_reached =
  last_tutorial_move in {clarify, elicit_action}
  and consecutive_clarify_turns >= 1
  and episode_clarity in {medium, high}
  and has_concrete_actions

Si cognitive_load == high ou interaction_risk == high:
  move = pace ou repair
  intent = protect_and_continue
  number_of_questions = 1
  question_style = single_safe
  contraintes = single_question_only + no_question_stacking + no_micro_explanation

Sinon si episode_clarity == low:
  intent = clarify_episode
  move = clarify

Sinon si has_concrete_actions == false:
  intent = elicit_concrete_action
  move = elicit_action

Sinon si clarify_frontier_reached:
  intent = exit_clarification_loop
  move = analyze si problem_salience in {low, high} sinon problematize
  contraintes += do_not_repeat_action_clarification + anchor_on_existing_actions

Sinon si safety_or_quality_risk_level in {medium, high}:
  intent = secure_and_analyze
  move = analyze
  contraintes += anchor_to_referential_criterion
  si technical_criterion_focus == none:
    contraintes += ask_for_criterion_explicitation
  si tech_representation_level == explicit:
    contraintes += allow_practice_reference_comparison

Sinon si problem_salience == none et reflection_phase == description:
  intent = surface_problem
  move = problematize

Sinon si contradiction_status == suspected et episode_clarity in {medium, high}:
  intent = check_contradiction
  move = contrast_gently

Sinon si can_close_for_now:
  intent = close_safely
  move = close

Sinon si intervention_necessity == none:
  intent = stabilize_without_reopening
  move = reformulate

Sinon si reflection_phase == analysis:
  intent = deepen_analysis
  move = analyze

Sinon si reflection_phase == projection:
  intent = support_projection
  move = project

Sinon:
  intent = stabilize_description
  move = clarify

Ensuite, hors mode protecteur:
  si need_encouragement et self_efficacy_signal == low et episode_clarity in {medium, high} et has_concrete_actions:
    intent = restore_confidence
    move = reassure
    contraintes += validation_before_question

  same_micro_objective =
    primary_intent in {deepen_analysis, support_projection, secure_and_analyze}

  problematize_can_double =
    pedagogical_move == problematize
    and has_concrete_actions
    and episode_clarity in {medium, high}

  si (same_micro_objective et episode_clarity == high et reflective_depth == high)
     ou problematize_can_double:
    number_of_questions = 2
    question_style = double_same_goal
  sinon:
    number_of_questions = 1
    question_style = simple_open

Calculer ensuite:
  should_explain_briefly
  should_recap
  should_encourage
  should_reframe
  should_close
```

## 5.2 Version pseudo-code plus proche du code reel
```python
def decide_conversation(state):
    primary_intent = "maintain_progress"
    pedagogical_move = "clarify"
    number_of_questions = 1
    question_style = "simple_open"

    if state.cognitive_load == "high" or state.interaction_risk == "high":
        pedagogical_move = "pace" if state.cognitive_load == "high" else "repair"
        primary_intent = "protect_and_continue"
        number_of_questions = 1
        question_style = "single_safe"

    elif state.episode_clarity == "low":
        primary_intent = "clarify_episode"
        pedagogical_move = "clarify"

    elif not state.has_concrete_actions:
        primary_intent = "elicit_concrete_action"
        pedagogical_move = "elicit_action"

    elif clarify_frontier_reached(state):
        primary_intent = "exit_clarification_loop"
        pedagogical_move = "analyze" if state.problem_salience in {"low", "high"} else "problematize"

    elif state.safety_or_quality_risk_level in {"medium", "high"}:
        primary_intent = "secure_and_analyze"
        pedagogical_move = "analyze"

    elif state.problem_salience == "none" and state.reflection_phase == "description":
        primary_intent = "surface_problem"
        pedagogical_move = "problematize"

    elif state.contradiction_status == "suspected" and state.episode_clarity in {"medium", "high"}:
        primary_intent = "check_contradiction"
        pedagogical_move = "contrast_gently"

    elif state.can_close_for_now:
        primary_intent = "close_safely"
        pedagogical_move = "close"

    elif state.intervention_necessity == "none":
        primary_intent = "stabilize_without_reopening"
        pedagogical_move = "reformulate"

    elif state.reflection_phase == "analysis":
        primary_intent = "deepen_analysis"
        pedagogical_move = "analyze"

    elif state.reflection_phase == "projection":
        primary_intent = "support_projection"
        pedagogical_move = "project"

    else:
        primary_intent = "stabilize_description"
        pedagogical_move = "clarify"

    if not protected(state):
        if encouragement_case(state):
            primary_intent = "restore_confidence"
            pedagogical_move = "reassure"

        if double_question_case(state, primary_intent, pedagogical_move):
            number_of_questions = 2
            question_style = "double_same_goal"
        else:
            number_of_questions = 1
            question_style = "simple_open"

    should_explain_briefly = micro_explanation_case(state)
    should_recap = state.need_recap and state.cognitive_load != "high"
    should_encourage = state.need_encouragement
    should_reframe = state.need_reframing and pedagogical_move not in {"repair", "pace"}
    should_close = state.can_close_for_now and pedagogical_move == "close"
```

## 6. Regles exactes sur `number_of_questions`

## 6.1 Valeur decidee par `decision_engine`
La valeur decidee aujourd'hui est en pratique:

- `1` dans la plupart des cas;
- `2` dans certains cas;
- jamais `3` dans `decision_engine`.

## 6.2 Cas forcement a 1 question
`number_of_questions = 1` si:

- `cognitive_load == high`
- ou `interaction_risk == high`

Dans ce cas:

- `question_style = single_safe`
- contraintes:
  - `single_question_only`
  - `simple_wording_only`
  - `no_question_stacking`
  - `no_micro_explanation`

## 6.3 Cas autorisant 2 questions
Hors mode protecteur, `number_of_questions = 2` si:

### Cas A
`primary_intent` est dans:

- `deepen_analysis`
- `support_projection`
- `secure_and_analyze`

et en plus:

- `episode_clarity == high`
- `reflective_depth == high`

### Cas B
`pedagogical_move == "problematize"`

et:

- `has_concrete_actions == true`
- `episode_clarity in {"medium", "high"}`

Dans ces cas:

- `question_style = double_same_goal`
- contrainte ajoutee: `two_questions_same_micro_goal_max`

## 6.4 Borne par le `TutorPrompt`
Dans l'orchestrateur:

```python
bounded_question_count = max(
    1,
    min(max_questions_per_turn, conversation_decision.number_of_questions),
)
```

Donc:

- le backend ne depassera jamais `TutorPrompt.max_questions_per_turn`;
- mais il peut etre plus restrictif que le prompt.

## 6.5 Impact des output guardrails
La reponse finale peut encore etre reduite par `_apply_output_guardrails()`:

- si mode `single_question` ou contraintes de securite:
  1 seule question conservee;
- si mode `reflection_block`:
  maximum 2 questions extraites du texte, plus eventuellement une ligne d'accompagnement;
- si mode `multi_question_numbered`:
  extraction/troncature a `max_questions`.

Important:

- meme si un `TutorPrompt` autorise 3 questions;
- meme si le LLM en produit 3;
- le pipeline actuel peut encore sortir 1 ou 2 questions selon `conversation_decision` et `output_mode`.

## 7. Regles exactes sur le changement de phase

## 7.1 Resolution de la phase effective d'entree
Ordre de priorite:

1. `user_input.session_phase` si fourni et valide;
2. `session.manual_phase_override` si present;
3. `session.current_phase` si present;
4. sinon `exploration`.

## 7.2 Calcul heuristique de `turn_state.session_phase`
Regle exacte:

- si `base_phase == opening` -> `opening`
- sinon si `base_phase == potential_closure` -> `potential_closure`
- sinon si `reflection_phase == analysis` -> `deepening`
- sinon si `reflection_phase == projection` et `evidence_strength in {medium, high}` -> `potential_closure`
- sinon -> `exploration`

Donc:

- `session_phase` peut regresser a `exploration` si l'analyse n'est pas encore suffisante;
- la logique n'est pas strictement monotone.

## 7.3 Determinisme dans `TeachingPlan`
`_derive_next_phase_from_state()` applique:

- si `conversation_decision.should_close` ou `turn_state.can_close_for_now` -> `potential_closure`
- sinon si `episode_clarity == low` ou `has_concrete_actions == false` -> `exploration`
- sinon si `reflection_phase == analysis` -> `deepening`
- sinon si `reflection_phase == projection` et `evidence_strength in {medium, high}` -> `potential_closure`
- sinon fallback vers `compute_next_session_phase()`

`compute_next_session_phase()` utilise des heuristiques textuelles:

- `opening` -> `exploration` si le texte n'est pas vide
- `exploration` -> `deepening` si patterns de raisonnement (`parce que`, `j'ai choisi`, `analyse`, etc.)
- `deepening` -> `potential_closure` si patterns de projection (`je vais`, `prochaine fois`, `checklist`, etc.)

## 7.4 Adaptateur de phase avant classifieur LLM
`phase_decider._derive_adapter_phase()` applique:

- si `should_close` ou `can_close_for_now` -> `potential_closure`
- sinon si `episode_clarity == low` ou `has_concrete_actions == false` -> `exploration`
- sinon si `pedagogical_move in {"analyze", "contrast_gently"}` -> `deepening`
- sinon si `pedagogical_move == "project"` -> `potential_closure`
- sinon -> phase deterministe du teaching plan

## 7.5 Classifieur LLM de phase
Si le classifieur de phase est actif:

- il propose `opening|exploration|deepening|potential_closure` avec un `confidence`;
- son resultat n'est accepte que si:
  - la phase candidate est valide;
  - la transition est autorisee;
  - `confidence >= phase_classifier_min_confidence`.

La FSM du classifieur autorise seulement:

- rester sur place;
- ou avancer d'un cran.

Regle exacte:

```python
return candidate_idx in {current_idx, current_idx + 1}
```

Donc le classifieur LLM ne peut pas:

- revenir en arriere;
- sauter directement 2 phases.

Mais attention:

- le `state_adapter`, lui, peut renvoyer `exploration` meme depuis une phase plus avancee.
- la contrainte FSM s'applique seulement au candidat LLM, pas au fallback adapter.

## 7.6 Ecriture en base
Dans `views_sessions.py`:

- si `next_session_phase` est valide et differente de `session.current_phase`,
- alors `session.current_phase` est mise a jour avant l'appel LLM de reponse.

## 8. Regles exactes sur la cloture

## 8.1 Condition backend `can_close_for_now`
`can_close_for_now = true` si toutes les conditions suivantes sont vraies:

- `session_phase == potential_closure`
- `session_maturity == high`
- `evidence_strength == high`
- `interaction_risk == low`
- `cognitive_load != high`

## 8.2 Condition `should_close`
`should_close = true` si:

- `can_close_for_now == true`
- et `pedagogical_move == "close"`

## 8.3 Effets de la cloture
Si `should_close` ou `can_close_for_now`:

- la phase suivante est forcee vers `potential_closure`;
- le prompt peut activer recap et cloture naturelle;
- la contrainte `closure_must_be_natural` est ajoutee si `should_close`.

Important:

- il ne s'agit pas d'une fermeture "hard stop" de la session;
- il s'agit d'une eligibility a conclure proprement.

## 9. Exemples complets anonymises

## 9.1 Exemple A - cas securite/qualite, analyse, 1 question

### Message apprenant
```text
Avant de remettre sous tension, j'ai branche un radiateur de 2500 W sur une ligne 16 A
ou il y avait deja un autre radiateur. Ca a disjoncte et je n'avais pas verifie la puissance totale.
```

### `turn_state` attendu selon les regles actuelles
```json
{
  "episode_clarity": "high",
  "has_concrete_actions": true,
  "problem_salience": "none",
  "reflection_phase": "description",
  "reflective_depth": "low",
  "self_efficacy_signal": "neutral",
  "affect_valence": "neutral",
  "cognitive_load": "low",
  "interaction_risk": "low",
  "epistemic_balance": "balanced",
  "zpd_estimate": "in",
  "session_phase": "exploration",
  "session_maturity": "low",
  "evidence_strength": "medium",
  "intervention_necessity": "none",
  "contradiction_status": "none",
  "concept_clarity": "low",
  "available_material": "medium",
  "conversation_goal": "structure_description",
  "current_phase": "exploration",
  "emotional_state": "neutral",
  "action_feasibility": "medium",
  "autonomy_level": "medium",
  "recent_progress": "unclear",
  "need_recap": false,
  "need_encouragement": false,
  "need_reframing": true,
  "can_close_for_now": false,
  "last_tutorial_move": "",
  "consecutive_clarify_turns": 0,
  "sticky_has_concrete_actions": true,
  "tech_representation_level": "partial",
  "technical_criterion_focus": "none",
  "safety_or_quality_risk_level": "high"
}
```

### `conversation_decision` attendu
```json
{
  "primary_intent": "secure_and_analyze",
  "pedagogical_move": "analyze",
  "number_of_questions": 1,
  "question_style": "simple_open",
  "should_explain_briefly": false,
  "should_recap": false,
  "should_encourage": false,
  "should_reframe": true,
  "should_close": false,
  "response_constraints": [
    "one_regulation_objective",
    "anchor_to_referential_criterion",
    "ask_for_criterion_explicitation",
    "single_question_default",
    "question_style:simple_open",
    "question_count:1"
  ]
}
```

### Effet sur la phase
- `teaching_plan.next_session_phase` tend vers `deepening` car le move est `analyze` dans l'adapter de phase.
- Si le classifieur de phase ne prend pas la main, `session.current_phase` est mise a jour vers `deepening`.

### Exemple de `raw_response` plausible
```text
Tu as deja repere un point important dans la situation.
Peux-tu expliquer comment tu aurais pu verifier, avant la remise sous tension, si la ligne pouvait supporter la puissance totale ?
```

### `final_response` apres guardrails en mode `reflection_block`
```text
Tu as deja repere un point important dans la situation.
1. Peux-tu expliquer comment tu aurais pu verifier, avant la remise sous tension, si la ligne pouvait supporter la puissance totale ?
```

## 9.2 Exemple B - problematization, 2 questions

### Message apprenant
```text
J'ai remplace un bouton poussoir, j'ai recable comme l'ancien, puis j'ai teste.
Ca marche, mais je ne sais pas trop ce que j'aurais du verifier avant de remettre en service.
```

### `turn_state` attendu selon les regles actuelles
```json
{
  "episode_clarity": "high",
  "has_concrete_actions": true,
  "problem_salience": "none",
  "reflection_phase": "description",
  "reflective_depth": "low",
  "self_efficacy_signal": "low",
  "affect_valence": "neutral",
  "cognitive_load": "low",
  "interaction_risk": "low",
  "epistemic_balance": "balanced",
  "zpd_estimate": "in",
  "session_phase": "exploration",
  "session_maturity": "low",
  "evidence_strength": "medium",
  "intervention_necessity": "low",
  "contradiction_status": "none",
  "concept_clarity": "low",
  "available_material": "medium",
  "conversation_goal": "structure_description",
  "current_phase": "exploration",
  "emotional_state": "neutral",
  "action_feasibility": "medium",
  "autonomy_level": "low",
  "recent_progress": "unclear",
  "need_recap": false,
  "need_encouragement": true,
  "need_reframing": true,
  "can_close_for_now": false,
  "last_tutorial_move": "",
  "consecutive_clarify_turns": 0,
  "sticky_has_concrete_actions": true,
  "tech_representation_level": "implicit",
  "technical_criterion_focus": "none",
  "safety_or_quality_risk_level": "low"
}
```

### `conversation_decision` attendu
```json
{
  "primary_intent": "surface_problem",
  "pedagogical_move": "problematize",
  "number_of_questions": 2,
  "question_style": "double_same_goal",
  "should_explain_briefly": false,
  "should_recap": false,
  "should_encourage": true,
  "should_reframe": true,
  "should_close": false,
  "response_constraints": [
    "one_regulation_objective",
    "two_questions_same_micro_goal_max",
    "question_style:double_same_goal",
    "question_count:2"
  ]
}
```

### Exemple de `raw_response` plausible
```text
Tu as deja une base concrete sur laquelle t'appuyer.
Qu'est-ce que tu considères maintenant comme le point de verification le plus decisif avant remise en service ?
Et qu'est-ce que cette verification t'aurait permis de confirmer ou d'ecarter ?
```

### `final_response` apres guardrails en mode `reflection_block`
```text
Tu as deja une base concrete sur laquelle t'appuyer.
1. Qu'est-ce que tu consideres maintenant comme le point de verification le plus decisif avant remise en service ?
2. Et qu'est-ce que cette verification t'aurait permis de confirmer ou d'ecarter ?
```

## 10. Points fragiles ou provisoires connus

## 10.1 Heuristiques lexicales encore simples
Une grande partie de P0 repose sur des regex lexicales.

Conséquences:

- sensibilite aux formulations exactes;
- couverture imparfaite du francais reel;
- fragilite face aux fautes, abreviations, regionalismes, jargon metier local.

## 10.2 `problem_salience` et `safety_or_quality_risk_level` ne couvrent pas les memes lexiques
Exemple typique:

- `disjoncte` fait monter le risque securite/qualite;
- mais ne fait pas automatiquement monter `problem_salience`.

Donc un message peut etre:

- tres technique et risqué;
- mais encore vu comme `problem_salience = none`.

Ce n'est pas incoherent du point de vue code, mais c'est un point de vigilance pedagogique.

## 10.3 Certaines variables sont calculees mais peu ou pas consommees dans la decision
Exemples:

- `recent_progress`
- `autonomy_level`
- `action_feasibility`
- `emotional_state`

Elles existent dans `TurnState`, sont injectees dans le prompt/tracing, mais influencent peu ou pas directement `decision_engine`.

## 10.4 `current_phase` duplique `session_phase`
`current_phase` est actuellement une copie de `session_phase`.

Cela simplifie certains contrats de prompt/UI, mais introduit une redondance.

## 10.5 `emotional_state` duplique `affect_valence`
Meme logique:

- utile pour le contrat de rendu;
- mais redondant techniquement.

## 10.6 `sticky_has_concrete_actions` peut prolonger artificiellement une impression de concret
Comme l'historique garde en memoire que des actions ont deja ete donnees:

- un message elliptique suivant peut rester interprete comme suffisamment concret;
- cela aide contre les boucles;
- mais peut parfois masquer un besoin reel de re-clarification locale.

## 10.7 `session_maturity` est basee sur un comptage simple
`session.messages.count()` compte la session de facon brute.

Cela reste un proxy tres simple:

- il ne distingue pas la richesse effective des tours;
- il ne tient pas compte de la qualite du travail reflexif;
- il depend du volume de tours plutot que de leur valeur pedagogique.

## 10.8 La phase peut regresser via l'adapter
Le classifieur de phase LLM est borne par une FSM "stay ou +1".

En revanche:

- l'adapter backend peut renvoyer `exploration` depuis une phase plus avancee si clarte basse ou actions manquantes.

Donc la progression globale n'est pas strictement monotone.

## 10.9 Le classifieur de phase semble actuellement fragile au parsing
Dans l'etat actuel du fichier `phase_decider.py`, la fonction `_extract_json_object()` parait inachevee, avec du code de parsing situe apres un `return` dans une autre fonction.

Effet probable:

- le classifieur LLM de phase peut retomber frequemment, voire systematiquement, sur `state_adapter`.

Ce point doit etre verifie/corrige si l'on attend un reel arbitrage LLM sur la phase.

## 10.10 `number_of_questions` est re-borne a plusieurs etages
Il y a plusieurs niveaux:

1. `decision_engine`
2. `TutorPrompt.max_questions_per_turn`
3. `_derive_output_mode()`
4. `_apply_output_guardrails()`

Conséquence:

- une bonne sortie LLM peut encore etre contractee apres coup;
- la cause d'un "une seule question" n'est pas necessairement le prompt.

## 10.11 Le mode `reflection_block` n'extrait que 2 questions max
Dans `_apply_output_guardrails()`:

```python
questions = _extract_questions(text, min(max_questions, 2))
```

Donc, en pratique:

- meme si `max_questions_this_turn = 3`,
- un `reflection_block` n'extrait actuellement jamais plus de 2 questions.

## 10.12 Les exemples et patterns sont aujourd'hui tres orientes situations techniques terrain
Le systeme est deja favorable aux cas type MELEC:

- disjoncteur
- differentiel
- terre
- puissance
- câblage

Mais il est moins robuste pour:

- d'autres domaines professionnels;
- des situations plus relationnelles ou organisationnelles;
- des formulations pedagogiques plus meta-reflexives.

## 11. Resume executif

### Ce qui est stable aujourd'hui
- P0 calcule bien un etat structure avant la generation.
- La decision conversationnelle est deterministe.
- Les variables de risque, de clarte et d'actions concretes pilotent reellement la reponse.
- L'anti-boucle repose deja sur l'historique.

### Ce qui reste provisoire
- les heuristiques lexicales;
- certaines redondances dans `TurnState`;
- le role reel du classifieur LLM de phase;
- la consommation encore partielle de certaines variables derivees;
- le fait que `reflection_block` soit en pratique plafonne a 2 questions.

### Question cle pour les evolutions
La bonne question n'est pas seulement:

"Est-ce que la variable est bien nommee ?"

mais:

"Est-ce que cette variable produit effectivement une meilleure decision conversationnelle et une meilleure progression pedagogique ?"
