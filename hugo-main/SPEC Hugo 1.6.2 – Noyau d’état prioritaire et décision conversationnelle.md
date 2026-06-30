
***

# SPEC Hugo 1.6.2 – Noyau d’état prioritaire et décision conversationnelle

**Audience** : CTO, dev backend, architecte data, responsable produit.
**Statut** : cadrage technique – annule et remplace la partie « modèle d’état et signaux » de Hugo 1.6, sans modifier les invariants AFEST / sécurité / repo‑first.[^2]

## 1. Objet

Hugo 1.6.2 confirme le positionnement d’Hugo comme **moteur de régulation tutorale piloté par état**, et non comme simple générateur de prochaine question, mais **priorise** un noyau réduit de variables d’état directement actionnables.[^3][^4][^2]

L’objectif est triple :

- rendre l’implémentation du runtime réaliste à court terme (Mistral 4B/7B + backend existant) ;
- faciliter la calibration et les tests A/B ;
- garder ouvertes les extensions prévues en 1.6 (mémoire thématique, contradiction, verbatim interne gouverné, profils de tuteur).[^5][^2]

Les invariants AFEST, confidentialité‑first, multi‑tenant RLS, RAG non dominant, choix d’un seul objectif de régulation par message, restent inchangés.[^2][^5]

***

## 2. Invariants conservés

Les points suivants restent **strictement identiques** à Hugo 1.6 :

- **Posture AFEST** :
    - Hugo reste un tuteur réflexif, non magistral, sans jugement ni validation autonome.[^5][^2]
- **Règle conversationnelle** :
    - 1 objectif de régulation par message ;
    - 1–N questions brèves possibles si elles servent le même micro‑objectif ;
    - fallback automatique à 1 seule question simple en cas de risque relationnel ou de charge cognitive élevée.[^2]
- **Mémoire hybride gouvernée** :
    - learnerstate et mémoires thématiques comme base durable ;
    - verbatim interne chiffré, non loggé, non exposé, mobilisable de façon bornée pour contradiction/ambiguïté/rappel d’épisode ;
    - RAG documentaire comme renfort situé, jamais comme mémoire principale.[^5][^2]
- **Sécurité / confidentialité** :
    - multi‑tenant strict (organisationid, RLS) ;
    - partage opt‑in des synthèses, preuves, verbatim ;
    - aucun log de hugomessage.content, prompts complets, texte brut de chunks RAG ou de verbatim interne.[^2][^5]
- **Repo‑first** :
    - SPEC > .cursorrules > docs > prompts ;
    - toute évolution du modèle d’état doit être répercutée dans les prompts et tests via le workflow existant.[^5][^2]

***

## 3. Noyau d’état prioritaire (P0)

Hugo 1.6.2 définit un **noyau P0** de variables d’état utilisées dès la v1 du nouveau moteur. Les autres champs de 1.6 passent en P1 (logging/expérimentation) ou backlog, sans être interdits.[^2]

Les blocs suivants sont stockés dans analysisstate / conversationstate / learnermodel / decisionstate, mais avec des noms et niveaux bornés.

### 3.1 Bloc situation / épisode

- **episode_clarity** ∈ {low, medium, high}
    - Clarté globale de la situation racontée (qui fait quoi, où, quand, avec quels enjeux).
    - Remplace et agrège : situationclarity, timelineclarity.[^2]
- **has_concrete_actions** ∈ {true, false}
    - Indique si des actions, décisions et observations concrètes sont décrites (vs discours général).
    - Dérivé de actionconcreteness.[^2]
- **problem_salience** ∈ {none, low, high}
    - Importance apparente d’un problème, d’un écart, d’un dilemme ou d’une difficulté dans l’épisode.
    - Agrège hasdifficulty, hassurprise, gaptype.[^1][^2]


### 3.2 Bloc métacognitif / réflexif

- **reflection_phase** ∈ {description, analysis, projection}
    - Focalisation dominante du tour : décrire, analyser, se projeter dans l’action future.[^1]
- **reflective_depth** ∈ {low, medium, high}
    - Profondeur de mise en mots des raisons d’agir, critères, prises d’information.[^6][^2]
- **self_efficacy_signal** ∈ {low, neutral, high}
    - Estimation de la confiance perçue de l’apprenant dans sa capacité à faire face à la situation.[^7][^8][^1]


