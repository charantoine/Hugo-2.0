# ADR — Hugo 1.8 comme sidecar d’engagement produit au-dessus de P0

## Statut

Proposé pour implémentation immédiate.[file:3][file:18]

## Contexte

Le moteur Hugo actuel est un runtime conversationnel orchestré dans Django, structuré autour d’une chaîne `TurnState -> ConversationDecision -> TeachingPlan -> phase -> prompt -> guardrails`. Ce noyau a déjà consolidé les priorités de protection, clôture, répétition, aide explicite, anti-boucle et gestion 0/1/2 question. Hugo 1.8 doit ajouter une couche de ludification au service de l’apprentissage, sans redéfinir ce noyau.[file:1][file:18][file:20][file:3]

Le frontend actuel expose de nombreux éléments de debug et d’instrumentation utiles aux tests du moteur. Il doit être conservé comme branche testeur/debug, tandis qu’une nouvelle branche prod montrable doit être créée pour présenter une expérience utilisateur apprenant plus propre et plus crédible.[file:3][file:18]

## Décision

Décider que Hugo 1.8 sera implémenté comme :
- un **front prod montrable** séparé du front testeur/debug ;
- un **petit sidecar d’engagement produit** calculant un `EngagementUIModel` dérivé des signaux runtime existants ;
- **aucune modification structurelle du noyau P0** pour supporter la ludification.[file:1][file:3]

## Pourquoi cette décision

Cette décision :
- respecte la vérité actuelle du moteur ;
- limite le risque de régression ;
- permet une démo client rapide ;
- évite de créer un second moteur comportemental ;
- prépare Hugo 1.9 sans le préempter.[file:1][file:3][file:20]

## Conséquences positives

- séparation nette entre logique tutorale et logique d’engagement ;
- conservation du front testeur comme outil de calibration ;
- possibilité de construire un front apprenant crédible sans casser l’existant ;
- compatibilité avec l’architecture Django/TutorPrompt/repo-first déjà cadrée.[file:18][file:20][file:3]

## Conséquences négatives / coûts

- ajout d’une couche d’adaptation supplémentaire ;
- coexistence durable de deux variantes UI ;
- besoin probable d’une projection API dérivée plus propre pour le front prod.[file:3][file:18]

## Alternatives rejetées

### Alternative 1 — Modifier `TurnState` ou `ConversationDecision`

Rejetée car cela contaminerait le noyau P0 avec des préoccupations produit/ludiques contraires au cadrage 1.8.[file:1][file:3]

### Alternative 2 — Créer un moteur de gamification pilotant les tours

Rejetée car le pilotage doit rester dans le moteur tutoriel existant, pas dans une couche ludique parallèle.[file:1][file:3][file:20]

### Alternative 3 — Remplacer le front actuel au lieu de le bifurquer

Rejetée car le front actuel a une valeur de test, d’inspection et de non-régression qu’il faut conserver intacte.[file:3]

## Règles d’implémentation issues de cette ADR

- pas de nouveaux champs P0 pour la ludification ;
- pas de modification des règles 0/1/2 question ;
- pas de modification de la hiérarchie de décision ;
- pas de pilotage ludique de phase/prompt/guardrails ;
- UI prod montrable activée par feature flags / layouts / routes dédiées ;
- `EngagementUIModel` dérivé des signaux runtime existants ;
- exposition d’objets visibles à l’utilisateur sans exposer les internals moteur.[file:1][file:3][file:18]
