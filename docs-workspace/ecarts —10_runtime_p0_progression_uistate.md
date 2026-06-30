# Rapport d’écarts — domaine runtime / P0 / progression / UIState

> **Mise à jour post-cluster 16 — 2026-06-18** · `conv-hugo-post-tests-c16`  
> **Confirmé local :** UIState, CTA (`ui.advisory`), `conversation_mode` + `allowed_posture_transitions`, `dispersion_risk`, set-posture (`test_cluster16_interface_apprenant_backend.py`, cluster 4/15).  
> **PARTIEL+ :** sélecteur posture (`PostureSelector.vue`), bandeau scène (`LearnerSceneContextBar.vue`). **A_VÉRIFIER :** v17 prod, Encoors.  
> Rapports : `rapport_mise_a_jour_doc_post_cluster16_2026-06-18.md`, `cluster16_interface_apprenant_resultats_tests.md`

## 0. Statut du document

Ce document est un **rapport d’écarts de domaine** destiné au pack CTO local. Il ne remplace ni la spec canonique 2.0, ni les audits du réel, ni le glossaire d’alignement. Il sert à formuler proprement, sur un périmètre restreint, les écarts entre la **cible doctrinale 2.0** et le **Hugo réel audité**, au bon niveau de détail pour préparer les corrections documentaires et les futurs chantiers d’implémentation.[file:35][file:38][file:12]

Ce document doit être lu avec la hiérarchie de vérité suivante en tête : le code et les tests priment pour décrire le réel, la spec 2.0 prime pour décrire la cible, et les documents intermédiaires comme celui-ci servent uniquement à **raccorder**, **qualifier** et **préparer l’action**.[file:12][file:35]

## 1. Objet du domaine

Le périmètre de ce rapport couvre le **noyau conversationnel montrable** de Hugo cœur, à savoir :

- la chaîne runtime conversationnelle backend ;
- le noyau de régulation locale **P0** ;
- le **contrat de décision** produit par cette régulation ;
- la **progression conversationnelle** inter-tours ;
- la traduction produit vers le front au travers du **UIState**.[file:35][file:38]

Ce rapport ne couvre pas en détail :

- les prompts eux-mêmes ;
- la mémoire gouvernée inter-session au-delà de son point de raccord avec ce pipeline ;
- le workflow terminal complet de synthèse et d’évaluation ;
- les orchestrateurs formateur et tuteur ;
- les extensions Hugo & Cie.[file:35][file:38][file:12]

L’objectif est de répondre à une question simple : **sur ce bloc central, qu’est-ce qui est déjà bien aligné entre la doctrine 2.0 et le réel audité, qu’est-ce qui doit être renommé ou mieux documenté, et où se situent les risques de dérive si l’on corrige mal ?**[file:35][file:38]

## 2. Cible 2.0 sur ce bloc

La spec canonique 2.0 décrit Hugo cœur comme un moteur tutoriel multi-postures, piloté par état, avec backend Django orchestré, TutorPrompt comme pivot runtime, P0 comme noyau local de régulation, progression conversationnelle persistée, et UIState comme traduction produit montrable dérivée côté backend.[file:35]

Dans cette cible, le runtime conversationnel suit une chaîne stable en six temps :

1. construction du contexte ;
2. analyse du tour apprenant ;
3. décision tutorale locale ;
4. rendu du prompt via TutorPrompt ;
5. appel LLM ;
6. post-traitement, garde-fous, journalisation technique et persistance.[file:35]

Le P0 reste le régulateur local commun. Il s’appuie sur un état borné, produit un **contrat de décision** structuré, et ne doit pas être dupliqué par des sous-pipelines spécialisés ni contourné par le front.[file:35]

Le contrat de décision cible doit contenir au minimum :

