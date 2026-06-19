
## 1. Orchestrateur diagnostic

### Bloc D1 — Mission, type de questions, style de conduite

- **Source** : LOT 3 multi‑postures, template diagnostic.[^1]
- **Extrait** :
    - Mission : “aider l’apprenant à explorer une situation professionnelle, identifier ce qui s’est passé, cartographier les causes possibles et formuler les points à creuser. Tu ne poses pas de diagnostic à sa place. Tu l’aides à poser le sien”.[^1]
    - Posture : curieux, questionnant, n’aboutit pas lui‑même à une conclusion ; explore avant d’analyser ; aide à nommer plutôt qu’à valider ; ne fait jamais cours, ne juge pas.[^1]
    - Logique de questionnement : priorité à la clarification ; si situation floue → une seule question de clarification ; si situation claire → une question centrée sur causes/facteurs ; jamais deux thèmes dans la même question ; pas de questions rhétoriques.[^1]
- **Domaine** : orchestrateur diagnostic.
- **Ce que ça précise** :
    - **Objectif** : rendre la situation intelligible, faire émerger le “bon” problème et les hypothèses, sans substituer le jugement de l’orchestrateur à celui de l’apprenant.[^1]
    - **Règles de conduite** : très questionnant, structurant, mais non magistral ; clarifier avant d’analyser ; une seule question thématiquement cohérente par tour ; pas de verdict.[^1]
    - **Entrées** : situation professionnelle décrite par l’apprenant, phase de séance, maturité, teaching plan du tour (focus compétence, geste tutoriel, points couverts / ouverts, chunks RAG éventuels).[^1]
    - **Sorties** : réponse courte (2–4 phrases max), pas de liste, une question (deux si contrat l’autorise), pas de conclusion ni d’évaluation.[^1]
    - **Dépendances** : teachingplan, session_phase, session_maturity, RAG “appuis documentaires” quand disponible.[^1]
    - **Effets UI** (implicites) : indication claire qu’on est en “Diagnostic”, affichage de la phase et de la maturité, visibilité du nombre de questions autorisées.[^1]
- **Ambiguïté** : niveau de directivité maximal tolérable (jusqu’où peut aller la structuration des hypothèses) n’est pas chiffré ni formalisé au niveau de P0.[^1]
- **Lecture à privilégier** : orchestrateur diagnostic avec directivité modérée mais structure forte, restant subordonné aux garde‑fous P0 (charge, risque, ZPD).[^2][^1]
- **Pourquoi** : les templates insistent sur exploration et nommage sans jugement ni cours, tandis que le modèle décisionnel impose prudence, micro‑explication limitée et contrôle du nombre de questions.[^2][^1]
- **Ce qu’il manque pour finaliser la spec** :
    - seuils de maturité chiffrés pour dire quand le diagnostic est “suffisant” ;
    - protocole concret de sortie de diagnostic (vers réflexif, ou vers évaluation) au niveau orchestration.

***

### Bloc D2 — Signaux de maturité, conditions d’entrée / maintien / sortie

- **Source** : contextualisation 1.9 (LOT 1 progression, LOT 3 postures).[^2]
- **Extrait** :
    - ConversationProgress calcule maturité globale RED/ORANGE/GREEN, branches actives, dispersion_risk, priority_branch_id et éligibilité synthèse/évaluation, avec reasoncodes.[^2]
    - LOT 3 ajoute ConversationPosture avec DIAGNOSTIC, reflexif, knowledge_review, postureselector, posturetransitions, endpoint set‑posture, intégration des contraintes de posture dans orchestrateur et rendu.[^2][^1]
- **Domaine** : orchestrateur diagnostic + P0.
- **Ce que ça précise** :
    - **Conditions d’entrée** :
        - signaux P0 d’épisode flou (episode_clarity low), absence d’actions concrètes, peu de branches actives, phase opening/exploration.[^2][^1]
        - OU override explicite via endpoint de posture en début de séance.[^1]
    - **Maintien** : tant que les reasoncodes montrent un besoin de clarification et que la maturité n’atteint pas un seuil permettant de basculer en réflexif ou vers une autre phase.[^2][^1]
    - **Sortie** : lorsque la branche principale devient mûre (maturité ORANGE/VERTE selon définition diag) et que P0 considère qu’il est pertinent d’entrer en compréhension réflexive ou d’ouvrir une phase suivante.[^2]
    - **Signaux de maturité** :
        - au moins “problème nommé” (palier orange) puis “cause plausible confirmée” (palier vert) dans la logique diag (formulé dans la synthèse du fil).[^3]
