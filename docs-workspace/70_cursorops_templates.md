## Template Cursor — Audit évaluation / traces / preuves (domaine 70)

### 0. Objectif du prompt

Auditer le comportement réel de la branche **évaluation / traces / preuves** dans le runtime local Hugo, en partant du code et des endpoints, en la comparant à la cible 2.0 minimale, et en identifiant clairement ce qui est :

- réellement implémenté aujourd’hui ;
- partiellement en place ;
- absent ou à traiter comme **contrat cible** seulement.

L’objectif n’est pas d’enrichir tout de suite la chaîne d’évaluation, mais de :

- stabiliser la compréhension du **flux d’évaluation** (endpoints, états) ;
- clarifier ce que les traces et preuves exposent réellement ;
- préparer un **contrat minimal** de branche terminale d’évaluation, honnête (pas de certification autonome).

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
- `docs-workspace/ecarts — 70_evaluation_traces_preuves.md`
- `docs-workspace/glossaire_alignement_hugo_reel_vs_spec.md`
- `docs-workspace/03_ETAT_PRODUIT_REEL.md`
- `docs-workspace/05_ECARTS_DOC_CODE_PRODUIT.md`

L’audit doit distinguer **cœur** (branche terminale utilisable, mapping EvaluationTrace doc) et **couronne** (trace exportable enrichie, D9bis). Ne pas promouvoir en IMPLÉMENTÉ ce qui est CIBLE / A_VÉRIFIER dans la synthèse globale.

Rappels méthodologiques impératifs :

- Séparer explicitement dans la réponse :
  - réel observé ;
  - cible 2.0 ;
  - écarts confirmés ;
  - points `A_VERIFIER` ;
  - hypothèses de convergence éventuelles.
- Ne jamais utiliser la spec 2.0 ou le glossaire comme preuve autonome d’implémentation.
- Partir du **backend** (`hugo_back`) pour décrire le comportement réel (code, tests, endpoints), puis seulement le front (`hugo-hugolucia`) et les docs `docs-workspace`.

---

### 2. Tâches demandées à Cursor

#### 2.1. Cartographier les endpoints d’évaluation

1. Dans `hugo_back`, localiser tous les endpoints liés à l’évaluation et aux traces, notamment (noms à adapter à ce qui existe réellement) :
   - `request-evaluation` ou équivalent ;
   - `finalize-evaluation` ou équivalent ;
   - `evaluation-readiness` ou équivalent ;
   - `generate-trace` ou équivalent ;
   - tout endpoint exposant des traces / preuves / évaluations (lecture, génération, consultation).
2. Pour chaque endpoint identifié, produire une fiche :
   - route exacte (méthode HTTP + path) ;
   - fonctions / vues backend correspondantes ;
   - modèles / services principaux impliqués (par exemple `LearnerEvaluationRecord`, `Trace`, `Evidence`, etc.) ;
   - tests associés s’ils existent (fichiers de tests, scénarios couverts).

#### 2.2. Décrire le flux d’évaluation côté backend

À partir du code :

1. Décrire le **flux nominal d’évaluation** du point de vue backend, étape par étape.  
   Par exemple (à adapter au code réel) :
   - comment l’état “prêt à évaluer” est déterminé (endpoint `evaluation-readiness` ou logique interne) ;
   - comment une demande d’évaluation est lancée (`request-evaluation`) ;
   - comment une évaluation est finalisée (`finalize-evaluation`) ;
   - comment une trace ou une preuve est générée (`generate-trace` ou équivalent).
2. Pour chaque étape :
   - expliquer quelle donnée d’entrée est requise ;
   - quels objets métier sont manipulés ou créés ;
   - quels changements d’état observables côté backend (statuts, flags, champs, enregistrements).
3. Identifier les points où le code **prévoit** des comportements (statuts, callbacks, stockage de preuves) mais où l’implémentation semble partielle ou peu utilisée.

#### 2.3. Objets d’évaluation, traces et preuves

1. Localiser les modèles et objets principaux liés à l’évaluation, par exemple :
   - `LearnerEvaluationRecord` (ou équivalent) ;
   - `Trace` ;
   - `Evidence` ;
   - tout autre objet qui semble porter des traces ou preuves d’évaluation.
2. Pour chaque modèle :
   - donner les champs principaux et leur rôle ;
   - expliquer comment ils sont alimentés par les endpoints d’évaluation ;
   - préciser s’ils sont **effectivement** utilisés dans le runtime courant ou s’ils sont surtout “préparés”.