### 3.3 Bloc socio‑affectif / relationnel

- **affect_valence** ∈ {negative, neutral, positive}
    - Tonalité émotionnelle globale du tour.[^8][^9][^2]
- **cognitive_load** ∈ {low, medium, high}
    - Estimation de la charge cognitive/saturation du moment.[^10][^2]
- **interaction_risk** ∈ {low, medium, high}
    - Risque de tension relationnelle ou de rupture si le tuteur pousse trop fort.
    - Agrège risksignal, defensiveness, needreassurance.[^1][^2]


### 3.4 Bloc épistémique / ZPD

- **epistemic_balance** ∈ {tutor_more_expert, balanced, learner_more_expert}
    - Rapport perçu de savoir entre Hugo et l’apprenant sur la situation en cours.
    - Agrège epistemicgradient + domainauthoritybalance.[^2]
- **zpd_estimate** ∈ {below, in, beyond}
    - Position de la demande par rapport à la zone proximale de développement : trop facile, ajustée, trop difficile.[^11][^6][^2]


### 3.5 Bloc trajectoire de séance / parcours

- **session_phase** ∈ {opening, exploration, deepening, potential_closure}
    - Étape en cours dans la séance, pour séquencer les gestes macro.[^1][^2]
- **session_maturity** ∈ {low, medium, high}
    - Degré d’avancement global de la séance (combien a déjà été travaillé).[^2]
- **evidence_strength** ∈ {low, medium, high}
    - Solidité des éléments accumulés (situations, écarts, critères, pistes) pour soutenir une synthèse / auto‑évaluation.[^6][^1][^2]


### 3.6 Bloc décision locale

- **intervention_necessity** ∈ {none, low, high}
    - Degré de nécessité d’intervenir fortement maintenant (vs laisser respirer / reformuler brièvement).[^11]
- **contradiction_status** ∈ {none, suspected, under_check, resolved}
    - État simplifié de contradictioncase pour la décision locale.[^2]

***

## 4. Variables P1 (logging / expérimentation)

Les variables suivantes, présentes en 1.6, passent en P1 : loggées ou calculées, mais **non utilisées dans la logique de décision P0** tant qu’elles ne sont pas validées.[^2]

- memory_gap_detected
- pragmatic_issue_type détaillé
- opencontradictionids détaillés, reasoncodes fins
- lastmicroexplanationturn
- recurringpatterns, preferredprocessingstyle

Deux nouvelles variables introduites passent aussi en P1 pour l’instant :

- **language_support_needed** ∈ {low, medium, high}
    - Besoin d’aide langagière (simplification, reformulation).[^12][^13]
- **user_goal_clarity** ∈ {low, medium, high}
    - Clarté perçue de l’objectif de séance exprimé par l’apprenant.[^3][^1]

***

## 5. Politique de décision mise à jour (vue CTO)

Les règles conceptuelles de Hugo 1.6 sont conservées, mais formalisées avec le noyau P0.[^2]

### 5.1 Priorités hiérarchiques (rappel)

1. **Compréhension mutuelle \& cadrage**
2. **Accès à l’activité réelle**
3. **Problématisation \& analyse**
4. **Clôture / évaluation facultative**[^1][^2]

### 5.2 Règles P0 (pseudo‑code de haut niveau)

1. **Clarification / cadrage avant tout**
    - Si episode_clarity = low → geste = clarify (question simple) quel que soit le reste.
    - Si has_concrete_actions = false → geste = elicitaction (décrire ce que tu as fait…), pas d’analyse.
2. **Problématisation minimale avant analyse**
    - Si problem_salience = none \& reflection_phase = description → geste = problematisation légère (contrast / question de nud).
3. **Garde‑fous relationnels et cognitifs**
    - Si cognitive_load = high OU interaction_risk = high →
        - mode = singlequestion ;
        - geste ∈ {repair, reassure, pace, clarify} ;
        - pas de microexplain, pas de contrast direct.[^2]
4. **ZPD et micro‑explication**
    - Si zpd_estimate = in \& reflective_depth ∈ {medium, high} \& epistemic_balance ≠ learner_more_expert →
        - microexplain autorisé (1 phrase) ;
    - sinon, microexplain interdit, rester en mode questionnant.[^11][^2]
5. **Contradiction explicite**
    - Si contradiction_status = suspected ET episode_clarity ≥ medium →
        - geste = contrast léger, éventuellement déclenchement de verbatim retrieval sécurisé (si autorisé par flags et politique).[^2]
