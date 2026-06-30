# 00_rapport_ecarts — 50_orchestrateur_formateur

> **Mise à jour post-cluster 16 — 2026-06-18** · **Cluster 16 :** pas d'impact direct. **PARTIEL :** atelier élicitation V0 (C15).

## Domaine

- `DOMAINE_CODE = 50_orchestrateur_formateur`
- `DOMAINE_LABEL = orchestrateur formateur`

---

## 1. Objet du rapport

Ce rapport qualifie, pour le seul domaine **orchestrateur formateur** de Hugo cœur, l’écart entre :
- la **cible 2.0** décrite par la spec canonique, son complément et les specs de domaine ;
- le **réel observable** décrit par les audits du workspace Hugo réel ;
- le **pont de vocabulaire** fourni par le glossaire d’alignement.

Ce document ne traite ni Hugo & Cie, ni un backlog transversal 2.0, ni une refonte générale du moteur. Il vise uniquement à :
- borner le périmètre du domaine ;
- décrire ce qui est réellement observable ;
- analyser les écarts de manière narrative ;
- rappeler explicitement les garde-fous de lecture.

---

## 2. Règles de lecture et de vérité appliquées à ce domaine

### 2.1 Réel, cible, glossaire

Pour parler du **réel**, ce rapport s’appuie d’abord sur les audits du corpus Hugo réel, en particulier :
- `02_ETAT_MOTEUR_REEL.md` pour les services backend, les objets trainer, l’ingestion documentaire et les vues ou endpoints observés ;
- `03_ETAT_PRODUIT_REEL.md` pour les surfaces réellement visibles côté front ;
- `07_RUNTIME_DEMO_REFERENCE.md` pour ne pas confondre démo produit et preuve moteur ;
- `05_ECARTS_DOC_CODE_PRODUIT.md` pour les contradictions confirmées entre specs, code local et runtime distant supposé.

Pour parler de la **cible**, ce rapport s’appuie sur :
- `spec_canonique_hugo_2_0.md` ;
- `complement_unique_specs_2_0.md` ;
- les documents 2.0 de domaine mentionnés par le glossaire comme corpus cible de référence.

Le **glossaire d’alignement** sert uniquement à raccorder vocabulaire doctrinal et noms réels observés. Il ne prouve jamais, à lui seul, qu’un workflow formateur complet est implémenté.

### 2.2 Garde-fous de lecture

- La spec 2.0 décrit un **état cible** ; elle ne prouve jamais qu’un orchestrateur formateur complet est déjà livré.
- La présence d’un objet `TrainerKnowledgeItem`, d’une vue trainer ou d’un service d’ingestion documentaire ne prouve pas, à elle seule, que toute la chaîne cible est stabilisée de bout en bout.
- Toute affirmation dépendant du runtime distant, de flags ou de variantes non auditées reste marquée `A_VERIFIER`.
- Le domaine doit être lu dans la doctrine Hugo 2.0 : backend Django orchestré, moteur piloté par état, P0 conserv et enrichi additivement, TutorPrompt pivot runtime, validation humaine obligatoire, front consommateur d’états et d’objets backend gouvernés.

---

## 3. Périmètre cible 2.0 du domaine

Dans la cible Hugo 2.0, l’**orchestrateur formateur** est un orchestrateur spécialisé distinct des régimes apprenant.

### 3.1 Ce que la cible 2.0 fixe déjà

La cible fixe les points suivants :

- L’orchestrateur formateur sert à **faire élaborer, expliciter, structurer et valider** le savoir métier utile au système.
- Il combine **ingestion documentaire gouvernée** et **questionnaire dialogique**.
- Il ne s’agit pas d’un simple écran d’administration ni d’un simple CRUD documentaire.
- Il produit des objets de connaissance structurés, de type `TrainerKnowledgeItem` ou équivalent.
- Ces objets doivent comporter au minimum :
  - un statut ;
  - un type ;
  - un contenu ;
  - une provenance ;
  - des rattachements référentiels ;
  - des métadonnées d’usage documentaire ou RAG.
- Les statuts minimaux de connaissance doivent distinguer :
  - `declared` ;
  - `derived_provisional` ;
  - `validated_human`.
- Aucun item dérivé ne peut être promu automatiquement vers un statut validé humainement.
- La base formateur reste subordonnée au référentiel métier et à la validation humaine ; elle n’est pas une vérité réglementaire autonome.

### 3.2 Ce que la cible 2.0 laisse encore ouvert

Même si la doctrine est déjà solide, plusieurs points restent volontairement ouverts :
- le script conversationnel détaillé de l’orchestrateur formateur ;
- l’ordre exact des sections ;
- les règles fines de relance ;
- la chorégraphie UI détaillée ;
- la matrice précise des rôles habilités à valider ;
- le niveau exact d’exposition produit des objets trainer ;
- la liste opérationnelle stabilisée des variables backend consommées par les futurs prompts spécialisés.

Le domaine doit donc être lu comme **fortement cadré doctrinalement**, mais **encore partiellement sous-spécifié** sur sa mise en forme détaillée.

---

## 4. Photo du réel observé

### 4.1 Présence réelle d’objets et services trainer

Le réel audité montre que le domaine n’est pas théorique :
- `TrainerKnowledgeItem` est explicitement mentionné dans le corpus d’audit comme objet réel observé ;
- le glossaire le classe comme un alignement fort entre cible et réel ;
- des vues trainer et une couche de gestion associée existent dans le backend audité ;
- la présence d’un service de type `DocumentIngestor` ou équivalent est documentée comme raccord plausible entre ingestion documentaire et production d’items gouvernés.

Autrement dit, le domaine **existe réellement dans Hugo développé** au moins sous forme d’objets, de vues et de briques backend.

### 4.2 Ce que le réel permet d’affirmer avec confiance

Le réel permet d’affirmer, avec un niveau de confiance raisonnable, que :
- Hugo cœur possède déjà une **base de connaissances formateur nominale** ;
- des objets `TrainerKnowledgeItem` sont présents ;
- des vues/actions trainer existent ;
- l’ingestion documentaire fait partie du périmètre du système ;
- la responsabilité métier “structurer du savoir formateur utile au système” n’est donc pas absente du code.

Le glossaire renforce cette lecture en indiquant que `TrainerKnowledgeItem` est l’un des alignements les plus solides entre doctrine 2.0 et réel audité.

### 4.3 Ce que le réel ne prouve pas encore complètement

En revanche, le corpus audité utilisé ici ne prouve pas, à lui seul :
- qu’un **questionnaire dialogique complet** de l’orchestrateur formateur est déjà stabilisé ;
- que le workflow formateur est entièrement lisible et homogène dans ses statuts, validations et relances ;
- que la chaîne complète `documents -> explicitation trainer -> items structurés -> validation -> consommation apprenant` est démontrée de bout en bout dans toutes ses étapes ;
- que les variantes runtime distantes suivent exactement le même comportement que le code local audité.

Le réel montre donc des **briques substantielles et compatibles**, mais pas encore une preuve simple d’un orchestrateur formateur 2.0 totalement clos.

### 4.4 Surface produit réellement visible

Côté produit, le domaine apparaît surtout sur des surfaces **trainer / testeur / back-office**, et non dans le parcours apprenant prod montrable.

Le produit réel audité montre :
- un parcours apprenant centré sur conversation, `ui-state`, synthèse, évaluation, partage et preuves ;
- des routes et vues trainer / admin séparées ;
- une exposition plus limitée du domaine formateur dans la démo publique.

Le domaine doit donc être lu comme un domaine **majoritairement backend et métier**, avec une existence produit réelle, mais peu démonstrative côté parcours apprenant standard.

