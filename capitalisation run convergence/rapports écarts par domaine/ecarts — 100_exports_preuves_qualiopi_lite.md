# 00_rapport_ecarts — 100_exports_preuves_qualiopi_lite

## Domaine

- `DOMAINE_CODE = 100_exports_preuves_qualiopi_lite`
- `DOMAINE_LABEL = exports, preuves et Qualiopi lite`

---

## 1. Objet du rapport

Ce rapport qualifie, pour le seul domaine **exports / preuves / Qualiopi lite** de Hugo cœur, l’écart entre :
- la **cible 2.0** décrite par la spec canonique et les documents projet associés ;
- le **réel observable** décrit par les audits du workspace Hugo réel ;
- le **pont de vocabulaire** fourni par le glossaire d’alignement.

Le document ne vaut ni décision technique définitive, ni plan de refonte. Il sert à établir une lecture propre du domaine, à distinguer ce qui relève déjà du réel de ce qui reste une cible, et à préparer la matrice d’écarts, les décisions documentaires et le backlog d’actions.

---

## 2. Règles de lecture et niveau de vérité

### 2.1 Réel, cible et glossaire

Pour parler du **réel**, ce domaine est lu à partir du corpus d’audit du Hugo développé, avec priorité au corpus “Hugo réel audité”, en particulier :
- `02_ETAT_MOTEUR_REEL.md` pour les services backend, la génération de traces, les endpoints d’exports et les objets métier ;
- `03_ETAT_PRODUIT_REEL.md` pour ce qui est effectivement montrable côté front et back-office ;
- `07_RUNTIME_DEMO_REFERENCE.md` et `09_PARCOURS_DEMO_ET_SCENARIOS.md` pour ce qui est démontrable sans sur-vendre ;
- `05_ECARTS_DOC_CODE_PRODUIT.md` pour les contradictions confirmées entre docs, code et produit.

Pour parler de la **cible**, on s’appuie d’abord sur :
- `spec_canonique_hugo_2_0.md` ;
- puis, lorsque c’est utile pour les formulations historiques du périmètre POC export/preuves/Qualiopi lite, sur `SPEC_POC_v1.5-update-27_03_2026.md`, en rappelant explicitement qu’il s’agit d’un cadrage antérieur et non de la doctrine 2.0.

Le **glossaire d’alignement** ne sert ici qu’à raccorder les noms doctrinaux aux noms réels observés (`Trace`, `Evidence`, `EvidenceBundleView`, `LearnerEvaluationRecord`, endpoints réels). Il ne constitue jamais une preuve d’implémentation à lui seul.

### 2.2 Garde-fous de lecture

- La spec 2.0 décrit une **cible**, pas une preuve de livraison.
- Une ancienne spec POC qui mentionne exports, pack audit ou bundle Qualiopi ne prouve pas à elle seule l’état exact du runtime actuel.
- Une présence d’endpoint, de modèle ou de vue ne prouve pas automatiquement un workflow métier complet, stable et démontré de bout en bout.
- Toute affirmation dépendant du runtime distant, de flags, d’une variante Encoors ou d’une configuration non auditée localement reste marquée `A_VERIFIER`.
- Le domaine est lu strictement dans **Hugo cœur** : pas de dérive vers Hugo & Cie, pas de relecture de ce domaine comme une brique de constellation externe.

---

## 3. Périmètre cible 2.0 du domaine

### 3.1 Ce que la cible 2.0 fixe déjà

Dans la cible Hugo 2.0, le domaine **exports / preuves / Qualiopi lite** est un domaine de **sortie gouvernée** du moteur et non un sous-produit administratif autonome.

La spec canonique fixe déjà plusieurs invariants utiles :

- Hugo doit pouvoir produire des **exports structurés**, notamment CSV et JSON.
- Les **preuves** doivent rester rattachées à une session, une trace ou un contexte métier explicite ; elles ne doivent jamais circuler comme objets flottants.
- Les **preuves photo** doivent être gérées avec suppression EXIF par défaut et GPS en opt-in.
- Les règles de **confidentialité-first**, de **partage explicite** et de **multi-tenant strict** s’appliquent aussi aux exports, aux bundles et aux preuves.
- Le produit ne doit pas contourner la validation humaine ni laisser croire qu’un export ou un bundle vaut à lui seul preuve de certification, de conformité complète ou de validation autonome.

Autrement dit, la cible 2.0 fixe solidement le **cadre de gouvernance** de ce domaine, même si elle n’entre pas encore dans tout le détail opérationnel d’un pack Qualiopi finalisé.

### 3.2 Ce que la cible 2.0 laisse encore ouvert

Le corpus 2.0 fixe bien la responsabilité du domaine, mais laisse encore ouvertes plusieurs précisions documentaires et techniques :
- la nomenclature canonique exacte des types d’exports ;
- le contrat final entre traces, évaluations, preuves et bundles d’audit ;
- la place exacte de “Qualiopi lite” dans la terminologie 2.0 durable ;
- la granularité des vues et filtres par rôle pour déclencher, consulter ou télécharger ces artefacts.

Il faut donc lire ce domaine comme **cadré dans ses invariants**, mais encore **partiellement ouvert dans sa formalisation cible détaillée**.

---

## 4. Photo du réel observé

### 4.1 Présence réelle d’exports et de preuves

Le réel audité montre que le domaine n’est pas théorique. Il existe bien dans Hugo développé une base concrète autour de :
- `Trace` pour les objets de trace métier ;
- `Evidence` pour les preuves ;
- des endpoints d’exports ;
- un endpoint orienté bundle Qualiopi ;
- des vues ou services associés à l’assemblage d’artefacts exportables.

Le glossaire d’alignement confirme que les noms réels `Trace`, `Evidence` et `EvidenceBundleView` sont des ancrages importants pour ce domaine. Il recommande d’ailleurs de mieux les faire apparaître dans la documentation cible, précisément pour éviter une doc trop abstraite.

### 4.2 Contrats historiques observables côté POC

Le document `SPEC_POC_v1.5-update-27_03_2026.md` décrit un périmètre POC où Hugo produit :
- des exports CSV ;
- un export JSON de type `traceRichV1` ;
- des preuves photo rattachées ;
- un endpoint `POST quality/qualiopi/evidence-bundle` ;
- un ZIP minimal exploitable pour un audit Qualiopi lite.

Ce document ne vaut pas preuve du runtime 2.0 actuel, mais il reste utile pour comprendre la responsabilité historique déjà portée par Hugo cœur : produire des traces, des preuves, des exports auditables et un bundle orienté conformité légère.

### 4.3 Écarts confirmés dans le réel local

Le corpus d’écarts confirme plusieurs points importants sur le réel local :

- les endpoints d’exports existent bien côté backend ;
- le pack Qualiopi lite est bien documenté comme artefact métier dans l’ancien périmètre POC ;
- le réel local comporte des objets et routes compatibles avec cette responsabilité ;
- mais la génération de trace est actuellement **plus minimale** que certaines docs peuvent le laisser croire.

Le point le plus critique signalé par `05_ECARTS_DOC_CODE_PRODUIT.md` est que le `generate-trace` local produit un **payload minimal** avec peu d’enrichissement, ce qui limite mécaniquement la richesse des exports aval, des bundles d’audit et de certaines preuves dérivées.

### 4.4 Preuves photo et rattachement métier

Le cadrage POC historique est explicite : une `Evidence` doit être rattachée au moins à une `Trace` ou à une `HugoSession`, sans preuve orpheline, avec suppression EXIF par défaut et GPS en opt-in.

