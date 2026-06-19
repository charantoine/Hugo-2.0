
# interfaces

Pour les interfaces, on peut déjà stabiliser pas mal de choses à partir de ce fil, surtout côté apprenant et formateur. Je te propose une première passe synthétique, centrée sur ce qui est fixé et ce qui manque encore.[^1][^2]

## Interface apprenant

### Structure visible de la conversation

- L’interface doit être construite à partir d’un **UIState propre** (et non des champs P0) qui expose au minimum : scène (phase de séance), progression, quête ou branche active, couleur de maturité, état des boutons synthèse/évaluation, objets persistants éventuels, profil d’engagement.[^2][^1]
- La scène suit une grammaire simple type “Raconter / Comprendre / Décider”, couplée à la **branch principale** et à la progression calculée (ConversationProgress : maturité RED/ORANGE/GREEN, priority_branch, dispersion_risk).[^1][^2]
- Le **mode actif** (diagnostic / réflexif / révision / évaluation) doit être perceptible : la présence de ConversationPosture, d’un endpoint `set-posture`, de postureselector et de posturetransitions implique un **état de posture affichable** côté UI.[^3][^2][^1]

En pratique, tu as donc au minimum, côté apprenant :

- un **panneau de progression** (HugoProgressPanel) lisant `/ui-state` ;
- un affichage de la **scène** (phase de séance) et de la **branche/objectif courant** ;
- un indicateur de **maturité** (code couleur ou label) ;
- un affichage du **mode** ou au moins de la posture (diagnostic / réflexif / révision).[^2][^3][^1]


### Commandes et contrôle utilisateur

- Un **sélecteur de posture**/mode est prévu : endpoint PATCH `/sessions/{id}/posture/`, bloqué après un certain nombre de messages et de phase (pas de changement en séance avancée).[^3]
- Les **actions terminales** (synthèse / évaluation) apparaissent comme boutons ou CTA dont l’état dépend de l’éligibilité calculée (via ConversationProgress + P0 `optionalevaluationeligible`).[^1][^2]
- La reprise de fil, bifurcation, clôture sont articulées sur le concept de **ConversationBranch** (branche principale, branches secondaires limitées, risque de dispersion).[^2][^1]

Ce qui est clair :

- L’apprenant peut **choisir une posture en début de fil**, dans des conditions sûres (phase d’ouverture, peu de messages).[^3]
- Il voit **s’il peut lancer une synthèse ou une évaluation** (boutons actifs/inactifs d’après /ui-state).[^1][^2]

Ce qui manque encore :

- La palette exacte d’actions “relance / reprise de fil / demande de bascule” n’est pas listée exhaustivement.
- Le statut visuel “déconseillé / forcé” pour l’évaluation est seulement suggéré (via notion d’éligibilité + reasoncodes) mais pas spécifié UI.


### Grammaire UI fine

- Le fil insiste sur une **structure front lisible** plutôt que sur des micro‑composants nommés, mais on voit émerger :
    - un **panneau de progression** (ProgressPanel) ;
    - des **labels de scène** et de **quête active** ;
    - des **boutons synthèse / évaluation** avec états (actif / grisé / caché) ;
    - des **objets persistants** dans UIState pour porter les éléments durables (mémos, capsules, traces à confirmer).[^2][^1]
- Il est explicitement interdit de montrer des **signaux techniques P0** (scores, variables internes) dans le front : UIState est le seul modèle produit montrable.[^1]
- Certains objets (mémoire thématique, verbatim interne, reasoncodes détaillés) doivent rester **implicites** pour l’apprenant, même si le moteur les utilise pour décider.[^2][^1]

En résumé, la grammaire UI apprenant doit rendre explicites :

- “où j’en suis” (scène, progression, branche active, maturité) ;
- “dans quel régime je suis” (diagnostic / réflexif / révision / évaluation) ;
- “ce que je peux faire maintenant” (parler, demander, synthétiser, évaluer) ;

…sans exposer P0 brut ni la mécanique interne de mémoire.

### Session memory — contrat minimal lot courant

Dans la trajectoire locale de convergence, la mémoire visible ou relisible dans l’expérience apprenant doit d’abord converger vers une mémoire gouvernée intra‑conversation, utile à la continuité du fil courant. Cette section décrit le contrat cible minimal de cette mémoire pour le lot courant ; elle ne prouve pas que toutes les rubriques sont déjà livrées dans le runtime local.

#### Principes

- La mémoire utile du fil courant est un résumé gouverné et non un verbatim brut.
- Elle est produite et mise à jour côté backend, puis projetée via UIState ou un objet dérivé ; le front ne la calcule jamais lui‑même.
- Elle sert à reprendre le thème actif, l’objectif, les faits établis, les points ouverts et les actions à venir, sans exposer la mécanique interne du moteur.
- Elle ne doit pas être décrite comme une mémoire inter‑sessions déjà active dans ce lot.

#### Contrat cible minimal

