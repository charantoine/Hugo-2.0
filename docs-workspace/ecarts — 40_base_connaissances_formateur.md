# 00_rapport_ecarts — 40_base_connaissances_formateur

> **Mise à jour post-cluster 16 — 2026-06-18** · **Cluster 16 :** pas d'impact direct. **PARTIEL+ local :** validate/reject/provisional (C15).  
> **Mise à jour juin 2026 — 30/06 :** fiabilité documentaire biblio formateur (`trainer_reliability` dans `document.meta`), réindex auto front après PATCH, tests `test_reliability_rag_and_reindex.py` + E2E TLIB-REL — **IMPLÉMENTÉ** local ; Encoors **A_VÉRIFIER**.  
> **Navigation shell prod 30/06 :** entrée TRAINER → `/app/trainer/knowledge` ; référentiels globaux `/app/trainer/referentials*` ; limite config groupe `/group/:id/referential` (tester) — `03` §2.3.

## Domaine

- `DOMAINE_CODE = 40_base_connaissances_formateur`
- `DOMAINE_LABEL = base de connaissances formateur`

---

## 1. Objet du rapport

Ce rapport qualifie, pour le seul domaine **base de connaissances formateur** de Hugo cœur, l’écart entre :
- la **cible 2.0** décrite par la spec canonique, son complément et la spec formateur/tuteur ;
- le **réel observable** décrit par les audits du workspace Hugo réel et les documents d’écarts doc/code/produit ;
- le **pont de vocabulaire** fourni par le glossaire d’alignement.

Ce document ne traite ni Hugo & Cie, ni l’ensemble des surfaces tuteur, ni la totalité du domaine RAG documentaire. Il porte sur la capacité de Hugo cœur à **faire émerger, structurer, valider et exploiter du savoir métier formateur** sous forme d’objets gouvernés, sans requalifier la cible comme déjà livrée.

---

## 2. Règles de lecture et de vérité appliquées sur ce domaine

### 2.1 Réel, cible, glossaire

Pour parler du **réel**, on s’appuie d’abord sur les audits du corpus Hugo réel, en particulier :
- `02_ETAT_MOTEUR_REEL.md` pour les objets backend, services, modèles et usages moteur ;
- `03_ETAT_PRODUIT_REEL.md` pour les surfaces réellement montrables côté produit ;
- `07_RUNTIME_DEMO_REFERENCE.md` et `09_PARCOURS_DEMO_ET_SCENARIOS.md` pour la démonstrabilité réelle ;
- `05_ECARTS_DOC_CODE_PRODUIT.md` pour les divergences confirmées entre docs, code local et runtime distant supposé.

Pour parler de la **cible**, on s’appuie sur :
- `spec_canonique_hugo_2_0.md` ;
- `complement_unique_specs_2_0`;
- `specs-formateur-tuteur-2.0.md`.

Le **glossaire d’alignement** ne prouve jamais à lui seul l’existence d’une implémentation complète. Il sert seulement à raccorder la doctrine 2.0 à des noms réels observés comme `TrainerKnowledgeItem`, vues trainer ou services d’ingestion documentaire.

### 2.2 Garde-fous méthodologiques

- La spec 2.0 décrit une **cible** ; elle ne démontre jamais qu’une base de connaissances formateur complète est déjà livrée.
- La présence d’un objet `TrainerKnowledgeItem`, de vues trainer, ou d’une ingestion documentaire ne suffit pas à prouver que l’**orchestrateur formateur 2.0** est complet de bout en bout.
- Toute affirmation dépendant du runtime distant, de flags, ou d’une variante Encoors non auditée localement reste marquée `A_VERIFIER`.
- La base formateur doit toujours être lue comme **subordonnée** au référentiel métier primaire, à la validation humaine et à la logique moteur backend ; elle n’est ni une vérité automatique, ni un moteur parallèle.

---

## 3. Périmètre cible 2.0 du domaine

### 3.1 Ce que la cible 2.0 fixe déjà

Dans Hugo 2.0, la **base de connaissances formateur** est un composant gouverné du cœur produit, distinct des régimes apprenant. La cible fixe déjà plusieurs points structurants :

- Hugo doit comporter une **base de connaissances formateur gouvernée**, construite par ingestion documentaire et explicitation dialogique, produisant des items structurés exploitables par les orchestrateurs apprenant.
- Les objets centraux sont des **`TrainerKnowledgeItem`** ou équivalents, avec statut explicite, type, contenu, rattachements référentiels, provenance et métadonnées d’usage documentaire ou RAG.
- L’**orchestrateur formateur** est un orchestrateur spécialisé distinct des régimes apprenant ; il ne s’agit pas d’un simple formulaire d’admin mais d’un dialogue d’élaboration du savoir métier.
- Les statuts minimaux sont doctrinalement fixés : **déclaré**, **dérivé provisoire**, **validé humainement** ; aucun item dérivé ne doit être auto-promu au statut validé.
- La base formateur peut enrichir les orchestrateurs apprenant via un **RAG gouverné** et des contenus validés, sans court-circuiter le référentiel primaire, la validation humaine ni le noyau P0.

### 3.2 Ce que la cible 2.0 laisse encore ouvert

La cible 2.0 est ferme sur la fonction du domaine, mais laisse encore plusieurs zones ouvertes :
- le **script conversationnel détaillé** de l’orchestrateur formateur ;
- l’ordre fin des sections, questions, reprises et relances ;
- la **répartition exacte** des responsabilités de validation entre formateur, coordinateur et autres rôles habilités ;
- le détail final des surfaces UI trainer et du workflow de validation ;
- le contrat backend précis entre `TrainerKnowledgeItem`, référentiel, documentaire/RAG et consommation par les orchestrateurs apprenant.

Ce domaine doit donc être lu comme **fortement cadré doctrinalement**, mais encore **partiellement sous-spécifié** dans ses modalités fines.

---

## 4. Photo du réel observé

### 4.1 Présence réelle d’objets et de surfaces trainer

Le corpus audité montre que Hugo cœur comporte bien une **présence réelle** de ce domaine :
- l’objet **`TrainerKnowledgeItem`** est explicitement mentionné dans le moteur audité ;
- des **vues trainer** existent ;
- des tests et surfaces associées sont mentionnés dans le corpus ;
- l’ingestion documentaire et l’explicitation côté trainer sont référencées dans la documentation d’audit et dans la spec de domaine comme points de contact avec le réel.