- objectif primaire ;
- geste tutoral principal ;
- mode ou régime actif ;
- nombre cible de questions ;
- autorisation éventuelle de bundling ;
- autorisation éventuelle de micro-explication ;
- usage mémoire thématique ;
- usage de récupération verbatim interne ;
- priorité éventuelle d’overlay référentiel ;
- usage éventuel du RAG ;
- éligibilité éventuelle à l’évaluation ;
- `reason_codes` traçables.[file:35]

La progression conversationnelle cible repose non sur le dernier message seul, mais sur des **branches conversationnelles** avec branche prioritaire, maturité globale, risque de dispersion, conditions de synthèse, conditions d’évaluation et éléments manquants pour passer au niveau suivant.[file:35]

Le UIState cible est un **état produit dérivé**, lisible et stable, qui expose la scène de séance, la progression, la quête active, la couleur de maturité, la posture active si le produit choisit de l’exposer, et l’état des actions terminales, sans jamais exposer TurnState ni les champs P0 bruts au front.[file:35]

## 3. Réel audité sur ce bloc

Le glossaire d’alignement et les audits de référence montrent qu’il existe déjà un ancrage réel fort pour ce domaine, mais avec un vocabulaire d’implémentation plus concret que le vocabulaire doctrinal 2.0.[file:38][file:12]

### 3.1 Chaîne runtime observée

Le point d’entrée réel documenté est `buildhugoturn`, avec une séquence observée de services du type :

`buildhugocontext` → `resolveposture` → `analyzeturnstate` → `classifyp0turnstate` → `decideconversation` / `decideconversationv17` → `buildteachingplan` → `decidenextphase` → `selectragchunks` → `buildsessionmemory` → `buildconversationprogress` → `builduistate` → `renderwithtutorprompt`.[file:38]

Le réel audité confirme aussi que **TutorPrompt** est bien un pivot runtime important, avec coexistence de plusieurs chemins de rendu ou fallback, notamment `renderwithtutorprompt`, `buildafestpromptslegacy` et `rendertutorpromptv17`.[file:38]

### 3.2 P0 et décision locale

Le réel audité confirme un bon ancrage de la couche P0 via :

- `analyzeturnstate` ;
- `classifyp0turnstate` ;
- `decideconversation` ;
- des flags de coexistence type `HUGOP0V17ENABLED` et `HUGOP0CLASSIFIERENABLED`.[file:38]

Le glossaire indique que les variables de décision réellement observées incluent déjà une base très utile pour la future architecture des prompts et des contrats techniques :

- `primarygoal` ;
- `tutorialmove` ;
- `mode` ;
- `targetquestioncount` ;
- `microexplainallowed` ;
- `usethemememory` ;
- `useverbatimretrieval` ;
- `userag` ;
- `optionalevaluationeligible` ;
- `reasoncodes`.[file:38]

Le vocabulaire réel documenté ne parle toutefois pas directement de `DecisionContract` comme dans la doctrine 2.0. Le réel semble plutôt exprimer cette sortie structurée via `ConversationDecision`, `decisionstate` et `decideconversation`.[file:38]

### 3.3 Progression conversationnelle

Le réel documenté confirme un bon alignement de la progression via :

- `buildconversationprogress` ;
- `buildconversationprogresscontract` ;
- des tests dédiés ;
- des notions de branches actives, `prioritybranchid`, maturité `RED / ORANGE / GREEN`, `missingfornextlevel` et `reasoncodes`.[file:38]

La doctrine 2.0 et le réel convergent donc assez bien sur l’idée générale : la progression est un objet inter-tours structuré, centré sur branches, maturité et conditions de clôture, et non un simple calcul opportuniste côté front.[file:35][file:38]

### 3.4 UIState et projection produit

Le réel documenté montre une très bonne assise du vocabulaire produit avec :

- `builduistate` ;
- `uistatebuilder.py` ;
- l’endpoint `GET /hugo/sessions/{id}/ui-state`.[file:38]

Ce point est important car il confirme que la doctrine backend-first côté produit n’est pas purement spéculative : le réel expose déjà une projection UI dérivée côté backend, ce qui en fait un bon point d’ancrage pour les travaux correctifs de spec et de contrat.[file:38][file:35]