### 4.5 Runtime de démonstration et limites de preuve

La baseline de démo observée s’appuie sur `frontend1.8` branché par défaut sur une API distante.

Cela implique une limite importante pour ce domaine :
- une démo fonctionnelle peut montrer que certaines surfaces trainer existent ;
- elle ne prouve pas à elle seule la complétude du workflow local audité ;
- elle ne prouve pas non plus l’équivalence exacte entre code local et runtime distant ;
- tout écart de flags, d’activation ou de version back doit rester `A_VERIFIER`.

---

## 5. Analyse narrative des écarts

### 5.1 Zone de bon alignement

Le domaine **orchestrateur formateur** présente un bon alignement de fond entre cible 2.0 et réel audité.

La cible 2.0 décrit un orchestrateur spécialisé de structuration du savoir métier, et le réel montre déjà :
- une base formateur ;
- des objets `TrainerKnowledgeItem` ;
- des vues trainer ;
- une ingestion documentaire ;
- une logique de connaissance gouvernée distincte du parcours apprenant standard.

Il serait donc incorrect de conclure que le domaine est absent ou purement spéculatif.

### 5.2 Écart principal : le workflow complet est encore plus doctrinal que probant

Le principal écart ne porte pas sur l’existence du domaine, mais sur le **niveau de complétude démontré**.

La cible 2.0 parle d’un orchestrateur formateur dialogique, structurant, validant et produisant des items réutilisables. Le réel montre des objets et des briques compatibles, mais le corpus audité ne donne pas encore une preuve simple et continue d’un workflow complet, stabilisé et documenté de bout en bout.

L’écart est donc surtout un **écart de formalisation et de preuve complète**, plus qu’un écart d’absence.

### 5.3 Écart important : script conversationnel encore ouvert

La cible 2.0 assume explicitement que le script détaillé de l’orchestrateur formateur reste ouvert :
- ordre exact des questions ;
- stratégie de relance ;
- sections ;
- écrans ;
- granularité UX.

Le réel n’entre pas non plus, dans les audits utilisés ici, dans un niveau de détail permettant de dire que cette couche est déjà finalisée. Sur ce point, cible et réel sont moins en contradiction qu’en **coexistence d’un ouvert cadré** : la doctrine fixe l’ambition, mais ni la cible ni le réel n’imposent encore une chorégraphie fine figée.

### 5.4 Écart de vocabulaire : doctrine propre, noms réels encore à raccorder

Le glossaire montre que l’objet `TrainerKnowledgeItem` est bien aligné, mais il confirme aussi la nécessité de documenter proprement les noms réels observés côté backend et vues trainer.

Cela signifie que le travail principal n’est pas de rebaptiser toute la doctrine avec les noms du code, mais de :
- conserver la structure 2.0 ;
- ajouter les noms réels utiles ;
- distinguer nom doctrinal, nom réel observé, niveau de preuve et action documentaire.

L’écart ici est un **écart documentaire de raccord**, pas un problème architectural majeur.

### 5.5 Écart de gouvernance : validation humaine doctrinalement claire, opérationnellement encore à préciser

La cible 2.0 verrouille très clairement l’invariant suivant :
- pas d’auto-promotion d’un item dérivé vers un statut validé humainement.

Le réel est compatible avec cette exigence, mais le corpus audité ici ne suffit pas encore à documenter finement :
- quels rôles exacts valident ;
- sur quelles surfaces ;
- avec quelles transitions détaillées ;
- avec quel niveau de traçabilité produit.

L’écart n’est donc pas un désaccord doctrinal ; c’est un **écart de précision de contrat**.

### 5.6 Écart de consommation aval : rôle exact dans les orchestrateurs apprenant encore partiellement prouvé

La cible 2.0 fixe que les `TrainerKnowledgeItem` validés doivent enrichir les orchestrateurs apprenant et le RAG gouverné, sans court-circuiter le référentiel ni la validation humaine.

Le réel montre que cette articulation est plausible et préparée, mais le corpus mobilisé ici ne permet pas de décrire de façon exhaustive :
- quand les items trainer sont lus ;
- par quels services précis ;
- dans quels régimes apprenant ;
- avec quels garde-fous exacts par régime.

Ce point doit donc rester **partiellement confirmé** et non sur-affirmé.

### 5.7 Ce que la spec 2.0 ne doit pas déclencher ici

La spec 2.0 ne doit pas être relue, sur ce domaine, comme une injonction à reconstruire tout un sous-système.

Le réel couvre déjà une part importante de la responsabilité métier :
- objets ;
- briques trainer ;
- ingestion ;
- structuration de savoir ;
- gouvernance de connaissance.

La bonne lecture est donc :
- conserver ce socle ;
- clarifier les contrats ;
- mieux documenter les statuts et le rôle de validation ;
- préparer les compléments backend additifs nécessaires ;
- éviter toute refonte doctrinale ou architecture parallèle.

---

## 6. Lecture de synthèse par niveau de vérité

### 6.1 Implémenté / observable

Sur ce domaine, le réel audité permet de considérer comme **implémenté ou observable** :
- l’existence d’une base formateur ;
- la présence de `TrainerKnowledgeItem` ;
- des vues / actions trainer ;
- une ingestion documentaire liée au domaine ;
- un raccord conceptuel fort entre cible 2.0 et objets réels du système.

### 6.2 Cible 2.0

Relèvent clairement de la **cible 2.0** :
- l’orchestrateur formateur comme dialogue d’élaboration structuré ;
- le pseudo-contrat doctrinal complet de `TrainerKnowledgeItem` ;
- la formalisation fine des statuts et transitions ;
- la matrice détaillée des rôles de validation ;
- la liste stabilisée des variables backend pour prompts spécialisés ;
- la chorégraphie détaillée du workflow formateur.

### 6.3 Écarts confirmés

Les écarts confirmés sur ce domaine sont principalement :
- absence de preuve simple d’un workflow complet formateur 2.0 stabilisé de bout en bout ;
- raccord documentaire insuffisant entre vocabulaire doctrinal et noms réels observés ;
- niveau de précision encore insuffisant sur les transitions de validation ;
- rôle exact de consommation aval des items trainer encore partiellement documenté.

### 6.4 À vérifier

Restent explicitement `A_VERIFIER` :
- l’équivalence entre code local audité et runtime distant pour les surfaces trainer ;
- les flags ou variantes activant certaines capacités trainer ;
- la profondeur réelle du questionnaire dialogique en runtime distant ;
- le mapping exact entre objets trainer locaux et leur consommation effective dans tous les orchestrateurs apprenant ;
- toute affirmation forte sur un workflow complet “déjà livré” au-delà de ce que les audits permettent de constater.

---

## 7. Garde-fous pour la suite documentaire et technique

### 7.1 Ce qu’il ne faut pas faire

Pour ce domaine, il faut éviter :
1. de relire la spec 2.0 comme preuve que l’orchestrateur formateur complet est déjà en production ;
2. de déduire un workflow complet du seul fait que `TrainerKnowledgeItem` existe ;
3. de réduire le domaine à un simple CRUD admin documentaire ;
4. de lancer une refonte globale alors que le réel couvre déjà une part sérieuse de la responsabilité métier ;
5. de projeter sur Hugo cœur des éléments Hugo & Cie ou des extensions non auditées.

### 7.2 Ce qu’il faut privilégier

La bonne trajectoire pour ce domaine consiste à :
- clarifier le contrat documentaire du domaine ;
- stabiliser le vocabulaire de raccord entre doctrine et code ;
- expliciter ce qui est observé, partiellement observé, cible, ou `A_VERIFIER` ;
- préparer les compléments backend additifs sans casser le socle existant ;
- séparer rigoureusement validation humaine, ingestion, structuration et consommation aval.