Le glossaire d’alignement classe d’ailleurs `TrainerKnowledgeItem` en **alignement excellent** entre cible et réel, ce qui constitue un signal fort de raccord doctrinal/vocabulaire, sans suffire à démontrer la complétude fonctionnelle du domaine.

### 4.2 Lien réel avec l’ingestion documentaire et le RAG

Le réel audité montre aussi un socle documentaire déjà en place :
- upload et indexation de documents via la bibliothèque ;
- ingestion documentaire existante ;
- sélection RAG backend effectivement présente dans le pipeline ;
- capacité à relier documents et usages trainer au moins de manière nominale et structurelle.

Cela confirme que la base formateur n’est pas pensée isolément : elle s’insère dans un système où référentiel, documentaire et RAG existent déjà côté backend. En revanche, le réel ne prouve pas encore à lui seul la totalité du **flux trainer -> item gouverné -> validation -> consommation apprenant** comme contrat stabilisé de bout en bout.

### 4.3 Ce que le réel ne prouve pas encore complètement

À partir du corpus mobilisé ici, plusieurs points restent insuffisamment prouvés :
- l’existence d’un **questionnaire dialogique formateur complet** déjà opérationnel au niveau 2.0 cible ;
- la profondeur réelle du workflow de validation humaine sur les items ;
- la finesse des statuts effectivement gérés dans toutes les variantes runtime ;
- le niveau exact de consommation de `TrainerKnowledgeItem` par les orchestrateurs apprenant en production ou en démo ;
- l’équivalence entre local audité et runtime distant Encoors.

Le réel audité montre donc une **base réelle partielle et crédible**, mais pas encore une preuve complète d’un orchestrateur formateur 2.0 pleinement stabilisé.

### 4.4 Exposition produit réellement montrable

Côté produit, ce domaine apparaît surtout comme une **capacité back-office / trainer**, et non comme un objet visible du parcours apprenant standard :
- les surfaces formateur sont mentionnées ;
- les statuts et vues trainer sont prévus doctrinalement et partiellement raccordés au réel ;
- la démonstration produit apprenant ne met pas la base formateur au centre du parcours.

Autrement dit, le réel observable suggère un domaine davantage **outillé côté formateur/backend** que pleinement exposé comme expérience produit mature, montrable et complète dans la démo apprenant.

---

## 5. Analyse narrative des écarts

### 5.1 Zone de bon alignement

Le domaine présente un **alignement doctrinal de fond plutôt bon**.

La cible 2.0 veut une base de connaissances formateur gouvernée, alimentée par documents et explicitation, structurée en `TrainerKnowledgeItem`, subordonnée au référentiel primaire et à la validation humaine. Le réel audité montre justement la présence de `TrainerKnowledgeItem`, de vues trainer et d’un socle documentaire backend déjà existant.

Cela signifie que la spec 2.0 ne part pas de zéro sur ce domaine. Elle formalise et clarifie une responsabilité métier dont une partie existe déjà dans Hugo cœur.

### 5.2 Écart principal : complétude de l’orchestrateur formateur

L’écart majeur n’est pas l’absence pure du domaine, mais la **distance entre présence réelle d’objets/outillage** et **orchestrateur formateur cible pleinement spécifié et démontré**.

La cible 2.0 décrit un dialogue d’élaboration, une ingestion gouvernée, une structuration d’items, des statuts nets, une validation humaine obligatoire et une exploitation apprenant. Le réel montre des briques importantes de ce domaine, mais le corpus mobilisé ici ne suffit pas à prouver :
- la chorégraphie complète du dialogue formateur ;
- la chaîne UI de validation ;
- le rôle exact de chaque acteur habilité ;
- l’intégration runtime bout-en-bout dans tous les usages apprenant.

L’écart est donc surtout un écart de **formalisation, de bornage et de preuve de complétude**, plus qu’un écart d’existence brute.

### 5.3 Écart important : vocabulaire et contrats encore partiellement stabilisés

Le glossaire indique un **très bon alignement** sur `TrainerKnowledgeItem`, mais aussi un besoin général de raccord documentaire entre doctrine 2.0 et noms réels observés.

Sur ce domaine, cela veut dire :
- garder les noms doctrinaux 2.0 pour raisonner juste ;
- faire apparaître les noms réels observés dans le code et les audits ;
- ne pas laisser croire qu’un objet bien nommé dans le réel suffit à figer tout son contrat métier.

Le besoin principal n’est donc pas de renommer brutalement le code, mais de **rendre explicite le mapping** entre doctrine, objets réels et niveau de stabilisation effectif.

### 5.4 Écart fort : validation humaine et rôles encore partiellement ouverts

La cible 2.0 est très claire : **aucun auto-upgrade** d’un item dérivé vers un item validé humainement, et la base formateur ne remplace jamais la vérité réglementaire primaire.

Le réel semble compatible avec cette doctrine, mais le corpus utilisé ici ne permet pas encore de figer complètement :
- qui valide exactement ;
- à quel niveau produit ;
- avec quels écrans, transitions et droits ;
- avec quel lien explicite entre statuts réels et rôles métier.

Cet écart n’est pas une contradiction doctrinale ; c’est une **zone ouverte à contractualiser proprement**.

### 5.5 Écart avec la démonstrabilité produit

Le domaine est doctrinalement important, mais **faiblement démontré** dans les parcours apprenant standards.

Autrement dit, il faut éviter deux erreurs opposées :
- sous-estimer le domaine en disant “rien n’existe” ;
- sur-vendre le domaine comme si l’orchestrateur formateur 2.0 complet était déjà visible, stabilisé et démontré en production.

La position juste, au vu du corpus, est : **socle réel présent, valeur métier nette, démonstration produit encore partielle**.

### 5.6 Lien avec le reste de Hugo cœur

La base de connaissances formateur ne doit jamais être lue comme une architecture indépendante. Dans la cible 2.0 comme dans le réel partiellement observé, elle reste :
- backend-first ;
- subordonnée au référentiel primaire ;
- consommée via des services gouvernés ;
- compatible avec un moteur tutoriel piloté par état, et non par prompts seuls.

C’est important pour éviter une mauvaise lecture du chantier : ce domaine appelle surtout des **contrats clarifiés**, des **mappings documentaires propres** et des **compléments backend additifs**, pas une refonte du moteur principal.

---

## 6. Lecture de synthèse par niveau de vérité

### 6.1 Implémenté / observable