- **Ambiguïté** : la frontière exacte entre “assez clarifié pour basculer en réflexif” et “ encore du diagnostic à faire” n’est pas formalisée (pas de règle pseudo‑algorithmique unique dans les docs).[^3][^2]
- **Lecture à privilégier** : P0 + ConversationProgress + PostureSelector coopèrent : PostureSelector décide le mode sur base d’état P0 + progression, P0 garde la main sur micro‑décisions de conduite.[^3][^2][^1]
- **Pourquoi** : LOT 3 décrit PostureSelector comme lecture des sorties P0 et de la progression, sans modifier decideconversation ; P0 reste intact.[^1]
- **Ce qu’il manque pour finaliser la spec** :
    - matrice explicite “phase / problème nommé / cause confirmée / charge / risque → maintien ou bascule” ;
    - mapping clair dans UIState pour rendre visible “diagnostic encore en cours vs assez avancé pour passer à autre chose”.

***

## 2. Orchestrateur réflexif (mode historique)

### Bloc R1 — Objectif, type de relance, logique de mise en sens

- **Source** : contextualisation 1.9 (doctrine conversationnelle), cadrage 1.6 (moteur réflexif), SoT historique sous‑entendue dans LOT 3 (hugo_reflective_afest_v1).[^3][^2][^1]
- **Extrait** :
    - Doctrine : posture réflexive, un seul objectif de régulation par message, question simple par défaut, plusieurs questions brèves possibles si cohérentes, fallback single‑question en cas de charge ou de risque, pas de cours magistral ni de jugement, pas de boucle absurde.[^2]
    - Gestes tutoraux : repair, reassure, pace, clarify, elicitaction, analyze, bilan, microexplain, contrast.[^3]
- **Domaine** : orchestrateur réflexif.
- **Ce que ça précise** :
    - **Objectif** : aider l’apprenant à prendre du recul, comprendre ce qui s’est passé, formuler un sens et dégager des pistes d’action, dans la filiation du moteur réflexif historique.[^3][^2]
    - **Type de relances** : questions de clarification, de mise en perspective, d’analyse, de bilan partiel, parfois de mise en contraste, assorties éventuellement de micro‑explication très courte.[^3]
    - **Logique** :
        - priorité à la clarté de l’épisode et à la description concrète ;
        - ensuite analyse de ce qui est significatif (saillance du problème) ;
        - puis mise en perspective (ZPD, transfert, bilan) quand maturité suffisante.[^3][^2]
    - **Niveau de guidage** : étayage progressif, pas de pilotage directif fort comme en révision ; vise l’autonomisation réflexive plutôt qu’un résultat “correct”.[^3]
- **Ambiguïté** : le contenu complet du SoT réflexif v1 n’est pas reproduit dans ce fil, même si sa logique est décrite (mission, posture, formats, interdits).[^1]
- **Lecture à privilégier** : orchestrateur réflexif comme héritier direct du Hugo cœur, les autres modes étant des spécialisations plus ciblées sur diagnostic ou contenus.[^2][^3]
- **Pourquoi** : contextualisation 1.9 et la hiérarchie de vérité le posent comme posture historique, inchangée, avec P0 gelé.[^2]
- **Ce qu’il manque pour finaliser la spec** :
    - texte complet du SoT v1 pour vérifier la cohérence point par point ;
    - règles explicites de passage en mode bilan vs “réflexif en cours”.

***

### Bloc R2 — Conditions d’entrée / maintien / sortie, synthèse/bilan

- **Source** : contextualisation 1.9 (mode, decisionstate, optionalevaluationeligible), cadrage 1.6.[^3][^2]
- **Extrait** :
    - decisionstate inclut `mode`, `optionalevaluationeligible`, `usethemememory`, `useoverlayfirst`, etc.[^2]
    - Politique de décision locale : clarifier avant d’analyser, micro‑explication bornée, pas de bilan avant maturité de séance suffisante.[^2]
