# 00_rapport_ecarts — 60_orchestrateur_tuteur

> **Mise à jour post-cluster 16 — 2026-06-18** · **Cluster 16 :** pas d'impact direct. **Confirmé :** B1-01 timeline. **PARTIEL :** surfaces `/app/tutor`.

## Domaine

- `DOMAINE_CODE = 60_orchestrateur_tuteur`
- `DOMAINE_LABEL = orchestrateur tuteur`

---

## 1. Objet du rapport

Ce rapport qualifie, pour le seul domaine **orchestrateur tuteur** de Hugo cœur, l’écart entre :
- la **cible 2.0** décrite par la spec canonique et son complément ;
- le **réel observable** décrit par les audits du workspace Hugo réel ;
- le **pont de vocabulaire** fourni par le glossaire d’alignement.

Le domaine traité ici est strictement celui de la **couche tuteur** d’Hugo cœur : lecture de progression, compréhension des blocages, aides à l’accompagnement humain, lecture de traces partageables, signaux de qualité et vues cohorte. Ce rapport n’ouvre ni un chantier d’admin complet, ni une réflexion Hugo & Cie, ni une extension client spécifique de validation terminale.

---

## 2. Règles de lecture et de vérité appliquées

### 2.1 Sources mobilisées

Pour parler de la **cible**, ce rapport s’appuie d’abord sur la spec canonique 2.0 et sur son complément, qui fixent le rôle du tuteur, les garde-fous de confidentialité, la place des signaux de qualité conversationnelle, et le statut des validations éventuellement associées à certaines traces partageables.[file:6][file:7]

Pour parler du **réel**, ce rapport s’appuie sur les audits du corpus Hugo réel et sur le glossaire d’alignement, qui documentent les services réellement observés côté progression, synthèse, évaluation, qualité, `ui-state`, `memory-summary`, ainsi que les frictions de vocabulaire entre doctrine et implémentation locale.[file:1][file:16]

### 2.2 Garde-fous méthodologiques

La spec 2.0 décrit un **état cible** et non un état livré ; elle ne doit donc jamais être relue comme preuve qu’une couche tuteur complète est déjà présente dans le runtime audité.[file:6][file:7]

Le glossaire d’alignement est un **pont de vocabulaire** utile pour raccorder `ConversationProgress`, `UIState`, `ConversationQualitySignal`, `QualityTracker` et les endpoints observés, mais il ne suffit jamais à lui seul pour démontrer l’existence d’une vraie surface tuteur métier de bout en bout.[file:1]

Toute affirmation dépendant du runtime distant, des flags ou de variantes non auditées localement reste marquée `A_VERIFIER` ; en particulier, une démonstration contre `hugoback.encoors.com` ne prouve pas l’équivalence avec le back local audité, et inversement.[file:16]

---

## 3. Périmètre cible 2.0 du domaine

### 3.1 Ce que la cible 2.0 fixe déjà

Dans la cible 2.0, l’orchestrateur tuteur est une **couche spécialisée distincte** des régimes apprenant. Son rôle est de lire la progression, détecter les besoins, comprendre les blocages, interpréter des traces partageables et préparer des recommandations d’accompagnement humain, sans piloter directement le moteur conversationnel apprenant.[file:6]

Cette couche tuteur consomme prioritairement :
- les objets de progression ;
- les signaux de qualité conversationnelle ;
- les synthèses ;
- les évaluations partageables ;
- les traces partageables utiles à l’accompagnement.[file:6]

La cible fixe aussi plusieurs interdits structurants :
- pas d’accès au verbatim non partagé ;
- pas de contrôle direct du P0 ;
- pas de forage libre des orchestrateurs apprenant ;
- pas d’autonomie certificative ;
- pas de dérive vers une lecture opaque ou déshumanisée des apprenants.[file:6][file:7]

### 3.2 Ce que la cible laisse encore ouvert

La cible 2.0 fixe bien la **fonction** de la couche tuteur, mais laisse encore ouvertes plusieurs précisions :
- le catalogue canonique détaillé des `ConversationQualitySignal` ;
- le rôle exact du tuteur dans certaines validations terminales ;
- les vues cohorte détaillées ;
- la forme précise des écrans ou contrats API dédiés à une surface tuteur complète.[file:6][file:7]

Le complément 2.0 ferme même explicitement un point important : en Hugo cœur 2.0, le tuteur **ne dispose pas par défaut** d’un pouvoir générique de validation terminale des évaluations ; cette possibilité n’est reconnue que comme extension ultérieure spécifique, non standard dans Hugo cœur.[file:7]

---

## 4. Photo du réel observable

### 4.1 Ce qui est fortement observable dans le réel

Le réel audité montre un socle backend déjà présent sur lequel une couche tuteur peut s’appuyer :
- `ConversationProgress` et ses services de calcul ;
- `UIState` et son exposition produit ;
- `memory-summary` comme projection de mémoire gouvernée ;
- `SynthesisService` ;
- workflow d’évaluation ;
- `QualityTracker` et `ConversationQualitySignal` ;
- traces et objets liés à l’évaluation ou aux preuves partageables.[file:1][file:16]

Le glossaire signale un bon alignement de vocabulaire entre doctrine 2.0 et réel observé pour `ConversationProgress`, `UIState`, `ConversationQualitySignal`, `QualityTracker`, ainsi qu’un alignement au moins partiel sur les routes ou projections utiles au tuteur comme `ui-state`, `memory-summary`, synthèse et évaluation.[file:1]

### 4.2 Ce qui est moins directement démontré

Le réel audité documente très bien les **briques backend** nécessaires à une future couche tuteur, mais démontre moins clairement une **surface tuteur métier complète et stabilisée** comme produit autonome.

Autrement dit, les audits montrent :
- des services et objets consommables par un tuteur ;
- des signaux de qualité et des artefacts partageables ;
- des endpoints ou workflows utiles ;
mais ils ne prouvent pas encore à eux seuls l’existence d’un orchestrateur tuteur complet, cohérent et pleinement frontalisé comme domaine métier stabilisé de bout en bout.[file:1][file:16]

### 4.3 Vocabulaire réel observable utile au domaine

Le glossaire confirme plusieurs points d’appui concrets pour ce domaine :
- `QualityTracker` existe comme service réel observé ;
- `ConversationQualitySignal` existe comme objet aligné ;
- `ConversationProgress` est bien documenté via `buildconversationprogress` ;
- `UIState` est bien documenté via `builduistate` ;
- les endpoints `ui-state`, `memory-summary`, `request-synthesis` et les workflows d’évaluation constituent des ancrages réels de lecture ou d’accompagnement.[file:1]

En revanche, le glossaire et les audits invitent à la prudence sur ce qui n’est pas encore démontré comme surface tuteur autonome :
- endpoint `progress` dédié réellement exposé ;
- pouvoir de validation terminale générique du tuteur ;
- écrans tuteur métier complets ;
- catalogue stabilisé des signaux de qualité et de leurs recommandations associées.[file:1][file:7]

### 4.4 Confidentialité et partage dans le réel

Le domaine tuteur est directement contraint par les garde-fous de confidentialité déjà fortement fixés dans la cible 2.0 et rappelés dans les audits : le verbatim reste privé par défaut, l’accès des rôles non apprenant est borné par le partage explicite, et l’accès libre au contenu apprenant non partagé est interdit.[file:6][file:7]

