# Contextualisation complète — Hugo 1.9, intentions de livraison, lots Cursor 0 à 6, contraintes de fil et état cible connu (V2)

## Objet du document

Ce document sert de **socle de compréhension opérationnel** pour Cursor. Il ne doit pas seulement lister des lots ou des fichiers : il doit rappeler **ce que la livraison cherchait à obtenir**, **pourquoi ces lots existent**, **ce qui relève de la spec écrite**, **ce qui relève des consignes du fil**, et **ce qui doit rester une interprétation prudente tant que le code réel n’a pas été audité**.

Il distingue explicitement :
- ce qui relève de la **spec explicite** ;
- ce qui relève d’une **synthèse consolidée** de plusieurs documents de référence ;
- ce qui relève d’une **consigne contextuelle explicite du fil** ;
- ce qui relève d’une **interprétation prudente** utile pour auditer ou compléter.

---

## 1. Ce qu’est Hugo dans le périmètre POC

Hugo est un assistant réflexif AFEST centré apprenant, intégré dans un POC multi-tenant. Le périmètre reste centré sur Hugo, pas sur une constellation générique d’agents. L’architecture cible reste une webapp unique, responsive, mobile-first côté apprenant terrain et desktop-first côté tuteur, formateur, coordinateur et administration. Les comptes sont créés manuellement dans le POC à ce stade.

### 1.1 Points de cadrage stables
- Hugo n’est ni un évaluateur autonome, ni un enseignant magistral, ni un agent de validation autonome.
- La source de vérité comportementale n’est plus le prompt seul : elle résulte de la combinaison **SPEC + orchestrateur backend + TutorPrompt + contexte structuré**.
- L’architecture réelle doit **enrichir l’orchestrateur Django existant** et ne pas recréer une architecture parallèle de type `hugoconfig` ou “simple prompt builder”.

### 1.2 Intention produit de fond
L’intention de fond de la trajectoire 1.6 → 1.9 est de faire passer Hugo :
- d’un assistant surtout pensé comme “générateur de prochaine question” ;
- à un **moteur de régulation tutorale piloté par état** ;
- avec une logique plus explicite, plus testable, plus montrable, et plus cohérente entre backend, prompt, UI et traces d’audit.

Autrement dit, la livraison n’avait pas seulement pour but d’ajouter des objets techniques. Elle devait rendre Hugo :
- plus **piloté par état** ;
- plus **lisible produit** ;
- plus **démontrable côté interface** ;
- plus **gouvernable** côté mémoire, postures et observabilité.

---

## 2. Hiérarchie de vérité à retenir

### Niveau 1 — SPEC POC v1.5 update 27/03/2026
Cette SPEC reste la source principale produit/technique. Elle fixe :
- la doctrine multi-tenant ;
- les rôles ;
- la logique de confidentialité ;
- la webapp unique ;
- l’architecture technique ;
- les endpoints MVP ;
- les tests d’acceptation minimaux ;
- la logique TutorPrompt ;
- la place du P0 et de la décision locale.

### Niveau 2 — Hugo 1.6 Cadrage Transformation du comportement
Ce cadrage précise la transformation du comportement conversationnel en moteur de régulation tutorale piloté par état. C’est le document qui donne la bonne manière de penser Hugo au-delà du prompt, et qui explique l’intention profonde des évolutions : un seul objectif de régulation par message, possibilité bornée de bundling, priorité à la réparation/rassurance/tempo, mémoire hybride gouvernée, contradiction explicite, ZPD, et articulation structurée entre état, mémoire, overlay et RAG.

### Niveau 3 — README Cursor et lots Cursor 0 à 6
Ces documents décrivent le découpage d’implémentation additif par lots. Ils figent le principe “P0 inchangé / enrichissements additifs”, structurent les migrations, nouveaux objets, endpoints, garde-fous de sérialisation, règles enum/string, mémoire thématique, UIState et analytics.

### Niveau 4 — Code réel / branches / tests / UI
Le code réel décide de l’état effectivement livré. Mais il doit toujours être comparé à la hiérarchie documentaire ci-dessus. La présence d’un fichier ne suffit jamais à conclure qu’une capacité est réellement intégrée, visible en UI, ou conforme à l’intention de départ.

---

## 3. Invariants produit et sécurité non négociables