3. Dégager un **mapping doctrinal minimal** :
   - quels objets réels correspondent aux concepts 2.0 “EvaluationTrace”, “Trace”, “Evidence”, “LearnerEvaluationRecord”, même de manière partielle.

#### 2.4. Projection vers le produit (UI / UIState)

1. Dans `hugo-hugolucia` (front) et/ou dans les services UIState backend, identifier :
   - comment l’état d’évaluation est exposé à l’UI (par exemple via `ui-state`, `buildUiState`, champs d’UIState liés à l’évaluation) ;
   - quels CTA (boutons, actions) sont reliés aux endpoints d’évaluation (`request-evaluation`, `finalize-evaluation`, etc.).
2. Décrire :
   - quels états sont visibles pour l’apprenant (prêt / en attente / en cours / finalisé) ;
   - s’il existe des messages de blocage ou d’inéligibilité (et sur quoi ils reposent) ;
   - si l’UI montre ou non des “preuves” ou “traces” au sens métier (et sous quelle forme).

> Si Chromium est disponible, proposer en plus un court parcours dans le front local pour vérifier que les CTA d’évaluation et les états visibles correspondent bien à ce que le backend expose (nom des boutons, messages affichés, etc.).

#### 2.5. Réel vs cible minimale d’évaluation

En t’appuyant sur `ecarts — 70_evaluation_traces_preuves.md` et la méthode :

1. Résumer la **cible 2.0 minimale** pour ce lot :
   - branche terminale d’évaluation **utilisable** ;
   - validation finale **humaine**, pas de certification autonome ;
   - trace minimale, mais standardisable ;
   - pas de sur-promesse sur la richesse de la trace.
2. Mettre en regard, pour les grands axes :
   - flux d’évaluation (endpoints, états) ;
   - objets de trace / preuve ;
   - projection produit (UI / UIState, CTA).
3. Pour chaque axe, lister :
   - ce qui est confirmément aligné ;
   - ce qui est partiel ;
   - ce qui est absent et relève d’un **nouveau contrat** à définir.

---

### 3. Synthèse structurée attendue

La réponse doit contenir ces sections explicites :

1. `## Sources mobilisées`  
   - fichiers backend (paths) ;  
   - endpoints ;  
   - modèles ;  
   - fichiers front / UIState ;  
   - docs `docs-workspace` utilisées.

2. `## Réel confirmé`  
   - flux nominal d’évaluation (étapes, endpoints, objets) tel qu’il ressort du code ;  
   - objets réellement alimentés (évaluation, traces, preuves) ;  
   - ce qui est effectivement exposé ou utilisable côté produit.

3. `## Cible 2.0 minimale pour ce lot`  
   - rappel synthétique (1–2 paragraphes) de la cible raisonnable décrite dans les docs (branche utilisable, validation humaine, trace minimale, pas de certification autonome).

4. `## Écarts confirmés`  
   - liste courte, structurée par thème (flux, objets, projection produit) ;  
   - mention explicite des statuts possibles (ALIGNE, ALIGNE DOC PARTIEL, PARTIEL, A_VERIFIER, ABSENT/NOUVEAU CONTRAT) si utile.

5. `## Points A_VERIFIER`  
   - ce que le corpus lu ne permet pas de trancher sans tests ou instrumentation supplémentaires (par exemple : activation de certains flags, comportements en prod distante).

6. `## Prochaine sortie utile (DOC / CODE / OPS)`  
   Proposer quelques actions très concrètes, par exemple :
   - DOC : définir un **contrat minimal** d’état d’évaluation et de trace exposable (schéma JSON, champs UIState, règles de discours produit) ;  
   - CODE : clarifier ou compléter le flux sur 1–2 endpoints critiques (vérifications, statuts, mapping des objets) ;  
   - OPS : préparer un template de tests ou un second prompt Cursor ciblé sur un endpoint.

---

### 4. Garde-fous à respecter dans la réponse Cursor

La réponse ne doit pas :

- présenter Hugo comme système de certification autonome ;
- traiter des objets non utilisés comme preuve d’implémentation complète ;
- confondre trace technique et preuve pédagogique validée ;
- recentrer la vérité sur le front, sans recouper avec le backend et les tests.

La réponse doit rester :

- explicite sur les zones `A_VERIFIER` ;
- fidèle au code et aux docs du workspace ;
- prudente sur la généralisation des comportements observés.

---

## Template Cursor — Audit CTA synthèse / évaluation (lot 1)

### 0. Objectif du prompt

Auditer le comportement réel des **CTA de synthèse et d’évaluation** dans Hugo local (backend + UIState + front), en vérifiant l’alignement avec :

