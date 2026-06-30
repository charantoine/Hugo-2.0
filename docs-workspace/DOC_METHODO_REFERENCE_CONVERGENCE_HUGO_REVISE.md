# Méthode de référence — conduite des analyses et plans de convergence Hugo réel → Hugo 2.0

## Statut du document

Ce document formalise la **méthode de travail** à réutiliser dans d’autres fils pour analyser un domaine Hugo, définir une cible de convergence, produire des écarts propres, préparer des décisions documentaires, puis construire un backlog CTO exploitable. Il ne décrit pas un domaine fonctionnel particulier ; il décrit la manière correcte de travailler sur les domaines du Space.[cite:104][cite:85]

Il doit servir de source de référence méthodologique lorsque l’objectif est de produire un travail fiable, raccordé aux documents de l’espace, sans confusion entre réel observé, cible spécifiée, vocabulaire d’alignement, et hypothèses de convergence.[cite:104][cite:40]

## Finalité de la méthode

La méthode a quatre buts principaux :

- décrire le réel sans le sur-interpréter ;[cite:104]
- décrire la cible 2.0 sans la faire passer pour déjà livrée ;[cite:104][cite:40]
- identifier des écarts confirmés, et non des impressions ;[cite:85][cite:89]
- transformer ces écarts en artefacts de travail utilisables par un CTO, un rédacteur de spec ou un développeur backend/front.[cite:85]

Cette méthode existe précisément pour éviter les dérives documentaires les plus fréquentes dans le workspace : prendre une spec comme preuve de code, prendre un nom doctrinal comme preuve d’objet implémenté, confondre runtime local et runtime distant, ou reconstruire le produit depuis un seul écran, un seul endpoint ou un seul prompt.[cite:104][cite:40]

## Principes non négociables

### 1. Toujours séparer les niveaux de vérité

Tout travail doit distinguer explicitement :

- **réel observé** ;
- **cible spécifiée** ;
- **écarts confirmés** ;
- **A_VERIFIER** ;
- **hypothèses de convergence** le cas échéant.[cite:104][cite:85]

Cette séparation doit apparaître dans les documents, les tableaux, les synthèses et les backlogs. Une phrase ambiguë qui mélange cible et réel vaut erreur documentaire, même si l’intuition métier est correcte.[cite:104]

### 2. La spec cible ne prouve jamais le réel

Une spec 2.0, un complément, une note d’interface ou un document de cadrage produit décrivent un état visé. Ils ne démontrent jamais qu’une fonctionnalité existe déjà dans Hugo développé.[cite:104][cite:40]

Cette règle vaut particulièrement pour les objets “propres” du corpus cible, comme `EvaluationTrace`, `PersistentObjects`, `SessionInterstitial`, `PATCH /sessions/{id}/posture` ou certaines vues tutorales. Tant que le croisement avec les audits du réel n’est pas fait, ces éléments restent des éléments de cible ou des points A_VERIFIER.[cite:40][cite:85]

### 3. Le glossaire est un pont, pas une preuve

Le glossaire d’alignement sert à raccorder les noms du corpus 2.0 aux noms réellement observés dans Hugo développé. Il ne doit jamais être utilisé comme preuve autonome qu’un objet cible est livré tel quel dans le code ou dans le produit.[cite:40]

La bonne lecture est donc : **nom doctrinal juste pour raisonner, nom réel observé pour parler juste du développé**. L’objectif n’est ni de tout rebaptiser selon le code, ni de tout réécrire selon la spec ; l’objectif est de documenter proprement le raccord entre les deux.[cite:40][cite:85]

### 4. La vérité comportementale ne doit jamais être recentrée sur le front

Le cœur de Hugo reste backend-first : backend Django orchestré, P0, TutorPrompt, progression, mémoire gouvernée, services terminaux et règles produit. Le front lit des états dérivés, il n’est pas la source de vérité comportementale.[cite:104][cite:40]

En conséquence, toute analyse ou future spec doit éviter :

- de faire du front un pilote moteur ;[cite:104]
- d’exposer des champs P0 bruts ;[cite:40]
- de lire un composant UI comme preuve suffisante de la logique métier ;[cite:104]
- de reconstituer la doctrine depuis un seul écran produit.[cite:104][cite:85]

### 5. Le runtime distant reste distinct du runtime local audité

Dès qu’un texte parle de `hugoback.encoors.com`, d’un environnement distant, d’un flag non inspecté ou d’un comportement prod non recoupé, il faut le marquer explicitement **A_VERIFIER**.[cite:104][cite:85][cite:89]

