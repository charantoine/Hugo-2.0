
# SPEC canonique Hugo 2.0

## 0. Statut du document

Ce document est la **spec canonique 2.0 propre** de Hugo cœur. Il consolide le cadrage projet, les lots structurants, les clarifications doctrinales du fil, et les précisions sur les orchestrateurs formateur et tuteur, sans relire une cible comme un état livré.

Ce document doit être utilisé comme **porte d’entrée de travail** pour la suite de la conception, de l’audit et des prompts d’implémentation. Il décrit l’état **spécifié** et l’état **cible consolidé**, pas une preuve d’implémentation observée.

> **Statut runtime local (2026-06-18)** — voir `rapport_mise_a_jour_doc_post_cluster16_2026-06-18.md` : UIState, CTA (dont advisory), mémoire intra API + panneau, posture/scène/profils apprenant = **implémentation partielle PARTIEL+** (clusters 15–16). Le reste de cette spec reste **CIBLE** tant qu’il n’est pas raccordé explicitement dans la matrice V5.

## 1. Objet

Hugo 2.0 est un moteur tutoriel **réflexif** multi-postures, piloté par état, centré apprenant, construit sur un backend Django orchestré, avec TutorPrompt comme pivot runtime, un noyau P0 de régulation locale, une mémoire gouvernée, et une couche produit dérivée d’états serveur plutôt que d’une logique conversationnelle portée par le front.

Le multi-postures ne doit pas être compris comme une juxtaposition de bots distincts ni comme un empilement de prompts. Il s’agit de plusieurs régimes conversationnels spécialisés opérant sur une charpente commune : backend Django orchestré, régulation par état via P0, TutorPrompt, mémoire gouvernée, confidentialité-first et front dérivé des états.

## 2. Périmètre

Le périmètre de cette spec est **Hugo cœur**. Il couvre le moteur conversationnel, les objets d’état, les régimes conversationnels, la mémoire gouvernée, la base de connaissances formateur, les surfaces tuteur/formateur nécessaires, les exports, les garde-fous de sécurité et les états front montrables.

Ne relèvent pas de cette spec canonique : les extensions de type constellation d’assistants, une administration produit entièrement détaillée de tous les rôles, ou une interface métier finale exhaustivement maquettée quand le corpus ne la fixe pas encore.

## 3. Règle de lecture

Cette spec doit toujours être lue en distinguant :
- ce qui est explicitement spécifié ;
- ce qui est consolidé à partir de plusieurs documents ;
- ce qui reste ouvert ou sous-spécifié ;
- ce qui relèvera ensuite d’une vérification code / produit / runtime.

Elle ne doit jamais être utilisée pour prétendre qu’une fonctionnalité est livrée parce qu’elle est décrite. Inversement, elle fixe ce que les futurs audits et chantiers doivent comparer au réel.

## 4. Terminologie canonique

Le vocabulaire canonique 2.0 est le suivant :
- **régime conversationnel** : politique globale de conduite de séance ;
- **posture active** : valeur runtime qui indique le régime actuellement actif ;
- **geste tutoral** : mouvement local de conduite à l’intérieur d’un régime ;
- **P0** : noyau de régulation locale par état ;
- **contrat de décision** : sortie structurée de décision locale ;
- **progression conversationnelle** : état persistant de branches, maturité et conditions de clôture ;
- **UIState** : traduction produit montrable des états internes.

Les ambiguïtés anciennes entre profil, posture, mode et geste doivent être lues ainsi : le **régime conversationnel** est de niveau global ; le **geste tutoral** est de niveau local ; le front ne produit pas ces états mais les restitue et déclenche seulement des actions bornées.

## 5. Principes non négociables

Les invariants de Hugo 2.0 sont :
- backend Django orchestré ;
- TutorPrompt comme pivot runtime ;
- P0 conservé et enrichi additivement ;
- logique moteur gouvernée côté backend ;
- front dérivé d’états produit propres ;
- mémoire gouvernée, structurée, non assimilable à un historique brut ;
- confidentialité-first, partage explicite, multi-tenant strict ;
- aucune exposition libre du verbatim non partagé.

Le système ne doit ni devenir un enseignant magistral, ni un évaluateur autonome, ni un moteur de validation humaine, ni un outil qui contourne la séparation entre logique moteur, surface produit et données sensibles.

## 6. Architecture cible

Le runtime conversationnel cible suit une chaîne stable en six temps :
1. construction du contexte ;
2. analyse du tour apprenant ;
3. décision tutorale locale ;
4. rendu du prompt via TutorPrompt ;
5. appel LLM ;
6. post-traitement, garde-fous, journalisation technique et persistance.

La source de vérité comportementale n’est pas le prompt seul. Elle résulte de la combinaison entre la spec, l’orchestrateur backend, TutorPrompt, le contexte structuré de session, les profils ou curseurs de conduite, la progression conversationnelle, la mémoire gouvernée et les règles de sécurité produit.