Cette logique est cohérente avec la doctrine 2.0 actuelle. Le domaine des preuves apparaît donc comme une zone de **continuité doctrinale forte** entre le POC ancien et la cible Hugo cœur 2.0, même si le niveau exact de robustesse du workflow actuel doit continuer à être qualifié par audit du réel.

### 4.5 Surface produit observable

Le domaine est surtout visible côté :
- export métier ;
- back-office / administration / formateur-coordo ;
- bundles d’audit ;
- pièces rattachées à des sessions ou traces.

Il n’apparaît pas comme une grande surface conversationnelle autonome côté apprenant. Cela confirme que ce domaine est principalement un **domaine d’artefacts métier gouvernés**, issu du moteur et des objets structurés, et non un sous-produit UI indépendant.

---

## 5. Analyse narrative des écarts

### 5.1 Zone de bon alignement

Le domaine est **réellement présent** et globalement bien aligné sur la doctrine de fond.

Le réel, le glossaire et les anciens contrats convergent sur plusieurs points solides :
- Hugo cœur produit bien des traces et des preuves ;
- il existe une logique d’exports structurés ;
- les preuves sont pensées comme rattachées à un contexte métier ;
- le domaine Qualiopi lite est historiquement porté dans Hugo cœur, pas dans une extension séparée ;
- la confidentialité et le partage restent des contraintes constitutives du domaine.

Sur cette base, il n’y a **pas** lieu de traiter le domaine comme absent ni de déclencher une refonte par principe.

### 5.2 Écart majeur : richesse documentaire surestimée par certaines docs

L’écart principal ne porte pas sur l’existence du domaine, mais sur le **niveau réel de richesse** de certains artefacts.

Le corpus d’écarts signale que la génération de trace locale est aujourd’hui plus pauvre que ce que certaines docs ou attentes peuvent laisser imaginer. Si la trace amont est minimale, les exports, bundles et preuves dérivées restent forcément moins riches, moins contextualisés ou moins démonstratifs qu’une lecture ambitieuse des specs pourrait le suggérer.

Le point important ici est documentaire : il faut cesser d’écrire le domaine comme si tous les exports Qualiopi lite étaient déjà riches, consolidés et probants au même niveau que la cible projetée.

### 5.3 Écart de vocabulaire : doctrine 2.0 vs objets réels

La doctrine 2.0 parle d’exports structurés, de preuves, de validation humaine, d’artefacts partageables. Le réel, lui, s’appuie sur des objets plus concrets :
- `Trace` ;
- `Evidence` ;
- `EvidenceBundleView` ;
- `LearnerEvaluationRecord` pour une partie de la zone évaluation/export ;
- des endpoints d’exports et de bundle Qualiopi.

Le glossaire montre ici un besoin classique de **raccord de vocabulaire** :
- garder les notions doctrinales 2.0 pour raisonner juste ;
- faire apparaître les noms réels observés pour parler juste du code ;
- ne pas inventer trop tôt un modèle cible unique là où le réel reste réparti entre plusieurs objets.

### 5.4 Écart de formalisation : Qualiopi lite encore plus POC que canon 2.0

Le terme **Qualiopi lite** est fortement ancré dans le cadrage POC ancien, avec un bundle ZIP minimal exploitable, des exports horodatés, des citations documentaires et des extraits d’audit log.

Dans la cible 2.0, les principes de gouvernance restent valides, mais la formalisation canonique du domaine n’est pas encore aussi détaillée sous cette étiquette. Il existe donc un écart entre :
- un **nom et un contrat historique POC** assez explicites ;
- une **cible 2.0** plus doctrinale, plus générale, et moins cristallisée sur ce label précis.

Le bon traitement n’est pas de supprimer le terme, ni de le figer comme canon définitif sans discussion. Il faut plutôt le documenter comme **artefact métier réel / historique**, puis clarifier sa place exacte dans la nomenclature 2.0.

### 5.5 Écart sur la chaîne complète de preuve

Le domaine repose sur une chaîne implicite :
session -> message -> trace -> validation -> preuve -> partage -> export -> bundle.

Cette chaîne est doctrinalement cohérente, mais le corpus disponible ne prouve pas encore que tous ses maillons soient :
- homogènes ;
- riches ;
- stables ;
- également visibles dans toutes les variantes runtime.

Le point de friction n’est donc pas l’absence d’objet, mais la **complétude de la chaîne de preuve**. C’est particulièrement sensible pour les usages d’audit, car un bundle peut exister nominalement sans que tous ses intrants soient au niveau documentaire attendu.

### 5.6 Distant, prod et variantes : zone à maintenir sous contrôle

Le document d’écarts rappelle explicitement que l’API distante n’a pas été inspectée de bout en bout et que plusieurs points restent `A_VERIFIER` dès qu’on sort du local.

Il faut donc éviter d’affirmer trop vite :
- que le bundle Qualiopi lite distant est strictement équivalent au local ;
- que les contrats d’exports sont identiques entre variantes ;
- que les filtres, droits ou contenus des bundles sont démontrés en prod ;
- ou que la richesse réelle des exports de démo reflète toujours l’état du backend local audité.

---

## 6. Lecture de synthèse par niveau de vérité

### 6.1 Implémenté / observable

Peuvent être tenus comme **implémentés ou observables** dans ce domaine :
- l’existence d’objets `Trace` ;
- l’existence d’objets `Evidence` ;
- une capacité d’exports structurés ;
- l’existence d’un endpoint orienté Qualiopi lite / evidence bundle dans le cadrage POC et la documentation d’API ;
- le rattachement métier attendu des preuves à une session ou à une trace ;
- l’existence d’une logique de bundle d’audit au moins nominale et historiquement portée par Hugo cœur.

### 6.2 Cible 2.0

Relèvent de la **cible 2.0** :
- une formalisation plus canonique et durable du domaine exports / preuves / bundles ;
- une articulation stabilisée entre trace terminale, évaluation, preuve, partage, export et validation humaine ;
- une nomenclature plus propre des artefacts exportables par rôle ;
- une clarification plus nette entre ce qui est export métier, export technique, preuve partagée et bundle d’audit.

### 6.3 Écarts confirmés

À ce stade, les **écarts confirmés** sont principalement :
- certaines docs peuvent surestimer la richesse effective des traces et donc des exports dérivés ;
- le vocabulaire 2.0 et le vocabulaire réel ne sont pas encore complètement raccordés sur cette zone ;
- le label “Qualiopi lite” est historiquement fort côté POC, mais pas encore complètement re-canonisé dans la documentation 2.0 ;
- la chaîne complète de preuve n’est pas suffisamment documentée comme continuum de responsabilités et de niveaux de preuve.

### 6.4 A vérifier

Restent explicitement `A_VERIFIER` :
- le comportement exact du runtime distant sur les exports et bundles ;
- l’équivalence local / Encoors sur ce domaine ;
- les permissions fines par rôle sur téléchargement, consultation ou génération des artefacts ;
- la composition réelle des bundles dans les variantes non auditées ;
- le niveau de robustesse des exports prod au regard des attentes d’audit en situation réelle.

---

## 7. Garde-fous pour la suite documentaire et technique

### 7.1 Ce qu’il ne faut pas faire

Pour ce domaine, il faut éviter :
1. de lire la cible 2.0 comme preuve qu’un système complet d’exports conformité est déjà livré ;
2. de prendre une ancienne spec POC comme photographie exacte du runtime actuel ;
3. de présenter le bundle Qualiopi lite comme une preuve de conformité complète, autonome ou certifiante ;
4. de relire ce domaine comme une simple tuyauterie d’exports alors qu’il dépend d’objets métier gouvernés en amont ;
5. de confondre la présence d’un endpoint ou d’un modèle avec la qualité effective des artefacts produits.

