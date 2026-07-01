# Spécification — reconfiguration des chats tuteur et formateur dans Hugo

## Statut du document

- Date : 2026-07-01
- Portée : cadrage produit et fonctionnel pour la reconfiguration des espaces conversationnels tuteur et formateur
- Usage cible : document de travail pour implémentation et automatisation Cursor
- Baseline de référence principale : **B = front 1.8 + hugo_back local** [file:5][file:7]
- Baseline distante : **A = front 1.8 + Encoors**, à distinguer explicitement quand la parité n'est pas prouvée [file:5][file:7]

## Sources mobilisées

- R2_CARTOGRAPHIE_FONCTIONNELLE_ACTUALISEE.md [file:5]
- R4_CONTRATS_ET_PREUVES_RUNTIME.md [file:7]
- modelisation_activite_formateur.md [file:1]
- modelisation_activite_tuteur.md [file:2]

## Réel confirmé

Le pipeline conversationnel actif par défaut dans Hugo est le pipeline **P0 legacy** via `build_hugo_turn()` en baseline B ; la branche v17 n'est pas le chemin général tant que `HUGO_P0_V17_ENABLED=true` n'est pas explicitement activé, ce qui est observé localement mais reste à vérifier côté Encoors [file:5]. Le runtime conversationnel expose d'un côté un **contract UI state** via `GET /hugo/sessions/{id}/ui-state/` produit par `build_contract_ui_state`, et de l'autre des payloads de tour POST/SSE relevant de `build_ui_state`, avec un schéma différent ; ces deux surfaces ne doivent pas être confondues [file:5][file:7].

La mémoire de session est calculée, attachée au tour, exposée dans les payloads et via `GET /hugo/sessions/{id}/memory-summary/`, mais elle n'est pas injectée dans le prompt LLM du tour [file:5][file:7]. Le RAG observé dans le chemin actif est **lexical uniquement** ; `pgvector` est présent en dépendance mais inactif en sélection dans le runtime observé [file:5].

Côté formateur, les surfaces réellement observées en baseline B sont le CRUD `TrainerKnowledgeItem`, les actions `validate / provisional / reject / edit`, l'atelier d'élicitation, l'ingest documentaire et le panneau de contexte groupe ; l'ensemble est **REL OBSERV** ou **REL OBSERV PARTIEL** selon la sous-surface [file:5][file:7]. Côté tuteur, les surfaces observées sont `/app/tutor`, la timeline filtrée sans verbatim apprenant, `TutorLearnerLink` pour la visibilité des apprenants, ainsi que les backends `conduct profiles` et `tutor prompts` en local ; la surface métier tuteur riche reste cependant **REL OBSERV PARTIEL** et en grande partie **CIBLE** [file:5].

## Problème à résoudre

Les chats tuteur et formateur sont actuellement des copies quasi conformes du chat apprenant, alors que leurs activités réelles diffèrent fortement de celles de l'apprenant [file:1][file:2]. L'infrastructure conversationnelle et l'interface sont en place, mais elles sont calibrées pour des entretiens réflexifs et aides au diagnostic destinés à l'apprenant, pas pour le travail de suivi, de coordination, de gouvernance documentaire ou de régulation attendu des tuteurs et formateurs [file:1][file:2].

La reconfiguration attendue doit donc viser deux objectifs complémentaires : d'abord **différencier les comportements conversationnels** par prompting et profils de conduite ; ensuite **ouvrir des flows métier adaptés** permettant de transformer certains résultats du chat en objets de travail stables, révisables et traçables [file:1][file:2][file:5]. Elle doit aussi inclure un **chantier transverse de réalignement UI** : si une page existante est respecifiée, tous les boutons, cartes, libellés d'accès, titres de page et microcopies qui y pointent doivent être revus pour refléter la fonction réelle de la cible, et non son héritage historique [file:5].

## Cadre métier — formateur

