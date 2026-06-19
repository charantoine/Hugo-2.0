# 20_memoire_gouvernee — 00_rapport_ecarts.md

> **Mise à jour post-cluster 16 — 2026-06-18** · `conv-hugo-post-tests-c16`  
> **Confirmé local :** `SessionMemoryContract`, memory-summary sans verbatim (B16-M1/M2).  
> **PARTIEL+ :** panneau `LearnerMemoryPanel.vue` (troncature `ExpandableText`, vouvoiement, U16-S3).  
> **CIBLE :** injection prompt ; mémoire dans UIState. Rapport : `rapport_mise_a_jour_doc_post_cluster16_2026-06-18.md`

## 0. Statut du document et sources mobilisées

Ce document est un **rapport narratif d’écarts** pour le domaine `20_memoire_gouvernee`.  
Il ne constitue pas une preuve d’implémentation à lui seul, mais un document de travail articulant cible 2.0, réel audité et glossaire d’alignement.

Pour parler de la **cible 2.0**, ce rapport s’appuie principalement sur :

- `spec_canonique_hugo_2_0.md` (sections mémoire gouvernée, référentiel / documentaire / RAG, matrices des objets et services backend, matrice validation humaine et statuts) ;
- les mentions de `LearnerThemeMemory` et de la logique de consolidation inter-session dans ces matrices.

Pour parler du **réel**, il s’appuie sur :

- `00_HIERARCHIE_DOCUMENTAIRE.md` pour la hiérarchie des sources et les règles de lecture mémoire / persistence ;
- `glossaire_alignement_hugo_reel_vs_spec.md` pour les couples `LearnerThemeMemory` ↔ `memoryconsolidator.py`, projection `memory-summary`, distinction mémoire intra-session vs thématique inter-session ;
- la note de lot courant intra‑conversation et les constats de code résumés dans `20_memoire_gouvernee_note_lot_courant_memoire_intra_conversation.md`.

Le glossaire est utilisé uniquement comme **pont de vocabulaire** (nom doctrinal vs nom réel observé), jamais comme preuve unique d’implémentation.

## 1. Périmètre du domaine mémoire gouvernée

### 1.1 Cible 2.0 — ce que couvre « mémoire gouvernée »

Dans la spec canonique 2.0, la **mémoire gouvernée** désigne un ensemble cohérent :

- une mémoire **thématique, structurée, gouvernée, référentiel-first**, distincte d’un simple historique brut de conversation ;
- un **ordre de récupération de contexte** priorisant l’état apprenant, puis la mémoire thématique, puis éventuellement du verbatim interne borné, puis l’overlay référentiel et enfin le documentaire ;
- une **consolidation inter-session** post-conversation, effectuée côté backend dans une structure dédiée, sans verbatim brut et sans auto-promotion d’un statut provisoire vers un statut « validé humainement » ;
- un objet de domaine central `LearnerThemeMemory` ou équivalent, destiné à porter cette mémoire thématique gouvernée ;
- un endpoint / projection `GET /sessions/{id}/memory-summary` servant à exposer, côté produit, un résumé gouverné de la mémoire, jamais du verbatim brut.

Cette mémoire gouvernée est articulée avec :

- le référentiel métier et la logique RAG (qui restent centrés sur les documents actifs de formation, sans devenir la mémoire principale) ;
- les règles de validation humaine et de statuts (provisoire vs validé) pour éviter toute auto-certification implicite via la mémoire.

### 1.2 Réel audité — ce qui relève du même périmètre

Côté réel, tel qu’il ressort des docs 00–10, du glossaire d’alignement et de la note de lot courant :

- le service backend `MemoryConsolidator` (fichier `memoryconsolidator.py`, hooks post-conversation) est positionné comme consolidateur de mémoire inter-session ;
- le modèle / objet `LearnerThemeMemory` est mentionné dans le code et les docs comme support de mémoire thématique inter-session, mais n’est pas démontré comme injecté dans `build_hugo_turn` ;
- une **mémoire intra-session** est gérée via un service de type `build_session_memory` / `session_memory.py`, qui produit un résumé de fil courant distinct de la mémoire thématique inter-session ;
- l’endpoint `GET /hugo/sessions/{id}/memory-summary` expose une projection de mémoire thématique inter-session ;
- `00_HIERARCHIE_DOCUMENTAIRE.md` rappelle que, pour la mémoire / persistence, il faut repartir des modèles et services réels (mémoire de session, consolidateur, endpoint) plutôt que s’appuyer sur des lots mémoire historiques comme preuve.

