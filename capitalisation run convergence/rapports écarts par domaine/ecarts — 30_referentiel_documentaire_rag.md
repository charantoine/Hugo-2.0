# 00_rapport_ecarts — 30_referentiel_documentaire_rag

## Domaine

- `DOMAINE_CODE = 30_referentiel_documentaire_rag`
- `DOMAINE_LABEL = référentiel documentaire RAG`

---

## 1. Objet du rapport

Ce rapport qualifie, pour le seul domaine **référentiel / documentaire / RAG** de Hugo cœur, l’écart entre :
- la **cible 2.0** décrite par la spec canonique, son complément et les specs de domaine ;
- le **réel observable** décrit par les audits du workspace Hugo réel ;
- le **pont de vocabulaire** fourni par le glossaire d’alignement.

Ce document ne décrit **ni Hugo & Cie**, ni un backlog général Hugo 2.0, ni une refonte globale du moteur. Il vise à établir une photo propre du domaine, à séparer ce qui est déjà couvert par le réel de ce qui relève encore d’un contrat cible, et à préparer les décisions documentaires et actions bornées qui suivront.

---

## 2. Règles de lecture et de vérité appliquées sur ce domaine

### 2.1 Réel, cible, glossaire

Pour parler du **réel**, la priorité est donnée aux audits du corpus Hugo réel, en particulier :
- `02_ETAT_MOTEUR_REEL.md` pour le pipeline backend, les services RAG, la bibliothèque documentaire, les modèles et endpoints observés ;
- `03_ETAT_PRODUIT_REEL.md` pour ce qui est effectivement consommé côté front montrable ;
- `09_PARCOURS_DEMO_ET_SCENARIOS.md` pour ce qui peut être montré en démo sans sur-vendre ;
- `01_CARTOGRAPHIE_WORKSPACE_REEL.md` et `05_ECARTS_DOC_CODE_PRODUIT.md` pour les ambiguïtés de structure et les écarts confirmés doc/code/produit.

Pour parler de la **cible**, on s’appuie sur :
- `spec_canonique_hugo_2_0.md` ;
- `complement_unique_specs_2_0`;
- `specs formateur + tuteur 2.0.md`.

Le **glossaire d’alignement** est utilisé uniquement comme **pont de vocabulaire** entre objets doctrinaux 2.0 et noms réellement observés dans Hugo développé. Il ne suffit jamais à lui seul pour prouver qu’un objet ou une responsabilité est effectivement implémenté.

### 2.2 Garde-fous de lecture

- La spec 2.0 décrit un **état cible** ; elle ne prouve jamais qu’une capacité est déjà livrée.
- La présence d’un modèle, d’un endpoint, d’un champ `pgvector`, d’un dossier `RAG` ou d’un code de support documentaire ne prouve pas à elle seule une capacité runtime complète.
- Toute dépendance à `hugoback.encoors.com`, à des flags runtime ou à une variante distante non auditée localement reste marquée `A_VERIFIER`.
- Le domaine est lu dans la doctrine Hugo 2.0 : backend Django orchestré, P0 conserv et enrichi additivement, TutorPrompt pivot runtime, récupération de contexte gouvernée côté serveur, front non pilote.

---

## 3. Périmètre cible 2.0 du domaine

Dans la cible Hugo 2.0, le domaine **référentiel / documentaire / RAG** ne constitue pas un moteur parallèle. Il s’insère dans la hiérarchie générale de récupération de contexte et reste subordonné au moteur tutoriel piloté par état.

### 3.1 Ce que la cible 2.0 fixe déjà

La doctrine 2.0 fixe les points suivants pour ce domaine :

- Le **référentiel métier** reste central pour orienter la couverture, la structuration des traces et les overlays de groupe. Il ne doit pas être remplacé par une logique documentaire pure.
- Le **RAG** reste **question-driven**, centré sur les documents actifs du contexte de formation, utilisé comme **renfort situé**, et non comme mémoire principale ni comme moteur de cours.
- La **base de connaissances formateur** doit produire des `TrainerKnowledgeItem` gouvernés, structurés et validables humainement, exploitables ensuite par les orchestrateurs apprenant.
- L’ordre doctrinal de récupération du contexte est explicite : **état structuré du tour**, puis **mémoire gouvernée**, puis **verbatim interne ciblé** si nécessaire, puis **overlay/référentiel**, puis **documentaire / RAG**.
- Les futurs prompts et le runtime doivent **consommer** des variables backend documentaires et référentielles gouvernées ; ils ne doivent pas redéfinir seuls la politique de vérité comportementale.

### 3.2 Ce que la cible 2.0 ne dit pas encore complètement

La cible 2.0 fixe fermement la place fonctionnelle du domaine, mais laisse encore ouvertes plusieurs précisions d’implémentation :
- le contrat exact entre référentiel, overlay, TrainerKnowledgeItem et RAG gouverné ;
- le workflow détaillé de l’orchestrateur formateur ;
- le niveau exact d’exposition produit de ces objets côté surfaces trainer/tuteur ;
- la granularité canonique des variables backend documentaires injectées dans les futurs prompts.

En conséquence, ce domaine doit être lu comme un **domaine à forte doctrine stabilisée**, mais avec des **contrats techniques encore partiellement à formaliser**.

---

## 4. Photo du réel observé

### 4.1 Référentiel et bibliothèque documentaire dans le réel audité

Le réel audité montre que Hugo cœur dispose bien d’un **socle référentiel et documentaire existant** :
- une app `referentials` pour groupes, référentiels et import ;
- une app `library` pour upload, indexation de documents et bibliothèque ;
- des endpoints et vues internes associées ;
- des parcours testeur/admin permettant d’importer des référentiels, gérer une bibliothèque de groupe et utiliser des documents côté calibration.

Le corpus audité montre aussi que des documents de démonstration existent dans les monorepos (`RAG Melec`, docs d’audit, corpus métier), mais ces jeux de données ne doivent pas être confondus avec une preuve de comportement runtime complet.

### 4.2 RAG runtime réellement observé

