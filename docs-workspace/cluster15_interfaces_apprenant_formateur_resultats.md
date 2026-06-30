# Cluster 15 — Interfaces apprenant + formateur (résultats)

## Sources mobilisées

- `cluster2_matrice_runtime_vs_cible.md` (domaines 10, 20, 110)
- `cluster2_prompts_audit_runtime_et_memoire.md` (sections B, C, C.1, D)
- `ecarts — 110_interfaces_formateur_tuteur.md` (IFT-026, IFT-036, IFT-037, IFT-041, IFT-042)
- `specs interface 2.0.md` (profils d’affichage, bandeaux de mode, orchestrateur formateur)
- Code réel : `hugo_back`, `hugo-hugolucia/frontend_1.8`

---

## Réel confirmé (avant cluster 15)

| Zone | Déjà livré | Manque identifié |
|------|------------|------------------|
| Apprenant UIState | `conversation_mode`, `learner_display_profile`, CTA synthèse/évaluation | Pas d’appel `set-posture` ; pas de panneau `memory-summary` |
| Backend posture | `POST /hugo/sessions/{id}/set-posture/`, `can_transition` | Consommé uniquement par tests |
| Mémoire | `GET .../memory-summary/` (intra + theme_memories) | Front prod ne consommait pas |
| Formateur | Liste + validate | Rejet, provisoire, atelier élicitation, usage |

## Cible 2.0 (périmètre cluster 15)

- Apprenant : sélecteur posture gouverné, profils d’affichage, mémoire intra-conversation résumée.
- Formateur : workflow validation complet, atelier élicitation V0, indicateurs d’usage minimaux.

## Écarts comblés par ce cluster

- **A1** : sélecteur posture branché sur `set-posture` + reload UIState.
- **A2** : profils déjà câblés (`learner_display_profile` → classes CSS) — polish CSS conservé.
- **A3** : panneau mémoire consommant **uniquement** `session_memory` (pas `theme_memories`).
- **B1** : tableau trainer + validate / provisoire / rejet (motif) / édition.
- **B2** : route `/app/trainer/elicitation` + endpoints élicitation/ingest existants.
- **B3** : `usage_stats` minimal côté API (exploitable / note) — compteur RAG réel **AVERIFIER**.

---

## 1. Décisions par fonctionnalité (A1–A3, B1–B3)

### A1 — Sélecteur de posture apprenant

**Décision** : remplacer le bandeau lecture seule par `PostureSelector.vue` qui :
- affiche posture courante + micro-copie doctrinale (constante front alignée sur `PROFILE_LABELS` backend) ;
- n’affiche le `<select>` que si `conversation_mode.can_switch === true` ;
- appelle `POST /hugo/sessions/{id}/set-posture/` puis recharge UIState (pas de recalcul local) ;
- mappe `transition_not_allowed` et `Invalid posture` en messages utilisateur.

**Garde-fou** : le front ne calcule jamais l’éligibilité ; il consomme `can_switch` du backend.

### A2 — Profils d’affichage (`learnerDisplayProfile`)

**Décision** : aucun changement de contrat backend requis — `learner_display_profile` est déjà dans UIState (`ui_state_builder._resolve_learner_display_profile`). Le front applique `prod-workspace--{profile}` et `prod-panel--{profile}` (youth / adult / professional), distinct de `gamification_profile` (cosmétique).

### A3 — Panneau mémoire gouvernée

**Décision** : `LearnerMemoryPanel.vue` appelle `GET .../memory-summary/` et n’affiche que `session_memory` (champs du `SessionMemoryContract`). Les `theme_memories` inter-sessions restent hors UI apprenant (doctrine lot mémoire intra-conversation).

**Garde-fou** : pas de verbatim, pas de TurnState, pas de P0.

### B1 — Workflow validation TrainerKnowledgeItem