## 4. Écarts principaux

Sur ce domaine, les écarts observés ne sont pas principalement des contradictions de fond. Ce sont surtout des **écarts de formulation**, de **niveau d’abstraction** et de **stabilisation documentaire** entre la cible 2.0 et le réel audité.[file:35][file:38]

### 4.1 Écart 1 — chaîne runtime cible vs pipeline réel documenté

La spec 2.0 décrit une chaîne en six temps stable et doctrinale. Le réel audité documente une chaîne plus détaillée, plus “nommée code”, avec plusieurs services intermédiaires et une coexistence legacy / v17.[file:35][file:38]

L’écart n’est pas que la cible soit fausse. L’écart est que la spec 2.0 **n’explicite pas encore suffisamment** quels noms réels actuels portent ces étapes, ni comment la coexistence des chemins legacy / v17 doit être lue sans confusion.[file:38][file:35]

**Correction documentaire recommandée :**
- conserver la chaîne doctrinale 2.0 comme structure cible ;
- ajouter en annexe ou matrice backend les noms réels observés (`buildhugoturn`, `analyzeturnstate`, `buildconversationprogress`, `builduistate`, etc.) ;
- documenter explicitement la coexistence de variantes runtime derrière flags et fallback.[file:38][file:35]

### 4.2 Écart 2 — contrat de décision doctrinal vs vocabulaire réel de décision

La cible parle de **contrat de décision**. Le réel documenté parle plutôt de `ConversationDecision`, `decisionstate` et `decideconversation`.[file:35][file:38]

Ici, le problème n’est pas conceptuel. La logique de sortie structurée existe bien dans le réel, mais le nom doctrinal et le nom d’implémentation ne sont pas encore raccrochés proprement dans la documentation.[file:38]

**Correction documentaire recommandée :**
- conserver `contrat de décision` comme nom canonique pour raisonner juste ;
- faire apparaître explicitement qu’en l’état du développé, ce contrat correspond à `ConversationDecision` / `decisionstate` produits par `decideconversation` ;
- éviter de renommer toute la doctrine selon le nom des fonctions Python.[file:38][file:35]

### 4.3 Écart 3 — service de sélection de posture

La doctrine 2.0 parle d’un `PostureSelector` dédié. Le réel documenté fait surtout apparaître `resolveposture` dans le pipeline.[file:35][file:38]

Cette zone est marquée **AMBIGUË** dans le glossaire, ce qui signifie que l’idée fonctionnelle existe, mais que le mapping entre objet doctrinal propre et service réel observable n’est pas encore suffisamment net pour être figé sans relecture complémentaire du code.[file:38]

**Correction documentaire recommandée :**
- garder `PostureSelector` comme nom cible ;
- mentionner `resolveposture` comme nom réel observé à ce stade ;
- ne pas présenter comme acquis que l’objet/service canonique 2.0 est déjà implémenté sous cette forme stabilisée.[file:38]

### 4.4 Écart 4 — progression : bon alignement conceptuel, nomenclature encore hétérogène

La progression est l’une des zones les mieux alignées entre la cible et le réel. En revanche, la documentation 2.0 ne reprend pas encore suffisamment les noms réels observés comme `buildconversationprogress`, `buildconversationprogresscontract`, `prioritybranchid`, `missingfornextlevel` ou les niveaux de maturité `RED / ORANGE / GREEN`.[file:38][file:35]

**Correction documentaire recommandée :**
- garder `ConversationProgress` et `ConversationBranch` comme noms doctrinaux ;
- ajouter la colonne “nom réel observé” dans les matrices de services et d’objets ;
- stabiliser plus tard un dictionnaire canonique plus fin de maturité et de signaux dérivés.[file:38][file:35]

### 4.5 Écart 5 — UIState : alignement fort, contrat encore à formaliser