## 7. Noyau P0

Le P0 reste le régulateur local commun de Hugo 2.0. Les régimes spécialisés modulent le comportement autour de lui mais ne dupliquent ni le pipeline principal ni la logique de décision locale.

Le noyau P0 doit rester fondé sur un état borné couvrant au moins la clarté de l’épisode, les actions concrètes, la saillance du problème, la phase réflexive, la valence affective, la charge cognitive, le risque interactionnel, la balance épistémique, la ZPD estimée, la phase de séance, la maturité de séance, la force des preuves, la nécessité d’intervention et le statut de contradiction.

À partir de cet état, Hugo doit au minimum :
- clarifier avant d’analyser si l’épisode est flou ;
- demander l’action réelle si elle n’est pas concrète ;
- protéger relation et cognition par fallback mono-question en cas de charge ou risque élevés ;
- autoriser une micro-explication uniquement sous conditions ;
- gérer les contradictions progressivement ;
- n’ouvrir la synthèse ou l’évaluation qu’à maturité suffisante.

## 8. Contrat de décision

Le moteur doit produire un contrat de décision structuré contenant au moins :
- objectif primaire ;
- geste tutoral principal ;
- mode ou régime actif ;
- nombre cible de questions ;
- autorisation éventuelle de bundling ;
- autorisation éventuelle de micro-explication ;
- usage de mémoire thématique ;
- usage de récupération verbatim interne ;
- priorité éventuelle d’un overlay référentiel ;
- usage éventuel du RAG ;
- éligibilité éventuelle à une évaluation ;
- reason codes traçables.

Ce contrat fait le lien entre la régulation locale, la progression, le choix de posture, le rendu prompt, et les états restitués au produit. Il ne doit pas être contourné par des décisions frontales ou par des raccourcis d’implémentation.

## 9. Doctrine conversationnelle commune

Hugo 2.0 reste un moteur tutoriel réflexif : un seul micro-objectif de régulation par message, une question simple par défaut, et plusieurs questions seulement si elles restent très brèves, non redondantes, et au service du même objectif local.

Le système ne fait pas cours, ne juge pas, n’impose pas une analyse prématurée et ne maintient pas des boucles absurdes. En situation fragile, ambiguë ou cognitivement chargée, il revient à une conduite plus légère, plus sûre et plus focalisée.

## 10. Régimes conversationnels principaux

Hugo 2.0 comporte trois régimes conversationnels principaux sur runtime commun :
- réflexif ;
- diagnostic ;
- révision de savoirs.

Ces régimes ne sont pas de simples variantes de ton. Ils correspondent à des politiques distinctes de questionnement, de recours au contenu, de directivité, de micro-explication, de clôture et de maturité conversationnelle, tout en partageant le même squelette backend et les mêmes garde-fous.

### 10.1 Régime réflexif

Le régime réflexif est le régime historique de Hugo, renommé dans le vocabulaire canonique 2.0. Il vise l’élucidation d’une situation vécue, la mise en mots d’un apprentissage situé, la progression réflexive, puis éventuellement une synthèse ou une évaluation facultative lorsque la séance devient suffisamment mûre.

### 10.2 Régime diagnostic

Le régime diagnostic vise à clarifier une situation-problème, faire émerger le problème utile, nommer des causes plausibles et orienter le travail suivant, sans que Hugo pose le diagnostic à la place de l’apprenant.

Il est plus structurant et plus hypothetico-vérificatif que le régime réflexif. Il priorise la clarification de situation avant l’analyse, interdit de valider une hypothèse non formulée par l’apprenant et limite fortement toute dérive magistrale.

### 10.3 Régime révision de savoirs

Le régime révision de savoirs sert à explorer, consolider ou réviser un contenu conceptuel, procédural, réglementaire ou opératoire, avec plus d’étayage contenu que le régime réflexif, sans devenir un bot de cours.

Ce régime doit faire rappeler avant d’expliquer, n’autoriser qu’une micro-explication brève par tour, puis revenir à une question de consolidation, de vérification ou de défi. Si le contenu est déjà maîtrisé, il doit monter en niveau plutôt que répéter un contenu élémentaire.

### 10.4 Évaluation facultative

L’évaluation n’est pas un quatrième régime principal. Elle doit être lue comme une branche terminale spécialisée, facultative, de fin de scénario, soumise à des conditions strictes de maturité, de sécurité relationnelle et d’exploitabilité des bases structurées.

Elle peut préparer une trace, un auto-positionnement ou un objet partageable, mais la validation finale reste humaine. Le produit ne doit jamais laisser croire que Hugo certifie seul un niveau ou une compétence.

## 11. Distinction entre régime et geste tutoral

Les gestes tutoraux locaux ne doivent pas être confondus avec les régimes conversationnels. Les régimes définissent la politique de séance ; les gestes pilotent la conduite locale à l’intérieur d’un régime.