Dans le moteur audité, la zone RAG runtime est **implémentée mais limitée** :
- le service de support RAG existe (`ragsupport.py`) ;
- la sélection de chunks documentaires se fait dans le pipeline conversationnel ;
- l’indexation documentaire découpe le texte en chunks ;
- la capacité réellement observée est une **sélection lexicale / token-based** ;
- la recherche vectorielle n’est **pas** observée comme active dans `selectragchunks`, malgré la présence de `pgvector` dans la stack et de champs d’embedding dans les modèles.

Autrement dit, le réel montre un **RAG documentaire opérationnel au sens minimum**, mais pas le niveau de sophistication qu’une lecture rapide de l’infra pourrait laisser croire.

### 4.3 Place du documentaire dans le pipeline réel

Le pipeline moteur observé suit une séquence dans laquelle :
1. le contexte de session est construit ;
2. la posture est résolue ;
3. le tour est analysé ;
4. la décision conversationnelle est produite ;
5. un `teaching plan` et une phase sont décidés ;
6. les chunks RAG sont sélectionnés ;
7. la mémoire de session, la progression et le `ui-state` sont construits ;
8. le prompt final est rendu via `TutorPrompt`.

Cette séquence montre que le documentaire existe **comme couche backend du pipeline**, et non comme logique frontale. Elle confirme aussi que le RAG intervient **après** la décision locale et **dans un pipeline tutoriel déjà gouverné**, ce qui est doctrinalement cohérent avec Hugo 2.0.

### 4.4 Référentiel, produit montrable et surfaces observables

Côté produit montrable :
- le parcours apprenant prod ne frontalisent pas directement le référentiel ou le détail des objets documentaires ;
- le front prod consomme surtout `ui-state`, chat, synthèse, évaluation, traces et partage ;
- les surfaces documentaires et référentielles sont surtout visibles en **mode testeur / back-office** ;
- `09_PARCOURS_DEMO_ET_SCENARIOS.md` indique explicitement qu’il ne faut pas sur-vendre le RAG : la sélection observée reste lexicale, pas vectorielle.

Le réel observable confirme donc un domaine surtout **backend et back-office**, plus qu’une capacité apprenant directement exposée comme objet produit autonome.

### 4.5 Base de connaissances formateur dans le réel

Le moteur audité mentionne explicitement `TrainerKnowledgeItem`, ainsi que des vues trainer et des tests associés. Le réel montre donc une **présence nominale et structurelle** de la base de connaissances formateur, avec ingestion documentaire et explicitation côté trainer.

En revanche, le corpus d’audit utilisé ici ne prouve pas encore, à lui seul, que l’ensemble de la chaîne cible 2.0 soit stabilisée de bout en bout :
- profondeur réelle du workflow dialogique trainer ;
- articulation précise entre `TrainerKnowledgeItem`, overlay référentiel, chunks documentaires et RAG runtime ;
- niveau de validation humaine effectivement exercé dans les variantes distantes ;
- rôle exact de cette base dans tous les régimes conversationnels de Hugo cœur.

Ces points doivent rester distingués entre **présence réelle partielle**, **alignement documentaire**, et **contrat cible encore à formaliser**.

---

## 5. Analyse narrative des écarts

### 5.1 Zone de bon alignement

Le domaine est globalement **bien orienté doctrinalement** dans le réel audité.

Le réel confirme plusieurs responsabilités clés déjà compatibles avec Hugo 2.0 :
- le référentiel n’est pas absent du système ;
- la bibliothèque documentaire et l’indexation existent ;
- le RAG est bien traité côté backend ;
- le documentaire n’est pas le pilote principal de la conversation ;
- la base formateur existe au moins sous la forme d’objets et vues réelles (`TrainerKnowledgeItem`, vues trainer, ingestion documentaire).

Sur ce point, il ne faut donc **pas** relire la spec 2.0 comme un appel à “réinventer” tout le domaine. La responsabilité métier de base est déjà couverte : référentiel, documents, ingestion, appui documentaire et outillage trainer existent réellement.

### 5.2 Écart majeur : sophistication RAG surestimée par certaines docs

Le principal écart confirmé sur ce domaine porte sur le **niveau réel du RAG**.

La stack et certains éléments de doc ou d’infra peuvent laisser penser à un RAG vectoriel plus avancé. Or l’audit du moteur et le document d’écarts doc/code/produit convergent : la sélection runtime observée est **lexicale**, et l’indexation documentaire observée ne calcule pas d’embeddings exploitables dans le pipeline courant.

Cet écart n’impose pas une refonte doctrinale. Il impose surtout de :
- **désambiguïser** la documentation ;
- distinguer clairement **RAG documentaire lexical observé** et **RAG gouverné cible plus ambitieux** ;
- éviter de faire croire que `pgvector` ou un champ `embedding` démontrent une recherche vectorielle active.

### 5.3 Écart important : hiérarchie cible du contexte non encore complètement matérialisée

La cible 2.0 fixe une hiérarchie nette : état structuré, mémoire gouvernée, verbatim ciblé, overlay/référentiel, puis documentaire/RAG.

Le réel montre bien une couche documentaire subordonnée au pipeline tutoriel, ce qui est positif. En revanche, l’audit moteur montre aussi que :
- la mémoire thématique inter-session n’est pas encore réinjectée dans l’orchestrateur ;
- la hiérarchie complète de récupération du contexte n’est pas encore formalisée comme contrat documentaire unique ;
- le lien entre overlay référentiel, mémoire gouvernée et documentaire n’est pas encore stabilisé dans la documentation du réel.

Le point critique ici n’est donc pas “le RAG existe-t-il ?” mais plutôt : **la hiérarchie de contexte 2.0 est-elle déjà contractualisée et observable de bout en bout ?** À ce stade, la réponse est **non, pas encore complètement**.

### 5.4 Écart de vocabulaire : doctrine 2.0 vs noms réels observés

Le glossaire montre un bon potentiel d’alignement de vocabulaire, mais aussi plusieurs frictions utiles pour ce domaine :
- la doctrine parle de **référentiel / overlay / documentaire / RAG gouverné / TrainerKnowledgeItem** ;
- le réel parle plus concrètement de `referentials`, `library`, `ragsupport.py`, `indexdocument`, `TrainerKnowledgeItem`, vues trainer, groupes et documents.

Le glossaire confirme que ce domaine appelle surtout un travail de **raccord documentaire** :
- conserver les noms doctrinaux 2.0 pour raisonner juste ;
- faire apparaître les noms réels observés pour parler juste du code ;
- ne pas requalifier trop vite des concepts cibles comme objets entièrement stabilisés dans le réel.