```json
{
  "session_memory": {
    "session_id": "<uuid>",
    "updated_at": "ISO datetime",
    "theme": {
      "label": "texte court lisible",
      "tags": ["string"]
    },
    "learning_objective": {
      "label": "objectif pédagogique courant",
      "status": "in_progress | reached | abandoned"
    },
    "facts_confirmed": [
      {
        "label": "fait ou décision confirmé dans le fil",
        "confirmed_at": "ISO datetime"
      }
    ],
    "open_points": [
      {
        "label": "question ou point encore ouvert",
        "priority": "normal | blocking"
      }
    ],
    "pending_actions": [
      {
        "label": "action à faire dans ce fil",
        "due_in_turns": 3
      }
    ],
    "memory_scope": "session"
  }
}
```

#### Interdits

- Ne jamais exposer de verbatim brut ou d’historique complet comme pseudo‑mémoire gouvernée.
- Ne jamais exposer de champs P0 bruts dans `session_memory` ou dans les blocs UI qui le consomment.
- Ne pas dériver un profil apprenant durable à partir de cette mémoire de fil dans le lot courant.
- Ne pas présenter `LearnerThemeMemory` comme équivalent direct de cette structure tant que l’audit code ne le prouve pas pour la conduite du tour courant.


### Évaluation côté apprenant

- L’évaluation est présentée comme une **action terminale facultative**, éligible seulement lorsque certains critères sont réunis (maturité séance, charge/risk, base structurée) : cet état d’éligibilité doit être reflété par l’UI (bouton d’évaluation activable vs inactif).[^1][^2]
- Le fil suggère implicitement trois états :
    - non éligible (bouton absent/grisé) ;
    - éligible (bouton actif, éventuellement avec message “possible maintenant”) ;
    - éligible mais **déconseillé** si l’utilisateur force malgré un warning (scénario évoqué dans ta doctrine cible, pas explicitement détaillé dans les docs).[^2]

Manques :

- pas de description formelle des messages de prudence (“c’est un peu tôt pour évaluer”) ;
- pas de code couleur précis (genre vert = recommandé, orange = possible mais déconseillé).

### CTA synthèse / évaluation — contrat minimal lot courant

Dans le lot courant, les actions terminales de synthèse et d’évaluation sont pilotées par le backend via des champs dédiés dans `ui_state`. Ce contrat vise à standardiser les états, les raisons de blocage et les endpoints associés, sans prétendre que toute la chaîne d’évaluation 2.0 est déjà livrée.

#### Principes

- Les CTA sont des **actions terminales facultatives** pour l’apprenant.
- L’**éligibilité** et les **raisons de blocage** sont calculées côté backend et projetées dans `ui_state`.
- Le front ne recalcule pas l’éligibilité : il lit `ui_state.cta_evaluation` et `ui_state.cta_synthesis` et affiche les boutons en conséquence.
- Aucune formulation produit ne doit laisser entendre que Hugo délivre une **certification autonome** : la validation finale reste humaine.

#### Contrat cible minimal (UIState)

```json
{
  "cta_evaluation": {
    "evaluation_ready_status": "eligible | blocked_missing_data | blocked_min_turns_not_reached | blocked_context_incomplete | blocked_other",
    "blocking_reasons": ["liste courte de raisons lisibles, non P0"],

    "endpoints": {
      "request_evaluation": "/api/hugo/sessions/{session_id}/request-evaluation/",
      "finalize_evaluation": "/api/hugo/sessions/{session_id}/finalize-evaluation/",
      "evaluation_readiness": "/api/hugo/sessions/{session_id}/evaluation-readiness/"
    },

    "ui": {
      "show_evaluation_button": true,
      "button_label": "Demander une évaluation",
      "button_disabled": false,
      "helper_text": null
    },

    "last_evaluation": {
      "status": "none | in_progress | completed | failed",
      "completed_at": "ISO datetime ou null"
    }
  },

  "cta_synthesis": {
    "synthesis_ready_status": "eligible | blocked_not_enough_content | blocked_context_incomplete",
    "blocking_reasons": ["liste courte de raisons lisibles, non P0"],

    "endpoints": {
      "generate_synthesis": "/api/hugo/sessions/{session_id}/generate-synthesis/"
    },

    "ui": {
      "show_synthesis_button": true,
      "button_label": "Obtenir une synthèse",
      "button_disabled": false,
      "helper_text": null
    }
  }
}
```

#### Contraintes

- Les champs `evaluation_ready_status` et `synthesis_ready_status` sont des **énums fermés**, pas des chaînes libres.
- `blocking_reasons` contient des messages lisibles destinés à l’apprenant, sans dumps techniques ni champs P0.
- Les endpoints listés sont les seules routes attendues pour les CTA de ce lot ; le front n’invente pas de nouvelles URLs ni de paramètres.
- Les textes définitifs (`button_label`, `helper_text`) peuvent varier, mais la structure et les états doivent rester conformes à ce contrat.

#### Effets côté front

- Bouton d’évaluation :
  - affiché si `cta_evaluation.ui.show_evaluation_button == true` ;
  - désactivé si `cta_evaluation.ui.button_disabled == true` ;
  - les messages d’aide proviennent de `cta_evaluation.ui.helper_text` ou, à défaut, d’une interprétation simple de `blocking_reasons`.
- Bouton de synthèse :
  - piloté de la même manière par `cta_synthesis.ui.*`.