Cette règle protège contre la confusion entre :

- ce que montre le code local ;
- ce que montrent les parcours de démo ;
- ce que le front distant semble consommer ;
- ce qui est réellement activé en production distante.[cite:104][cite:89]

## Sources à utiliser selon la nature de la question

## Réel audité

Pour décrire le **réel**, la hiérarchie documentaire de référence impose de lire d’abord le code `hugoback`, les tests backend, le front `frontend1.8` de `hugo-hugolucia`, puis les documents docs-workspace qui synthétisent ces constats.[cite:104]

Dans la bibliothèque, les points d’entrée structurants sont :

- `00_HIERARCHIE_DOCUMENTAIRE.md` pour savoir quelle source fait foi pour quoi ;[cite:104]
- `01_CARTOGRAPHIE_WORKSPACE_REEL.md` pour savoir où est quoi dans le workspace ;[cite:27]
- `02_ETAT_MOTEUR_REEL.md` pour le moteur ;[cite:40]
- `03_ETAT_PRODUIT_REEL.md` pour le produit montrable ;[cite:40]
- `05_ECARTS_DOC_CODE_PRODUIT.md` pour les divergences transverses ;[cite:89]
- `07` à `10` pour le runtime et les démos, selon le besoin.[cite:104]

## Cible 2.0

Pour décrire la **cible**, la priorité va à la spec canonique Hugo 2.0 et à ses compléments de domaine. Le glossaire rappelle explicitement que ce corpus cible prime toujours sur les anciennes specs ou les récits historiques lorsque l’enjeu est de formuler une cible de convergence.[cite:40]

La lecture cible doit donc partir de :

- `spec_canonique_hugo_2_0.md` ;[cite:40]
- `complement_unique_specs_2_0-1.md` ou autres compléments consolidés si mobilisés dans le domaine ;[cite:40]
- `specs-Orchestrateur-diagnostic-2.0.md`, `specs-formateur-tuteur-2.0.md`, `specs-interface-2.0.md` selon le sujet ;[cite:40]
- éventuellement `dernier-run-intercallaire.docx` si le chantier concerne les intercalaires, mais toujours comme matériau cible, pas comme preuve du réel.[cite:40]

## Vocabulaire et alignement

Le **glossaire** doit être mobilisé dès qu’il existe un risque de collision de vocabulaire entre doctrine 2.0 et noms réels observés dans le code ou les audits.[cite:40]

Il sert en particulier à :

- relier `UIState` à `buildUiState` et à l’endpoint `ui-state` ;[cite:40]
- relier `ConversationProgress` à `buildConversationProgress` ;[cite:40]
- clarifier `LearnerThemeMemory`, `TrainerKnowledgeItem`, `Trace`, `Evidence`, `LearnerEvaluationRecord` ;[cite:40]
- repérer les zones ambiguës comme `EvaluationTrace`, `PersistentObjects`, `PATCH posture`, `SessionInterstitial`.[cite:40]

## Travaux antérieurs par domaine

Pour tout domaine, il faut ensuite s’appuyer sur le fichier `ecarts — <domaine>.md` correspondant. C’est désormais le support central pour lire un domaine, parce qu’il regroupe le rapport d’écarts, la matrice, les décisions documentaires et le backlog.[cite:85][cite:89]

Les domaines ne doivent plus être relus à partir d’un seul rapport ancien ou d’une seule note isolée si un fichier centralisé `ecarts — <domaine>.md` existe déjà.[cite:85]

## Processus standard en 8 étapes

## Étape 1 — Cadrer la question exacte

Avant toute analyse, il faut reformuler le chantier en question opératoire. Exemples :

- quel est le contrat cible du front apprenant sur la bascule de posture ;
- quel est le mapping cible vs réel des objets d’évaluation ;
- quelle mémoire gouvernée minimale est nécessaire pour Hugo 2.0 ;
- quels artefacts exports/preuves sont déjà présents et lesquels restent à construire.[cite:85][cite:89]

Le cadrage doit aussi préciser si l’on travaille sur :

- un domaine cœur ;
- une surface produit ;
- un objet de domaine ;
- un contrat API ;
- une décision documentaire ;
- ou un backlog de convergence.[cite:85]

## Étape 2 — Déclarer le corpus utilisé

Chaque production doit indiquer explicitement quelles sources sont mobilisées :

- pour le réel ;
- pour la cible ;
- pour le vocabulaire ;
- pour les travaux antérieurs du domaine.[cite:40][cite:85]