La modélisation formateur distingue deux plans irréductibles. Le premier est la **médiation directe** aux apprentissages : A1 expliciter et clarifier, A2 animer l'analyse de pratique, A3 produire un feedback formatif dialogique, A4 lire et interpréter des trajectoires d'apprentissage [file:1]. Le second est l'**ingénierie et la gouvernance didactique** : B1 configurer les conditions didactiques, B2 gouverner la qualité des ressources, B3 capitaliser et institutionnaliser, B4 coordonner les acteurs et arbitrer les tensions, B5 réguler les parcours à l'échelle de la cohorte [file:1].

Le réel Hugo actuellement observé couvre surtout **B2** via la gouvernance des ressources et la base de connaissances, mais couvre peu ou pas A4, B3, B4 et B5 dans des surfaces métier confirmées [file:1][file:5]. Il faut donc éviter de réduire le chat formateur à un simple canal de gestion documentaire, même si c'est aujourd'hui la partie la mieux instrumentée [file:1].

## Cadre métier — tuteur

La modélisation tuteur distingue huit familles d'activités : 1 se préparer à accompagner, 2 recueillir et susciter l'expression, 3 diagnostiquer une situation apprenante, 4 réfléchir avec l'apprenant, 5 soutenir et réguler dans l'action, 6 orienter et réguler le parcours, 7 valider / évaluer / instituer, 8 documenter et clôturer provisoirement [file:2]. Les invariants de conception les plus structurants pour Hugo sont l'ancrage contextuel sur des objets nommés, le recueil avant proposition, le diagnostic gradué, la non-réponse directe systématique, la projection d'une suite, la mémoire longitudinale, la pluralité temporelle et la corégulation humain/IA [file:2].

Le chat tuteur doit donc être pensé moins comme un clone du chat apprenant que comme un **instrument d'orchestration tutorale** : lecture de situations, préparation d'interventions, diagnostic prudent, documentation d'hypothèses, transmission à d'autres rôles et préparation d'étayages [file:2].

## Principes directeurs de reconfiguration

### Principe 1 — différenciation comportementale par prompting

La première couche de reconfiguration est la plus réaliste à court terme : différencier les chats tuteur et formateur au moyen de `conduct-profiles`, `TutorPrompt` et prompt-templates spécialisés, sans modifier immédiatement l'architecture profonde du runtime [file:5][file:7]. Côté tuteur, ces profils doivent être orientés vers les régimes de dialogue tutoriel documentés : pré-réflexion silencieuse, entretien d'expression, aide au diagnostic, entretien réflexif, soutien dans l'action et travail sur feedback [file:2]. Côté formateur, ils doivent être orientés vers les tâches d'explicitation, d'analyse de signaux collectifs, de préparation d'arbitrage documentaire et d'écriture assistée de décisions [file:1].

### Principe 2 — le chat prépare, l'humain valide, le flow métier écrit

Le chat ne doit pas écrire directement dans les objets métier stables. Le bon modèle est une bifurcation contrôlée : le tour de chat produit un **brouillon structuré**, puis un bouton ouvre un flow de confirmation dans lequel l'utilisateur relit, corrige, contextualise et valide avant write backend [file:7][file:5].

### Principe 3 — pas de verbatim brut comme objet métier

Le système ne doit pas réinjecter ou importer le verbatim brut du chat comme ressource métier. Les imports doivent porter sur des **reformulations structurées** et révisables : explication, note, justification, transmission, plan d'intervention, bilan [file:1][file:2][file:7].

### Principe 4 — séparation stricte des niveaux

Il faut distinguer quatre niveaux qui ne doivent pas être écrasés dans un flux unique : **lire une situation, interpréter une situation, décider une action et justifier cette action** [file:2]. Le flow produit doit conserver cette séparation, notamment pour le tuteur et pour les demandes d'arbitrage ou de transmission [file:1][file:2].

### Principe 5 — surface dédiée quand le chat ne suffit pas

Le chat peut bien soutenir la formulation, la reformulation, l'exploration, la préparation de décisions ou la rédaction assistée. En revanche, la vue de cohorte, la validation formelle, la coordination inter-rôles et la capitalisation documentaire durable appellent des **surfaces plus stables** et ne doivent pas être dissoutes dans le flux conversationnel [file:1].