La taxonomie locale comprend au moins réparer, rassurer, rythmer, clarifier, faire émerger l’action, analyser, micro-expliquer, contraster et faire bilan. Ces gestes peuvent rester principalement internes et ne sont pas destinés à être tous frontalisés comme des modes explicites.

## 12. Sélection de posture active

La posture active doit être déterminée par un service dédié de sélection, en lecture des sorties P0 et de la progression conversationnelle, sans modifier le cœur de la décision locale existante.

Une seule posture globale est active par tour. Une sélection explicite de session peut primer en début de séance, puis le backend maintient ou ajuste la posture selon les règles de transition autorisées.

Les signaux minimaux de sélection incluent notamment la clarté de l’épisode, la présence d’actions concrètes, le nombre de branches actives, la phase de séance, la saillance du problème, la disponibilité de matière documentaire, et les curseurs de conduite stockés côté TutorPrompt (metadata ou overrides bornés).

## 13. TutorPrompt 2.0

TutorPrompt reste le pivot runtime de configuration. Les variations de conduite doivent prioritairement passer par lui et par des overrides bornés, avec priorité de sélection session puis groupe puis organisation puis fallback legacy si nécessaire.

Chaque régime principal doit disposer de son propre couple de templates versionnés system / user, tout en gardant le même renderer, le même contexte de rendu, et le même contrat de décision injecté.

Les templates spécialisés doivent exprimer clairement mission, posture, protocole d’ouverture, logique de questionnement, usage du teaching plan, règles de confidentialité, format de sortie et interdits propres au régime.

Les curseurs de comportement doivent être portés dans TutorPrompt.metadata ou des overrides bornés, et non enfouis dans le texte du prompt. Ils modulent les seuils de conduite sans modifier la doctrine de fond.

## 14. Progression conversationnelle

La bonne unité de progression produit n’est pas le seul dernier tour mais une branche conversationnelle couplant au minimum un thème (ou une situation) et un objectif pédagogique actif.

La conversation peut comporter une branche prioritaire, des branches secondaires limitées, un risque de dispersion, un niveau de maturité global, des conditions de synthèse, des conditions d’évaluation, et des éléments manquants pour le niveau suivant.

Le moteur doit calculer et persister une structure de progression contenant au moins : branches actives, branche prioritaire, maturité globale (rouge/orange/vert), dispersion risk, missing for next level, reason codes, éligibilité synthèse et éligibilité évaluation.

## 15. UIState et traduction produit

Le front ne doit jamais consommer TurnState ou les champs bruts P0. Il doit consommer un UIState propre, dérivé côté backend, compréhensible produit, et stable côté interface.

Ce UIState doit exposer au minimum : scène visible, progression, quête active, couleur de maturité, posture active si le produit l’expose, état des actions de synthèse, état des actions d’évaluation, et objets persistants visibles ou confirmables.

La grammaire visible côté apprenant doit rester simple et non technique. Elle doit rendre perceptible où l’on en est, ce qu’on cherche, ce qui manque encore et quelles actions sont possibles, sans jamais exposer la mécanique brute du moteur.

## 16. Front conversationnel

Le front de Hugo 2.0 doit rendre visible la progression conversationnelle de manière montrable. À partir du moment où UIState, ConversationProgress, un panneau de progression et des actions terminales sont prévus, il ne s’agit plus d’un front quasi inchangé.

Le front doit pouvoir permettre ou afficher :
- la scène de séance ;
- la posture active ou le régime de conduite selon le niveau d’explicitation retenu ;
- la branche prioritaire ;
- le niveau de maturité ;
- les actions terminales disponibles ;
- certains objets persistants ou mémoires à confirmer ;
- les transitions de posture si elles sont exposées à l’utilisateur.

Doivent rester cachés ou implicites : les champs P0 bruts, les prompts complets, les variables de debug, le verbatim interne non partagé et les traces sensibles non explicitement partageables.

## 17. Mémoire gouvernée

La mémoire de Hugo 2.0 doit être thématique, structurée, gouvernée, référentiel-first et extensible par thèmes émergents. Elle ne doit pas être confondue avec un historique brut de conversation.

L’ordre de récupération du contexte doit suivre une logique priorisée de type : état apprenant, mémoire thématique, verbatim interne ponctuel si nécessaire, overlay référentiel, puis documentaire en renfort situé.

Le verbatim interne ne peut être qu’un outil de récupération borné pour contradictions, ambiguïtés persistantes ou rappels ciblés. Il ne doit jamais devenir la mémoire principale ni une surface librement consultable par un humain hors partage explicite.

La consolidation mémoire inter-session doit être post-conversation, gouvernée backend, stockée dans une structure dédiée, sans verbatim brut et sans auto-promotion d’un statut provisoire vers un statut validé humainement.

## 18. Référentiel, documentaire et RAG

