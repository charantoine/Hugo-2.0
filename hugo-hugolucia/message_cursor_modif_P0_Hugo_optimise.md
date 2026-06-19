# Message pour Cursor — patch prioritaire P0 pour fiabiliser Hugo dans un fil de conversation

## But

Je te demande un patch **ciblé, rapide et robuste** de P0 pour améliorer le fonctionnement d’Hugo **dans une conversation unique**.

La priorité n’est pas encore la mémoire inter-conversations, ni l’intégration complète de tous les contextes de formation.
La priorité est de corriger les bugs et comportements observés dans un fil courant :

- perte du dernier message ;
- fuite méta du prompt interne dans la réponse visible ;
- boucle sur des points déjà couverts ;
- incapacité à aider quand l’apprenant dit « je sais pas » / « aide moi » ;
- incapacité à clore vraiment quand l’apprenant dit « on a fini », « non j’ai fini », « oui, déjà dit », etc. ;
- sur-usage de `problematize` / `surface_problem` alors que la conversation a déjà avancé.

Je veux une solution **P0-first**, compatible avec l’existant, sans refonte générale.

---

## Intention fonctionnelle

À l’échelle d’un fil, Hugo doit :

1. savoir ce qui est **déjà acquis** ;
2. savoir ce qui est **encore ouvert** ;
3. détecter et prioriser :
   - les demandes d’aide ;
   - les signaux de répétition / saturation ;
   - les signaux explicites de clôture ;
4. choisir un **geste tutoriel pertinent** ;
5. pouvoir produire **0, 1 ou 2 questions** selon le geste choisi ;
6. ne jamais laisser fuiter du méta-prompt dans la réponse finale.

---

## Contraintes de design

### A. Un seul micro-objectif de régulation par tour
On garde ce principe.

### B. Fin de la pseudo-règle « une seule question simple par message »
La décision correcte est :

- d’abord choisir le **geste tutoriel** ;
- ensuite décider le nombre de questions : **0, 1 ou 2** ;
- `2` seulement si les deux questions servent le même micro-objectif ;
- `0` si le bon comportement est une clôture effective.

### C. Patch additif
Je veux un patch additif et rapide, pas une refonte profonde.

### D. D’abord heuristique
Pour ce patch, privilégier des heuristiques robustes plutôt qu’un nouveau classifieur LLM complexe.

---

## Diagnostic à corriger

Aujourd’hui, même quand l’apprenant a déjà :

- décrit la situation ;
- formulé une cause plausible ;
- formulé une action future ;
- demandé de l’aide ;
- ou demandé explicitement de conclure ;

le moteur retombe trop souvent sur :

- `reflection_phase = description`
- `problem_salience = none`
- `primary_intent = surface_problem`
- `pedagogical_move = problematize`
- `should_close = false`

Je veux donc rééquilibrer la décision de tour autour de :

- la **couverture du fil courant** ;
- les **signaux explicites de l’apprenant** ;
- la **sortie des boucles** ;
- la **clôture effective**.

---

# 1. Ajouter une mémoire de couverture minimale dans `TurnState`

## Fichier
`backend/apps/hugo/domain/schemas.py`

## Nouveaux champs à ajouter à `TurnState`

```python
covered_points: list[str]
remaining_open_points: list[str]
learner_help_request: str
closure_signal: str
repetition_signal: str
loop_risk: str
assistant_meta_leak_risk: str
```

## Valeurs attendues

### `covered_points`
Liste de points déjà couverts dans le fil.

Valeurs à gérer au minimum :

- `episode_described`
- `concrete_actions_described`
- `problem_named`
- `cause_hypothesis_named`
- `cause_confirmed`
- `future_action_named`
- `learning_rule_named`
- `session_done_explicitly`

### `remaining_open_points`
Liste de points encore utiles à ouvrir.

Valeurs minimales :

- `missing_episode_details`
- `missing_problem_identification`
- `missing_cause`
- `missing_future_action`
- `missing_transfer_rule`
- `need_closure_confirmation`
- `none`

### `learner_help_request`
Enum :

- `none`
- `implicit`
- `explicit`

### `closure_signal`
Enum :

- `none`
- `implicit`
- `explicit`

### `repetition_signal`
Enum :

- `none`
- `implicit`
- `explicit`