### Principe 6 — alignement sémantique de l'interface

Toute page respecifiée doit entraîner une revue systématique de ses **points d'accès UI** : boutons d'accueil, cartes, liens, tuiles, breadcrumbs, titre de page, sous-titre et microcopies [file:5]. Un libellé d'entrée ne doit jamais conserver le nom d'une ancienne fonction si la cible a changé ; il doit nommer la **fonction actuelle de la destination** [file:5].

Exemple : si, côté formateur, un bouton depuis la page d'accueil pointe vers l'espace conversationnel propre du formateur, un libellé de type **« chat apprenant »** devient trompeur et doit être remplacé par une formulation alignée sur la cible réelle, par exemple **« Mon chat »** [file:5].

## Cible 2.0

La cible est un système où les espaces tuteur et formateur conservent le moteur conversationnel commun, mais sont reconfigurés par persona autour de leurs activités propres, avec :

- des profils de conduite spécialisés ;
- des gabarits de réponses et garde-fous distincts ;
- des boutons d'import transformant des résultats de chat en brouillons d'objets métier ;
- des flows de validation humaine explicite ;
- des surfaces stables complémentaires pour tout ce qui engage parcours, coordination, capitalisation ou décision institutionnelle ;
- un réalignement des points d'entrée UI avec les usages réels de ces espaces [file:1][file:2][file:5].

Cette cible est **CIBLE**, non livrée comme telle aujourd'hui [file:5].

## Passage du contenu du chat au flow géré par bouton

### Schéma général

Le passage du chat vers le flow bouton doit suivre quatre étages :

1. **Tour de chat** : l'utilisateur échange via `POST /hugo/sessions/{id}/messages/` ou `POST /hugo/sessions/{id}/messages/stream/` [file:7].
2. **Extraction locale** : le front identifie qu'un contenu est importable et fabrique un `draft` d'import à partir de la réponse assistant, du contexte visible, de l'ID de session et éventuellement de l'ID de message source [file:7].
3. **Flow bouton** : au clic sur un bouton d'import, le front ouvre une modale ou un panneau prérempli permettant relecture, édition, choix de cible et confirmation [file:5].
4. **Write backend** : le front appelle alors la route métier cible, par exemple `trainer/knowledge-items/` pour créer une ressource provisoire [file:7][file:5].

### Règles de ce passage

- Le flow ne s'appuie pas sur `GET /ui-state/` pour récupérer le contenu importable ; `build_contract_ui_state` sert à l'état d'interface, pas au brouillon métier [file:5][file:7].
- Le brouillon ne repose pas sur une mémoire longue injectée au LLM ; la mémoire disponible est gouvernée, calculée, exposée, mais non injectée dans le prompt [file:5][file:7].
- Le brouillon doit être borné, éditable et attribué à un objet cible explicite : groupe, apprenant, item documentaire, demande d'arbitrage [file:1][file:2].

### Contrat d'entrée générique du flow bouton (CIBLE)

Le contrat d'entrée générique recommandé pour tout bouton d'import est :

```json
{
  "session_id": "uuid",
  "source_message_ids": ["uuid"],
  "import_kind": "string",
  "draft_title": "string",
  "draft_body": "string",
  "source_summary": "string",
  "target_ref": {
    "kind": "group|learner|knowledge_item|role_request",
    "id": "uuid"
  },
  "human_validation_required": true
}
```

Ce contrat est **CIBLE** mais cohérent avec les routes et objets déjà observés [file:7][file:5].

## Matrice des boutons d'import

### 1. Importer comme ressource provisoire — formateur

- Persona : TRAINER [file:5][file:7]
- Objet créé : `TrainerKnowledgeItem` [file:5][file:7]
- Statut initial : `provisional` [file:5][file:7]
- Flow : bouton sous le message assistant ; ouverture d'une modale préremplie ; confirmation ; write sur route trainer knowledge items [file:5][file:7]
- Champs préremplis : titre, résumé court, contenu structuré, contexte groupe, métadonnée `source=chat`
- Validation humaine : obligatoire avant toute validation finale [file:5]
- Tag : **REL OBSERV** pour l'objet cible ; **CIBLE** pour le bouton