6. **Bilan / évaluation facultative**
    - Bilan possible seulement si :
        - session_phase = potential_closure,
        - session_maturity = high,
        - evidence_strength = high,
        - interaction_risk = low,
        - cognitive_load ≠ high.[^2]
7. **Nécessité d’intervention**
    - Si intervention_necessity = none →
        - geste = reformulation courte / validation / mini‑résumé, sans ouvrir de nouveau front ;
    - Si low → question courte, sans bouleverser le focus ;
    - Si high → appliquer les règles 1–4 pour choisir le geste prioritaire.[^11]

***

## 6. Impacts techniques

### 6.1 Analyse du tour (LLM local)

- Le module d’analyse (Mistral 4B ou 7B local) doit produire à chaque tour un JSON structuré contenant **au minimum les 16 variables P0**.[^14][^15]
- Les prompts d’analyse dans le backend sont à mettre à jour pour refléter la nouvelle liste et les nouvelles échelles.


### 6.2 Backend et schéma

- Les tables d’état existantes (analysisstate, conversationstate, learnermodel, decisionstate, themememory…) restent inchangées, mais certains champs :
    - sont marqués **P0** (utilisés par la logique de décision) ;
    - d’autres sont rétrogradés en P1 (logs, analytics).[^2]
- Aucune modification immédiate n’est requise sur le schéma POC, mais :
    - les champs inutilisés en P0 peuvent être rendus optionnels ;
    - les nouveaux champs (intervention_necessity, éventuellement user_goal_clarity, language_support_needed) sont à ajouter dans analysisstate / conversationstate si on souhaite les tracer.[^2]


### 6.3 Prompts et tests

- Le prompt SoT Hugo doit être mis à jour pour :
    - mentionner explicitement les gestes tutoraux supportés et la logique high‑level (priorités de régulation) ;
    - rester générique sur le détail des signaux (pas besoin de refléter toutes les variables P0 dans le texte).[^2]
- Les tests d’acceptation doivent vérifier :
    - le fallback singlequestion en cas de cognitive_load high ou interaction_risk high ;
    - les conditions minimales de micro‑explication ;
    - l’activation correcte de l’évaluation facultative selon session_maturity \& evidence_strength.[^2]

***

## 7. Plan d’implémentation recommandé (lot 1.6.2)

1. **Alignement modèle d’état**
    - Mettre à jour la doc interne pour refléter la liste P0/P1 ;
    - marquer les anciens champs 1.6 comme « legacy/expérimental » ou « P1 ».
2. **Mise à jour analyseur LLM**
    - Concevoir un prompt d’analyse unique produisant les 16 variables P0 ;
    - validation par quelques centaines de tours annotés manuellement.
3. **Implémentation de la décision P0**
    - Coder les règles 1–7 dans un module déterministe ;
    - exposer, pour audit, les valeurs P0 + geste/MODE choisis dans decisiontrace.[^2]
4. **Mise à jour des tests d’acceptation**
    - Ajouter des scénarios couvrant : clarification, offload, ZPD/microexplain, contradiction, bilan.
5. **Itérations P1**
    - Utiliser les champs P1 loggés pour analyser, a posteriori, les cas où le moteur se trompe, et décider quelles variables méritent d’entrer dans P0 v2.

***


***

## 8. Prompts de classification

### 8.1. Bloc situation / épisode

```text
Tu joues le rôle d’un classifieur.
À partir de la réponse de l’apprenant et du contexte donné, tu dois évaluer :

1. episode_clarity ∈ {low, medium, high}
- low : récit confus, peu de repères (qui, quoi, quand, où), chronologie floue.
- medium : on comprend globalement la scène mais certains éléments restent vagues.
- high : situation clairement décrite, avec acteurs, contexte, enchaînement d’actions.

2. has_concrete_actions ∈ {true, false}
- true : l’apprenant décrit des actions concrètes qu’il a réalisées (faire, dire, vérifier, décider…).
- false : discours surtout général, normatif, ou sans actions situées.

3. problem_salience ∈ {none, low, high}
- none : aucun problème, écart, dilemme ou difficulté n’apparaît.
- low : difficulté légère ou implicite, sans forte mise en avant.
- high : problème, surprise, dilemme ou difficulté clairement mis en avant.

Donne UNIQUEMENT une réponse JSON au format :
{
  "episode_clarity": "low|medium|high",
  "has_concrete_actions": true|false,
  "problem_salience": "none|low|high"
}

Contexte:
{{CONTEXT}}

Dernier message apprenant:
{{LEARNER_MESSAGE}}
```


