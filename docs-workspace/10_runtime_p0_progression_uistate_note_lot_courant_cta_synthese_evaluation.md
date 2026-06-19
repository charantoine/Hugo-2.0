# NOTE — Actions terminales synthèse / évaluation (lot 1)

### 0. Objet de la note

Cette note décrit ce qui est standardisé dans le lot courant pour les **CTA de synthèse et d’évaluation** côté apprenant : états backend, projection dans l’UIState, comportements attendus des boutons, et limites explicites (pas de certification automatique).[^1]
Elle fixe un contrat de convergence front / backend suffisamment précis pour coder, sans prétendre que toute la chaîne d’évaluation 2.0 est déjà livrée.[^2][^1]

> Convention de lot  
> Cette note couvre la **Vague 1** du plan de convergence (`plan_documentation_cto_convergence_hugo.md`). Les Vagues 2 et 3 (profils d’affichage, confidentialité, parcours encadrants, décisions structurantes v17) et la couronne optionnelle sont synthétisées dans `synthese_globale_ecarts_par_domaine.md` et détaillées dans `cluster2_matrice_runtime_vs_cible.md` (V3).
***

### 1. Corpus mobilisé

- Code (réel) :
    - Endpoints d’évaluation : `request-evaluation`, `finalize-evaluation`, `evaluation-readiness`, `generate-trace` (fichiers API et services correspondants)
    - Construction de l’`ui_state` et projection des CTA (builder UIState côté backend, composants front apprenant).[^1]
- Docs :
    - `plan_documentation_cto_convergence_hugo.md` — section “Standardisation des actions terminales” (lot courant).[^1]
    - Rapport d’écarts domaine 70 `ecarts — 70_evaluation_traces_preuves.md` pour la chaîne d’évaluation et les limites (validation humaine, EvaluationTrace partielle).[^3][^1]
- Prompts / contrats lot :
    - Contrat UIState minimal défini pour `cta_evaluation` et `cta_synthesis` (statuts, blocking_reasons, endpoints, UI, last_evaluation).

***

### 2. Réel confirmé (niveau lot)

Les rapports d’écarts et le plan de doc convergent sur les points suivants :[^3][^1]

- Il existe déjà une **branche terminale d’évaluation utilisable** :
    - endpoints d’entrée (`request-evaluation`, `evaluation-readiness`)
    - génération de traces (`generate-trace`)
    - finalisation (`finalize-evaluation`).[^3][^1]
- Le système peut produire une **trace minimale d’évaluation** (objets de type `LearnerEvaluationRecord`, `Trace`, `Evidence`), mais le **mapping doctrinal complet EvaluationTrace 2.0 ↔ modèle réel** reste partiel.[^3][^1]
- La **validation finale est humaine** : aucune spécification ne décrit une certification autonome par Hugo, et les documents rappellent explicitement que c’est interdit de la présenter comme telle.[^1][^3]
- Le front apprenant dispose déjà de CTA permettant de déclencher synthèse / évaluation, mais leurs états et raisons de blocage ne sont pas encore standardisés dans un contrat UIState canonisé.[^1]

Voilà la note assemblée, prête à coller dans `10_runtime_p0_progression_uistate_note_lot_courant_cta_synthese_evaluation.md` (sans les `[^n]`, adaptés ici en citations).

***

## NOTE — Actions terminales synthèse / évaluation (lot courant)

### 0. Objet de la note

Cette note décrit ce qui est standardisé dans le lot courant pour les **CTA de synthèse et d’évaluation** côté apprenant : états backend, projection dans l’UIState, comportements attendus des boutons, et limites explicites (pas de certification automatique).[^1][^2]
Elle fixe un contrat de convergence front / backend suffisamment précis pour coder, sans prétendre que toute la chaîne d’évaluation 2.0 est déjà livrée.[^1]

***

### 1. Corpus mobilisé

- Code (réel) :
    - endpoints d’évaluation : `request-evaluation`, `finalize-evaluation`, `evaluation-readiness`, `generate-trace` (fichiers API et services correspondants)
    - construction de l’`ui_state` et projection des CTA (builder UIState côté backend, composants front apprenant).[^1]
- Docs :
    - `plan_documentation_cto_convergence_hugo.md` — section “Standardisation des actions terminales” (lot courant)[^1]
    - rapport d’écarts domaine 70 `ecarts — 70_evaluation_traces_preuves.md` pour la chaîne d’évaluation et les limites (validation humaine, EvaluationTrace partielle).[^2]
- Prompts / contrats lot :
    - contrat UIState minimal défini pour `cta_evaluation` et `cta_synthesis` (statuts, blocking_reasons, endpoints, UI, last_evaluation).[^1]

***

### 2. Réel confirmé (niveau lot)

Les rapports d’écarts et le plan de doc convergent sur les points suivants.[^2][^1]

- Il existe déjà une **branche terminale d’évaluation utilisable** :
    - endpoints d’entrée (`request-evaluation`, `evaluation-readiness`)
    - génération de traces (`generate-trace`)
    - finalisation (`finalize-evaluation`).[^2][^1]
- Le système peut produire une **trace minimale d’évaluation** (objets de type `LearnerEvaluationRecord`, `Trace`, `Evidence`), mais le **mapping doctrinal complet EvaluationTrace 2.0 ↔ modèle réel** reste partiel.[^2]
- La **validation finale est humaine** : aucune spécification ne décrit une certification autonome par Hugo, et les documents rappellent explicitement que c’est interdit de la présenter comme telle.[^2][^1]
- Le front apprenant dispose déjà de CTA permettant de déclencher synthèse / évaluation, mais leurs états et raisons de blocage ne sont pas encore standardisés dans un contrat UIState canonisé.[^1]