**Décision** : enrichir la liste API (`usage_stats`, `validated_by`, dates ISO) et la vue tableau avec actions :
- `validate`, `mark_provisional` (nouveau), `reject` (+ motif optionnel journalisé en `provenance_note` avant suppression), `edit` (valide avec contenu corrigé).

### B2 — Atelier d’élicitation V0

**Décision** : nouvelle vue `ProdTrainerElicitationView.vue` — saisie `referential_item_id`, questions GET élicitation, POST réponses → items `declared`, option ingest document par `file_path` serveur. Pas de pilotage conversation apprenant, pas de verbatim apprenant.

### B3 — Vue usage minimale

**Décision** : champ `usage_stats` en lecture seule sur chaque item :
- `exploitable` : `status === validated_trainer` ;
- `usage_count` : `null` (pas de modèle de citation RAG lié aux items aujourd’hui — **AVERIFIER** pour compteur réel) ;
- `usage_note` : message produit explicite.

---

## 2. Matrices champ / source / consommateur / garde-fou

### A1 — Posture

| Champ / composant | Source backend | Consommateur front | Garde-fou |
|-------------------|----------------|--------------------|-----------|
| `conversation_mode.code/label` | `ui_state_builder._build_conversation_mode` | `PostureSelector` | Lecture seule si `can_switch` false |
| `conversation_mode.can_switch` | idem + `can_transition` | `PostureSelector` | Pas de liste locale d’éligibilité |
| `conversation_mode.switch_warning` | idem | `PostureSelector` | Avertissement orange/vert |
| POST `{ posture }` | `SessionSetPostureView` | `PostureSelector` | Erreurs API affichées |

### A2 — Profil d’affichage

| Champ | Source backend | Consommateur front | Garde-fou |
|-------|----------------|--------------------|-----------|
| `learner_display_profile` | UIState / groupe / org | `ProdLearnerWorkspace`, `HugoProgressPanel`, `LearnerMemoryPanel` | Aucune logique métier branchée |
| `gamification_profile` | UIState param | `engagementUiModel` | Cosmétique uniquement |

### A3 — Mémoire

| Champ | Source backend | Consommateur front | Garde-fou |
|-------|----------------|--------------------|-----------|
| `session_memory.*` | `SessionMemorySummaryView` → `build_session_memory` | `LearnerMemoryPanel` | Intra-conversation uniquement |
| `theme_memories` | même endpoint | **Non affiché** | Inter-session hors périmètre UI |

### B1 — Validation trainer

| Action | Endpoint | Vue | Garde-fou |
|--------|----------|-----|-----------|
| Liste | `GET /hugo/trainer/knowledge-items/` | `ProdTrainerKnowledgeView` | Rôle trainer |
| Valider | `POST .../validate/` `{action: validate}` | idem | Humain obligatoire |
| Provisoire | `{action: mark_provisional}` | idem | Ne remplace pas validation finale |
| Rejeter | `{action: reject, reason?}` | idem | Suppression — motif best-effort |
| Éditer | `{action: edit, content}` | idem | Valide après correction |

### B2 — Élicitation

| Étape | Endpoint | Vue | Garde-fou |
|-------|----------|-----|-----------|
| Questions | `GET .../elicitation-questions/` | `ProdTrainerElicitationView` | Pas de données apprenant |
| Réponses | `POST .../elicitation-answers/` | idem | Items `declared` |
| Ingest | `POST /hugo/trainer/documents/ingest/` | idem | Chemin serveur, pas d’upload direct V0 |

### B3 — Usage

| Champ | Source | Vue | Garde-fou |
|-------|--------|-----|-----------|
| `usage_stats.exploitable` | `_usage_stats_for_item` | Colonne Usage | Pas d’analytics complet |
| `usage_stats.usage_count` | `null` (placeholder) | — | **AVERIFIER** liaison RAG future |

---

## 3. Fichiers modifiés / créés

### Backend (`hugo_back`)

