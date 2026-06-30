# Guide testeurs pédagogiques: comprendre P0 et proposer des améliorations

## Objectif du document
Ce document explique, en langage non technique, comment Hugo produit un **état de tour** avant de générer sa réponse.

Cet état s'appelle ici **P0**. Il sert à répondre à une question simple:

**"Dans quel état est la conversation maintenant, et de quel type d'aide l'apprenant a-t-il besoin au tour suivant ?"**

L'objectif pour les testeurs n'est donc pas seulement d'évaluer si la réponse "sonne bien", mais aussi de repérer:

- si Hugo a bien compris le niveau de description ou de réflexion de l'apprenant ;
- si Hugo choisit le bon geste pédagogique ;
- si la logique actuelle doit évoluer ;
- si le problème vient plutôt de la logique backend, du prompt, ou des deux.

## Vue d'ensemble
Le fonctionnement se fait en 3 étages:

1. **Analyse du message apprenant**
   Hugo repère des signaux dans le message: action concrète, problème, émotion, surcharge, projection, etc.

2. **Construction d'un état de tour**
   Ces signaux alimentent des variables structurées: par exemple `episode_clarity`, `reflection_phase`, `cognitive_load`.

3. **Décision conversationnelle**
   À partir de cet état, Hugo choisit:
   - le **geste pédagogique** (`clarify`, `analyze`, `problematize`, `project`, etc.) ;
   - le **nombre de questions** ;
   - le **style de réponse** ;
   - des contraintes de formulation.

Ensuite seulement, le prompt envoyé au LLM est construit.

En résumé:

- **P0 ne rédige pas la réponse** ;
- **P0 prépare le terrain pour que le prompt soit mieux orienté**.

## Les deux sources de P0
P0 peut venir de deux sources complémentaires.

### 1. Source heuristique
C'est la base du système.

Le backend applique des règles simples à partir du texte de l'apprenant:

- mots ou tournures qui signalent une action ;
- mots qui signalent un problème ;
- indices d'analyse, de projection, d'émotion, de charge cognitive, etc.

Exemple:

- "j'ai branché le radiateur" fait monter `has_concrete_actions` ;
- "ça a disjoncté" fait monter `problem_salience` et souvent `safety_or_quality_risk_level` ;
- "parce que" ou "j'ai choisi" poussent vers `reflection_phase = analysis`.

### 2. Classifieur LLM P0
En plus de cette base heuristique, Hugo peut lancer un **petit classifieur LLM**.

Ce classifieur ne rédige pas une réponse à l'apprenant. Il doit seulement renvoyer un **JSON strict** avec quelques variables P0.

Le backend:

- lui fournit le message apprenant ;
- lui donne comme référence l'état heuristique ;
- récupère son JSON ;
- vérifie qu'il est valide ;
- ne l'accepte que si sa **confiance** dépasse un seuil minimal.

Si le classifieur échoue, renvoie un JSON invalide, ou a une confiance trop faible:

- Hugo **retombe sur l'heuristique**.

## Ce que couvre exactement P0
Le noyau P0 minimal utilisé pour piloter la conversation contient 8 champs:

- `has_concrete_actions`
- `episode_clarity`
- `problem_salience`
- `reflection_phase`
- `affect_valence`
- `cognitive_load`
- `interaction_risk`
- `session_phase`

Parmi eux, le classifieur LLM ne surclasse directement que 7 champs:

- `has_concrete_actions`
- `episode_clarity`
- `problem_salience`
- `reflection_phase`
- `affect_valence`
- `cognitive_load`
- `interaction_risk`

`session_phase` est ensuite recalculé par la logique backend à partir de l'ensemble du contexte.

## Détail des variables du noyau P0

### 1. `has_concrete_actions`
Valeurs:

- `true`
- `false`

Question métier:

**L'apprenant décrit-il ce qu'il a fait, vu, testé, mesuré, branché, observé, choisi ?**

Exemples:

- "J'ai branché les deux fils et remis sous tension" -> `true`
- "Ça s'est mal passé" -> souvent `false`

Effet principal:

