
## 1. Objet du document

Ce document spécifie **Hugo 1.8 – branche prod montrable**, à implémenter sans casser l’existant, en conservant le front actuel comme **front testeur/debug** et en créant une variante **prod_showable** destinée à la démonstration client et à de premiers tests terrain.[^3][^1]
La cible n’est **pas** un nouveau moteur Hugo, mais une bifurcation frontale et produit, adossée au même backend Django orchestré et au même noyau P0 de régulation tutorale piloté par état.[^4][^2][^3]

## 2. Sources de vérité

Ordre de vérité documentaire à respecter pour toute implémentation 1.8 :

1. `p0_description_technique_actuelle_mise_a_jour.md` pour l’état réel du moteur, du `TurnState`, de `ConversationDecision`, du pipeline et des guardrails.[^4]
2. `Hugo-1.6-Cadrage-Transformation-du-comportement.md` pour la doctrine de fond, les invariants de posture, de mémoire, de confidentialité, de repo-first et de moteur piloté par état.[^2]
3. `Quel-type-dengagement-vise-t-on-en-priorite-__Ret-2.md` et `Nous-ouvrons-ici-le-chantier-Hugo-1.8-centre-sur-3.md` pour le cadrage 1.8 de ludification au service de l’apprentissage.[^5][^1]
4. `SPEC_POC_v1.5-update-27_03_2026.md` pour le cadre plateforme, Django, TutorPrompt, API, multi-tenant, confidentialité, responsive webapp, tant qu’il n’entre pas en conflit avec 1.7/P0 actuel.[^3]

## 3. Décision centrale

**Décision produit-technique** : Hugo 1.8 ne redéfinit pas Hugo 1.7/P0. Hugo 1.8 ajoute une couche de progression visible, de quêtes courtes, d’objets persistants et de récompenses symboliques, calculée à partir des signaux déjà produits par le runtime existant, et exposée dans une nouvelle variante de front montrable.[^1][^4]
Cette couche ne décide jamais du geste tutoriel, ne modifie pas `TurnState`, ne modifie pas `ConversationDecision`, ne déplace pas le pilotage vers le LLM, et ne court-circuite pas `TutorPrompt` ni l’orchestrateur Django.[^2][^3][^4]

## 4. Invariants non négociables

### 4.1 Invariants moteur

Doivent être conservés tels quels :

- chaîne runtime actuelle `build_hugo_turn()` → `analyze_turn_state()` → `classify_p0_turn_state()` → `decide_conversation()` → `build_teaching_plan()` → `decide_next_phase()` → `render_with_tutor_prompt()` → guardrails de sortie.[^3][^4]
- logique backend orchestrée dans Django.[^4][^3]
- `TutorPrompt` comme brique de configuration runtime, avec priorité session → groupe → organisation.[^3]
- hiérarchie de décision actuelle, qui priorise protection, clôture explicite, répétition explicite, aide explicite, sécurité/qualité, contradiction, clôture possible, puis approfondissement.[^4]
- règles 0/1/2 question et guardrails associés.[^4]
- idée qu’un message Hugo poursuit un seul objectif de régulation.[^2][^3]


### 4.2 Invariants produit

Doivent être préservés :

- posture AFEST, réflexive, non magistrale, sans jugement ni validation autonome.[^2][^3]
- référentiel-first, mémoire gouvernée, RAG situé et non dominant.[^3][^2]
- confidentialité-first, partage explicite, non-exposition du verbatim non partagé aux rôles humains.[^2][^3]
- repo-first : la spec prime, puis règles Cursor/docs/tests, puis implémentation.[^3][^2]


### 4.3 Invariants 1.8

Doivent être respectés :

- engagement au service de l’apprentissage, pas l’inverse.[^5][^1]
- priorités d’engagement hiérarchisées : profondeur de réflexion > complétude de scène jusqu’au mini-bilan/texte tuteur > retour régulier dans l’app.[^1][^5]
- pas de leaderboard, pas de scoring scolaire opaque, pas de streak central, pas de monnaie virtuelle, pas de loot aléatoire, pas de réouverture artificielle des scènes.[^5][^1]
- hypothèse d’architecture préférée : P0 inchangé ou presque, petit engagement engine léger à côté de P0, UI qui rend visible cette progression.[^1]