À ce stade, le corpus permet d’affirmer comme **réellement observables** :
- la présence de l’objet **`TrainerKnowledgeItem`** ;
- l’existence de **vues trainer** ;
- un lien réel avec l’ingestion documentaire ;
- l’existence d’un socle documentaire/RAG backend dans lequel cette base peut s’insérer ;
- un alignement de vocabulaire fort entre cible et réel sur cet objet central.

### 6.2 Cible 2.0

Relèvent clairement de la **cible 2.0** :
- un orchestrateur formateur dialogique pleinement explicité ;
- des statuts gouvernés stabilisés à l’échelle produit ;
- une matrice claire des rôles de validation ;
- un contrat backend propre entre documents source, explicitation, `TrainerKnowledgeItem`, validation humaine et consommation par les orchestrateurs apprenant ;
- une UI trainer plus précisément contractualisée.

### 6.3 Écarts confirmés

Les **écarts confirmés** sur ce domaine sont surtout :
- écart entre présence réelle d’objets/outillage et preuve d’un orchestrateur complet de bout en bout ;
- manque de formalisation documentaire propre sur les rôles, statuts et flux ;
- démonstrabilité produit encore partielle ;
- besoin de raccord doctrine/code plus explicite, sans surinterpréter les objets observés.

### 6.4 À vérifier

Restent explicitement `A_VERIFIER` :
- le niveau exact de consommation runtime de `TrainerKnowledgeItem` dans toutes les variantes apprenant ;
- les différences éventuelles entre local audité et runtime distant Encoors ;
- les flags ou variantes pouvant modifier le workflow trainer ;
- la profondeur réelle de validation humaine dans les variantes runtime non observées ici ;
- l’existence de surfaces trainer plus riches côté distant ou branches non auditées.

---

## 7. Garde-fous pour la suite documentaire et technique

### 7.1 Ce qu’il ne faut pas faire

Pour ce domaine, il faut éviter :
1. de lire la spec 2.0 comme preuve qu’un orchestrateur formateur complet est déjà livré ;
2. de prendre la seule présence de `TrainerKnowledgeItem` comme preuve d’un flux complet documents -> dialogue -> validation -> consommation apprenant ;
3. de transformer la base formateur en source primaire de vérité métier ;
4. de dériver vers une architecture parallèle, prompt-driven ou front-driven.

### 7.2 Ce qu’il faut privilégier

La bonne trajectoire pour ce domaine est :
- clarifier les **contrats backend** ;
- stabiliser le **vocabulaire** doctrine / code ;
- expliciter les **statuts** et la **validation humaine** ;
- documenter honnêtement le niveau réel déjà couvert ;
- compléter de manière **additive** les chaînons encore sous-spécifiés, sans refonte inutile du moteur.

---

## 8. Conclusion opérationnelle du domaine

Le domaine `40_base_connaissances_formateur` est un domaine **réellement amorcé**, **doctrinalement bien cadré**, mais **pas encore complètement démontré** comme orchestrateur 2.0 stabilisé de bout en bout.

Le réel audité montre des appuis solides : `TrainerKnowledgeItem`, vues trainer, ingestion documentaire, socle backend documentaire/RAG. La cible 2.0 ne doit donc pas être lue comme une réinvention ex nihilo, mais comme un travail de **consolidation** : formaliser les contrats, clarifier les statuts, borner la validation humaine, raccorder proprement le vocabulaire et distinguer explicitement ce qui est déjà observable de ce qui reste à prouver ou à spécifier.

# 01_matrice_ecarts — 40_base_connaissances_formateur

## Domaine

- `DOMAINE_CODE = 40_base_connaissances_formateur`
- `DOMAINE_LABEL = base de connaissances formateur`

---

## 1. Légende des statuts

- `ALIGNE` : cible 2.0 et réel sont cohérents, vocabulaire déjà raccord ou facilement raccordable.
- `ALIGNE_DOC_PARTIEL` : fond aligné, mais la documentation doit mieux expliciter le mapping ou le périmètre.
- `RENOMMER_DANS_DOC` : la doc 2.0 doit faire apparaître les noms réels observés sans changer la doctrine.
- `AMBIGU` : le corpus actuel montre un début d’alignement mais le mapping ou le périmètre ne sont pas assez nets.
- `A_VERIFIER` : le corpus utilisé (audits locaux, doc) ne permet pas de conclure sur le réel ou sur le runtime distant.
- `ABSENT / NOUVEAU_CONTRAT` : aucune implémentation probante observée, alors que la cible 2.0 fixe une responsabilité claire.

---

## 2. Objets de base de connaissances formateur

### 2.1 Objets centraux

| Objet / notion 2.0 | Noms réels observés | Description (cible vs réel) | Statut | Commentaire d’écart |
|--------------------|---------------------|-----------------------------|--------|---------------------|
| `TrainerKnowledgeItem` (item de savoir métier gouverné) | `TrainerKnowledgeItem` | Objet central de la base formateur, structurant des contenus, rattaché au référentiel, avec statuts gouvernés. Le réel montre la présence de ce modèle et de vues trainer associées. | ALIGNE | Très bon alignement doctrinal et vocabulaire ; la doc 2.0 doit continuer à s’appuyer sur ce nom comme pivot. |
| Statuts de connaissance (`declared`, `derived_provisional`, `validated_trainer`) | Champs/enum de statut dans `TrainerKnowledgeItem` (à confirmer dans le code) | La cible impose au minimum ces trois statuts et interdit tout auto-upgrade vers un statut validé. Le réel semble compatible mais la mise en œuvre exacte des statuts n’est pas entièrement documentée. | ALIGNE_DOC_PARTIEL | Les règles de validation sont claires doctrinalement ; la doc doit expliciter ce qui est déjà implémenté et ce qui reste à formaliser. |
| Base de connaissances formateur gouvernée | `TrainerKnowledgeItem` + vues trainer + stockage associé | La cible décrit une base gouvernée alimentée par documents et explicitation, reliée au référentiel et au RAG, subordonnée à la validation humaine. Le réel montre une base structurée mais sans preuve complète de tout le workflow cible. | ALIGNE_DOC_PARTIEL | Responsabilité métier déjà couverte en partie ; la doc doit mieux borner la complétude et les limites actuelles. |

### 2.2 Liens avec référentiel, mémoire et documentaire