### 3.1 Multi-tenant strict
- `organisationid` sur les tables métier.
- `SET LOCAL app.organisationid` par transaction.
- RLS active et testée cross-tenant.
- Aucun tenant A ne lit/écrit le tenant B.

### 3.2 Confidentialité-first
- Le verbatim est privé par défaut.
- Le partage est distinct pour synthèse, preuves et verbatim.
- Les rôles non apprenant ne voient que ce qui est explicitement partagé.
- En sandbox/dev, une journalisation technique plus riche peut exister pour déboguer l’orchestration, mais cela ne constitue pas une exposition métier autorisée.

### 3.3 Doctrine conversationnelle stable
- posture AFEST réflexive ;
- un seul objectif de régulation par message ;
- dans le POC, une question simple par défaut ;
- possibilité bornée de plusieurs questions très brèves si elles servent le même micro-objectif ;
- fallback automatique vers une seule question simple en cas de charge cognitive ou risque interactionnel élevés ;
- pas de cours magistral, pas de jugement, pas de boucle absurde.

### 3.4 Pivot runtime
- la configuration pivot n’est plus `hugoconfig` mais `TutorPrompt` ;
- la priorité de sélection est session > groupe > organisation > fallback legacy ;
- les variations comportementales passent par TutorPrompt et les overrides runtime déjà présents ;
- la logique d’orchestration doit rester dans le backend Django existant.

---

## 4. Intention détaillée de la livraison 1.9

Cette livraison ne doit pas être lue comme une juxtaposition de lots techniques. Son intention détaillée était la suivante.

### 4.1 Rendre Hugo plus explicite comme moteur de régulation
Le système devait devenir plus lisible comme moteur piloté par état, avec un noyau P0 inchangé, une décision locale explicite, des objets intermédiaires nommés, et une meilleure cohérence entre backend, prompts, tests et rendu produit.

### 4.2 Rendre la progression visible et montrable
Une intention forte de la série de modifications était de transformer des signaux internes difficiles à montrer en une **lisibilité produit visible côté front**. C’est précisément le rôle du couple `ConversationProgress` / `UIState`, puis du LOT 2 côté interface.

### 4.3 Sortir d’un front trop technique ou trop opaque
Le front attendu ne devait pas simplement “continuer à marcher”. Il devait commencer à montrer :
- une scène ou étape lisible ;
- une progression compréhensible ;
- une quête active ;
- une couleur de maturité ;
- des actions synthèse/évaluation présentées comme états produit ;
- et cela **sans exposer les signaux bruts de P0**.

### 4.4 Rendre les modes de conduite visibles
La livraison devait aussi rendre explicites des postures de conduite de séance, au lieu de laisser cette logique enfouie dans le prompt ou dans des heuristiques implicites.

### 4.5 Ajouter une mémoire utile mais gouvernée
Il ne s’agissait pas d’ajouter une “mémoire totale”, mais une mémoire thématique post-conversation, structurée, persistante, sans verbatim brut, et compatible avec validation humaine pour les niveaux plus stabilisés.

### 4.6 Préparer la montée en puissance tutorale
La livraison préparait aussi la suite :
- une base de connaissances formateur gouvernée ;
- une observabilité qualité/cohorte ;
- et, plus largement, un produit plus administrable et plus auditable.

---

## 5. Lots Cursor de la livraison 1.9 — objectifs, intentions et attendus

> Remarque de forme importante : cette section doit parler explicitement des **lots Cursor 0 à 6**. Éviter les titres flous du type “ce que les lots ajoutent concrètement”. Préférer une formulation du type : **“Lots Cursor 0 à 6 de la livraison 1.9 — finalité, intention et attendus”**.

## 5.1 LOT 0 — Contrats et fondations

### Finalité
Introduire les objets intermédiaires communs sans toucher au noyau P0 existant.

### Intention
Créer un socle additif testable, stable, réutilisable par les lots suivants. À ce stade, l’objectif n’était pas encore de produire un changement front visible majeur, mais de préparer ce qui devait le rendre possible proprement.

### Ajouts structurants attendus
- `ConversationPosture`
- `SessionMaturityLevel`
- `KnowledgeItemStatus`
- `ConversationBranch`
- `ConversationProgress`
- `UIState`
- `reasoncodes`
- `tutorprofiles.py` stub
- migration `conversationprogress` sur `HugoSession`
- stubs endpoints `/progress`, `/ui-state`, `/posture`
- tests NR P0, dont NR-07 et NR-09