Le référentiel métier reste central pour orienter la couverture, la structuration des traces et les overlays de groupe. Il ne doit pas être remplacé par une logique documentaire pure.

Le RAG reste question-driven, centré sur les documents actifs du contexte de formation, et utilisé comme renfort situé. Il ne doit devenir ni une mémoire principale, ni un moteur de cours.

La base de connaissances formateur validée peut enrichir ce socle documentaire gouverné, mais sans court-circuiter la logique référentielle ni la validation humaine.

## 19. Base de connaissances formateur

Hugo 2.0 doit comporter une base de connaissances formateur gouvernée, construite par ingestion documentaire et explicitation dialogique, produisant des items structurés exploitables par les orchestrateurs apprenant.

Cette base doit permettre de capter au moins des documents source, des règles, des critères de maîtrise, des erreurs fréquentes, des raisonnements attendus, des raisonnements à éviter, et des liens au référentiel, aux compétences, aux situations et aux tâches.

Les objets centraux sont des `TrainerKnowledgeItem` ou équivalents, avec statut explicite, type, contenu, rattachements référentiels, provenance et métadonnées d’usage documentaire ou RAG.

## 20. Orchestrateur formateur

L’orchestrateur formateur est un orchestrateur spécialisé distinct des régimes apprenant. Il sert à faire élaborer, expliciter, structurer et valider le savoir métier utile au système, au moyen d’un questionnaire dialogique et d’une ingestion documentaire gouvernée.

Il ne s’agit pas d’un simple formulaire d’admin. C’est un dialogue d’élaboration transformant des matériaux métier hétérogènes en items de connaissance structurés, prêts à être validés puis consommés par les orchestrateurs apprenant.

## 21. Statuts de connaissance

Les statuts de connaissance doivent distinguer au minimum :
- déclaré ;
- dérivé provisoire ;
- validé humainement.

Aucun item dérivé ne doit passer automatiquement au statut validé humainement. Toute promotion vers un statut validé doit résulter d’un acte explicite d’un rôle habilité dans le produit.

La base de connaissances formateur n’est pas la source primaire de vérité réglementaire. Elle reste subordonnée au référentiel métier et à la validation humaine.

## 22. Orchestrateur tuteur

Hugo 2.0 doit aussi comporter une couche tuteur orientée lecture de progression, détection de besoins, compréhension des blocages et préparation d’actions d’accompagnement humain, sans pilotage direct du moteur conversationnel apprenant.

Cette couche tuteur consomme les objets de progression, les signaux de qualité conversationnelle, les synthèses et les traces partageables pour produire des aides à l’interprétation, des recommandations d’accompagnement et des suggestions de moments pertinents pour synthèse ou évaluation.

Le tuteur ne doit pas avoir accès au verbatim non partagé, ni au contrôle direct du P0, ni à un forage libre des orchestrateurs apprenant au niveau serveur. Son rôle est d’accompagner, recommander, lire, commenter et valider certaines traces partageables dans la réalité de travail.

## 23. Observabilité et qualité conversationnelle

Le système 2.0 doit prévoir des signaux de qualité conversationnelle et des vues cohorte, sans tomber dans un scoring opaque ou une lecture désincarnée des apprenants.

Le corpus permet déjà de fixer la fonction de ces signaux : progression par branche, maturité, dispersion, reason codes et autres indicateurs de qualité, à formaliser ensuite dans un catalogue canonique plus fin.

## 24. Confidentialité, partage et multi-tenant

Le verbatim est privé par défaut. Toute visibilité pour des rôles non apprenant doit passer par un partage explicite distinct pour synthèse, preuves ou verbatim, selon le niveau d’ouverture autorisé par le produit.

Le multi-tenant strict implique une isolation complète par organisation, avec RLS active et absence de lecture-écriture inter-tenant. Cette contrainte fait partie de la spec produit et non d’un simple choix d’infrastructure.

Les rôles non apprenant, y compris tuteur, formateur, coordinateur, org admin et superadministration technique, ne doivent jamais disposer d’un accès libre au contenu apprenant non partagé.

## 25. Rôles

Le produit doit au minimum distinguer les rôles suivants : apprenant, tuteur, formateur, coordinateur, administrateur d’organisation et superadministration technique.

Les capacités exactes d’administration métier sur comptes, rattachements et écrans complets restent partiellement ouvertes dans le corpus actuel. En revanche, la séparation des responsabilités, la confidentialité et l’interdiction d’une lecture libre du contenu apprenant par l’administration sont déjà clairement fixées.

## Matrice canonique des rôles et usages pour les tests

Cette section ne redéfinit pas la doctrine des rôles de Hugo 2.0.
Elle fixe un point d’ancrage unique pour les protocoles de test, afin
d’éviter que des droits implicites ou contradictoires soient introduits au fil
des scénarios.

### Rôle de la matrice dans les tests