### 2. Importer comme explicitation pédagogique — formateur

- Persona : TRAINER [file:5]
- Objet créé : `TrainerKnowledgeItem` typé “explicitation”
- Statut initial : `provisional`
- Champs préremplis : objectif d'apprentissage, situation de référence, erreurs fréquentes, indices de réussite, usages recommandés [file:1]
- Raison métier : soutenir A1 et B2 sans réduire l'explicitation à un simple texte libre [file:1]
- Tag : **REL OBSERV PARTIEL** pour le socle trainer ; **CIBLE** pour le type d'objet et le bouton

### 3. Importer comme justification d'arbitrage — formateur

- Persona : TRAINER
- Objet créé : note de décision liée à un item ou bloc de justification dans l'item
- Statut initial : brouillon
- Champs préremplis : décision envisagée, raisons, risques, critères utilisés, action suivante [file:1]
- Raison métier : soutenir B2 et B3 via écriture assistée de justification [file:1]
- Tag : **CIBLE**, avec appui sur surfaces trainer existantes

### 4. Importer comme note tutorale — tuteur

- Persona : TUTOR [file:5]
- Objet créé : note tutorale privée non destinée à l'apprenant
- Statut initial : brouillon
- Champs préremplis : hypothèse de blocage, signaux observés, action tutorale envisagée, points de vigilance, suite prévue [file:2]
- Raison métier : soutenir la famille 8 “documenter et clôturer provisoirement” [file:2]
- Tag : **CIBLE**

### 5. Importer comme préparation d'intervention — tuteur

- Persona : TUTOR
- Objet créé : mini-plan d'accompagnement
- Statut initial : brouillon
- Champs préremplis : objectif de la prochaine interaction, questions à poser, mode d'étayage à privilégier, indicateurs d'observation [file:2]
- Raison métier : soutenir les familles 1, 3, 4 et 5 [file:2]
- Tag : **CIBLE**

### 6. Importer comme transmission au formateur — tuteur

- Persona : TUTOR vers TRAINER
- Objet créé : transmission structurée inter-rôles
- Statut initial : brouillon puis “sent” après confirmation
- Champs préremplis : motif de transmission, faits partageables, interprétation prudente, question adressée au formateur, niveau d'urgence [file:2][file:1]
- Raison métier : conserver la distinction faits / interprétation / décision et soutenir la coordination [file:1][file:2]
- Tag : **CIBLE**

### 7. Importer comme demande d'arbitrage inter-rôles — tuteur ou formateur

- Persona : TRAINER ou TUTOR
- Objet créé : ticket de coordination / arbitrage
- Statut initial : open après validation humaine
- Champs préremplis : tension observée, options considérées, option préférée, raisons, impact attendu [file:1]
- Raison métier : soutenir B4 sans dissoudre l'arbitrage dans le flux conversationnel [file:1]
- Tag : **CIBLE**

### 8. Importer comme bilan capitalisable — formateur

- Persona : TRAINER
- Objet créé : capsule de capitalisation ou note de bilan durable
- Statut initial : brouillon
- Champs préremplis : incident ou changement, décision prise, effets observés, leçons apprises, recommandations [file:1]
- Raison métier : soutenir B3 capitaliser et institutionnaliser [file:1]
- Tag : **CIBLE**

## Contrat produit détaillé bouton par bouton

### Bouton 1 — Importer comme ressource provisoire

**Déclencheur** : affiché sous un message assistant du chat formateur lorsque la réponse contient une explication, un cas-type, une ressource ou une reformulation réutilisable. **Tag : CIBLE**.

**Entrée flow** : `session_id`, `source_message_ids`, `import_kind="trainer_resource_provisional"`, `draft_payload`, `group_id`. **Tag : CIBLE**.

**UI de confirmation** : modale ou side-sheet dans `/app/trainer` montrant les champs `title`, `summary`, `body`, groupe cible, tags et avertissement “créé depuis chat — à relire”. **Tag : REL OBSERV PARTIEL** sur la surface trainer [file:5].