- **Domaine** : orchestrateur réflexif + P0.
- **Ce que ça précise** :
    - **Entrée** : mode par défaut quand aucun signal fort de diagnostic ou de révision ne domine, et quand la séance est déjà engagée dans l’analyse / mise en sens.[^3][^2]
    - **Maintien** : tant que la séance n’a pas atteint un niveau de maturité et de stabilité suffisants pour passer au bilan ou à une évaluation ; tant que les questions restent de type compréhension et mise en sens.[^2]
    - **Sortie** :
        - soit vers une phase de bilan/synthèse ;
        - soit vers une évaluation facultative (si `optionalevaluationeligible` true) ;
        - soit vers un retour ponctuel au diagnostic si une contradiction forte ou une incompréhension majeure surgit.[^3][^2]
    - **Synthèse/bilan** : formes de synthèse centrées sur ce que l’apprenant retient, comment il se repositionne, quelles pistes il identifie ; forme à dominante textuelle, potentiellement utilisable comme trace ou capsule.[^3]
- **Ambiguïté** : la distinction exacte entre “bilan réflexif” et “évaluation” n’est pas formalisée comme deux orchestrateurs distincts dans ce fil (l’évaluation reste décrite comme geste/branche).[^3][^2]
- **Lecture à privilégier** : orchestrateur réflexif conserve un geste de bilan interne ; l’orchestrateur d’évaluation apprenant est un régime terminal plus normatif construit au‑dessus.[^3]
- **Pourquoi** : le texte insiste sur l’évaluation comme facultative, bornée, non autonome, avec seuils d’éligibilité plus stricts que la synthèse ; cela fait de la synthèse réflexive un artefact distinct.[^2][^3]
- **Ce qu’il manque pour finaliser la spec** :
    - spécification détaillée du format d’une “capsule réflexive” vs “trace d’évaluation” ;
    - règles d’appel à `synthesisservice` (présent dans LOT 3) en mode réflexif.

***

## 3. Orchestrateur bûchage / révision (knowledge review)

### Bloc B1 — Objectif, logique d’entraînement, style d’interaction

- **Source** : LOT 3 templates knowledge_review, contextualisation 1.9.[^1][^2]
- **Extrait** :
    - Mission : aider l’apprenant à explorer, mémoriser, consolider des contenus de savoir (concepts, règles, procédures, réglementation) ; poser des défis, demander des rappels, signaler lacunes/erreurs, apporter des micro‑explications courtes.[^1]
    - Posture : pédagogue, patient, centré contenu ; peut expliquer brièvement ; peut proposer un défi ou une question de rappel ; ne fait pas de cours magistral ; ne juge pas.[^1]
    - Logique de questionnement : priorité au rappel avant explication ; en cas de lacune confirmée → micro‑explication (1 phrase) puis question de consolidation ; si contenu maîtrisé → question de niveau supérieur ou défi ; jamais de listes de cours ; pas plus d’une explication par tour.[^1]
- **Domaine** : orchestrateur bûchage / révision.
- **Ce que ça précise** :
    - **Objectif** : consolidation de savoirs via rappels actifs, défis et corrections légères, sans basculer en mode cours.[^1]
    - **Logique d’entraînement** :
        - cycles rappel → vérification → micro‑explication → consolidation ;
        - adaptation du niveau de difficulté selon estimation de maîtrise ;
        - usage intensif du teaching plan et des contenus de référence.[^2][^1]
    - **Style d’interaction** : plus directif côté contenu que le réflexif, mais toujours borné en longueur et en ton ; interaction centrée sur questions précises, micro‑explications, corrections.[^1]
    - **Place des micro‑explications** : autorisées explicitement (contrairement au réflexif où elles sont exceptionnelles), mais limitées en longueur (1 phrase) et en fréquence (max une par tour).[^1]
- **Ambiguïté** : la granularité d’un “exercice” n’est pas formalisée (pas de description d’items types, de scoring ou de séries).[^3]
- **Lecture à privilégier** : orchestrateur de révision sans mécanisme d’exercices complexes (QCM multi‑items) dans ce fil ; on reste dans des tours de conversation enrichis de défis et de rappels.[^3]
- **Pourquoi** : rien dans ces documents ne décrit un système d’exercices structuré type LMS ; tout reste formulé en termes de tours conversationnels.[^2][^3]
- **Ce qu’il manque pour finaliser la spec** :
    - spec d’un mini‑langage d’exercices si tu en veux un ;
    - règles de progression de difficulté plus détaillées (par ex. niveaux, nombre d’essais, etc.).

***

### Bloc B2 — Conditions d’entrée / maintien / sortie, signaux de maîtrise

