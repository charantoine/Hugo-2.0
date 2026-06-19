
## NOTE — Mémoire gouvernée (lot 1, intra‑conversation)

### 0. Objet de la note

Cette note décrit la **mémoire gouvernée intra‑conversation** visée dans le lot courant Hugo local : ce qui est effectivement livré, ce qui reste préparé (inter‑sessions) et les règles à ne pas violer côté code et produit.[^1][^2]
Elle sert de contrat de convergence entre backend, orchestrateur, UIState et documentation, sans prétendre que la cible 2.0 complète est déjà implémentée.[^3][^1]

> Convention de lot  
> Cette note couvre la **Vague 1** du plan de convergence (`plan_documentation_cto_convergence_hugo.md`). Les Vagues 2 et 3 (encadrants, exports, décisions structurantes) et la couronne optionnelle sont synthétisées dans `synthese_globale_ecarts_par_domaine.md` et détaillées dans `cluster2_matrice_runtime_vs_cible.md` (V3).

***

### 1. Corpus mobilisé

- Code :
    - `hugo_back/apps/hugo/services/session_memory.py` (`build_session_memory`)
    - `domain/schemas.py` (`SessionMemorySummary`, schémas mémoire)
    - `hugo_orchestrator.py` (injection runtime)
    - `ui_state_builder.py` (projection dans `ui_state.session_memory`)
    - `views_sessions.py` (`SessionMemorySummaryView`)
    - `memory_consolidator.py` (consolidation inter‑session, hors périmètre lot).[^2]
- Docs :
    - `docs-workspace/ecarts — 20_memoire_gouvernee .md` (rapport d’écarts + matrice + décisions)[^2]
    - `plan_documentation_cto_convergence_hugo.md` (ordre de production, réduction de périmètre intra‑conversation).[^1]
- Tests existants :
    - `test_p0_v17_flow.py` (garde‑fou `memory_scope == "governed_structured"`)
    - `test_memory_consolidation.py` (consolidation inter‑session, statuts `DERIVED_PROVISIONAL`).[^2]

***

### 2. Réel observé dans le code

#### 2.1 Producteur intra‑session : `build_session_memory`

Dans `session_memory.py`, `build_session_memory(session: HugoSession, max_messages=6) -> SessionMemorySummary` :[^2]

- lit un `LearnerState` inter‑session (cache consolidé) pour `summary`, `open_action_items`, etc. ;
- lit les derniers `HugoMessage` apprenant filtrés par `(organisation_id, learner_id, group_id)` sans contrainte `session_id` (agrégation cross‑sessions) ;
- n’utilise que les champs structurés `turn_state` des payloads LLM et **jamais `message.content`**.[^2]

La structure réelle `SessionMemorySummary` comprend notamment :[^2]

- `summary: str` — `LearnerState.summary` ou fallback générique ;
- `active_themes: list[str]` — `turn_state.covered_points` des derniers messages apprenant ;
- `carry_over_points: list[str]` — `turn_state.remaining_open_points` ;
- `open_action_items: list[str]` — labels aplatis issus de `LearnerState.open_action_items` ;
- `last_session_at: str | None` — session précédente du même apprenant/groupe ;
- `sessions_considered: int` — nombre de sessions distinctes dans les payloads lus ;
- `validated_traces_count: int` ;
- `memory_scope: "governed_structured"` (constante).[^2]

Points structurants :

- pas de `session_id` ni `updated_at` dans l’objet produit ;
- la requête messages n’est pas strictement intra‑session → **fuite inter‑session** dans un service présenté comme mémoire de fil ;
- `LearnerState` est un cache **inter‑session**, pas strictement intra‑conversation ;
- aucun accès à `message.content` → pas de verbatim brut dans ce module.[^2]


#### 2.2 Injection runtime

Dans `hugo_orchestrator.py` :[^2]

- `session_memory = build_session_memory(session)` est appelé dans `build_hugo_turn` **avant** la persistance du tour courant, la mémoire reflète donc l’état $N-1$ ;
- `session_memory` est injecté dans `HugoTurn.session_memory` et dans `UiState.session_memory = session_memory.to_dict()` ;
- ces champs sont exposés dans la réponse message via `_serialize_message_response` (`session_memory` + `ui_state.session_memory`).[^2]

`LearnerThemeMemory` n’est ni importé ni utilisé dans `hugo_orchestrator.py` → pas d’injection inter‑session au tour courant (confirmé par lecture statique).[^2]

#### 2.3 Endpoint `GET /hugo/sessions/{session_id}/memory-summary/`