**Write backend** : création d'un `TrainerKnowledgeItem` en `provisional`. **Tag : REL OBSERV** pour l'objet cible et la route trainer [file:5][file:7].

**Règle métier** : aucune validation automatique ; passage éventuel à `validate` par action humaine explicite. **Tag : REL OBSERV / CART CONFIRM** [file:5].

### Bouton 2 — Importer comme explicitation pédagogique

**Déclencheur** : affiché sous un message assistant formateur produisant une explicitation pédagogique exploitable. **Tag : CIBLE**.

**Entrée flow** : `import_kind="trainer_explication"`, avec draft structuré. **Tag : CIBLE**.

**UI de confirmation** : formulaire spécialisé réutilisant la base `TrainerKnowledgeItem` avec champs dédiés à l'explicitation. **Tag : REL OBSERV PARTIEL** sur la base trainer [file:5].

**Write backend** : création d'un item provisoire typé explicitation. **Tag : REL OBSERV PARTIEL / CIBLE**.

**Règle métier** : ne pas confondre exactitude informationnelle et valeur formative ; la revue humaine doit porter sur la valeur pédagogique. **Tag : CIBLE, fondé sur B2** [file:1].

### Bouton 3 — Importer comme justification d'arbitrage

**Déclencheur** : disponible quand l'échange porte sur l'opportunité de valider, rejeter, retravailler ou laisser provisoire une ressource. **Tag : CIBLE**.

**Entrée flow** : `knowledge_item_id`, `import_kind="trainer_decision_rationale"`, `draft_payload`. **Tag : CIBLE**.

**UI de confirmation** : bloc prérempli lié à la ressource cible. **Tag : CIBLE avec appui sur surfaces trainer**.

**Write backend** : écriture d'une note liée à l'item ou d'un champ de justification. **Tag : CIBLE**.

**Règle métier** : le chat rédige une proposition de justification, jamais la décision institutionnelle elle-même. **Tag : CIBLE / doctrine humaine** [file:1][file:5].

### Bouton 4 — Importer comme note tutorale

**Déclencheur** : affiché dans le chat tuteur lorsqu'une hypothèse de compréhension de situation ou de suivi émerge. **Tag : CIBLE**.

**Entrée flow** : `learner_id`, `import_kind="tutor_note"`, `draft_payload`. **Tag : CIBLE**.

**UI de confirmation** : modale sur fiche apprenant ou contexte tuteur permettant édition, confidentialité et planification de suite. **Tag : CIBLE**, avec base de surface tuteur **REL OBSERV PARTIEL** [file:5].

**Write backend** : création d'une note tutorale privée. **Tag : CIBLE**.

**Règle métier** : pas de partage automatique à l'apprenant ; l'objet sert la mémoire tutorale et la préparation d'accompagnement. **Tag : CIBLE, fondé sur famille 8** [file:2].

### Bouton 5 — Importer comme préparation d'intervention

**Déclencheur** : affiché quand le chat a aidé le tuteur à préparer un prochain échange ou une action d'étayage. **Tag : CIBLE**.

**Entrée flow** : `learner_id`, `import_kind="tutor_intervention_plan"`, `draft_payload`. **Tag : CIBLE**.

**UI de confirmation** : formulaire très court, utilisable rapidement. **Tag : CIBLE**.

**Write backend** : création d'un plan d'intervention tutorale. **Tag : CIBLE**.

**Règle métier** : préserver le diagnostic gradué et la non-réponse directe ; le plan doit privilégier questions, reformulations et étayages gradués avant prescription. **Tag : CIBLE, fondé sur invariants 3 et 4** [file:2].

### Bouton 6 — Importer comme transmission au formateur

**Déclencheur** : affiché lorsqu'un cas doit être remonté au formateur. **Tag : CIBLE**.

**Entrée flow** : `learner_id`, `group_id`, `import_kind="tutor_to_trainer_transmission"`, `draft_payload`. **Tag : CIBLE**.