### Lecture audit utile
Si LOT 0 n’est pas propre, les lots suivants deviennent fragiles. En particulier, `UIState` ne doit jamais réexposer du P0 brut.

---

## 5.2 LOT 1 — Progression conversationnelle

### Finalité
Calculer l’avancement global de la conversation indépendamment du seul tour courant et stocker le résultat dans `HugoSession.conversationprogress`.

### Intention
Donner à Hugo une **mémoire courte structurée de progression** exploitable à la fois par le backend et par le front, pour sortir d’une logique trop instantanée centrée sur le dernier tour.

### Attendus
- `ConversationProgressCalculator`
- calcul des branches actives
- maturité globale RED / ORANGE / GREEN
- `priority_branch_id`
- `dispersion_risk`
- éligibilité synthèse / évaluation
- `missing_for_next_level`
- `reasoncodes`
- `build_ui_state_from_progress`
- `deserialize_conversation_progress`
- remplacement des stubs LOT 0 pour `/progress` et `/ui-state`

### Point doctrinal important
Toute reconstruction depuis le JSONB de `conversationprogress` doit passer par une vraie désérialisation explicite. L’usage brut de `ConversationProgress(**raw)` est à proscrire dès qu’il y a enums et branches imbriquées.

### Conséquence produit attendue
LOT 1, à lui seul, ne garantit pas encore un front radicalement transformé. Mais il crée la matière première qui devait précisément être rendue visible par LOT 2.

---

## 5.3 LOT 2 — Adaptateur UI 1.9

### Finalité
Brancher le front sur un modèle produit montrable dérivé de `UIState`, et non sur des signaux internes techniques.

### Intention explicite de ce lot
C’est **le lot front principal de la série**. Son but n’était pas un simple branchement discret, mais une évolution visible de la lisibilité produit côté interface.

### Attendus documentés
- `progressionLabels.js`
- remplacement de `engagementUiModel.js`
- `HugoProgressPanel.jsx`
- consommation de `/ui-state`
- endpoints ou actions synthèse / évaluation intégrées à l’UI

### Intention front à rappeler explicitement
Le front attendu ne devait pas rester “quasi inchangé”. À partir du moment où `UIState` existe, où `/ui-state` est branché, et où un panneau de progression dédié est attendu, il devait y avoir des effets visibles sur :
- la compréhension de la progression ;
- la lisibilité de l’état de séance ;
- la mise en avant de la quête ou scène active ;
- l’état des actions de synthèse / évaluation.

### Garde-fou d’interprétation
Le front produit ne doit pas montrer les variables P0 brutes. `UIState` existe précisément pour transformer un état technique en éléments produits simples et montrables.

### Consigne contextuelle du fil à ne pas perdre
Les changements front devaient être appliqués **sur la branche déjà améliorée ergonomiquement pour être plus montrable**. Ce point n’est pas forcément écrit noir sur blanc dans chaque lot, mais il a été donné comme consigne contextuelle importante et doit faire partie du cadre d’audit.

### Conséquence audit immédiate
Si, après la série de modifications, le front paraît très peu changé, il faut auditer en priorité :
1. si LOT 2 a vraiment été intégré ;
2. si `/ui-state` est réellement consommé ;
3. si le panneau de progression est effectivement monté ;
4. si les changements ont été faits sur la bonne branche front ;
5. si le code n’est pas présent mais non branché dans les écrans montrables.

---

## 5.4 LOT 3 — Modes / postures de conduite

### Finalité
Introduire trois postures explicites de conduite de séance, opérant avant P0 tout en gardant P0 intact.

### Intention
Rendre visible et gouvernable quelque chose qui était jusque-là trop implicite : le fait qu’Hugo peut conduire une séance selon plusieurs modes cohérents, sans casser le noyau décisionnel de base.

### Postures attendues
- `DIAGNOSTIC`
- `REFLECTIVE_AFEST`
- `KNOWLEDGE_REVIEW`

### Ajouts attendus
- `postureselector.py`
- `tutorprofiles.py` complet remplaçant le stub
- `posturetransitions.py`
- `synthesisservice.py`
- endpoint `set-posture`
- injection de contraintes de posture dans l’orchestrateur et le rendu

### Intention produit derrière ce lot
Le but n’est pas seulement de poser trois enums. Il s’agit de rendre la conduite de séance plus intelligible, plus testable, et potentiellement plus visible côté produit.