Le domaine `20_memoire_gouvernee` **n’englobe pas** :

- la totalité du référentiel documentaire / RAG (couverts dans `30_referentiel_documentaire_rag`) ;
- la base de connaissances formateur (`TrainerKnowledgeItem`, ingestion, statuts) qui relève d’un autre domaine ;
- les objets de traces / preuves d’évaluation (domaine 70).

## 2. Cible 2.0 — doctrine mémoire gouvernée

### 2.1 Nature et rôle de la mémoire gouvernée

Dans la cible 2.0 :

- la mémoire est **thématique, structurée, gouvernée, référentiel-first**, et non assimilable à un historique brut ;
- le verbatim interne n’est qu’un **outil de récupération borné** pour quelques cas (contradictions, ambiguïtés, rappels ciblés) ;
- la consolidation est **inter-session**, côté backend, dans une structure dédiée (type `LearnerThemeMemory`), sans verbatim brut et sans auto-promotion du provisoire vers le « validé humainement » ;
- la projection côté produit se fait via un **résumé gouverné** exposé par un endpoint de type `GET /sessions/{id}/memory-summary`, avec uniquement des éléments partageables ou confirmables.

Dans les matrices 2.0 :

- `LearnerThemeMemory` incarne la mémoire thématique inter-session ;
- `MemoryConsolidator` est le service de consolidation inter-session ;
- `GET /sessions/{id}/memory-summary` est l’endpoint d’expo mémoire gouvernée côté UI.

### 2.2 Garde-fous de validation et d’usage

La doctrine relie fortement mémoire gouvernée et **validation humaine** :

- aucun item dérivé (mémoire, savoir formateur, trace) ne doit être auto-promu au statut « validé humainement » ;
- la promotion de statut doit résulter d’un **acte explicite** d’un rôle habilité ;
- la mémoire inter-session et les analytics sont consolidés **post-conversation**, pas en flux continu non gouverné ;
- la mémoire ne doit pas devenir un substitut à la validation humaine, ni une « vérité automatique » sur le niveau d’un apprenant.

### 2.3 Articulation avec référentiel et RAG

La mémoire gouvernée se situe au croisement :

- de l’expérience apprenant (thèmes, situations, objectifs travaillés) ;
- du référentiel métier (compétences, critères de maîtrise, erreurs fréquentes) ;
- du documentaire / RAG (documents actifs, overlays situés).

La doctrine insiste sur :

- le **référentiel** comme primaire pour orienter structuration, traces et overlays ;
- un **RAG** question-driven, centré sur des documents actifs, qui ne devient ni mémoire principale ni moteur de cours.

Le domaine `20_memoire_gouvernee` cible donc une **mémoire apprenant structurée** qui dialogue avec, mais ne se confond ni avec le RAG ni avec la base de connaissances formateur.

## 3. Réel observé — état des lieux mémoire

### 3.1 Services et objets identifiés dans le réel

Les éléments suivants sont consolidés côté réel :

- un service de consolidation `MemoryConsolidator` dans `memoryconsolidator.py` ;
- un modèle `LearnerThemeMemory` pour la mémoire thématique inter-session ;
- une mémoire intra-session via un service `build_session_memory` / `session_memory.py`, distinct de `LearnerThemeMemory` ;
- un endpoint `GET /hugo/sessions/{id}/memory-summary` côté API, qui expose aujourd’hui une projection inter-session ;
- une injection de mémoire de session dans le tour courant et dans UIState, décrite dans la note de lot courant.

### 3.2 Points fermes vs points à vérifier (avant réduction de périmètre)

Fermement étayé (avant prise en compte du lot courant) :