Tout protocole de test Hugo 2.0 qui implique un rôle non-apprenant
(tuteur, formateur, coordinateur, administrateur d’organisation,
superadministration technique) doit :

- déclarer explicitement le rôle testé dans sa section « Rôle testé » ;
- se référer à la définition du rôle dans cette section de la spec canonique ;
- considérer comme échec tout comportement qui contredit les garde-fous
  de confidentialité-first, de partage explicite et de multi-tenant strict
  déjà fixés ici.

En particulier :

- aucun rôle non-apprenant ne doit disposer d’un accès libre au contenu
  apprenant non partagé ;
- aucun rôle ne doit consommer les champs P0 ou TurnState bruts via le front ;
- aucune lecture ou écriture inter-tenant ne doit être possible.

Toute évolution de ces droits doit être traitée comme une décision
documentaire explicite, et non comme un « effet de bord » d’un protocole
de test ou d’un front isolé.

## 26. Exports et preuves

Le produit doit pouvoir produire des exports structurés, notamment CSV et JSON, ainsi que des traces et preuves rattachées à une session ou une trace, avec règles de confidentialité adaptées.

Les preuves photo doivent être gérées avec suppression EXIF par défaut et GPS opt-in. Toute preuve doit rester attachée à un contexte explicite et ne jamais flotter librement hors gouvernance métier.

## 27. Règles d’implémentation transverses

Les règles techniques transverses à respecter en 2.0 sont au minimum :
- aucun champ P0 existant modifié sans nécessité majeure ;
- enrichissement additif ;
- enums canoniques centralisées ;
- stockage des enums Django via `.value` ;
- reconstruction depuis JSONB via désérialisation explicite ;
- pas d’usage brut des objets JSON lorsqu’ils contiennent enums ou structures imbriquées ;
- UIState sans champs P0 ;
- consolidation mémoire et analytics post-conversation ;
- aucun auto-upgrade d’un état dérivé provisoire vers un état validé humainement.

Ces règles constituent le filtre principal pour distinguer une implémentation correcte d’un assemblage fragile ou approximatif.

## 28. Ce que Hugo 2.0 ne doit pas faire

Hugo 2.0 ne doit pas :
- recréer une architecture parallèle au backend Django existant ;
- multiplier les pipelines LLM indépendants hors charpente commune ;
- exposer les champs P0 au front ;
- utiliser le verbatim brut comme mémoire principale ;
- transformer la base de connaissances formateur en vérité automatique ;
- laisser croire que l’évaluation finale est autonome ;
- faire du front le pilote réel de la conduite tutorale.

## 29. Matrices canoniques

### 29.1 Matrice des couches

| Couche | Rôle | Source de vérité | Ce qui y vit | Ce qui n’y vit pas |
|---|---|---|---|---|
| Doctrine produit | Fixer le cadre global | Spec canonique + cadrage consolidé [file:230][file:333] | invariants, sécurité, posture générale, frontières produit [file:230] | logique front ad hoc non spécifiée [file:230] |
| P0 | Régulation locale par état | backend moteur [file:230] | état borné, décision locale, garde-fous, fallback mono-question [file:230] | UIState, verbatim exposable, logique métier formateur [file:230][file:333] |
| Régime conversationnel | Politique globale de séance | posture active + TutorPrompt + progression [file:290][file:333] | sélection de régime, templates spécialisés, curseurs de conduite [file:290] | pipeline LLM séparé, duplication du P0 [file:290] |
| Progression conversationnelle | Lisibilité inter-tours | ConversationProgress [file:230][file:333] | branches, maturité, dispersion, éligibilité synthèse/évaluation [file:230] | champs techniques bruts de P0 [file:230] |
| Traduction produit | Rendu montrable | UIState [file:230][file:333] | scène, quête active, couleur de maturité, CTA terminales, objets persistants [file:333] | debug moteur, prompts complets, verbatim non partagé [file:230][file:333] |

### 29.2 Matrice des régimes conversationnels

| Régime | Finalité | Politique dominante | Type d’aide autorisé | Condition de sortie | Effets UI attendus |
|---|---|---|---|---|---|
| Réflexif | Élucider une situation vécue et en faire émerger l’apprentissage [file:230][file:333] | exploration située, progression réflexive [file:230] | questionnement, reformulation, micro-explication bornée si nécessaire [file:230] | maturité suffisante pour synthèse ou évaluation facultative [file:230][file:333] | scène lisible, quête active, progression, CTA de synthèse/évaluation si éligible [file:333] |
| Diagnostic | Clarifier un problème et nommer des causes plausibles [file:333][file:290] | clarification avant analyse, hypothèses formulées par l’apprenant [file:290] | questionnement structurant, pas de validation d’hypothèse externe [file:290] | problème nommé puis cause plausible suffisamment confirmée [file:333] | posture visible, objectif courant, progression orientée problème → cause [file:333] |
| Révision de savoirs | Consolider ou réviser un contenu sans faire cours [file:333][file:290] | rappel actif avant explication, consolidation, défi [file:290] | micro-explication très brève, vérification, défi progressif [file:290] | acquis nommé, règle de transfert ou maîtrise plus haute [file:333] | objectif d’apprentissage explicite, suivi de ce qui est retenu [file:333] |
| Évaluation facultative | Produire une trace terminale bornée de fin de scénario [file:333] | branche terminale, non permanente [file:333] | auto-positionnement, trace structurée, préparation d’export [file:333] | validation humaine finale [file:333][file:344] | état locked/possible/ready, raisons d’éligibilité ou blocage [file:333] |

