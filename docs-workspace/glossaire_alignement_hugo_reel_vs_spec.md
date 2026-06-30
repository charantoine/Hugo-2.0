# Glossaire d’alignement Hugo 2.0 vs Hugo réel audité

## Statut du document

Ce document est un **document de travail de bibliothèque** destiné à préparer les futurs chantiers d’analyse d’écarts entre le projet Hugo spécifié et le Hugo réellement développé. Son rôle n’est pas de réécrire la doctrine 2.0, ni de produire déjà une matrice complète d’écarts ; il sert à **ré-aligner le vocabulaire, les catégories et les objets** entre le corpus cible 2.0 et le corpus d’audit du réel.

Il doit être lu comme un **pont de vocabulaire contrôlé** entre deux corpus distincts :

- le corpus **Hugo réel audité**, qui décrit ce qui est observable dans Hugo développé ;
- le corpus **Hugo projet / cible 2.0**, qui décrit l’état visé et la doctrine de référence.

## Corpus mobilisés

### Corpus “Hugo réel audité”

Documents utilisés pour parler du réel :

- `00_HIERARCHIE_DOCUMENTAIRE.md`
- `01_CARTOGRAPHIE_WORKSPACE_REEL.md`
- `02_ETAT_MOTEUR_REEL.md`
- `03_ETAT_PRODUIT_REEL.md`
- `07_RUNTIME_DEMO_REFERENCE.md`
- `10_FICHE_RUNTIME_PROD_ENCOORS.md`

### Corpus “Hugo projet / cible 2.0”

Documents utilisés pour parler de la cible :

- `spec_canonique_hugo_2_0.md`
- `complement_unique_specs_2_0.md`
- `specs-Orchestrateur-diagnostic-2.0.md`
- `specs-formateur-tuteur-2.0.md`
- `specs-interface-2.0.md`
- `dernier-run-intercallaire.docx`

### Règle d’arbitrage

Les anciennes specs Hugo et les documents de commercialisation / storytelling peuvent aider à lever une ambiguïté, mais **la base 2.0 consolidée prime toujours** en cas de conflit. Le but de ce document n’est donc pas de réimporter l’ancien vocabulaire tel quel, mais de **reformuler ce qui est utile dans le vocabulaire 2.0 tout en le raccordant aux noms réellement utilisés** dans Hugo développé.

## Objet précis de cette passe

Cette passe vise à répondre à une question simple :

> Quels sont les **noms doctrinaux 2.0** qui correspondent déjà à des **noms réels observables** dans Hugo développé, lesquels doivent être rapprochés, et lesquels doivent rester explicitement marqués comme cibles non encore stabilisées dans le réel ?

L’objectif est double :

1. faciliter la mise à jour ultérieure de la documentation 2.0 ;
2. éviter les collisions de vocabulaire dans les futurs travaux d’écarts, de prompts Cursor et de plans CTO.

## Périmètre retenu

Le périmètre de cette première passe est volontairement centré sur le **noyau Hugo cœur** et couvre :

- runtime conversationnel backend ;
- P0 et contrat de décision ;
- progression de conversation ;
- traduction produit vers le front ;
- objets mémoire / connaissances / évaluation déjà nommés dans la cible 2.0 et observables dans les audits ;
- services terminaux visibles dans le réel (synthèse, évaluation, qualité).

Sont exclus de cette passe :

- les prompts détaillés ;
- les maquettes UI fines ;
- les récits marketing / storytelling ;
- les extensions Hugo & Cie ;
- les objets purement cibles encore trop peu raccordables au réel sans relecture de code complémentaire.

## Méthode de lecture recommandée

Pour chaque notion, il faut distinguer quatre niveaux :

- **nom doctrinal 2.0** : la manière propre dont la cible nomme l’objet ou le service ;
- **nom réel observé** : la manière dont le Hugo développé le nomme dans les audits Cursor ;
- **statut d’alignement** : la qualité du raccord entre les deux ;
- **action documentaire** : ce qu’il faudra faire ensuite dans les specs.

Ce document ne cherche donc pas à imposer un seul nom partout. Il cherche au contraire à rendre visible le bon couple :

- **nom canonique pour raisonner juste** ;
- **nom réel pour parler juste du développé**.

## Catégories couvertes

Les catégories couvertes sont les suivantes :

1. chaîne runtime et architecture ;
2. régulation locale P0 et sortie de décision ;
3. progression de conversation et traduction produit ;
4. services backend structurants ;
5. objets de domaine persistés ou déjà nommés ;
6. endpoints / surfaces observables servant de révélateurs de vocabulaire.

## Légende des statuts