### 7.2 Ce qu’il faut privilégier

La bonne trajectoire sur ce domaine est :
- clarifier les **contrats d’artefacts** ;
- aligner le **vocabulaire** entre doctrine 2.0 et objets réels ;
- documenter honnêtement le **niveau réel de richesse** des traces et exports observés ;
- séparer clairement **preuve métier**, **export technique**, **export métier** et **bundle d’audit** ;
- renforcer le domaine par compléments backend additifs plutôt que par réécriture globale.

---

## 8. Conclusion opérationnelle du domaine

Le domaine `100_exports_preuves_qualiopi_lite` est un **domaine réel**, déjà présent dans Hugo cœur, et non un simple projet sur étagère.

Le socle observable est clair : objets de trace, objets de preuve, exports structurés, logique de bundle audit, continuité avec un héritage POC orienté Qualiopi lite. En revanche, la cible 2.0 et le réel ne sont pas encore parfaitement raccordés sur la **richesse effective des artefacts**, la **nomenclature canonique**, et la **documentation de la chaîne complète de preuve**.

Ce domaine doit donc être lu comme :
- **présent dans le réel** ;
- **globalement cohérent avec la doctrine 2.0** ;
- **encore partiellement hétérogène dans son vocabulaire et sa formalisation** ;
- **à renforcer d’abord par clarification documentaire, raccord des contrats et amélioration additive du backend**, sans sur-affirmer l’état du runtime distant ni réinventer une architecture parallèle.

# 01_matrice_ecarts — 100_exports_preuves_qualiopi_lite

## Domaine

- `DOMAINE_CODE = 100_exports_preuves_qualiopi_lite`
- `DOMAINE_LABEL = exports, preuves et Qualiopi lite`

---

## 1. Règle de lecture

Cette matrice ne déduit jamais le réel d’un seul document.

Chaque ligne articule explicitement :
- la **cible 2.0** quand elle existe ;
- le **réel observable** dans les audits et écarts du workspace ;
- le **glossaire d’alignement** quand il aide à raccorder le vocabulaire ;
- les anciens contrats POC quand ils éclairent l’historique fonctionnel du domaine sans être pris pour une preuve du runtime actuel.

Les statuts utilisés sont :
- `ALIGNE`
- `ALIGNE_DOC_PARTIEL`
- `RENOMMER_DANS_DOC`
- `AMBIGU`
- `A_VERIFIER`
- `ABSENT / NOUVEAU_CONTRAT`

---

## 2. Matrice des écarts