- **Source** : contextualisation 1.9, synthèse du fil.[^2][^3]
- **Extrait** :
    - Mode révision autorise étayage contenu plus fort mais reste piloté par état, ZPD, directivité acceptable, garde‑fous anti‑magistraux ; maturité verte lorsque l’apprenant formule une règle de transfert ou un acquis nommé.[^3]
    - LOT 3 curseurs posture_cursors incluent `knowledge_support_bias`, `rag_aggressiveness`, etc., avec valeurs élevées en knowledge_review.[^1]
- **Domaine** : orchestrateur bûchage / révision + P0.
- **Ce que ça précise** :
    - **Entrée** :
        - cas où du contenu disponible (available_material high) et knowledge_support_bias élevé ;
        - probable déclenchement principalement lorsque la tâche est moins centrée sur compréhension d’une expérience et plus sur maîtrise de notions/règles.[^3][^1]
    - **Maintien** : tant que les signaux de maîtrise ne sont pas au vert (pas encore de formulation claire de ce qui est retenu) et que la charge/risk restent acceptables.[^2][^3]
    - **Sortie** : quand l’apprenant peut formuler ce qu’il retient, une règle ou un principe, ce qui correspond à un seuil de maturité spécifique (vert) pour ce mode.[^3]
    - **Signaux de progression** :
        - réussite aux défis ;
        - rappels corrects ;
        - expression autonome de règles ;
        - stable dans ConversationProgress (même branche).[^2][^3]
- **Ambiguïté** : pas de métrique explicite (nombre minimal de tours de révision, proportion de réponses justes, etc.).[^3]
- **Lecture à privilégier** : orchestrateur révision plus “dense” en micro‑explications et contenu, mais s’appuyant sur la même progression de branches/maturité que le réflexif.[^2][^3]
- **Pourquoi** : ConversationProgress et UIState ne distinguent pas de type d’exercices, seulement des branches, maturité, éligibilité synthèse/évaluation.[^2]
- **Ce qu’il manque pour finaliser la spec** :
    - typologie de “critères de maîtrise” consommables par cet orchestrateur ;
    - mapping UI plus précis pour montrer les progrès en révision (barres, badges, etc.).

***

## 4. Orchestrateur évaluation apprenant

### Bloc E1 — Statut, conditions d’activation, maturité, sorties

- **Source** : contextualisation 1.9, cadrage 1.6, synthèse du fil.[^3][^2]
- **Extrait** :
    - Évaluation facultative de fin de scénario, déclenchable seulement si la séance est suffisamment mûre, si risque relationnel et charge cognitive sont faibles, si une base structurée est exploitable, et sans transformer Hugo en évaluateur autonome.[^2][^3]
    - `optionalevaluationeligible` dans le contrat de décision ; état d’éligibilité calculé distinct de la synthèse.[^3][^2]
- **Domaine** : orchestrateur évaluation (apprenant) + P0.
- **Ce que ça précise** :
    - **Statut exact** : orchestrateur ou protocole terminal spécialisé, distinct des trois régimes de conduite principaux mais réutilisant la même charpente P0/TutorPrompt/mémoire.[^3]
    - **Conditions d’activation** :
        - maturité de séance élevée (vert) ;
        - faible charge cognitive et faible risque relationnel ;
        - présence de mémoire structurée (traces, synthèses, référentiel/règles) suffisante pour que l’évaluation ait du sens.[^2][^3]
    - **Conditions de maturité** : plus exigeantes que pour une simple synthèse ; l’évaluation n’est “disponible” que lorsque la conversation a suffisamment couvert les points pertinents.[^3]
    - **Différences disponible / déconseillée / forcée** (implicites) :
        - disponible : eligible true, UI autorise le bouton ;
        - déconseillée : eligible false mais l’utilisateur pourrait forcer, avec avertissement ;
        - forcée : ce n’est pas décrit dans ce fil, mais ton cadre cible l’autoriserait éventuellement en tant qu’override humain.[^3]
    - **Sorties attendues** :
        - trace d’évaluation qui peut nourrir exports, pack Qualiopi, et validation humaine ultérieure ;
        - bilan positionné sur référentiel plutôt que conversation brute.[^2][^3]
    - **Articulation avec validation humaine** : rien ne passe “validé” sans validation humaine ; l’évaluation automatique reste un support, non une décision de certification.[^2]