- `ALIGNÉ` : la cible 2.0 et le réel utilisent déjà des noms très proches ou manifestement compatibles.
- `ALIGNÉ_DOC_PARTIEL` : le raccord est bon, mais la documentation doit mieux expliciter le lien.
- `RENOMMER_DANS_DOC` : le réel emploie un nom concret qu’il faut faire apparaître dans la doc 2.0.
- `RENOMMER_DANS_CODE` : cas potentiel où le code devrait à terme converger vers le nom canonique ; aucun cas fort n’est figé dans cette passe.
- `AMBIGU` : le raccord conceptuel existe, mais le mapping n’est pas encore suffisamment net.
- `A_VERIFIER` : le corpus utilisé ici ne permet pas de prouver un mapping sûr.

## Glossaire croisé

| Catégorie | Nom 2.0 (doctrine) | Nom(s) réel(s) observé(s) | Type | Statut | Lecture / action recommandée |
|---|---|---|---|---|---|
| Architecture | Chaîne runtime 2.0 en 6 temps / 7 mouvements | `buildhugoturn` comme point d’entrée ; séquence `buildhugocontext` → `resolveposture` → `analyzeturnstate` → `classifyp0turnstate` → `decideconversation` / `decideconversationv17` → `buildteachingplan` → `decidenextphase` → `selectragchunks` → `buildsessionmemory` → `buildconversationprogress` → `builduistate` → `renderwithtutorprompt` | Chaîne de services | `RENOMMER_DANS_DOC` | Conserver la formulation doctrinale 2.0, mais documenter explicitement la séquence réelle actuelle comme implémentation observée. |
| Architecture | TutorPrompt pivot runtime | `TutorPrompt`, `renderwithtutorprompt`, fallback `buildafestpromptslegacy`, `rendertutorpromptv17` | Objet + service de rendu | `ALIGNÉ` | Bon alignement global. Ajouter dans la doc le fait que plusieurs chemins de rendu coexistent selon flags et fallback. |
| Architecture | PostureSelector | `resolveposture` observé dans le pipeline réel ; `PostureSelector` dans la doctrine 2.0 | Service / logique de posture | `AMBIGU` | Garder `PostureSelector` comme nom cible, mais noter que l’audit du réel documente surtout `resolveposture`. |
| Régulation | TurnState | `TurnState`, `analyzeturnstate`, `turnstateanalyzer.py`, `domainschemas.py` | État local du tour | `ALIGNÉ` | Le concept et le nom sont déjà compatibles. Ajouter les noms de fichiers réels dans les annexes techniques. |
| Régulation | Contrat de décision / DecisionContract | `ConversationDecision`, `decisionstate`, `decideconversation`, `decisionengine.py` | Sortie structurée de décision | `RENOMMER_DANS_DOC` | La doc 2.0 doit expliciter que le contrat de décision doctrinal correspond dans le réel à `ConversationDecision` / `decisionstate`. |
| Régulation | P0 | `analyzeturnstate`, `classifyp0turnstate`, `decideconversation`, flags `HUGOP0V17ENABLED`, `HUGOP0CLASSIFIERENABLED` | Couche de régulation locale | `ALIGNÉ` | Très bon alignement doctrinal. Il faut cependant mieux documenter la coexistence legacy / v17 comme réalité du développé. |
| Régulation | Variables P0 brutes non exposées | `primarygoal`, `tutorialmove`, `mode`, `targetquestioncount`, `microexplainallowed`, `usethemememory`, `useverbatimretrieval`, `userag`, `optionalevaluationeligible`, `reasoncodes` | Variables de décision | `ALIGNÉ` | Ces variables constituent une très bonne base pour les futurs prompts et les futures specs techniques, sans exposition front brute. |
| Progression | ConversationBranch | branches actives, `prioritybranchid`, branche principale / secondaire dans les docs d’audit | Objet de progression | `ALIGNÉ_DOC_PARTIEL` | Le concept est net, mais le nom d’objet réel n’est pas encore stabilisé au niveau doc. Garder le nom doctrinal et ajouter le mapping documentaire actuel. |
| Progression | ConversationProgress | `buildconversationprogress`, `buildconversationprogresscontract`, `testconversationprogress.py` | Calcul de progression inter-tours | `ALIGNÉ` | Très bon alignement. La doc 2.0 peut reprendre plus explicitement ces noms de service réels. |
| Progression | Maturité | `sessionmaturity`, maturité `RED/ORANGE/GREEN`, `missingfornextlevel`, `reasoncodes` | État / indicateurs | `ALIGNÉ` | Base commune déjà solide. À stabiliser plus tard dans un dictionnaire canonique plus fin. |
| Produit | UIState | `builduistate`, `uistatebuilder.py`, endpoint `ui-state` | Traduction produit | `ALIGNÉ` | Le réel confirme fortement le vocabulaire 2.0. C’est une bonne zone candidate pour un futur contrat quasi-JSON. |
| Produit | Projection produit montrable | endpoint `GET /hugo/sessions/{id}/ui-state` | Endpoint / contrat produit | `ALIGNÉ` | Point d’ancrage concret à garder pour la grammaire UI backend-first. |
| Service | Analyse du tour | `analyzeturnstate` | Service backend | `RENOMMER_DANS_DOC` | La matrice backend 2.0 doit citer ce nom réel comme implémentation actuelle du bloc d’analyse du tour. |
| Service | Décision locale | `decideconversation`, `decisionengine.py`, `decideconversationv17` | Service backend | `ALIGNÉ_DOC_PARTIEL` | Le concept est aligné, mais la dualité legacy / v17 doit être mieux explicitée. |
| Service | ProgressionCalculator | `buildconversationprogress` | Service backend | `RENOMMER_DANS_DOC` | Garder le nom cible pour la doctrine, mais faire apparaître le nom réellement utilisé. |
| Service | UIStateBuilder | `builduistate`, `uistatebuilder.py` | Service backend | `ALIGNÉ_DOC_PARTIEL` | Même logique : conserver le nom canonique, noter le nom réel. |
| Service | MemoryConsolidator | `memoryconsolidator.py`, `postconversationhooks` | Service backend | `ALIGNÉ` | Le rôle doctrinal et le nom réel sont proches. |
| Service | Session memory intra-session | `buildsessionmemory`, `sessionmemory.py` | Service backend | `RENOMMER_DANS_DOC` | La doc 2.0 doit mieux distinguer mémoire intra-session réelle et mémoire thématique gouvernée inter-session. |
| Service | SynthesisService | `synthesisservice.py`, endpoint `request-synthesis` | Service terminal | `ALIGNÉ` | Bonne continuité entre cible et réel. |
| Service | Evaluation service / workflow | `evaluationservice.py`, `evaluationworkflowengine.py`, endpoints `request-evaluation`, `finalize-evaluation`, `evaluation-readiness` localement | Service terminal | `ALIGNÉ_DOC_PARTIEL` | La doc doit distinguer plus clairement branche terminale doctrinale et workflow réel observé. |
| Service | QualityTracker | `qualitytracker.py`, `analyticscohortdashboard.py` | Service qualité / observabilité | `ALIGNÉ` | Très bonne cohérence entre la doctrine et le réel. |
| Mémoire | LearnerThemeMemory | `LearnerThemeMemory`, `memoryconsolidator.py` | Objet mémoire inter-session | `ALIGNÉ_DOC_PARTIEL` | Le nom est cohérent, mais l’audit signale qu’il n’est pas encore injecté dans `buildhugoturn`. Important pour les futurs écarts. |
| Mémoire | Mémoire gouvernée résumée | endpoint `memory-summary` | Vue / projection mémoire | `ALIGNÉ` | Très bon point de raccord entre cible mémoire gouvernée et produit réel. |
| Objet | HugoSession | `HugoSession` | Modèle de session | `RENOMMER_DANS_DOC` | Le pseudo-schéma 2.0 doit mieux faire apparaître `HugoSession` comme conteneur réel principal. |
| Objet | HugoMessage | `HugoMessage` | Modèle de message | `RENOMMER_DANS_DOC` | Utile dans les annexes techniques, sans recentrer la doctrine sur le verbatim. |
| Objet | LearnerState | `LearnerState`, task `recalclearnerstate` | Objet d’état apprenant | `ALIGNÉ_DOC_PARTIEL` | Objet réel présent mais encore partiel / immature dans l’audit. |
| Objet | TrainerKnowledgeItem | `TrainerKnowledgeItem` | Objet de connaissance gouvernée | `ALIGNÉ` | Excellent alignement cible / réel. |
| Objet | EvaluationTrace | `LearnerEvaluationRecord`, traces d’évaluation, workflow évaluation | Objet / trace terminale | `AMBIGU` | La cible 2.0 parle d’`EvaluationTrace`, tandis que le réel semble réparti entre `LearnerEvaluationRecord` et objets de trace. Harmonisation à prévoir. |
| Objet | Trace | `Trace`, `TraceCriterionAssessment`, endpoint `generate-trace` | Objet métier | `RENOMMER_DANS_DOC` | La doc 2.0 doit mieux relier la notion large de trace aux objets réels `Trace*`. |
| Objet | Evidence | `Evidence`, `EvidenceBundleView` | Objet métier / preuve | `RENOMMER_DANS_DOC` | Le nom réel `Evidence` doit apparaître plus clairement dans la doc cible sur preuves / exports. |
| Objet | ConversationQualitySignal | `ConversationQualitySignal` | Objet qualité | `ALIGNÉ` | Nom déjà cohérent entre doctrine et réel. |
| Objet | PersistentObjects | pas de modèle unique observé ; objets persistants mentionnés côté UI 2.0 | Concept produit | `AMBIGU` | À conserver comme concept produit sans lui inventer un backing model unique tant que le réel n’est pas plus clair. |
| Objet | ContradictionCase | pas de nom réel observé dans le corpus de réel utilisé ici | Objet conceptuel cible | `A_VERIFIER` | Le complément 2.0 le verrouille doctrinalement, mais le mapping réel n’est pas démontré ici. |
| Intercalaire | SessionInterstitial / équivalent | aucun nom réel observé dans Hugo développé ; seulement cible intercalaires V1 | Objet dérivé cible | `A_VERIFIER` | Ne pas l’introduire comme objet du réel tant que le chantier n’est pas implémenté. |
| Endpoint | Lecture UIState | `GET /hugo/sessions/{id}/ui-state` | Endpoint | `ALIGNÉ` | Point de référence fort pour la documentation produit. |
| Endpoint | Lecture progression | cible 2.0 : `GET /sessions/{id}/progress` ; réel audité : pas de route `progress` clairement observée, progression plutôt exposée via `ui-state` / services backend | Endpoint / projection | `AMBIGU` | La doc 2.0 devra soit assumer un futur endpoint dédié, soit noter que le réel observable passe aujourd’hui surtout par `ui-state`. |
| Endpoint | Changement de posture | cible 2.0 : `PATCH /sessions/{id}/posture` ; réel audité de ce périmètre : non confirmé dans les docs réelles utilisées | Endpoint | `A_VERIFIER` | Ne pas présenter comme acquis du réel sans relecture complémentaire. |
| Endpoint | Mémoire résumée | `GET /hugo/sessions/{id}/memory-summary` | Endpoint | `ALIGNÉ` | Très bon point de raccord entre mémoire gouvernée cible et exposition produit réelle. |
| Endpoint | Synthèse | `POST /hugo/sessions/{id}/request-synthesis` | Endpoint | `ALIGNÉ` | À reprendre tel quel dans les annexes de contrat produit. |
| Endpoint | Évaluation | `POST /hugo/sessions/{id}/request-evaluation`, `POST /finalize-evaluation`, `GET /evaluation-readiness` localement ; divergences partielles sur Encoors | Endpoint | `ALIGNÉ_DOC_PARTIEL` | La doc devra distinguer plus proprement le réel local audité et le runtime distant observé. |