## 5. Ce que Hugo 1.8 doit être

Hugo 1.8 doit être une **première proposition produit montrable**, où l’utilisateur voit mieux ce qu’il est en train d’accomplir dans une scène, ce qu’il a déjà consolidé, ce qu’il peut transmettre, et ce qu’il a débloqué de façon symbolique grâce à un usage utile de l’app.[^1]
Cette version doit rendre l’expérience plus désirable sans altérer la qualité tutorale : plus de lisibilité, plus de sentiment d’avancer, plus de traces exploitables, plus de complétude utile.[^1][^4]

## 6. Ce que Hugo 1.8 ne doit surtout pas devenir

Hugo 1.8 ne doit pas devenir :

- une refonte du moteur P0,[^4][^1]
- un système ludique qui pilote les tours à la place de `decide_conversation()`,[^1][^4]
- une seconde architecture conversationnelle parallèle,[^2][^3]
- une couche de rétention vide favorisant le temps passé, le bavardage ou la complétion artificielle,[^5][^1]
- une UX infantilisante ou incompatible avec un contexte pro sérieux.[^5][^1]


## 7. Split des deux fronts

### 7.1 Front testeur / debug conservé

Le front actuel reste la surface de calibration, d’inspection et de non-régression.[^3][^1]
Il conserve notamment :

- affichage détaillé de `TurnState` et de ses dérivés, y compris `covered_points`, `remaining_open_points`, `learner_help_request`, `closure_signal`, `repetition_signal`, `loop_risk`, `session_maturity`, `evidence_strength`, `can_close_for_now`, etc.[^4]
- affichage de `ConversationDecision`, y compris `pedagogical_move`, `number_of_questions`, `question_style`, `response_constraints`, `reason_codes`.[^4]
- réglages de runtime, phase, classifier-config, TutorPrompt actif, instrumentation de prompt/rendu si autorisée en sandbox/dev.[^3][^4]
- toute UI utile pour voir et tester la logique réelle du moteur.[^4]


### 7.2 Front prod montrable à créer

Le front prod montrable est une variante UI épurée, destinée à l’apprenant et à la démo client.[^1]
Il masque toute la plomberie et rend visibles seulement des éléments compréhensibles produit :

- conversation Hugo,[^1]
- progression visible de scène,[^1]
- quêtes courtes de complétude,[^1]
- objets persistants,[^1]
- mini-bilan / trace prête,[^3][^1]
- récompenses symboliques sobres.[^1]


### 7.3 Commun aux deux

Les deux fronts partagent :

- le même backend Django,[^3]
- les mêmes endpoints métier Hugo,[^3]
- le même moteur P0 et les mêmes contrats tutoraux,[^4]
- les mêmes règles de confidentialité, de partage et de multi-tenant.[^2][^3]


## 8. Architecture cible 1.8

### 8.1 Principe général

Architecture cible 1.8 :

- **P0 inchangé**,[^4][^1]
- **Engagement Engine léger dérivé**,[^1]
- **Prod UI model** construit à partir des sorties runtime existantes,[^4][^1]
- **coexistence de deux variantes UI** sur la même base applicative.[^3][^1]


### 8.2 Placement de l’Engagement Engine

L’Engagement Engine doit être placé **hors P0**, dans la couche produit/backend applicatif ou dans une couche d’adaptation dédiée, mais jamais dans `analyze_turn_state()` ni dans `decide_conversation()`.[^4][^1]
Il lit les signaux existants, calcule des dérivés d’engagement et alimente l’UI montrable.[^4][^1]
Il n’a **aucun effet rétroactif** sur le geste tutoriel, le nombre de questions, la phase, le prompt ou les guardrails.[^1][^4]

### 8.3 Variables source autorisées