| Objet / notion 2.0 | Noms réels observés | Description (cible vs réel) | Statut | Commentaire d’écart |
|--------------------|---------------------|-----------------------------|--------|---------------------|
| Lien au référentiel métier (ancrage des items) | `referentials` app, champs de rattachement au référentiel (à confirmer) | La cible impose que les items soient rattachés au référentiel (compétences, situations, tâches). Le réel dispose d’une app `referentials` et d’objets TrainerKnowledgeItem, mais le mapping exact entre les deux n’est pas complètement documenté. | AMBIGU | L’alignement conceptuel est clair, mais les liens concrets (modèles, clés, UI) restent à qualifier précisément. |
| Interaction base formateur ↔ mémoire gouvernée | `LearnerThemeMemory`, `memory-summary` (coté apprenant) | La cible indique que la base formateur interagit avec mémoire gouvernée et exports, mais sans que l’orchestrateur formateur manipule directement la mémoire apprenant. Le réel montre la mémoire gouvernée, mais pas encore un flux explicite entre base formateur et mémoire. | ABSENT / NOUVEAU_CONTRAT | La responsabilité est ciblée mais le contrat explicite manque ; à formaliser comme contrat additif sans complexifier le moteur existant. |
| Interaction base formateur ↔ documentaire/RAG gouverné | `library`, `ragsupport.py`, champs d’usage RAG dans `TrainerKnowledgeItem` (à confirmer) | La cible prévoit une base formateur alimentant un RAG gouverné. Le réel a un socle RAG et des items trainer, mais le couplage exact entre items validés et corpus RAG consommé n’est pas démontré. | AMBIGU | Bon alignement de fond, mais le niveau réel de consommation des items trainer dans le RAG doit être clarifié. |

---

## 3. Services et orchestrateur formateur

### 3.1 Services backend

| Service / responsabilité 2.0 | Noms réels observés | Description (cible vs réel) | Statut | Commentaire d’écart |
|-----------------------------|---------------------|-----------------------------|--------|---------------------|
| `DocumentIngestor` / `documentingestor` (ingestion documentaire formateur) | `documentingestor.py` ou équivalent (mentionné dans la spec formateur) | La cible fixe un service transformant documents + réponses formateur en `TrainerKnowledgeItem` dérivés. Le réel semble disposer d’un service d’ingestion documentaire, mais son périmètre exact formateur vs apprenant n’est pas pleinement décrit dans les audits. | ALIGNE_DOC_PARTIEL | La responsabilité backend existe ; la doc doit préciser le périmètre formateur et les limites actuelles. |
| Orchestrateur formateur (service de dialogue guidé) | Orchestrateur formateur (mentionné dans la spec), vues trainer | La cible décrit un orchestrateur dialogique dédié. Le réel montre des vues trainer et des objets, mais ne prouve pas encore un orchestrateur complet au niveau de détail 2.0 (séquences, relances, gestion des impasses). | AMBIGU | Concept et présence partielle réelles, mais l’orchestrateur complet reste à documenter et/ou compléter. |
| Service de validation des items (workflow d’acceptation) | Vues de validation dans l’interface formateur (à confirmer) | La cible impose une validation humaine explicite pour les items dérivés. Le réel semble prévoir des statuts et des écrans de validation, mais la matrice des rôles et actions n’est pas entièrement stabilisée dans la doc. | ALIGNE_DOC_PARTIEL | Alignement doctrinal net ; la doc doit détailler les rôles, transitions et garde-fous, sans forcer le code. |

### 3.2 Flux et chorégraphie d’orchestrateur

| Flux 2.0 | Noms réels observés | Description (cible vs réel) | Statut | Commentaire d’écart |
|----------|---------------------|-----------------------------|--------|---------------------|
| Dialogue d’élaboration (questionnaire formateur guidé) | Vues trainer question/réponse (à confirmer) | La cible décrit un questionnaire dialogique qui structure le savoir formateur. Le réel montre l’existence d’un orchestrateur et de vues, mais le script complet (sections, relances, reprises) n’est pas documenté. | ABSENT / NOUVEAU_CONTRAT | La responsabilité est claire mais le contrat concret reste à écrire ; chantier de spec + implé additif. |
| Passage documents → items dérivés | `documentingestor` + `TrainerKnowledgeItem` | La cible impose la transformation des documents en items structurés. Le réel a les briques principales, mais le flux détaillé et ses garde-fous ne sont pas visibles dans l’audit. | ALIGNE_DOC_PARTIEL | Les objets sont en place ; besoin d’un contrat explicite et d’une doc de flux. |
| Passage items dérivés → items validés | Vues de validation, champs statut | La cible interdit toute auto-promotion, impose la validation humaine. Le réel semble compatible mais la chaîne complète (rôles, écrans, logs) n’est pas démontrée dans la doc actuelle. | AMBIGU | Aligner la doc sur les garde-fous 2.0, vérifier le code avant d’affirmer la complétude. |

---

## 4. Rôles, statuts et validation humaine

| Élément 2.0 | Noms réels observés | Description (cible vs réel) | Statut | Commentaire d’écart |
|-------------|---------------------|-----------------------------|--------|---------------------|
| Rôle FORMATEUR (TRAINER) | Rôle formateur dans l’interface trainer | La cible donne au formateur le rôle principal de producteur/valideur de savoir métier. Le réel dispose d’une surface formateur avec upload, création, validation. | ALIGNE_DOC_PARTIEL | Il faut fixer plus clairement dans la doc le périmètre exact de ce rôle vs d’autres rôles habilités. |
| Rôle COORDO / ORGADMIN dans la validation d’items | Rôles coordo/orgadmin (mentionnés globalement) | La cible laisse ouvert qui, outre le formateur, peut valider. Le réel ne tranche pas nettement dans les audits actuels. | ABSENT / NOUVEAU_CONTRAT | Nécessité d’un contrat produit/orga explicite ; ne pas inférer sans spec complémentaire. |
| Non-auto-upgrade du provisoire vers le validé | Règle globale “pas de promotion auto” dans la canonique | La cible interdit l’auto-upgrade. Le réel n’est pas décrit comme contredisant cette règle, mais le workflow exact n’est pas vérifié. | A_VERIFIER | Il faut un audit ciblé pour confirmer que le code n’introduit pas d’auto-promotion implicite. |

---

## 5. Surfaces UI formateur et exposition produit