**UI de confirmation** : modale avec destinataire, niveau d'urgence, périmètre de partage, note de prudence sur la confidentialité. **Tag : CIBLE**.

**Write backend** : création d'un ticket de transmission tutorale. **Tag : CIBLE**.

**Règle métier** : toujours distinguer faits partageables, interprétation et question adressée ; pas de déversement de verbatim brut. **Tag : CIBLE, fondé sur familles 6-8 et B4** [file:2][file:1].

### Bouton 7 — Importer comme demande d'arbitrage inter-rôles

**Déclencheur** : affiché lorsqu'une tension de parcours, de rôle, de gouvernance ou de partage appelle une décision explicite. **Tag : CIBLE**.

**Entrée flow** : `target_role`, `group_id`, `import_kind="role_arbitration_request"`, `draft_payload`. **Tag : CIBLE**.

**UI de confirmation** : formulaire de coordination, journalisé, avec champ “options examinées”. **Tag : CIBLE**.

**Write backend** : création d'une demande d'arbitrage. **Tag : CIBLE**.

**Règle métier** : le chat aide à formuler le problème ; l'arbitrage reste humain et traçable. **Tag : CIBLE, fondé sur B4** [file:1].

### Bouton 8 — Importer comme bilan capitalisable

**Déclencheur** : affiché après un échange de retour d'expérience, d'incident ou de reconfiguration de dispositif. **Tag : CIBLE**.

**Entrée flow** : `group_id` ou `promotion_id`, `import_kind="trainer_capitalisation"`, `draft_payload`. **Tag : CIBLE**.

**UI de confirmation** : formulaire de bilan durable distinguant constat, décision, effets et recommandations. **Tag : CIBLE**.

**Write backend** : création d'une capsule de capitalisation. **Tag : CIBLE**.

**Règle métier** : séparer note de travail temporaire et document capitalisable réutilisable. **Tag : CIBLE, fondé sur B3** [file:1].

## Tâche transverse UI — vérification et mise à jour des points d'entrée

### Objectif

Ajouter au chantier une tâche explicite de **revue et réalignement UI** des points d'entrée vers les espaces conversationnels tuteur et formateur, ainsi que de toute page existante respecifiée [file:5]. L'objectif est d'éviter qu'une interface continue à exposer des libellés hérités du modèle apprenant alors que la cible métier a changé [file:5][file:1][file:2].

### Périmètre

- pages d'accueil tuteur et formateur ;
- cartes, tuiles et boutons pointant vers une page conversationnelle respecifiée ;
- menus et liens contextuels ;
- titre de page cible ;
- sous-titre, aides de contexte, textes d'introduction ;
- CTA secondaires associés à la page cible [file:5].

### Règle produit

Quand une page existante change de fonction métier, tous ses points d'accès doivent être revus. Un point d'entrée UI doit nommer la **fonction réelle actuelle** de la destination, pas sa signification historique [file:5].

### Exemple explicite à traiter

Pour le formateur, si un bouton depuis la page d'accueil pointe vers l'espace conversationnel propre du formateur mais porte encore un libellé comme **« chat apprenant »** ou équivalent, ce bouton doit être renommé avec une formulation cohérente avec la cible, par exemple **« Mon chat »** [file:5]. Le titre et la microcopy de la page cible doivent être alignés avec ce renommage [file:5].

### Livrables attendus

- inventaire des labels actuels ;
- mapping `label actuel -> label cible` ;
- justification métier du renommage ;
- liste des composants front impactés ;
- captures avant / après ou tests Playwright si faisable [file:5].

### Tag de vérité

- existence des interfaces tuteur / formateur : **REL OBSERV PARTIEL** [file:5]
- nécessité du réalignement UI : **CIBLE** mais fortement justifiée par le différentiel entre fonction historique et cible respecifiée [file:5][file:1][file:2]

## Priorisation de livraison recommandée

### Lot P1 — formateur, faible risque

À implémenter en premier :