## Lecture consolidée

### Alignements forts à conserver

Les alignements les plus solides entre la doctrine 2.0 et le réel sont :

- `TurnState` ;
- `P0` comme couche de régulation locale ;
- `ConversationProgress` ;
- `UIState` ;
- `LearnerThemeMemory` ;
- `TrainerKnowledgeItem` ;
- `ConversationQualitySignal` ;
- `TutorPrompt` comme pivot runtime.

Ces termes peuvent rester au centre de la documentation cible, à condition d’être reliés explicitement aux noms de services réels observés.

### Frictions de vocabulaire principales

Les zones de friction les plus importantes à ce stade sont :

- `DecisionContract` côté doctrine vs `ConversationDecision` / `decisionstate` côté réel ;
- `ProgressionCalculator` / `UIStateBuilder` côté doctrine vs `buildconversationprogress` / `builduistate` côté réel ;
- `EvaluationTrace` côté doctrine vs objets réels d’évaluation plus dispersés ;
- `PostureSelector` côté doctrine vs `resolveposture` côté pipeline réel documenté ;
- `PersistentObjects` comme concept produit encore plus propre que réellement observable dans le développé.

### Zones à ne pas forcer trop tôt

Il ne faut pas réécrire la documentation comme si les éléments suivants étaient déjà stabilisés dans le réel :