- existence des objets et services mémoire ;
- existence de l’endpoint `memory-summary` ;
- existence d’une mémoire de session injectée dans le tour et projetée dans UIState.

Restait à vérifier :

- le degré réel d’injection de `LearnerThemeMemory` dans `build_hugo_turn` ;
- la structure exacte et la granularité du contrat `memory-summary` ;
- la gouvernance fine des règles d’inclusion/exclusion (verbatim, niveaux de détail).

Ces points sont repris dans la section 7 comme `A_VERIFIER`.

## 3 bis. Réduction de périmètre pour le lot courant

Pour la trajectoire locale et le lot courant, un addendum méthodologique impose une réduction de périmètre mémoire :

- la capacité effectivement visée et prouvable à court terme est une **mémoire gouvernée intra-conversation**, construite côté backend, injectée dans le tour courant et projetée dans UIState ;
- la mémoire inter-sessions reste **préparée dans les contrats**, dans le vocabulaire et dans les points d’extension backend (`LearnerThemeMemory`, `MemoryConsolidator`, endpoint inter-session), mais n’est pas considérée comme livrée dans ce lot ;
- la documentation active de ce lot doit donc distinguer :

  - mémoire intra-conversation visée à court terme ;
  - préparation technique et documentaire de l’inter-sessions ;
  - inter-sessions effectivement implémenté, qui reste hors périmètre immédiat.

Ce changement de périmètre ne remet pas en cause la doctrine 2.0 complète, mais fixe une cible d’implémentation plus étroite pour ce lot.

## 4. Alignements, écarts et ambiguïtés majeurs

### 4.1 Alignements forts

- La cible 2.0 pose `LearnerThemeMemory` comme objet de mémoire thématique inter-session, et le réel utilise déjà ce nom pour un modèle.
- La cible prévoit un service `MemoryConsolidator`, et le réel dispose d’un fichier `memoryconsolidator.py` jouant ce rôle.
- La cible prévoit un endpoint de mémoire résumée, et le réel expose `GET /hugo/sessions/{id}/memory-summary`.
- La doctrine de **non-exposition de verbatim brut** comme mémoire principale est compatible avec le fait que la projection passe par des résumés et non par un historique brut.
- La note de lot courant confirme l’existence d’une mémoire de session construite côté backend et injectée dans le tour, alignée avec la réduction de périmètre intra-conversation.

### 4.2 Écarts et points partiels

- `LearnerThemeMemory` est bien positionné doctrinalement, mais son injection effective dans `build_hugo_turn` n’est pas démontrée : la mémoire inter-session reste **partiellement intégrée** au runtime.
- La doc historique ne distingue pas toujours clairement **mémoire intra-session** (fil courant) et **mémoire thématique inter-session** (consolidée), ce qui peut entraîner des confusions.
- Le contrat détaillé de `memory-summary` (champs, granularité, filtres) n’est pas encore canonisé dans les specs.
- La stratégie de validation humaine appliquée au contenu de mémoire gouvernée (promotion éventuelle de certains éléments vers des statuts plus forts) reste partielle.

### 4.3 Ambiguïtés et risques de confusion

- Frontière entre mémoire gouvernée apprenant (domaine 20) et référentiel / RAG (domaine 30).
- Granularité des items dans `LearnerThemeMemory` : résumé de séance, thèmes transverses, objectifs, etc.
- Application concrète des statuts (déclaré, dérivé provisoire, validé humainement) aux contenus de mémoire gouvernée.
- Risque de relire `memory-summary` comme preuve d’une mémoire complète et canonisée alors que le contrat n’est pas encore documenté finement.

## 5. Cible 2.0 complète vs cible d’implémentation lot courant

### 5.1 Cible 2.0 complète

On conserve la doctrine complète :

- mémoire thématique gouvernée inter-session ;
- consolidation post-conversation via `MemoryConsolidator` ;
- résumé gouverné exposé par un endpoint `memory-summary` ;
- articulation forte avec référentiel, RAG et validation humaine.

Cette cible reste la référence de long terme pour le domaine.

### 5.2 Cible d’implémentation retenue pour le lot courant