### 5.5 Écart de formalisation : base formateur partiellement réelle, contrat 2.0 encore incomplet

La présence de `TrainerKnowledgeItem` et de vues trainer dans le réel est un point fort. Mais la cible 2.0 attend plus qu’une simple présence d’objet :
- un rôle clairement gouverné dans le système apprenant ;
- des statuts stabilisés ;
- une articulation nette avec le référentiel primaire ;
- une validation humaine explicite ;
- un RAG enrichi mais non souverain.

Le réel semble déjà couvrir une partie importante de cette responsabilité, mais le contrat 2.0 n’est pas encore totalement traduit en une documentation de chantier propre. L’écart à traiter est donc d’abord un **écart de formalisation et de bornage**, plus qu’un constat d’absence pure.

### 5.6 Produit et démo : prudence sur ce que le domaine “prouve”

Le domaine référentiel/documentaire/RAG est faiblement visible dans le parcours apprenant prod. La démo montre surtout :
- qu’un moteur conversationnel backend existe ;
- qu’il peut consommer un contrat `ui-state` ;
- qu’un outillage de référentiels et documents existe côté back-office/testeur.

Elle ne prouve pas à elle seule :
- la réalité d’un RAG vectoriel ;
- l’équivalence entre runtime local et runtime distant Encoors ;
- la complétude de la chaîne formateur -> TrainerKnowledgeItem -> RAG gouverné -> appui tutoriel apprenant ;
- la conformité intégrale de toutes les variantes runtime à la hiérarchie de contexte cible 2.0.

---

## 6. Lecture de synthèse par niveau de vérité

### 6.1 Implémenté / observable

Sur ce domaine, le réel audité permet d’affirmer comme **implémenté ou observable** :
- une couche `referentials` et import référentiel ;
- une couche `library` avec upload / indexation documentaire ;
- une sélection RAG backend réellement utilisée dans le pipeline ;
- une indexation documentaire par chunks ;
- des surfaces trainer / testeur liées au documentaire ;
- la présence réelle de `TrainerKnowledgeItem` et de vues trainer associées.

### 6.2 Cible 2.0

Relèvent de la **cible 2.0** :
- un ordre hiérarchique complètement explicite et stabilisé entre état structuré, mémoire gouvernée, verbatim ciblé, référentiel/overlay, puis RAG ;
- un RAG pleinement gouverné, documenté comme renfort situé ;
- une base de connaissances formateur doctrinalement intégrée, avec validation humaine et articulation fine avec le référentiel primaire ;
- une cartographie propre des variables backend documentaires et référentielles réutilisables par les futurs prompts.

### 6.3 Écarts confirmés

À ce stade, les **écarts confirmés** sur le domaine sont principalement :
- la documentation ou l’infra peuvent suggérer un RAG vectoriel avancé alors que le runtime observé est lexical ;
- la hiérarchie complète de récupération de contexte n’est pas encore documentée/probante de bout en bout dans le réel ;
- le contrat documentaire entre référentiel, overlay, TrainerKnowledgeItem et RAG n’est pas encore assez explicite ;
- le glossaire et les audits montrent un besoin clair de raccord de vocabulaire entre doctrine 2.0 et services réels observés.

### 6.4 À vérifier

Restent explicitement `A_VERIFIER` :
- l’équivalence entre le runtime local audité et `hugoback.encoors.com` sur ce domaine ;
- les flags ou variantes pouvant changer le comportement documentaire ou trainer en runtime distant ;
- la profondeur réelle de la validation humaine opérée dans les variantes non auditées ici ;
- toute affirmation forte sur un usage vectoriel actif en production distante ;
- toute conclusion sur une orchestration trainer 2.0 “complète” tant que les variantes runtime distantes ne sont pas inspectées.

---

## 7. Garde-fous pour la suite documentaire et technique

### 7.1 Ce qu’il ne faut pas faire

Pour ce domaine, il faut éviter quatre dérives :
1. relire la spec 2.0 comme si elle prouvait déjà un RAG gouverné complet ;
2. relire la présence de `pgvector`, de champs d’embedding ou d’objets trainer comme preuve d’un pipeline vectoriel ou trainer complet en runtime ;
3. recentrer la solution sur le documentaire ou sur les prompts au lieu de conserver le primat du moteur piloté par état ;
4. déclencher une refonte globale alors que le réel couvre déjà une partie substantielle de la responsabilité métier.

### 7.2 Ce qu’il faut privilégier

La bonne trajectoire pour ce domaine est plutôt :
- clarifier les **contrats** ;
- aligner le **vocabulaire** doctrine / code ;
- expliciter la différence entre **référentiel primaire**, **overlay**, **TrainerKnowledgeItem** et **RAG documentaire** ;
- documenter honnêtement le **niveau réel** du RAG observé ;
- préparer des compléments backend **additifs** plutôt qu’une architecture parallèle.

---

## 8. Conclusion opérationnelle du domaine

Le domaine `30_referentiel_documentaire_rag` n’est ni absent, ni proprement aligné de bout en bout.

Le réel audité montre un socle déjà présent et utile : référentiel, bibliothèque documentaire, ingestion, sélection RAG backend, base trainer nominale. La cible 2.0 n’appelle donc pas une réinvention du domaine, mais un **raccord méthodique** entre doctrine et réel : clarification des responsabilités, désambiguïsation du niveau réel du RAG, formalisation du contrat entre référentiel / documentaire / base trainer, et marquage explicite des zones encore `A_VERIFIER`.

Ce domaine est donc à lire comme :
- **socle réel existant** ;
- **alignement doctrinal globalement bon** ;
- **écarts surtout de sophistication, de formalisation et de vocabulaire** ;
- **pas de preuve suffisante, à ce stade, d’un RAG vectoriel gouverné complet ni d’une chaîne trainer 2.0 totalement stabilisée en runtime**.

# 01_matrice_ecarts — 30_referentiel_documentaire_rag

> Domaine : `30_referentiel_documentaire_rag` — référentiel, documentaire, RAG, base formateur