Le réel audité confirme aussi que la projection produit observable est organisée autour d’objets dérivés backend-first (`ui-state`, synthèse, mémoire résumée, traces), et non autour d’une exposition brute des états P0 ou du verbatim ; cela va dans le bon sens pour une future couche tuteur gouvernée.[file:1][file:16]

---

## 5. Analyse narrative des écarts

### 5.1 Alignement doctrinal globalement bon

Le domaine est globalement **bien préparé** dans le réel pour converger vers la cible 2.0.

Le plus important est déjà en place sur le plan des responsabilités :
- progression conversationnelle calculée ;
- états produit dérivés ;
- mémoire gouvernée résumée ;
- synthèse ;
- évaluation ;
- signaux de qualité conversationnelle.[file:1][file:16]

Cela signifie que la cible 2.0 ne doit pas être lue comme une injonction à inventer ex nihilo une couche tuteur. Le réel couvre déjà une part substantielle du socle métier requis, même si cette couverture est encore plus nette au niveau backend et des objets que du niveau surface tuteur stabilisée.[file:1][file:6]

### 5.2 Écart principal : couche tuteur doctrinalement claire, produit réel encore partiellement implicite

Le principal écart n’est pas l’absence totale du domaine, mais le fait que la couche tuteur est aujourd’hui **plus lisible dans la doctrine et dans les briques backend** que dans une surface métier tuteur complète et clairement bornée.

La cible 2.0 décrit un rôle tuteur lisible : lecture, interprétation, recommandation, accompagnement, lecture de cohortes, validation de certaines traces partageables dans des bornes précises.[file:6] Le réel, lui, montre surtout les ingrédients techniques nécessaires à cette couche, sans établir encore de façon aussi nette un orchestrateur tuteur finalisé, cohérent et documenté comme tel dans l’état livré observable.[file:1][file:16]

### 5.3 Écart important : validation terminale du tuteur à ne pas sur-affirmer

Une zone de friction importante concerne la **validation**.

La spec canonique mentionne que le tuteur peut lire, commenter, recommander et éventuellement valider certaines traces partageables.[file:6] Mais le complément 2.0 resserre explicitement le cadre : en Hugo cœur 2.0, le tuteur ne dispose **pas par défaut** d’un pouvoir générique de validation terminale des évaluations ; une telle capacité relèverait d’une extension spécifique ultérieure.[file:7]

Le risque documentaire est donc double :
- soit sous-spécifier le rôle du tuteur en le réduisant à un simple lecteur passif ;
- soit sur-spécifier un pouvoir de validation terminale standard qui n’est pas acté dans Hugo cœur.

Sur ce point, le bon traitement documentaire est une clarification de contrat, pas une sur-interprétation du réel ni une inflation fonctionnelle.

### 5.4 Écart de vocabulaire : “couche tuteur” cible vs surfaces réelles observées

Le glossaire montre que le domaine tuteur doit être documenté à partir d’un **assemblage de briques réelles** plutôt qu’à partir d’un unique service nommé “orchestrateur tuteur”.

Autrement dit, la doctrine parle d’un rôle ou d’une couche tuteur, tandis que le réel observable parle plutôt de :
- `buildconversationprogress` ;
- `builduistate` ;
- `qualitytracker.py` ;
- `ConversationQualitySignal` ;
- `synthesisservice.py` ;
- `evaluationworkflowengine.py` ;
- endpoints de projection ou d’action associés.[file:1]

L’écart n’est donc pas seulement fonctionnel ; il est aussi documentaire. Il faut éviter de laisser croire qu’un service unique déjà nommé et stabilisé “TutorOrchestrator” existerait dans le code si ce n’est pas ce que montrent les audits.

### 5.5 Écart sur les vues cohorte et la lisibilité transverse

La cible 2.0 acte l’existence de **vues cohorte** et de signaux de qualité conversationnelle sans scoring opaque.[file:6] Le glossaire montre que `QualityTracker` et `ConversationQualitySignal` sont bien présents comme points d’appui réels, avec mention d’`analyticscohortdashboard.py` dans le réel observé.[file:1]

Cependant, le complément 2.0 précise aussi que le **catalogue canonique** des signaux de qualité reste encore ouvert.[file:7] Il y a donc ici un écart de **formalisation** plutôt qu’un vide complet : le domaine qualité/cohorte existe déjà en partie dans le réel, mais son contrat canonique tuteur reste encore incomplètement stabilisé.

### 5.6 Écart sur les endpoints et contrats tuteur

Le glossaire qualifie comme `AMBIGU` l’existence d’un endpoint `progress` réellement exposé, alors que `ui-state`, `memory-summary`, synthèse et évaluation sont de meilleurs points d’ancrage observables.[file:1]

Le complément 2.0 recommande d’ailleurs de stabiliser d’abord un contrat quasi-JSON autour de `UIState`, `ConversationProgress`, des actions terminales et des objets montrables, plutôt que de supposer déjà tous les écrans ou endpoints tuteur finaux.[file:7]

Sur ce domaine, le bon mouvement n’est donc pas d’inventer trop tôt une API tuteur complète, mais de clarifier :
- ce qui est déjà observable ;
- ce qui reste un contrat cible ;
- ce qui doit être marqué `A_VERIFIER`.

---

## 6. Lecture de synthèse par niveau de vérité

### 6.1 Implémenté / observable

Sur ce domaine, le réel audité permet d’affirmer comme **implémentés ou observables** :
- calcul et persistance de la progression conversationnelle ;
- construction de `UIState` ;
- mémoire gouvernée résumée ;
- synthèse ;
- workflow d’évaluation ;
- signaux de qualité conversationnelle ;
- objets et services de qualité exploitables à des fins de lecture tuteur.[file:1][file:16]

### 6.2 Cible 2.0

Relèvent clairement de la **cible 2.0** :
- une couche tuteur explicitement structurée comme rôle de lecture, interprétation et recommandation ;
- des vues cohorte proprement cadrées ;
- un catalogue canonique plus fin des `ConversationQualitySignal` ;
- une articulation documentaire stabilisée entre progression, signaux, synthèses, évaluations partageables et recommandations d’accompagnement.[file:6][file:7]

### 6.3 Écarts confirmés

À ce stade, les **écarts confirmés** portent surtout sur :
- la différence entre un socle backend bien présent et une surface tuteur métier pleinement explicitée ;
- l’ambiguïté sur certains endpoints ou contrats dédiés au tuteur ;
- le besoin de clarifier le rôle exact du tuteur dans les validations terminales ;
- le besoin d’aligner vocabulaire doctrinal et noms réels observés.[file:1][file:7]

### 6.4 À vérifier

Restent explicitement `A_VERIFIER` :
- l’existence et la stabilité d’une vraie surface tuteur complète sur runtime distant ;
- l’exposition effective d’un endpoint `progress` distinct dans le réel livré ;
- les pouvoirs précis de validation du tuteur dans les variantes non auditées ;
- les écarts éventuels entre le local audité et `hugoback.encoors.com` sur ce domaine.[file:1][file:16]

---

## 7. Garde-fous pour la suite documentaire

### 7.1 Ce qu’il ne faut pas faire