| Élément du domaine | Cible 2.0 | Réel / observé | Statut | Lecture d’écart | Action documentaire recommandée |
|---|---|---|---|---|---|
| Exports structurés CSV / JSON | La spec canonique 2.0 fixe que Hugo cœur doit pouvoir produire des exports structurés, notamment CSV et JSON. | Le cadrage POC historique décrit `POST exports/run`, `GET exports/download/{runid}`, un export JSON de type `traceRichV1` et un export CSV pivot. | ALIGNE_DOC_PARTIEL | La responsabilité métier est bien couverte, mais la doc 2.0 reste plus générique que les noms de contrats réellement observés. | Garder la formulation canonique 2.0 et ajouter les noms réels d’exports déjà observés dans les annexes de domaine. |
| Existence d’un domaine “preuves” rattaché au moteur | La cible 2.0 prévoit des traces et preuves rattachées à une session ou une trace, sous gouvernance métier. | Le réel et le cadrage POC utilisent explicitement les objets `Trace` et `Evidence`. | RENOMMER_DANS_DOC | Le domaine existe réellement, mais la doc 2.0 doit mieux faire apparaître les noms réels `Trace` et `Evidence`. | Ajouter dans les docs de domaine un bloc de vocabulaire reliant “trace” -> `Trace` et “preuve” -> `Evidence`. |
| Preuve photo rattachée à un contexte explicite | La cible 2.0 fixe qu’une preuve photo doit rester rattachée à une session ou une trace, sans flotter librement hors gouvernance. | Le cadrage POC précise qu’une `Evidence` doit être rattachée à une `Trace` ou à une `HugoSession`, sinon l’API refuse la validation. | ALIGNE_DOC_PARTIEL | Très bon alignement doctrinal, mais la documentation active doit distinguer ce qui relève du principe 2.0 et ce qui relève du contrat POC historique. | Écrire ce point comme responsabilité métier stable, puis citer le contrat POC comme ancrage historique utile, sans le prendre pour vérité runtime complète. |
| Suppression EXIF par défaut | La cible 2.0 fixe que les preuves photo sont gérées avec suppression EXIF par défaut. | Le cadrage POC décrit explicitement l’upload photo avec EXIF supprimés par défaut. | ALIGNE | L’alignement doctrine / contrat historique est net. | Conserver tel quel dans les docs de domaine. |
| GPS en opt-in sur les preuves photo | La cible 2.0 fixe que le GPS reste en opt-in. | Le cadrage POC détaille `gpsOptIn`, métadonnées GPS structurées et conservation uniquement sur consentement. | ALIGNE | Le point est doctrinalement stable et historiquement explicite. | Conserver comme invariant documentaire du domaine. |
| Export technique de payload de trace | La cible 2.0 fixe des exports structurés mais ne canonise pas finement les libellés d’exports techniques hérités du POC. | Le cadrage POC mentionne un export JSON `traceRichV1` destiné à l’interop / branchements. | ALIGNE_DOC_PARTIEL | Le besoin existe réellement, mais le nom `traceRichV1` relève davantage d’un contrat historique ou technique que d’un vocabulaire canonique 2.0 stabilisé. | Documenter `traceRichV1` comme nom réel observé / historique, sans le faire passer pour catégorie canonique 2.0 définitive. |
| Export CSV pivot “1 ligne trace / item compétence” | La cible 2.0 autorise des exports structurés ; elle ne fixe pas encore une forme canonique aussi détaillée. | Le cadrage POC décrit un CSV pivot avec structure “1 ligne trace / item compétence”, séparateur configurable, UTF-8 BOM, dates ISO. | ALIGNE_DOC_PARTIEL | Le réel historique est assez précis, mais la cible 2.0 n’a pas encore transformé cette granularité en contrat canonique durable. | Garder cette forme dans les docs de domaine comme contrat réel historique / observé, pas comme seule forme canonique possible. |
| Endpoint d’exports métier | La cible 2.0 suppose des exports structurés et gouvernés, sans figer tous les endpoints. | Le cadrage POC décrit `POST exports/run` et `GET exports/download/{runid}`. | RENOMMER_DANS_DOC | La responsabilité est alignée, mais les noms réels d’endpoints doivent apparaître dans la doc de domaine. | Ajouter un sous-bloc “endpoints réels observés” dans la doc de domaine. |
| Bundle d’audit Qualiopi lite | La cible 2.0 prévoit des exports et preuves gouvernés, mais ne formalise pas encore complètement la place canonique du label “Qualiopi lite”. | Le cadrage POC décrit explicitement `POST quality/qualiopi/evidence-bundle` et un ZIP minimal exploitable. | AMBIGU | La capacité existe historiquement et nominalement, mais sa place exacte dans la nomenclature 2.0 reste à stabiliser. | Documenter “Qualiopi lite” comme artefact métier historique réel, en attente d’un calage canonique plus propre dans la cible 2.0. |
| Contenu minimal du bundle Qualiopi lite | La cible 2.0 fixe des garde-fous de gouvernance, mais pas encore un contrat canonique détaillé du ZIP. | Le cadrage POC annonce : exports CSV/JSON, validations, preuves, audit log filtré, overlays actifs, documents actifs / citations RAG, synthèse de couverture. | ALIGNE_DOC_PARTIEL | Le contrat historique est utile, mais il ne faut pas le faire passer pour contrat 2.0 stabilisé ni pour preuve complète du runtime local actuel. | Reprendre ce contenu en “contrat POC historique observé”, distinct d’un futur contrat canonique 2.0. |
| Extraits d’audit log dans le bundle | La cible 2.0 impose confidentialité et partage explicite, mais ne détaille pas encore finement la place des extraits d’audit log dans les bundles. | Le cadrage POC indique que l’accès à la traçabilité se fait via les exports et le pack Qualiopi lite, qui inclut des extraits d’audit log filtrés. | ALIGNE_DOC_PARTIEL | La fonction existe côté cadrage historique, mais la doc 2.0 doit mieux préciser comment l’écrire sans créer d’ambiguïté sur les droits ni sur le runtime distant. | Documenter cette capacité comme sortie filtrée et gouvernée, non comme accès libre à l’audit log brut. |
| Export / bundle comme artefact auditable mais non certifiant | La cible 2.0 interdit de laisser croire qu’Hugo certifie seul ou remplace la validation humaine finale. | Le bundle Qualiopi lite POC est décrit comme “ZIP minimal exploitable” et non comme couverture fine des 32 indicateurs ni preuve autonome de certification. | ALIGNE | Le cadrage POC est cohérent avec la doctrine 2.0 : aide audit, pas certification automatique. | Garder cette frontière explicitement dans tous les documents du domaine. |
| Rattachement des preuves au partage explicite | La cible 2.0 impose partage explicite et absence d’accès libre au non-partagé. | Le cadrage POC distingue `shareSummary`, `shareEvidence`, `shareVerbatim` et limite les rôles non apprenant à ce qui a été partagé. | ALIGNE | Bon alignement de doctrine et de contrat historique. | Maintenir cette distinction comme invariant transverse du domaine. |
| Capacités d’export par rôle non apprenant | La cible 2.0 indique qu’org admin et autres rôles ont des capacités à préciser, sous garde-fous de confidentialité. | Le cadrage POC donne à l’ORGADMIN la capacité d’administrer, déclencher exports et pack Qualiopi, tout en restant soumis aux mêmes règles de confidentialité sur le contenu apprenant. | ALIGNE_DOC_PARTIEL | Le sens est bon, mais la granularité précise des droits par rôle reste partiellement ouverte dans le corpus 2.0. | Ajouter une matrice par rôle dans les décisions documentaires, sans sur-affirmer des permissions plus fines que celles démontrées. |
| EvidenceBundleView comme nom réel | La cible 2.0 parle de preuves / exports / bundles sans encore imposer un nom objet unique. | Le glossaire d’alignement mentionne `EvidenceBundleView` comme nom réel utile pour la zone preuve / export. | RENOMMER_DANS_DOC | Le pont de vocabulaire existe et doit être visible dans la doc. | Faire apparaître `EvidenceBundleView` dans les annexes de noms réels observés du domaine. |
| Mapping entre EvaluationTrace cible et objets réels d’évaluation/export | La cible 2.0 parle d’`EvaluationTrace` comme trace terminale structurée. | Le glossaire indique une zone de friction entre `EvaluationTrace`, `LearnerEvaluationRecord`, objets de trace et validation partagée. | AMBIGU | Le mapping conceptuel existe, mais la nomenclature réelle n’est pas assez stabilisée pour être écrite comme alignée. | Marquer explicitement cette zone comme floue dans la matrice et traiter séparément dans les décisions documentaires. |
| Génération de trace suffisamment riche pour alimenter les exports | La cible 2.0 suppose des traces structurées exploitables pour synthèse, évaluation, exports et preuves. | `05_ECARTS_DOC_CODE_PRODUIT.md` signale que `generate-trace` local produit aujourd’hui un payload minimal, avec listes vides et faible richesse documentaire. | ABSENT / NOUVEAU_CONTRAT | La responsabilité “produire une trace” existe, mais le niveau de richesse attendu par certaines docs n’est pas couvert dans le réel local. | Ne pas parler d’exports riches sans qualifier la pauvreté actuelle de certains intrants ; prévoir un contrat additif de “trace exportable enrichie”. |
| Qualité démontrée des bundles produits par le runtime local | La cible 2.0 demande des artefacts gouvernés, mais pas d’affirmation sans preuve. | Le cadrage POC décrit le bundle ; le document d’écarts montre que certains intrants locaux sont plus pauvres qu’attendu. | AMBIGU | Le bundle existe comme capacité nominale / historique, mais sa richesse réelle bout en bout n’est pas entièrement démontrée par le corpus disponible. | Distinguer “capacité nominale existante” et “richesse effective démontrée localement”. |
| Équivalence local / runtime distant sur exports et bundle | La cible 2.0 n’autorise pas à déduire le prod du local ni l’inverse. | Le document d’écarts rappelle que l’API distante n’est pas prouvée équivalente au local et que les points prod restent à vérifier. | A_VERIFIER | Toute affirmation sur Encoors, les variantes ou les flags distants doit rester prudente. | Ajouter un encadré `A_VERIFIER` systématique sur runtime distant, composition du bundle et permissions effectives en prod. |
| Multi-tenant strict appliqué aux exports et bundles | La cible 2.0 fixe un multi-tenant strict et une absence de lecture/écriture inter-tenant. | Le cadrage POC pose `organisationId` partout, `SET LOCAL app.organisationid`, RLS et tests cross-tenant, y compris pour les tables métier concernées par les exports. | ALIGNE_DOC_PARTIEL | La doctrine est claire et le cadrage historique est détaillé, mais la preuve runtime prod réelle n’est pas établie ici. | Écrire : invariant cible ferme, ancrages locaux forts, preuve prod complète `A_VERIFIER`. |
| Audit log consultable directement par API | La cible 2.0 n’exige pas une lecture brute directe. | Le cadrage POC précise qu’il n’existe pas d’endpoint direct de lecture d’audit log ; l’accès passe par exports et bundle filtré. | ALIGNE | Le choix historique est cohérent avec la confidentialité-first. | Garder ce point comme garde-fou documentaire. |
| Liste canonique des artefacts exportables par rôle | La cible 2.0 indique exports, traces, preuves, évaluations partageables, mais sans matrice finale complète. | Le corpus répartit l’information entre spec canonique, cadrage POC, glossaire et documents d’écarts. | ABSENT / NOUVEAU_CONTRAT | Il manque encore un contrat documentaire synthétique et propre qui distingue export technique, export métier, preuve, bundle, artefact partageable et artefact validable. | Produire ce contrat dans `02_decisions_documentaires.md`. |
| Place canonique du terme “Qualiopi lite” dans Hugo 2.0 | La cible 2.0 couvre les exports et preuves, mais ne verrouille pas encore complètement ce label dans sa taxonomie canonique. | Le terme est très présent dans le cadrage POC et les anciens endpoints métier. | AMBIGU | Le terme est utile et réel, mais son statut exact dans la doc 2.0 reste à clarifier. | Le conserver comme terme métier opérant pour ce domaine, avec mention explicite de son origine POC et de sa portée bornée. |
| Hugo cœur vs Hugo & Cie sur ce domaine | La cible 2.0 demande de rester sur Hugo cœur. | Le cadrage POC export/preuves/Qualiopi lite est porté par Hugo lui-même, sans dépendance fonctionnelle nécessaire à Hugo & Cie. | ALIGNE | Le domaine relève bien du noyau Hugo cœur. | Le rappeler explicitement dans les docs ultérieurs pour éviter les glissements de périmètre. |
Artefacts analytiques LLM par tour (ConversationTurnLLMAnalysis / ConversationLLMAnalysis) La cible 2.0 prévoit une couche analytique optionnelle, produite par le LLM à partir du verbatim brut de chaque tour et agrégée par conversation, destinée uniquement à des usages de debug, de démarche qualité ou de recherche, hors UX métier. Le rel mobilisé ici ne montre pas encore d’objets ou d’exports formalisés correspondant à cette couche analytique ; seuls les exports techniques de debug et certains logs internes sont décrits. ABSENT NOUVEAUCONTRAT Il s’agit d’un nouveau type d’artefact, à documenter comme export technique réservé superadmin, distinct des exports métier, des preuves et des bundles. Créer un sous-contrat d’export technique pour ces objets, et interdire explicitement leur exposition dans les surfaces apprenant, tuteur, formateur ou ORGADMIN.