Colonnes :
- `ZONE_OBJET`
- `CIBLE_2_0`
- `REEL_OBSERVE`
- `STATUT`
- `NATURE_ECART`
- `RISQUE`
- `CORRECTION_RECOMMANDEE`
- `PRIORITE`

---

| ZONE_OBJET | CIBLE_2_0 | REEL_OBSERVE | STATUT | NATURE_ECART | RISQUE | CORRECTION_RECOMMANDEE | PRIORITE |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Référentiel métier (structure) | Référentiel métier central, structurant la couverture, les traces et les overlays de groupe ; non remplacé par le documentaire ou le RAG. | App `referentials` présente, import v2, référentiels JSON, structure de compétences, overlays de classe documentés dans les anciens docs POC ; utilisés dans les exports et dans certaines vues de suivi. | ALIGNE_DOC_PARTIEL | Aligner la doctrine 2.0 avec un référentiel déjà implémenté mais surtout documenté dans le corpus 1.x. | Faible | Mettre à jour la doc 2.0 pour citer explicitement `referentials` comme implémentation actuelle du référentiel métier, en rappelant que la doctrine 2.0 conserve le rôle central du référentiel. | M |
| Overlay de référentiel (par classe / groupe) | Overlays de référentiel par groupe pour contextualiser le référentiel global avec exemples, erreurs fréquentes, questions, liens documentaires. | Overlays de classe décrits dans les docs POC 1.5, et encore présents conceptuellement côté import et bibliothèques de groupe ; réalisations exactes peu détaillées dans les audits 02/03. | AMBIGU | Concept présent dans l’archive, mais niveau d’implémentation exact dans le code actuel insuffisamment documenté. | Moyen | Marquer `overlay` comme concept cible aligné mais `A_VERIFIER` sur le code actuel ; prévoir un audit ciblé de `referentials` et des overlays de groupe, puis ajuster la doc 2.0 avec les noms réels. | M |
| Bibliothèque documentaire de groupe | Bibliothèque documentaire gouvernée par groupe, alimentant un RAG question-driven ; documents tagués et rattachés au contexte de formation. | App `library` présente, upload et indexation de documents, découpe en chunks, bibliothèques par groupe ; corpus RAG Melec de démo ; tâches Celery d’indexation. | ALIGNE_DOC_PARTIEL | La bibliothèque existe et est utilisée, mais son rôle exact comme “RAG gouverné” n’est pas encore formalisé au niveau 2.0. | Faible | Documenter explicitement `library` et ses tâches (upload, indexdocument) dans la spec 2.0 comme implémentation actuelle de la bibliothèque documentaire de groupe. | M |
| RAG runtime — principe | RAG question-driven, centré sur les documents ACTIFS du contexte, utilisé comme renfort situé ; ne doit pas devenir mémoire principale ni moteur de cours. | Service RAG runtime présent (`ragsupport.py`), sélection de chunks appelée dans le pipeline ; RAG activé en mode testeur (RAG search), utilisé comme support documentaire, pas comme mémoire principale. | ALIGNE_DOC_PARTIEL | Le positionnement doctrinal du RAG comme renfort situé est cohérent, mais la doc historique surestime parfois son rôle. | Faible | Alignement documentaire : clarifier que le RAG actuel est un renfort documentaire, non une mémoire principale ; ajouter ce point dans la spec 2.0 et dans une note de garde-fou produit. | M |
| RAG runtime — niveau technique (vectoriel vs lexical) | Cible 2.0 compatible avec un RAG gouverné, potentiellement vectoriel, mais jamais au centre du pilotage ; la spec ne fige pas le moteur technique. | `pgvector` présent dans la stack et certains modèles, mais `selectragchunks` fonctionne en sélection lexicale ; pas de calcul d’embeddings exploités dans le pipeline ; écarts doc/code confirment “RAG vectoriel” comme non implémenté. | RENOMMER_DANS_DOC | Doc et discours peuvent laisser croire à un RAG vectoriel actif alors que le runtime est lexical. | Moyen | Mettre à jour doc et supports pour parler de “RAG lexical gouverné” dans l’état réel ; réserver “RAG vectoriel gouverné” comme capacité cible non livrée. | H |
| Hiérarchie de récupération de contexte | Ordre doctrinal explicite : état structuré apprenant, mémoire thématique gouvernée, verbatim interne ciblé, overlay/référentiel, documentaire/RAG ; documentaire en dernier ressort. | Pipeline réel : construction du contexte, décision locale, teaching plan, sélection RAG, session memory, progression, UiState ; LearnerThemeMemory consolidée post-conversation mais non réinjectée ; hiérarchie complète pas encore codée comme contrat structuré. | ALIGNE_DOC_PARTIEL | L’ordre “documentaire après le reste” est cohérent dans les faits, mais pas formalisé comme contrat. | Moyen | Formaliser cette hiérarchie dans la doc 2.0 en s’appuyant sur le complément 2.0, puis introduire progressivement un service backend dédié (ContextRetrieval) documentant explicitement l’ordre appliqué ; pas de refonte du pipeline si la responsabilité est déjà couverte. | M |
| Orchestration formateur — principe | Orchestrateur formateur distinct, dialogique, pour expliciter et structurer le savoir métier, produire des `TrainerKnowledgeItem` gouvernés, validés humainement. | Modèle `TrainerKnowledgeItem` présent, vues trainer et tests associés ; ingestion documentaire et explicitation formateur existent ; statuts documentés dans les specs 1.9/2.0, mais workflow complet non audité en runtime distant. | ALIGNE_DOC_PARTIEL | Le rôle de la base formateur est aligné, mais la chaîne complète F1–F4 du doc 2.0 n’est pas entièrement décrite comme implémentée. | Moyen | Stabiliser la doc 2.0 sur la base formateur en citant `TrainerKnowledgeItem` et les vues existantes comme implémentation partielle ; marquer explicitement ce qui reste cible (dialogue complet, UX, mapping détaillé vers RAG). | M |
| Orchestration formateur — statuts et validation humaine | Statuts `declared`, `derived_provisional`, `validated_trainer` ; aucun auto-upgrade ; validation humaine obligatoire ; base formateur subordonnée au référentiel métier primaire. | Statuts et objets présents dans les specs 1.9 et 2.0 ; code et tests confirment les statuts sur `TrainerKnowledgeItem` ; niveau de validation réelle dans toutes les variantes runtime non documenté dans cet audit. | AMBIGU | Alignement conceptuel fort, mais usage et enforcement runtime non complètement démontrés. | Moyen | Marquer dans la doc 2.0 que les statuts sont doctrinaux et partiellement implémentés ; planifier un audit ciblé des vues trainer (local et distant) pour confirmer les flux de validation et mettre à jour la doc si nécessaire. | M |
| Rôle du référentiel vs base formateur vs RAG | Référentiel métier : base primaire ; base formateur : savoir dérivé validé ; RAG : renfort situé ; aucun des trois ne doit devenir “vérité automatique” ou mémoire principale. | Référentiel et base formateur existent ; RAG documentaire opère déjà ; certains docs historiques tendent à mélanger ces responsabilités ou à sur-jouer le RAG. | RENOMMER_DANS_DOC | Sur-agrégation conceptuelle dans certains textes (RAG présenté comme pivot) ; risque de confusion côté équipe. | Moyen | Re-écrire la partie 18 de la canonique et le complément 2.0 en explicitant les trois couches, en citant les noms réels (`referentials`, `TrainerKnowledgeItem`, `library`/RAG), et en insistant sur la hiérarchie référentiel > base formateur > RAG. | H |
| Endpoint / surface — RAG debug | RAG accessible côté calibration / debug pour vérifier le comportement documentaire, pas comme surface produit apprenant. | Endpoint `internal/rag/search` présent, réservé calibration ; documented dans 02 et 09 comme mode testeur. | ALIGNE | Alignement fort : le RAG debug n’est pas exposé au front apprenant. | Faible | Documenter cette séparation dans specs interface 2.0 (surface testeur vs surface apprenant) ; ne pas bouger le code. | L |
| Endpoint / surface — exposition documentaire apprenant | L’ apprenant consomme les effets du RAG via le comportement de Hugo, pas un moteur de recherche documentaire libre. | Front prod ne propose pas de moteur de recherche documentaire autonome pour l’apprenant ; le RAG est utilisé en interne ; seul le chat et les objets visibles (traces, synthèses) apparaissent. | ALIGNE | Cible 2.0 respectée : pas de RAG libre côté apprenant. | Faible | Rappeler dans la spec interface 2.0 que la recherche documentaire apprenant reste pilotée par le moteur, pas par une UI libre. | L |
| Mappage vocabulaire doctrine 2.0 ↔ code (référentiel/RAG) | Termes canoniques : Référentiel, Overlay, RAG gouverné, TrainerKnowledgeItem, MemoryConsolidator, DocumentIngestor. | Termes réels : `referentials`, `library`, `ragsupport.py`, `indexdocument`, `TrainerKnowledgeItem`, vues trainer, `RAG Melec`. Glossaire partiellement renseigné. | RENOMMER_DANS_DOC | Mapping existant dans le glossaire, mais pas encore intégré dans les matrices backend/interface 2.0. 