Pour ce domaine, il faut éviter :
1. de présenter la couche tuteur cible comme déjà complètement livrée ;
2. de réduire le domaine à un simple dashboard analytics ;
3. de supposer un droit générique de validation terminale du tuteur en Hugo cœur ;
4. de déduire l’existence d’un “TutorOrchestrator” unique dans le code si les audits montrent surtout un assemblage de briques backend ;
5. de contourner les garde-fous de confidentialité et de partage explicite.[file:6][file:7][file:16]

### 7.2 Ce qu’il faut privilégier

Il faut au contraire :
- documenter le domaine comme une **couche d’usage tuteur appuyée sur des briques backend réelles** ;
- expliciter les noms réels observés utiles au domaine ;
- distinguer clairement socle observable, cible 2.0 et zones ouvertes ;
- clarifier la frontière entre lecture/recommandation tuteur et validation terminale humaine ;
- ne proposer que des compléments backend et documentaires additifs.[file:1][file:6][file:7]

---

## 8. Conclusion opérationnelle du domaine

Le domaine `60_orchestrateur_tuteur` n’est ni absent, ni déjà stabilisé comme couche produit complète de bout en bout.

Le réel audité montre un socle solide : progression, `UIState`, mémoire résumée, synthèse, évaluation, qualité conversationnelle et objets partageables. La cible 2.0 fournit, de son côté, une doctrine claire du rôle tuteur : lecture, interprétation, recommandation et accompagnement humain, sous garde-fous stricts de confidentialité et sans pilotage direct du moteur apprenant.[file:6][file:1]

L’écart principal est donc un écart de **formalisation, de surface et de vocabulaire**, plus qu’un vide fonctionnel absolu. La bonne suite pour ce domaine est de clarifier les contrats documentaires, d’aligner les noms avec le réel observé, de verrouiller les garde-fous sur validation et confidentialité, et de marquer explicitement `A_VERIFIER` tout ce qui dépend encore du runtime distant ou de surfaces tuteur non auditables localement.[file:7][file:16]

# 01_matrice_ecarts — 60_orchestrateur_tuteur

## Domaine

- `DOMAINE_CODE = 60_orchestrateur_tuteur`
- `DOMAINE_LABEL = orchestrateur tuteur`

---

## 1. Règles de lecture

Cette matrice porte sur le seul domaine **orchestrateur tuteur** de Hugo cœur. Elle croise :
- la **cible 2.0** ;
- le **réel observable** dans les audits ;
- le **glossaire d’alignement** comme pont de vocabulaire.[file:1][file:6]

Les statuts utilisés sont :
- `ALIGNE`
- `ALIGNE_DOC_PARTIEL`
- `RENOMMER_DANS_DOC`
- `AMBIGU`
- `A_VERIFIER`
- `ABSENT / NOUVEAU_CONTRAT`.[file:1]

Rappel méthodologique :
- la spec 2.0 décrit une **cible**, pas un état livré ;[file:6][file:7]
- le glossaire ne prouve pas seul l’implémentation ;[file:1]
- toute dépendance au runtime distant ou à une variante non auditée reste `A_VERIFIER`.[file:16]

---

## 2. Matrice d’écarts

| Axe | Élément cible 2.0 | Réel observable / noms réels | Statut | Lecture d’écart / décision documentaire |
|---|---|---|---|---|
| Rôle tuteur | Couche tuteur de lecture de progression, détection de besoins, compréhension des blocages, recommandation d’accompagnement humain | Pas de service unique nommé “TutorOrchestrator” confirmé ; domaine appuyé sur `buildconversationprogress`, `builduistate`, `qualitytracker.py`, synthèse, évaluation, projections produit [file:1][file:6] | `ALIGNE_DOC_PARTIEL` | La responsabilité métier existe de façon distribuée, mais la doc doit éviter de faire croire à un orchestrateur tuteur unique déjà nommé et stabilisé dans le code. |
| Consommation de progression | Le tuteur consomme `ConversationProgress` ou une projection lisible de progression [file:6][file:7] | `ConversationProgress` bien aligné avec `buildconversationprogress`, projection surtout via `ui-state` dans le réel [file:1] | `ALIGNE` | Très bon point d’ancrage du domaine tuteur ; conserver le nom doctrinal et citer `buildconversationprogress` comme nom réel observé. |
| Lecture produit montrable | Le tuteur lit un état produit dérivé, pas les champs P0 bruts [file:6][file:7] | `UIState` aligné avec `builduistate`, endpoint `ui-state` observé [file:1] | `ALIGNE` | Zone solide ; peut servir d’ossature documentaire pour la surface tuteur lisible. |
| Signaux de qualité conversationnelle | `ConversationQualitySignal` et signaux qualité/cohorte exploitables sans scoring opaque [file:6][file:7] | `QualityTracker`, `ConversationQualitySignal`, `analyticscohortdashboard.py` observés [file:1] | `ALIGNE` | Alignement fort ; faire apparaître explicitement `qualitytracker.py` comme implémentation réelle observée. |
| Vues cohorte | La cible prévoit des vues cohorte pour lecture tuteur [file:6] | Mention d’`analyticscohortdashboard.py` et de qualité/cohorte dans le réel, mais pas de contrat produit complet stabilisé [file:1] | `ALIGNE_DOC_PARTIEL` | La responsabilité existe au moins partiellement, mais la surface cohorte finale reste à mieux documenter. |
| Lecture mémoire gouvernée | Le tuteur peut consommer une mémoire gouvernée résumée, sans verbatim brut [file:6][file:7] | Endpoint `memory-summary` bien observé et bien raccordé au réel [file:1] | `ALIGNE` | Très bon point d’appui ; à conserver dans le périmètre tuteur comme surface de lecture autorisée. |
| Lecture synthèse | Le tuteur peut s’appuyer sur des synthèses partageables [file:6] | `SynthesisService` et endpoint `request-synthesis` observés [file:1][file:16] | `ALIGNE` | Bonne continuité entre doctrine et réel. |
| Lecture / usage des évaluations partageables | Le tuteur peut lire des évaluations partageables et recommander des moments d’évaluation [file:6][file:7] | Workflow réel dispersé entre `evaluationservice.py`, `evaluationworkflowengine.py`, `request-evaluation`, `finalize-evaluation`, `evaluation-readiness` [file:1] | `ALIGNE_DOC_PARTIEL` | Responsabilité couverte, mais vocabulaire et contrats à clarifier entre cible doctrinale et workflow réel. |
| Objet `EvaluationTrace` | Objet canonique de trace terminale structurée consommable par tuteur [file:6][file:7] | Mapping réel `LearnerEvaluationRecord` + traces d’évaluation + objets de trace, jugé flou par le glossaire [file:1] | `AMBIGU` | Ne pas forcer l’équivalence ; documenter le mapping comme zone de friction prioritaire. |
| Traces partageables | Le tuteur lit et commente certaines traces partageables [file:6] | Objets réels `Trace`, `TraceCriterionAssessment`, endpoint `generate-trace` [file:1][file:16] | `RENOMMER_DANS_DOC` | La doc tuteur doit faire apparaître les noms réels `Trace` et dérivés pour parler juste du réel. |
| Preuves partageables | Le tuteur peut lire certaines preuves selon règles de partage [file:6] | Objets réels `Evidence`, `EvidenceBundleView` [file:1] | `RENOMMER_DANS_DOC` | La doc doit citer explicitement `Evidence` comme nom réel observé. |
| Confidentialité du verbatim | Le tuteur n’a pas accès au verbatim non partagé [file:6][file:7] | Le cadre doctrine + projections backend-first va dans ce sens ; pas de preuve auditable d’un accès libre autorisé au tuteur [file:6][file:16] | `ALIGNE` | Garde-fou central à conserver tel quel dans la doc. |
| Interdiction de pilotage moteur | Le tuteur ne pilote pas directement le P0 ni les orchestrateurs apprenant [file:6][file:7] | Aucun service réel observé ne prouve un pilotage direct tuteur -> moteur ; le glossaire présente surtout des projections et services backend séparés [file:1] | `ALIGNE_DOC_PARTIEL` | Bon alignement conceptuel, mais la doc doit expliciter que la couche tuteur lit / interprète plutôt qu’elle ne commande. |
| Validation de certaines traces partageables | La canonique mentionne une éventuelle validation de certaines traces partageables par le tuteur [file:6] | Le complément 2.0 resserre : pas de pouvoir générique de validation terminale des évaluations en Hugo cœur standard [file:7] | `AMBIGU` | Clarifier dans la doc de domaine que “certaines validations de traces” n’équivalent pas à “validation terminale générique des évaluations”. |
| Validation terminale des évaluations | Pouvoir générique de validation terminale du tuteur | Explicitement non standard en Hugo cœur 2.0 ; seulement extension ultérieure spécifique [file:7] | `ABSENT / NOUVEAU_CONTRAT` | Ne pas documenter comme capacité standard du domaine. |
| Endpoint `GET /sessions/{id}/progress` | La cible 2.0 prévoit une lecture de progression dédiée [file:6][file:7] | Le glossaire la marque `AMBIGU` ; le réel observable passe surtout par `ui-state` et services backend, sans preuve claire d’une route dédiée [file:1] | `AMBIGU` | Garder comme contrat cible possible ; ne pas le présenter comme endpoint réellement observé sans preuve complémentaire. |
| Endpoint `GET /sessions/{id}/ui-state` | Point d’entrée produit montrable pouvant servir aussi à la lecture tuteur [file:6][file:7] | Endpoint `ui-state` fortement observé [file:1] | `ALIGNE` | Point d’ancrage fort pour la doc tuteur. |
| Endpoint `GET /sessions/{id}/memory-summary` | Point d’accès à mémoire gouvernée lisible [file:6] | Endpoint `memory-summary` observé [file:1] | `ALIGNE` | Point d’ancrage fort pour la doc tuteur. |
| Actions synthèse / évaluation | Le tuteur peut recommander ou déclencher selon cas des actions terminales sous garde-fous [file:6] | `request-synthesis` et `request-evaluation` observés localement ; runtime distant non garanti équivalent [file:1][file:16] | `ALIGNE_DOC_PARTIEL` | Bien distinguer réel local audité et runtime distant. |
| Catalogue des `ConversationQualitySignal` | La cible fixe la fonction mais laisse le catalogue détaillé ouvert [file:6][file:7] | Objet réel présent, mais catalogue canonique fin non stabilisé [file:1][file:7] | `ALIGNE_DOC_PARTIEL` | Bon alignement de fond, contrat détaillé encore ouvert. |
| Surface tuteur métier complète | La cible implique des surfaces tuteur lisibles, mais sans UI complète figée [file:6][file:7] | Les briques nécessaires existent, sans preuve complète d’une surface tuteur unifiée et stabilisée dans le réel local audité [file:1][file:16] | `AMBIGU` | Ne pas sur-affirmer une UI tuteur complète déjà livrée. |
| Runtime distant Encoors sur domaine tuteur | Équivalence local / distant | Non prouvée ; plusieurs points runtime restent `VRIFIER` dans l’audit croisé [file:16] | `A_VERIFIER` | Toute affirmation sur la couche tuteur en prod distante doit être marquée `A_VERIFIER`. |