---

## 3. Lecture consolidée

### 3.1 Alignements solides

Les alignements les plus solides sur ce domaine sont :
- existence d’exports structurés ;
- existence d’objets réels `Trace` et `Evidence` ;
- rattachement gouverné des preuves à un contexte métier ;
- suppression EXIF par défaut et GPS en opt-in ;
- confidentialité-first et partage explicite appliqués aux preuves et exports ;
- présence historique réelle d’un bundle Qualiopi lite côté Hugo cœur.

### 3.2 Frictions principales

Les frictions les plus importantes à ce stade sont :
- la richesse réelle des traces locales qui alimente moins bien les exports que certaines docs ne le laissent penser ;
- la place exacte de `Qualiopi lite` dans la nomenclature canonique 2.0 ;
- le mapping encore flou entre `EvaluationTrace`, `LearnerEvaluationRecord`, traces de validation et objets exportables ;
- la difficulté à écrire proprement la chaîne complète session -> trace -> preuve -> partage -> export -> bundle sans sur-affirmer des maillons non démontrés.

### 3.3 Zones à vérifier

Restent `A_VERIFIER` :
- équivalence du runtime distant avec le local sur ce domaine ;
- composition exacte des bundles en environnement distant ;
- permissions fines par rôle sur génération / téléchargement / consultation ;
- preuve RLS effective en prod pour les flux d’exports et bundles ;
- niveau réel de robustesse de certains artefacts exportés hors périmètre local audité.

---

## 4. Conséquence documentaire immédiate

La suite logique sur ce domaine est :
1. garder la structure doctrinale 2.0 ;
2. injecter les noms réels observés (`Trace`, `Evidence`, `EvidenceBundleView`, endpoints d’exports) ;
3. ne pas survendre la richesse actuelle des traces ;
4. distinguer proprement :
   - export technique,
   - export métier,
   - preuve,
   - bundle d’audit,
   - objet partageable,
   - validation humaine finale ;
1. marquer explicitement tout ce qui dépend du runtime distant comme `A_VERIFIER`.

# 02_decisions_documentaires — 100_exports_preuves_qualiopi_lite

## Domaine

- `DOMAINE_CODE = 100_exports_preuves_qualiopi_lite`
- `DOMAINE_LABEL = exports, preuves et Qualiopi lite`

---

## 1. Objet du document

Ce document fixe les **décisions documentaires** à appliquer pour le domaine `100_exports_preuves_qualiopi_lite`.

Il ne tranche ni un backlog technique général, ni une refonte produit. Son rôle est de décider **comment écrire juste** ce domaine dans la documentation Hugo cœur, en distinguant strictement :
- ce qui relève de la **cible 2.0** ;
- ce qui est **observable dans le réel audité** ;
- ce qui provient d’un **cadrage POC historique utile** ;
- ce qui doit rester **A_VERIFIER** tant que le runtime distant ou certaines variantes ne sont pas démontrés.

---

## 2. Décisions de cadrage

### D1 — Garder le domaine dans Hugo cœur, sans le déporter vers Hugo & Cie

Le domaine **exports / preuves / Qualiopi lite** est documenté comme un domaine propre de **Hugo cœur**.

Il ne doit pas être réécrit comme une extension dépendante d’une constellation d’assistants, ni comme un sous-produit administratif externe. La documentation doit rappeler que Hugo cœur produit déjà des traces, preuves et exports gouvernés, dans un cadre confidentialité-first et multi-tenant strict.

### D2 — Conserver la doctrine 2.0 comme charpente, sans la prendre pour du livré

La documentation du domaine doit continuer à utiliser la doctrine 2.0 comme structure de lecture :
- exports structurés ;
- preuves rattachées à une session ou une trace ;
- partage explicite ;
- validation humaine finale ;
- multi-tenant strict.

En revanche, aucun passage ne doit laisser croire qu’une capacité est **livrée** du seul fait qu’elle figure dans la spec canonique 2.0. Les formulations doivent donc distinguer explicitement :
- **“la cible 2.0 fixe…”**
- **“le réel audité montre…”**
- **“le cadrage POC historique décrit…”**

### D3 — Ne pas écrire “Qualiopi lite” comme équivalent canonique universel d’exports

Le terme **Qualiopi lite** est conservé dans la documentation, mais comme **terme métier historique et opérant**, pas comme catégorie canonique unique englobant tout le domaine.

Décision d’écriture :
- utiliser **“bundle d’audit Qualiopi lite”** pour parler du paquet métier historique ;
- utiliser **“exports structurés”** pour la famille canonique plus large ;
- utiliser **“preuves”** pour les artefacts rattachés à une session ou une trace ;
- éviter d’écrire comme si tout export Hugo était un artefact Qualiopi.

---

## 3. Décisions de vocabulaire

### D4 — Introduire explicitement les noms réels `Trace` et `Evidence`

À partir de maintenant, la documentation de domaine doit faire apparaître les noms réels observés :
- `Trace`
- `Evidence`

Ces noms doivent être présentés comme les **objets réels observés** correspondant aux notions doctrinales de trace et preuve. La doc ne doit pas rester au seul niveau d’un vocabulaire conceptuel abstrait quand les objets réels sont déjà connus.

### D5 — Introduire `EvidenceBundleView` dans les annexes de vocabulaire, pas comme preuve suffisante d’un contrat complet

Le nom réel `EvidenceBundleView` doit apparaître dans les annexes de vocabulaire ou dans un bloc “noms réels observés”.

En revanche, il ne doit pas être utilisé pour prétendre qu’un **contrat complet, stabilisé et exhaustif** du bundle d’audit est déjà démontré. On l’emploie comme **pont de vocabulaire** utile, pas comme preuve d’alignement complet de bout en bout.

### D6 — Maintenir `EvaluationTrace` comme nom doctrinal, sans masquer la friction avec `LearnerEvaluationRecord`

La doc 2.0 peut conserver `EvaluationTrace` comme nom doctrinal cible.

Mais toute zone qui touche aux exports, validations terminales ou objets d’évaluation doit désormais contenir une mention explicite de friction de vocabulaire :
- `EvaluationTrace` côté doctrine ;
- `LearnerEvaluationRecord` et objets de trace / validation côté réel.

Décision : tant que ce mapping n’est pas stabilisé, la documentation doit **montrer la friction**, pas la lisser artificiellement.

---

## 4. Décisions de structure documentaire

### D7 — Séparer systématiquement cinq sous-blocs dans les documents du domaine

Tous les documents futurs sur ce domaine devront suivre la séparation suivante :

