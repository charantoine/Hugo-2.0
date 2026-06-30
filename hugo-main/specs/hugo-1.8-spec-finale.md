# Hugo 1.8 — Spec exécutable pour branche prod montrable

## Objet

Cette spec définit l’implémentation de **Hugo 1.8** comme une **branche prod montrable** de l’application existante, tout en **conservant le frontend actuel comme branche testeur/debug**. Hugo 1.8 ne redéfinit pas le noyau Hugo 1.7/P0 ; il ajoute une couche produit/UX de progression visible et d’engagement léger au-dessus du runtime Django existant.[file:1][file:3][file:18][file:20]

## Sources de vérité

Ordre de priorité documentaire obligatoire :

1. `p0_description_technique_actuelle_mise_a_jour.md` : vérité du moteur actuel, de la chaîne runtime, des champs `TurnState`, de `ConversationDecision`, des règles 0/1/2 question et des priorités de décision.[file:1]
2. `Hugo-1.6-Cadrage-Transformation-du-comportement.md` : doctrine de fond, invariants produit, mémoire gouvernée, confidentialité-first, repo-first, moteur piloté par état.[file:20]
3. `Quel-type-dengagement-vise-t-on-en-priorite-__Ret-2.md` et `Nous-ouvrons-ici-le-chantier-Hugo-1.8-centre-sur-3.md` : cadrage 1.8 ludification, objectifs d’engagement, mécaniques autorisées/interdites, hypothèse “P0 inchangé + petit engagement engine léger + UI visible”.[file:2][file:3]
4. `SPEC_POC_v1.5-update-27_03_2026.md` : cadre technique plateforme, Django, TutorPrompt, API, multi-tenant, confidentialité, webapp responsive, tant qu’il n’entre pas en conflit avec P0 actuel.[file:18]

## Décision centrale

Hugo 1.8 est une **couche produit et UX** au-dessus du moteur actuel. Il ajoute :
- une progression visible de scène ;
- des quêtes courtes ;
- des objets persistants ;
- des récompenses symboliques ;
- une variante UI `prod_showable` ;
- un `EngagementUIModel` dérivé des signaux runtime existants.[file:1][file:3]

Hugo 1.8 n’ajoute pas :
- de nouvelle architecture conversationnelle parallèle ;
- de logique ludique dans `TurnState` ;
- de logique ludique dans `ConversationDecision` ;
- de déplacement du pilotage vers le LLM ;
- de scoring scolaire opaque ;
- de leaderboard ;
- de streak central ;
- de réouverture artificielle de scène.[file:1][file:3][file:20]

## Invariants non négociables

### Invariants moteur

Doivent être conservés tels quels :
- la chaîne runtime actuelle `TurnState -> ConversationDecision -> TeachingPlan -> phase -> prompt -> guardrails` ;
- le backend Django orchestré ;
- `TutorPrompt` comme brique de configuration runtime ;
- la hiérarchie de décision actuelle ;
- les règles 0/1/2 question ;
- la priorité à la protection, la clôture, la répétition, l’aide explicite et l’anti-boucle ;
- la règle “un seul objectif de régulation par message”.[file:1][file:18][file:20]

### Invariants produit

Doivent être conservés :
- posture AFEST réflexive, non magistrale ;
- référentiel-first ;
- mémoire structurée et gouvernée ;
- RAG situé et non dominant ;
- confidentialité-first ;
- partage explicite ;
- repo-first ;
- inscription dans une trajectoire future plus large que le seul cas AFEST.[file:18][file:20]

### Invariants 1.8

Doivent être respectés :
- l’engagement est au service de l’apprentissage, pas l’inverse ;
- priorité d’engagement : profondeur de réflexion > complétude de scène > retour régulier ;
- la ludification rend visible un progrès utile, elle ne crée pas un second moteur comportemental ;
- la solution privilégiée est `P0 inchangé ou presque + petit engagement engine léger à côté de P0 + UI produit qui rend visible la progression`.[file:2][file:3]

## Split des deux fronts

### Front testeur/debug

Le front actuel est conservé comme surface d’inspection et de calibration. Il garde :
- affichage `TurnState` détaillé ;
- affichage `ConversationDecision` détaillé ;
- réglages de phase/classifier/runtime ;
- instrumentation et outils de débogage ;
- visibilité du comportement réel du moteur.[file:1][file:3]

### Front prod montrable

Le front prod montrable est une variante UI apprenant qui :
- masque toute instrumentation ;
- expose conversation, progression visible, quêtes courtes, objets persistants, mini-bilan/trace et récompenses symboliques ;
- reste branché sur le même backend et les mêmes endpoints métier.[file:3][file:18]

### Commun aux deux

Les deux fronts partagent :
- le même backend Django ;
- le même moteur P0 ;
- les mêmes contrats métier principaux ;
- les mêmes règles de confidentialité, RLS et partage.[file:1][file:18][file:20]

## Architecture cible 1.8

### Principe

Architecture cible :
- `P0` inchangé ;
- `EngagementUIModel` dérivé ;
- coexistence de deux variantes UI ;
- aucune contamination du noyau tutoriel par la couche ludique.[file:1][file:3]

### Placement du moteur léger d’engagement

Le petit moteur d’engagement doit être placé **hors P0**, dans une couche produit/applicative. Il consomme les sorties runtime existantes et calcule un modèle UI dérivé. Il ne renvoie aucune consigne au moteur tutoriel.[file:1][file:3]

### Signaux source autorisés

Le calcul d’engagement peut dériver ses informations à partir de signaux déjà présents dans le moteur, par exemple :
- `covered_points` ;
- `remaining_open_points` ;
- `learner_help_request` ;
- `closure_signal` ;
- `repetition_signal` ;
- `loop_risk` ;
- `session_maturity` ;
- `evidence_strength` ;
- `can_close_for_now` ;
- `reflective_depth` ;
- `recent_progress` ;
- `has_concrete_actions` ;
- `episode_clarity`.[file:1][file:3]