# 02_decisions_documentaires — 30_referentiel_documentaire_rag

## Domaine

- `DOMAINE_CODE = 30_referentiel_documentaire_rag`
- `DOMAINE_LABEL = référentiel documentaire RAG`

---

## 1. Objet du document

Ce document fixe les **décisions documentaires** à appliquer au domaine `30_referentiel_documentaire_rag` après lecture croisée :
- de la cible 2.0 ;
- des audits du réel Hugo cœur ;
- du glossaire d’alignement ;
- et de la matrice d’écarts du domaine.

Il ne décide **ni une refonte code immédiate**, ni une extension Hugo & Cie, ni une réécriture générale de la doctrine. Son objet est de stabiliser la manière correcte de **documenter** ce domaine, sans sur-promesse, sans régression doctrinale, et sans confusion entre cible, réel et vocabulaire.

---

## 2. Principes de décision retenus

### 2.1 Doctrine de lecture maintenue

Pour ce domaine, la doctrine 2.0 reste inchangée :
- Hugo cœur reste un moteur tutoriel multi-postures piloté par état ;
- le backend Django orchestré reste la source de conduite ;
- TutorPrompt reste pivot runtime ;
- le documentaire et le RAG restent des **couches de contexte gouvernées**, non un pilote conversationnel autonome ;
- le référentiel métier reste prioritaire sur la base documentaire et sur le RAG.

### 2.2 Règle de vérité documentaire

Les décisions documentaires suivent la règle suivante :
- la **spec 2.0** continue de décrire la **cible** ;
- les **audits 00–10** décrivent le **réel observable** ;
- le **glossaire** sert à raccorder les noms, pas à prouver l’implémentation ;
- toute divergence entre discours et réel doit être corrigée en priorité côté doc avant d’ouvrir un chantier technique non nécessaire.

### 2.3 Règle de non-régression

Aucune décision documentaire de ce domaine ne doit :
- réintroduire une lecture “prompt-centered” ;
- faire glisser Hugo vers un moteur de cours piloté par le RAG ;
- transformer la base formateur en vérité automatique ;
- ni laisser croire qu’un composant documentaire devient la mémoire principale du système.

---

## 3. Décisions documentaires structurantes

### D1 — Conserver le triptyque canonique « référentiel / base formateur / RAG »

La documentation 2.0 conserve explicitement les trois couches suivantes :
1. **référentiel métier primaire** ;
2. **base de connaissances formateur gouvernée** ;
3. **documentaire / RAG comme renfort situé**.

Décision :
- ne pas fusionner ces trois couches dans un vocabulaire flou du type “base documentaire Hugo” ;
- réécrire les sections concernées pour rendre la hiérarchie lisible ;
- rappeler systématiquement que le RAG n’est ni la vérité primaire, ni la mémoire principale, ni le pilote de la conduite tutorale.

### D2 — Documenter le réel actuel comme « RAG lexical gouverné observé »

Dans la documentation du **réel** et dans toute note d’alignement, le RAG actuellement observé est décrit comme :
- un **RAG documentaire backend** ;
- **question-driven** ;
- à **sélection lexicale de chunks** ;
- intégré au pipeline moteur, mais non vectoriel démontré dans l’audit courant.

Décision :
- bannir, pour l’état réel, les formulations ambiguës laissant entendre un “RAG vectoriel actif” ;
- remplacer ces formulations par “RAG lexical observé” ou “sélection documentaire lexicale observée” ;
- réserver la notion de RAG vectoriel gouverné à un **état cible ou lot ultérieur**, tant qu’aucune preuve runtime supplémentaire n’existe.