---

## 3. Lecture consolidée

### 3.1 Zones les plus alignées

Les alignements les plus solides pour le domaine tuteur portent sur :
- `ConversationProgress` ;  
- `UIState` ;  
- `ConversationQualitySignal` / `QualityTracker` ;  
- `memory-summary` ;  
- synthèse ;  
- une partie du workflow d’évaluation.[file:1][file:6]

### 3.2 Frictions principales

Les principales frictions documentaires du domaine sont :
- l’absence de service unique nommé “orchestrateur tuteur” dans le réel observable ;
- le mapping encore flou entre `EvaluationTrace`, `LearnerEvaluationRecord` et objets de trace ;
- l’ambiguïté sur un endpoint `progress` réellement exposé ;
- la frontière exacte entre lecture/recommandation tuteur et validation terminale.[file:1][file:7]

### 3.3 Règle de décision pour la suite

La suite documentaire doit :
1. conserver la structure doctrinale 2.0 ;
2. ajouter les noms réels observés quand ils existent ;
3. ne pas transformer une cible tuteur en capacité livrée ;
4. ne pas confondre “lecture de traces partageables” avec “validation terminale générique d’évaluation”.[file:1][file:6][file:7]

# 02_decisions_documentaires — 60_orchestrateur_tuteur

## Domaine

- `DOMAINE_CODE = 60_orchestrateur_tuteur`
- `DOMAINE_LABEL = orchestrateur tuteur`

---

## 1. Objet du document

Ce document fixe les **décisions documentaires** à appliquer pour le domaine **orchestrateur tuteur** dans le corpus Hugo 2.0, en distinguant strictement :
- la **cible doctrinale 2.0** ;
- le **réel observable** dans Hugo cœur audité ;
- les zones encore **ouvertes**, **ambiguës** ou **à vérifier**.

Il ne décrit ni une refonte code immédiate, ni une preuve d’implémentation complète, ni une extension Hugo & Cie. Il sert à stabiliser la manière d’écrire juste sur ce domaine dans les specs, audits consolidés et futurs prompts Cursor.

---

## 2. Décisions de cadrage

### D1 — Conserver “orchestrateur tuteur” comme nom doctrinal cible

La documentation 2.0 conserve le terme **orchestrateur tuteur** comme nom doctrinal de la couche tuteur, car il structure correctement la cible Hugo cœur : lecture de progression, détection de blocages, interprétation, recommandation d’accompagnement et usage gouverné des traces partageables.[file:6][file:7]

En revanche, la doc ne doit pas laisser croire qu’un service unique et explicitement nommé `TutorOrchestrator` est déjà identifié comme tel dans le réel audité. Le réel observable doit être présenté comme une **capacité distribuée** s’appuyant notamment sur `ConversationProgress`, `UIState`, `QualityTracker`, synthèse, évaluation et surfaces de lecture associées.[file:1][file:6]

### D2 — Ne pas documenter le tuteur comme pilote du moteur apprenant

Toute documentation du domaine doit rappeler explicitement que le tuteur :
- ne pilote pas directement le P0 ;
- ne force pas librement les orchestrateurs apprenant ;
- n’a pas de contrôle direct sur la logique backend de conduite tutorale.[file:6][file:7]