Aucun nouveau champ P0 ni nouveau champ `ConversationDecision` ne doit être introduit dans ce lot pour supporter la ludification.[file:1][file:3]

## Contrat dérivé recommandé

Créer un contrat dérivé de type `EngagementUIModel` contenant au minimum :
- `scene_progress` ;
- `quest_cards` ;
- `persistent_objects` ;
- `symbolic_rewards` ;
- `gamification_profile` ;
- `ui_visibility_flags`.[file:3]

Ce contrat doit être stable pour le front, découplé des internals P0, mais alimenté par eux.[file:1][file:3]

## MVP UX prod montrable

### Vue session apprenant

Créer une page session avec 4 zones :
1. fil conversationnel ;
2. progression visible de scène ;
3. quêtes courtes ;
4. panneau “traces et acquis”.[file:3]

### Progression visible de scène

Mapping recommandé MVP :
- `Raconter` ;
- `Comprendre` ;
- `Décider` ;
- `Retenir` ;
- `Transmettre`.[file:1][file:3]

Ce mapping est descriptif, non scriptant. Il représente l’état de la scène à partir des signaux réels, sans imposer un tunnel rigide.[file:1][file:3]

### Quêtes courtes

Créer 1 à 3 cartes de quêtes courtes dérivées du manque utile actuel, par exemple :
- clarifier la situation ;
- nommer le problème ;
- identifier une cause plausible ;
- formuler la prochaine action ;
- préparer le message pour le tuteur.[file:1][file:3]

### Objets persistants MVP

Exposer au moins :
- traces prêtes à transmettre ;
- compétences mobilisées illustrées ;
- capsules de progrès.[file:3][file:18]

### Récompenses symboliques MVP

Limiter le premier lot à :
- badges ;
- thèmes visuels ;
- variantes sobres d’avatar Hugo.[file:2][file:3]

Ne pas implémenter dans ce lot :
- leaderboard ;
- score global ;
- streak central ;
- monnaie virtuelle ;
- renommage libre de Hugo ;
- styles caricaturaux ou infantilisants.[file:2][file:3]

## Profils de ludification

Implémenter trois profils configurables :
- `A` = ludique assumé ;
- `B` = intermédiaire ;
- `C` = sobre pro.[file:2][file:3]

Ces profils modulent uniquement l’expression visuelle et la fréquence des feedbacks, jamais la logique tutorale.[file:1][file:3]

## Intégration front

### Variante UI

Créer deux layouts :
- `TesterLayout` ;
- `ProdLearnerLayout`.[file:3]

### Feature flags

Introduire au minimum :
- `frontend_mode = tester | prod_showable` ;
- `engagement_ui_enabled` ;
- `scene_progress_enabled` ;
- `persistent_objects_enabled` ;
- `symbolic_rewards_enabled` ;
- `gamification_profile = A | B | C`.[file:3]

### Routes

Recommandation simple :
- conserver les routes debug existantes ;
- créer une route prod montrable dédiée, par exemple `/app/session/:id`, branchée sur les mêmes endpoints backend métier.[file:3][file:18]

## Intégration backend

### Réutilisation prioritaire

Réutiliser les endpoints Hugo existants avant toute extension :
- `POST /hugo/sessions` ;
- `GET /hugo/sessions/{session_id}` ;
- `POST /hugo/sessions/{session_id}/messages` ;
- `POST /hugo/sessions/{session_id}/generate-trace` ;
- `POST /traces/{trace_id}/validate` ;
- `POST /hugo/sessions/{session_id}/share`.[file:18]

### Projection dérivée si nécessaire

Si le payload actuel n’est pas suffisant pour le front prod montrable, créer une projection dérivée dédiée, par exemple `GET /hugo/sessions/{session_id}/engagement-view`.[file:3][file:18]

Cette projection expose le `EngagementUIModel`, sans modifier le contrat central du moteur.[file:3][file:18]

## Sécurité et confidentialité

Toute implémentation 1.8 doit respecter :
- RLS multi-tenant stricte ;
- visibilité limitée aux rôles autorisés ;
- partage explicite ;
- non-exposition du verbatim non partagé ;
- conformité avec la doctrine confidentialité-first existante.[file:18][file:20]

L’UI prod montrable ne doit jamais contourner les `share_*` flags existants.[file:18][file:20]

## Critères d’acceptation

Le lot est acceptable si :
- le moteur P0 se comporte à l’identique en mode testeur avant/après ;
- aucune logique d’engagement n’a été injectée dans `TurnState` ou `ConversationDecision` ;
- le front prod masque totalement l’instrumentation ;
- la progression visible est branchée sur des signaux réels et non sur le temps passé ;
- les profils A/B/C n’altèrent pas la logique tutorale ;
- le mini-bilan/texte tuteur est valorisé comme accomplissement de scène.[file:1][file:3]

## Non-objectifs explicites

Ne pas faire dans ce lot :
- refonte P0 ;
- nouvelle architecture conversationnelle ;
- moteur ludique pilotant les tours ;
- logique de scoring scolaire opaque ;
- gamification de rétention creuse ;
- préemption de Hugo 1.9 longitudinal.[file:1][file:3][file:20]

## Arbitrages ouverts

- calcul du `EngagementUIModel` côté backend ou côté front ;
- nombre exact d’étapes de progression visible ;
- profondeur de persistance des objets 1.8 dès le premier lot ;
- démarrage avec profils B/C seulement ou A/B/C ;
- wording produit final de “compétences mobilisées”.[file:2][file:3][file:18]