### 29.3 Matrice des objets de domaine

| Objet | Rôle | Producteur principal | Consommateurs principaux | Exposition front |
|---|---|---|---|---|
| TurnState | État brut local du tour [file:230] | pipeline moteur/P0 [file:230] | décision locale, posture selector, renderer [file:290] | non [file:230] |
| Contrat de décision | Sortie structurée de régulation locale [file:230] | P0 / décision locale [file:230] | renderer, progression, traces, services de posture [file:230][file:290] | non brut, seulement via traduction produit [file:230] |
| ConversationBranch | Unité de progression thématique/pédagogique [file:230][file:333] | calcul de progression [file:230] | UIState, synthèse, évaluation, tuteur [file:333][file:344] | oui, sous forme traduite [file:333] |
| ConversationProgress | État inter-tours de progression [file:230] | calculator dédié [file:230] | UIState, synthèse, évaluation, tuteur, analytics [file:230][file:344] | indirectement via UIState ou vues dédiées [file:230] |
| UIState | Traduction produit montrable [file:230][file:333] | adaptateur backend [file:230] | front learner, tutor, trainer [file:333][file:344] | oui [file:230] |
| LearnerThemeMemory | Mémoire thématique inter-session [file:230] | consolidation post-conversation [file:230] | moteur apprenant, résumés mémoire, synthèse [file:333] | oui, uniquement sous forme gouvernée [file:333] |
| TrainerKnowledgeItem | Item de savoir métier gouverné [file:344][file:230] | orchestrateur formateur [file:344] | RAG gouverné, moteurs apprenant, validation humaine [file:344] | oui côté formateur, pas brut côté apprenant [file:344] |
| EvaluationTrace | Trace terminale structurée [file:333] | branche d’évaluation [file:333] | apprenant, tuteur, exports, validation humaine [file:333][file:344] | oui si partageable [file:333] |
| EvaluationTrace pivot (`evaluation_trace_pivot_v1`) | Agrégat JSON minimal local — session, record, trace, preuves | `evaluation_trace_pivot.py`, generate-trace, ExportRun JSON | exports encadrants, lecture trace | non UIState apprenant ; **≠ EvaluationTrace 2.0 complète** |
| ConversationTurnLLMAnalysis (D9bis) | Analyse dérivée par tour — sans verbatim | build D9bis SUPERADMIN | export QA/ops | **non** — canal technique |
| ConversationLLMAnalysis (D9bis) | Agrégat session analytics | idem | export QA/ops | **non** — canal technique |
| PersistentObjects | Conteneur produit d’objets durables visibles [file:333] | backend produit / synthèse / mémoire [file:333] | front, exports, vues métier [file:333] | oui [file:333] |

### 29.4 Matrice des services backend

| Service | Fonction | Entrées minimales | Sorties minimales | Contraintes |
|---|---|---|---|---|
| Analyse du tour | Produire l’état borné local [file:230] | message apprenant, contexte, session [file:230] | TurnState [file:230] | pas de logique front, pas d’exposition directe [file:230] |
| Décision locale | Arbitrer le tour courant [file:230] | TurnState, contexte, règles runtime [file:230] | contrat de décision [file:230] | P0 intact, garde-fous actifs [file:230] |
| PostureSelector | Choisir le régime actif [file:290] | TurnState, décision, progression, override éventuel, curseurs [file:290] | posture active + reason codes [file:290] | lecture seule des sorties P0, pas de duplication du pipeline [file:290] |
| PromptRenderer | Charger les templates adaptés et injecter le contexte [file:290] | TutorPrompt, posture active, contexte de rendu [file:290] | system prompt + user prompt [file:290] | fallback sécurisé vers le régime réflexif si nécessaire [file:290] |
| ProgressionCalculator | Calculer la progression de séance [file:230] | historique, branches, décisions, session [file:230] | ConversationProgress [file:230] | désérialisation explicite, pas d’usage brut JSONB [file:230] |
| UIStateBuilder | Traduire la progression en état produit [file:230][file:333] | ConversationProgress + objets produit [file:230] | UIState [file:230] | aucun champ P0 brut [file:230] |
| MemoryConsolidator | Consolider la mémoire utile inter-session [file:230] | traces structurées post-conversation [file:230] | LearnerThemeMemory [file:230] | pas de verbatim brut, pas d’auto-upgrade [file:230] |
| DocumentIngestor / orchestrateur formateur | Transformer documents et explicitation en savoir gouverné [file:344][file:230] | documents, réponses formateur, référentiel [file:344] | TrainerKnowledgeItem dérivés [file:344] | validation humaine obligatoire avant statut validé [file:344][file:230] |
| SynthesisService | Produire une synthèse structurée [file:230][file:333] | progression, branches, mémoire utile, traces partageables [file:333] | synthèse partageable [file:333] | pas de fuite de données sensibles [file:230] |
| QualityTracker | Produire des signaux de qualité conversationnelle [file:230][file:344] | progression, traces structurées, métriques [file:230] | ConversationQualitySignal / indicateurs cohorte [file:230] | pas de scoring opaque, post-conversation ou vue agrégée [file:344] |

