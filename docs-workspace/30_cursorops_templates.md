## Template Cursor — Audit RAG / référentiel documentaire (domaine 30)

### 0. Objectif du prompt

Auditer le comportement réel du **RAG documentaire** dans Hugo local (backend + front via Chromium), en vérifiant que :

- le RAG est bien **lexical, gouverné, question-driven** ;
- il fonctionne comme **renfort documentaire situ**, pas comme mémoire principale ni moteur de cours ;
- ce qui est exposé à l’apprenant est cohérent avec cette doctrine (pas de sur-promesse “mémoire”).

L’objectif n’est pas de transformer le RAG en architecture vectorielle idéale, mais de décrire précisément ce qui existe et de préparer un **contrat minimal RAG lexical** pour le lot courant.

---

### 1. Contexte à coller en entrée de prompt

Tu travailles dans le workspace local suivant :

- `~/Desktop/zone de travail hugo/docs-workspace`
- `~/Desktop/zone de travail hugo/hugo_back`
- `~/Desktop/zone de travail hugo/hugo-hugolucia`
- `~/Desktop/zone de travail hugo/hugo-main`

Les documents de référence à respecter sont :

- `docs-workspace/00_HIERARCHIE_DOCUMENTAIRE.md`
- `docs-workspace/DOC_METHODO_REFERENCE_CONVERGENCE_HUGO_REVISE.md`
- `docs-workspace/plan_documentation_cto_convergence_hugo.md`
- `docs-workspace/synthese_globale_ecarts_par_domaine.md`
- `docs-workspace/ecarts — 30_referentiel_documentaire_rag.md`
- `docs-workspace/glossaire_alignement_hugo_reel_vs_spec.md`
- `docs-workspace/03_ETAT_PRODUIT_REEL.md`
- `docs-workspace/05_ECARTS_DOC_CODE_PRODUIT.md`

Ce domaine relève de la **couronne** plan CTO (renfort situé) : décrire le RAG comme **lexical observé**, pas vectoriel, tant qu’aucune preuve runtime ne contredit la synthèse globale.

Rappels impératifs :

- Séparer explicitement :  
  - réel observé ;  
  - cible 2.0 ;  
  - écarts confirmés ;  
  - points `AVERIFIER` ;  
  - hypothèses de convergence.
- Le RAG doit être documenté comme **lexical et gouverné**, tant qu’aucune preuve plus forte n’existe.
- Le front n’est **jamais** la source de vérité moteur ; Chromium sert à **confirmer** la projection produit des comportements backend.

---

### 2. Tâches demandées à Cursor — Plan Backend

#### 2.1. Cartographier les services et modules RAG

1. Dans `hugo_back`, localiser les services, modules ou fonctions qui portent le RAG documentaire, par exemple :
   - services de recherche documentaire (index, queries, “rag”, “search”, “document retrieval”) ;
   - code qui construit les requêtes sur le référentiel (filtres, tags, taxonomies, statuts de documents) ;
   - éventuels “overlays” (documents situés par contexte).
2. Pour chaque composant identifié, produire une fiche :
   - fichier et chemin ;
   - rôle principal (recherche, ranking, filtrage, overlay, etc.) ;
   - type de requête (lexicale, full-text, simple filtrage, autre).

#### 2.2. Nature réelle du RAG (lexical vs autre)

En lisant le code :

1. Expliquer comment sont construites les requêtes :
   - quels champs / colonnes sont interrogés ;
   - s’il y a scoring lexical, simple `LIKE`, full-text, autre ;
   - presence ou non de librairies vectorielles (si non, ne pas en inventer).
2. Confirmer si, dans l’état actuel :
   - le RAG est **lexical** (mot-clé / texte) ;
   - gouverné par des règles explicites (types de documents, statuts, filtres métiers) ;
   - question-driven (appelé à la demande, pas un flux silencieux “toujours actif”).

#### 2.3. Articulation avec le référentiel métier

1. Identifier comment les documents utilisés par le RAG sont reliés :
   - au référentiel métier (compétences, objectifs, situations) ;
   - aux structures de référentiel décrites dans les docs (si présentes).
2. Dire clairement :
   - si les documents RAG sont simplement des “pièces jointes” ou s’ils sont intégrés dans un référentiel structuré ;
   - quels champs portent la gouvernance (type de document, statut, source, etc.).

#### 2.4. Injection du RAG dans le contexte / UIState

1. Localiser dans le backend où les résultats RAG sont :
   - injectés dans le contexte de génération (TutorPrompt / pipeline de tour), si c’est le cas ;
   - exposés à l’UI via UIState (par exemple dans un builder `buildUiState`, champs `documents`, `resources` ou équivalent).