---

## 8. Conclusion opérationnelle du domaine

Le domaine `50_orchestrateur_formateur` n’est ni un angle mort, ni un sous-système 2.0 déjà complètement prouvé.

Le réel audité montre un socle substantiel déjà présent dans Hugo cœur : objets `TrainerKnowledgeItem`, vues trainer, ingestion documentaire, logique de connaissance gouvernée. La cible 2.0 ajoute un cadrage fort sur la nature dialogique de l’orchestrateur, les statuts, la validation humaine et l’articulation avec les orchestrateurs apprenant.

L’écart principal n’est donc pas une absence brute, mais un écart de **formalisation, de preuve complète et de raccord documentaire**. La suite logique sur ce domaine n’est pas une refonte, mais un travail méthodique de clarification des contrats, d’alignement de vocabulaire et de bornage explicite des zones encore `A_VERIFIER`.

# 01_matrice_ecarts — 50_orchestrateur_formateur

## Domaine

- `DOMAINE_CODE = 50_orchestrateur_formateur`
- `DOMAINE_LABEL = orchestrateur formateur`

---

## 1. Légende des statuts

- `ALIGNE` : cible 2.0 et réel audité convergent, vocabulaire déjà raccord.
- `ALIGNE_DOC_PARTIEL` : fond aligné, mais la documentation doit mieux l’expliciter.
- `RENOMMER_DANS_DOC` : la doc 2.0 doit faire apparaître un nom réel observé.
- `AMBIGU` : mapping cible / réel plausible mais pas assez net.
- `A_VERIFIER` : information dépendant de runtime distant, flags ou zones non auditées.
- `ABSENT / NOUVEAU_CONTRAT` : contrat cible sans preuve d’implémentation dans le réel audité (ou domaine à créer).

---

## 2. Matrice d’écarts — objets et responsabilités

### 2.1 Objets de connaissance formateur

| Élément cible 2.0                                      | Nom(s) réel(s) observé(s) / indice code | Constat d’alignement                                                                 | Statut                  | Commentaire opérationnel                                                                                                      |
|--------------------------------------------------------|------------------------------------------|--------------------------------------------------------------------------------------|-------------------------|------------------------------------------------------------------------------------------------------------------------------|
| Base de connaissances formateur gouvernée             | Présence d’une base formateur, modèles trainer, vues trainer | Base formateur bien présente, cohérente avec la cible 2.0 (savoir gouverné, distinct du parcours apprenant). | ALIGNE                  | Ne pas la relire comme “non implémentée” ; travail à faire sur la formalisation documentaire, pas sur l’existence.          |
| `TrainerKnowledgeItem` comme objet pivot              | `TrainerKnowledgeItem`                   | Objet central doctrinal et observé dans le réel, identifié comme alignement fort.   | ALIGNE                  | Nom pivot à conserver dans la doc 2.0 et à relier explicitement aux fichiers / modules concrets dans les annexes.          |
| Statuts de connaissance (`declared`, `derived_provisional`, `validated_human`) | Champs de statut dans les modèles trainer (à confirmer finement) | Doctrine claire, existence de statuts dans le code, mais mapping exact partiellement documenté. | ALIGNE_DOC_PARTIEL      | Documenter les noms de champs réels, leurs valeurs, et l’absence d’auto-promotion.                                         |
| Non-auto-promotion vers “validé humainement”          | Règles de validation côté trainer        | Doctrine explicite ; pas de preuve d’auto-promotion dans l’audit, mais pas encore un contrat documenté complet. | ALIGNE_DOC_PARTIEL      | Formaliser la règle comme invariant de domaine, vérifier ponctuellement dans le code et l’admin.                           |
| Subordination au référentiel métier                   | `referentials`, import RNCP, liens référentiels | Cible et réel convergent : référentiel primaire bien présent, base formateur en surcouche. | ALIGNE                  | À rappeler nettement dans la doc du domaine pour éviter toute relecture “base formateur = vérité réglementaire”.           |

### 2.2 Orchestrateur formateur comme service

| Élément cible 2.0                                      | Nom(s) réel(s) observé(s) / indice code        | Constat d’alignement                                                                     | Statut                  | Commentaire opérationnel                                                                                           |
|--------------------------------------------------------|------------------------------------------------|------------------------------------------------------------------------------------------|-------------------------|-------------------------------------------------------------------------------------------------------------------|
| Orchestrateur formateur (orchestrateur spécialisé distinct des régimes apprenant) | Briques trainer + ingestion doc + vues dédiées | Responsabilité métier présente, mais pas de service “unique” lisible comme orchestrateur complet dans l’audit. | ALIGNE_DOC_PARTIEL      | Domaine réel existant ; orchestrateur à formaliser comme combinaison de services plutôt que comme unique classe. |
| Dialogue d’élaboration (questionnaire formateur)       | Flows / vues / formulaires trainer             | Doctrine claire, existence de surfaces trainer, mais script conversationnel non documenté en détail.           | AMBIGU                  | Cible fixée, réel partiel ; à documenter comme “OUVERT_CADRE”, non comme “déjà complètement livré”.              |
| `DocumentIngestor` / ingestion documentaire gouvernée | Service d’ingestion documentaire utilisé par trainer | Alignement fort cible / réel sur la présence de l’ingestion; détails de gouvernance partiellement décrits.    | ALIGNE_DOC_PARTIEL      | Mieux décrire le rôle exact dans la chaîne formateur -> items -> usage RAG / apprenant.                          |
| Production d’items structurés pour les orchestrateurs apprenant | `TrainerKnowledgeItem` + usage RAG / apprenant (partiel) | Cible explicite ; réel compatible mais niveau d’usage runtime exact pas entièrement prouvé dans tous les modes. | A_VERIFIER              | Audit ciblé à prévoir pour confirmer le chaînage complet et ses garde-fous par régime conversationnel.           |

---

## 3. Matrice d’écarts — workflow et statuts

| Élément cible 2.0                                      | Nom(s) réel(s) observé(s)          | Constat d’alignement                                                       | Statut                  | Commentaire opérationnel                                                                                     |
|--------------------------------------------------------|------------------------------------|----------------------------------------------------------------------------|-------------------------|-------------------------------------------------------------------------------------------------------------|
| Workflow complet d’orchestrateur formateur (étapes, sections, relances) | Vues trainer, routes formateur     | Doctrine claire, briques présentes, mais aucune spec fine du script complet ni preuve d’un flow unique stabilisé. | AMBIGU                  | À documenter comme “workflow cible à préciser”, sans supposer une implémentation complète déjà figée.       |
| Étapes : upload docs -> explicitation -> structuration -> validation | Uploads trainer + ingestion doc    | Étapes “upload” et ingestion réelles ; structuration/validation visibles mais sans chaîne documentée exhaustive. | ALIGNE_DOC_PARTIEL      | Décrire la séquence minimale observée et ce qui est encore à formaliser comme contrat explicite.            |
| Validation humaine explicite obligatoire               | Actions de validation / changement de statut | Conforme à la doctrine ; pas de contradiction relevée, mais pas de matrice claire rôle x statut.                 | ALIGNE_DOC_PARTIEL      | À traduire en matrice rôles x statuts dans la doc, sans inventer de workflow multi-rôles non prouvé.        |
| Rôle exact des rôles (formateur, coordinateur, org admin) dans la validation | Surfaces trainer / admin (partielles) | Doctrine ouverte sur la répartition ; réel montre surtout des vues formateur/admin, sans répartition exhaustive. | AMBIGU                  | À laisser explicite comme zone ouverte, éviter de fixer un partage des rôles sans décision produit claire.  |