Cette discipline évite les formulations orphelines du type “la cible prévoit”, “le réel montre”, “le domaine confirme” sans que le lecteur sache sur quel corpus la phrase repose.[cite:40]

## Étape 3 — Lire selon l’ordre de priorité correct

L’ordre de lecture ne doit pas être improvisé. Le document de hiérarchie documentaire impose un ordre clair : le code `hugoback` et les fronts montrables priment sur les anciennes specs ; les documents docs-workspace synthétisent ; les specs historiques n’ont qu’un rôle secondaire ; les archives ne doivent jamais servir seules de base de vérité.[cite:104]

Autrement dit :

- pour le réel, on remonte vers `02`, `03`, `05`, `07-10` ;[cite:104][cite:27]
- pour la cible, on remonte vers la spec canonique 2.0 et les compléments ;[cite:40]
- pour le vocabulaire, on utilise le glossaire ;[cite:40]
- pour un domaine, on lit son fichier `ecarts — <domaine>.md`.[cite:85]

## Étape 4 — Produire une lecture par niveau de vérité

Une bonne analyse doit faire apparaître au minimum quatre blocs :

- ce qui est confirmé dans le réel ;
- ce qui est fixé en cible 2.0 ;
- les écarts confirmés ;
- les zones A_VERIFIER.[cite:85][cite:89]

Quand c’est utile, un cinquième bloc peut expliciter les hypothèses de convergence ou les propositions de contrat cible, à condition de les distinguer clairement du réel observé et de la doctrine déjà fixée.[cite:85]

## Étape 5 — Utiliser le glossaire pour stabiliser les noms

Dès qu’un objet doctrinal 2.0 n’a pas d’équivalent évident dans le réel, il faut éviter les conclusions rapides. Le glossaire sert alors à qualifier le statut du raccord : `ALIGN`, `ALIGN DOC PARTIEL`, `RENOMMER DANS DOC`, `AMBIGU`, `A_VERIFIER`.[cite:40]

Cette étape est cruciale pour ne pas écrire trop vite :

- “EvaluationTrace existe”, alors que le réel est dispersé entre `LearnerEvaluationRecord`, objets de trace et workflow d’évaluation ;[cite:40][cite:85]
- “PersistentObjects est déjà modélisé”, alors que le backing model réel reste ambigu ;[cite:40][cite:85]
- “PATCH posture est livré”, alors que le mapping réel reste à vérifier.[cite:40]

## Étape 6 — Transformer l’analyse en artefacts standardisés

La méthode de domaine retenue dans les travaux existants procède en **quatre artefacts successifs** :

1. `00_rapport_ecarts_<domaine>.md` ;
2. `01_matrice_ecarts_<domaine>.md` ;
3. `02_decisions_documentaires_<domaine>.md` ;
4. `03_backlog_actions_<domaine>.md`.[cite:85]

Cette chaîne est explicitement décrite dans le domaine 60 et constitue une très bonne base réutilisable pour les autres domaines du Space.[cite:85]

### 6.1 Rapport d’écarts

Le rapport d’écarts sert à qualifier narrativement le domaine, rappeler les règles de vérité, décrire le périmètre, les sources, les garde-fous, puis raconter les écarts de manière intelligible avant passage en matrice.[cite:85]

### 6.2 Matrice d’écarts

La matrice transforme ensuite les constats en lignes comparables : objet, cible, réel observé, statut, lecture de l’écart, action documentaire recommandée. Ce format rend le chantier pilotable et force la précision.[cite:89][cite:85]

### 6.3 Décisions documentaires

Les décisions documentaires fixent la manière d’écrire juste sur le domaine : quels noms doctrinaux conserver, quels noms réels faire apparaître, quelles zones garder ouvertes, quels endpoints traiter comme ancrages, quels interdits de formulation rappeler.[cite:85]

### 6.4 Backlog d’actions

Le backlog convertit ensuite les constats et décisions en actions ordonnées, priorisées, typées et reliées à des preuves documentaires. Il ne doit jamais être une roadmap vague ; il doit être un backlog de convergence articulé à la doctrine et au réel observé.[cite:85]

## Étape 7 — Produire des formulations sûres

Une bonne production doit utiliser des formulations calibrées selon le niveau de preuve. Exemples de formulations correctes :

- “Le réel audité confirme…” ;
- “La cible 2.0 fixe…” ;
- “Le glossaire raccorde…” ;
- “Le domaine traite ce point comme ambigu…” ;
- “Ce point reste A_VERIFIER sur le runtime distant…” ;
- “La proposition ci-dessous relève d’un contrat cible recommandé, non d’un fait observé…”[cite:40][cite:85][cite:89]