### D3 — Ajouter les noms réels observés dans les docs 2.0 de référence

Le glossaire recommande d’ajouter, dans les specs 2.0, les **noms réels observés** lorsque le mapping est suffisamment net.

Décision :
- dans ce domaine, faire apparaître explicitement, à côté du nom doctrinal, les noms réels suivants lorsqu’ils sont pertinents :
  - `referentials` ;
  - `library` ;
  - `ragsupport.py` ;
  - `indexdocument` ou tâches d’indexation documentaire ;
  - `TrainerKnowledgeItem`.

Règle d’écriture :
- conserver le **nom canonique 2.0** comme nom de raisonnement ;
- ajouter juste après le **nom réel observé** comme point d’ancrage code ;
- ne pas rebaptiser toute la doctrine selon les noms Python du runtime.

### D4 — Formaliser la hiérarchie de récupération de contexte dans la doc 2.0

Le complément 2.0 fixe désormais une hiérarchie doctrinale explicite de récupération de contexte : état structuré, mémoire gouvernée, verbatim ciblé, overlay/référentiel, puis documentaire/RAG.

Décision :
- cette hiérarchie doit être intégrée explicitement dans la documentation du domaine ;
- le bloc “référentiel / documentaire / RAG” doit être réécrit pour montrer que le RAG arrive **après** les couches d’état et de mémoire gouvernée ;
- la documentation doit préciser que cette hiérarchie est un **invariant doctrinal**, même si sa formalisation technique complète reste encore progressive dans le réel.

### D5 — Maintenir `TrainerKnowledgeItem` comme point d’ancrage principal de la base formateur

La cible 2.0 et le réel convergent suffisamment sur `TrainerKnowledgeItem` pour en faire le point d’ancrage documentaire central de la base formateur.

Décision :
- dans ce domaine, la base formateur doit être documentée à partir de `TrainerKnowledgeItem` comme objet principal ;
- les docs doivent rappeler les statuts doctrinaux minimaux (`declared`, `derived_provisional`, `validated humanly` ou équivalent produit) ;
- les docs doivent aussi rappeler qu’aucun item dérivé ne peut être promu automatiquement vers un statut validé humainement.

### D6 — Ne pas figer dans la doc un workflow trainer plus précis que ce que le corpus soutient

La cible 2.0 fixe le rôle, le périmètre et les garde-fous de l’orchestrateur formateur, mais laisse encore ouverts le script fin, l’ordre exact des écrans et certaines règles de relance.

Décision :
- la doc de ce domaine doit décrire **ce qui est fixé** : ingestion documentaire, explicitation dialogique, production d’items structurés, validation humaine ;
- elle ne doit pas inventer un workflow écran par écran ou un script conversationnel prétendument stabilisé si le corpus ne le prouve pas ;
- les zones non stabilisées doivent rester marquées comme **à préciser** plutôt que comblées par reconstruction.

### D7 — Séparer clairement réel observable et cible 2.0 dans les passages sur le RAG

Le domaine contient un risque documentaire particulier : la cible 2.0 est cohérente et ambitieuse, tandis que le réel observé est déjà utile mais plus limité techniquement.

Décision :
- toute section importante de ce domaine doit comporter une séparation visible entre :
  - **cible 2.0** ;
  - **réel observable** ;
  - **zones à vérifier** ;
- il ne faut plus écrire de paragraphes mélangeant dans la même phrase la doctrine cible et une prétendue implémentation déjà livrée.

### D8 — Marquer explicitement les points `A_VERIFIER` dépendant du runtime distant

Les audits rappellent que les variantes distantes, flags et comportements Encoors ne peuvent pas être déduits automatiquement du code local ou de la démo.

Décision :
- tous les passages qui dépendent de `hugoback.encoors.com`, d’un comportement prod distant, d’un éventuel pipeline vectoriel actif ou d’une chaîne trainer complète non auditée doivent être marqués `A_VERIFIER` ;
- cette mention doit être explicite, sans langage insinuant que “c’est probablement déjà le cas”.

---

## 4. Décisions de mise à jour par document cible

### 4.1 `spec_canonique_hugo_2_0.md`

Décisions :
- réécrire ou compléter la partie **“Référentiel, documentaire et RAG”** pour faire apparaître plus nettement :
  - la hiérarchie référentiel > base formateur > RAG ;
  - la nature question-driven et située du RAG ;
  - la distinction entre doctrine cible et implémentation réellement auditée.

- ajouter, dans la matrice des services et objets, les **noms réels observés** utiles sur ce domaine :
  - `referentials`, `library`, `TrainerKnowledgeItem`, `ragsupport.py`, tâches d’indexation documentaire.

- ne pas présenter un moteur vectoriel comme déjà livré tant que ce n’est pas démontré dans les audits.

### 4.2 `complement_unique_specs_2_0`

Décisions :
- reprendre explicitement, dans la zone sur l’ordre de récupération de contexte, une formulation plus opérationnelle pour le domaine ;
- ajouter un sous-bloc de rappel disant que le **documentaire/RAG reste la couche de renfort finale**, après état, mémoire et référentiel ;
- ajouter un rappel que les futurs prompts consomment des variables documentaires gouvernées, sans que cela fasse du RAG une source souveraine de vérité comportementale.

### 4.3 `specs-formateur-tuteur-2.0.md`

Décisions :
- ancrer davantage la partie formateur sur le nom réel `TrainerKnowledgeItem` déjà convergent entre cible et réel ;
- expliciter que la base formateur produit des objets structurés pouvant enrichir le RAG gouverné, **sans se substituer au référentiel primaire** ;
- conserver les zones ouvertes sur le script dialogique fin au lieu de les “inventer” en doc stable.

### 4.4 Documents d’audit et de réalignement

Décisions :
- dans les documents décrivant le **réel**, employer une terminologie prudente :
  - “RAG lexical observé” ;
  - “sélection de chunks observée” ;
  - “présence de `pgvector` non suffisante pour conclure à une recherche vectorielle active”.

- créer ou compléter un sous-bloc d’alignement lexical pour le domaine avec :
  - nom doctrinal ;
  - nom réel observé ;
  - statut ;
  - action documentaire.