---

## 4. Matrice d’écarts — consommation aval par les orchestrateurs apprenant

| Élément cible 2.0                                      | Nom(s) réel(s) observé(s)         | Constat d’alignement                                                    | Statut        | Commentaire opérationnel                                                                                         |
|--------------------------------------------------------|-----------------------------------|-------------------------------------------------------------------------|---------------|-----------------------------------------------------------------------------------------------------------------|
| Consommation des `TrainerKnowledgeItem` par les régimes apprenant | Raccord plausible via RAG et context builders | Doctrine explicite ; réel montre briques compatibles, mais intensité / couverture d’usage non démontrée. | A_VERIFIER    | Nécessite un audit code ciblé pour chaque régime (réflexif, diagnostic, révision).                              |
| Utilisation comme base documentaire enrichie (RAG gouverné) | RAG documentaire + items trainer | Cible claire : RAG gouverné ; réel : RAG lexical et base formateur existante, pas de preuve d’un RAG “full gouverné”. | ALIGNE_DOC_PARTIEL | Ne pas sur-vendre un RAG gouverné complet ; documenter honnêtement le niveau réel (lexical + gouvernance partielle). |
| Respect de la hiérarchie contexte (mémoire thématique, référentiel, items trainer, documentaire) | Ordre consolidé dans la doctrine ; code partiellement aligné | Doctrine fixée ; réel montre une hiérarchie partielle, mais injection mémoire et usage trainer encore incomplets. | ALIGNE_DOC_PARTIEL | À décrire comme hiérarchie cible consolidée, avec point spécifique “injection LearnerThemeMemory / trainer” confirmée manquante. |

---

## 5. Matrice d’écarts — surfaces UI formateur

| Élément cible 2.0                                      | Nom(s) réel(s) observé(s)          | Constat d’alignement                                                      | Statut                  | Commentaire opérationnel                                                                                          |
|--------------------------------------------------------|------------------------------------|---------------------------------------------------------------------------|-------------------------|------------------------------------------------------------------------------------------------------------------|
| Vue formateur orientée “élaboration de savoir”         | Vues trainer / admin existantes    | Surfaces réelles présentes, mais non décrites comme orchestrateur complet dans la doc.                          | ALIGNE_DOC_PARTIEL      | Documenter ce qui existe réellement en évitant de prétendre à une UI finalisée 2.0.                             |
| UI pour statuts de connaissance                        | Écrans affichant états / statuts   | Existence probable d’affichage partiel des statuts ; niveau de lisibilité et de filtrage encore peu documenté. | AMBIGU                  | À clarifier dans les specs d’interface 2.0, sans prendre les maquettes anciennes comme vérité d’état actuel.   |
| Export / vue structurée de la base formateur           | Exports, listes, filtres trainer   | Doctrine prévoit des exports ; réel comporte une couche exports générale, mapping exact avec base formateur à détailler. | A_VERIFIER              | Nécessite une vérification spécifique des endpoints / vues utilisés pour les items trainer.                     |

---

## 6. Matrice d’écarts — contrats et vocabulaire

| Élément cible 2.0                                      | Nom(s) réel(s) observé(s)                    | Constat d’alignement                                                        | Statut                  | Commentaire opérationnel                                                                                               |
|--------------------------------------------------------|----------------------------------------------|-------------------------------------------------------------------------------|-------------------------|-----------------------------------------------------------------------------------------------------------------------|
| Nom doctrinal `orchestrateur formateur`               | Combinaison de services / vues trainer        | Concept doctrinal clair, peu de traces textuelles directes dans le code sous ce nom. | RENOMMER_DANS_DOC       | Garder le terme doctrinal dans les specs, tout en listant les services réels qui incarnent cette responsabilité.      |
| Nom doctrinal `TrainerKnowledgeItem`                  | `TrainerKnowledgeItem`                        | Alignement fort, concept et nom déjà partagés cible / réel.                  | ALIGNE                  | À utiliser comme pivot dans le glossaire de domaine et les futures matrices.                                          |
| Nom doctrinal `DocumentIngestor`                      | Tâches / services d’ingestion documentaire    | Concept présent, noms concrets à expliciter (tâches, jobs, services).        | RENOMMER_DANS_DOC       | Ajouter les noms de fonctions / modules observés dans la matrice backend de la spec canonique.                       |
| Contrat d’objet détaillé pour `TrainerKnowledgeItem`  | Champs de modèle réels (à préciser)           | Doctrine fixe le rôle ; réel possède un modèle, mais contrat documentaire light encore manquant. | ABSENT / NOUVEAU_CONTRAT | Nouveau contrat documentaire à rédiger, sans sur-spécifier l’ORM.                                                    |
| Matrice rôles x statuts formateur                     | Rôles existants, permissions partielles       | Doctrine générale sur validation humaine ; répartition fine des droits incertaine. | ABSENT / NOUVEAU_CONTRAT | Matrice à produire dans `02_decisions_documentaires.md` sans prétendre décrire déjà le produit final 2.0 complet.    |

---

## 7. Matrice d’écarts — dépendances runtime / variantes

| Élément cible 2.0                                      | Nom(s) réel(s) observé(s)           | Constat d’alignement                                              | Statut     | Commentaire opérationnel                                                                                 |
|--------------------------------------------------------|-------------------------------------|-------------------------------------------------------------------|------------|---------------------------------------------------------------------------------------------------------|
| Comportement de l’orchestrateur formateur sur runtime local | Code audité (backend local)         | Briques présentes, comportement global compatible avec la doctrine 2.0. | ALIGNE_DOC_PARTIEL | Continuer à utiliser le local comme base principale pour décrire le réel.                              |
| Comportement de l’orchestrateur formateur sur runtime distant (Encoors) | API distante, flags, baselines A/B | Non audité directement ; dépend de configs et flags non complètement documentés. | A_VERIFIER | Ne jamais présenter l’état distant comme preuve d’une version plus aboutie du domaine sans inspection. |

---

## 8. Synthèse par famille

- **Objets de connaissance formateur** : responsabilité métier et pivot `TrainerKnowledgeItem` bien alignés (`ALIGNE` / `ALIGNE_DOC_PARTIEL`), besoin surtout de contrats documentaires explicites.
- **Service “orchestrateur formateur”** : responsabilité réelle présente mais fragmentée dans le code (`ALIGNE_DOC_PARTIEL` / `AMBIGU`), workflow complet encore `OUVERT_CADRE`.
- **Workflow et validation** : doctrine claire, réel compatible mais incomplet en termes de preuve et de documentation (`ALIGNE_DOC_PARTIEL` / `AMBIGU`).
- **Consommation aval** : usage partiel plausible, mais à confirmer service par service (`A_VERIFIER`).
- **UI formateur** : surfaces réelles existantes, mais non documentées comme orchestrateur complet 2.0 (`ALIGNE_DOC_PARTIEL` / `AMBIGU`).
- **Contrats et vocabulaire** : plusieurs éléments à marquer `RENOMMER_DANS_DOC` ou `ABSENT / NOUVEAU_CONTRAT` côté documentaire, en gardant la doctrine 2.0 comme structure.


# 02_decisions_documentaires — 50_orchestrateur_formateur

## Domaine

- `DOMAINE_CODE = 50_orchestrateur_formateur`
- `DOMAINE_LABEL = orchestrateur formateur`

---

## 1. Objet du document

Ce document fixe les **décisions documentaires** à appliquer pour le domaine **orchestrateur formateur** dans le corpus Hugo cœur.

