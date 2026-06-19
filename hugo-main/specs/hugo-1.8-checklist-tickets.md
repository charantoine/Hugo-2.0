# Hugo 1.8 — Checklist de tickets ultra-opérationnelle

## Ticket 1 — Verrouillage de périmètre

**Objectif** : figer le fait que Hugo 1.8 n’altère pas P0.[file:1][file:3]

**À faire**
- Écrire et committer l’ADR.
- Ajouter une note de garde-fou dans la doc repo.
- Documenter les non-objectifs explicites du lot.

**Livrable attendu**
- ADR committée.
- Garde-fous visibles dans la doc d’implémentation.

**Risque principal**
- Dérapage vers une refonte implicite du moteur.[file:1][file:3]

## Ticket 2 — Cartographie des signaux runtime

**Objectif** : identifier tous les champs runtime réutilisables pour le front prod montrable.[file:1]

**À faire**
- Cartographier les champs de `TurnState` exploitables.
- Cartographier les dérivés de `ConversationDecision` utiles à l’UI.
- Rédiger le tableau source runtime -> transformation -> usage produit.

**Livrable attendu**
- Mapping validé par le CTO.

**Risque principal**
- Mélanger variable technique brute et affordance UX.[file:1][file:3]

## Ticket 3 — Définition du `EngagementUIModel`

**Objectif** : définir le contrat dérivé stable côté produit.[file:3]

**À faire**
- Définir `scene_progress`.
- Définir `quest_cards`.
- Définir `persistent_objects`.
- Définir `symbolic_rewards`.
- Définir `gamification_profile`.
- Définir les flags de visibilité.

**Livrable attendu**
- Schéma JSON stable et committé.

**Risque principal**
- Recréer un second moteur de décision au lieu d’un modèle dérivé.[file:3][file:1]

## Ticket 4 — Implémentation de la projection dérivée

**Objectif** : fournir au front prod un modèle propre sans toucher au noyau tutoriel.[file:1][file:3]

**À faire**
- Choisir backend dérivé ou adaptateur front.
- Implémenter le calcul du `EngagementUIModel`.
- Ajouter des tests unitaires sur le mapping.

**Livrable attendu**
- Modèle dérivé calculé à partir des signaux réels.

**Risque principal**
- Toucher au contrat central du moteur pour “faire simple”.[file:1][file:3]

## Ticket 5 — Feature flags et variantes UI

**Objectif** : permettre la coexistence testeur/prod montrable.[file:3]

**À faire**
- Ajouter `frontend_mode`.
- Ajouter `engagement_ui_enabled`.
- Ajouter `scene_progress_enabled`.
- Ajouter `persistent_objects_enabled`.
- Ajouter `symbolic_rewards_enabled`.
- Ajouter `gamification_profile`.

**Livrable attendu**
- Deux variantes UI activables séparément.

**Risque principal**
- Duplication désordonnée ou couplage fort des deux fronts.[file:3]

## Ticket 6 — Création du layout prod montrable

**Objectif** : créer un layout apprenant propre et crédible.[file:3]

**À faire**
- Créer `ProdLearnerLayout`.
- Créer la page session prod montrable.
- Retirer toute instrumentation visible.
- Revoir le wording pour qu’il soit produit et non technique.

**Livrable attendu**
- Une session montrable sans éléments de debug.

**Risque principal**
- Conserver trop d’artefacts du front testeur.[file:3]

## Ticket 7 — Composant progression visible

**Objectif** : rendre visible l’avancement réel de la scène.[file:1][file:3]

**À faire**
- Mapper les points couverts vers 4 ou 5 étapes UX.
- Afficher l’étape active.
- Afficher les jalons franchis.
- Afficher les points encore ouverts en langage non technique.

**Livrable attendu**
- Une progression lisible et branchée sur des signaux réels.

**Risque principal**
- Rigidifier artificiellement la conversation.[file:1][file:3]

## Ticket 8 — Quêtes courtes

**Objectif** : ajouter 1 à 3 quêtes d’accomplissement utile.[file:3]

**À faire**
- Définir la logique de sélection des quêtes.
- Créer le composant des cartes de quêtes.
- Vérifier qu’aucune quête ne récompense le temps passé ou le bavardage.

**Livrable attendu**
- Quêtes branchées sur le manque utile actuel.

**Risque principal**
- Gamification creuse ou incitation à répondre pour “faire monter la jauge”.[file:3]

## Ticket 9 — Objets persistants MVP

**Objectif** : matérialiser les acquis utiles de scène.[file:3][file:18]

**À faire**
- Créer l’objet “trace prête”.
- Créer l’objet “compétence mobilisée illustrée”.
- Créer l’objet “capsule de progrès”.

**Livrable attendu**
- Au moins 3 objets persistants visibles dans l’UI prod.

**Risque principal**
- Employer un vocabulaire laissant croire à une validation formelle automatique.[file:3][file:18]

## Ticket 10 — Récompenses symboliques

**Objectif** : donner un feedback gratifiant mais sobre.[file:2][file:3]

**À faire**
- Implémenter badges.
- Implémenter thèmes visuels.
- Implémenter variantes sobres d’avatar Hugo.

**Livrable attendu**
- Au moins un déblocage symbolique visible sans scoring opaque.

**Risque principal**
- Faire gadget ou infantilisant.[file:2][file:3]

## Ticket 11 — Profils A/B/C

**Objectif** : adapter l’intensité de la couche ludique selon le contexte.[file:2][file:3]

**À faire**
- Implémenter profil A.
- Implémenter profil B.
- Implémenter profil C.
- Vérifier que seul l’habillage change.

**Livrable attendu**
- Profils opérationnels modulant l’expression, pas la logique tutorale.

**Risque principal**
- Glissement des profils vers des comportements tutoriels différents.[file:1][file:3]

## Ticket 12 — Non-régression moteur

**Objectif** : prouver que P0 n’a pas été altéré.[file:1]

**À faire**
- Tester le mode testeur avant/après.
- Vérifier stabilité des règles 0/1/2 question.
- Vérifier stabilité des reason codes et priorités.

**Livrable attendu**
- Rapport de non-régression moteur.

**Risque principal**
- Altération discrète des services d’orchestration existants.[file:1][file:18]

## Ticket 13 — QA de démo

**Objectif** : rendre la branche prod montrable démontrable en client-facing.[file:3]

**À faire**
- Vérifier responsive.
- Vérifier masquage complet du debug.
- Vérifier wording produit.
- Vérifier scénario complet de scène jusqu’au mini-bilan.
- Vérifier qu’aucun écran n’expose de labels internes moteur.

**Livrable attendu**
- Démo client propre, stable et crédible.

**Risque principal**
- Démo visuellement propre mais conceptuellement trop proche de l’outil de test.[file:3]