Le UIState est bien présent à la fois côté cible 2.0 et côté réel audité. L’écart principal n’est pas l’existence mais le **niveau de formalisation** du contrat.[file:35][file:38]

Autrement dit : la doctrine pose correctement le principe “backend dérive / front consomme”, et le réel montre `builduistate` et `ui-state`, mais la spec n’est pas encore descendue à un contrat quasi-JSON suffisamment figé pour éviter les ambiguïtés futures.[file:38][file:35]

**Correction documentaire recommandée :**
- conserver `UIState` comme objet canonique fort ;
- préparer une annexe ou matrice produit détaillant les champs visibles minimaux et les exclusions ;
- continuer à poser comme invariant qu’aucun champ P0 brut n’y figure.[file:35][file:38]

## 5. Risques de dérive et de régression

Le principal danger de cette passe n’est pas de “manquer un mot”. Le vrai risque est de **corriger les docs en reculant doctrinalement**.[file:35][file:38]

### 5.1 Risque 1 — recentrer la vérité sur le prompt

Parce que le réel contient plusieurs chemins de rendu et objets liés au prompt, il serait tentant de réécrire la spec comme si le vrai centre de décision était le prompt renderer. Ce serait une régression nette par rapport à la 2.0, qui pose clairement que la source de vérité comportementale résulte de l’orchestrateur backend, de P0, du contrat de décision, de la progression, du contexte structuré et de TutorPrompt, pas du prompt seul.[file:35]

### 5.2 Risque 2 — relire le réel comme un simple assistant AFEST historique

Le pipeline réel contient des traces legacy et des fallbacks historiques. Les réinjecter sans filtre dans la doc comme doctrine centrale ferait retomber Hugo vers une lecture mono-posture ou historiquement AFEST-centrée, alors que la 2.0 fixe un moteur tutoriel multi-postures piloté par état.[file:35][file:12][file:38]

### 5.3 Risque 3 — faire glisser le produit vers du front-driven

Le réel expose un endpoint `ui-state`, et la 2.0 pose clairement que le front consomme des états dérivés. Si les corrections documentaires deviennent floues, le risque est de réintroduire des formulations où le front “pilote” la progression, la posture ou la logique locale au lieu de les lire.[file:35][file:38]

### 5.4 Risque 4 — exposer P0 ou TurnState sous couvert de transparence

La tentation classique, lorsqu’on formalise un contrat produit, est de “montrer ce qu’il y a derrière”. Or la 2.0 fixe explicitement que TurnState et les champs P0 bruts ne doivent pas être consommés par le front.[file:35]

Toute correction documentaire qui laisserait entendre que `primarygoal`, `tutorialmove`, `reasoncodes` ou d’autres variables P0 sont des champs UI natifs ferait dériver l’architecture produit.[file:35][file:38]

### 5.5 Risque 5 — prendre les noms de fonctions réelles pour des objets canoniques stabilisés

Le glossaire sert de pont de vocabulaire, pas de réécriture complète de la doctrine par les noms du code. Si l’on confond trop vite `builduistate` avec le concept complet de `UIStateBuilder`, ou `resolveposture` avec un `PostureSelector` déjà parfaitement stabilisé, on fabrique une doc pauvre conceptuellement et fragile face aux évolutions futures.[file:38][file:35]

## 6. Garde-fous de correction

Pour corriger ce domaine sans dérive, les garde-fous suivants doivent être appliqués.

### 6.1 Garde-fous de formulation

- Garder les **noms doctrinaux 2.0** comme structure principale : runtime cible, P0, contrat de décision, progression conversationnelle, UIState.[file:35]
- Ajouter ensuite les **noms réels observés** dans le développé quand ils sont connus et utiles : `buildhugoturn`, `analyzeturnstate`, `decideconversation`, `buildconversationprogress`, `builduistate`, `ui-state`.[file:38]
- Ne jamais rebaptiser brutalement la doctrine à partir des seuls noms de fonctions Python.[file:38]

