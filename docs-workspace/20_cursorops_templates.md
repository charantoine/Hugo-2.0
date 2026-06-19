## Template Cursor — Audit mémoire gouvernée intra-conversation (domaine 20)

### 0. Objectif du prompt

Auditer le comportement réel de la **mémoire dans Hugo local**, en distinguant clairement :

- mémoire intra-conversation (session courante) ;
- préparation inter-sessions éventuelle (sans la décrire comme active) ;
- projection de type `memory-summary` côté API.

Objectif du lot : vérifier ce qui est **effectivement** en place pour la mémoire gouvernée **intra-conversation**, sans sur-interpréter la cible 2.0 complète.

---

### 1. Contexte à coller en entrée de prompt

Tu travailles dans le workspace local :

- `~/Desktop/zone de travail hugo/docs-workspace`
- `~/Desktop/zone de travail hugo/hugo_back`
- `~/Desktop/zone de travail hugo/hugo-hugolucia`
- `~/Desktop/zone de travail hugo/hugo-main`

Les documents de référence à respecter sont :

- `docs-workspace/00_HIERARCHIE_DOCUMENTAIRE.md`
- `docs-workspace/DOC_METHODO_REFERENCE_CONVERGENCE_HUGO_REVISE.md`
- `docs-workspace/plan_documentation_cto_convergence_hugo.md`
- `docs-workspace/synthese_globale_ecarts_par_domaine.md`
- `docs-workspace/ecarts — 20_memoire_gouvernee.md`
- `docs-workspace/glossaire_alignement_hugo_reel_vs_spec.md`
- `docs-workspace/03_ETAT_PRODUIT_REEL.md`
- `docs-workspace/05_ECARTS_DOC_CODE_PRODUIT.md`

L’audit doit distinguer le **cœur de convergence** (mémoire intra-conversation, lot Vague 1) de la **couronne** (inter-sessions active, injection prompt si hors décision doc). Ne pas promouvoir en IMPLÉMENTÉ ce qui reste CIBLE ou A_VÉRIFIER dans la synthèse globale.

Rappels impératifs :

- Séparer explicitement : réel observé, cible 2.0, écarts confirmés, `AVERIFIER`, hypothèses.
- La cible du lot courant est **mémoire gouvernée intra-conversation seulement** ; l’inter-sessions est préparée mais **non livrée**.
- Le verbatim brut ne doit pas être traité comme mémoire principale ; ne pas exposer de champs P0 au front.

---

### 2. Tâches demandées à Cursor — Plan Backend

#### 2.1. Cartographier les services et modèles mémoire

1. Dans `hugo_back`, localiser :
   - le service / module de **mémoire de session** (souvent `buildsessionmemory`, `sessionmemory.py`) ;
   - le service `MemoryConsolidator` (`memoryconsolidator.py`) ;
   - le modèle `LearnerThemeMemory` (ou équivalent) ;
   - tout code lié à `memory-summary` ou à `GET hugosessionsidmemory-summary`.
2. Pour chacun, produire une fiche :
   - chemin de fichier ;
   - rôle (mémoire de session, consolidation inter-session, projection, etc.) ;
   - types de données manipulées.

#### 2.2. Mémoire intra-conversation (session courante)

À partir du code :

1. Expliquer comment la **mémoire intra-session** est construite :
   - où et comment `buildsessionmemory` (ou équivalent) est appelé ;
   - quels éléments du tour ou de la session sont intégrés (thèmes, objectifs, points ouverts, faits clarifiés, etc.) ;
   - structure de la mémoire (objets, champs, JSON si visible).
2. Décrire comment cette mémoire est **relue** dans les tours suivants :
   - où elle est injectée dans le pipeline runtime (par exemple dans `buildhugoturn` ou un service de contexte) ;
   - quels champs sont consommés par le moteur.
3. Dire précisément ce qui est **confirmé** dans le code pour la session courante, et ce qui reste `AVERIFIER`.

#### 2.3. Projection `memory-summary` côté API

1. Localiser l’endpoint `GET hugosessionsidmemory-summary` (ou équivalent).
2. Décrire le contrat JSON réel :
   - structure (champs, types, exemples si possible) ;
   - présence ou absence de verbatim brut ;
   - quelles informations sont agrégées (thèmes, objectifs, points ouverts, etc.).
3. Dire explicitement :
   - si cette projection peut raisonnablement être lue comme “résumé gouverné du fil courant” ;
   - ce qui reste `AVERIFIER` (filtres, liens avec le référentiel, niveau de gouvernance).

#### 2.4. Statut de `LearnerThemeMemory` et de la consolidation inter-session

1. Vérifier si `LearnerThemeMemory` est :
   - seulement défini comme modèle ;
   - ou réellement alimenté par `MemoryConsolidator` ;
   - et surtout, s’il est injecté dans le runtime (par exemple via `buildhugoturn`).