Conformément à la méthode de convergence et au plan CTO, la cible d’implémentation retenue pour le lot courant du domaine mémoire est volontairement **réduite à la mémoire gouvernée intra-conversation**.

Dans ce lot :

- la mémoire utile doit se comporter comme une **mémoire de conversation courante** : synthétique, discrète, pilotée backend, utile à la continuité du fil et non comme un historique brut ou un profil durable apprenant ;
- l’inter-sessions reste préparée dans les objets, les modèles et les contrats (`LearnerThemeMemory`, `MemoryConsolidator`, endpoint inter-session), mais ne doit pas être décrite comme déjà active dans la conduite du tour courant sans preuve d’audit complémentaire.

Le contrat JSON minimal à retenir pour cette mémoire intra-conversation est le suivant :

```json
{
  "session_memory": {
    "session_id": "<uuid>",
    "updated_at": "ISO datetime",
    "theme": {
      "label": "texte court lisible",
      "tags": ["string"]
    },
    "learning_objective": {
      "label": "objectif pédagogique courant",
      "status": "in_progress | reached | abandoned"
    },
    "facts_confirmed": [
      {
        "label": "fait ou décision confirmé dans le fil",
        "confirmed_at": "ISO datetime"
      }
    ],
    "open_points": [
      {
        "label": "question ou point encore ouvert",
        "priority": "normal | blocking"
      }
    ],
    "pending_actions": [
      {
        "label": "action à faire dans ce fil",
        "due_in_turns": 3
      }
    ],
    "memory_scope": "session"
  }
}
```

Ce contrat doit être lu comme un **contrat de convergence lot courant** : assez précis pour guider les ajustements backend, UIState et tests, sans transformer cette cible en fait déjà prouvé dans tous les artefacts runtime.

Les garde‑fous applicables sont :

- pas de verbatim brut dans la mémoire gouvernée ;
- pas de champs P0 bruts exposés au front via `session_memory` ou ses projections ;
- pas de description de `LearnerThemeMemory` comme mémoire active du fil courant tant que ce point n’est pas démontré ;
- pas de glissement où `memory-summary` serait automatiquement lu comme preuve d’une mémoire thématique complète déjà stabilisée ;
- séparation explicite entre mémoire de session intra‑conversation et mémoire thématique inter‑sessions dans les contrats et prompts.

## 6. Décisions documentaires corrigées

### 6.1 Décision directrice

La doctrine 2.0 reste la **structure canonique** du domaine mémoire, mais la documentation active du lot courant doit désormais expliciter que la capacité réellement visée et prouvée est d’abord une **mémoire gouvernée intra-conversation**, construite côté backend, injectée dans le tour courant, et exposée au produit sous forme gouvernée.

### 6.2 Noms à garder et noms réels à injecter

Les termes canoniques à garder sont :

- mémoire gouvernée ;
- mémoire intra-conversation ;
- mémoire thématique inter-session ;
- `LearnerThemeMemory` ;
- `MemoryConsolidator` ;
- résumé mémoire gouverné ;
- verbatim interne borné ;
- validation humaine.

Les noms réels qui doivent apparaître explicitement dans la doc technique ou les annexes sont :

- `build_session_memory`, `session_memory.py` ;
- `MemoryConsolidator`, `memoryconsolidator.py` ;
- modèle `LearnerThemeMemory` ;
- endpoint `GET /hugo/sessions/{id}/memory-summary` ;
- `build_hugo_turn` pour l’injection runtime ;
- `ui-state`, `persistent_objects` pour la projection produit.

### 6.3 Distinctions à rendre explicites

La documentation doit désormais distinguer explicitement :

- mémoire intra-conversation injectée au tour courant (contrat `session_memory`) ;
- mémoire thématique inter-session persistée (`LearnerThemeMemory`) ;
- projection API `memory-summary` (actuellement inter-session) ;
- projection produit via UIState / `persistent_objects`.

Elle doit aussi cesser de laisser entendre que `memory-summary` serait forcément la source directe de la mémoire visible apprenant dans le front actuel, tant que cet usage n’est pas démontré.

## 7. Points A_VERIFIER

Restent explicitement `A_VERIFIER` :