### `loop_risk`
Enum :

- `low`
- `medium`
- `high`

### `assistant_meta_leak_risk`
Enum :

- `low`
- `high`

---

# 2. Calculer ces champs dans `turn_state_analyzer.py`

## Fichier
`backend/apps/hugo/services/turn_state_analyzer.py`

## Règles demandées

### `covered_points`
Calcul cumulatif à partir :

- du message courant ;
- des derniers tours ;
- des payloads précédents si disponibles.

Exemples :

- si l’apprenant a raconté une suite d’actions : ajouter `episode_described`, `concrete_actions_described` ;
- s’il dit « j’aurais pas dû forcer » : ajouter `cause_hypothesis_named` ;
- s’il dit « un des fils était sorti de la cosse » : ajouter `cause_confirmed` ;
- s’il dit « la prochaine fois je vérifierai… » : ajouter `future_action_named` ;
- s’il dit « j’ai fini » : ajouter `session_done_explicitly`.

### `remaining_open_points`
Calculer par différence entre :

- ce qui serait utile pour une réflexion minimale ;
- ce qui est déjà couvert.

Important : si `closure_signal == explicit`, réduire fortement cette liste, sauf risque sécurité/qualité bloquant.

### `learner_help_request`
Détection heuristique robuste.
Exemples à gérer :

- explicite : `aide moi`, `je sais pas aide moi`, `dis moi`, `je comprends pas aide moi`
- implicite : `je sais pas`, `je vois pas`, `je bloque`

### `closure_signal`
Détection heuristique robuste.
Exemples à gérer :

- explicite : `on a fini`, `c'est fini`, `j'ai fini`, `oui déjà dit`
- implicite : `je pense qu'on a fait le tour`, `c'est réglé`

### `repetition_signal`
Détection heuristique robuste.
Exemples à gérer :

- explicite : `on tourne en rond`, `déjà dit`, `je te l'ai déjà dit`
- implicite : `encore`, `je viens de le dire`

### `loop_risk`
Règle simple :

- `high` si `repetition_signal == explicit`
- `high` si on continue à questionner un point déjà couvert sans ouvrir de nouveau point
- `medium` si stagnation sur plusieurs tours
- sinon `low`

### `can_close_for_now`
Conserver la logique actuelle, mais ajouter une logique de clôture par couverture.

Proposition minimum :

```python
can_close_from_coverage = (
    "episode_described" in state.covered_points
    and (
        "cause_hypothesis_named" in state.covered_points
        or "cause_confirmed" in state.covered_points
        or "future_action_named" in state.covered_points
        or "learning_rule_named" in state.covered_points
    )
)
```

Puis intégrer ça dans la logique de clôture.

---

# 3. Revoir l’ordre de priorité dans `decision_engine.py`

## Fichier
`backend/apps/hugo/services/decision_engine.py`

## Problème actuel
L’ordre de décision favorise trop tôt `problematize`.

## Nouvel ordre demandé

Pseudo-code cible :

```python
def decide_conversation(state):
    init_defaults()

    if protected_mode(state):
        return protect_and_continue(state)

    if explicit_closure_case(state):
        return close_now(state)

    if explicit_repetition_case(state):
        return repair_and_close_or_shift(state)

    if explicit_help_request_case(state):
        return assist_reasoning(state)

    if safety_or_quality_priority_case(state):
        return secure_and_analyze(state)

    if contradiction_case(state):
        return contrast_gently(state)

    if closeable_case(state):
        return close_now(state)

    if analysis_case(state):
        return deepen_analysis(state)

    if projection_case(state):
        return support_projection(state)

    if clarification_frontier_reached(state):
        return analyze_or_consolidate_from_existing_actions(state)

    if episode_still_unclear(state):
        return clarify_episode(state)

    if concrete_actions_missing(state):
        return elicit_action(state)

    return stabilize_or_reformulate(state)
```

## Effets fonctionnels attendus

### `explicit_closure_case(state)`
Si l’apprenant exprime explicitement qu’il veut finir :

- `primary_intent = close_safely`
- `pedagogical_move = close`
- `number_of_questions = 0`
- `should_close = True`
- ajouter une contrainte type `respect_explicit_closure`

Sauf cas exceptionnel sécurité/qualité vraiment bloquant.