1. **Invariants 2.0**
2. **Objets réels observés**
3. **Contrats / endpoints historiques utiles**
4. **Limites et écarts confirmés**
5. **Zones A_VERIFIER**

Cette structure est obligatoire pour éviter les glissements entre cible, réel et archive POC.

### D8 — Créer une distinction stable entre cinq catégories d’artefacts

La documentation doit désormais distinguer explicitement :
- **export technique**
- **export métier**
- **preuve**
- **bundle d’audit**
- **artefact partageable / validable**

Cette décision répond à un flou documentaire actuel : plusieurs textes parlent indistinctement d’exports, de preuves, de bundles, de validations ou de traces terminales, alors que ces objets n’ont pas la même fonction ni le même niveau de gouvernance.

### D9 — Documenter les endpoints historiques dans un sous-bloc “réel / POC observé”, pas dans la matrice canonique centrale

Les endpoints historiques utiles du domaine doivent être regroupés dans un sous-bloc spécifique, par exemple :
- `POST exports/run`
- `GET exports/download/{runid}`
- `POST quality/qualiopi/evidence-bundle`

Ils ne doivent pas être injectés directement dans la matrice canonique 2.0 comme s’ils constituaient déjà le contrat final universel. Cela permet de garder la doctrine propre tout en préservant les ancrages observés.

D9bis Distinguer explicitement les artefacts analytiques LLM des autres exports

La documentation doit introduire une catégorie explicite d’“export analytique LLM” (par exemple basée sur les objets ConversationTurnLLMAnalysis et ConversationLLMAnalysis), réservée aux usages de debug, de démarche qualité ou de recherche, et distincte :
- des exports techniques historiques (payloads de trace, logs filtrés) ;
- des exports métier structurés (CSV, JSON) ;
- des objets de preuve (Evidence) et des bundles d’audit (dont Qualiopi lite).

Décision d’écriture :
1. Toute mention de ces artefacts analytiques doit les rattacher à la superadministration technique, via les exports de debug, et non aux surfaces métier.
2. Ils ne doivent jamais être décrits comme des preuves ou des artefacts d’audit directement montrables ; ils restent des observables techniques gouvernés, pouvant contenir du verbatim et des analyses, hors UX apprenant, tuteur, formateur et ORGADMIN.
3. Leur existence ne change pas l’invariant “verbatim non partagé invisible produit” : ils restent confinés dans des exports techniques explicitement marqués comme non montrables produit.

---

## 5. Décisions sur le contenu métier

### D10 — Conserver l’invariant “preuve jamais orpheline”

La documentation de domaine doit acter comme invariant métier stable :
- une preuve doit rester rattachée à une session ou une trace ;
- une preuve ne flotte jamais librement hors gouvernance métier.

Cet invariant est cohérent avec la cible 2.0 et avec le cadrage POC historique. Il doit donc être écrit comme **règle ferme du domaine**, même si certains détails d’API peuvent encore évoluer.

### D11 — Conserver EXIF supprimés par défaut et GPS en opt-in comme invariants transverses

Les règles suivantes deviennent des invariants documentaires stables du domaine :
- suppression EXIF par défaut ;
- GPS uniquement en opt-in ;
- métadonnées sensibles gouvernées ;
- pas d’ouverture implicite des preuves aux autres rôles.

Ces points sont suffisamment cohérents entre doctrine de confidentialité et cadrage POC pour être conservés sans ambiguïté.

### D12 — Écrire clairement que les exports et bundles sont des artefacts d’audit, pas des actes de certification

La documentation doit interdire toute formulation laissant penser que :
- Hugo certifie seul ;
- le bundle Qualiopi lite vaut certification ;
- l’export vaut validation finale autonome.

Le bon cadrage documentaire est :
- Hugo prépare des **artefacts auditables** ;
- certaines validations humaines peuvent s’appuyer dessus ;
- la validation finale reste humaine ;
- le domaine soutient un audit ou une exploitation métier, sans se substituer à une décision humaine finale.

---

## 6. Décisions sur confidentialité et rôles

### D13 — Réécrire toute la partie visibilité à partir du partage explicite, pas de l’export

La documentation du domaine doit partir du principe de **partage explicite**, puis décrire ensuite ce qui peut être exporté.

Ordre documentaire décidé :
1. verbatim privé par défaut ;
2. partage distinct synthèse / preuves / verbatim ;
3. droits filtrés par rôle ;
4. seulement ensuite, exports et bundles.

Cela évite une dérive classique où l’artefact export devient implicitement plus visible que les données sources dont il procède.

### D14 — Documenter l’ORGADMIN comme rôle à capacité d’export bornée, pas comme rôle d’accès libre au contenu

La documentation doit conserver que l’ORGADMIN peut disposer de capacités d’administration et d’exports métier.

Mais elle doit écrire explicitement que cela n’implique **jamais** un accès libre au contenu apprenant non partagé. Les exports et bundles doivent être décrits comme des sorties **filtrées, gouvernées et contraintes**, pas comme une lecture brute du contenu applicatif.

### D15 — Maintenir le multi-tenant comme invariant produit, tout en séparant preuve locale et preuve runtime distant

Le domaine doit documenter le multi-tenant strict comme invariant produit non négociable.

Mais la preuve de son application effective doit être écrite sur deux plans distincts :
- **ancrages locaux forts** : `organisationId`, RLS, pattern `SET LOCAL`, tests cross-tenant dans les textes POC ;
- **preuve runtime distant** : `A_VERIFIER` tant que les variantes Encoors / prod ne sont pas auditées à ce niveau.

---

## 7. Décisions sur les limites à expliciter

### D16 — Ne plus survendre la richesse réelle des traces qui alimentent les exports

La documentation de domaine doit désormais intégrer explicitement le fait qu’il existe un **écart entre certains contrats documentaires riches et la pauvreté observée de certains payloads locaux**, notamment autour de `generate-trace`.

Conséquence rédactionnelle :
- on peut documenter la responsabilité “produire une trace exportable” ;
- on ne doit pas faire croire que tous les intrants réels sont déjà riches, stables et complets.

### D17 — Distinguer “capacité nominale du bundle” et “richesse réellement démontrée bout en bout”

Décision de rédaction obligatoire :
- **capacité nominale** : le domaine comporte historiquement un bundle d’audit Qualiopi lite ;
- **richesse bout en bout démontrée** : partiellement établie, pas entièrement prouvée par le corpus local disponible.

Cette distinction évite à la fois la sous-lecture et la sur-affirmation.

### D18 — Marquer explicitement toute dépendance au runtime distant comme `A_VERIFIER`

Dès qu’un passage parle de :
- composition exacte du bundle en prod ;
- permissions effectives par rôle sur Encoors ;
- équivalence local / distant ;
- preuves RLS runtime prod ;
- richesse réelle des artefacts générés en environnement distant,

la doc doit ajouter un marquage explicite `A_VERIFIER`.

---

## 8. Décisions d’écriture pour les futures specs

### D19 — Ajouter une colonne “nom réel observé” dans les futures matrices de ce domaine

Pour ce domaine, les futures matrices ou tableaux de spec doivent ajouter une colonne :
- **nom doctrinal 2.0**
- **nom réel observé**
- **niveau de preuve / statut**

Cela est cohérent avec la méthode du glossaire d’alignement et évite de réouvrir les mêmes ambiguïtés à chaque passe.

### D20 — Ne pas rebaptiser la doctrine à partir des noms d’API ou des vues