- existence de flags ou variantes runtime qui modifieraient la source mémoire injectée au tour (session vs thème) ;
- existence d’autres écrans front appelant `memory-summary` directement ;
- gouvernance fine des règles d’inclusion/exclusion avant exposition API (notamment pour tout contenu dérivé de verbatim interne) ;
- validation bout-en-bout via tests API et scénarios front (Chromium ou équivalent) ;
- degré exact d’injection ou non de `LearnerThemeMemory` dans `build_hugo_turn` pour la conduite du tour ;
- contenu détaillé de `LearnerState.summary` et usages, pour éviter toute exposition indirecte de verbatim.

Tout point dépendant du runtime distant, d’une variante non auditée ou d’un comportement front non recoupé doit rester marqué `A_VERIFIER`.

## 8. Backlog d’actions corrigé (vue noyau)

### 8.1 Actions DOC

- **D1 — Contrat mémoire intra-conversation minimal**  
  Rédiger et intégrer le contrat JSON ci-dessus dans la spec interface (section UIState / mémoire) et dans les docs de domaine comme contrat de convergence lot courant.

- **D2 — Corriger la doc domaine 20**  
  Expliciter dans ce rapport et dans les décisions de domaine que l’injection runtime confirmée porte sur la mémoire de session, et non, à ce stade prouvé, sur `LearnerThemeMemory` inter-session.

- **D3 — Canoniser le contrat minimal de `memory-summary`**  
  À partir d’un audit code futur, documenter le contrat réel dans la spec interface ou un complément, en distinguant bien mémoire de session et mémoire inter-session.

### 8.2 Actions CODE

- **C1 — Clarifier explicitement les points d’injection runtime**  
  Distinguer dans le code et les commentaires de convergence `session_memory` déjà injectée et `LearnerThemeMemory` inter-session si non injectée au tour.

- **C2 — Ajouter un test de non-régression sur l’absence de verbatim dans `memory-summary`**  
  Verrouiller le garde-fou déjà observé selon lequel la projection mémoire ne doit pas exposer de verbatim brut.

- **C3 — Auditer l’usage exact de `LearnerThemeMemory` dans l’orchestration de tour**  
  Lever les `A_VERIFIER` restants sur l’injection mémoire inter-session dans `build_hugo_turn`.

### 8.3 Actions OPS

- **O1 — Préparer un template Cursor d’audit mémoire intra-conversation**  
  Maintenir un prompt standard pour auditer les services mémoire (session, consolidation, endpoint) et les contrats JSON en suivant la méthode (réel vs cible, écarts, A_VERIFIER).

- **O2 — Intégrer ces décisions dans le handover CTO**  
  Rattacher ce dossier au plan CTO de convergence pour que les priorités mémoire (intra-conversation d’abord) soient visibles et pilotables.

---

## 9. Mise à jour cluster 11 — verrouillage runtime vs Encoors

**Sources :** `cluster11_verrouillage_runtime_vs_encoors_resultats.md` · `encoors_oracle.py` (M1) · `audit_rls_prod_template.sql`.

| Point | Statut cluster 11 |
|---|---|
| memory-summary smoke local | **ALIGNE** — PASS |
| Parité memory-summary Encoors | **A_VÉRIFIER** — oracle M1 auth |
| Option A `?scope=intra` | **ADR** — couronne si arbitrage |
| Injection LLM mémoire | **Absente** — accepté lot courant |

---

## 10. Mise à jour cluster 13 — articulation mémoire ↔ RAG

**Sources :** `cluster13_rag_referentiel_documentaire_plan_resultats.md` · hiérarchie contexte v1.

| Point | Statut cluster 13 |
|---|---|
| Ordre doctrinal état > mémoire > RAG | **DOC** — contrat v1 cluster 13 |
| SessionMemoryContract au tour | **ALIGNE** — `build_session_memory` post-RAG sélection |
| Mémoire inter-session au tour | **Absente** — inchangé |
| RAG comme renfort (non mémoire) | **ALIGNE** — `should_use_rag` gating |
| Exposition mémoire via RAG front | **ABSENT** — conforme |

---