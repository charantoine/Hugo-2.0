# Prompt Cursor CTO-ready — Hugo 1.8

Tu implémentes Hugo 1.8 comme une **branche prod montrable** de l’application existante.

## Mission

Créer une variante UI `prod_showable` crédible pour démonstration client et premiers pilotes, tout en conservant le frontend actuel comme `tester/debug`. Cette variante doit rendre visible la progression utile de scène, des quêtes courtes, des objets persistants et des récompenses symboliques, **sans modifier le noyau tutoriel P0**.[file:1][file:3][file:18][file:20]

## Contraintes absolues

- Ne refonds pas le moteur P0.[file:1][file:3]
- Ne modifies pas la chaîne runtime Django existante.[file:1][file:18]
- Ne déplaces pas le pilotage tutoriel vers le LLM.[file:18][file:20]
- N’ajoutes pas de logique de gamification dans `TurnState` ni dans `ConversationDecision`.[file:1][file:3]
- Ne modifies pas les règles 0/1/2 question.[file:1]
- Ne modifies pas la hiérarchie de décision actuelle.[file:1]
- Ne remplaces pas le front testeur/debug actuel : conserve-le.[file:3]
- N’implémentes ni leaderboard, ni score global opaque, ni streak central, ni économie de points par message.[file:2][file:3]

## Architecture à respecter

Conserver la logique existante :
- runtime orchestré Django ;
- `TutorPrompt` comme brique de configuration runtime ;
- moteur décisionnel P0 intact ;
- front testeur/debug conservé ;
- variante prod montrable ajoutée à côté.[file:1][file:18][file:20]

## Solution à implémenter

Implémente Hugo 1.8 comme :
1. une couche UI `prod_showable` ;
2. un `EngagementUIModel` dérivé des signaux runtime existants ;
3. des feature flags pour activer `tester` ou `prod_showable` ;
4. des profils A/B/C pour moduler l’intensité visuelle de la ludification.[file:2][file:3]

## Signaux source autorisés

Utilise uniquement des signaux déjà produits par le runtime, notamment :
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

## Contrat dérivé à produire

Définis et implémente un `EngagementUIModel` contenant au minimum :
- `scene_progress` ;
- `quest_cards` ;
- `persistent_objects` ;
- `symbolic_rewards` ;
- `gamification_profile` ;
- `ui_visibility_flags`.[file:3]

## UX attendue pour `prod_showable`

Créer une vue session apprenant avec 4 zones :
1. fil conversationnel ;
2. progression visible de scène ;
3. quêtes courtes ;
4. panneau “traces et acquis”.[file:3]

### Progression visible

Mapping recommandé :
- `Raconter` ;
- `Comprendre` ;
- `Décider` ;
- `Retenir` ;
- `Transmettre`.[file:1][file:3]

### Quêtes courtes

Prévoir 1 à 3 cartes dérivées du manque utile actuel, par exemple : clarifier, comprendre, décider, transmettre.[file:3]

### Objets persistants MVP

Prévoir au minimum :
- trace prête à transmettre ;
- compétence mobilisée illustrée ;
- capsule de progrès.[file:3][file:18]

### Récompenses symboliques MVP

Prévoir au minimum :
- badges ;
- thèmes visuels ;
- variantes sobres d’avatar Hugo.[file:2][file:3]

## Implémentation front

- Crée `TesterLayout` et `ProdLearnerLayout` si nécessaire.[file:3]
- Ajoute `frontend_mode = tester | prod_showable`.[file:3]
- Ajoute `engagement_ui_enabled`, `scene_progress_enabled`, `persistent_objects_enabled`, `symbolic_rewards_enabled`, `gamification_profile`.[file:3]
- Masque tout label, réglage ou artefact debug dans `prod_showable`.[file:3]

## Implémentation backend

- Réutilise les endpoints Hugo existants autant que possible.[file:18]
- Si nécessaire, crée une projection dérivée dédiée du type `GET /hugo/sessions/{session_id}/engagement-view`.[file:3][file:18]
- Ne modifie pas le contrat central du moteur pour supporter la ludification.[file:1][file:3]

## Tests attendus

- Test de non-régression moteur avant/après en mode testeur.[file:1]
- Test de stabilité des règles 0/1/2 question.[file:1]
- Test de cohérence du `EngagementUIModel` à partir de cas de scène réels.[file:1][file:3]
- Test de masquage complet des éléments debug en mode `prod_showable`.[file:3]

## Résultat attendu

Un diff propre qui :
- conserve le front testeur/debug ;
- introduit une variante prod montrable activable ;
- ne casse pas P0 ;
- ne mélange pas instrumentation moteur et UX apprenant ;
- permet une première démo client crédible rapidement.[file:1][file:3]

## Sources de vérité à utiliser pendant l’implémentation

Utilise par priorité :
1. le document P0 actuel pour le moteur ;
2. Hugo 1.6 pour la doctrine ;
3. les documents 1.8 pour la ludification ;
4. la SPEC POC 1.5 patchée pour le cadre technique et API.[file:1][file:2][file:3][file:18][file:20]