2. Qualifier l’état réel de la **mémoire inter-sessions** :
   - non utilisée ;
   - partiellement préparée ;
   - utilisée dans certains cas.
3. Distinguer clairement :
   - ce qui relève de la **préparation inter-sessions** (objet/modele, service de consolidation) ;
   - ce qui est effectivement utilisé dans la session courante.

---

### 3. Tâches demandées à Cursor — Plan Front (Chromium)

> Cette partie est optionnelle mais utile si Chromium est installée pour tester le front.

#### 3.1. Lancer le front local

1. Lancer Chromium sur le front local Hugo (`hugo-hugolucia`) avec l’URL/commande appropriée.
2. Ouvrir un parcours apprenant typique (conversation tutorielle).

#### 3.2. Observer la mémoire visible côté produit

1. Identifier si le front expose :
   - un “récap” ou résumé du fil courant ;
   - des rappels d’objectifs, de points ouverts, d’engagements ;
   - tout élément présenté comme “mémoire” ou “ce que Hugo retient”.
2. Vérifier :
   - que rien n’est présenté comme **historique brut complet** ;
   - qu’aucun champ technique ou P0 n’est exposé ;
   - qu’il n’y a pas d’UI qui donne l’illusion d’une mémoire inter-sessions profil apprenant déjà stable.

3. Vérifier si l’UI utilise (via UIState) les informations renvoyées par `memory-summary` ou par la mémoire de session (et comment elles sont formulées dans le produit).

---

### 4. Réel vs cible minimale mémoire pour ce lot

En t’appuyant sur `ecarts — 20_memoire_gouvernee.md` et l’addendum méthodo :

1. Résumer la **cible minimale** pour ce lot :
   - mémoire gouvernée **intra-conversation**, pilotée backend ;
   - mémoire utile du fil courant = **résumé gouverné**, pas verbatim brut ;
   - inter-sessions préparée, mais **hors périmètre** d’implémentation immédiate.
2. Mettre en regard :
   - **Mémoire de session** (construction, lecture, structure) ;
   - **Projection `memory-summary`** (contrat réel, contenu) ;
   - **Inter-sessions** (LearnerThemeMemory, MemoryConsolidator) ;
   - **Projection produit** (éventuelle mémoire visible à l’apprenant).

Pour chaque axe, lister :

- ce qui est **confirmé** comme aligné ;
- ce qui est **partiel** ;
- ce qui est **absent** et relèverait d’un **nouveau contrat**.

---

### 5. Synthèse structurée attendue

La réponse doit contenir :

1. `## Sources mobilisées`
   - fichiers backend (paths) ;
   - endpoints ;
   - modèles ;
   - fichiers front / UIState ;
   - docs `docs-workspace` utilisées.

2. `## Réel confirmé`
   - mémoire intra-conversation (comment elle est construite, relue, ce qu’elle contient) ;
   - projection `memory-summary` (structure, contenu) ;
   - état de LearnerThemeMemory / MemoryConsolidator (préparation vs usage réel) ;
   - ce qui est éventuellement visible côté produit.

3. `## Cible 2.0 minimale pour ce lot`
   - rappel synthétique des décisions : mémoire intra-conversation seulement, inter-sessions préparée, pas de verbatim brut exposé.

4. `## Écarts confirmés`
   - par thème : session, summary, inter-sessions, produit ;
   - avec statuts si utile (ALIGNE, ALIGNE DOC PARTIEL, PARTIEL, AVERIFIER, ABSENT/NOUVEAU CONTRAT).

5. `## Points AVERIFIER`
   - éléments non tranchables sans tests supplémentaires (ex. flags, comportements distants, variantes).

6. `## Prochaine sortie utile (DOC / CODE / OPS)`
   - DOC : ébauche de contrat minimal de mémoire intra-conversation (schéma JSON, rubriques autorisées, interdits) ;
   - CODE : clarifications éventuelles (filtrage du verbatim, points d’injection, naming) ;
   - OPS : scénarios de test à refaire (Chromium, tests API).

---

### 6. Garde-fous à respecter dans la réponse Cursor

La réponse ne doit pas :

- présenter une mémoire inter-sessions comme déjà active si le code ne le prouve pas ;
- assimiler `LearnerThemeMemory` à une injection runtime complète sans vérification ;
- décrire `memory-summary` comme export brut de conversation ;
- proposer d’exposer au front :
  - verbatim complet ;
  - champs P0 ;
  - diagnostics non validés.

La réponse doit rester :

- descriptive sur ce que le code montre vraiment ;
- prudente sur la cible ;
- orientée vers la stabilisation de la **mémoire intra-conversation** comme premier socle.