Dans `views_sessions.py`, `SessionMemorySummaryView` :[^2]

- lit des `LearnerThemeMemory` filtrés sur `(organisation_id, learner_id)` ;
- renvoie une liste de thèmes avec `theme_key`, `stabilised_points`, `open_loops`, `persistent_difficulties`, `knowledge_status`, `last_conversation_id`, `updated_at`.[^2]

Constat critique : cet endpoint **expose la mémoire thématique inter‑session** (`LearnerThemeMemory`), pas la mémoire intra‑conversation produite par `build_session_memory` ; le nom `memory-summary` est trompeur pour le lot courant.[^2]

#### 2.4 Projection front actuelle

Sur le front apprenant :[^2]

- `ui_state.session_memory` contient `SessionMemorySummary.to_dict()` (résumé gouverné, sans verbatim) ;
- `ui_state.persistent_objects['session-memory']` expose `memory.summary` seulement ;
- `ui_state.scene_progress` expose `covered_points` / `remaining_open_points` (codes internes, non verbatim mais vocabulaire technique) ;
- la réponse message contient `turn_state.to_dict()` complet (P0), ce qui expose du P0 au client, hors périmètre mémoire gouvernée mais important pour la règle globale “pas de P0 au front”.[^2]

`GET /ui-state/` exploite des branches thématiques contractuelles mais ne reconstruit pas encore une mémoire de fil courant canonisée.[^2]

#### 2.5 Tests existants

- `test_p0_v17_flow.py` vérifie que `turn.session_memory.memory_scope == "governed_structured"`.[^2]
- il n’existe pas de `test_session_memory.py` ni de tests pour :
    - la structure JSON projetée ;
    - l’absence de verbatim ;
    - la cohérence de l’endpoint `memory-summary` avec la doctrine.[^2]

***

### 3. Cible 2.0 et réduction pour le lot

#### 3.1 Doctrine 2.0 mémoire gouvernée

Selon la spec canonique et le domaine 20 :[^2]

- mémoire gouvernée = mémoire thématique, structurée, gouvernée, **référentiel‑first**, distincte d’un simple historique brut ;
- ordre de récupération de contexte : état apprenant → mémoire thématique → verbatim interne born → overlay référentiel → documentaire ;
- consolidation inter‑session post‑conversation côté backend, dans une structure dédiée (`LearnerThemeMemory`), sans verbatim brut ni auto‑promotion au statut validé humainement ;
- exposition via un endpoint de type `GET .../memory-summary` renvoyant un **résumé gouverné** partageable.[^2]


#### 3.2 Cible retenue pour le lot courant

Le plan de convergence réduit explicitement le périmètre :[^1][^2]

- la mémoire gouvernée visée dans ce lot est **uniquement intra‑conversation** :
    - utile à la continuité du fil courant ;
    - produite et mise à jour côté backend ;
    - sans exposer de verbatim brut ni de champs P0 ;
    - sans dépendance runtime à une mémoire inter‑session injectée dans l’orchestrateur.[^1][^2]
- la mémoire inter‑session (`LearnerThemeMemory`, `MemoryConsolidator`, endpoint inter‑session) reste doctrinale et préparée, mais **hors périmètre d’implémentation immédiat** pour la conduite du tour courant.[^1][^2]

Cible contractuelle intra‑conversation (schéma minimal) :[^1][^2]

- `session_id`, `updated_at`
- `theme` : label lisible + quelques tags thématiques
- `learning_objective` : objectif courant + statut `in_progress|reached|abandoned`
- `facts_confirmed[]` : faits / décisions confirmés et datés
- `open_points[]` : questions / boucles ouvertes, avec `priority` simple
- `pending_actions[]` : actions à réaliser dans ce fil, avec horizon en tours.

***

### 4. Alignement rubrique par rubrique vs contrat cible

À partir de l’audit :[^2]


| Rubrique contrat | Statut | Réel observé |
| :-- | :-- | :-- |
| `session_id` | Absent | Non présent dans `SessionMemorySummary`. |
| `updated_at` | Absent | Non présent. |
| `theme.label` + `theme.tags` | Partiel | `active_themes` = codes (`episode_described`, etc.), pas de label lisible ni tags ; label ailleurs. |
| `learning_objective.*` | Absent | `active_objective` existe dans `ConversationProgress`, pas dans `session_memory`. |
| `facts_confirmed[]` | Absent | `active_themes` ≈ points couverts, sans `confirmed_at` ni typage “fait confirmé”. |
| `open_points[]` + priorité | Partiel | `carry_over_points` = labels sans `priority`. |
| `pending_actions[]` | Partiel | `open_action_items` = strings, sans `due_in_turns`. |
| Pas de verbatim brut | Aligné | Aucun `message.content` lu dans `session_memory`. |
| Pas de P0 dans mémoire | Aligné | `session_memory.to_dict()` ne contient pas de P0 ; P0 seulement dans `turn_state` exposé séparément. |
| Endpoint fil courant dédié | Absent | `memory-summary` = inter‑session (`LearnerThemeMemory`), pas mémoire du fil. |