### 29.5 Matrice des endpoints et actions serveur minimales

| Endpoint / action | Rôle | Utilisateur / surface | Réponse attendue | Garde-fou |
|---|---|---|---|---|
| `POST /sessions/{id}/messages` | Envoyer un tour apprenant | apprenant [file:290][file:230] | message, session sérialisée, posture active, états dérivés pertinents [file:290] | accès session contrôlé, logique moteur backend [file:290][file:230] |
| `PATCH /sessions/{id}/posture` | Demander une posture active en début de séance [file:290] | apprenant, éventuellement surface guidée [file:333] | posture active, changement appliqué ou refus motivé [file:290] | refus si séance trop avancée, journalisation obligatoire [file:290] |
| `GET /sessions/{id}/progress` | Lire la progression | front produit / tuteur [file:230] | ConversationProgress ou projection dédiée [file:230] | données filtrées par rôle et partage [file:230][file:344] |
| `GET /sessions/{id}/ui-state` | Lire l’état produit montrable [file:230] | front apprenant / tuteur [file:230][file:344] | UIState [file:230] | aucun champ P0 brut [file:230] |
| `GET /sessions/{id}/memory-summary` | Lire la mémoire gouvernée résumée [file:230][file:333] | apprenant, surfaces autorisées [file:333] | objets mémoire partageables / confirmables [file:333] | jamais de verbatim brut non partagé [file:333] |
| actions de synthèse | Déclencher une synthèse si éligible [file:333] | apprenant, tuteur selon cas [file:333][file:344] | synthèse structurée / blocage explicité [file:333] | maturité requise, confidentialité respectée [file:333] |
| actions d’évaluation | Déclencher la branche terminale si éligible [file:333] | apprenant, éventuellement recommandée par tuteur [file:344] | trace d’évaluation / blocage explicité [file:333] | validation humaine finale, pas d’autonomie certificative [file:333][file:344] |
| vues / actions trainer | Gérer la base de savoir métier [file:344][file:230] | formateur [file:344] | liste items, statuts, validations, exports [file:344] | aucun accès libre au non-partagé apprenant [file:344] |

### 29.6 Matrice des surfaces UI par rôle

| Rôle | Ce qu’il voit | Ce qu’il peut faire | Ce qu’il ne voit pas |
|---|---|---|---|
| Apprenant | conversation, scène, progression, quête active, posture si exposée, CTA terminales, objets persistants [file:333][file:230] | converser, choisir une posture dans les limites prévues, confirmer/partager certains objets, déclencher synthèse/évaluation si éligible [file:290][file:333] | P0 brut, prompts complets, verbatim interne non partagé [file:230][file:333] |
| Tuteur | progression, signaux de blocage, traces partagées, synthèses, évaluations partageables, vues cohorte / apprenant [file:344] | lire, commenter, recommander, préparer un accompagnement, éventuellement valider certaines traces partageables [file:344] | verbatim non partagé, contrôle direct du P0, forçage moteur libre [file:344] |
| Formateur | documents, questionnaire dialogique, items de connaissance, statuts, liens référentiels, écrans de validation [file:344] | uploader, expliciter, structurer, corriger, valider, rattacher au référentiel, exporter [file:344] | doctrine centrale modifiable librement, contenu apprenant non partagé [file:344] |
| Coordinateur | vues métier à préciser plus finement [file:344][file:230] | coordination et validation selon habilitations produit futures [file:344] | non-partagé apprenant en accès libre [file:230] |
| Org admin | capacités d’administration minimales et exports [file:230] | administrer dans les bornes du POC, gérer utilisateurs/groupes, exports [file:230] | lecture libre du contenu apprenant non partagé [file:230] |
| Superadministration technique | supervision technique globale sous contraintes [file:230] | maintenance et administration technique [file:230] | lecture applicative libre du contenu apprenant [file:230] |

### 29.7 Matrice validation humaine et statuts