- `ContradictionCase` comme objet réellement implémenté ;
- `SessionInterstitial` ou équivalent ;
- un endpoint `progress` réellement exposé si la preuve auditable n’est pas claire ;
- une nomenclature finale et propre du workflow d’évaluation tant que le mapping `EvaluationTrace` / `LearnerEvaluationRecord` / `Trace` n’est pas fixé.

## Actions documentaires recommandées

### 1. Spec canonique 2.0 – matrices backend

Ajouter, pour chaque service doctrinal, une mention explicite du nom réel observé dans Hugo développé lorsqu’il est connu :

- `buildhugoturn`
- `analyzeturnstate`
- `decideconversation`
- `buildconversationprogress`
- `builduistate`
- `memoryconsolidator.py`
- `synthesisservice.py`
- `evaluationworkflowengine.py`
- `qualitytracker.py`

### 2. Spec canonique 2.0 – matrice des objets

Ajouter une colonne « nom réel observé dans Hugo développé » pour réduire les collisions entre objets doctrinaux et modèles effectivement présents, notamment :

- `HugoSession`
- `HugoMessage`
- `LearnerState`
- `LearnerThemeMemory`
- `TrainerKnowledgeItem`
- `Trace`
- `TraceCriterionAssessment`
- `Evidence`
- `LearnerEvaluationRecord`
- `ConversationQualitySignal`