---

## 5.5 LOT 4 — Mémoire thématique inter-session

### Finalité
Ajouter une mémoire thématique structurée, persistante, gouvernée backend, sans tomber dans une mémoire totale ni dans du verbatim brut.

### Intention
Permettre à Hugo de mieux retrouver et stabiliser ce qui a déjà été travaillé, sans casser la doctrine de confidentialité-first et sans dériver vers une mémoire narrative incontrôlée.

### Ajouts attendus
- modèle `LearnerThemeMemory`
- migration associée
- `memoryconsolidator.py`
- endpoint `memory-summary`
- injection conditionnelle en contexte via feature flag

### Règles fortes
- consolidation post-conversation uniquement ;
- pas de verbatim brut ;
- enums stockées en `.value` ;
- pas d’auto-upgrade `derived_provisional` vers `validated_trainer`.

### Intention de livraison à rappeler
Le but n’était pas de “faire de la mémoire” au sens vague. Le but était de construire une mémoire **pédagogiquement utile, structurée, gouvernée et audit-able**.

---

## 5.6 LOT 5 — Base de connaissances formateur

### Finalité
Permettre au formateur d’uploader des documents, d’éliciter des connaissances, puis de les structurer dans une base de connaissance exploitable par Hugo avec validation humaine.

### Intention
Préparer une base de connaissances gouvernée, distincte du verbatim apprenant, distincte aussi d’une vérité réglementaire automatique. Ce lot sert à outiller le formateur, pas à déléguer la validation à la machine.

### Ajouts attendus
- modèle `TrainerKnowledgeItem`
- `documentingestor.py`
- questionnaire dialogique formateur
- vues trainer
- validation humaine explicite

### Règles fortes
- rien ne doit passer `validated_trainer` sans validation humaine ;
- la base de connaissance n’est pas la source primaire de vérité réglementaire.

---

## 5.7 LOT 6 — Observabilité et cohorte

### Finalité
Ajouter des signaux de qualité de conversation et des métriques cohorte.

### Intention
Permettre un audit plus fin de la qualité tutorale, du comportement d’Hugo et d’effets cohortes, sans retomber dans une observabilité bavarde exposant des contenus bruts sensibles.

### Ajouts attendus
- `ConversationQualitySignal`
- `qualitytracker.py`
- `analytics/cohortdashboard.py`
- `views/analytics.py`
- tests qualité

### Intention à rappeler
Ce lot n’est pas cosmétique. Il sert à rendre Hugo **pilotable, mesurable, et auditable à l’échelle**, en cohérence avec la logique de produit régulé.

---

## 6. Règles transverses réaffirmées par le README Cursor

Le README des lots consolide plusieurs garde-fous qui doivent servir de filtre d’audit principal :

- aucun champ P0 modifié ;
- enums canoniques dans `conversationprofile.py` uniquement ;
- `UIState` sans champ P0 ;
- `organisationid` avec `s` partout ;
- consolidation et analytics post-conversation uniquement ;
- `derived_provisional` n’est jamais auto-upgradé ;
- toute reconstruction depuis JSONB passe par une désérialisation explicite ;
- toute enum stockée en base Django est persistée sous forme de `.value`.

Ces règles sont importantes parce qu’elles permettent de repérer vite les implémentations approximatives, fragiles ou conceptuellement déviantes.

---

## 7. Front — rappel renforcé des intentions et du cadre d’audit

### 7.1 Ce qui relève de la spec ou des lots
Le front doit consommer `UIState` via `/ui-state`, remplacer le vieux modèle UI ciblé, et intégrer un panneau de progression ou équivalent produit.

### 7.2 Ce qui relève de l’intention de livraison
Le front ne devait pas être presque inchangé. Il devait devenir plus montrable, plus lisible, et mieux aligné sur la progression conversationnelle réelle.

### 7.3 Ce qui relève d’une consigne contextuelle explicite du fil
Les modifications front de cette série devaient être appliquées sur la **branche déjà retravaillée ergonomiquement pour être plus montrable**.

### 7.4 Ce qui doit guider l’audit
Un audit front ne doit pas se contenter de vérifier la présence des fichiers. Il doit vérifier :
- l’intégration réelle ;
- le branchement dans les écrans utiles ;
- le rendu visible ;
- la cohérence avec la branche ergonomique de référence ;
- l’absence d’exposition de signaux techniques bruts à la place d’un modèle produit.