Il ne s’agit ni d’une preuve d’implémentation supplémentaire, ni d’une spec détaillée de chantier, ni d’une décision de refonte code. Son rôle est plus limité et plus opérationnel :
- stabiliser le vocabulaire ;
- distinguer clairement réel observé, cible 2.0 et zones ouvertes ;
- décider ce qui doit être réécrit, complété, renommé ou explicitement laissé ouvert dans la documentation ;
- éviter que les futures specs, matrices et prompts Cursor mélangent doctrine, glossaire et état livré.

---

## 2. Principes directeurs retenus pour ce domaine

### 2.1 Doctrine conservée

Décision :
- la doctrine 2.0 sur l’orchestrateur formateur est **conservée** comme cadre de référence.

Conséquence documentaire :
- on maintient explicitement que l’orchestrateur formateur est un **orchestrateur spécialisé distinct des régimes apprenant** ;
- on maintient qu’il sert à **élaborer, expliciter, structurer et valider** le savoir métier utile au système ;
- on maintient qu’il combine **ingestion documentaire gouvernée** et **dialogue d’explicitation** ;
- on maintient qu’il ne s’agit ni d’un simple écran admin, ni d’un simple CRUD documentaire.

Cette décision est conservatrice au bon sens du terme : elle évite de dégrader la doctrine 2.0 sous prétexte que le réel audité est encore partiellement fragmenté.

### 2.2 Réel non sous-estimé

Décision :
- la documentation de domaine doit reconnaître explicitement que le réel audité montre déjà un **socle trainer substantiel**.

Conséquence documentaire :
- il ne faut plus écrire ou laisser entendre que l’orchestrateur formateur serait “à inventer” ou “absent du réel” ;
- il faut mentionner explicitement l’existence observée de :
  - `TrainerKnowledgeItem` ;
  - vues / actions trainer ;
  - ingestion documentaire ;
  - base de connaissances formateur nominale.

La bonne formulation documentaire n’est donc ni “déjà complet”, ni “pas encore là”, mais : **socle réel présent, contrat 2.0 encore partiellement à formaliser**.

### 2.3 Glossaire utilisé comme pont, pas comme preuve

Décision :
- le glossaire d’alignement reste un **outil de raccord vocabulaire**, jamais une preuve autonome d’implémentation.

Conséquence documentaire :
- toute décision de rédaction sur ce domaine doit continuer à croiser :
  - spec canonique 2.0 ;
  - complément 2.0 ;
  - audits du réel ;
  - glossaire d’alignement.
- aucune phrase du type “le glossaire montre que c’est implémenté” ne doit apparaître.

---

## 3. Décisions de vocabulaire

### 3.1 Terme directeur à conserver

Décision :
- le terme directeur à conserver dans la documentation est **orchestrateur formateur**.

Conséquence documentaire :
- on ne remplace pas ce terme par “module trainer”, “admin trainer”, “workflow d’upload”, ou par un nom de fonction Python ;
- la doctrine doit continuer à nommer la responsabilité métier avec un terme stable et intelligible.

### 3.2 Nom pivot d’objet à conserver

Décision :
- `TrainerKnowledgeItem` reste le **nom pivot** de l’objet de connaissance formateur dans la documentation 2.0.

Conséquence documentaire :
- ce nom doit être gardé comme point d’ancrage central dans :
  - la spec canonique ;
  - la spec formateur / tuteur ;
  - les futures annexes techniques ;
  - les matrices d’écarts.
- il faut éviter de disperser la documentation entre plusieurs synonymes non stabilisés pour ce même rôle métier.

### 3.3 Ajout obligatoire des noms réels observés

Décision :
- la documentation 2.0 doit désormais faire apparaître, quand ils sont connus, les **noms réels observés** correspondant aux responsabilités de l’orchestrateur formateur.

Conséquence documentaire :
- dans les matrices et annexes, ajouter une colonne ou un sous-bloc “nom réel observé dans Hugo développé” ;
- pour ce domaine, faire apparaître au minimum :
  - `TrainerKnowledgeItem` ;
  - vues / actions trainer ;
  - service d’ingestion documentaire ou équivalent ;
  - objets référentiels liés quand ils participent au workflow.

Règle de rédaction :
- nom doctrinal pour raisonner juste ;
- nom réel pour parler juste du développé ;
- jamais l’un sans l’autre quand le mapping est connu.

### 3.4 Pas de rebaptême brutal à partir du code

Décision :
- aucun rebaptême doctrinal global ne doit être déclenché à partir des seuls noms techniques du code.

Conséquence documentaire :
- on n’écrase pas le terme “orchestrateur formateur” au profit d’un assemblage de noms de fichiers ;
- on n’écrase pas non plus la structure doctrinale sous prétexte que le réel apparaît plus fragmenté dans les audits.

---

## 4. Décisions sur le périmètre documentaire

### 4.1 Périmètre minimum désormais figé dans la doc

Décision :
- le périmètre minimum à documenter comme **acté côté cible 2.0** est le suivant :
  1. upload de documents métier ;
  2. dialogue guidé d’explicitation ;
  3. production d’items de connaissance structurés ;
  4. validation humaine obligatoire avant passage à un statut validé.

Conséquence documentaire :
- ces quatre points doivent apparaître ensemble dans la documentation du domaine ;
- il ne faut pas documenter seulement l’upload ou seulement les statuts ;
- il faut montrer que le domaine est une **chaîne métier cohérente**, même si son script fin reste ouvert.

### 4.2 Script détaillé laissé explicitement ouvert

Décision :
- le **workflow conversationnel détaillé** de l’orchestrateur formateur reste explicitement **ouvert** dans la documentation de référence.

Conséquence documentaire :
- ne pas figer prématurément :
  - ordre exact des sections ;
  - wording des relances ;
  - enchaînement UX détaillé ;
  - granularité des écrans.
- les futures docs doivent utiliser une formulation du type :
  - “périmètre fixé” ;
  - “script détaillé à préciser” ;
  - “workflow détaillé non figé à ce stade”.

Cette décision évite deux dérives symétriques :
- prétendre que tout est déjà spécifié ;
- relancer inutilement le débat doctrinal alors que le cadrage métier est déjà clair.

### 4.3 Pas de confusion avec un simple back-office documentaire

Décision :
- la documentation doit désormais expliciter que l’orchestrateur formateur **n’est pas** un simple sous-ensemble d’administration documentaire.

Conséquence documentaire :
- les surfaces trainer ne doivent pas être décrites uniquement sous l’angle “upload / liste / filtre / validation” ;
- il faut maintenir la dimension de **dialogue d’élaboration** comme partie constitutive du domaine, même si son UX fine reste ouverte.

---

## 5. Décisions sur les objets et statuts

### 5.1 Contrat documentaire léger pour `TrainerKnowledgeItem`

Décision :
- un **pseudo-contrat documentaire léger** doit être ajouté pour `TrainerKnowledgeItem`.

Conséquence documentaire :
- sans transformer la spec en documentation ORM exhaustive, il faut faire apparaître au minimum :
  - rôle ;
  - producteur principal ;
  - consommateurs principaux ;
  - exposition front éventuelle ;
  - statuts minimaux ;
  - provenance ;
  - rattachements référentiels ;
  - usage documentaire / RAG.

Formulation attendue :
- document métier orienté responsabilités ;
- pas un schéma SQL détaillé ;
- pas une simple mention nominale sans contenu.

### 5.2 Statuts minimaux à verrouiller dans la doc

Décision :
- les trois statuts doctrinaux minimaux doivent être explicitement maintenus dans la doc :
  - `declared` ;
  - `derived_provisional` ;
  - `validated_human`.