| Élément UI 2.0 | Noms réels observés | Description (cible vs réel) | Statut | Commentaire d’écart |
|----------------|---------------------|-----------------------------|--------|---------------------|
| Liste d’items de connaissance avec statuts | Vues trainer listant `TrainerKnowledgeItem` (à confirmer) | La cible prévoit des vues listant les items, leurs statuts, leurs liens référentiels. Le réel semble disposer de vues trainer, mais le niveau de détail n’est pas entièrement décrit dans les audits. | ALIGNE_DOC_PARTIEL | Surfaces plausibles ; la doc doit aligner vocabulaire et périmètre sans sur-vendre. |
| Créer / modifier des items | Actions CRUD sur `TrainerKnowledgeItem` | La cible prévoit création, édition, correction. Le réel semble permettre au moins la gestion d’items via l’interface trainer. | ALIGNE_DOC_PARTIEL | Actionnalité alignée de fond ; l’UX et les garde-fous doivent être précisés dans la doc. |
| Workflow de validation (tableau, filtres, statuts) | Vues de validation (à confirmer) | La cible décrit un tableau de validation. Le réel n’est pas documenté assez finement pour affirmer l’existence d’un workflow complet tel que décrit. | AMBIGU | Besoin de spécifier et/ou vérifier l’implémentation avant de figer la doc. |
| Visualisation d’impact sur les parcours apprenants (usage des items) | Potentielles vues d’usage/statistiques | La cible évoque des usages possibles dans exports et vues formateur, mais sans les figer. Le réel n’apporte pas de preuve claire de cette visualisation. | ABSENT / NOUVEAU_CONTRAT | Idée cible à garder, mais à écrire comme capacité future, pas comme déjà livrée. |

---

## 6. Intégration avec les orchestrateurs apprenant

| Élément 2.0 | Noms réels observés | Description (cible vs réel) | Statut | Commentaire d’écart |
|-------------|---------------------|-----------------------------|--------|---------------------|
| Consommation d’items validés par le régime révision de savoirs | RAG backend + logique de recours au contenu | La cible prévoit que les orchestrateurs apprenant s’appuient sur des contenus formateur validés. Le réel montre un RAG documentaire et des items trainer, mais ne détaille pas la sélection fine de ces items dans tous les régimes. | AMBIGU | Concept cohérent ; la granularité réelle de consommation par régime reste à préciser. |
| Effets sur feedbacks apprenants (critères, erreurs typiques) | Potentielles métadonnées dans `TrainerKnowledgeItem` | La cible décrit des objets incluant critères, erreurs fréquentes, raisonnements attendus/à éviter. Le réel dispose de l’objet, mais les champs et leur exploitation exacte ne sont pas détaillés. | ALIGNE_DOC_PARTIEL | La responsabilité est bien posée ; la doc et éventuellement le code doivent préciser les champs réellement utilisés. |
| Non-substitution au référentiel primaire | Référentiel existant + base formateur | La cible insiste sur la subordination de la base formateur au référentiel métier. Le réel dispose d’un référentiel et d’une base formateur ; aucun signal d’inversion de hiérarchie n’apparaît dans les audits. | ALIGNE | Alignement doctrinal fort ; à rappeler clairement dans la doc pour éviter toute dérive. |

---

## 7. Zones explicitement `A_VERIFIER`

| Élément | Description | Motif `A_VERIFIER` |
|--------|-------------|--------------------|
| Usage réel de `TrainerKnowledgeItem` dans le pipeline apprenant | Niveau exact d’injection dans les contextes LLM, par régime conversationnel. | Non démontré par le corpus audité seul ; nécessite inspection ciblée du code et des traces. |
| Divergences éventuelles entre runtime local et Encoors pour l’orchestrateur formateur | Variantes de flags, de surfaces ou de workflows côté distant. | L’audit ne couvre pas le runtime distant ; pas de conclusion possible sans vérification supplémentaire. |
| Workflow complet de validation (statuts, rôles, logs) | Chaîne fine `declared` → `derived_provisional` → `validated_trainer`. | Les règles doctrinales sont claires ; l’implémentation détaillée n’est pas prouvée à ce stade. |
| Visualisation produit de l’impact des items formateur sur les parcours | Vues d’usage, stats, exports outillant le formateur. | Idée présente dans les specs, mais pas démontrée dans le réel audité. |

---

## 8. Synthèse matricielle

- Le socle du domaine (présence de `TrainerKnowledgeItem`, base formateur, vues trainer, liens avec le documentaire) est **globalement ALIGNE ou ALIGNE_DOC_PARTIEL**.
- Les flux d’orchestrateur formateur, le workflow complet de validation et certains liens avec mémoire/RAG sont **AMBIGUS ou ABSENT / NOUVEAU_CONTRAT** et doivent être traités comme chantiers à contractualiser, pas comme refonte globale.
- Plusieurs points critiques (usage runtime effectif des items, différences local/distant, workflow de validation complet) restent explicitement **`A_VERIFIER`** avant toute affirmation forte dans la doc ou le discours produit.


# 02_decisions_documentaires — 40_base_connaissances_formateur

## Domaine

- `DOMAINE_CODE = 40_base_connaissances_formateur`
- `DOMAINE_LABEL = base de connaissances formateur`

---

## 1. Statut et objet du document

Ce document fixe les **décisions documentaires** à appliquer pour le domaine **base de connaissances formateur**, à partir :
- de la cible 2.0 ;
- du réel audité ;
- de la matrice d’écarts de ce domaine ;
- du glossaire d’alignement comme pont de vocabulaire.

Il ne décide ni d’une refonte code globale, ni d’un chantier Hugo & Cie, ni d’une réécriture complète des specs 2.0. Il sert à documenter proprement ce qui doit être :
- **conservé** ;
- **clarifié** ;
- **renommé dans la doc** ;
- **laissé ouvert / à vérifier** ;
- **introduit comme contrat cible encore non stabilisé dans le réel**.

---

## 2. Décisions de cadrage

### DCD-01 — Conserver la doctrine 2.0 comme structure de référence du domaine

La documentation du domaine continue à décrire la **base de connaissances formateur** comme un composant gouverné de Hugo cœur, distinct des régimes apprenant, subordonné au référentiel primaire, à la validation humaine et à la logique backend pilotée par état.

**Conséquence documentaire :**
- on conserve les notions doctrinales `base de connaissances formateur`, `orchestrateur formateur`, `TrainerKnowledgeItem`, `validation humaine`, `RAG gouverné` ;
- on n’écrase pas cette structure avec les seuls noms de vues, de services ou de modèles observés dans le réel.

### DCD-02 — Ne jamais présenter la cible 2.0 comme déjà livrée

Tout passage décrivant :
- un questionnaire dialogique complet ;
- un workflow UI complet de validation ;
- une chaîne runtime trainer -> item -> validation -> consommation apprenant ;
doit être rédigé comme **cible 2.0** ou **contrat en cours de stabilisation**, sauf preuve explicite tirée du corpus audité.