- si cette variable est à `false`, Hugo a tendance à **faire émerger des actions concrètes** avant d'aller vers l'analyse ;
- si elle est à `true`, Hugo peut plus facilement **sortir de la clarification**.

Point de vigilance test:

- un apprenant peut décrire une action de manière implicite ou familière ;
- si Hugo ne la reconnaît pas, il risque de reposer des questions déjà couvertes.

### 2. `episode_clarity`
Valeurs:

- `low`
- `medium`
- `high`

Question métier:

**La situation racontée est-elle suffisamment située et compréhensible ?**

Cette variable augmente si le message contient:

- des repères de contexte ;
- des actions concrètes ;
- une chronologie ;
- suffisamment de matière descriptive.

Effet principal:

- `low` pousse Hugo à clarifier ;
- `medium` ou `high` autorisent davantage l'analyse ou la problématisation.

Point de vigilance test:

- un message court mais précis peut être pédagogiquement suffisant ;
- à l'inverse, un message long peut rester flou.

### 3. `problem_salience`
Valeurs:

- `none`
- `low`
- `high`

Question métier:

**Le problème ou l'enjeu est-il réellement visible dans ce que dit l'apprenant ?**

Effet principal:

- si `none` et que l'apprenant reste en description, Hugo peut choisir `problematize` ;
- si `high`, Hugo peut passer en mode plus analytique, voire prudent si la sécurité est en jeu.

Point de vigilance test:

- il faut distinguer un problème technique réel d'une simple difficulté de formulation ;
- un système trop sensible peut dramatiser ;
- un système trop peu sensible peut rester plat.

### 4. `reflection_phase`
Valeurs:

- `description`
- `analysis`
- `projection`

Question métier:

**L'apprenant est-il en train de raconter, d'expliquer, ou d'anticiper la suite ?**

Repères actuels:

- `description`: il raconte ce qu'il s'est passé ;
- `analysis`: il explique, compare, justifie, cherche des causes ;
- `projection`: il dit ce qu'il ferait ensuite ou la prochaine fois.

Effet principal:

- `description` maintient souvent Hugo dans la structuration de l'épisode ;
- `analysis` permet d'aller vers `analyze` ;
- `projection` peut préparer une clôture ou un plan d'action.

Point de vigilance test:

- certains apprenants mélangent description et analyse dans une même phrase ;
- c'est souvent un bon terrain d'amélioration pour la logique et pour le prompt.

### 5. `affect_valence`
Valeurs:

- `negative`
- `neutral`
- `positive`

Question métier:

**Quel est le ton émotionnel du message ?**

Effet principal:

- `negative` peut activer davantage d'encouragement ;
- `positive` peut laisser plus de place à l'analyse ;
- `neutral` ne modifie pas fortement la stratégie.

Point de vigilance test:

- il ne faut pas sur-interpréter une émotion faible ;
- il ne faut pas non plus manquer un moment de découragement réel.

### 6. `cognitive_load`
Valeurs:

- `low`
- `medium`
- `high`

Question métier:

**L'apprenant semble-t-il déjà saturé, perdu, ou submergé ?**

Effet principal:

- si `high`, Hugo doit ralentir ;
- il passe alors en mode plus protecteur, avec une seule question, plus simple.

Point de vigilance test:

- une charge cognitive élevée n'est pas la même chose qu'un manque d'effort ;
- si cette variable est trop souvent à `high`, Hugo devient excessivement prudent.

### 7. `interaction_risk`
Valeurs:

- `low`
- `medium`
- `high`

Question métier:

**Y a-t-il un risque de rupture relationnelle, d'agacement, de retrait, ou de lassitude ?**

Effet principal:

- si `high`, Hugo évite d'empiler les questions ;
- il privilégie la réparation, l'apaisement, ou le recentrage.

Point de vigilance test:

- cette variable est importante pour éviter une conversation vécue comme intrusive ou scolaire ;
- mais si elle est sur-détectée, Hugo peut devenir trop timide.

### 8. `session_phase`
Valeurs actuellement utilisées:

- `opening`
- `exploration`
- `deepening`
- `potential_closure`

Question métier:

**Où en est la séance, du point de vue de sa progression pédagogique ?**

Cette phase ne dépend pas uniquement du message. Elle dépend aussi:

- de la phase courante de la session ;
- du niveau d'analyse détecté ;
- de la qualité des éléments fournis.

Effet principal:

- elle aide à faire évoluer l'entretien ;
- elle évite que tout reste bloqué en exploration.

Point de vigilance test:

- un mauvais passage de phase peut créer des boucles ;
- l'enjeu n'est pas d'aller vite en clôture, mais d'aller au bon moment.

## Les variables dérivées importantes
En plus du noyau P0, le backend calcule d'autres variables qui influencent fortement la suite.

Les plus utiles à lire en test sont les suivantes.

### `reflective_depth`
Estime la profondeur de réflexion déjà présente.

- `low` : peu d'analyse ;
- `medium` : début de mise en relation ;
- `high` : analyse plus installée.

### `evidence_strength`
Estime la qualité de la matière disponible pour avancer.

- `low`
- `medium`
- `high`

Cette variable monte si l'épisode est clair, concret, et déjà un peu analysé.

### `session_maturity`
Estime la maturité de la séance.

Elle dépend notamment:

- du nombre de tours ;
- des traces déjà existantes.

### `conversation_goal`
Objectif principal du tour suivant.

Exemples:

- `clarify_episode`
- `elicit_concrete_action`
- `deepen_analysis`
- `close_or_project`
- `structure_description`

### `need_recap`, `need_encouragement`, `need_reframing`
Ces booléens orientent le ton et la structure de la réponse.

Exemples:

- récapituler ;
- encourager ;
- recadrer doucement la réflexion.

### `last_tutorial_move`, `consecutive_clarify_turns`, `sticky_has_concrete_actions`
Ces variables servent surtout à l'**anti-boucle**.

Leur rôle:

- mémoriser le dernier geste pédagogique ;
- compter les tours successifs de clarification ;
- conserver le fait que des actions concrètes ont déjà été exprimées, même si le dernier message est moins précis.

### `tech_representation_level`, `technical_criterion_focus`, `safety_or_quality_risk_level`
Ces variables servent à mieux gérer les cas techniques et à mieux mobiliser le référentiel.

Exemples:

- l'apprenant parle-t-il de composants techniques précis ?
- fait-il explicitement référence à un critère, une norme, une sécurité, une conformité ?
- le message signale-t-il un risque sécurité ou qualité ?

Elles sont particulièrement importantes dans les cas MELEC.

## Comment la décision conversationnelle est prise
Une fois l'état calculé, Hugo décide du **geste pédagogique du tour**.

Les gestes possibles sont par exemple:

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

## Logique simplifiée de décision

### Cas 1: protection
Si `cognitive_load = high` ou `interaction_risk = high`:

- Hugo protège la relation ;
- il pose une seule question ;
- il simplifie la formulation ;
- il évite d'empiler plusieurs objectifs.

### Cas 2: manque de clarté
Si `episode_clarity = low`:

- Hugo clarifie l'épisode.

### Cas 3: manque d'actions concrètes
Si `has_concrete_actions = false`:

- Hugo cherche d'abord à faire décrire ce qui a été fait.

### Cas 4: sortie de boucle de clarification
Si l'apprenant a déjà donné assez d'éléments et que Hugo a déjà clarifié:

- Hugo doit sortir de la boucle ;
- il passe plutôt vers `analyze` ou `problematize`.

### Cas 5: risque sécurité ou qualité
Si `safety_or_quality_risk_level` est `medium` ou `high`:

- Hugo s'ancre davantage dans l'analyse ;
- il peut davantage orienter vers un critère du référentiel ;
- il évite de rester sur une clarification purement descriptive.

### Cas 6: analyse ou projection déjà engagée
Si l'apprenant est déjà dans l'analyse:

- Hugo peut approfondir.

Si l'apprenant est dans la projection:

- Hugo peut soutenir la suite ou préparer la clôture.

## Pourquoi Hugo pose parfois 1 question, parfois 2
Le nombre de questions n'est pas fixé uniquement par le prompt.

Il dépend aussi de la **décision conversationnelle**.

Règle actuelle simplifiée:

- si la conversation nécessite de la protection: 1 question ;
- sinon, la logique par défaut reste prudente ;
- 2 questions sont possibles quand elles servent **le même micro-objectif** ;
- `problematize` peut monter à 2 questions si l'épisode est assez clair et concret.

Donc, quand un testeur observe:

"Le prompt autorise 3 questions, mais Hugo n'en pose qu'une"

il faut vérifier si cela vient:

- du prompt ;
- des guardrails ;
- ou surtout de la décision backend `number_of_questions`.

## Rôle exact du prompt dans ce système
Le prompt ne décide pas tout seul de la stratégie.

Le backend lui transmet déjà des choix structurants:

- la phase ;
- l'intention principale ;
- le geste pédagogique ;
- les contraintes ;
- le nombre de questions visé ;
- le type de sortie attendu.

On peut donc distinguer deux types de problèmes.

### Problème de logique backend
Exemples:

- Hugo reste trop longtemps en clarification alors que l'apprenant a déjà donné des actions précises ;
- Hugo n'identifie pas qu'un problème technique est déjà formulé ;
- Hugo déclenche trop souvent une posture protectrice ;
- Hugo ne change pas de phase au bon moment.

Dans ce cas, il faut surtout ajuster:

- les variables ;
- leurs règles de calcul ;
- les seuils ;
- la décision conversationnelle.

### Problème de prompt
Exemples:

- le LLM a la bonne stratégie mais formule mal ;
- il reste trop scolaire ;
- il ne mobilise pas assez le référentiel alors que le backend l'y oriente ;
- il fait des réponses pauvres malgré un bon `pedagogical_move`.

Dans ce cas, il faut surtout ajuster:

- le `TutorPrompt` ;
- les formulations attendues ;
- les exemples ;
- le cadrage du ton ;
- les consignes sur le niveau d'explicitation.

## Ce que les testeurs doivent observer pendant les essais
Pour chaque échange, il est utile d'observer 4 niveaux.

### Niveau 1: qualité apparente de la réponse
Questions utiles:

- La réponse paraît-elle pertinente ?
- Fait-elle avancer la réflexion ?
- Évite-t-elle la redite ?
- Le ton est-il juste ?

### Niveau 2: qualité du diagnostic P0
Questions utiles:

- Hugo a-t-il bien compris si l'apprenant décrivait une action concrète ?
- A-t-il bien repéré s'il y avait un problème technique ou de sécurité ?
- A-t-il bien distingué description, analyse et projection ?
- A-t-il correctement perçu la charge cognitive ou le risque d'agacement ?

### Niveau 3: qualité de la décision conversationnelle
Questions utiles:

- Le bon geste pédagogique a-t-il été choisi ?
- Hugo aurait-il dû clarifier, analyser, problématiser, reformuler, clore ?
- Le nombre de questions est-il adapté ?
- Le système sort-il assez tôt des boucles de clarification ?

### Niveau 4: qualité de la formulation LLM
Questions utiles:

- Le backend avait-il raison, mais la formulation finale est faible ?
- Ou bien la formulation semble logique au regard d'une mauvaise décision en amont ?

## Comment formuler une proposition d'amélioration
Pour être exploitable, une remarque de test doit idéalement séparer:

- **ce que l'apprenant a dit**
- **ce que Hugo a répondu**
- **ce qui aurait été préférable**
- **où se situe probablement le problème**

Format conseillé:

1. **Situation testée**
   Résumer le message apprenant.

2. **Comportement observé**
   Décrire la réponse de Hugo.

3. **Diagnostic pédagogique**
   Expliquer pourquoi ce n'est pas satisfaisant.

4. **Hypothèse**
   Dire si le problème semble venir plutôt:
   - de la logique P0 ;
   - de la décision conversationnelle ;
   - du prompt ;
   - du référentiel injecté ;
   - ou d'un mélange de ces éléments.

5. **Proposition**
   Donner une règle ou une consigne plus adaptée.

## Aide au diagnostic: logique ou prompt ?

### Symptôme: Hugo répète des questions déjà couvertes
Probable côté logique:

- `has_concrete_actions` mal évalué ;
- `episode_clarity` sous-estimé ;
- anti-boucle pas assez fort ;
- `last_tutorial_move` ou `sticky_has_concrete_actions` insuffisamment exploités.