À l’inverse, les formulations suivantes doivent être évitées si elles ne sont pas prouvées :

- “est déjà implémenté” ;
- “existe dans Hugo” ;
- “est exposé en prod” ;
- “le tuteur valide l’évaluation” ;
- “l’UI permet de…” ;
- “l’objet X correspond à Y” sans statut de raccord explicité.[cite:85][cite:104]

## Étape 8 — Finir par des sorties réutilisables

La méthode doit toujours viser une sortie utile pour l’action. Les sorties attendues selon les cas sont :

- matrice d’écarts ;[cite:85][cite:89]
- décisions documentaires ;[cite:85]
- contrat API cible ;[cite:40]
- contrat UIState cible ;[cite:40]
- mini-spec front ou backend ;[cite:85]
- backlog CTO ;[cite:85]
- note de vérification A_VERIFIER ;[cite:104]
- document de méthode ou de gouvernance documentaire.[cite:104]

## Comment écrire juste sur un domaine

## Structure minimale recommandée

Pour tout document d’analyse, la structure minimale conseillée est :

1. objet du document ;
2. corpus mobilisé ;
3. règles de vérité appliquées ;
4. réel confirmé ;
5. cible 2.0 ;
6. écarts confirmés ;
7. zones A_VERIFIER ;
8. décisions, contrats ou actions à produire.[cite:85][cite:89]

Cette structure n’est pas rigide, mais elle garantit de ne pas sauter directement aux solutions avant d’avoir stabilisé la lecture du domaine.[cite:85]

## Statuts de lecture recommandés

Les statuts les plus utiles, déjà employés dans les fichiers de domaine, sont :

- `ALIGNE` ;
- `ALIGNE DOC PARTIEL` ;
- `RENOMMER DANS DOC` ;
- `AMBIGU` ;
- `A_VERIFIER` ;
- `ABSENT / NOUVEAU CONTRAT`.[cite:40][cite:89]

Ils ont deux avantages :

- ils évitent le faux binaire “présent/absent” ;[cite:89]
- ils permettent de préparer des actions documentaires ou techniques adaptées à la nature réelle de l’écart.[cite:85]

## Quand ouvrir un “nouveau contrat”

Le statut `ABSENT / NOUVEAU CONTRAT` doit être utilisé lorsqu’un besoin cible est légitime, mais que le réel observé ne permet pas de montrer une capacité déjà installée comme telle. C’est typiquement le cas d’une projection d’intercalaires V1 ou d’une UI tutorale très détaillée encore non démontrée dans le réel mobilisé.[cite:89][cite:91]

Ce statut est utile car il évite deux erreurs inverses :

- prétendre que l’existant couvre déjà le besoin ;
- prétendre qu’il faut tout réinventer alors qu’un socle proche existe peut-être.[cite:89][cite:85]

## Garde-fous rédactionnels à appliquer dans tous les fils

### Ne jamais déduire le réel d’un seul fichier

Un domaine ne doit jamais être décrit à partir d’un seul document isolé. La méthode impose au minimum un croisement entre documents du réel, cible, glossaire et travaux de domaine.[cite:104][cite:40][cite:85]

### Ne pas relire une vue testeur ou admin comme une surface produit stabilisée

Cette prudence est déjà explicitement rappelée dans la bibliothèque. Beaucoup d’éléments observables dans les monorepos ou dans certaines vues ne doivent pas être promus d’office au rang de vérité produit montrable standard.[cite:104][cite:90]

### Ne pas faire du verbatim brut la mémoire principale

La spec 2.0 et le glossaire sont convergents sur ce point : la mémoire cible est gouvernée, structurée, thématique, post-conversation. Toute formulation qui réinstalle le verbatim brut comme mémoire principale ou surface libre est une régression documentaire.[cite:40]

### Ne pas transformer le tuteur ou le formateur en pilote du moteur

Les domaines tutoraux et formateur doivent être décrits comme des couches de lecture, de structuration, de validation humaine et d’accompagnement. Les documents de domaine rappellent explicitement qu’il faut éviter tout glissement vers un cockpit de pilotage libre du moteur apprenant.[cite:85][cite:90]

### Ne pas confondre validation de certaines traces et validation terminale générale

Le domaine tuteur rappelle qu’il est interdit de documenter un pouvoir générique de validation terminale standard si le corpus 2.0 ne le fixe pas comme capacité Hugo cœur par défaut. Cette prudence doit être conservée dans tous les futurs fils liés à l’évaluation.[cite:85]

## Patrons de sortie recommandés