Conséquence documentaire :
- ces statuts doivent être visibles dans la spec de domaine et rappelés dans les matrices ;
- si les noms de champs réels diffèrent partiellement, la doc devra afficher le mapping au lieu de supprimer le vocabulaire 2.0.

### 5.3 Invariant de non-auto-promotion à rendre plus visible

Décision :
- la règle “aucun item dérivé ne passe automatiquement à validé humainement” devient un **invariant documentaire de premier niveau** pour ce domaine.

Conséquence documentaire :
- cette règle doit apparaître :
  - dans la spec de domaine ;
  - dans la matrice de validation ;
  - dans les garde-fous de backlog ;
  - dans les futurs prompts Cursor liés au domaine.
- il faut la traiter comme un invariant de non-régression, pas comme une simple note de bas de page.

### 5.4 Matrice rôles x statuts à créer, sans fiction produit

Décision :
- une matrice documentaire **rôles x statuts x actions** doit être produite ultérieurement pour ce domaine.

Conséquence documentaire :
- cette matrice doit préciser :
  - qui peut créer ;
  - qui peut corriger ;
  - qui peut proposer ;
  - qui peut valider ;
  - qui peut exporter.
- en revanche, tant que les audits et arbitrages ne vont pas plus loin, il ne faut pas inventer une répartition détaillée non prouvée entre formateur, coordinateur et admin.

La règle est donc :
- **créer la matrice** ;
- **ne pas sur-spécifier** son contenu au-delà de ce qui est confirmé.

---

## 6. Décisions sur l’articulation avec les autres couches

### 6.1 Référentiel métier prioritaire

Décision :
- la documentation du domaine doit rappeler explicitement que la base formateur reste **subordonnée au référentiel métier**.

Conséquence documentaire :
- toute formulation laissant croire que la base trainer remplace le référentiel doit être corrigée ;
- l’ordre correct est :
  - référentiel primaire ;
  - base formateur gouvernée ;
  - enrichissement documentaire / RAG gouverné.

### 6.2 Usage aval par les orchestrateurs apprenant : formulation prudente

Décision :
- la documentation doit maintenir que les `TrainerKnowledgeItem` sont destinés à enrichir les orchestrateurs apprenant, **sans prétendre que toute la chaîne d’usage est déjà complètement démontrée**.

Conséquence documentaire :
- formulation recommandée :
  - “destinés à être consommés par les orchestrateurs apprenant” ;
  - “usage aval partiellement observé / à confirmer” ;
  - “intégration doctrinalement fixée, niveau de preuve réel partiel”.
- formulation à éviter :
  - “déjà consommés complètement en production dans tous les régimes”.

### 6.3 RAG et base formateur : pas de confusion

Décision :
- la documentation doit distinguer clairement :
  - base de connaissances formateur ;
  - référentiel métier ;
  - documentaire / RAG.

Conséquence documentaire :
- on ne fusionne pas ces trois couches dans un seul bloc flou “knowledge” ;
- on explique leur articulation sans les confondre ;
- on maintient que le RAG reste un **renfort situé**, pas la mémoire principale ni la source souveraine de vérité métier.

---

## 7. Décisions sur les surfaces produit

### 7.1 Existence produit à reconnaître, sans sur-promesse

Décision :
- les surfaces trainer réelles doivent être reconnues dans la documentation, mais sans être décrites comme UI 2.0 finale stabilisée.

Conséquence documentaire :
- la doc doit parler de :
  - surfaces trainer observées ;
  - vues / actions réelles ;
  - exposition partielle côté produit ;
  - granularité encore ouverte sur l’UX complète.
- elle ne doit pas faire croire que la chorégraphie formateur 2.0 est déjà figée et démontrée de bout en bout.

### 7.2 Pas de contamination du parcours apprenant

Décision :
- la documentation du domaine ne doit pas projeter les objets trainer comme s’ils appartenaient au parcours apprenant standard.

Conséquence documentaire :
- bien distinguer :
  - surfaces trainer ;
  - consommation backend aval ;
  - front apprenant.
- `TrainerKnowledgeItem` peut être consommé indirectement côté moteur apprenant, mais il n’est pas un objet apprenant brut à frontaliser tel quel.

---

## 8. Décisions de structure documentaire à appliquer

### 8.1 Dans la spec canonique 2.0

Décision :
- renforcer la matrice des objets de domaine et la matrice des services backend pour ce domaine.

À faire dans la doc :
- ajouter ou expliciter pour `TrainerKnowledgeItem` :
  - rôle ;
  - producteurs ;
  - consommateurs ;
  - exposition ;
  - statuts.
- ajouter les noms réels observés lorsque connus.
- mieux relier la ligne `DocumentIngestor` au domaine orchestrateur formateur.

### 8.2 Dans la spec formateur / tuteur

Décision :
- faire du domaine **orchestrateur formateur** un bloc documentaire plus explicite et moins implicite.

À faire dans la doc :
- isoler un sous-bloc avec :
  - finalité du domaine ;
  - périmètre minimum figé ;
  - statuts ;
  - validation humaine ;
  - zones volontairement ouvertes ;
  - vocabulaire réel observé.

### 8.3 Dans les matrices futures

Décision :
- toutes les futures matrices sur ce domaine doivent intégrer une colonne de niveau de vérité.

Valeurs minimales recommandées :
- `réel observé` ;
- `cible 2.0` ;
- `ouvert cadré` ;
- `A_VERIFIER`.

Cette décision vise à empêcher les glissements entre :
- cible doctrinale ;
- réel audité ;
- hypothèse de chantier.

---

## 9. Formulations à imposer / à proscrire

### 9.1 Formulations à privilégier

Utiliser de préférence :

- “socle trainer réel déjà présent”
- “orchestrateur spécialisé distinct des régimes apprenant”
- “ingestion documentaire gouvernée et dialogue d’explicitation”
- “production d’items structurés gouvernés”
- “validation humaine obligatoire avant statut validé”
- “workflow détaillé encore ouvert / à préciser”
- “usage aval partiellement observé / à confirmer”
- “nom doctrinal 2.0 + nom réel observé”

### 9.2 Formulations à éviter

Éviter :

- “orchestrateur formateur entièrement livré”
- “simple module d’admin documentaire”
- “workflow complet démontré de bout en bout” si ce n’est pas prouvé
- “la base formateur remplace le référentiel”
- “le glossaire prouve l’implémentation”
- “la présence d’un modèle suffit à démontrer le comportement”
- “les prompts définissent à eux seuls la logique du domaine”

---

## 10. Décision de clôture documentaire pour ce domaine

Décision de synthèse :
- pour le domaine `50_orchestrateur_formateur`, la ligne documentaire retenue est la suivante :

> **Conserver la doctrine 2.0, reconnaître explicitement le socle réel déjà présent, documenter le domaine comme une chaîne gouvernée “ingestion + explicitation + structuration + validation”, ajouter les noms réels observés, produire un pseudo-contrat léger de `TrainerKnowledgeItem`, et laisser explicitement ouvert le script détaillé du workflow sans le remplacer par une fiction de complétude ni par une sous-description admin.**

Cette décision constitue la base documentaire de référence pour :
- le backlog d’actions de domaine ;
- les mises à jour des specs 2.0 ;
- les futurs prompts Cursor d’audit et d’alignement.

# 03_backlog_actions — 50_orchestrateur_formateur

## Domaine

- `DOMAINE_CODE = 50_orchestrateur_formateur`
- `DOMAINE_LABEL = orchestrateur formateur`

---

## 1. Objet du backlog