---

## 5. Décisions rédactionnelles concrètes

### 5.1 Vocabulaire à employer

Employer préférentiellement :
- **référentiel métier primaire** ;
- **base de connaissances formateur gouvernée** ;
- **RAG documentaire gouverné** ;
- **RAG lexical observé** quand on parle du réel audité ;
- **TrainerKnowledgeItem** comme objet d’ancrage côté base formateur.

Éviter ou corriger :
- “RAG vectoriel Hugo” pour l’état réel ;
- “base documentaire Hugo” si cela mélange référentiel, documents et base formateur ;
- “mémoire RAG” ;
- “le RAG pilote la posture ou la conduite” ;
- “la base formateur remplace le référentiel”.

### 5.2 Formulations à imposer

Formulations à imposer dans ce domaine :
- “Le RAG intervient comme renfort situé dans un pipeline tutoriel backend déjà gouverné.”
- “Le référentiel métier reste la couche primaire d’orientation.”
- “La base formateur enrichit le système sous validation humaine.”
- “Le niveau exact de sophistication technique du RAG observé doit être distingué de la cible 2.0.”

### 5.3 Formulations à bannir

Formulations à bannir :
- “Hugo dispose d’un RAG vectoriel opérationnel” tant que non prouvé ;
- “les documents constituent la mémoire de Hugo” ;
- “le trainer alimente automatiquement la vérité métier” ;
- “la spec 2.0 acte l’existant” ;
- toute phrase qui mélange en un seul plan ce qui est **cible**, **réel** et **supposé prod**.

---

## 6. Décisions de structuration documentaire

### 6.1 Structure recommandée pour ce domaine dans la base 2.0

Pour les prochains textes, ce domaine doit être structuré dans l’ordre suivant :
1. rôle du **référentiel métier** ;
2. rôle de la **base formateur gouvernée** ;
3. rôle du **documentaire/RAG** ;
4. ordre de récupération du contexte ;
5. noms réels observés dans Hugo développé ;
6. zones `A_VERIFIER` runtime, flags, distant.

### 6.2 Niveau de détail autorisé

Le bon niveau de détail est :
- suffisamment précis pour raccorder la doctrine aux objets réels ;
- suffisamment prudent pour ne pas transformer une présence code en preuve de comportement livré ;
- orienté responsabilités, pas description ORM ou infra exhaustive.

---

## 7. Décisions non retenues

Les décisions suivantes sont **explicitement non retenues** sur ce domaine :

- ne pas ouvrir un chantier de refonte complète du RAG sur seule base documentaire ;
- ne pas renommer brutalement la doctrine 2.0 selon les noms de modules Python ;
- ne pas fusionner référentiel, base formateur et documentaire dans une seule catégorie fourre-tout ;
- ne pas documenter Hugo cœur comme si la chaîne trainer 2.0 complète était déjà démontrée bout en bout ;
- ne pas inférer le runtime distant depuis le local.

---

## 8. Résultat attendu après application

Après application de ces décisions documentaires, le domaine `30_referentiel_documentaire_rag` doit être documenté comme suit :

- **doctrinalement clair** : référentiel d’abord, base formateur gouvernée ensuite, RAG en renfort situé ;
- **honnête sur le réel** : RAG backend existant, lexicalement observé, non sur-vendu ;
- **raccordé au code** : noms réels visibles quand ils sont connus ;
- **proprement borné** : workflow trainer détaillé, runtime distant et sophistication vectorielle restent séparés ou marqués `A_VERIFIER` ;
- **sans régression doctrinale** : pas de recentrage prompt, pas de mémoire documentaire dominante, pas de front pilotant la conduite.



# 03_backlog_actions — 30_referentiel_documentaire_rag — référentiel documentaire RAG

## 0. Statut du document

Backlog d’actions **ciblé sur ce domaine**, dérivé de `00_rapport_ecarts.md` et `01_matrice_ecarts.md`.[file:16]  
Ce n’est ni un plan CTO global, ni une spec en soi ; il liste des actions concrètes, réalisables, priorisées, à revalider par le CTO.[file:16]

---

## 1. Actions documentation / spec

Actions pour mettre en cohérence la doc avec le réel, sans toucher au code.

| ID | Type | Description courte | Source écart | Priorité | Responsable pressenti |
|----|------|--------------------|--------------|----------|-----------------------|
| D1 | DOC | Réécrire les passages du domaine qui laissent entendre un **RAG vectoriel déjà actif**, en documentant explicitement une sélection documentaire lexicale observée en runtime local. | Matrice : `ALIGNE_DOC_PARTIEL` / `RENOMMER_DANS_DOC` sur RAG runtime ; audit croisé RAG vectoriel non démontré | Haute | Doc / moteur |
| D2 | DOC | Ajouter dans la doc du domaine un bloc de hiérarchie explicite **référentiel primaire → base formateur gouvernée → documentaire/RAG en renfort situé**. | Matrice : `ALIGNE_DOC_PARTIEL` sur doctrine cible vs réel ; ordre de récupération du contexte | Haute | Doc / produit |
| D3 | DOC | Ajouter une colonne ou un sous-bloc **nom réel observé** pour les objets du domaine : `referentials`, `library`, `ragsupport.py`, indexation documentaire, `TrainerKnowledgeItem`. | Matrice : `RENOMMER_DANS_DOC` | Haute | Doc |
| D4 | DOC | Stabiliser dans la doc la frontière entre **présence réelle partielle** de la base formateur et **chaîne trainer 2.0 complète encore non prouvée**. | Matrice : `AMBIGU` sur usage bout-en-bout de `TrainerKnowledgeItem` | Haute | Doc / produit |
| D5 | DOC | Clarifier le rôle de `TrainerKnowledgeItem` comme objet gouverné, subordonné au référentiel primaire, avec validation humaine obligatoire avant statut validé. | Matrice : `ALIGNE_DOC_PARTIEL` | Haute | Doc / formateur |
| D6 | DOC | Documenter explicitement la différence entre **objet cible 2.0** et **preuve du réel** pour éviter de présenter comme livrés des objets ou flux encore conceptuels dans ce domaine. | Matrice : `A_VERIFIER` / `ABSENT / NOUVEAU_CONTRAT` | Moyenne | Doc |
| D7 | DOC | Ajouter dans les annexes de domaine les garde-fous de rédaction : ne pas déduire le réel depuis `pgvector`, un champ embedding ou un objet trainer nominal. | Matrice : `AMBIGU` / `A_VERIFIER` | Moyenne | Doc |