***

### 3. Cible lot courant — contrat UIState CTA

Pour ce lot, on fixe un contrat minimal côté UIState, produit par le backend et consommé tel quel par le front.[^1]

#### 3.1 Contrat cible minimal (UIState)

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

- les champs `*_ready_status` sont des **énums fermés**, pas des chaînes libres ;[^1]
- `blocking_reasons` est une **liste courte de messages lisibles**, sans structures P0 ni verbatim techniques ;[^1]
- les endpoints listés sont les seuls attendus pour les CTA de ce lot ; pas de nouvelle API inventée côté front.[^1]

***

### 4. Écarts et décisions (lot courant)

#### 4.1 Niveau de richesse de la trace

- Doctrine 2.0 : `EvaluationTrace` comme objet riche liant `LearnerEvaluationRecord`, `Trace`, `Evidence`, avec statuts et validation humaine explicites.[^2]
- Réel lot courant :
    - objets séparés existent, mais le **contrat unique EvaluationTrace** n’est pas stabilisé ;
    - le lot vise à **sécuriser la branche existante** (endpoints, surface de déclenchement, UIState) sans refondre toute la chaîne d’évaluation.[^2][^1]
- Décision : parler d’**évaluation utilisable** avec trace minimale et validation humaine, sans sur‑vendre l’alignement doctrinal complet.[^2][^1]


#### 4.2 États et blocages non standardisés

- Avant ce contrat, les conditions d’éligibilité à l’évaluation / synthèse étaient dispersées et peu lisibles côté front (logique partielle, textes ad hoc).[^1]
- Décision :
    - standardiser quelques états d’éligibilité simples (`eligible`, `blocked_*`) ;
    - rendre explicites les **raisons de blocage** en texte court ;
    - interdire l’exposition de dumps techniques ou de P0 dans ces raisons.[^1]


#### 4.3 Position du front

- La vérité comportementale reste côté backend ; UIState est une traduction produit, pas une logique moteur.[^3][^1]
- Décision : le front apprenant **lit** `ui_state.cta_evaluation` / `cta_synthesis` et n’en déduit pas d’autres états — il n’invente ni règles d’éligibilité ni raisonnements supplémentaires.[^1]

***

### 5. Contrat à respecter (backend et front)

#### 5.1 Backend

Le backend doit, pour la vue apprenant, produire **systématiquement** :[^1]

- un objet `cta_evaluation` conforme au contrat ci‑dessus ;
- un objet `cta_synthesis` conforme au contrat ;
- un `last_evaluation` cohérent dès qu’une évaluation a été déclenchée dans la session.

Et garantir que :

- les valeurs de `evaluation_ready_status` et `synthesis_ready_status` restent dans les listes prévues ;
- `blocking_reasons` contient uniquement des formulations lisibles, sans IDs internes, noms de flags ou dumps de structures P0 ;
- les endpoints renseignés pointent vers les routes effectivement supportées dans le backend local.[^1]

Interdits :

- ajouter dans ces objets des champs P0 ou des extraits de `turn_state` ;[^1]
- encoder une **certification autonome** : l’évaluation reste un avis / une trace appelant validation humaine.[^2][^1]


#### 5.2 Front apprenant

Le front doit :[^1]

- lire uniquement `ui_state.cta_evaluation` / `cta_synthesis` pour :
    - afficher ou non les boutons,
    - choisir le label, l’état disabled et le helper text,
    - afficher les raisons de blocage ;
- ne pas :
    - ré‑implémenter des règles d’éligibilité côté front (nombre de tours, complétude, etc.) ;
    - extrapoler des statuts de certification à partir des CTA ;
    - piocher directement dans des réponses P0 pour décider d’activation de boutons.[^3][^1]

***

### 6. Tests et garde‑fous

Actions attendues côté tests :[^1]

- backend :
    - tests sur les énums de `*_ready_status` ;
    - tests garantissant l’absence de champs P0 / dumps techniques dans `blocking_reasons` ;
    - tests de cas principaux : `eligible`, `blocked_missing_data`, `blocked_min_turns_not_reached`, `blocked_context_incomplete`, blocage synthèse par manque de contenu ;
- front :
    - tests unitaires / e2e garantissant que l’affichage des CTA et helper texts se cale exclusivement sur `ui_state.cta_*` ;
    - absence de logique métier parallèle d’éligibilité côté front.[^1]

***

### 7. Limites explicites à documenter produit

Le discours produit et métier doit respecter les bornes suivantes :[^2][^1]

- Hugo **propose une évaluation** et une trace, mais **ne certifie pas** l’apprenant de façon autonome.
- Les CTA de synthèse et d’évaluation **aident à structurer la fin de fil** (synthèse, relecture, feedback), sans remplacer un examen ou une validation humaine.
- Les traces produites peuvent être utilisées comme **support** par un formateur ou un organisme, mais ne doivent pas être décrites comme une preuve automatique de niveau.


<div align="center">⁂</div>

[^1]: plan_documentation_cto_convergence_hugo.md

[^2]: ecarts — 70_evaluation_traces_preuves.md

[^3]: DOC_METHODO_REFERENCE_CONVERGENCE_HUGO_REVISE.md