Ce backlog borne les **actions à mener sur le seul domaine orchestrateur formateur** pour Hugo cœur.

Il ne constitue ni un plan global 2.0, ni une roadmap de refonte du moteur, ni une to-do list produit complète. Il sert à prioriser les actions utiles pour :
- réduire les ambiguïtés documentaires ;
- raccorder proprement doctrine 2.0 et réel audité ;
- expliciter les contrats minimums du domaine ;
- préparer, si nécessaire, des vérifications ciblées côté code ou runtime sans sur-réécrire l’existant.

---

## 2. Principes de priorisation

### 2.1 Règle générale

La priorisation suit l’ordre suivant :
1. **clarifier la documentation** ;
2. **stabiliser le vocabulaire** ;
3. **formaliser les contrats minimums** ;
4. **vérifier les zones réellement ambiguës** ;
5. **ne proposer des évolutions produit / backend que si un manque reste réel après clarification**.

### 2.2 Ce que ce backlog exclut

Ce backlog n’ouvre pas :
- une refonte générale de l’admin trainer ;
- une réarchitecture parallèle au backend Django existant ;
- une réécriture prompt-centric du domaine ;
- une extension Hugo & Cie ;
- une spécification UX complète non demandée ;
- une supposition d’état livré sur runtime distant non audité.

---

## 3. Priorité P0 — documentation de vérité

### Action P0.1 — Ajouter un bloc dédié “orchestrateur formateur” dans la spec de domaine

**Objectif**  
Créer ou renforcer un sous-bloc documentaire autonome décrivant le domaine avec la bonne structure : finalité, périmètre minimum, objets, validation humaine, articulation avec référentiel et orchestrateurs apprenant.

**Pourquoi maintenant**  
Le domaine existe doctrinalement et réellement, mais reste trop souvent dispersé entre base formateur, ingestion doc, trainer views et savoir gouverné.

**Livrable attendu**  
Un bloc documentaire court et stable contenant :
- définition du domaine ;
- périmètre minimum figé ;
- rôle de `TrainerKnowledgeItem` ;
- rappel de la validation humaine ;
- mention explicite que le workflow détaillé reste ouvert.

**Dépendances**  
Aucune.

**Statut recommandé**  
À lancer immédiatement.

---

### Action P0.2 — Ajouter une colonne “nom réel observé” dans les matrices concernées

**Objectif**  
Réduire les collisions entre vocabulaire doctrinal et noms réels observés dans Hugo développé.

**Pourquoi maintenant**  
Le glossaire recommande explicitement d’ajouter les noms réels observés dans les matrices backend et objets pour éviter les glissements de langage.

**Livrable attendu**  
Pour les matrices concernées, une colonne ou sous-colonne :
- nom doctrinal 2.0 ;
- nom réel observé ;
- statut d’alignement ;
- commentaire documentaire.

**Cibles minimales**  
- `TrainerKnowledgeItem` ;
- ingestion documentaire / `DocumentIngestor` ou équivalent ;
- vues / actions trainer ;
- objets référentiels liés ;
- endpoints ou surfaces si connus.

**Dépendances**  
P0.1 conseillé mais non obligatoire.

**Statut recommandé**  
Immédiat.

---

### Action P0.3 — Rendre explicite la règle “socle réel présent, workflow détaillé encore ouvert”

**Objectif**  
Éliminer les formulations documentaires extrêmes :
- soit “tout est déjà là” ;
- soit “tout reste à construire”.

**Pourquoi maintenant**  
C’est le principal risque de lecture sur ce domaine.

**Livrable attendu**  
Un encadré ou sous-bloc dans les docs de domaine avec trois niveaux :
- **réel observé** ;
- **cible 2.0** ;
- **ouvert cadré / A_VERIFIER**.

**Dépendances**  
Aucune.

**Statut recommandé**  
Immédiat.

---

## 4. Priorité P1 — contrats documentaires minimums

### Action P1.1 — Rédiger un pseudo-contrat léger de `TrainerKnowledgeItem`

**Objectif**  
Documenter l’objet pivot du domaine sans transformer la spec en schéma ORM exhaustif.

**Pourquoi maintenant**  
`TrainerKnowledgeItem` est l’un des alignements les plus solides entre doctrine 2.0 et réel audité, mais la documentation reste encore trop nominale.

**Livrable attendu**  
Une fiche pseudo-schéma orientée responsabilités indiquant au minimum :
- rôle métier ;
- producteur principal ;
- consommateurs principaux ;
- exposition front éventuelle ;
- provenance ;
- rattachements référentiels ;
- statuts minimaux ;
- usage documentaire / RAG.

**Contraintes**
- ne pas écrire un schéma SQL ;
- ne pas inventer des champs non confirmés ;
- distinguer clairement ce qui est doctrinal, observé, ou à confirmer.

**Dépendances**  
P0.2.

**Statut recommandé**  
Haute priorité.

---

### Action P1.2 — Formaliser la matrice “statuts x validation humaine”

**Objectif**  
Rendre beaucoup plus visible le fait que les statuts trainer sont gouvernés et non auto-promus.

**Pourquoi maintenant**  
La doctrine 2.0 est claire sur ce point, mais la documentation reste trop diffuse.

**Livrable attendu**  
Une mini-matrice indiquant au minimum :
- `declared` ;
- `derived_provisional` ;
- `validated_human` ;
- mode de production ;
- possibilité ou non d’auto-promotion ;
- besoin de validation humaine.

**Contraintes**
- ne pas inventer la répartition détaillée des rôles si elle n’est pas confirmée ;
- garder un niveau de précision compatible avec le corpus actuel.

**Dépendances**  
P1.1.

**Statut recommandé**  
Haute priorité.

---

### Action P1.3 — Documenter explicitement la subordination au référentiel métier

**Objectif**  
Empêcher toute lecture où la base formateur deviendrait la source primaire de vérité métier.

**Pourquoi maintenant**  
Le corpus 2.0 fixe clairement la centralité du référentiel et la subordination de la base formateur validée.

**Livrable attendu**  
Dans la doc du domaine, un sous-bloc d’articulation :
- référentiel métier ;
- base formateur gouvernée ;
- documentaire / RAG ;
- orchestrateurs apprenant.

**Dépendances**  
P0.1.

**Statut recommandé**  
Haute priorité.

---

## 5. Priorité P2 — clarifications d’usage aval

### Action P2.1 — Clarifier le niveau de preuve de consommation aval par les orchestrateurs apprenant

**Objectif**  
Dire précisément ce qui est doctrinalement prévu et ce qui est réellement confirmé.

**Pourquoi maintenant**  
Le risque actuel est de sur-affirmer l’usage runtime complet des `TrainerKnowledgeItem` par les régimes apprenant.

**Livrable attendu**  
Un sous-bloc documentaire distinguant :
- cible : objets consommables par les orchestrateurs apprenant ;
- réel : usage plausible / partiellement observé ;
- vérification restante : chaînage exact par service ou régime.

**Dépendances**  
P1.1.

**Statut recommandé**  
Moyenne priorité.

---

### Action P2.2 — Produire une note de raccord “base formateur vs RAG vs référentiel”

**Objectif**  
Désambiguïser trois couches souvent confondues dans les discussions.

**Pourquoi maintenant**  
Le domaine formateur touche directement au référentiel et au RAG, avec fort risque de mélange de responsabilités.

**Livrable attendu**  
Une note courte ou tableau à 3 colonnes :
- couche ;
- rôle ;
- ce qu’elle n’est pas.

**Exemple de structure**
- Référentiel métier : source primaire de structuration ;
- Base formateur : savoir gouverné validable ;
- Documentaire / RAG : renfort situé question-driven.