- L’UI ne lit pas directement les endpoints d’évaluation ou les signaux P0 : elle passe par `ui_state.cta_*` uniquement.

***

## Interface formateur

### Vues et objets

- Le formateur manipule une **base de connaissances métier gouvernée**, avec des `TrainerKnowledgeItem` et un `documentingestor`, plus une **interface dialogique d’explicitation** (questionnaire où il raconte, explicite, structure).[^1][^2]
- Les **objets** sont marqués par statuts `declared`, `derived_provisional`, `validated_trainer`, avec l’interdiction explicite de passer à “validé” sans validation humaine.[^2][^1]
- Il voit :
    - documents importés ;
    - critères de maîtrise ;
    - erreurs fréquentes ;
    - raisonnements attendus ou à éviter ;
    - objets en attente de validation ;
    - structures référentielles/RAG prêtes à être exploitées par Hugo.[^1][^2]


### Actions

- Apporter des documents, expliciter des savoirs, structurer un référentiel, enrichir le matériau pédagogique, **valider / rejeter / corriger** des connaissances dérivées, rattacher des connaissances à des référentiels ou compétences, préparer des corpus utilisables par les orchestrateurs apprenant.[^2][^1]
- Configurer certains paramètres dans des bornes prévues (profils, processus, éventuellement curseurs) sans éditer la doctrine centrale ni les prompts SoT.[^2]


### Pilotage

- Le formateur peut orienter le système en **préparant le matériau** (documents, critères, erreurs, raisonnements) et en **validant** les connaissances que les orchestrateurs pourront exploiter en sécurité.[^1][^2]
- Il ne pilote pas la conversation apprenant au tour par tour, mais influence :
    - ce que les orchestrateurs de révision et d’évaluation peuvent utiliser ;
    - la qualité des suggestions ;
    - la couverture référentiel/critères.[^1][^2]

Manques sur l’interface formateur :

- L’ordre exact des écrans (workspace, tableau de validation, vue de lecture, panneau de configuration) n’est pas détaillé.
- On ne sait pas encore si le formateur voit des **capsules d’usage** montrant comment ses contenus ont été utilisés par les orchestrateurs.

***

## Interface tuteur

### Ce que le tuteur voit

- Il a une **vue de progression apprenant** construite sur ConversationProgress et UIState : branches, maturité, dispersion, état des actions terminales.[^2][^1]
- Il voit des **signaux gouvernés** : qualité de conversation (via future `ConversationQualitySignal`), traces, synthèses, évaluations, mais **pas le verbatim privé** non explicitement partagé.[^1][^2]
- Il devrait voir (doctrine) : état de séance, mode courant, maturité, besoins/difficultés déduits des signaux P0/Progress (par exemple blocages, dispersion, manque de preuves).[^2]


### Actions et limites

- Le tuteur peut **recommander des aménagements** des situations de travail, **suggérer des bascules de mode** ou des cadences différentes, préparer ou recommander une synthèse ou évaluation, mais sans accès libre au verbatim privé et sans pouvoir re‑piloter directement la conversation en place de l’apprenant.[^1][^2]
- Les accès sont **strictement filtrés** par le partage explicite : il ne voit que ce qui a été partagé comme synthèse, capsule, trace ou preuve.[^2][^1]

Manques sur l’interface tuteur :

- La différence exacte de vue entre tuteur et formateur n’est pas listée point par point (par exemple, tuteur ne manipule pas la base de connaissances, seulement les traces de conversation).
- La palette précise de commandes tuteur (“recommander une bascule”, “demander une synthèse”, “ajouter un commentaire pédagogique”) n’est pas décrite.

***

## Granularité présente vs manquante

- **Présent** :
    - architecture de front basée sur `/ui-state` + `/progress` ;
    - invariants de confidentialité (verbatim privé, partage explicite, pas de P0 brut) ;
    - existence d’un sélecteur de mode côté apprenant, d’une progression lisible, de boutons synthèse/évaluation dépendants de l’état serveur ;
    - base formateur gouvernée avec statuts et validation humaine ;
    - vues tuteur basées sur signaux et traces partagées.[^3][^1][^2]
- **Manquant ou sous‑spécifié** :
    - maquettes logiques plus fines (composition exacte du ProgressPanel, des bandeaux de mode, des cartes d’état) ;
    - messages UI pour l’évaluation (déconseillée / forcée) ;
    - chorégraphie détaillée des workflows formateur et tuteur (ordre des écrans, interactions fines) ;
    - découpe explicite des droits tuteur vs formateur vs orgadmin dans l’UI métier.

Si tu veux, on peut maintenant prendre une des interfaces (apprenant, formateur ou tuteur) et la pousser au niveau “quasi‑maquette logique” : sections, blocs, états UI détaillés, en restant fidèle à cette matière. Laquelle tu veux approfondir en premier ?

<div align="center">⁂</div>

[^1]: CONTEXTUALISATION_COMPLETE_HUGO_1_9.md

[^2]: Contexte_Ce-fil-contient-des-elements-de-conceptio.md

[^3]: LOT3_multi_postures_cursor-2.md