Même si certains noms réels sont utiles, la doctrine 2.0 ne doit pas être rebaptisée à partir :
- d’un endpoint historique ;
- d’une vue backend ;
- d’un nom de payload technique ;
- d’un libellé de ZIP POC.

Décision : on **ajoute** les noms réels dans la documentation, mais on ne remplace pas la structure doctrinale par le vocabulaire d’implémentation.

### D21 — Réserver les détails de format bas niveau aux annexes techniques

Les détails comme :
- séparateur CSV ;
- UTF-8 BOM ;
- `traceRichV1` ;
- structure pivot “1 ligne trace / item compétence” ;
- paramètres d’appel du bundle,

doivent être documentés en **annexe technique** ou dans une section “contrats observés / historiques”, pas dans le noyau doctrinal du domaine.

### D22 Règles transverses pour les protocoles de test (domaine 100)

Les scénarios de test qui impliquent exports, preuves ou bundles,
y compris les bundles historiques dits « Qualiopi lite », doivent
appliquer les règles suivantes :

1. En-tête « Niveau de preuve ciblé »

- Utiliser le gabarit d’en-tête décrit dans `plan_documentation_cto_convergence_hugo.md`
  pour distinguer :
  - la responsabilité cible 2.0 ;
  - ce qui est réellement observable dans le runtime local audité ;
  - ce qui dépend du runtime distant, de la production ou de flags
    non audités (à marquer AVERIFIER).

2. Test des invariants de gouvernance des preuves

Tout protocole qui touche aux preuves doit vérifier :

- qu’aucune Evidence n’est orpheline (toute preuve est rattachée à une
  Trace ou une HugoSession) ;
- que les photos de preuve sont traitées avec suppression EXIF par défaut
  et GPS uniquement en opt-in, conformément aux invariants documentés ;
- que le partage explicite est respecté (séparation synthèse / preuves /
  verbatim), en cohérence avec le domaine 90.

3. Oracle exports / preuves : capacité nominale vs richesse effective

L’oracle du test doit toujours distinguer :

- la capacité nominale :
  - un export ou un bundle est produit ;
  - la structure minimale attendue est présente ;
- la richesse effective :
  - documentée et vérifiée ;
  - partielle ;
  - non vérifiable dans ce protocole (→ marquer la dimension comme AVERIFIER).

Les tests ne doivent pas affirmer une « richesse complète » des exports
ou bundles là où le rel audit montre des traces ou artefacts encore
minimaux.

4. Marquage AVERIFIER sur la prod et les variantes distantes

Toute affirmation de test concernant :

- la composition exacte des bundles en environnement distant ;
- les permissions fines par rôle sur génération, consultation ou téléchargement ;
- l’équivalence entre runtime local et distant sur ce domaine ;

doit être marquée AVERIFIER tant qu’aucun audit spécifique n’a prouvé
ces comportements sur l’environnement cible.
---

## 9. Formulation canonique retenue pour ce domaine

La formulation de référence à utiliser désormais est la suivante :

> Hugo cœur doit pouvoir produire des exports structurés et des preuves rattachées à une session ou une trace, sous contraintes de confidentialité, de partage explicite et de multi-tenant strict.  
> Le domaine comprend aussi un héritage métier de bundle d’audit Qualiopi lite utile pour l’exploitation et l’audit, sans que cela vaille preuve d’une certification autonome ni équivalence automatique entre cible 2.0, runtime local et runtime distant.  
> Les noms réels observés `Trace`, `Evidence` et, lorsqu’il est pertinent, `EvidenceBundleView`, doivent être visibles dans la documentation de domaine comme ponts de vocabulaire vers le code.

---

## 10. Résultat attendu sur les prochains documents

À partir de ces décisions, les prochains documents du domaine devront :
- mieux raccorder vocabulaire doctrinal et noms réels ;
- réduire les ambiguïtés autour de `Qualiopi lite` ;
- rendre visibles les invariants de confidentialité et de validation humaine ;
- séparer le contrat canonique des détails POC historiques ;
- signaler clairement les zones `A_VERIFIER` liées au runtime distant ou à la richesse effective des artefacts.

# 03_backlog_actions — 100_exports_preuves_qualiopi_lite

## Domaine

- `DOMAINE_CODE = 100_exports_preuves_qualiopi_lite`
- `DOMAINE_LABEL = exports, preuves et Qualiopi lite`

---

## 1. Objet du backlog

Ce backlog liste les actions à mener sur le seul domaine **exports / preuves / Qualiopi lite** de Hugo cœur.

Il ne constitue ni un plan de refonte globale du moteur, ni un backlog infra transverse, ni une feuille de route Hugo & Cie. Il suit la ligne suivante :
- d’abord **recaler la documentation et les contrats** ;
- ensuite **borner les zones ambiguës** ;
- puis seulement **ouvrir des actions techniques additives** là où le réel ne couvre pas encore suffisamment la responsabilité métier.

---

## 2. Priorisation retenue

### P0 — À traiter immédiatement

Actions nécessaires pour éviter de continuer à documenter faux ou ambigu.

### P1 — À traiter ensuite

Actions importantes pour stabiliser le domaine, mais non bloquantes pour le recalage documentaire immédiat.

### P2 — À cadrer après vérification

Actions utiles mais dépendantes d’un audit complémentaire, d’un arbitrage produit ou d’une confirmation runtime.

---

## 3. Backlog priorisé