Les variables qu’il peut consommer doivent provenir des sorties existantes du runtime, notamment :

- `covered_points`, `remaining_open_points`,[^4]
- `session_maturity`, `evidence_strength`, `can_close_for_now`,[^4]
- `learner_help_request`, `closure_signal`, `repetition_signal`, `loop_risk`,[^4]
- `reflective_depth`, `recent_progress`, `has_concrete_actions`, `episode_clarity`,[^4]
- `last_tutorial_move`, `consecutive_clarify_turns`, `sticky_has_concrete_actions` si utile pour des feedbacks plus fins.[^4]

Aucun nouveau champ P0 ou champ `ConversationDecision` ne doit être ajouté dans ce lot pour supporter 1.8.[^1][^4]

## 9. Modèle dérivé recommandé

Créer un modèle dérivé côté produit, par exemple `EngagementUIModel`, de la forme suivante :

- `scene_progress` : état de progression visible dans la scène.[^1][^4]
- `quest_cards` : 1 à 3 quêtes courtes pertinentes.[^1]
- `persistent_objects` : objets déjà acquis ou en cours.[^1]
- `symbolic_rewards` : récompenses débloquées.[^1]
- `gamification_profile` : A/B/C.[^5][^1]
- `ui_visibility_flags` : ce qui doit être affiché ou masqué selon le mode.[^1]

Ce modèle doit être stable pour le front et découplé des détails internes P0, même s’il est calculé à partir d’eux.[^4][^1]

## 10. Mapping produit recommandé

### 10.1 Progression visible de scène

La progression visible doit être dérivée des `covered_points` et `remaining_open_points`, mais exprimée dans un langage produit simple.[^4][^1]
Mapping recommandé MVP :

- **Raconter** : épisode et actions concrètes posés.[^4]
- **Comprendre** : problème nommé, cause amorcée.[^4]
- **Décider** : action future ou règle d’action formulée.[^4]
- **Retenir** : règle ou apprentissage formulé.[^4]
- **Transmettre** : mini-bilan ou texte tuteur prêt / scène clôturable.[^1][^4]

Ce mapping doit rester descriptif et non prescriptif : il montre où en est la scène, il ne transforme pas la conversation en tunnel scripté.[^1][^4]

### 10.2 Quêtes courtes

Les quêtes courtes doivent être des reformulations UX de micro-accomplissements pédagogiques réels.[^1]
Exemples MVP :

- Clarifier la situation.[^1][^4]
- Nommer le vrai problème.[^4]
- Identifier une cause plausible.[^4]
- Formuler la prochaine action.[^4]
- Préparer un texte utile pour le tuteur.[^3][^1]

Une quête ne récompense jamais un volume de messages ni du temps passé.[^1]

### 10.3 Objets persistants

Les objets persistants MVP recommandés sont :

1. **Traces prêtes à transmettre** : mini-bilan, texte pour tuteur, trace exploitable.[^3][^1]
2. **Compétences mobilisées illustrées** : visualisation honnête d’une compétence mobilisée dans la scène, sans prétendre à une validation autonome par Hugo.[^3][^1]
3. **Capsules de progrès** : matérialisation de vrais sauts utiles, par exemple sortie de blocage, meilleure formulation transmissible, amélioration d’un type de scène.[^1]

### 10.4 Récompenses symboliques

Les récompenses symboliques MVP autorisées sont :

- thèmes visuels,[^5][^1]
- badges,[^5][^1]
- variantes sobres d’avatar Hugo.[^5][^1]

Ne pas inclure dans 1.8 :

- renommage libre de Hugo,[^5]
- profils de style “fun” type marseillais/cockney,[^5]
- monnaie virtuelle, coffres, loot, score global, leaderboard.[^5][^1]


## 11. Profils de ludification

Implémenter trois profils de ludification configurables côté produit :

- **Profil A** : ludique assumé, cible 16–25.[^5][^1]
- **Profil B** : intermédiaire.[^5]
- **Profil C** : sobre pro.[^5][^1]