- **Ambiguïté** : ce fil ne décrit pas explicitement un orchestrateur évaluatif complet (avec ses propres templates system/user), mais plutôt une branche ou protocole terminal ; la granularité des items et des feedbacks n’est pas spécifiée.[^3]
- **Lecture à privilégier** : orchestrateur dédié léger, principalement défini par ses critères d’éligibilité, ses formats de sortie et ses interactions avec validation humaine, réutilisant la logique de P0 (optionalevaluationeligible, reasoncodes).[^2][^3]
- **Pourquoi** : la doctrine insiste sur l’évaluation comme “facultative”, “vue/geste borné de fin de scénario” plutôt que quatrième posture principale sur le même plan que diagnostic/réflexif/révision, mais ton cadre imposé nous autorise à la formaliser comme orchestrateur spécialisé à partir de cette branche.[^3]
- **Ce qu’il manque pour finaliser la spec** :
    - templates system/user explicites pour le mode évaluation ;
    - description détaillée du format de la trace d’évaluation (structure JSON, champs, statut).

***

## 5. Rôle de P0 vis‑à‑vis des orchestrateurs apprenant

### Bloc P1 — Contrat P0, variables, décisions locales

- **Source** : contextualisation 1.9 (P0, décision locale, contrat de décision), cadrage 1.6.[^2][^3]
- **Extrait** :
    - P0 = 16 variables bornées (clarté épisode, actions concrètes, saillance problème, valence, charge, risque interactionnel, ZPD, phase séance, maturité, force des preuves, nécessité d’intervention, etc.).[^2]
    - Politique de décision : clarifier avant analyser, demander action réelle si absente, problématiser minimalement, protéger relation/cognition via single‑question, autoriser micro‑explication seulement sous conditions, gérer contradictions progressivement, n’ouvrir bilan qu’en séance mûre.[^2]
    - Contrat de décision : `primarygoal`, `tutorialmove`, `mode`, `targetquestioncount`, `questionbundlingallowed`, `microexplainallowed`, `usethemememory`, `useverbatimretrieval`, `useoverlayfirst`, `userag`, `optionalevaluationeligible`, `reasoncodes`.[^2]
- **Domaine** : P0 (pour les 4 orchestrateurs apprenant).
- **Ce que ça précise** :
    - **Ce que P0 régule localement** :
        - nombre et style de questions ;
        - droit à la micro‑explication ;
        - usage mémoire (thématique, verbatim, overlay, RAG) ;
        - éligibilité évaluation ;
        - prudence relationnelle (charge/risk → single‑question mode) ;
        - type de geste tutoriel (clarify, analyze, bilan, etc.).[^3][^2]
    - **Ce qu’il peut valider / refuser / ajuster** :
        - refuser des enchaînements trop agressifs (pas de double question si charge élevée) ;
        - refuser d’ouvrir une évaluation si les critères d’éligibilité ne sont pas réunis ;
        - ajuster le recours à la mémoire ou au RAG (useoverlayfirst, userag) ;
        - limiter ou autoriser micro‑explication selon mode et ZPD.[^2]
    - **Arbitrage des transitions** :
        - via `mode` et `optionalevaluationeligible`, en coopérant avec PostureSelector qui lit TurnState + ConversationProgress + curseurs de posture ;
        - P0 ne casse pas l’orchestrateur, mais borne les décisions tour par tour (garde‑fous).[^1][^3][^2]
    - **Remontée d’états au front** :
        - reasoncodes, éligibilité synthèse/évaluation, maturité, risque de dispersion, etc., via ConversationProgress/UIState plutôt que P0 brut.[^3][^2]
- **Ambiguïté** : la frontière “exactement ce qui relève de P0 vs de l’orchestrateur spécialisé” n’est pas découpée formellement ; P0 “ne change pas” dans LOT 3 mais il expose `mode` dans le contrat de décision.[^1][^2]
- **Lecture à privilégier** :
    - orchestrateurs spécialisés = logique haute de conduite (prompting, mission, type de questions, usage des contenus) ;
    - P0 = couche d’arbitrage bas niveau sur sécurité, charge, ZPD, éligibilité, micro‑explication, bundling.[^3][^2]
- **Pourquoi** : LOT 3 affirme explicitement que `analyzeturnstate`, `classifyp0turnstate` et `decideconversation` restent intacts, et que PostureSelector lit ces sorties sans les modifier.[^1]
- **Ce qu’il manque pour finaliser la spec** :
    - une matrice “décisions P0” par orchestrateur (diagnostic / réflexif / révision / évaluation) pour clarifier les marges de manœuvre ;
    - un schéma séquence montrant comment P0 et PostureSelector se parlent dans chaque mode.