| Fichier | Action | Description |
|---------|--------|-------------|
| `apps/hugo/views_trainer.py` | Modifié | `mark_provisional`, reject+motif, `_serialize_trainer_item`, `usage_stats` |
| `apps/hugo/tests/test_trainer_knowledge.py` | Modifié | Tests liste usage, provisoire, rejet |

*Inchangés mais consommés* : `views_sessions.py` (`SessionSetPostureView`, `SessionMemorySummaryView`), `services/ui_state_builder.py`, `domain/posture_transitions.py`.

### Front apprenant (`frontend_1.8`)

| Fichier | Action | Description |
|---------|--------|-------------|
| `src/constants/conversationPostures.js` | **Créé** | Labels + micro-copies postures |
| `src/components/learner/PostureSelector.vue` | **Créé** | Bandeau + sélecteur posture |
| `src/components/learner/LearnerMemoryPanel.vue` | **Créé** | Panneau mémoire intra-conversation |
| `src/components/learner/ProdLearnerWorkspace.vue` | Modifié | Intégration A1 + A3 |
| `src/style.css` | Modifié | Styles posture + mémoire |

*Conservé* : `ConversationModeBanner.vue` (legacy lecture seule, remplacé en prod).

### Front formateur

| Fichier | Action | Description |
|---------|--------|-------------|
| `src/views/ProdTrainerKnowledgeView.vue` | Modifié | Tableau B1 + B3 |
| `src/views/ProdTrainerElicitationView.vue` | **Créé** | Atelier B2 |
| `src/router/index.js` | Modifié | Route `/app/trainer/elicitation` |

---

## 4. Extraits de code représentatifs

### A1 — Backend (contrat UIState posture)

```python
# apps/hugo/services/ui_state_builder.py
def _build_conversation_mode(progress):
    posture = progress.posture
    can_switch = any(
        target != posture and can_transition(posture, target, progress.overall_maturity)[0]
        for target in ConversationPosture
    )
    return {
        "code": posture.value,
        "label": PROFILE_LABELS.get(posture.value, posture.value),
        "can_switch": can_switch,
        "switch_warning": switch_warning,
    }
```

```python
# apps/hugo/views_sessions.py — SessionSetPostureView
allowed, warning = can_transition(current_posture, next_posture, progress.overall_maturity)
if not allowed:
    return Response({"detail": "transition_not_allowed"}, status=400)
session.posture = next_posture.value
return Response({"posture": session.posture, "warning": warning})
```

### A1 — Front (PostureSelector)

```javascript
const { data } = await api.post(`/hugo/sessions/${sessionId}/set-posture/`, {
  posture: nextPosture,
})
emit('posture-changed', data)
// ProdLearnerWorkspace → loadSessionUiState()
```

### A2 — Front (profil déjà branché)

```vue
<div class="prod-workspace" :class="`prod-workspace--${engagementModel.learnerDisplayProfile}`">
```

### A3 — Backend + Front mémoire

```python
# SessionMemorySummaryView — session_memory via SessionMemoryContract.to_dict()
return Response({"session_memory": session_memory, "theme_memories": [...]})
```

```javascript
// LearnerMemoryPanel — consomme session_memory uniquement
const { data } = await api.get(`/hugo/sessions/${sessionId}/memory-summary/`)
sessionMemory.value = data?.session_memory || null
```

### B1 — Backend validation étendue

```python
if action == "mark_provisional":
    item.status = KnowledgeItemStatus.DERIVED_PROVISIONAL.value
    item.save(update_fields=["status", "updated_at"])
    return Response({"status": "derived_provisional"})
```

### B2 — Front atelier

```javascript
await api.get(`/hugo/trainer/referential-items/${itemId}/elicitation-questions/`)
await api.post(`/hugo/trainer/referential-items/${itemId}/elicitation-answers/`, { answers })
```

### B3 — Usage stats