Ces profils modulent uniquement :

- intensité visuelle,[^5]
- fréquence des feedbacks visuels,[^5]
- niveau d’animation,[^5]
- explicitation de la couche ludique.[^5]

Ils ne modifient pas les conditions d’obtention, la doctrine tutorale, le geste du moteur ni les règles 0/1/2 question.[^1][^4]

## 12. UX cible du front prod montrable

### 12.1 Vue session apprenant

Créer une page de session prod montrable avec 4 zones :

1. **Zone conversation principale** : fil Hugo / apprenant propre, sans instrumentation.[^1]
2. **Zone progression** : rail ou barre de progression de scène.[^1]
3. **Zone quêtes / objectifs utiles** : 1 à 3 cartes d’accomplissement en cours.[^1]
4. **Zone traces \& acquis** : panneau latéral ou drawer montrant mini-bilan, objets persistants, déblocages.[^1]

### 12.2 Ce qui doit être visible

Doivent être visibles :

- ce qui a déjà été clarifié,[^4][^1]
- ce qui manque pour compléter utilement la scène,[^4][^1]
- si une trace partageable est prête,[^3][^1]
- ce qui a été débloqué par accomplissement réel.[^1]


### 12.3 Ce qui doit être masqué

Doivent être masqués pour l’utilisateur standard :

- détail P0,[^4]
- `ConversationDecision`,[^4]
- `reason_codes`,[^4]
- phase runtime,[^4]
- flags de classifier,[^3]
- réglages de prompt/session,[^3]
- instrumentation de debug.[^1]


## 13. Intégration front recommandée

### 13.1 Variante UI

Implémenter deux variantes UI dans la même app :

- `TesterLayout`,[^1]
- `ProdLearnerLayout`.[^1]

La logique métier et les appels API de base restent communs ; seules changent la projection, la présentation et les composants spécialisés.[^3][^1]

### 13.2 Feature flags

Introduire au minimum les flags suivants :

- `frontend_mode = tester | prod_showable`, [^1]
- `engagement_ui_enabled`,[^1]
- `scene_progress_enabled`,[^1]
- `persistent_objects_enabled`,[^1]
- `symbolic_rewards_enabled`,[^1]
- `gamification_profile = A | B | C`. [^5][^1]

Activation possible par environnement, org, groupe, ou utilisateur pilote.[^3][^1]

### 13.3 Routes

Recommandation simple :

- garder les routes debug existantes ou leurs équivalents,[^1]
- créer une route prod montrable dédiée, par exemple `/app/session/:id`.[^1]

Les deux peuvent lire les mêmes endpoints backend de session Hugo.[^3][^4]

## 14. Intégration backend recommandée

### 14.1 Endpoints existants à réutiliser

Réutiliser en priorité les endpoints Hugo existants :

- `POST /hugo/sessions`,[^3]
- `GET /hugo/sessions/{session_id}`,[^3]
- `POST /hugo/sessions/{session_id}/messages`,[^3]
- `POST /hugo/sessions/{session_id}/generate-trace`,[^3]
- `POST /traces/{trace_id}/validate`,[^3]
- `POST /hugo/sessions/{session_id}/share`,[^3]
- `GET /learners/sessions`, `GET /learners/traces`, `GET /learners/evidence` pour historique si utile au hub.[^3]


### 14.2 Projection supplémentaire recommandée

Si les payloads existants ne suffisent pas à alimenter proprement le front prod, créer une **projection dérivée** sans toucher au contrat central du moteur, par exemple :

- `GET /hugo/sessions/{session_id}/engagement-view`[^3][^1]
ou
- enrichissement contrôlé de la vue session retournée au front, côté applicatif.[^3][^1]

Le but est d’exposer un modèle UI propre, pas d’ouvrir plus d’internals P0 côté prod.[^4][^1]

## 15. Contraintes sécurité, confidentialité, observabilité

La branche prod montrable doit rester conforme à la doctrine existante :