***

### 8.2. Bloc métacognitif / réflexif

```text
Tu es un classifieur de comportement réflexif.

À partir de la réponse de l’apprenant, tu dois évaluer :

1. reflection_phase ∈ {description, analysis, projection}
- description : l’apprenant raconte surtout ce qui s’est passé, sans expliquer ni se projeter.
- analysis : il cherche à comprendre, expliquer, relier à des critères ou des causes.
- projection : il parle surtout de ce qu’il fera / pourrait faire à l’avenir.

2. reflective_depth ∈ {low, medium, high}
- low : peu ou pas de justifications, quasi pas de critères ou de prises d’information explicites.
- medium : quelques raisons, critères ou alternatives sont évoqués.
- high : raisons détaillées, critères explicites, mise en tension de plusieurs éléments.

3. self_efficacy_signal ∈ {low, neutral, high}
- low : il se dit peu capable, hésitant, en doute ou impuissant.
- neutral : il ne se prononce pas sur sa capacité, ton neutre.
- high : il exprime de la confiance, de l’aisance ou de la fierté.

Réponds UNIQUEMENT en JSON :
{
  "reflection_phase": "description|analysis|projection",
  "reflective_depth": "low|medium|high",
  "self_efficacy_signal": "low|neutral|high"
}

Dernier message apprenant:
{{LEARNER_MESSAGE}}
```


***

### 8.3. Bloc socio‑affectif / relationnel

```text
Tu es un classifieur d’état socio-affectif dans un tutorat.

À partir de ce message d’apprenant, évalue :

1. affect_valence ∈ {negative, neutral, positive}
- negative : émotions dominantes de colère, tristesse, peur, frustration, découragement.
- neutral : ton plutôt factuel, sans émotion marquée.
- positive : satisfaction, enthousiasme, fierté, soulagement.

2. cognitive_load ∈ {low, medium, high}
- low : l’apprenant semble à l’aise, ne signale ni surcharge ni confusion.
- medium : il signale une certaine difficulté mais reste fonctionnel.
- high : il se dit perdu, saturé, qu’« il y en a trop », ou montre une très forte confusion.

3. interaction_risk ∈ {low, medium, high}
- low : climat détendu, coopération, pas de défensive.
- medium : légers signes de malaise, d’agacement, de résistance.
- high : ton très défensif, repli, agacement marqué, risque de rupture de la conversation.

Réponse JSON uniquement :
{
  "affect_valence": "negative|neutral|positive",
  "cognitive_load": "low|medium|high",
  "interaction_risk": "low|medium|high"
}

Dernier message apprenant:
{{LEARNER_MESSAGE}}
```


***

### 8.4. Bloc épistémique / ZPD

```text
Tu es un classifieur de position épistémique et de difficulté.

À partir de ce message d’apprenant, évalue :

1. epistemic_balance ∈ {tutor_more_expert, balanced, learner_more_expert}
- tutor_more_expert : l’apprenant se présente comme novice ou peu expérimenté sur la situation.
- balanced : il ne se positionne pas clairement, ou comme « intermédiaire ».
- learner_more_expert : il affiche une forte expertise terrain ou une longue expérience.

2. zpd_estimate ∈ {below, in, beyond}
- below : ce qui est travaillé lui paraît trivial ou trop simple.
- in : c’est difficile mais gérable, il peut progresser avec un soutien adapté.
- beyond : il exprime que c’est beaucoup trop difficile ou hors de portée.

Réponds en JSON :
{
  "epistemic_balance": "tutor_more_expert|balanced|learner_more_expert",
  "zpd_estimate": "below|in|beyond"
}

Dernier message apprenant:
{{LEARNER_MESSAGE}}
```


***

### 8.5. Bloc trajectoire de séance / parcours

Ici tu peux mixer calcul serveur (compteur de tours) + un LLM si tu le souhaites, mais un prompt global reste possible.