### `explicit_repetition_case(state)`
Si l’apprenant dit `on tourne en rond`, `déjà dit`, etc. :

- ne jamais repartir en `problematize`
- ne jamais reposer une question de clôture déjà posée
- aller vers `repair`, `reformulate` bref ou `close`

### `explicit_help_request_case(state)`
Si l’apprenant dit `je sais pas, aide moi` ou équivalent :

- ne pas repartir sur `problematize`
- ne pas repartir sur `project`
- aller vers un mode d’aide brève

Option préférée : créer un nouveau `pedagogical_move = assist`.

Sinon, fallback acceptable : `analyze` avec `should_explain_briefly = True`.

### `closeable_case(state)`
Je veux que la clôture soit déclenchable :

- par `closure_signal`
- par `can_close_for_now`
- par couverture suffisante du fil

### Réduction de `problematize`
`problematize` doit devenir un cas plus rare.
Ne l’utiliser que si :

- le problème n’a pas encore émergé ;
- pas de demande d’aide ;
- pas de répétition ;
- pas de clôture ;
- pas de fil déjà suffisamment couvert.

---

# 4. Autoriser `number_of_questions = 0`

## Fichiers
- `decision_engine.py`
- `teaching_plan_builder.py`
- `prompt_renderer.py`
- guardrails de sortie

## Règle demandée
Le nombre de questions dépend du geste tutoriel.

### `close`
- `0` par défaut
- `1` exceptionnellement si vraie validation minimale utile

### `repair`, `pace`, `assist`
- `0` ou `1`
- jamais `2`

### `analyze`, `project`, `secure_and_analyze`
- `1` ou `2`
- `2` seulement si même micro-objectif

### `clarify`, `elicit_action`, `problematize`
- `1` par défaut
- `2` possible seulement si le fil n’est pas saturé

## Important
Il faut vérifier toute la chaîne :

- borne `TutorPrompt.max_questions_per_turn`
- output mode
- `_apply_output_guardrails()`

Objectif : si `number_of_questions = 0`, aucun post-traitement ne doit réinjecter artificiellement une question.

---

# 5. Revoir la clôture

## Fichiers
- `turn_state_analyzer.py`
- `decision_engine.py`
- `phase_decider.py`
- éventuellement `teaching_plan_builder.py`

## Nouvelle logique demandée
Distinguer clairement :

- `can_close_for_now` = éligibilité structurelle
- `should_close` = décision réelle du tour
- `closure_signal` = volonté exprimée par l’apprenant

Et faire en sorte que `closure_signal = explicit` puisse, dans la majorité des cas, **surcharger** le reste.

## Attendu

### Cas explicite
Exemples :
- `on a fini ?`
- `ok c'est fini`
- `non j'ai fini`
- `oui déjà dit`

Réponse attendue :
- clôture brève
- aucune nouvelle question
- pas de reformulation longue
- pas de nouvelle validation de clôture

### Cas implicite mais fil mûr
Si le fil a déjà produit :
- situation décrite
- cause plausible
- action future ou règle de transfert

alors :
- clôture ou mini-bilan bref
- ne pas rouvrir un sous-thème artificiel

## Point important pour `phase_decider.py`
Si `should_close = True` ou `closure_signal = explicit`, ne pas laisser le système reboucler vers `exploration` sauf raison sécurité/qualité majeure.

---

# 6. Ajouter un garde-fou anti-fuite méta

## Fichiers
- `backend/apps/hugo/services/prompt_renderer.py`
- couche de guardrails de sortie

## Problème à corriger
Ne plus jamais sortir dans la réponse finale des formulations du type :

- `je vois que vous me demandez de rebondir sur le dernier message de l'apprenant`
- `j'aurais besoin de connaître ce message`
- `pourriez-vous me le communiquer ?`
- `tu échanges avec un apprenant`
- `system prompt`
- `instruction`

## Règles demandées

### A. Détection
Créer une liste de patterns interdits.

### B. Remédiation
Si pattern détecté :

1. ne jamais livrer tel quel ;
2. tenter une réécriture locale sûre ;
3. sinon fallback vers une réponse courte non méta.

### C. Prévention
Sécuriser l’injection du dernier message apprenant dans le prompt renderer pour éviter toute ambiguïté entre :