**Conséquence documentaire :**
- bannir les formulations de type “Hugo fait déjà…” lorsqu’elles ne sont pas prouvées par les audits ;
- préférer “la cible 2.0 fixe…”, “le réel montre…”, “reste à confirmer…”.

---

## 3. Décisions de vocabulaire

### DCD-03 — Conserver `TrainerKnowledgeItem` comme pivot nominal du domaine

`TrainerKnowledgeItem` devient le **nom pivot documentaire** pour raccorder cible et réel sur ce domaine.

**Conséquence documentaire :**
- la doc 2.0 conserve `TrainerKnowledgeItem` comme objet central ;
- les futurs documents de chantier ne cherchent pas à le remplacer par une abstraction plus floue ;
- les annexes doivent faire apparaître clairement qu’il s’agit aussi d’un nom **réel observé** dans Hugo développé.

### DCD-04 — Ajouter systématiquement les noms réels observés dans les annexes techniques

La doc de domaine doit faire apparaître, lorsque pertinent :
- `TrainerKnowledgeItem` ;
- vues trainer ;
- `documentingestor.py` ou équivalent ;
- liens documentaires / RAG réellement observés ;
comme **noms réels observés**, à côté du vocabulaire doctrinal.

**Conséquence documentaire :**
- ajout d’un sous-bloc “nom réel observé” ou d’une colonne dédiée dans les futures matrices/specs ;
- maintien de la séparation entre **nom conceptuel** et **nom concret de code**.

### DCD-05 — Ne pas déduire un contrat complet à partir du seul nom de l’objet

Même si `TrainerKnowledgeItem` est réel et bien aligné, la documentation ne doit pas laisser entendre que :
- tous les statuts sont stabilisés ;
- tout le workflow trainer est complet ;
- toute la consommation apprenant est prouvée ;
simplement parce que l’objet existe.

**Conséquence documentaire :**
- chaque fois qu’un objet réel est cité, préciser aussi son **niveau de stabilisation fonctionnelle** : observé, partiellement documenté, ou à vérifier.

---

## 4. Décisions sur le périmètre fonctionnel à décrire

### DCD-06 — Décrire le domaine comme une capacité de structuration du savoir métier, pas comme un simple admin CRUD

L’orchestrateur formateur doit rester documenté comme une capacité visant à :
- faire expliciter du savoir métier ;
- transformer documents et réponses en items structurés ;
- produire des objets exploitables par Hugo ;
- soumettre ces objets à validation humaine.

**Conséquence documentaire :**
- éviter de réduire le domaine à “écran d’upload + formulaire d’édition” ;
- éviter aussi l’excès inverse qui consisterait à prétendre qu’un vrai dialogue complet est déjà démontré dans le réel.

### DCD-07 — Décrire explicitement la subordination au référentiel primaire

La documentation doit rappeler à chaque niveau pertinent que la base formateur :
- n’est pas la source primaire de vérité réglementaire ;
- reste subordonnée au référentiel métier ;
- enrichit Hugo sans remplacer la hiérarchie référentiel -> documentaire -> RAG gouverné.

**Conséquence documentaire :**
- ajouter cette règle dans la section “garde-fous” du domaine ;
- la rappeler dans les schémas de flux et dans les descriptions d’objets.

### DCD-08 — Documenter la validation humaine comme invariant non négociable

La règle “aucun auto-upgrade du provisoire vers le validé humainement” doit être écrite comme un **invariant de domaine**, pas comme une simple préférence UX ou un détail d’implémentation.

**Conséquence documentaire :**
- insérer un encadré ou une règle explicite sur les statuts ;
- distinguer systématiquement `declared`, `derived_provisional`, `validated_trainer` ;
- préciser que le passage au validé suppose un acte humain explicite.

---

## 5. Décisions sur les zones ouvertes et ambiguës

### DCD-09 — Marquer explicitement le workflow détaillé de l’orchestrateur formateur comme “ouvert cadré”

Le script conversationnel détaillé, l’ordre exact des questions, les relances et la chorégraphie UI fine ne doivent pas être documentés comme stabilisés dans le réel ni totalement figés dans la canonique actuelle.

**Conséquence documentaire :**
- créer une sous-section “ce qui est fixé / ce qui reste à spécifier” ;
- classer ce point comme **contrat cible encore à détailler**, pas comme absence pure.

### DCD-10 — Laisser ouverte la matrice exacte des rôles de validation

La documentation doit indiquer que la validation humaine est requise, mais que la répartition exacte entre :
- formateur ;
- coordinateur ;
- org admin ;
reste encore à préciser au niveau produit.

**Conséquence documentaire :**
- éviter d’affirmer sans preuve que seul le formateur valide ;
- éviter aussi d’inventer un workflow multi-rôles détaillé non encore stabilisé.

### DCD-11 — Marquer comme `A_VERIFIER` l’usage runtime effectif des items trainer dans les orchestrateurs apprenant

La doc ne doit pas affirmer que les `TrainerKnowledgeItem` sont déjà consommés de manière complète, stable et traçable dans tous les régimes apprenant tant que cela n’est pas confirmé par audit ciblé du code ou du runtime.

**Conséquence documentaire :**
- employer une formulation du type : “la cible prévoit cette consommation ; le réel montre des briques compatibles ; le niveau exact d’usage runtime reste à vérifier”.

### DCD-12 — Marquer comme `A_VERIFIER` toute divergence local / Encoors sur ce domaine

Tout comportement attribué au runtime distant, aux flags ou à des variantes de surfaces trainer non auditées localement doit rester explicitement marqué `A_VERIFIER`.

**Conséquence documentaire :**
- ne pas faire de la démo distante une preuve d’état de livraison de ce domaine ;
- ne pas extrapoler depuis le local vers Encoors ni l’inverse.

---

## 6. Décisions de structure pour les futures specs de domaine

### DCD-13 — Introduire un pseudo-contrat d’objet pour `TrainerKnowledgeItem`

Les futures versions de la doc de domaine doivent comporter un **pseudo-contrat léger** pour `TrainerKnowledgeItem`, avec au minimum :
- rôle ;
- producteur principal ;
- consommateurs principaux ;
- statuts ;
- rattachement référentiel ;
- provenance ;
- exposition front éventuelle.

**Conséquence documentaire :**
- ne pas produire un schéma ORM exhaustif ;
- produire un contrat orienté responsabilités, cohérent avec la méthode 2.0.