| ID | Priorité | Action | Type | Objectif | Livrable attendu | Dépendances / garde-fous |
|---|---|---|---|---|---|---|
| EXP-001 | P0 | Réécrire la fiche de domaine “exports / preuves / Qualiopi lite” avec la séparation cible / réel / POC / A_VERIFIER | Documentation | Éliminer les confusions actuelles entre spec 2.0, héritage POC et réel audité | Une fiche de domaine propre intégrée au corpus de travail | Ne jamais écrire le runtime distant comme prouvé sans audit complémentaire |
| EXP-002 | P0 | Ajouter un bloc de vocabulaire réel observé : `Trace`, `Evidence`, `EvidenceBundleView`, `LearnerEvaluationRecord` | Documentation | Réduire les collisions entre doctrine 2.0 et noms réellement observés | Sous-bloc “noms réels observés” réutilisable dans les specs | Le glossaire reste un pont de vocabulaire, pas une preuve autonome |
| EXP-003 | P0 | Documenter explicitement les cinq catégories d’artefacts : export technique, export métier, preuve, bundle d’audit, artefact partageable / validable | Documentation | Sortir du flou actuel où plusieurs objets différents sont décrits comme s’ils étaient équivalents | Tableau canonique de typologie des artefacts du domaine | Ne pas confondre validation humaine, partage et export |
| EXP-004 | P0 | Ajouter un encadré “ce que le domaine ne prouve pas” | Documentation | Éviter toute sur-affirmation sur Qualiopi, certification, richesse réelle des traces ou équivalence local / distant | Encadré de garde-fous réutilisable dans les documents du domaine | Doit mentionner explicitement runtime distant `A_VERIFIER` |
| EXP-005 | P0 | Inscrire comme invariants fermes : preuve non orpheline, EXIF supprimés par défaut, GPS opt-in, partage explicite, multi-tenant strict | Documentation | Stabiliser le socle non ambigu du domaine | Bloc d’invariants documentaires de référence | S’appuyer sur cible 2.0 et cadrage POC, sans extrapoler plus loin |
| EXP-006 | P0 | Reclasser `Qualiopi lite` comme bundle métier historique et non comme catégorie canonique unique | Documentation | Éviter que toute la famille export/preuve soit absorbée par un seul terme historique | Vocabulaire documentaire harmonisé | Conserver le terme, mais borner sa portée |
| EXP-007 | P1 | Produire un tableau de mapping entre `EvaluationTrace` cible et objets réels `LearnerEvaluationRecord` / `Trace` / validation partagée | Documentation / analyse | Traiter la principale friction de vocabulaire du domaine | Tableau de mapping avec statuts `ALIGNE_DOC_PARTIEL`, `AMBIGU`, `A_VERIFIER` | Ne pas lisser artificiellement le mapping si la preuve manque |
| EXP-008 | P1 | Documenter proprement les endpoints historiques utiles du domaine (`exports/run`, `exports/download`, `quality/qualiopi/evidence-bundle`) | Documentation | Préserver les ancrages observés sans polluer le noyau doctrinal 2.0 | Annexe “contrats observés / historiques” | À écrire comme contrats observés ou POC, pas comme API canonique finale |
| EXP-009 | P1 | Ajouter une matrice par rôle sur visibilité, partage et exportabilité | Documentation produit | Clarifier ce qu’un LEARNER, TUTOR, TRAINER, COORDO, ORGADMIN peut voir ou déclencher | Tableau par rôle, borné au domaine | Ne jamais attribuer d’accès libre au contenu non partagé |
| EXP-010 | P1 | Recaler la documentation sur le fait que l’accès à l’audit log passe par sorties filtrées et non par lecture API brute | Documentation | Clarifier le rôle exact de l’audit log dans les bundles et exports | Paragraphe ou annexe dédiée “traçabilité filtrée” | Rappeler l’absence d’endpoint direct d’audit log dans le cadrage POC |
| EXP-011 | P1 | Ouvrir une vérification ciblée de la richesse réelle de `generate-trace` pour ce domaine | Audit code / contrat | Mesurer l’écart entre traces attendues pour exports et payloads réellement générés localement | Note courte “niveau réel de richesse des traces pour export” | Action bornée au domaine, sans dériver vers audit moteur général |
| EXP-012 | P1 | Définir un contrat documentaire minimal de “trace exportable enrichie” | Contrat fonctionnel | Poser un niveau minimal d’intrants nécessaire pour produire des exports et bundles crédibles | Mini-spec de contrat additif | Ne pas lancer directement une refonte code sans ce contrat |
| EXP-013 | P1 | Ajouter une colonne “nom réel observé” dans les futures matrices du domaine | Documentation | Réduire les ambiguïtés récurrentes entre vocabulaire canonique et code | Modèle de tableau réutilisable | Cohérent avec la méthode du glossaire |
| EXP-014 | P2 | Vérifier l’équivalence local / Encoors sur exports, bundles et permissions par rôle | Audit runtime | Savoir ce qui peut être affirmé sur le runtime distant | Note `A_VERIFIER` levée ou confirmée | Ne pas inférer la prod à partir du local |
| EXP-015 | P2 | Vérifier l’effectivité RLS Postgres sur le flux export / bundle en environnement réel | Audit infra / runtime | Confirmer que l’invariant multi-tenant du domaine est effectivement tenu au runtime visé | Résultat de vérification borné au domaine | Le corpus actuel ne suffit pas pour conclure |
| EXP-016 | P2 | Vérifier la composition réelle du bundle Qualiopi lite produit aujourd’hui | Audit fonctionnel | Passer d’une capacité nominale décrite à une preuve fonctionnelle observée | Capture de contrat réel / exemple anonymisé / note d’écart | À faire seulement sur environnement autorisé et auditable |
| EXP-017 | P2 | Évaluer la nécessité d’un enrichissement additif des traces ou preuves pour mieux couvrir le bundle | Cadrage technique | Préparer une éventuelle évolution technique bornée si le domaine reste trop pauvre | Option de lot additif, non engagée | À ouvrir seulement après EXP-011 et EXP-016 |
| EXP-018 | P2 | Préparer un prompt Cursor ciblé “audit export / preuve / bundle” | Outillage CTO | Permettre une passe code/doc plus rapide et plus sûre sur ce domaine | Prompt Cursor structuré | À rédiger après stabilisation du vocabulaire et des contrats |
| EXP-019 | P2 | Préparer un prompt Cursor ciblé “contrat trace exportable enrichie” | Outillage CTO | Encadrer un chantier additif éventuel côté backend | Prompt Cursor borné au domaine | Ne pas ouvrir tant que le besoin n’est pas confirmé |
| EXP-020 | P2 | Préparer un exemple d’artefact de bundle anonymisé pour documentation interne | Documentation / preuve | Disposer d’un exemple concret pour les futures docs internes ou audits | Exemple commenté anonymisé | Uniquement si un environnement autorisé permet de le produire proprement |

---

## 4. Séquence recommandée

### Étape 1 — Recalage documentaire immédiat

À lancer en premier :
- `EXP-001`
- `EXP-002`
- `EXP-003`
- `EXP-004`
- `EXP-005`
- `EXP-006`

Cette étape suffit à supprimer l’essentiel des ambiguïtés documentaires sans toucher au code.

### Étape 2 — Stabilisation des contrats et du vocabulaire

À lancer ensuite :
- `EXP-007`
- `EXP-008`
- `EXP-009`
- `EXP-010`
- `EXP-013`

Cette étape prépare une base documentaire propre pour des travaux CTO ou Cursor plus ciblés.

### Étape 3 — Vérification du réel et éventuels compléments additifs

À lancer seulement après les deux premières étapes :
- `EXP-011`
- `EXP-012`
- `EXP-014`
- `EXP-015`
- `EXP-016`
- `EXP-017`
- `EXP-018`
- `EXP-019`
- `EXP-020`

Cette étape sert à transformer les zones `A_VERIFIER` en constats propres, puis à décider s’il faut ou non une évolution backend additive.

---

## 5. Actions à ne pas engager tout de suite

Les actions suivantes ne doivent **pas** être engagées en première intention sur ce domaine :

- refonte globale du pipeline trace / évaluation ;
- réécriture généralisée des endpoints d’exports ;
- redesign produit complet des écrans admin / qualité ;
- migration doctrinale entière autour de Qualiopi ;
- conclusions sur la prod distante sans audit complémentaire ;
- changement de taxonomie 2.0 pour coller brutalement aux noms d’implémentation.

Le domaine demande d’abord un **raccord documentaire propre**, pas une réarchitecture.

---

## 6. Point d’arrêt de décision

Le backlog de domaine peut être considéré comme suffisamment sécurisé pour passage éventuel en chantier CTO quand les conditions suivantes sont réunies :

- le vocabulaire doctrinal / réel est stabilisé sur `Trace`, `Evidence`, `EvidenceBundleView`, `LearnerEvaluationRecord` ;
- la distinction entre export, preuve, bundle et validation humaine est écrite sans ambiguïté ;
- la portée exacte de `Qualiopi lite` est bornée ;
- la pauvreté éventuelle des traces locales est documentée honnêtement ;
- les zones runtime distant restent soit vérifiées, soit explicitement marquées `A_VERIFIER`.

---

## 7. Lecture opérationnelle finale

La bonne lecture de ce backlog est la suivante :
- **P0** : remettre la documentation d’équerre ;
- **P1** : stabiliser les contrats du domaine ;
- **P2** : seulement ensuite, vérifier le runtime réel et préparer d’éventuels compléments techniques additifs.

Le domaine exports / preuves / Qualiopi lite n’appelle donc pas, à ce stade, une refonte générale de Hugo cœur. Il appelle surtout :
- un recalage documentaire strict ;
- une réduction du flou de vocabulaire ;
- un bornage honnête entre capacité nominale, réel démontré et runtime encore à vérifier.