***

## Synthèse Tour 1 — A. Orchestrateurs apprenant

### Ce que le fil permet de fixer

- **Diagnostic** :
    - Objectif clair (mettre à jour problème et causes plausibles, non poser un verdict).[^1][^3]
    - Conduite très structurée, centrée sur clarification et hypothèses ; questions uniques, non rhétoriques.[^1]
    - Conditions d’entrée lisibles (épisode flou, pas d’actions, phase d’ouverture/exploration, available_material pas déterminant).[^1][^2]
    - Signaux de maturité (problème nommé → cause confirmée).[^3]
- **Réflexif** :
    - Héritier du moteur historique, centré sur mise en sens, recul, bilan et transfert.[^2][^3]
    - Gestes tutoraux nommés ; micro‑explication rare ; priorité à l’expérience réelle et à la compréhension.[^3]
    - Bilan réflexif distinct de l’évaluation, même s’il peut produire des traces.[^3]
- **Bûchage / révision** :
    - Mission explicite : rappel, consolidation, défis, corrections, micro‑explications très courtes.[^1]
    - Style d’interaction plus contenu‑centré, avec règles précises sur micro‑explication et pas de cours.[^1]
    - Entrée guidée par available_material, knowledge_support_bias et teachingplan.[^1][^3]
- **Évaluation** :
    - Statut d’évaluation finale facultative, non autonome, avec conditions d’éligibilité strictes (maturité, charge, risque, base structurée).[^2][^3]
    - Connexion explicite à `optionalevaluationeligible` et reasoncodes, avec sortie sous forme de trace exploitable et validée humainement.[^2]


### Ce qui reste à préciser

- Diagnostic : seuils formels de sortie, mapping UIState complet pour rendre visibles les étapes du diag.
- Réflexif : spec exacte des templates system/user ; découpage clair entre “réflexif en cours” et “bilan réflexif”.
- Bûchage : mécanique d’exercices éventuels (ou confirmation explicite qu’on reste à la granularité “question/mini‑explication”).
- Évaluation : templates dédiés, structure de la trace d’évaluation, éventuelle notion d’évaluation “forcée”.

***

## Synthèse Tour 1 — D. Rôle de P0

### Ce qui est clair

- P0 est un **régulateur local** : il ne change pas entre lots, il reste la couche d’état borné (16 variables) qui alimente toutes les décisions de conduite.[^1][^2]
- P0 prend en charge :
    - nombre et forme des questions ;
    - autorisation d’expliquer ;
    - usage de mémoire \& RAG ;
    - éligibilité à la synthèse/évaluation ;
    - prudence relationnelle (charge/risk → single‑question).[^2]
- P0 fournit `mode` et `optionalevaluationeligible` dans decisionstate, ce qui le place au cœur des transitions entre régimes et de la protection contre les usages abusifs de l’évaluation.[^2]
- LOT 3 garantit que P0 reste inchangé dans son code et ses champs : les nouveaux comportements se branchent **autour** (PostureSelector, curseurs de posture, templates posture‑spécifiques).[^1]


### Ce qui reste ambigu

- La frontière exacte entre “choix de mode par P0” et “choix de mode par orchestrateur spécialisé/PostureSelector” n’est pas dessinée formellement ; on a des signaux et des règles, mais pas une spec de type machine à états explicite.[^1][^3][^2]
- La répartition fine “ce que P0 peut bloquer dans chaque orchestrateur” (par exemple empêcher l’orchestrateur de révision de dépasser une densité d’explications) n’est pas détaillée.[^3]

En l’état, le fil permet donc de fixer une doctrine solide : **orchestrateurs spécialisés** pour les 4 régimes apprenant, **P0** comme couche de régulation/garde‑fous/transitions au tour par tour, **ConversationProgress/UIState** comme médiateurs vers le front.[^1][^3][^2]

Souhaites‑tu que le Tour 2 se concentre directement sur **formateur + tuteur**, ou préfères‑tu qu’on traite d’abord les interfaces apprenant pour capitaliser sur ce qu’on vient de clarifier ?

<div align="center">⁂</div>

[^1]: LOT3_multi_postures_cursor-2.md

[^2]: CONTEXTUALISATION_COMPLETE_HUGO_1_9.md

[^3]: Contexte_Ce-fil-contient-des-elements-de-conceptio.md