```python
def _usage_stats_for_item(item):
    validated = item.status == KnowledgeItemStatus.VALIDATED_TRAINER.value
    return {
        "exploitable": validated,
        "usage_count": None,
        "usage_note": "Exploitable par le moteur après validation formateur." if validated else "...",
    }
```

---

## 5. Plan de livraison par étapes

### Étape 1 — Apprenant posture + profil (A1, A2)

| PR | Contenu | Critères de complétion |
|----|---------|------------------------|
| PR-C15-L1 | `PostureSelector`, intégration workspace, constantes postures | `test_posture_modes.py` PASS ; sélecteur visible si `can_switch` ; reload UIState après switch |
| PR-C15-L1b | Polish CSS profils (si besoin) | Classes `prod-workspace--*` actives sur 3 profils demo |

### Étape 2 — Apprenant mémoire (A3)

| PR | Contenu | Critères |
|----|---------|----------|
| PR-C15-L2 | `LearnerMemoryPanel` | `test_memory_summary_smoke.py` PASS ; panneau sans verbatim ; pas de `theme_memories` affiché |

### Étape 3 — Formateur validation (B1, B3 partiel)

| PR | Contenu | Critères |
|----|---------|----------|
| PR-C15-T1 | Tableau + actions validate/provisional/reject/edit + `usage_stats` | `test_trainer_knowledge.py` PASS (3 tests) |

### Étape 4 — Formateur élicitation (B2)

| PR | Contenu | Critères |
|----|---------|----------|
| PR-C15-T2 | `ProdTrainerElicitationView` + route | Flow questions → items `declared` ; redirect liste ; smoke trainer role |

---

## 6. Plan de tests minimal (cluster 15 livré)

### Backend (pytest)

| Test | Fichier | Couvre |
|------|---------|--------|
| `test_set_posture_endpoint_updates_session` | `test_posture_modes.py` | A1 |
| `test_memory_summary_smoke_learner_no_verbatim` | `test_memory_summary_smoke.py` | A3 confidentialité |
| `test_trainer_elicitation_and_validation_flow` | `test_trainer_knowledge.py` | B1/B2 |
| `test_trainer_knowledge_list_includes_usage_stats` | idem | B3 |
| `test_trainer_mark_provisional_and_reject` | idem | B1 |

**État local** : 21 tests cluster 15 + 39 tests campagne C15 étendue + **90 tests consolidés post-doc (2026-06-18)** — **PASS**. Voir `rapport_mise_a_jour_doc_post_tests_2026-06-18.md`.

### Front (à ajouter / manuel)

| ID | Type | Scénario |
|----|------|----------|
| C15-E2E-A1 | Playwright | Session apprenant : si `can_switch`, changement posture → label UIState mis à jour |
| C15-E2E-A3 | Playwright | Panneau mémoire visible, pas de texte message brut |
| C15-E2E-B1 | Playwright | Formateur : valider item → statut `validated_trainer` |
| C15-E2E-B2 | Playwright | Atelier élicitation → item créé en liste |

### Risques de régression

- Surcharge UI apprenant (sidebar + progression) — mitigé par panneau repliable futur.
- Confusion formateur/tuteur — routes `/app/trainer/*` gardées par `requiresTrainerLike`.
- `theme_memories` toujours dans payload API — front les ignore ; ne pas les réintroduire en UI.
- Compteur usage RAG absent — ne pas sur-vendre B3 tant que liaison citation↔item **AVERIFIER**.

---

## AVERIFIER

- Compteur réel d’exploitation RAG par `TrainerKnowledgeItem` (modèle citation absent).
- Upload document formateur côté front (V0 = `file_path` serveur uniquement).
- Playwright C15 sur environnement demo Encoors.

## Prochaine sortie utile

1. MR Playwright C15 (A1, A3, B1, B2).
2. Extension backend `usage_count` si modèle de traçage RAG↔item confirmé.
3. Mise à jour `ecarts — 110` : IFT-026/041/042 → PARTIEL/LIVRÉ selon revue produit.