La couche tuteur est une couche de **lecture, interprétation, recommandation et accompagnement humain**, jamais une couche de souveraineté moteur. Cette frontière doit être répétée dans les passages structurants du domaine.

### D3 — Maintenir la confidentialité-first comme garde-fou central

La doc du domaine tuteur doit rappeler explicitement que le tuteur n’a pas accès au verbatim non partagé, ni à un accès libre au contenu apprenant non partagé. Toute visibilité passe par des objets gouvernés, des projections produit et des mécanismes explicites de partage.[file:6][file:7]

Cette règle doit être écrite comme un invariant de domaine, pas comme un détail d’implémentation ou une option produit.

---

## 3. Décisions de vocabulaire

### D4 — Garder les noms doctrinaux structurants, puis ajouter les noms réels observés

Pour ce domaine, la règle de rédaction est :
1. nom doctrinal 2.0 pour raisonner juste ;
2. nom réel observé juste après, quand il est connu et utile.[file:1]

Les équivalences à faire apparaître explicitement dans la doc sont au minimum :
- `ConversationProgress` -> `buildconversationprogress` ;
- `UIState` -> `builduistate`, `uistatebuilder.py` ;
- `ConversationQualitySignal` / `QualityTracker` -> `qualitytracker.py`, `analyticscohortdashboard.py` ;
- synthèse -> `synthesisservice.py`, `request-synthesis` ;
- workflow d’évaluation -> `evaluationservice.py`, `evaluationworkflowengine.py`, `request-evaluation`, `finalize-evaluation`, `evaluation-readiness`.[file:1]

### D5 — Stabiliser le vocabulaire des objets tuteur réellement consultables

La doc tuteur doit faire apparaître explicitement les objets réels suivants lorsqu’elle parle de traces ou preuves consultables :
- `Trace`
- `TraceCriterionAssessment`
- `Evidence`
- `LearnerEvaluationRecord`.[file:1]

La décision n’est pas de rebaptiser toute la doctrine selon ces noms, mais d’éviter une doc cible qui parlerait seulement d’objets abstraits sans aucun raccord aux noms réellement observés.

### D6 — Traiter `EvaluationTrace` comme concept doctrinal encore non stabilisé dans le réel

La documentation conserve `EvaluationTrace` comme **nom doctrinal cible** pour la trace terminale structurée, car son rôle est fixé dans la base 2.0.[file:6][file:7]

En revanche, tant que le mapping n’est pas stabilisé, la doc doit écrire explicitement que le réel observable est aujourd’hui réparti entre `LearnerEvaluationRecord`, objets de trace et workflow d’évaluation. Il est donc interdit de présenter `EvaluationTrace` comme un objet réel déjà harmonisé dans le code.[file:1]

### D7 — Ne pas sur-documenter `PersistentObjects` comme backing model réel du domaine tuteur

Le concept `PersistentObjects` peut rester dans la doctrine produit pour désigner des objets durables montrables ou confirmables, mais il ne doit pas être décrit comme un modèle réel unique déjà observé dans le code. Le glossaire le signale comme concept produit encore ambigu dans son backing model réel.[file:1][file:7]

---

## 4. Décisions sur les surfaces et endpoints

### D8 — `ui-state` devient le point d’ancrage documentaire principal côté lecture tuteur

Dans la documentation du domaine, `GET /sessions/{id}/ui-state` doit être utilisé comme point d’appui principal pour décrire la lecture produit montrable utilisable aussi côté tuteur, car c’est la surface la plus solidement raccordée entre doctrine et réel observable.[file:1][file:6][file:7]

La doc doit rappeler que `UIState` est une **projection backend-first**, sans champs P0 bruts ni debug moteur exposé.[file:6][file:7]

### D9 — `memory-summary` est retenu comme surface autorisée de mémoire gouvernée

`GET /sessions/{id}/memory-summary` doit être retenu dans la doc du domaine comme surface autorisée de lecture mémoire gouvernée, utile au tuteur sans exposition de verbatim brut.[file:1][file:6]

C’est un point d’ancrage documentaire solide et il doit être cité comme tel.

### D10 — `progress` reste un contrat cible, pas une surface réelle à sur-affirmer

La documentation peut conserver `GET /sessions/{id}/progress` comme **contrat cible 2.0** ou endpoint visé, car la canonique et le complément le portent comme lecture de progression dédiée.[file:6][file:7]

En revanche, tant que l’audit ne prouve pas clairement cette route dans le réel, la doc doit préciser que le réel observable passe aujourd’hui surtout par `ui-state` et par les services backend associés. Ce point reste **ambigu** et ne doit pas être sur-documenté comme livré.[file:1]

### D11 — Les actions terminales restent documentées avec distinction cible / réel

La doc du domaine tuteur doit distinguer :
- le **rôle cible** du tuteur dans la lecture et la recommandation des moments pertinents de synthèse / évaluation ;[file:6]
- le **réel observable** des endpoints `request-synthesis`, `request-evaluation`, `finalize-evaluation`, `evaluation-readiness` côté local audité.[file:1]

La documentation doit en outre rappeler que l’équivalence runtime local / runtime distant n’est pas démontrée ici et reste à marquer `A_VERIFIER` si le texte parle de prod distante.[file:1]

---

## 5. Décisions sur le rôle exact du tuteur

### D12 — Distinguer strictement “lecture / commentaire / recommandation” et “validation terminale”

La documentation du domaine doit écrire explicitement que le tuteur :
- lit ;
- interprète ;
- commente ;
- recommande ;
- prépare l’accompagnement humain ;
- peut intervenir sur certaines traces partageables selon cadrage produit.[file:6][file:7]

Mais elle ne doit pas confondre cette capacité avec un pouvoir générique de validation terminale des évaluations.

### D13 — Ne pas documenter un pouvoir générique de validation terminale standard

À compter de cette décision documentaire, toute formulation laissant entendre qu’en Hugo cœur 2.0 standard le tuteur valide par défaut des évaluations formatives ou sommatives doit être corrigée. Le complément 2.0 verrouille explicitement que ce pouvoir générique n’est **pas** inclus par défaut dans Hugo cœur de référence.[file:7]

La doc peut mentionner qu’un **mode client spécifique ultérieur** pourrait ouvrir ce pouvoir, mais seulement comme extension ultérieure, sous garde-fous renforcés, et jamais comme capacité standard déjà acquise.[file:7]

### D14 — Maintenir ouverte la zone “validation de certaines traces partageables”

La canonique autorise encore une formulation où le tuteur peut valider **certaines traces partageables**.[file:6] Cette zone doit rester documentée comme **ouverte et à préciser**, sans assimilation automatique à la validation terminale d’évaluation.[file:7]

La bonne rédaction est donc :
- validation de certaines traces partageables : **possible mais à cadrer** ;
- validation terminale générique des évaluations : **hors standard Hugo cœur 2.0**.

---

## 6. Décisions sur les zones ouvertes

### D15 — Le catalogue fin des signaux qualité reste ouvert

La documentation doit affirmer que la fonction des signaux de qualité conversationnelle est fixée, mais que le **catalogue canonique détaillé** des `ConversationQualitySignal` reste encore ouvert et à formaliser plus finement.[file:6][file:7]