- multi-tenant strict avec `organisation_id` et RLS.[^2][^3]
- partage explicite uniquement.[^2][^3]
- pas d’exposition du verbatim non partagé aux rôles non apprenant.[^2][^3]
- pas de logs bruts de contenu dans les surfaces métier.[^2]

L’UI 1.8 ne doit jamais contourner les `share_*` flags existants en affichant une trace ou un objet à des rôles qui ne devraient pas le voir.[^2][^3]

## 16. Critères d’acceptation fonctionnels 1.8

La version 1.8 MVP est acceptable si :

- le moteur P0 se comporte à l’identique en mode testeur avant/après branchement 1.8.[^4]
- aucune logique d’engagement n’a été injectée dans `TurnState` ou `ConversationDecision`.[^4][^1]
- le front prod montrable masque entièrement l’instrumentation interne.[^1]
- la progression visible de scène est alimentée par des signaux réels et non par du temps passé.[^4][^1]
- au moins 3 dispositifs POC sont opérationnels : progression visible, objets persistants, récompenses symboliques niveau 1.[^5][^1]
- les profils A/B/C modulent bien l’expression sans changer la logique tutorale.[^5][^1]
- le mini-bilan / texte pour tuteur est visible comme accomplissement de complétude.[^1]


## 17. Plan d’implémentation Cursor

### Lot 0 — Verrouillage documentaire

- Écrire une ADR “Hugo 1.8 = sidecar engagement + prod_showable UI, P0 unchanged”.[^2][^1]
- Documenter noir sur blanc les non-objectifs : pas de refonte moteur, pas de nouveaux champs P0, pas de pilotage par le jeu.[^4][^1]


### Lot 1 — Cartographie technique

- Identifier les services et serializers utilisés par le front actuel.[^3][^4]
- Lister les champs runtime réellement disponibles au front ou facilement exposables.[^4]
- Établir le mapping source runtime → dérivé UI.[^4][^1]


### Lot 2 — Contrat EngagementUIModel

- Définir le schéma JSON du modèle d’engagement dérivé.[^1]
- Implémenter le calcul minimal côté applicatif.[^3][^1]
- Ajouter tests unitaires sur le mapping des états de scène.[^4][^1]


### Lot 3 — Feature flags et coexistence

- Introduire `frontend_mode` et `gamification_profile`.[^5][^1]
- Garantir la coexistence propre testeur/prod.[^1]
- Ajouter garde-fou de non-régression sur le mode testeur.[^4]


### Lot 4 — Layout prod montrable

- Créer `ProdLearnerLayout`.[^1]
- Recomposer la page session apprenant.[^1]
- Masquer toute instrumentation.[^1]


### Lot 5 — Progression visible

- Implémenter le composant de progression de scène.[^4][^1]
- Brancher le mapping `covered_points` / `remaining_open_points`.[^4]
- Vérifier qu’aucune séquentialité forcée ne pollue l’expérience.[^1]


### Lot 6 — Quêtes et objets persistants

- Créer les cartes de quêtes courtes.[^1]
- Implémenter les 3 types d’objets persistants MVP.[^3][^1]
- Brancher mini-bilan / texte tuteur comme trace valorisée.[^3][^1]


### Lot 7 — Récompenses symboliques et profils

- Implémenter badges/thèmes/avatar sobre.[^5][^1]
- Brancher profils A/B/C.[^5]
- Tester les variantes visuelles.[^5]


### Lot 8 — QA démo

- Vérifier responsive, propreté visuelle, masquage debug.[^3][^1]
- Vérifier non-régression côté moteur.[^4]
- Préparer un scénario de démo standard.[^1]


## 18. Stratégie git recommandée

Stratégie simple recommandée :

- branche socle commune (`main` ou équivalent),[^3]
- branche `tester-debug` qui conserve la surface actuelle,[^1]
- branche `prod-showable-1.8` pour la variante montrable.[^1]

Tous les changements backend génériques et sûrs remontent au socle commun.[^3]
Les différences UX, layout, projection et gamification restent dans la branche prod tant qu’elles ne sont pas stabilisées.[^1]