Probable côté prompt:

- le prompt reformule trop mécaniquement une consigne de clarification.

### Symptôme: Hugo reste vague malgré un cas technique précis
Probable côté logique:

- `tech_representation_level` trop bas ;
- `technical_criterion_focus` mal détecté ;
- `safety_or_quality_risk_level` sous-estimé.

Probable côté prompt:

- le prompt ne force pas assez l'ancrage sur un critère ou une tension métier.

### Symptôme: Hugo devient trop prudent trop tôt
Probable côté logique:

- `cognitive_load` ou `interaction_risk` sur-détectés ;
- seuils ou patterns trop sensibles.

Probable côté prompt:

- formulation trop prudente même quand la décision backend autorise davantage.

### Symptôme: Hugo pose une bonne question, mais n'accompagne pas assez
Probable côté logique:

- `should_encourage`, `should_recap`, `should_reframe` non activés alors qu'ils devraient l'être.

Probable côté prompt:

- le prompt n'exploite pas assez les consignes d'accompagnement.

## Réglages runtime du classifieur P0
Le classifieur P0 est configurable avec une cascade:

- **session**
- sinon **groupe**
- sinon **settings**

Paramètres principaux:

- `p0_classifier_enabled`
- `p0_classifier_max_tokens`
- `p0_classifier_min_confidence`
- `p0_classifier_max_input_chars`

Presets actuellement disponibles:

- `safe`
- `balanced`
- `aggressive`

Interprétation simple:

- `safe`: plus prudent, moins de surclassement par le LLM ;
- `balanced`: compromis actuel ;
- `aggressive`: le LLM a plus de place et plus de chances d'influencer P0.

## Quand proposer une amélioration de logique
Il vaut mieux proposer une amélioration de logique quand:

- un même type de cas produit régulièrement une mauvaise orientation ;
- la mauvaise décision apparaît avant même la génération de texte ;
- plusieurs prompts différents produiraient probablement le même défaut ;
- le problème concerne l'évolution de phase, la sortie de boucle, la détection du risque, la profondeur réflexive, ou la mobilisation d'actions concrètes.

Exemples:

- "Dès qu'un apprenant mentionne une action technique précise et un incident, on devrait sortir plus vite de `clarify`."
- "Un message court mais très situé devrait pouvoir être classé `episode_clarity = medium`."
- "Un indice de sécurité explicite devrait augmenter plus souvent `safety_or_quality_risk_level`."

## Quand proposer une amélioration de prompt
Il vaut mieux proposer une amélioration de prompt quand:

- la décision backend semble bonne ;
- mais la formulation n'est pas assez pédagogique, chaleureuse, précise, ou située ;
- ou quand Hugo n'utilise pas correctement les éléments déjà fournis par le backend.

Exemples:

- "Quand `pedagogical_move = analyze`, le prompt pourrait demander une reformulation brève avant la question."
- "Quand un critère technique est disponible, le prompt pourrait demander un ancrage explicite dans l'opération décrite."
- "Quand `need_encouragement = true`, le prompt devrait forcer une première phrase de validation."

## En pratique: ce qu'il faut remonter après un test
Pour chaque cas important, il est utile de remonter:

- le message apprenant ;
- la réponse de Hugo ;
- si possible le `turn_state` ;
- si possible la `conversation_decision` ;
- votre lecture pédagogique ;
- votre suggestion de correction ;
- l'endroit pressenti: logique, prompt, ou les deux.

## Idée simple à garder en tête
P0 n'est pas une vérité pédagogique.

C'est une **hypothèse de lecture de la situation** faite par le système pour éviter que le LLM improvise seul sa stratégie.

La bonne question pour les testeurs n'est donc pas:

**"Est-ce que la variable est techniquement exacte ?"**

mais plutôt:

**"Est-ce que cette variable aide Hugo à faire le bon prochain pas pédagogique ?"**

## Résumé en une phrase
P0 est le mécanisme qui transforme un message apprenant en lecture pédagogique structurée, afin que Hugo choisisse une meilleure stratégie de dialogue avant même de rédiger sa réponse.