---

## 8. Rôles, comptes et administration

### 8.1 Ce qui est clairement spécifié
Les rôles structurants sont :
- LEARNER
- TUTOR
- TRAINER
- COORDO
- ORGADMIN
- SUPERADMIN

Le POC prévoit des comptes créés manuellement, sans invitations email. `ORGADMIN` peut administrer users, groups et déclencher des exports. `SUPERADMIN` correspond à une administration technique globale qui doit respecter l’isolation multi-tenant et éviter toute lecture applicative libre du contenu apprenant.

### 8.2 Ce qui est moins détaillé dans les lots
Les lots Cursor 0 à 6 ne décrivent pas encore, de manière complète et finalisée :
- un espace UI métier complet de création / suppression d’apprenants ;
- un espace UI métier complet de création / suppression de tuteurs ;
- un rattachement fin à une formation ;
- une édition complète des consignes pédagogiques dans une interface tuteur ;
- un espace superadmin produit complet et détaillé.

### 8.3 Conséquence d’audit
Il faut donc distinguer soigneusement :
- les endpoints/capacités backend existants ;
- l’admin technique déjà présente ;
- l’UI métier réellement exposée ;
- les manques avérés ;
- ce qui reste à spécifier avant toute construction propre.

### 8.4 Interprétation prudente
À ce stade, on peut dire que la spec **balise un minimum d’administration**, mais pas encore toute la gestion métier détaillée des comptes telle qu’on pourrait l’attendre pour un centre de formation complet.

---

## 9. Questions sensibles du fil à traiter explicitement pendant l’audit

### 9.1 Front jugé trop peu changé
C’est un signal d’alerte fort. Il faut vérifier non seulement la présence des fichiers LOT 2, mais leur intégration réelle et leur rendu visible.

### 9.2 Branche ergonomique de référence
Si les travaux ont été faits sur une autre branche que celle déjà améliorée ergonomiquement, il y a un problème de conformité à la demande initiale, pas seulement un problème de rendu.

### 9.3 Gestion des comptes centre / tuteurs / apprenants
Il faut d’abord cartographier l’existant avant de lancer une construction. Ne pas supposer qu’un espace métier existe parce que des rôles ou endpoints sont prévus dans la SPEC.

### 9.4 Traduction en critères auditables
Toute spec utile de ce fil doit pouvoir être transformée en critères vérifiables côté backend, frontend, intégration, droits, données, rendu et tests simulés.

---

## 10. Ce qu’il ne faut surtout pas faire pendant l’audit

- Ne pas déduire l’état attendu à partir d’un seul lot.
- Ne pas confondre présence de code et usage réel.
- Ne pas supposer qu’un espace admin existe parce qu’un endpoint existe.
- Ne pas supposer qu’un front est conforme parce que des composants sont présents dans le repo.
- Ne pas inventer de spécification détaillée sur les comptes si elle n’est pas écrite.
- Ne pas oublier la hiérarchie documentaire.
- Ne pas oublier la contrainte de branche ergonomique du front.

---

## 11. Résumé opératoire pour Cursor

Quand tu audites Hugo, pense-le ainsi :

1. **Socle** : P0 gelé, enrichi additivement.
2. **Intention de livraison** : rendre Hugo plus piloté par état, plus visible, plus montrable, plus gouvernable.
3. **Progression** : `ConversationProgress` et `UIState` doivent structurer la lisibilité produit.
4. **Front** : LOT 2 doit rendre cette progression visible de manière réellement montrable.
5. **Postures** : LOT 3 doit expliciter des modes de conduite sans casser P0.
6. **Mémoire** : LOT 4 doit ajouter une mémoire thématique post-conversation, pas du verbatim brut.
7. **Connaissance formateur** : LOT 5 doit structurer une base gouvernée à validation humaine.
8. **Analytics** : LOT 6 doit apporter des signaux qualité/cohorte si réellement implémenté.
9. **Administration** : la SPEC balise des capacités minimales, mais la gestion métier complète des comptes reste à cartographier.
10. **Audit** : toujours distinguer spec explicite, synthèse consolidée, consigne du fil, code réel, interprétation prudente.

Ce n’est qu’après cette lecture qu’on peut juger correctement si Hugo a été bien implémenté.