| Domaine | Statut / étape | Peut être auto-produit | Peut être auto-promu | Validation humaine requise |
|---|---|---|---|---|
| Mémoire apprenant | résumé / consolidation thématique [file:230][file:333] | oui, post-conversation sous gouvernance [file:230] | non vers un statut humainement validé [file:230] | oui si changement de statut humainement qualifié [file:230] |
| Savoir formateur | déclaré [file:344] | oui, saisi ou importé [file:344] | non [file:344] | pas encore validé [file:344] |
| Savoir formateur | dérivé provisoire [file:344] | oui, à partir de documents et dialogue [file:344] | non [file:344][file:230] | oui pour passage au validé [file:344] |
| Savoir formateur | validé humainement [file:344][file:230] | non | non | oui, acte explicite d’un rôle habilité [file:344] |
| Évaluation terminale | trace préparée [file:333] | oui, si éligible [file:333] | non en certification finale [file:333][file:344] | oui pour validation finale ou circulation de certaines preuves [file:344] |

### 29.8 Matrice explicite / implicite côté produit

| Élément | Statut côté produit | Raison |
|---|---|---|
| Scène de séance | explicite [file:333] | aide l’utilisateur à se repérer sans jargon moteur [file:333] |
| Quête active / objectif courant | explicite [file:333] | rend visible ce qu’on cherche maintenant [file:333] |
| Couleur de maturité | explicite [file:333] | matérialise l’avancement sans exposer le P0 [file:333] |
| Posture active | explicite minimalement si le produit l’assume [file:333][file:290] | rendre perceptible le régime de conduite [file:333] |
| Conditions de synthèse / évaluation | explicites ou semi-explicites [file:333] | rendre compréhensibles les CTA terminales [file:333] |
| TurnState brut | implicite / caché [file:230] | objet moteur technique [file:230] |
| Contrat de décision brut | implicite / caché [file:230] | non montrable tel quel [file:230] |
| Verbatim interne non partagé | caché [file:333][file:230] | confidentialité-first [file:230] |
| Prompts complets | cachés [file:333] | instructions internes non exposables [file:290][file:333] |
| Variables de debug P0 | cachées [file:230][file:290] | non-produit, non-frontalisables [file:230] |

### 29.9 Matrice des contraintes de non-régression

| Invariant | Doit rester vrai | Source |
|---|---|---|
| Aucun pipeline P0 dupliqué | oui [file:290] | [file:290] |
| Aucun champ central de décision modifié sans nécessité majeure | oui [file:290][file:230] | [file:290][file:230] |
| UIState sans champ P0 brut | oui [file:230][file:290] | [file:230][file:290] |
| Désérialisation explicite des objets JSONB structurés | oui [file:230] | [file:230] |
| Enums persistées via `.value` | oui [file:230] | [file:230] |
| Pas d’auto-upgrade du provisoire vers le validé humainement | oui [file:230][file:344] | [file:230][file:344] |
| Mémoire et analytics inter-session consolidés post-conversation | oui [file:230] | [file:230] |
| Confidentialité-first et partage explicite | oui [file:230][file:290] | [file:230][file:290] |

### 29.10 Matrice des zones encore à préciser

| Sujet | Ce qui est déjà fixé | Ce qui reste à préciser | Statut |
|---|---|---|---|
| Chorégraphie UX des transitions de posture | existence d’un état de posture, d’un sélecteur et de règles de transition backend [file:333][file:290] | verbalisation exacte, maquettes, granularité des messages de transition [file:333] | ouvert cadré [file:333] |
| Micro-pédagogie de la révision de savoirs | rappel avant explication, micro-explication bornée, défi progressif [file:290][file:333] | séquences détaillées d’exercice, drill, correction, répétition [file:333] | sous-spécifié [file:333] |
| Script détaillé de l’orchestrateur formateur | finalité, matériaux, statuts, validation humaine [file:344] | ordre exact des sections, relances, reprises, UX fine [file:344] | sous-spécifié [file:344] |
| Catalogue canonique des signaux qualité | existence de signaux de progression et qualité [file:230][file:344] | liste exhaustive, définitions, mapping signal → recommandation [file:344] | ouvert cadré [file:344] |
| Rôle exact du tuteur dans validation terminale | lecture, recommandation, validation de certaines traces partageables [file:344] | pouvoir précis de validation sur évaluations et promotions de statut [file:344] | ouvert cadré [file:344] |
| UI métier complète coordinateur / admin | capacités minimales et garde-fous connus [file:230] | écrans complets, navigation, workflows détaillés [file:230][file:344] | partiellement ouvert [file:230] |

## 30. Formule canonique de synthèse

Hugo 2.0 est un moteur tutoriel **réflexif** multi-postures, piloté par état, orchestré côté backend, régulé localement par un P0 conservé, configuré par TutorPrompt, prolongé par une progression conversationnelle et une mémoire gouvernée, et restitué au produit par des états dérivés propres plutôt que par l’exposition de sa mécanique interne.[file:230][file:333][file:290]