Il ne faut donc ni laisser cette zone vide, ni prétendre qu’elle est déjà complètement stabilisée.

### D16 — La surface tuteur métier complète reste sous-spécifiée

La doc peut affirmer qu’une couche tuteur est prévue et que plusieurs briques backend / projections produit existent déjà. En revanche, elle ne doit pas prétendre qu’une UI tuteur complète, unifiée et définitivement stabilisée est déjà prouvée dans le réel audité.[file:1][file:6]

Cette zone doit être marquée comme **partiellement ouverte** côté formulation produit.

### D17 — Tout ce qui dépend du runtime distant reste `A_VERIFIER`

Dès qu’un texte quitte le réel local audité pour parler de `hugoback.encoors.com`, d’une variante prod ou de flags runtime non inspectés dans le domaine tuteur, la documentation doit marquer explicitement `A_VERIFIER`.[file:1]

---

## 7. Consignes de réécriture pour les specs

### D18 — Ajouter une colonne “nom réel observé” dans les sections concernées

Dans les matrices et pseudo-schémas 2.0 touchant le domaine tuteur, il faut ajouter une colonne ou un sous-bloc “nom réel observé dans Hugo développé” afin de réduire les collisions de vocabulaire entre doctrine et code audité.[file:1]

### D19 — Ajouter un sous-bloc explicite “alignement avec le réel audité”

La spec formateur/tuteur 2.0 doit intégrer un sous-bloc de raccord rappelant au minimum :
- les objets tuteur lus via progression / `UIState` / mémoire gouvernée ;
- les objets réels de trace et preuve ;
- la dispersion actuelle autour d’`EvaluationTrace` ;
- l’état ambigu de l’endpoint `progress`.[file:1]

### D20 — Rappeler les garde-fous de non-régression dans toute réécriture du domaine

Toute mise à jour documentaire du domaine tuteur doit éviter :
- de réintroduire une logique front-driven ;
- de recentrer la vérité comportementale sur les prompts ;
- de transformer le tuteur en pilote du moteur ;
- de faire du verbatim brut une surface tuteur ;
- de prendre un nom de fichier Python comme preuve qu’un contrat cible est déjà entièrement livré.[file:1][file:6][file:7]

---

## 8. Synthèse de décision

Le domaine **orchestrateur tuteur** doit être documenté comme une **couche gouvernée de lecture et d’accompagnement humain**, appuyée sur progression, `UIState`, mémoire gouvernée, qualité conversationnelle, synthèse et objets partageables, sans pilotage direct du moteur apprenant.[file:6][file:7]

La doctrine 2.0 est maintenue ; le réel observable est raccordé explicitement par les noms concrets ; les zones floues — surtout `EvaluationTrace`, la validation terminale et l’endpoint `progress` — restent marquées comme telles, sans sur-affirmation.[file:1][file:7]

# 03_backlog_actions — 60_orchestrateur_tuteur

## Domaine

- `DOMAINE_CODE = 60_orchestrateur_tuteur`
- `DOMAINE_LABEL = orchestrateur tuteur`

---

## 1. Objet du document

Ce document transforme les constats du **rapport d’écarts**, de la **matrice d’écarts** et des **décisions documentaires** en backlog d’actions opérable pour le domaine **orchestrateur tuteur** de Hugo cœur.[file:45][file:47][file:46]

Il ne décrit pas une roadmap produit générale, ni une promesse de livraison immédiate. Il sert à ordonner les actions **documentaires**, **spécificationnelles**, **backend**, **surface produit** et **vérification runtime** nécessaires pour rendre ce domaine plus juste, plus lisible et plus implémentable sans contredire la doctrine 2.0 ni sur-affirmer le réel.[file:6][file:7][file:46]

---

## 2. Méthode utilisée dans ce fil

### 2.1 Chaîne documentaire à quatre artefacts

La méthode utilisée dans ce fil procède en quatre documents successifs pour un domaine donné :
1. `00_rapport_ecarts_<domaine>.md` ;
2. `01_matrice_ecarts_<domaine>.md` ;
3. `02_decisions_documentaires_<domaine>.md` ;
4. `03_backlog_actions_<domaine>.md`.[file:45][file:47][file:46]

Le **rapport d’écarts** qualifie le domaine, rappelle les règles de vérité, fixe le périmètre, puis décrit narrativement les écarts entre cible 2.0, réel observable et pont de vocabulaire.[file:45] La **matrice d’écarts** transforme ensuite ces constats en axes comparables, avec un statut d’alignement et une lecture d’écart par ligne.[file:47]

Les **décisions documentaires** stabilisent enfin la manière d’écrire juste sur le domaine : noms doctrinaux conservés, noms réels à ajouter, zones à maintenir ouvertes, interdits d’écriture, et surfaces à traiter comme ancrages principaux ou comme contrats encore ambigus.[file:46] Le présent **backlog d’actions** est la quatrième étape : il convertit ces décisions en actions ordonnées, typées, priorisées et rattachées à des preuves sources.[file:45][file:46][file:47]

### 2.2 Définition des domaines

Dans cette méthode, un **domaine** est une unité de travail documentaire et technique assez resserrée pour être auditée proprement, mais assez large pour produire un backlog cohérent. Un domaine porte un identifiant stable `DOMAINE_CODE` et un label lisible `DOMAINE_LABEL` ; ici : `60_orchestrateur_tuteur` / `orchestrateur tuteur`.[file:45][file:47][file:46]

Un domaine ne doit pas être défini par un simple nom de fichier ni par une intuition produit vague. Il est défini par un **périmètre fonctionnel**, des **objets canoniques**, des **noms réels observés**, des **garde-fous doctrinaux** et un **niveau de vérité** explicite distinguant cible, réel, ambigu et à vérifier.[file:45][file:6][file:1]

Pour le domaine `60_orchestrateur_tuteur`, le périmètre retenu dans le fil est strictement celui de la **couche tuteur de Hugo cœur** : lecture de progression, compréhension des blocages, aides à l’accompagnement humain, lecture de traces partageables, signaux de qualité et vues cohorte, sans ouvrir un chantier admin complet ni une extension Hugo & Cie.[file:45]

### 2.3 Règle de transformation en backlog

La règle de génération du backlog est la suivante :
- chaque friction importante observée dans `00` ou `01` doit produire soit une action, soit une décision explicite de non-action ;[file:45][file:47]
- chaque action doit dériver d’une décision documentaire stabilisée dans `02` ;[file:46]
- aucune action ne doit transformer une cible 2.0 en faux état livré ;[file:6][file:7]
- toute action dépendant du runtime distant doit être marquée `A_VERIFIER` tant qu’aucune preuve complémentaire n’existe.[file:16][file:46]

Le backlog distingue donc plusieurs familles d’actions :
- **DOC** : correction / réécriture documentaire ;
- **SPEC** : stabilisation de contrats cibles ;
- **BACK** : points backend à vérifier ou à compléter ;
- **PRODUIT** : cadrage de surface tuteur ou lecture montrable ;
- **AUDIT** : vérification complémentaire local / distant ;
- **CURSOR** : préparation d’un prompt d’intervention pour CTO / implémentation / audit ciblé.[file:45][file:46][file:47]

---

## 3. Principes de priorisation

