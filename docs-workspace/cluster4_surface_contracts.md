# Cluster 4 — Contrats de surface UIState

**Date :** 2026-06-16  
**Périmètre :** `conversation_mode` + `learner_display_profile` dans le contrat `GET /hugo/sessions/{id}/ui-state/`

## Contrats cibles minimaux (livré local)

### `conversation_mode`

Dérivé de `ConversationProgress.posture` (3 postures canoniques). Pas d’exposition P0.

```json
{
  "code": "reflective_afest",
  "label": "Réflexif AFEST",
  "can_switch": true,
  "switch_warning": null
}
```

| Champ | Type | Source réelle |
|-------|------|---------------|
| `code` | enum posture | `progress.posture` |
| `label` | string | `PROFILE_LABELS` (`ui_state_builder.py`) |
| `can_switch` | bool | `can_transition` vers au moins une autre posture |
| `switch_warning` | string \| null | Avertissement si `knowledge_review` + maturité RED |

### `learner_display_profile`

Enum 3 valeurs (spec interface 2.0 / personae A1–A3). **≠** `gamification_profile` A/B/C.

| Valeur | Persona cible | Rendu UX |
|--------|---------------|----------|
| `youth` | A1 jeune 16–20 | `[CIBLE]` front — champ backend prêt |
| `adult` | A2 reconversion | idem |
| `professional` | A3 ingénieur / défaut | ≈ UX actuelle |

**Lecture :** query param `?learner_display_profile=youth|adult|professional` (défaut `professional`). Même contrat UIState pour tous les profils.

## Tests

```bash
cd hugo_back
.venv/bin/python -m pytest apps/hugo/tests/test_cluster4_surface_contracts.py -q
```

**Statut (2026-06-16) :** 9/9 OK

Batterie élargie :

```bash
.venv/bin/python -m pytest \
  apps/hugo/tests/test_cluster4_surface_contracts.py \
  apps/hugo/tests/test_cluster3_oracles.py \
  apps/hugo/tests/test_cta_evaluation_contract.py \
  apps/hugo/tests/test_cta_synthesis_contract.py \
  apps/hugo/tests/test_p0_non_regression.py \
  apps/hugo/tests/test_conversation_progress.py::test_progress_and_ui_state_endpoints_return_contract \
  -q
```

**Statut :** 22/22 OK

## Fichiers code

| Fichier | Rôle |
|---------|------|
| `domain/conversation_profile.py` | `LearnerDisplayProfile`, champs `UIState` |
| `services/ui_state_builder.py` | `_build_conversation_mode`, `normalize_learner_display_profile` |
| `views_sessions.py` | Query/body param `learner_display_profile` sur ui-state / synthèse / éval |
| `tests/test_cluster4_surface_contracts.py` | Oracles cluster 4 |

## Reste CIBLE (hors cluster 4)

- Sélecteur posture **front** prod (`A1-08`, `G2-02`)
- Choix profil par formateur / ORGADMIN (DSP-05, DSP-06) — pas d’endpoint persisté
- Rendu UX différencié 3 grammaires côté `hugo-hugolucia`
- Skins cosmétiques au-dessus du profil d’affichage

## Recommandation CTO

**Livrable démontrable :** le backend expose un **contrat UIState unique** enrichi, testé, sans fuite P0 — prêt pour le front et les oracles INV-07 / DSP-04.

**Prochain move rentable :** consommation front de `conversation_mode` + `learner_display_profile` (parcours A1), puis endpoints de **persistance** du profil d’affichage au niveau groupe/org (DSP-05/06) — sans rouvrir D9bis ni EvaluationTrace.