***

### 5. A_VERIFIER

Points à garder explicitement ouverts :[^2]

- contenu réel de `LearnerState.summary` et usages (risque de verbatim si réinjecté dans un résumé du fil) ;
- impact produit d’un **filtrage strict par `session_id`** dans `build_session_memory` (perte de continuité cross‑sessions actuelle) ;
- usages réels de `GET /hugo/sessions/{session_id}/memory-summary/` côté front ou outils annexes ;
- besoin éventuel de reconstruire la mémoire de session dans `GET /ui-state/` pour le rafraîchissement sans nouveau message ;
- influence des flags runtime sur `turn_state` et donc sur les points couverts / ouverts consommés par la mémoire.

***

### 6. Décisions et contrat lot courant

#### 6.1 Décisions doctrinales

- La mémoire livrée dans ce lot est :
    - une mémoire **intra‑conversation gouvernée**, pilotée backend, non verbatim ;
    - utilisée uniquement pour la continuité du fil courant ;
    - exposée via `session_memory` dans la réponse message et via `ui_state.session_memory`.[^1][^2]
- La mémoire inter‑session (`LearnerThemeMemory`, `MemoryConsolidator`, endpoint inter‑session) est **préparée mais non activée** dans la conduite du tour courant, et doit être documentée comme telle.[^1][^2]
- Tout document ultérieur doit distinguer explicitement :
    - mémoire intra‑session (fil courant)
    - mémoire thématique inter‑session
    - RAG documentaire
    - base de connaissances formateur.[^1][^2]


#### 6.2 Contrat JSON minimal intra‑conversation

Contrat retenu comme cible de convergence pour `session_memory` :[^1][^2]

```json
{
  "session_id": "<uuid>",
  "updated_at": "ISO datetime",
  "theme": {
    "label": "texte court lisible",
    "tags": ["string"]
  },
  "learning_objective": {
    "label": "objectif pédagogique courant (phrase courte)",
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
      "label": "question ou point encore ouverte",
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
```

- Implémenté via un nouvel objet de domaine (par ex. `SessionMemoryContract`) embarqué dans ou à côté de `SessionMemorySummary`, de façon **additive**.[^2]
- Produit côté backend, consommé via `ui_state.session_memory` et, si besoin, via un endpoint fil courant distinct de la mémoire inter‑session.[^1][^2]


#### 6.3 Interdits techniques et produit

- ne jamais exposer de **verbatim brut** (`message.content` complet) dans `session_memory` ni dans tout endpoint présenté comme mémoire gouvernée ;[^1][^2]
- ne pas exposer de champs **P0 bruts** dans la mémoire gouvernée ou autres structures destinées au front (hors surfaces de debug explicites) ;[^1][^2]
- ne pas documenter la mémoire inter‑session comme “déjà injectée” dans `build_hugo_turn` tant que l’audit ne le prouve pas ;[^2]
- ne pas présenter la mémoire gouvernée comme trace ou évaluation automatique : c’est un support de continuité et de contexte, pas une preuve.[^1][^2]

***

### 7. Prochaines actions (backlog lot)

Les décisions de cette note alimentent directement le backlog CTO :[^1][^2]

- **DOC**
    - intégrer ce contrat dans `specs interface 2.0` (section UIState / mémoire) ;
    - enrichir `speccanoniquehugo20.md` avec la distinction intra vs inter‑session et le mapping vers `buildsessionmemory`, `LearnerThemeMemory`, `memoryconsolidator.py`.[^1][^2]
- **CODE**
    - implémenter le contrat `session_memory` dans `session_memory.py` et son injection orchestrateur de façon additive ;
    - ajuster `SessionMemorySummaryView` pour distinguer clairement `session_memory` (fil courant) et `theme_memories` (inter‑session), ou créer un endpoint dédié fil courant.[^2]
- **TESTS**
    - ajouter un fichier `test_session_memory_contract.py` couvrant structure, absence de verbatim, évolution sur nouveaux tours et comportement de l’endpoint.[^2]