- le contrat UIState minimal `cta_evaluation` / `cta_synthesis` du lot 1 ;
- la doctrine “évaluation utilisable, validation finale humaine, pas de certification autonome” ;
- la séparation nette entre état backend, projection UIState et discours produit.

L’objectif n’est pas de refondre toute la chaîne d’évaluation 2.0, mais de décrire précisément ce qui existe et de préparer les patchs CODE/TEST pour le lot 1.

---

### 1. Contexte

Tu travailles dans le workspace local suivant :

- `~/Desktop/zone de travail hugo/docs-workspace`
- `~/Desktop/zone de travail hugo/hugo_back`
- `~/Desktop/zone de travail hugo/hugo-hugolucia`
- `~/Desktop/zone de travail hugo/hugo-main`

Les documents de référence à respecter sont :

- `docs-workspace/00_HIERARCHIE_DOCUMENTAIRE.md`
- `docs-workspace/DOC_METHODO_REFERENCE_CONVERGENCE_HUGO_REVISE.md`
- `docs-workspace/10_runtime_p0_progression_uistate_note_lot_courant_cta_synthese_evaluation.md`
- `docs-workspace/ecarts — 70_evaluation_traces_preuves.md`
- `docs-workspace/specs-interface-2.0.md`
- `docs-workspace/plan_documentation_cto_convergence_hugo.md`

Rappels :

- Séparer explicitement : réel observé, cible 2.0, cible minimale lot 1, écarts confirmés, `A_VERIFIER`, hypothèses.
- Le lot 1 vise des CTA utilisables, pas une certification autonome par Hugo.
- L’UI apprenant doit être pilotée par `ui_state.cta_*`, pas par du P0 ni par une logique parallèle côté front.

---

### 2. Fichiers à ouvrir avant d’analyser

Ouvre au minimum :

- `docs-workspace/10_runtime_p0_progression_uistate_note_lot_courant_cta_synthese_evaluation.md`
- `docs-workspace/specs-interface-2.0.md`
- `docs-workspace/ecarts — 70_evaluation_traces_preuves.md`
- `hugo_back/apps/hugo/services/ui_state_builder.py` (ou équivalent)
- fichiers d’API qui portent :
  - `request-evaluation`
  - `finalize-evaluation`
  - `evaluation-readiness`
  - `generate-trace`
- fichiers de modèles liés à l’évaluation (`LearnerEvaluationRecord`, `Trace`, `Evidence`, etc.)
- tests backend existants sur l’évaluation si présents
- composants front apprenant qui affichent les boutons de synthèse / évaluation (`hugo-hugolucia`)

---

### 3. Contrat cible minimal UIState (rappel lot 1)

Référence pour le lot :

```json
{
  "cta_evaluation": {
    "evaluation_ready_status": "eligible | blocked_missing_data | blocked_min_turns_not_reached | blocked_context_incomplete | blocked_other",
    "blocking_reasons": ["liste courte de raisons lisibles, non P0"],

    "endpoints": {
      "request_evaluation": "/api/hugo/sessions/{session_id}/request-evaluation/",
      "finalize_evaluation": "/api/hugo/sessions/{session_id}/finalize-evaluation/",
      "evaluation_readiness": "/api/hugo/sessions/{session_id}/evaluation-readiness/"
    },

    "ui": {
      "show_evaluation_button": true,
      "button_label": "Demander une évaluation",
      "button_disabled": false,
      "helper_text": null
    },

    "last_evaluation": {
      "status": "none | in_progress | completed | failed",
      "completed_at": "ISO datetime ou null"
    }
  },

  "cta_synthesis": {
    "synthesis_ready_status": "eligible | blocked_not_enough_content | blocked_context_incomplete",
    "blocking_reasons": ["liste courte de raisons lisibles, non P0"],

    "endpoints": {
      "generate_synthesis": "/api/hugo/sessions/{session_id}/generate-synthesis/"
    },

    "ui": {
      "show_synthesis_button": true,
      "button_label": "Obtenir une synthèse",
      "button_disabled": false,
      "helper_text": null
    }
  }
}
```

Contraintes :

- `*_ready_status` sont des énums fermés.
- `blocking_reasons` contient des messages lisibles, sans dumps techniques ni P0.
- Le front ne rajoute pas de logique métier en dehors de ce contrat.

---

### 4. Tâches demandées à Cursor — Backend

#### 4.1 Cartographier les endpoints d’évaluation