## Patron 1 — Réponse d’analyse rapide

Pour une réponse courte dans un fil, utiliser le patron suivant :

- sources mobilisées ;
- réel confirmé ;
- cible 2.0 ;
- écarts ;
- A_VERIFIER ;
- prochaine sortie utile.[cite:85]

## Patron 2 — Note de domaine intermédiaire

Pour une note plus développée :

- objet ;
- corpus ;
- règles de vérité ;
- lecture du réel ;
- lecture de la cible ;
- tableau de mapping ;
- écarts ;
- zones ouvertes ;
- propositions de contrat ;
- backlog initial.[cite:85][cite:89]

## Patron 3 — Dossier de domaine complet

Pour un domaine à stabiliser sérieusement, suivre la chaîne complète :

- `00 rapport` ;
- `01 matrice` ;
- `02 décisions documentaires` ;
- `03 backlog actions`.[cite:85]

C’est le meilleur format lorsqu’il faut produire une base durable pour d’autres fils, des prompts Cursor ou des arbitrages CTO.[cite:85]

## Méthode de référence — personae Hugo 2.0

Cette section fixe la manière de construire et d’utiliser des personae
dans le Space, en cohérence avec la spec canonique Hugo 2.0, le
glossaire d’alignement et les fichiers d’écarts par domaine.

### 1. Rôle des personae dans la convergence

Les personae servent à :

- stabiliser des usages cibles cohérents avec la doctrine 2.0, sans
  inventer un marché générique hors corpus ;
- outiller le design produit, l’UX, les tests fonctionnels,
  interactionnels et de gouvernance ;
- décliner concrètement la matrice des rôles (apprenant, tuteur,
  formateur, coordinateur, ORGADMIN, superadmin technique) sans
  confondre cibles et capacités déjà livrées.

Ils ne remplacent ni la spec canonique, ni les écarts de domaine, ni
les audits du réel. Ils les complètent en fournissant des scénarios
d’usage testables.

### 2. Règles de vérité spécifiques aux personae

Chaque persona ou module de variation doit respecter la même discipline
que le reste du Space :

- **réel observé** : appuyé sur des cas, retours ou usages décrits dans
  les audits, les écarts de domaine ou les docs produit réels ;
- **cible spécifiée** : appuyée sur la spec canonique 2.0 et ses
  compléments (rôles, surfaces, invariants) ;
- **écarts confirmés** : lorsque un persona met en scène un usage qui
  n’est pas encore possible dans le réel audité mais cohérent avec la
  cible ;
- **A_VERIFIER** : dès qu’un comportement dépend du runtime distant,
  d’une surface non auditée ou d’un pouvoir de rôle non démontré ;
- **hypothèse de convergence** : pour les cas où le persona anticipe un
  usage souhaitable sans qu’il soit encore fixé doctrinalement.

Toute biographie, intention ou scénario persona doit être annoté avec
un niveau de preuve explicite. La narration ne doit jamais masquer cette
distinction.

### 3. Gabarit canonique de persona (noyau + modules)

Chaque persona Hugo 2.0 est construit en deux niveaux :

- un **noyau stable** :
  - identité synthétique ;
  - contexte (type d’organisme, cadre de formation, environnement) ;
  - rôle produit (apprenant, tuteur, formateur, coordinateur,
    ORGADMIN, superadmin technique… en vocabulaire canonique) ;
  - objectifs principaux dans Hugo ;
  - irritants majeurs actuels (réel ou cible) ;
  - contraintes clés (temps, équipements, règles d’orga, cadre légal) ;
  - attentes de confidentialité et de gouvernance ;
  - niveau de preuve global (réel, cible, hypothèse) ;
- des **modules de variation** combinables :
  - niveau de langage ;
  - niveau de littératie numérique ;
  - niveau d’autonomie ;
  - technicité métier ;
  - rapport à l’évaluation ;
  - rapport au partage ;
  - sensibilité à la preuve ;
  - rapport à l’explicitation.

Les modules ne créent pas de nouveaux personae autonomes à chaque
fois. Ils servent à générer des variantes de test à partir d’un même
noyau.

### 4. Bibliothèque de personae : structure attendue

La bibliothèque canonique de personae Hugo 2.0 doit, au minimum,
produire :

- une **galerie cœur** : quelques personae centraux couvrant les rôles
  majeurs et les tensions structurantes (novice vs expert, jeune vs
  reconversion, individuel vs organisationnel, faible vs forte autonomie,
  faible vs forte littératie numérique, usages métier vs audit/qualité) ;
