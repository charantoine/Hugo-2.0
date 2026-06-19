

## Fiche domaine 20 — Mémoire gouvernée intra-conversation (lot 1)

### Objet

Clarifier ce qui est livré en **mémoire de fil courant** dans Hugo local, ce qui reste préparation inter‑sessions, et les règles à ne pas casser dans les devs suivants.[^1][^2]

### Réel confirmé

- Contrat `SessionMemoryContract` stabilisé, sans verbatim :
`session_id`, `updated_at`, `theme`, `learning_objective`, `facts_confirmed`, `open_points`, `pending_actions`, `memory_scope="intra_conversation"`.[^3][^1]
- Endpoint `GET /hugo/sessions/{id}/memory-summary/` renvoyant :
    - `session_memory` = mémoire gouvernée du fil courant,
    - `theme_memories` = projection inter‑sessions (`LearnerThemeMemory`), marquée comme préparée/non injectée.[^2][^1][^3]
- Mémoire de fil projetée dans la réponse API (turn, traces, UIState éventuelle) mais non utilisée comme “profil durable” ni comme mémoire principale du moteur.[^1][^2]


### Cible minimale lot 1

- Mémoire gouvernée **intra-conversation uniquement**, produite backend, sans verbatim brut, disponible via `session_memory` et `memory-summary`.[^3][^1]
- Inter‑sessions : objets et consolidation présents, mais usage runtime explicitement **hors périmètre** du lot 1.[^2]


### Écarts / points à surveiller

- Ne pas documenter `theme_memories` comme capacité inter‑sessions livrée tant qu’on ne l’injecte pas réellement dans l’orchestrateur.[^1][^2]
- Ne pas réintroduire de verbatim ou de P0 dans les structures mémoire exposées au front.[^2][^3]


### Décisions à respecter

- Traiter `SessionMemoryContract` + réponse `memory-summary` comme **contrats de référence** pour tous les devs mémoire côté GitHub.[^4][^3]
- Toute extension mémoire (profil apprenant, inter‑sessions active, diagnostics) doit être documentée comme **lot suivant** et ne pas modifier silencieusement le contrat lot 1.[^2]

***

## Fiche domaine 70 — CTA synthèse / évaluation \& branche d’évaluation (lot 1)

### Objet

Fixer le socle lot 1 de la branche **synthèse / évaluation** : contrats UIState, gardes backend, doctrine produit (pas de certification autonome).[^5][^6][^2]

### Réel confirmé

- `UIState` expose `cta_synthesis` / `cta_evaluation` avec :
    - enums fermés `*_ready_status`,
    - `blocking_reasons` lisibles (mapping depuis `ConversationProgress`, sans P0),
    - `endpoints` réels (`/hugo/sessions/{id}/request-synthesis/`, `/request-evaluation/`, etc.),
    - bloc `ui.*` (show, label, disabled, helper),
    - `last_evaluation` simple (`status`, `completed_at`).[^4][^3]
- Endpoints synthèse / évaluation branchés de bout en bout : readiness, request, finalize, generate-trace.[^5][^4]
- Garde API ajoutée sur `request-evaluation` : cas non éligibles → `400 evaluation_not_eligible` avec `blocking_reasons` cohérent avec l’UI. Early trigger possible seulement sous policy explicite.[^4][^5]
- Front 1.8 consomme `ui_state.cta_*` comme **source unique** pour les boutons synthèse / éval.[^5][^4]


### Cible minimale lot 1

- Actions terminales **facultatives** pilotées par backend, avec états d’éligibilité clairs et raisons de blocage lisibles.[^6][^3]
- Évaluation : **proposition prudente**, validation finale **humaine**, aucun discours de certification automatique.[^6][^2]


### Écarts / points à surveiller

- EvaluationTrace doctrinale encore répartie entre `LearnerEvaluationRecord`, `Trace`, `TraceCriterionAssessment`, `Evidence` : pas d’objet unifié dans ce lot.[^5][^2]
- Front : tests JS CTA à intégrer et rejouer dans la CI GitHub.[^4]


### Décisions à respecter

- Toujours piloter les CTA synthèse / évaluation via `ui_state.cta_*` (et pas via P0 ou calcul local).[^3][^4]
- Ne jamais documenter l’évaluation comme certifiante ; garder la ligne “Hugo propose, humain valide”.[^6][^2]
- Toute évolution future d’EvaluationTrace doit être clairement marquée comme **lot 2** (nouveau contrat), sans réécrire l’histoire du lot 1.[^2]

***

## Fiche domaine 30 — RAG documentaire \& hiérarchie de contexte (lot 1)

### Objet

Cadrer le niveau réel du **RAG documentaire** dans Hugo local pour éviter toute sur‑promesse technique ou confusion avec la mémoire gouvernée.[^7][^2]

### Réel confirmé

- RAG décrit et utilisé comme **mécanisme lexical backend, gouverné, question-driven** : requêtes textuelles sur un référentiel documentaire, filtrées par des règles métiers.[^7][^2]
- Le RAG fonctionne comme **renfort documentaire situé** : fournit des documents/extraits pertinents, en complément de la progression et de la mémoire, sans les remplacer.[^7][^2]
- Aucune doc de lot 1 ne présente le RAG comme mémoire apprenant ou comme moteur autonome de cours.[^2]


### Cible minimale lot 1

> RAG documentaire lexical, gouverné, question-driven, utilisé comme renfort de contexte ; l’état et la mémoire gouvernée priment, le RAG vient en support. Toute architecture plus sophistiquée (vectoriel, hiérarchie complexe) est hors périmètre du lot 1 et devra rester additive et prouvée par le code avant d’être documentée.[^7][^2]

### Écarts / points à surveiller

- Audit de code RAG (services, filtres, types de documents, exposition UI) à faire/compléter pour verrouiller les détails ; la doctrine est posée mais pas exhaustivement illustrée dans cette fiche.[^7][^2]
- Risque classique : que le produit ou la doc marketing requalifient le RAG en “mémoire” ou en “IA qui connaît le référentiel” sans alignement code.[^2]


### Décisions à respecter

- Dans toute doc et tout ticket, parler explicitement de **RAG lexical gouverné** ; ne jamais le présenter comme mémoire principale ou moteur de cours.[^7][^2]
- Les futures évolutions RAG (vectorisation, context windows avancées, hiérarchie de contextes) devront être décrites comme **chantiers additionnels** avec leurs propres contrats, pas comme une relecture rétroactive du lot 1.[^2]

***

Tu peux mettre ces trois fiches dans `docs-workspace` (par exemple `NOTE_LOT1_20_memoire.md`, `NOTE_LOT1_70_cta_eval.md`, `NOTE_LOT1_30_rag.md`) et les lier depuis la note de convergence CTO.

<div align="center">⁂</div>

[^1]: 20_cursorops_templates.md

[^2]: plan_documentation_cto_convergence_hugo.md

[^3]: specs-interface-2.0.md

[^4]: backlog_lot_1.md

[^5]: 70_cursorops_templates.md

[^6]: 10_runtime_p0_progression_uistate_note_lot_courant_cta_synthese_evaluation.md

[^7]: 30_cursorops_templates.md