### DCD-14 — Séparer explicitement quatre niveaux dans la rédaction

La doc de domaine doit distinguer :
1. **objet doctrinal cible** ;
2. **nom réel observé** ;
3. **niveau de preuve dans le réel** ;
4. **action documentaire ou chantier restant**.

**Conséquence documentaire :**
- cette structure devient la base des futures matrices, décisions et prompts Cursor de ce domaine ;
- elle évite les glissements entre doctrine, audit et code réel.

### DCD-15 — Ajouter un sous-bloc “consommation apprenant” sans la sur-spécifier

Il faut documenter que la base formateur a vocation à enrichir :
- la révision de savoirs ;
- certains feedbacks ;
- certains appuis documentaires / RAG ;
mais sans prétendre que la logique exacte de consommation est déjà stabilisée.

**Conséquence documentaire :**
- conserver un bloc fonctionnel clair sur l’impact apprenant ;
- laisser le détail du mapping par régime à un futur document de contrat backend.

---

## 7. Formulations à utiliser / à éviter

### DCD-16 — Formulations recommandées

Utiliser préférentiellement des formulations comme :
- “La cible 2.0 fixe…”
- “Le réel audité montre…”
- “Le glossaire aligne le vocabulaire sans prouver à lui seul l’implémentation…”
- “Le niveau exact de consommation runtime reste à vérifier…”
- “Le workflow détaillé reste ouvert / sous-spécifié à ce stade…”

### DCD-17 — Formulations interdites ou à éviter

Éviter les formulations suivantes :
- “L’orchestrateur formateur est déjà entièrement livré.”
- “TrainerKnowledgeItem prouve que toute la base formateur 2.0 est en place.”
- “Le formateur valide seul tous les items.”
- “Le runtime distant confirme la complétude du domaine.”
- “La base formateur remplace le référentiel comme source principale.”

---

## 8. Synthèse des décisions à appliquer

### À conserver tel quel

- La base formateur comme composant gouverné de Hugo cœur.
- `TrainerKnowledgeItem` comme objet pivot du domaine.
- La validation humaine obligatoire et la non-auto-promotion.
- La subordination au référentiel primaire.

### À clarifier dans la doc

- Le niveau réel de complétude du workflow trainer.
- Le lien entre objets trainer, ingestion documentaire et RAG gouverné.
- La répartition exacte des rôles de validation.
- Le niveau réel de consommation apprenant des items validés.

### À marquer explicitement comme ouvert ou `A_VERIFIER`

- Le script dialogique détaillé.
- Les différences local / Encoors.
- La profondeur réelle du workflow de validation dans les variantes runtime.
- Le détail des vues d’impact et de consommation apprenant.

### À introduire comme contrat documentaire additif

- Un pseudo-contrat d’objet `TrainerKnowledgeItem`.
- Un sous-bloc “nom réel observé / niveau de preuve / action à mener”.
- Un futur contrat backend “base formateur -> consommation apprenant”, sans imposer de refonte moteur.

# 03_backlog_actions — 40_base_connaissances_formateur

## Domaine

- `DOMAINE_CODE = 40_base_connaissances_formateur`
- `DOMAINE_LABEL = base de connaissances formateur`

---

## 1. Règles de backlog

Ce backlog est limité au domaine **base de connaissances formateur** de Hugo cœur.

Il ne couvre pas :
- une refonte générale du moteur ;
- les sujets Hugo & Cie ;
- une réécriture globale des specs 2.0 ;
- des travaux non bornés sur l’admin complète, le front global ou l’infra générale.

Les actions proposées respectent les garde-fous suivants :
- priorité à l’alignement documentaire et contractuel ;
- pas de déduction du réel depuis la seule spec ;
- pas de refonte si le réel couvre déjà la responsabilité métier ;
- toute dépendance au runtime distant ou à des variantes non auditées reste `A_VERIFIER`.

---

## 2. Priorités retenues

### P1 — Clarifier ce qui existe déjà réellement

Objectif : éviter les glissements entre présence nominale de briques trainer et affirmation d’une chaîne 2.0 complète.

### P2 — Stabiliser le contrat documentaire minimal du domaine

Objectif : rendre lisible, pour CTO et prompts Cursor, ce qui est doctrinalement fixé, ce qui est observé, et ce qui reste ouvert.

### P3 — Préparer les vérifications ciblées restantes

Objectif : borner les points `A_VERIFIER` sans lancer de chantier trop large ni de refonte prématurée.

---

## 3. Backlog priorisé

### ACT-40-01 — Écrire la fiche canonique de domaine “base de connaissances formateur”

- **Priorité** : P1
- **Type** : documentation
- **Objectif** : produire une fiche courte qui sépare clairement cible 2.0, réel audité, écarts confirmés et points `A_VERIFIER`.
- **Livrable attendu** : une fiche de référence interne réutilisable dans les specs, prompts Cursor et plans CTO.
- **Justification** : le domaine est globalement aligné doctrinalement, mais encore trop exposé aux glissements entre objet réel (`TrainerKnowledgeItem`) et chaîne fonctionnelle complète.
- **Dépendances** : matrice d’écarts validée, décisions documentaires validées.
- **Statut recommandé** : à lancer immédiatement.

### ACT-40-02 — Formaliser un pseudo-contrat documentaire de `TrainerKnowledgeItem`

- **Priorité** : P1
- **Type** : contrat documentaire
- **Objectif** : décrire `TrainerKnowledgeItem` avec les champs de responsabilité minimaux : rôle, producteur, consommateurs, statuts, rattachements, provenance, exposition.
- **Livrable attendu** : bloc pseudo-schéma orienté responsabilités, non ORM-détaillé.
- **Justification** : la cible 2.0 fixe cet objet comme pivot du domaine, et le réel montre sa présence ; il manque encore un contrat de lecture stable.
- **Dépendances** : ACT-40-01.
- **Statut recommandé** : à lancer immédiatement après ACT-40-01.

### ACT-40-03 — Ajouter un tableau d’alignement “nom doctrinal / nom réel observé / niveau de preuve”

- **Priorité** : P1
- **Type** : documentation d’alignement
- **Objectif** : éviter les collisions de vocabulaire entre spec 2.0, audits et code observé.
- **Livrable attendu** : tableau de domaine couvrant au minimum `base de connaissances formateur`, `orchestrateur formateur`, `TrainerKnowledgeItem`, ingestion documentaire, validation humaine, consommation apprenant.
- **Justification** : le glossaire joue déjà ce rôle à l’échelle transverse, mais le domaine a besoin d’un niveau plus opératoire.
- **Dépendances** : ACT-40-01.
- **Statut recommandé** : immédiat.