- une **galerie étendue** : personae complémentaires pour affiner des
  domaines critiques (mémoire, évaluation, observabilité, exports et
  preuves, gouvernance multi-tenant) ;
- des **edge cases** : profils qui stressent les invariants
  confidentialité-first, partage explicite, multi-tenant strict, ou les
  limites UX ;

Chaque persona canonique doit être relié :

- à un ou plusieurs rôles de la spec 2.0 (section rôles et matrice
  des surfaces et des droits) ;
- à un ou plusieurs domaines d’écarts (`ecarts — <domaine>.md`) ;
- à des scénarios de test documentés (front apprenant, tuteur,
  formateur, exports, etc.).

### 5. Gabarit de sortie pour un persona canonique

Pour chaque persona de la galerie canonique, la fiche minimale attendue
comprend :

- identité synthétique ;
- contexte ;
- objectifs ;
- irritants ;
- contraintes ;
- niveau de langage (module) ;
- niveau numérique (module) ;
- comportements conversationnels typiques ;
- attentes UI ;
- attentes de rôle et de confidentialité ;
- scénarios de conversation à jouer ;
- scénarios de navigation UI ;
- scénarios de partage / export / validation ;
- cas limites et anti-cas ;
- critères d’oracle pour audit automatique (ce qui est considéré comme
  réussite / échec dans un test) ;
- niveau de preuve (réel, cible, écart, A_VERIFIER, hypothèse).

Les scénarios associés doivent préciser :

- quelles fonctions Hugo 2.0 sont mises en jeu ;
- quels risques d’échec sont testés (confidentialité, confusion des
  rôles, confusion front / moteur, survalorisation du verbatim, etc.) ;
- quelles dépendances sont A_VERIFIER (runtime distant, RLS prod,
  surfaces non auditées).

### 6. Garde-fous spécifiques contre les biais historiques

Dans la construction et l’usage des personae, il est interdit de :

- recentrer Hugo sur l’AFEST seule ou sur une mono-posture réflexive ;
- relire un persona comme “utilisateur type AFEST” si le corpus ne
  l’impose pas ;
- survaloriser le verbatim (persona centré sur “tout voir / tout lire”)
  au détriment de la mémoire gouvernée et des objets structurés ;
- confondre front et moteur (persona qui “pilote” directement P0 ou les
  orchestrateurs) ;
- lire la cible spécifiée comme preuve que la surface existe déjà dans
  le réel.

Toute dérive de ce type doit être traitée comme un biais à corriger,
pas comme une caractéristique désirable du persona.

### 7. Intégration aux autres artefacts

Les personae ne sont pas un silo séparé. Ils doivent être :

- référencés dans les rapports d’écarts de domaine lorsque certains
  usages sont au cœur des écarts ;
- utilisés comme colonnes ou lignes dans les matrices de test
  (persona × fonctions Hugo 2.0 × scénarios de test × risques
  d’échec) ;
- connectés à la spec canonique (rôles, surfaces, invariants) et au
  plan de documentation CTO.

Un persona qui ne peut pas être relié à la spec 2.0, au glossaire ou à
un fichier d’écarts doit être traité comme hypothèse faible et non
comme référence canonique.

## Références à mobiliser souvent

## Documents de méthode et de recalage

- `00_HIERARCHIE_DOCUMENTAIRE.md` — source de vérité sur l’ordre de lecture et les pièges connus.[cite:104]
- `01_CARTOGRAPHIE_WORKSPACE_REEL.md` — carte du workspace, utile pour savoir où se trouve le moteur, le produit et les zones ambiguës.[cite:27]
- `glossaire_alignement_hugo_reel_vs_spec.md` — pont de vocabulaire et statuts d’alignement.[cite:40]

## Exemples de bonne méthode déjà matérialisés

- `ecarts-60_orchestrateur_tuteur.md` — très utile pour la chaîne en quatre artefacts, les décisions documentaires et les formulations prudentes sur objets, endpoints et zones ouvertes.[cite:85]
- `ecarts-100_exports_preuves_qualiopi_lite.md` — très utile pour la rigueur de la matrice, la lecture par statuts et le traitement du runtime distant comme A_VERIFIER.[cite:89]

## Référence de posture de travail

La bonne posture méthodologique dans cet espace est la suivante : **décrire juste, borner juste, raccorder juste, puis backloguer juste**. Cela signifie :