---

## 2. Actions backend / contrats

Compléments backend réellement 2.0 identifiés pour ce domaine (nouveaux endpoints, intégrations mémoire, enrichissement de sélecteurs…), en respectant les invariants (enrichissement additif, pas de refonte pipeline, pas de front-driven).[file:6][file:7]

| ID | Type | Description courte | Nature (FORMALISER / COMPLETER / NOUVEAU_CONTRAT) | Priorité | Commentaires / garde-fous |
|----|------|--------------------|---------------------------------------------------|----------|---------------------------|
| B1 | BACKEND | Formaliser un **mini-contrat backend** séparant clairement référentiel, base formateur, documentaire source et RAG runtime. | FORMALISER | Haute | Ne pas recréer une couche parallèle ; simple clarification des responsabilités backend.[file:6][file:7] |
| B2 | BACKEND | Définir un contrat minimal de **DocumentContextBundle** ou équivalent pour le rendu prompt : overlay référentiel pertinent, documents actifs, chunks retenus, provenance trainer autorisée. | NOUVEAU_CONTRAT | Haute | Additif, backend-first, sans faire du RAG la mémoire dominante.[file:7][file:6] |
| B3 | BACKEND | Formaliser la place de `TrainerKnowledgeItem` dans la chaîne apprenant : producteur, consommateurs, statut, conditions d’usage documentaire/RAG. | FORMALISER | Haute | Ne pas auto-promouvoir les items ; validation humaine conservée.[file:5][file:6] |
| B4 | BACKEND | Préparer une cartographie des **variables backend documentaires** destinées aux futurs prompts : overlay, chunks retenus, usage RAG, provenance trainer, statut de validation. | COMPLETER | Moyenne | Les prompts doivent consommer ces variables, pas redéfinir la vérité comportementale.[file:7] |
| B5 | BACKEND | Ajouter un contrat d’**observabilité technique minimale** du domaine : source documentaire utilisée, fallback sans documentaire, présence de chunks, présence d’items trainer. | COMPLETER | Moyenne | Journalisation backend non exposée au front ; confidentialité inchangée.[file:6][file:7] |
| B6 | BACKEND | Si la matrice confirme une absence de contrat stable, préparer un pseudo-contrat d’indexation documentaire distinguant chunking, métadonnées et éventuels embeddings non actifs. | NOUVEAU_CONTRAT | Moyenne | Documenter sans imposer une refonte du moteur d’indexation existant.[file:16] |

---

## 3. Actions d’audit / à vérifier

Ce qu’il faut explicitement vérifier (runtime distant, flags prod, branches non auditées), sans présumer du résultat.

| ID | Type | Question / vérification à mener | Source (A_VERIFIER / AMBIGU) | Priorité | Mode (audit code, trace, runtime) |
|----|------|----------------------------------|------------------------------|----------|------------------------------------|
| V1 | AUDIT | Vérifier si le runtime distant active un chemin documentaire différent du local, notamment une recherche vectorielle ou un usage d’embeddings absent de l’audit local. | `A_VERIFIER` | Haute | Audit runtime + comparaison local/distant |
| V2 | AUDIT | Vérifier la chaîne active d’indexation documentaire : chunking seul, embeddings calculés mais non exploités, ou autre variante effectivement branchée. | `A_VERIFIER` / `AMBIGU` | Haute | Audit code + trace d’indexation |
| V3 | AUDIT | Vérifier le niveau réel d’usage de `TrainerKnowledgeItem` côté apprenant : présence nominale, usage partiel ou consommation effective dans le contexte runtime. | `AMBIGU` | Haute | Audit code + traces de pipeline |
| V4 | AUDIT | Vérifier les variantes de flags ou de configuration pouvant modifier le comportement documentaire ou trainer entre local et distant. | `A_VERIFIER` | Haute | Audit runtime + config |
| V5 | AUDIT | Vérifier si un contrat d’exposition dédié de progression documentaire / contexte documentaire existe déjà, ou si tout passe uniquement par `ui-state` et services internes. | `AMBIGU` | Moyenne | Audit code + endpoints |
| V6 | AUDIT | Vérifier si certaines docs trainer ou surfaces back-office exposent déjà des statuts, workflows ou validations plus riches que ce que le corpus d’audit actuel documente. | `A_VERIFIER` | Moyenne | Audit code + parcours UI interne |

---

## 4. Synthèse priorisée pour CTO

Liste très courte des **actions clés** à remonter dans un plan CTO global, en distinguant doc/spec, backend et audit.

- **D1** — Corriger sans délai la documentation qui sur-vend un RAG vectoriel déjà actif alors que le runtime local audité montre une sélection lexicale.[file:16]
- **D2** — Réécrire le domaine avec une hiérarchie nette référentiel → base formateur → documentaire/RAG, cohérente avec la doctrine 2.0.[file:6][file:7]
- **D3** — Ajouter les noms réels observés du domaine dans la doc pour réduire les collisions doctrine / code.[file:1]
- **D4** — Borner explicitement “présence réelle partielle” versus “chaîne trainer 2.0 complète non prouvée”.[file:5][file:16]

- **B1** — Formaliser un contrat backend simple séparant référentiel, base formateur, documentaire et RAG runtime.[file:6][file:7]
- **B2** — Préparer un contrat additif de contexte documentaire (`DocumentContextBundle` ou équivalent) sans double pipeline ni front-driven.[file:7][file:6]
- **B3** — Stabiliser la place de `TrainerKnowledgeItem` dans la chaîne backend apprenant, avec garde-fous de validation humaine.[file:5][file:6]

- **V1** — Vérifier si le runtime distant diverge du local sur la récupération documentaire et un éventuel vectoriel actif.[file:16]
- **V2** — Vérifier la chaîne d’indexation réellement active et son niveau de sophistication effectif.[file:16]
- **V3** — Vérifier le niveau réel de consommation de `TrainerKnowledgeItem` dans le pipeline apprenant.[file:5][file:16]