```text
Tu es un classifieur de trajectoire de séance de tutorat.

Tu reçois :
- un résumé très court de la séance jusqu’ici,
- le dernier message de l’apprenant.

Évalue :

1. session_phase ∈ {opening, exploration, deepening, potential_closure}
- opening : on installe le cadre, l’objectif, la situation.
- exploration : on explore une ou plusieurs situations sans aller très en profondeur.
- deepening : on analyse finement un ou deux nœuds importants.
- potential_closure : on commence à récapituler, faire bilan, se projeter.

2. session_maturity ∈ {low, medium, high}
- low : peu de tours, peu de matière travaillée.
- medium : une ou deux situations déjà travaillées.
- high : plusieurs cycles complets ont eu lieu, la séance est « mûre ».

3. evidence_strength ∈ {low, medium, high}
- low : peu ou pas de situations/écarts/critères explicités.
- medium : quelques éléments mais encore incomplets.
- high : au moins une situation bien décrite, des écarts nommés, des critères ou pistes clairs.

Réponds seulement :
{
  "session_phase": "opening|exploration|deepening|potential_closure",
  "session_maturity": "low|medium|high",
  "evidence_strength": "low|medium|high"
}

Résumé séance:
{{SESSION_SUMMARY}}

Dernier message apprenant:
{{LEARNER_MESSAGE}}
```


***

### 8.6. Bloc décision locale

```text
Tu es un classifieur qui aide un tuteur numérique à décider s’il doit beaucoup intervenir ou non.

À partir :
- des états déjà estimés,
- et du dernier message apprenant,

tu dois fixer :

1. intervention_necessity ∈ {none, low, high}
- none : la situation est stable, claire, sans problème urgent ; une simple reformulation ou validation suffit.
- low : une petite relance ou clarification est utile, mais sans ouvrir un nouveau gros chantier.
- high : il y a un problème ou un blocage qui justifie une intervention tutorale forte maintenant.

2. contradiction_status ∈ {none, suspected, under_check, resolved}
- none : pas de contradiction apparente avec ce qui a été dit avant.
- suspected : possible contradiction ou changement de version à vérifier plus tard.
- under_check : une contradiction est en cours d’exploration.
- resolved : la contradiction repérée a été levée.

Tu reçois les états actuels sous forme JSON, ne les recalcule pas, utilise-les.

Réponds uniquement en JSON :
{
  "intervention_necessity": "none|low|high",
  "contradiction_status": "none|suspected|under_check|resolved"
}

États actuels:
{{STATE_JSON}}

Dernier message apprenant:
{{LEARNER_MESSAGE}}
```


***

## 9. Exemple d’états AVANT / APRES décision

### 9.1. Exemple d’état AVANT décision

```json
{
  "session_id": "sess_abc123",
  "turn_id": "t_042",
  "learner_id": "learner_001",
  "analysisstate": {
    "episode_clarity": "medium",
    "has_concrete_actions": true,
    "problem_salience": "high",

    "reflection_phase": "analysis",
    "reflective_depth": "medium",
    "self_efficacy_signal": "low",

    "affect_valence": "negative",
    "cognitive_load": "medium",
    "interaction_risk": "medium",

    "epistemic_balance": "balanced",
    "zpd_estimate": "in",

    "session_phase": "exploration",
    "session_maturity": "medium",
    "evidence_strength": "medium",

    "intervention_necessity": "high",
    "contradiction_status": "none"
  },
  "conversationstate": {
    "last_tutor_move": "clarify",
    "last_tutor_mode": "singlequestion",
    "theme_id": "theme_incident_client",
    "turn_count": 9
  },
  "learnermodel": {
    "style": "verbose",
    "directivetolerance": "medium",
    "needsreassurance": true
  }
}
```


***

### 9.2. Exemple d’état APRÈS décision

```json
{
  "session_id": "sess_abc123",
  "turn_id": "t_042",
  "decisionstate": {
    "primary_goal": "support_analysis_safely",
    "tutorial_move": "analyze",
    "directive_level": "medium",
    "mode": "singlequestion",
    "target_question_count": 1,
    "questionbundling_allowed": false,
    "microexplain_allowed": true,
    "use_themememory": true,
    "use_verbatim_retrieval": false,
    "use_overlay_first": true,
    "use_rag": false,
    "optional_evaluation_eligible": false,
    "reason_codes": [
      "problem_salience_high",
      "episode_clarity_medium",
      "zpd_in",
      "reflective_depth_medium",
      "interaction_risk_medium"
    ]
  }
}
```