- partir des documents qui font foi ;[cite:104]
- dire ce qui est réel sans l’étendre ;[cite:104]
- dire ce qui est cible sans le présenter comme livré ;[cite:40]
- utiliser le glossaire pour réduire les collisions de vocabulaire ;[cite:40]
- documenter les écarts sans reconfigurer la doctrine ;[cite:85]
- sortir des contrats, matrices, décisions et backlogs réutilisables.[cite:85]

## Conclusion opératoire

La méthode de référence du Space n’est ni une méthode de brainstorming, ni une méthode de rédaction “au fil de l’eau”. C’est une méthode de convergence documentaire et technique fondée sur une hiérarchie stricte des sources, une séparation forte des niveaux de vérité, un usage contrôlé du glossaire, et une transformation systématique des constats en artefacts de pilotage.[cite:104][cite:40][cite:85]

Lorsqu’elle est appliquée correctement, cette méthode permet de préparer des fils robustes sur le front apprenant, l’évaluation, la mémoire, les interfaces tuteur/formateur, les exports/preuves ou les intercalaires, sans sur-vendre le réel, sans affaiblir la cible 2.0 et sans déplacer la source de vérité hors du backend orchestré.[cite:85][cite:89][cite:40]


## Addendum méthodologique intégré — juin 2026

### Réduction de périmètre mémoire gouvernée

- Décision de cadrage à appliquer immédiatement : le chantier **mémoire gouvernée** est réduit à un périmètre **intra-conversation** pour l’implémentation cible court terme.
- La mémoire inter-sessions reste **préparée dans les contrats**, dans le vocabulaire et dans les points d’extension backend, mais **n’est pas implémentée dans ce lot**.
- Toute formulation documentaire future doit donc distinguer :
  - mémoire intra-conversation effectivement visée à court terme ;
  - préparation technique et documentaire de l’inter-sessions ;
  - inter-sessions effectivement implémenté, qui reste hors périmètre immédiat.

### Règle de lecture mémoire : réel, cible, réduction de cible

Pour le domaine mémoire, la lecture doit désormais distinguer quatre niveaux :

- **Réel observé** : session memory, buildsessionmemory, sessionUiState, memory-summary, consolidation partielle, absence éventuelle d’injection orchestrateur selon le corpus audité.
- **Cible 2.0 canonique complète** : mémoire gouvernée thématique, structurée, référentiel-first, avec consolidation inter-sessions post-conversation.
- **Cible d’implémentation retenue maintenant** : mémoire gouvernée **intra-conversation** uniquement.
- **Préparation d’extension** : interfaces, objets et contrats qui permettent d’ajouter l’inter-sessions plus tard sans casser l’architecture.

### Ambiguïtés mémoire : règle d’arbitrage pragmatique inspirée des interfaces LLM intra-conversation

Pour trancher les ambiguïtés résiduelles de la spec mémoire gouvernée, adopter la règle suivante :

- dans l’expérience apprenant, la mémoire active de court terme doit se comporter comme une **mémoire de conversation courante**, synthétique, utile et discrète ;
- elle ne doit pas exposer un historique brut ni un verbatim complet ;
- elle doit servir avant tout à maintenir la continuité locale du fil, les thèmes actifs, les éléments encore ouverts, les engagements pris, et les objets à confirmer ;
- elle peut s’inspirer des interfaces LLM type Perplexity **intra-conversation**, où la continuité utile est maintenue au sein du fil sans transformer l’historique complet en mémoire produit exposée comme telle.

En pratique, cela impose :

- pas de mémoire “profil apprenant durable” dans ce lot ;
- pas de consolidation inter-sessions injectée dans l’orchestrateur pour l’instant ;
- pas de surface libre de consultation du verbatim comme pseudo-mémoire ;
- oui à une mémoire résumée du fil courant, pilotée backend, consommable via UIState ou objet produit dérivé ;
- oui à des objets préparés pour évoluer plus tard vers LearnerThemeMemory inter-sessions, sans promettre leur activation maintenant.

### Contrat cible minimal mémoire intra-conversation

Le contrat cible minimal à privilégier est le suivant :

- la mémoire utile du fil courant est un **résumé gouverné** et non un verbatim ;
- ce résumé contient uniquement les éléments nécessaires à la continuité tutorale ;
- il est produit et mis à jour côté backend ;
- il peut être relu par le moteur sur les tours suivants de la même conversation ;
- il peut être exposé au produit seulement sous forme propre, confirmable et non technique ;
- il ne doit pas devenir un écran annexe de debug ni un export brut du contexte moteur.

### Ce que la mémoire intra-conversation peut contenir

À ce stade, la mémoire gouvernée intra-conversation peut contenir de manière prioritaire :