**Dépendances**  
P1.3.

**Statut recommandé**  
Moyenne priorité.

---

## 6. Priorité P3 — vérifications ciblées

### Action P3.1 — Vérifier le mapping réel des statuts trainer dans le code

**Objectif**  
Confirmer les noms de champs, valeurs et transitions réelles sans spéculation.

**Pourquoi maintenant**  
La doctrine des statuts est claire, mais le mapping précis code/doc n’est pas encore assez explicite.

**Livrable attendu**  
Une note d’audit très courte :
- modèle réel ;
- noms de statuts observés ;
- transitions réelles ;
- points d’écart éventuels avec la doctrine.

**Contraintes**
- audit ciblé ;
- pas de relecture générale du backend ;
- ne pas conclure au-delà du code effectivement relu.

**Dépendances**  
P1.2.

**Statut recommandé**  
Après stabilisation documentaire initiale.

---

### Action P3.2 — Vérifier la chaîne réelle “document -> explicitation -> item -> validation”

**Objectif**  
Passer d’une plausibilité forte à une preuve mieux bornée sur la chaîne métier.

**Pourquoi maintenant**  
Le domaine est déjà suffisamment cadré pour qu’une vérification fine soit utile, mais elle n’est pas prioritaire avant la clarification documentaire.

**Livrable attendu**  
Une note de vérification ciblée indiquant :
- étape observée ;
- service / vue / tâche impliqué ;
- preuve locale ;
- zone encore `A_VERIFIER`.

**Dépendances**  
P0 et P1 terminés de préférence.

**Statut recommandé**  
Moyenne / basse priorité.

---

### Action P3.3 — Vérifier le comportement sur runtime distant uniquement si nécessaire

**Objectif**  
Confirmer ou invalider les différences éventuelles entre local audité et runtime distant.

**Pourquoi maintenant**  
Seulement si une décision documentaire ou un chantier dépend réellement de cette réponse.

**Livrable attendu**  
Un court mémo :
- élément testé ;
- comportement local ;
- comportement distant ;
- flags / variantes ;
- conclusion `ALIGNE` ou `A_VERIFIER`.

**Contraintes**
- ne pas faire dépendre toute la doc du runtime distant ;
- ne pas traiter le distant comme source de vérité prioritaire sur le réel audité local.

**Dépendances**  
P3.1 ou P3.2 selon le besoin.

**Statut recommandé**  
Optionnel / conditionnel.

---

## 7. Priorité P4 — préparation de chantiers ultérieurs

### Action P4.1 — Préparer une cartographie des variables backend utiles aux futurs prompts formateur

**Objectif**  
Préparer le terrain sans re-centrer l’architecture sur les prompts.

**Pourquoi maintenant**  
Le complément 2.0 recommande de préparer la cartographie des variables backend stables avant publication détaillée des prompts.

**Livrable attendu**  
Une liste de familles de variables pertinentes, par exemple :
- variables documentaires ;
- variables de validation ;
- variables de rattachement référentiel ;
- variables d’état ou de progression utiles côté trainer ;
- métadonnées de provenance.

**Contraintes**
- les prompts restent consommateurs de variables backend ;
- aucune logique métier ne doit être redéfinie dans le prompt.

**Dépendances**  
P1.1 et P1.2.

**Statut recommandé**  
Basse priorité préparatoire.

---

### Action P4.2 — Préparer un futur prompt Cursor d’audit ciblé “orchestrateur formateur”

**Objectif**  
Rendre la prochaine passe d’audit technique plus précise et mieux ancrée dans le vocabulaire réel.

**Pourquoi maintenant**  
Une fois les décisions documentaires prises, il devient utile de formuler un prompt d’audit limité et non spéculatif.

**Livrable attendu**  
Un prompt Cursor borné à :
- modèles trainer ;
- statuts ;
- vues / endpoints trainer ;
- ingestion documentaire ;
- consommation aval éventuelle.

**Contraintes**
- pas d’audit full repo ;
- pas de mélange avec orchestrateur tuteur ;
- pas de mélange avec RAG global si non nécessaire.

**Dépendances**  
P0.2, P1.1, P3.1.

**Statut recommandé**  
Après consolidation documentaire.

---

## 8. Tableau de priorisation

| ID        | Action | Type | Priorité | Sortie attendue |
|-----------|--------|------|----------|-----------------|
| P0.1 | Bloc dédié “orchestrateur formateur” dans la doc | Documentation | P0 | Sous-bloc stable de domaine |
| P0.2 | Colonne “nom réel observé” dans les matrices | Documentation | P0 | Matrices enrichies |
| P0.3 | Bloc “réel / cible / ouvert” | Documentation | P0 | Encadré de vérité |
| P1.1 | Pseudo-contrat léger `TrainerKnowledgeItem` | Contrat documentaire | P1 | Fiche objet |
| P1.2 | Matrice statuts x validation humaine | Contrat documentaire | P1 | Tableau de statuts |
| P1.3 | Articulation référentiel / base formateur / RAG | Clarification doctrine | P1 | Sous-bloc d’articulation |
| P2.1 | Clarification de la consommation aval | Clarification | P2 | Note “usage aval” |
| P2.2 | Note “base formateur vs RAG vs référentiel” | Clarification | P2 | Tableau comparatif |
| P3.1 | Vérification ciblée des statuts dans le code | Audit ciblé | P3 | Mémo de vérification |
| P3.2 | Vérification chaîne document -> item -> validation | Audit ciblé | P3 | Mémo de chaîne métier |
| P3.3 | Vérification runtime distant si nécessaire | Audit ciblé | P3 | Mémo local vs distant |
| P4.1 | Cartographie des variables backend trainer | Préparation chantier | P4 | Liste de variables |
| P4.2 | Prompt Cursor d’audit ciblé | Préparation chantier | P4 | Prompt prêt à lancer |

---

## 9. Séquence d’exécution recommandée

### Phase 1 — stabilisation documentaire immédiate
1. P0.1  
2. P0.2  
3. P0.3

### Phase 2 — formalisation des contrats minimums
4. P1.1  
5. P1.2  
6. P1.3

### Phase 3 — clarification et vérification ciblée
7. P2.1  
8. P2.2  
9. P3.1  
10. P3.2

### Phase 4 — préparation de chantier ultérieur
11. P3.3 si besoin réel  
12. P4.1  
13. P4.2

---

## 10. Règles de non-régression pour exécuter ce backlog

Chaque action de ce backlog doit respecter les garde-fous suivants :

- ne jamais prendre la spec 2.0 pour une preuve de livraison ;
- ne jamais déduire tout le réel depuis le glossaire seul ;
- ne jamais écraser la doctrine avec les seuls noms du code ;
- ne jamais déclencher une refonte si le besoin est d’abord documentaire ;
- ne jamais faire de la base formateur une vérité autonome hors référentiel et validation humaine ;
- ne jamais réintroduire une architecture pilotée par prompt seul ;
- ne jamais mélanger Hugo cœur et Hugo & Cie ;
- ne jamais sur-affirmer le runtime distant sans preuve auditée.

---

## 11. Décision d’exécution recommandée

La trajectoire recommandée pour ce domaine est :

- **d’abord** consolider la documentation et les contrats minimums ;
- **ensuite** vérifier les points de mapping réellement ambigus dans le code ;
- **enfin** seulement préparer les chantiers d’implémentation ou les prompts Cursor ciblés.

La priorité immédiate n’est donc pas une refonte de l’orchestrateur formateur, mais une **mise au propre documentaire structurée, appuyée sur le réel audité et cohérente avec la cible 2.0**.