- message apprenant ;
- consigne de cadrage ;
- bloc d’instructions.

---

# 7. Adapter le prompt renderer au nouvel état

## Fichier
`backend/apps/hugo/services/prompt_renderer.py`

Le prompt effectif doit exploiter au minimum :

- `covered_points`
- `remaining_open_points`
- `learner_help_request`
- `closure_signal`
- `repetition_signal`
- `loop_risk`

## Directives à injecter

Ajouter des consignes explicites du type :

- n’ouvre pas un point déjà couvert sauf contradiction ou ambiguïté nette ;
- si l’apprenant demande de l’aide explicitement, aide-le brièvement avant toute relance ;
- si l’apprenant signale une répétition, reconnais-la brièvement et change d’action ;
- si l’apprenant clôt explicitement, clos sans rouvrir ;
- tu peux poser 0, 1 ou 2 questions selon la décision ;
- si `number_of_questions = 0`, ne pose aucune question finale.

---

# 8. Ce qu’il faut modifier, fichier par fichier

## `backend/apps/hugo/domain/schemas.py`
- Ajouter les nouveaux champs à `TurnState`
- Ajouter `assist` au type de `pedagogical_move` si ce choix est retenu

## `backend/apps/hugo/services/turn_state_analyzer.py`
- Calculer `covered_points`
- Calculer `remaining_open_points`
- Détecter `learner_help_request`
- Détecter `closure_signal`
- Détecter `repetition_signal`
- Calculer `loop_risk`
- Revoir `can_close_for_now`

## `backend/apps/hugo/services/decision_engine.py`
- Revoir l’ordre des priorités
- Ajouter la branche `assist_reasoning`
- Autoriser `number_of_questions = 0`
- Réduire fortement `problematize`
- Déclencher `should_close` correctement

## `backend/apps/hugo/services/phase_decider.py`
- Stabiliser la clôture
- Éviter les retours artificiels en `exploration` quand la clôture est explicite

## `backend/apps/hugo/services/teaching_plan_builder.py`
- Répercuter correctement `should_close`
- Supporter `number_of_questions = 0`
- Supporter le nouveau move éventuel `assist`

## `backend/apps/hugo/services/prompt_renderer.py`
- Injecter les nouveaux champs
- Sécuriser l’injection du dernier message apprenant
- Ajouter les directives anti-boucle / aide / clôture

## Guardrails de sortie
- Bloquer la fuite méta
- Respecter strictement `number_of_questions = 0`
- Respecter la clôture effective

---

# 9. Critères d’acceptation

## Cas 1 — demande d’aide explicite
Entrée : `je sais pas, aide moi`

Attendu :
- pas de fuite méta
- pas de `problematize` automatique
- aide brève orientante
- au plus une question

## Cas 2 — signal de répétition
Entrée : `on tourne en rond, non ?`

Attendu :
- reconnaissance brève
- pas de répétition de la même question
- bascule vers `repair`, `reformulate` ou `close`

## Cas 3 — clôture explicite
Entrée : `non, j'ai fini`

Attendu :
- clôture effective
- 0 nouvelle question
- aucune relance de confirmation

## Cas 4 — clôture explicite après répétition
Entrée : `oui, déjà dit`

Attendu :
- pas de nouvelle question de clôture
- sortie courte et propre

## Cas 5 — fil déjà bien couvert
Contexte :
- cause déjà formulée
- action future déjà formulée

Attendu :
- pas de retour à `surface_problem`
- pas de question qui rouvre un point déjà traité
- possibilité de clôture propre

## Cas 6 — anti-fuite méta
Attendu :
- aucune réponse finale ne doit révéler le prompt interne ou la consigne de cadrage

---

# 10. Ce que j’attends comme livrable

Merci de produire :

1. le patch code ;
2. la liste des fichiers modifiés ;
3. un résumé des nouvelles priorités de décision ;
4. les tests minimaux couvrant les cas ci-dessus.

---

# 11. Résumé ultra-court

> Modifier P0 pour que Hugo régule le tour à partir de la couverture réelle du fil, des demandes d’aide, des signaux de répétition et des signaux de clôture, avec 0/1/2 questions selon le geste tutoriel, et sans aucune fuite méta dans la réponse finale.