## 19. Ce qui peut être mocké dans le premier lot

Peut être simplifié ou partiellement mocké pour la première proposition montrable :

- diversité des badges et thèmes,[^1]
- richesse du hub d’objets persistants,[^1]
- certaines capsules de progrès longitudinales si leur calcul réel est encore fragile.[^1]

En revanche, ne doivent pas être fake si la démo veut être crédible :

- progression de scène branchée sur des signaux réels,[^4][^1]
- mini-bilan / trace prête,[^3][^1]
- séparation nette entre front testeur et front montrable.[^1]


## 20. Format exact à déposer dans Cursor

Je te recommande de déposer cette spec dans Cursor sous 4 artefacts distincts, pas dans un seul pavé.[^2][^3]

- `docs/specs/hugo-1.8-prod-showable-spec.md` : la spec fonctionnelle et technique principale.[^2][^3]
- `docs/adr/ADR-hugo-1.8-engagement-sidecar.md` : la décision d’architecture “P0 untouched / sidecar engagement engine”.[^2][^1]
- `docs/tasks/hugo-1.8-cursor-implementation-plan.md` : la découpe en lots et tâches Cursor.[^3][^1]
- `docs/qa/hugo-1.8-acceptance-checklist.md` : les critères d’acceptation et de non-régression.[^3][^4]


## 21. Prompt de lancement Cursor pour le CTO

Tu peux donner à ton CTO ce prompt de départ, quasiment tel quel :[^3][^1]

> Implémente Hugo 1.8 comme une variante `prod_showable` de l’application existante, sans modifier le moteur P0 ni ses contrats.
> Respecte strictement la chaîne runtime actuelle Django `build_hugo_turn -> analyze_turn_state -> classify_p0_turn_state -> decide_conversation -> build_teaching_plan -> decide_next_phase -> render_with_tutor_prompt -> output guardrails`.[^3][^4]
> N’ajoute aucun champ à `TurnState` ni à `ConversationDecision` pour la gamification.[^4][^1]
> Crée une couche dérivée `EngagementUIModel` alimentée à partir des champs runtime existants (`covered_points`, `remaining_open_points`, `session_maturity`, `evidence_strength`, `can_close_for_now`, `learner_help_request`, `closure_signal`, `repetition_signal`, `loop_risk`, `reflective_depth`, `recent_progress`, `has_concrete_actions`, `episode_clarity`).[^4]
> Crée deux variantes UI coexistantes : `tester/debug` conservée et `prod_showable` montrable.[^1]
> Implémente dans `prod_showable` : progression visible de scène, quêtes courtes, objets persistants MVP, récompenses symboliques niveau 1, profils A/B/C.[^5][^1]
> Le système ludique n’a aucun droit de modifier le geste tutoriel, le nombre de questions, la phase, ni les guardrails.[^4][^1]
> Produit les fichiers de code, tests et docs nécessaires, avec feature flags permettant d’activer la variante prod montrable sans casser le front testeur.[^3][^1]

## 22. Recommandation nette

Si ton objectif est que ton CTO “dépose intelligemment” dans Cursor, il ne faut pas lui donner seulement une vision produit. Il faut lui donner **ce document + l’ADR + le plan de tâches + le prompt de lancement**. C’est cette combinaison qui respecte le mode repo-first/spec-first décrit dans vos documents et évite que Cursor parte en refonte ou en UI-gadget déconnectée du moteur.[^2][^3][^1]

## Arbitrages encore à décider

- Calcul de `EngagementUIModel` côté backend applicatif ou côté front via adaptateur local.[^3][^1]
- Nombre exact d’étapes de progression visible : 4 ou 5.[^4][^1]
- Niveau minimal de persistance réelle des objets 1.8 dès le premier lot.[^3][^1]
- Périmètre initial des profils : livrer A/B/C d’emblée ou commencer par B/C.[^5][^1]
- Wording produit final de “compétences mobilisées” pour éviter toute ambiguïté avec une validation formelle.[^3][^1]