1. Lister tous les endpoints d’évaluation et de synthèse réellement présents (noms exacts, méthodes HTTP, paths).
2. Pour chacun, donner :
   - la vue ou fonction backend associée ;
   - les services métier utilisés ;
   - les modèles principaux manipulés ;
   - les tests existants, s’il y en a.

#### 4.2 Décrire le flux d’évaluation lot 1

1. Décrire le flux nominal d’évaluation côté backend, étape par étape, à partir du code :
   - détermination de l’éligibilité (`evaluation-readiness` ou logique équivalente) ;
   - déclenchement (`request-evaluation`) ;
   - génération de trace (`generate-trace`) ;
   - finalisation (`finalize-evaluation`).
2. Pour chaque étape, préciser :
   - les entrées requises ;
   - les objets créés / mis à jour ;
   - les changements d’état (statuts, champs, flags).
3. Identifier ce qui est effectivement utilisé dans le runtime courant et ce qui est surtout préparé.

#### 4.3 Projection des CTA dans UIState

1. Dans `ui_state_builder` (ou équivalent), expliquer :
   - quels champs de progression / readiness alimentent `cta_evaluation` et `cta_synthesis` ;
   - comment `*_ready_status`, `blocking_reasons`, `ui.show_*_button`, `ui.button_disabled` et `last_evaluation` sont calculés.
2. Dire explicitement :
   - si le contrat UIState du lot est déjà respecté ;
   - où il manque des champs, des états ou un nettoyage des `blocking_reasons`.

---

### 5. Tâches demandées à Cursor — Front (optionnel mais recommandé)

Si possible, lancer le front local et :

1. Vérifier quels boutons / CTA sont visibles pour l’apprenant :
   - libellés des boutons ;
   - états (actif, grisé, absent) dans quelques scénarios simples.
2. Confirmer que :
   - l’affichage des CTA dépend bien de `ui_state.cta_*` ;
   - aucune logique parallèle d’éligibilité n’est recodée côté front ;
   - aucun texte produit ne parle de “certification automatique” ou d’équivalents.

---

### 6. Analyse réel vs cible lot 1

En t’appuyant sur la note lot courant et les écarts domaine 70 :

1. Pour `cta_evaluation` :
   - comparer `evaluation_ready_status`, `blocking_reasons`, `last_evaluation` et les endpoints réels avec le contrat cible ;
   - qualifier pour chaque rubrique : ALIGNE, ALIGNE_DOC_PARTIEL, PARTIEL, A_VERIFIER, ABSENT / NOUVEAU CONTRAT.
2. Pour `cta_synthesis` :
   - faire le même travail sur `synthesis_ready_status`, `blocking_reasons`, endpoints et `ui`.

3. Sur le discours produit :
   - vérifier que la documentation et les textes ne présentent pas Hugo comme certificateur autonome ;
   - identifier les formulations à corriger le cas échéant.

---

### 7. Structure de réponse attendue

Structure ta réponse avec exactement les sections suivantes :

- `## Sources mobilisées`
- `## Réel confirmé (backend + UIState + front)`
- `## Cible lot courant (CTA mémoire & éval)`
- `## Écarts confirmés`
- `## Points A_VERIFIER`
- `## Diffs backend proposés`
- `## Tests proposés`
- `## Backlog DOC / CODE / OPS`

---

### 8. Backlog DOC / CODE / OPS

Dans la section `## Backlog DOC / CODE / OPS`, liste les actions sous forme de tableau Markdown avec les colonnes :

- `ID` (préfixé CTA‑, ex. `CTA‑C01`)
- `Type` (`DOC`, `CODE`, `OPS`)
- `Pri` (`P0`, `P1`, `P2`)
- `Source` (référence à une section de ta réponse)
- `Intitulé court`
- `Livrable attendu`

Les actions doivent couvrir au minimum :

- DOC : ajustements de `specs-interface-2.0.md` et des notes produit si nécessaire ;
- CODE : complétion ou correction de `build_ui_state` et des services d’évaluation pour respecter le contrat ;
- TESTS : tests backend et front sur les énums, les raisons de blocage et l’usage exclusif de `ui_state.cta_*`.

---

### 9. Discipline de méthode

Dans ta réponse :

- Ne présente jamais Hugo comme système de certification autonome.
- Distingue clairement : flux d’évaluation réel, surface CTA lot 1, doctrine 2.0 complète.
- Ne recentre pas la vérité sur le front : la source reste le backend et l’UIState.
- Marque explicitement comme `A_VERIFIER` tout comportement dépendant d’un runtime distant, d’un flag ou d’une configuration non visible dans le corpus.