- thème ou situation active ;
- branche prioritaire en cours ;
- objectif pédagogique courant ;
- faits déjà clarifiés utiles à ne pas redemander ;
- hypothèses formulées par l’apprenant et encore ouvertes ;
- éléments manquants pour progresser ;
- points de synthèse locale ou d’évaluation encore non atteints ;
- objets confirmables ou partageables issus de la conversation.

Elle ne doit pas contenir comme surface de référence :

- le verbatim brut intégral ;
- une reconstruction exhaustive de l’historique ;
- des champs P0 exposés ;
- des diagnostics figés non validés ;
- des statuts humains implicites ;
- des déductions durables sur l’apprenant qui dépasseraient le fil courant.

### Décision de conception : comportement attendu côté UX

L’expérience mémoire intra-conversation doit rester proche d’une logique de continuité discrète :

- le système “se souvient” des éléments utiles du fil courant ;
- il évite les répétitions absurdes ;
- il reprend un thème ou un point ouvert sans réexposer la mécanique backend ;
- il peut montrer certains éléments mémorisés seulement s’ils sont utiles à l’apprenant et formulés dans une grammaire produit simple.

La mémoire visible n’est donc pas un “dossier mémoire” exhaustif mais, au besoin :

- un rappel de ce qui est en cours ;
- une reformulation de ce qui a déjà été établi ;
- une liste bornée de points à confirmer ;
- un objet de synthèse locale ou de continuité de séance.

### Règles d’implémentation à appliquer

- Implémenter d’abord la lecture/écriture de mémoire **dans la session courante**.
- Préparer une structure de données qui pourra être promue plus tard en inter-sessions sans rupture de contrat.
- Séparer explicitement `session memory` et `theme memory inter-session` dans la documentation et dans les contrats.
- Ne pas appeler inter-sessions une capacité qui ne sert encore qu’au fil courant.
- Ne pas faire dépendre la conduite tutorale d’un store mémoire durable non stabilisé.
- Ne pas faire du front la source de vérité mémoire ; la mémoire utile reste un produit dérivé backend.

### Formulation documentaire obligatoire pour les prochains chantiers

Toute doc ou backlog touchant la mémoire doit désormais employer une formule de ce type :

> La trajectoire retenue pour Hugo converge d’abord vers une mémoire gouvernée intra-conversation, pilotée backend, utile à la continuité du fil courant. L’inter-sessions est préparé doctrinalement et contractuellement, mais reste hors périmètre d’implémentation immédiat.

### Ajustement de la méthode générale de convergence

Cette réduction de périmètre confirme plusieurs règles générales déjà utiles au reste du programme :

- réduire le périmètre d’implémentation quand la cible 2.0 est plus large que ce qui est sécurisable à court terme ;
- conserver la doctrine cible comme direction, sans la sur-promettre comme état livré ;
- documenter les points d’extension explicitement, pour éviter les refontes inutiles ;
- s’inspirer d’interfaces LLM modernes uniquement comme **source d’arbitrage UX ou méthodologique**, jamais comme preuve que Hugo implémente déjà ces comportements.

### Verbatim méthodologique à conserver dans la référence

Les formulations suivantes doivent être conservées comme repères méthodologiques issus du fil :

- « mémoire gouvernée : réduire le périmètre d'implémentation à intra-conversation. en préparant l'inter-sessions, mais sans l'implémenter pour l'instant. »
- « Pour trancher certaines ambiguités résiduelles de la spec mémoire gouvernée, inspire toi de ce que font les interfaces LLM type perplexity intraconversation. »
- « Toujours distinguer : réel observé, cible spécifiée, écarts confirmés, points à vérifier, hypothèses. »
- « Ne jamais présenter une spec cible (2.0 ou 1.9) comme preuve qu’une fonctionnalité est déjà livrée. »
- « Ne pas utiliser le verbatim brut comme mémoire principale, ni exposer les champs P0 au front. »

### Vérifications de cohérence à appliquer après intégration

Après chaque mise à jour documentaire, vérifier explicitement :

- que la mémoire intra-conversation n’est pas décrite comme mémoire inter-sessions déjà en service ;
- que le nom LearnerThemeMemory n’est pas relu comme preuve d’injection réelle dans le tour courant sans recoupement audit ;
- que memory-summary n’est pas interprété automatiquement comme preuve d’une mémoire thématique complète ;
- que l’inspiration Perplexity intra-conversation reste au niveau UX/comportement, pas au niveau d’une preuve d’architecture Hugo ;
- que la cohérence globale backend-first, UIState, P0 non exposé, verbatim non central reste intacte.