La priorité est évaluée selon quatre questions :
- l’action réduit-elle un risque de mauvaise lecture du réel ;
- l’action évite-t-elle une régression doctrinale 2.0 ;
- l’action débloque-t-elle une spec ou un chantier CTO ;
- l’action dépend-elle d’un point runtime encore non vérifié.[file:6][file:7][file:16]

On utilise ici quatre niveaux :
- `P0` : indispensable pour parler juste du domaine ;
- `P1` : nécessaire pour stabiliser la spec et préparer les prompts CTO ;
- `P2` : utile pour consolider la surface, les contrats ou l’observabilité ;
- `P3` : amélioration complémentaire, à faire après stabilisation du socle.[file:45][file:46]

---

## 4. Backlog d’actions

| ID | Priorité | Type | Action | Justification | Dépendances | Sortie attendue |
|---|---|---|---|---|---|---|
| TUT-01 | `P0` | `DOC` | Réécrire la section de spec tuteur pour présenter l’orchestrateur tuteur comme **capacité distribuée** et non comme service unique déjà prouvé. | Le réel observable ne confirme pas un `TutorOrchestrator` unifié ; le domaine s’appuie sur `ConversationProgress`, `UIState`, `QualityTracker`, synthèse et évaluation.[file:47][file:46] | D1, D4 [file:46] | Section de spec réécrite avec distinction claire cible / réel observé. |
| TUT-02 | `P0` | `DOC` | Ajouter un sous-bloc systématique **“nom réel observé”** dans les sections tuteur concernées. | La décision documentaire impose de conserver les noms doctrinaux tout en raccordant explicitement `buildconversationprogress`, `builduistate`, `qualitytracker.py`, `evaluationworkflowengine.py`, etc.[file:46][file:1] | D4, D5, D18 [file:46] | Spécification enrichie avec équivalences doctrine / réel. |
| TUT-03 | `P0` | `DOC` | Verrouiller dans toute la doc tuteur les garde-fous : pas de pilotage direct du moteur, pas de verbatim non partagé, pas de souveraineté P0 côté tuteur. | Ce sont des invariants explicites de la cible 2.0 et des décisions de cadrage du domaine.[file:6][file:7][file:46] | D2, D3 [file:46] | Passages structurants homogènes dans toutes les docs du domaine. |
| TUT-04 | `P0` | `SPEC` | Clarifier noir sur blanc la frontière entre **lecture / commentaire / recommandation** et **validation terminale**. | La matrice signale une ambiguïté forte ; le complément 2.0 exclut un pouvoir générique standard de validation terminale du tuteur.[file:47][file:7][file:46] | D12, D13, D14 [file:46] | Sous-section de spec avec formulation verrouillée et cas autorisés / non autorisés. |
| TUT-05 | `P0` | `DOC` | Corriger toute formulation laissant penser qu’en Hugo cœur standard le tuteur valide par défaut les évaluations terminales. | Cette capacité est explicitement hors standard Hugo cœur 2.0 et relève au mieux d’une extension ultérieure spécifique.[file:7][file:46] | D13 [file:46] | Corpus nettoyé des formulations trompeuses. |
| TUT-06 | `P1` | `SPEC` | Produire une matrice canonique des **objets tuteur réellement consultables** : progression, `UIState`, `memory-summary`, synthèse, évaluation, traces, preuves. | Le rapport et la matrice montrent que le domaine existe surtout comme assemblage d’objets et services ; une matrice d’objets stabilise le périmètre sans fiction d’un service unique.[file:45][file:47] | TUT-01, TUT-02 | Tableau de référence domaine tuteur dans la spec. |
| TUT-07 | `P1` | `SPEC` | Formaliser le mapping documentaire de `EvaluationTrace` vers le réel observé (`LearnerEvaluationRecord`, objets de trace, workflow d’évaluation), sans forcer une équivalence non prouvée. | Le glossaire et la matrice qualifient ce point comme ambigu et prioritaire à clarifier.[file:47][file:46][file:1] | D6 [file:46] | Sous-bloc “mapping doctrinal / réel” avec statut `AMBIGU` assumé. |
| TUT-08 | `P1` | `DOC` | Introduire explicitement les objets réels `Trace`, `TraceCriterionAssessment`, `Evidence`, `LearnerEvaluationRecord` dans la documentation tuteur. | Les décisions documentaires imposent de les citer pour parler juste du réel sans abandonner le vocabulaire 2.0.[file:46][file:1] | D5 [file:46] | Terminologie enrichie dans les sections traces / preuves / évaluation. |
| TUT-09 | `P1` | `SPEC` | Définir une mini-grille canonique des **usages tuteur autorisés** par surface : lecture, commentaire, recommandation, validation éventuelle de certaines traces partageables, jamais pilotage moteur. | Le rôle tuteur est doctrinalement clair mais encore trop diffus dans les formulations.[file:45][file:47][file:46] | D2, D12, D14 [file:46] | Matrice “surface x action autorisée”. |
| TUT-10 | `P1` | `DOC` | Faire de `GET /sessions/{id}/ui-state` le point d’ancrage principal de la lecture tuteur montrable dans la doc. | `ui-state` est la surface la plus solidement alignée entre doctrine et réel observé.[file:47][file:46][file:1] | D8 [file:46] | Spec et schémas mis à jour avec `ui-state` comme ancrage principal. |
| TUT-11 | `P1` | `DOC` | Faire de `GET /sessions/{id}/memory-summary` le point d’ancrage principal de la mémoire gouvernée lisible côté tuteur. | `memory-summary` est explicitement retenu comme surface autorisée et solidement observée.[file:47][file:46] | D9 [file:46] | Documentation alignée sur la surface mémoire réellement lisible. |
| TUT-12 | `P1` | `DOC` | Maintenir `GET /sessions/{id}/progress` comme **contrat cible** uniquement, avec marquage explicite `AMBIGU` côté réel observé. | Le glossaire et la matrice ne prouvent pas clairement l’exposition réelle de cette route.[file:47][file:46][file:1] | D10 [file:46] | Formulation de spec corrigée, sans sur-affirmation. |
| TUT-13 | `P1` | `SPEC` | Produire une section “alignement avec le réel audité” dans la spec formateur/tuteur 2.0. | Les décisions documentaires demandent un sous-bloc de raccord explicite entre doctrine, objets réels et points ambigus.[file:46] | D19 [file:46] | Section de raccord prête à intégrer dans la spec 2.0. |
| TUT-14 | `P1` | `AUDIT` | Vérifier localement puis marquer proprement le statut réel de la lecture de progression dédiée (`progress`) et de toute surface tuteur non prouvée. | Plusieurs éléments restent `AMBIGU` ou `A_VERIFIER`, notamment l’endpoint `progress` et une surface tuteur métier complète.[file:47][file:45][file:16] | TUT-12 | Note d’audit complémentaire domaine tuteur. |
| TUT-15 | `P1` | `AUDIT` | Isoler ce qui est **local audité** versus ce qui serait **runtime distant Encoors** pour éviter toute contamination documentaire. | Le rapport rappelle explicitement que l’équivalence local / distant n’est pas démontrée.[file:45][file:47][file:16] | D17 [file:46] | Encadré ou annexe “local vs distant” dans le domaine 60. |
| TUT-16 | `P2` | `SPEC` | Construire un premier catalogue canonique de `ConversationQualitySignal` orienté usages tuteur, sans prétendre le clore définitivement. | La fonction est fixée mais le catalogue détaillé reste ouvert ; il faut sortir de l’implicite sans figer trop tôt.[file:6][file:7][file:46] | D15 [file:46] | Table initiale “signal / sens / lecture tuteur / statut”. |
| TUT-17 | `P2` | `PRODUIT` | Définir une maquette logique minimale de surface tuteur : progression, qualité, mémoire résumée, synthèse, évaluation, traces partageables. | Le rapport montre un socle backend solide mais une surface tuteur encore peu explicitée comme produit autonome.[file:45][file:47] | TUT-06, TUT-09, TUT-10, TUT-11 | Schéma de surface ou wireframe logique non engageant. |
| TUT-18 | `P2` | `PRODUIT` | Spécifier la zone **vues cohorte** en distinguant ce qui est déjà appuyé sur `analyticscohortdashboard.py` et ce qui reste cible produit. | La responsabilité cohorte existe partiellement, mais la surface finale n’est pas stabilisée.[file:47][file:45][file:1] | TUT-16 | Sous-section cohorte avec statut par bloc. |
| TUT-19 | `P2` | `BACK` | Vérifier si des contrats backend additifs sont nécessaires pour rendre les usages tuteur plus lisibles sans exposer P0 ni verbatim. | La doctrine impose des projections backend-first gouvernées ; la surface tuteur doit s’appuyer sur elles, pas sur des accès bruts.[file:6][file:7][file:45] | TUT-17 | Liste de contrats candidats ou conclusion “pas de nouveau contrat nécessaire”. |
| TUT-20 | `P2` | `DOC` | Documenter explicitement `PersistentObjects` comme concept doctrinal encore ambigu côté backing model réel, sans en faire un modèle code prouvé. | La décision documentaire interdit de le sur-documenter comme backing model unique déjà observé.[file:46][file:1][file:7] | D7 [file:46] | Passage de spec corrigé avec statut doctrinal explicite. |
| TUT-21 | `P2` | `CURSOR` | Préparer un prompt Cursor d’audit ciblé “domaine 60 tuteur” centré sur endpoints, builders, quality tracker, traces, preuves, évaluation et garde-fous de confidentialité. | Le domaine est transversal ; un prompt structuré est nécessaire pour auditer sans mélanger doctrine et réel.[file:45][file:46][file:1] | TUT-13, TUT-14, TUT-15 | Prompt CTO/audit prêt à exécuter sur repo. |
| TUT-22 | `P3` | `PRODUIT` | Étudier une surface tuteur unifiée seulement après stabilisation des contrats documentaires et des points ambigus runtime. | La matrice interdit de sur-affirmer une UI tuteur complète déjà livrée ; une surface unifiée ne doit venir qu’après consolidation.[file:47][file:46] | TUT-17, TUT-18, TUT-19 | Hypothèse de surface phase 2, non confondue avec le réel. |