### 6.2 Garde-fous d’architecture

- Le runtime reste **backend Django orchestré**.[file:35]
- TutorPrompt reste **pivot runtime**, mais non source unique de vérité comportementale.[file:35]
- P0 reste **noyau local commun**, enrichi additivement, non dupliqué.[file:35]
- Le front reste **consommateur d’états dérivés**, pas moteur de décision.[file:35]
- UIState reste **propre, stable, non technique**, sans champs P0 bruts.[file:35]

### 6.3 Garde-fous de lecture du réel

- Une spec ne prouve pas le réel ; un nom observé dans le réel ne prouve pas qu’un concept cible est entièrement livré.[file:12][file:35]
- Toute zone `AMBIGU` ou `A_VERIFIER` du glossaire doit rester explicitement marquée comme telle tant qu’une relecture complémentaire du code ou des audits n’a pas été faite.[file:38]
- La coexistence legacy / v17 doit être documentée comme une **réalité du développé**, pas comme une justification pour baisser le niveau doctrinal de la cible.[file:38][file:35]

## 7. Décisions documentaires à préparer

À la suite de ce rapport, les corrections documentaires les plus utiles sur ce domaine sont les suivantes :

1. **Spec canonique 2.0 — matrice backend**  
   Ajouter les noms réels observés pour les services de ce domaine : `buildhugoturn`, `analyzeturnstate`, `decideconversation`, `buildconversationprogress`, `builduistate`, `renderwithtutorprompt`.[file:38][file:35]

2. **Spec canonique 2.0 — matrice des objets**  
   Ajouter une colonne “nom réel observé” pour :
   - contrat de décision ↔ `ConversationDecision` / `decisionstate` ;
   - progression ↔ `buildconversationprogress` ;
   - UIState ↔ `builduistate` / endpoint `ui-state`.[file:38][file:35]

3. **Complément 2.0 ou annexe d’alignement**  
   Ajouter un sous-bloc de raccord de vocabulaire :
   - `PostureSelector` ↔ `resolveposture` ;
   - `DecisionContract` ↔ `ConversationDecision` / `decisionstate` ;
   - `ProgressionCalculator` ↔ `buildconversationprogress` ;
   - `UIStateBuilder` ↔ `builduistate`.[file:38]

4. **Futur contrat produit UIState**  
   Préparer un document de niveau inférieur décrivant :
   - les champs visibles minimaux du UIState ;
   - les exclusions formelles ;
   - la frontière stricte entre état moteur et état produit.[file:35][file:38]

## 8. Points encore ouverts après cette passe

À ce stade, les points qui restent ouverts sur ce domaine sont les suivants :

- le niveau exact de formalisation à donner au **contrat quasi-JSON de UIState** ;[file:35][file:38]
- le degré de stabilisation réel de la logique de **sélection de posture** au-delà du nom `resolveposture` ;[file:38]
- la manière la plus propre de documenter la coexistence **legacy / v17** sans rendre la spec illisible ;[file:38][file:12]
- la frontière précise entre **contrat de décision interne**, **progression persistée** et **projection UI** dans les futures annexes techniques.[file:35][file:38]

## 9. Conclusion opérationnelle

Sur le domaine runtime / P0 / progression / UIState, la situation n’est pas celle d’un écart doctrinal massif. Le noyau conceptuel 2.0 est globalement **bien raccordable** au réel audité, mais la documentation doit encore mieux relier les **noms canoniques** aux **noms réellement observés**.[file:35][file:38]

Le bon geste n’est donc pas de réécrire la doctrine, mais de produire maintenant les documents suivants dans cet ordre :

1. une **matrice d’écarts détaillée** sur ce même domaine ;
2. une **annexe de vocabulaire réel observé** pour la spec 2.0 ;
3. un **contrat de UIState** plus précis ;
4. puis seulement les prompts Cursor ou tickets techniques dérivés.[file:38][file:35][file:12]