- Bouton 1 — ressource provisoire
- Bouton 2 — explicitation pédagogique
- Bouton 3 — justification d'arbitrage
- Tâche transverse UI — revue des labels et points d'entrée formateur, y compris le cas `chat apprenant -> Mon chat`

Ce lot réutilise les surfaces réellement observées côté formateur en baseline B et limite les créations d'objets nouveaux [file:5][file:7].

### Lot P2 — tuteur, accompagnement et documentation

À implémenter en second :

- Bouton 4 — note tutorale
- Bouton 5 — préparation d'intervention
- Bouton 6 — transmission au formateur
- Revue des labels et points d'entrée tuteur

Ce lot est très cohérent métierment mais demande encore de nouvelles surfaces et objets côté tuteur [file:2][file:5].

### Lot P3 — coordination et capitalisation

À implémenter en troisième :

- Bouton 7 — demande d'arbitrage inter-rôles
- Bouton 8 — bilan capitalisable

Ce lot dépend davantage de surfaces de coordination et de capitalisation encore non observées [file:1][file:5].

## Écarts réel vs cible

- Le réel confirmé formateur couvre bien la base documentaire et l'élicitation, mais pas encore une vraie orchestration formateur complète autour des sept familles [file:1][file:5].
- Le réel confirmé tuteur couvre une base d'interface et de visibilité, mais pas les objets de note tutorale, plan d'intervention ou transmission structurée décrits ici [file:2][file:5].
- Le lien knowledge validé → conversation apprenant est encore **À VÉRIFIER** bout-en-bout, même si la gouvernance trainer est en place [file:5].
- Le différentiel local / Encoors reste important pour certaines routes conversationnelles et profils, donc les specs d'implémentation doivent toujours rappeler la baseline ciblée [file:7].
- Les interfaces formateur et tuteur existantes peuvent encore porter des labels issus d'un ancien cadrage fonctionnel ; ces libellés doivent être audités avant livraison [file:5].

## À VÉRIFIER

- Parité Encoors pour `conduct-profiles/` et plusieurs surfaces conversationnelles ; ne pas supposer que le local équivaut au distant sans oracle authentifié récent [file:7].
- Écart `INC-02` : `GET /dashboard/groups/{id}/learners/` renvoie `[]` pour TRAINER malgré memberships, ce qui limite tout flow dépendant d'une vraie lecture de cohorte [file:5].
- Usage bout-en-bout de `TrainerKnowledgeItem` validé dans le RAG actif, encore non prouvé [file:5].
- Inventaire exact des labels actuels en front pour les entrées formateur / tuteur, y compris le bouton actuellement nommé “chat apprenant” côté formateur : **À VÉRIFIER** par lecture code + rejeu UI [file:5].

## Décisions de conception recommandées

1. Implémenter les boutons sous forme d'un composant UI unique de type `ImportFromChatAction` configurable par `import_kind`.
2. Ne jamais écrire d'objet métier depuis le LLM sans écran de confirmation humaine.
3. Faire produire au chat un `draft payload` structuré, distinct du texte visible, pour fiabiliser le préremplissage des flows.
4. Réutiliser au maximum les surfaces trainer existantes pour P1.
5. Pour les flows tuteur, commencer par des objets simples et privés avant toute coordination inter-rôles avancée.
6. Journaliser systématiquement `session_id`, `source_message_ids`, `role`, `target_ref`, `import_kind`.
7. Ajouter à P1 un audit explicite de cohérence UI : points d'entrée, titres de page, microcopies et CTA doivent être alignés avec la cible fonctionnelle réelle.

## Prochaine sortie utile

Le prolongement naturel de cette spec est un document d'exécution Cursor détaillant les tâches CODE à produire dans `docs workspace`, l'ordre des commits, les contrats JSON cibles, les critères d'acceptation par lot et le lot transverse UI de réalignement des libellés.

---

## Addendum versionné (lots A + B + C)

Voir `docs-workspace/addendum_front_chats_lots_ABC_2026_07_01.md` pour l'état front réel après séparation des shells et mutualisation du noyau `useHugoSessionChat.js` (baseline B, 2026-07-01).