---

## 5. Séquencement recommandé

### Phase A — Recalage documentaire immédiat

À lancer en premier : `TUT-01` à `TUT-05`, puis `TUT-10` à `TUT-13`.[file:46][file:47] Cette phase suffit déjà à empêcher les principales erreurs de récit : tuteur présenté comme pilote moteur, validation terminale sur-affirmée, faux service unique, ou endpoints présentés comme livrés alors qu’ils restent ambigus.[file:45][file:46]

### Phase B — Stabilisation de la spec et des objets

Ensuite : `TUT-06` à `TUT-09`, `TUT-16`, `TUT-20`.[file:47][file:46] Le but est de produire un domaine tuteur spécifié proprement, raccordé au réel observable, mais sans forcer une architecture fictive ni une UI finalisée.[file:6][file:7]

### Phase C — Vérification et préparation d’implémentation

Enfin : `TUT-14`, `TUT-15`, `TUT-17`, `TUT-18`, `TUT-19`, `TUT-21`, puis éventuellement `TUT-22`.[file:45][file:16][file:46] Cette phase ne doit démarrer qu’une fois les formulations documentaires stabilisées, sinon l’audit et les prompts CTO risquent de partir d’un cadre faux.[file:45][file:46]

---

## 6. Actions explicitement hors backlog immédiat

Les actions suivantes ne doivent **pas** être lancées dans ce backlog domaine 60, sauf décision ultérieure explicite :
- création d’un `TutorOrchestrator` monolithique juste pour coller à la doctrine ;
- ouverture d’un accès tuteur au verbatim brut non partagé ;
- ajout d’un pouvoir générique de validation terminale standard ;
- refonte admin transverse ;
- extension Hugo & Cie masquée en évolution Hugo cœur.[file:6][file:7][file:45][file:46]

Ces exclusions sont aussi importantes que les actions positives, car elles empêchent de recréer une architecture parallèle, de contourner les invariants 2.0 ou de transformer une zone encore ouverte en faux acquis produit.[file:6][file:7]

---

## 7. Critères de done du backlog domaine 60

Le backlog pourra être considéré comme correctement exécuté lorsque les conditions suivantes seront réunies :
- la documentation tuteur parle juste du réel sans sur-affirmation ;
- les noms doctrinaux et les noms réels observés sont raccordés explicitement ;
- la frontière lecture/recommandation/validation est stabilisée ;
- `ui-state` et `memory-summary` sont traités comme ancrages principaux ;
- `progress`, `EvaluationTrace` et la surface tuteur complète sont marqués selon leur vrai statut (`contrat cible`, `ambigu`, `à vérifier`) ;
- un prompt Cursor d’audit / intervention est prêt à être utilisé par le CTO.[file:46][file:47][file:45]

---

## 8. Synthèse opérationnelle

Le domaine `60_orchestrateur_tuteur` ne demande pas d’abord une invention fonctionnelle ; il demande d’abord un **recalage documentaire et de contrat**.[file:45][file:47] Le socle réel existe déjà en grande partie via progression, `UIState`, mémoire gouvernée, synthèse, évaluation et qualité conversationnelle, mais la manière de le raconter et de le raccorder à la doctrine 2.0 doit être stabilisée avant toute extension de surface ou d’implémentation plus ambitieuse.[file:45][file:46][file:6]

---

## 9. Mise à jour cluster audit vague 5 — parcours tuteur E2E

**Sources :** `cluster_tests_e2e_et_encoors_vague5_resultats.md` · scénario T1.

| Capacité | Statut local |
|---|---|
| Timeline tuteur lié (`DashboardTimelineView`) | **ALIGNE** — API E2E |
| Verbatim non partagé masqué | **ALIGNE** — B1-01 confirmé |
| Validation trace | **ALIGNE** — POST `/traces/{id}/validate/` |
| Surface prod `/app/tutor` | **PARTIEL** — code OK ; browser E2E absent |
| Encoors parcours tuteur | **A_VÉRIFIER** |

---

## 10. Mise à jour cluster 8 OPS — smoke tuteur navigateur

| Capacité | Statut |
|---|---|
| `/app/tutor` charge sans erreur | **ALIGNE** — Playwright |
| Timeline sessions & traces visible | **ALIGNE** |
| Verbatim non partagé absent DOM | **ALIGNE** |
| Encoors timeline UI | **A_VÉRIFIER** |