### 3. Complément unique 2.0

Ajouter un sous-bloc « alignement de vocabulaire avec le réel audité » rappelant au minimum les équivalences suivantes :

- `DecisionContract` ↔ `ConversationDecision` / `decisionstate`
- `ProgressionCalculator` ↔ `buildconversationprogress`
- `UIStateBuilder` ↔ `builduistate`
- `PostureSelector` ↔ logique actuellement documentée via `resolveposture`
- mémoire intra-session ↔ `buildsessionmemory` / `sessionmemory.py`

### 4. Spec interface 2.0

Clarifier ce qui relève :

- d’un **contrat cible** encore partiellement projeté (`progress`, `set-posture`) ;
- et de ce qui est **déjà observable** dans les audits du Hugo développé (`ui-state`, `memory-summary`, `request-synthesis`, `request-evaluation`).

### 5. Spec formateur / tuteur 2.0

Stabiliser le mapping entre :

- `EvaluationTrace`
- `Trace`
- `LearnerEvaluationRecord`
- objets de validation / partage

C’est aujourd’hui l’une des zones de vocabulaire les plus floues pour la suite des travaux d’écarts.

## Règles de rédaction à appliquer ensuite

- Garder le **nom doctrinal 2.0** quand il structure correctement la cible.
- Ajouter juste après, quand c’est utile, le **nom réel observé** dans Hugo développé.
- Ne pas rebaptiser brutalement toute la doctrine à partir des noms de fonctions Python.
- Ne pas laisser non plus une doc projet n’utiliser que des noms qui n’existent nulle part dans le code réel.
- Pour tout terme non stabilisé dans le réel, marquer explicitement `objet cible`, `nom conceptuel` ou `à confirmer dans le code`.
- Toujours distinguer **nom conceptuel de doctrine**, **nom de service réel**, **nom de modèle réel**, **nom d’endpoint réel**.

## Garde-fous de non-régression

Le réalignement vocabulaire ne doit pas provoquer de régression doctrinale. Il faut donc éviter :

- de réintroduire Hugo comme simple assistant AFEST mono-posture ;
- de recentrer la vérité comportementale sur les prompts ;
- de faire glisser la doc vers une logique front-driven ;
- de prendre le nom d’une fonction réelle comme preuve qu’un concept cible est déjà entièrement livré ;
- de faire du verbatim brut le centre de la doc simplement parce que `HugoMessage` existe réellement ;
- de transformer un objet encore conceptuel (`ContradictionCase`, `SessionInterstitial`) en objet supposé déjà présent dans le réel.

La règle saine est la suivante : **la doctrine 2.0 garde la structure, le réel fournit les noms concrets et les preuves d’existence**.

## Utilisation recommandée de ce document

Ce document peut être utilisé de trois façons dans la bibliothèque :

1. comme **glossaire d’appui** avant un chantier d’écarts ;
2. comme **document de raccord** pour mettre à jour les specs 2.0 sans dérive ;
3. comme **référence de vocabulaire** pour rédiger ensuite des prompts Cursor plus précis et mieux ancrés dans le code réel.

Il ne doit pas être utilisé seul pour conclure qu’un objet cible est implémenté, ni pour trancher un écart fonctionnel sans retour au corpus d’audit du réel.

## Suites recommandées

Après l’upload de ce document dans la bibliothèque, les suites les plus utiles sont :

1. produire une version 2 centrée sur le couple **évaluation / traces / validation humaine** ;
2. produire ensuite une matrice d’écarts par responsabilités (cible 2.0 vs réel audité) ;
3. mettre à jour les matrices de la spec canonique 2.0 avec une colonne « nom réel observé » ;
4. préparer enfin le futur récapitulatif des variables backend exploitables par les prompts, une fois l’architecture suffisamment figée.