2. Pour chaque point d’injection :
   - décrire les objets / structures utilisés (listes de documents, extraits, métadonnées) ;
   - clarifier si le RAG est :
     - un renfort facultatif ;
     - un prérequis dur d’un comportement ;
     - ou juste un accessoire rarement utilisé.

---

### 3. Tâches demandées à Cursor — Plan Front (Chromium)

#### 3.1. Lancer le front local

1. Lancer Chromium sur le front local Hugo (`hugo-hugolucia`) avec l’URL / commande appropriée (à déduire depuis le projet).
2. Ouvrir au moins un **parcours apprenant** où le RAG devrait pouvoir intervenir (ex. situation avec accès à des documents, aide documentaire, ressources).

#### 3.2. Observer où et comment le RAG apparaît

Pour 1–2 scénarios :

1. Identifier dans l’UI :
   - sections ou panneaux qui affichent des documents, ressources, aide, “pour aller plus loin”, etc. ;
   - boutons/CTA qui mentionnent des documents, fiches, ou tout vocabulaire qui suggère le RAG.
2. Pour chaque zone :
   - noter le texte, la formulation, les labels ;
   - indiquer si la présentation reste clairement documentaire (ex. “Ressources”, “Documents liés”) ou dérive vers un discours de mémoire (“Ce que Hugo sait de vous”, etc.).

#### 3.3. Vérifier la cohérence front vs backend

1. Vérifier que ce que l’UI montre comme documents / ressources :
   - correspond à ce que le backend expose dans UIState / endpoints ;
   - n’est pas présenté comme “mémoire de l’apprenant” ni comme “savoir interne de Hugo”.
2. Noter tout écart entre :
   - le rôle documentaire réel (backend) ;
   - la promesse front (copywriting, labels, placement).

---

### 4. Réel vs cible minimale RAG pour ce lot

En t’appuyant sur `ecarts — 30_referentiel_documentaire_rag.md` et les docs de méthode :

1. Résumer la **doctrine cible minimale** pour ce lot :
   - RAG documentaire lexical, gouverné, question-driven ;
   - renfort documentaire situ, pas moteur de cours ni mémoire principale ;
   - contexte target : l’état + la mémoire utile priment, le RAG vient en support.
2. Mettre en regard, pour 3 axes :
   - **Moteur RAG backend** (construction des requêtes, filtrage, lexical vs autre) ;
   - **Articulation avec référentiel métier** (types de documents, statuts, filtre métier) ;
   - **Projection produit** (UIState + UI via Chromium).

Pour chaque axe, lister :

- ce qui est **confirmé** comme aligné avec la cible ;
- ce qui est **partiel** ;
- ce qui est **absent** et relèverait d’un **nouveau contrat**.

---

### 5. Synthèse structurée attendue

La réponse doit être structurée comme suit :

1. `## Sources mobilisées`
   - fichiers backend RAG ;
   - endpoints / services consultés ;
   - fichiers UIState / front ;
   - scénarios testés dans Chromium ;
   - docs `docs-workspace` utilisées.

2. `## Réel confirmé (backend + front)`
   - nature du RAG (lexical / gouverné / question-driven ou non) ;
   - pipeline backend (qui appelle quoi, avec quels filtres) ;
   - projection produit (comment les documents apparaissent réellement à l’apprenant).

3. `## Cible 2.0 minimale RAG pour ce lot`
   - 1–2 paragraphes de rappel doctrinal minimal, adaptés au lot courant.

4. `## Écarts confirmés`
   - par thème : moteur, référentiel, projection produit ;
   - statuts si utile (ALIGNE, ALIGNE DOC PARTIEL, PARTIEL, AVERIFIER, ABSENT/NOUVEAU CONTRAT).

5. `## Points AVERIFIER`
   - éléments non tranchables avec le code + Chromium (ex. flags runtime distant, configs non reproduites localement).

6. `## Prochaine sortie utile (DOC / CODE / OPS)`
   - DOC : contrat minimal “RAG lexical gouverné” (structure de requête, filtres, vocabulaire documentaire à utiliser côté produit) ;
   - CODE : petites actions de clarification / sécurisation (filtres, statuts de documents, champs UIState) ;
   - OPS : tests manuels ou automatisés à prévoir (scénarios Chromium, tests d’API).

---

### 6. Garde-fous à respecter dans la réponse Cursor

La réponse ne doit pas :

- décrire le RAG comme **mémoire** ou “profil apprenant” ;
- présenter un RAG “vectoriel” ou “intelligent” si le code montre une simple recherche lexicale ;
- transformer un widget documentaire UI en preuve que tout le moteur est RAG-driven ;
- promettre que le RAG “connaît tout le référentiel” sans preuve dans le code et les données.

La réponse doit rester :

- descriptive sur le réel ;
- prudente sur la cible ;
- orientée vers des contrats minimaux et des backlogs (DOC / CODE / OPS), pas vers des refontes globales.