### ACT-40-04 — Rédiger la section “ce qui est fixé / ce qui reste ouvert” pour l’orchestrateur formateur

- **Priorité** : P1
- **Type** : clarification de spec
- **Objectif** : borner précisément le workflow trainer sans le sur-spécifier.
- **Livrable attendu** : section documentaire distinguant :
  - finalité fixée ;
  - invariants fixés ;
  - script conversationnel encore ouvert ;
  - rôles de validation encore partiellement ouverts ;
  - consommation apprenant partiellement prouvée.
- **Justification** : la cible 2.0 fixe l’ambition et les garde-fous, mais laisse volontairement ouvert le script détaillé.
- **Dépendances** : ACT-40-01, ACT-40-02.
- **Statut recommandé** : immédiat.

### ACT-40-05 — Documenter explicitement la règle de validation humaine et de non-auto-promotion

- **Priorité** : P1
- **Type** : garde-fou documentaire
- **Objectif** : rendre non ambiguë la règle de passage entre statuts de connaissance.
- **Livrable attendu** : bloc invariant réutilisable dans toutes les docs de domaine et futurs prompts Cursor.
- **Justification** : c’est un invariant central de la cible 2.0 et un point sensible de gouvernance produit.
- **Dépendances** : aucune.
- **Statut recommandé** : immédiat.

### ACT-40-06 — Décrire explicitement la subordination au référentiel primaire

- **Priorité** : P2
- **Type** : clarification doctrinale
- **Objectif** : éviter toute lecture où la base formateur deviendrait la nouvelle vérité métier principale.
- **Livrable attendu** : section dédiée rappelant l’ordre référentiel primaire -> base formateur gouvernée -> usage documentaire / RAG.
- **Justification** : le domaine doit enrichir Hugo, pas remplacer la logique référentielle centrale.
- **Dépendances** : ACT-40-01.
- **Statut recommandé** : rapide.

### ACT-40-07 — Préparer une vérification ciblée code du chaînage `document ingestion -> TrainerKnowledgeItem -> usage runtime`

- **Priorité** : P2
- **Type** : audit ciblé
- **Objectif** : confirmer ce qui est effectivement implémenté de bout en bout sur le domaine.
- **Livrable attendu** : note d’audit courte listant :
  - points confirmés ;
  - points partiels ;
  - ruptures de chaîne ;
  - zones non observables.
- **Justification** : le réel montre des briques compatibles, mais pas encore une preuve complète de la chaîne fonctionnelle.
- **Dépendances** : ACT-40-02, ACT-40-03.
- **Statut recommandé** : après stabilisation documentaire minimale.

### ACT-40-08 — Marquer explicitement `A_VERIFIER` les usages runtime distants et variantes Encoors

- **Priorité** : P2
- **Type** : hygiène documentaire
- **Objectif** : empêcher qu’une démo ou une variante distante soit relue comme preuve de complétude du domaine.
- **Livrable attendu** : liste bornée des assertions interdites sans preuve complémentaire.
- **Justification** : la baseline démo distante ne prouve pas l’équivalence avec le local ni la complétude trainer.
- **Dépendances** : aucune.
- **Statut recommandé** : immédiat.

### ACT-40-09 — Préparer un mini-contrat “consommation apprenant des savoirs validés”

- **Priorité** : P3
- **Type** : contrat cible additif
- **Objectif** : préciser, sans refonte, comment les savoirs validés peuvent enrichir les orchestrateurs apprenant.
- **Livrable attendu** : note de contrat minimal couvrant :
  - usages autorisés ;
  - subordination au référentiel ;
  - articulation avec RAG ;
  - garde-fous de non-souveraineté.
- **Justification** : la cible 2.0 l’implique, mais le détail reste encore trop diffus.
- **Dépendances** : ACT-40-02, ACT-40-07.
- **Statut recommandé** : après audit ciblé.

### ACT-40-10 — Préparer un prompt Cursor d’audit strictement limité au domaine

- **Priorité** : P3
- **Type** : outillage CTO
- **Objectif** : permettre une vérification code/documentation bornée, sans dérive vers une refonte du moteur entier.
- **Livrable attendu** : prompt Cursor structuré avec :
  - périmètre fichiers ;
  - questions d’audit ;
  - résultats attendus ;
  - format de restitution.
- **Justification** : utile seulement une fois le contrat documentaire minimal clarifié.
- **Dépendances** : ACT-40-07.
- **Statut recommandé** : ensuite.

---

## 4. Séquencement recommandé

### Vague 1 — Mise au propre documentaire

- ACT-40-01 — fiche canonique de domaine
- ACT-40-02 — pseudo-contrat `TrainerKnowledgeItem`
- ACT-40-03 — tableau d’alignement vocabulaire / preuve
- ACT-40-04 — section “fixé / ouvert”
- ACT-40-05 — invariant validation humaine
- ACT-40-08 — marquage `A_VERIFIER`

### Vague 2 — Consolidation doctrinale du domaine

- ACT-40-06 — subordination au référentiel primaire
- ACT-40-07 — audit ciblé du chaînage réel

### Vague 3 — Préparation chantier additif

- ACT-40-09 — mini-contrat consommation apprenant
- ACT-40-10 — prompt Cursor d’audit borné domaine

---

## 5. Actions explicitement hors backlog de ce domaine

Les points suivants sont volontairement exclus de ce backlog :
- refonte globale du pipeline P0 ;
- redesign complet des surfaces trainer ;
- chantier global RAG ;
- admin produit complète multi-rôles ;
- alignement infra global local / Encoors ;
- backlog transverse Hugo 1.9 / 2.0.

Ils pourront être reliés à ce domaine plus tard, mais ne doivent pas être absorbés ici.

---

## 6. Critères de clôture du domaine documentaire

Le backlog documentaire du domaine pourra être considéré comme suffisamment traité lorsque :
- `TrainerKnowledgeItem` dispose d’un contrat documentaire léger mais stable ;
- la différence entre cible 2.0 et réel audité est lisible sans ambiguïté ;
- les points `A_VERIFIER` sont explicitement bornés ;
- le lien entre base formateur, référentiel primaire et consommation apprenant est formulé sans sur-promesse ;
- un prompt Cursor de vérification ciblée peut être exécuté sans rouvrir toute la doctrine Hugo.