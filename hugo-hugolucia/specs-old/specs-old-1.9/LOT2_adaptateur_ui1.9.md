# LOT 2 — Adaptateur UI 1.8

**Durée estimée :** 2–3 jours  
**Risque :** faible — front uniquement, aucun fichier backend P0 touché  
**Dépendance :** LOT 1 checklist verte — endpoint `/ui-state` opérationnel

---

## Objectif

Remplacer les indicateurs debug par des éléments produit dérivés de `UIState`.
Le moteur pédagogique reste dans le backend. Le front ne calcule rien.

---

## Règle de sécurité du lot

- Le front ne lit **jamais** directement un champ P0 brut.
- Le seul contrat front/back est la réponse de `/ui-state`.
- Les boutons Synthèse et Évaluation appellent des endpoints dédiés — éligibilité calculée côté backend uniquement.
- Les profils de gamification A/B/C sont **strictement cosmétiques**.
- Le paramètre `gamification_profile` reçu par l'endpoint `/ui-state` est validé côté backend.
  Toute valeur hors `A`, `B`, `C` retombe sur `B`.

---

## `frontend/src/hugo/progressionLabels.js`

```javascript
export const SCENE_LABELS = {
  "Raconter":    "Je raconte ma situation",
  "Explorer":    "J'explore avec Hugo",
  "Synthétiser": "Je fais le point",
};

export const MATURITY_LABELS = {
  red:    "En cours d'exploration",
  orange: "Bonne avancée",
  green:  "Prêt à faire le bilan",
};

export const SYNTHESIS_BUTTON_LABELS = {
  locked:   "Continuer la conversation",
  possible: "Faire une synthèse",
  ready:    "Synthèse disponible ✓",
};

export const EVALUATION_BUTTON_LABELS = {
  locked:   null,
  possible: null,
  ready:    "Valider mes apprentissages",
};

/** Profils de gamification — cosmétiques uniquement, aucune règle pédagogique. */
export const GAMIFICATION_PROFILES = {
  A: { showProgressBar: true,  showQuestLabel: true,  showMaturityBadge: true  },
  B: { showProgressBar: true,  showQuestLabel: false, showMaturityBadge: false },
  C: { showProgressBar: false, showQuestLabel: false, showMaturityBadge: false },
};
```

---

## `frontend/src/hugo/engagementUiModel.js` (remplacement complet)

```javascript
/**
 * Remplace l'ancienne version qui lisait des variables P0 internes.
 * Consomme UNIQUEMENT la réponse de /ui-state (UIState sérialisé).
 * Aucune logique pédagogique ici.
 */

import {
  SCENE_LABELS, MATURITY_LABELS,
  SYNTHESIS_BUTTON_LABELS, EVALUATION_BUTTON_LABELS, GAMIFICATION_PROFILES,
} from "./progressionLabels.js";

export function buildDisplayModel(uiState) {
  if (!uiState) return buildDefaultDisplayModel();
  const profile = GAMIFICATION_PROFILES[uiState.gamification_profile] || GAMIFICATION_PROFILES.B;
  return {
    sceneLabel:      SCENE_LABELS[uiState.scene_label] || uiState.scene_label,
    sceneProgress:   uiState.scene_progress ?? 0,
    showProgressBar: profile.showProgressBar,
    questLabel:      profile.showQuestLabel ? uiState.active_quest_label : null,
    questProgress:   uiState.quest_progress ?? 0,
    maturityLabel:   profile.showMaturityBadge ? (MATURITY_LABELS[uiState.maturity_color] || "") : null,
    maturityColor:   uiState.maturity_color,
    synthesisButton:  buildButtonModel(uiState.synthesis_button_state, SYNTHESIS_BUTTON_LABELS),
    evaluationButton: buildButtonModel(uiState.evaluation_button_state, EVALUATION_BUTTON_LABELS),
    persistentObjects: uiState.persistent_objects || [],
  };
}

function buildButtonModel(state, labels) {
  const label = labels[state];
  return { state, label, visible: label !== null, disabled: state === "locked", highlighted: state === "ready" };
}

function buildDefaultDisplayModel() {
  return {
    sceneLabel: "Je raconte ma situation", sceneProgress: 0, showProgressBar: true,
    questLabel: null, questProgress: 0, maturityLabel: null, maturityColor: "red",
    synthesisButton:  { state: "locked", label: "Continuer la conversation", visible: true, disabled: true, highlighted: false },
    evaluationButton: { state: "locked", label: null, visible: false, disabled: true, highlighted: false },
    persistentObjects: [],
  };
}
```

---

## `frontend/src/hugo/components/HugoProgressPanel.jsx`

```jsx
import React, { useEffect, useState } from "react";
import { buildDisplayModel } from "../engagementUiModel";

export function HugoProgressPanel({ sessionId, onSynthesisRequest, onEvaluationRequest }) {
  const [model, setModel] = useState(null);
  useEffect(() => {
    if (!sessionId) return;
    fetchUiState(sessionId).then(setModel);
  }, [sessionId]);
  if (!model) return null;
  return (
    <div className="hugo-progress-panel" aria-label="Progression de la conversation">
      <div className="scene-label">{model.sceneLabel}</div>
      {model.showProgressBar && (
        <progress className={`maturity-bar maturity-bar--${model.maturityColor}`}
          value={model.sceneProgress} max={1} aria-label="Avancement de la séance" />
      )}
      {model.questLabel && <div className="quest-label">{model.questLabel}</div>}
      {model.maturityLabel && (
        <span className={`maturity-badge maturity-badge--${model.maturityColor}`}>
          {model.maturityLabel}
        </span>
      )}
      {model.synthesisButton.visible && (
        <button
          className={`hugo-btn hugo-btn--synthesis hugo-btn--${model.synthesisButton.state}`}
          disabled={model.synthesisButton.disabled}
          onClick={() => !model.synthesisButton.disabled && onSynthesisRequest?.()}
          aria-disabled={model.synthesisButton.disabled}>
          {model.synthesisButton.label}
        </button>
      )}
      {model.evaluationButton.visible && (
        <button
          className={`hugo-btn hugo-btn--evaluation hugo-btn--${model.evaluationButton.state}`}
          disabled={model.evaluationButton.disabled}
          onClick={() => !model.evaluationButton.disabled && onEvaluationRequest?.()}
          aria-disabled={model.evaluationButton.disabled}>
          {model.evaluationButton.label}
        </button>
      )}
    </div>
  );
}

async function fetchUiState(sessionId, gamificationProfile = "B") {
  const profile = ["A", "B", "C"].includes(gamificationProfile) ? gamificationProfile : "B";
  try {
    const res = await fetch(
      `/api/hugo/sessions/${sessionId}/ui-state/?gamification_profile=${encodeURIComponent(profile)}`
    );
    if (!res.ok) return null;
    return buildDisplayModel(await res.json());
  } catch {
    return null;
  }
}
```

---

## CSS minimal profils A/B/C

```css
/* HugoProgressPanel.css */
.maturity-bar--red    { accent-color: var(--color-error,   #c0392b); }
.maturity-bar--orange { accent-color: var(--color-warning, #e67e22); }
.maturity-bar--green  { accent-color: var(--color-success, #27ae60); }

.maturity-badge--red    { background: var(--color-error-highlight);   color: var(--color-error); }
.maturity-badge--orange { background: var(--color-warning-highlight); color: var(--color-warning); }
.maturity-badge--green  { background: var(--color-success-highlight); color: var(--color-success); }

.hugo-btn--locked   { opacity: 0.45; cursor: not-allowed; }
.hugo-btn--possible { opacity: 0.80; }
.hugo-btn--ready    { font-weight: 600; box-shadow: 0 0 0 2px var(--color-primary); }
```

---

## Endpoints déclenchement synthèse / évaluation (backend)

```python
# backend/apps/hugo/views/sessions.py — ajouter

@action(detail=True, methods=["post"], url_path="request-synthesis")
def request_synthesis(self, request, pk=None):
    session = self.get_object()
    raw = getattr(session, "conversation_progress", None)
    if raw:
        from backend.apps.hugo.domain.conversation_profile import ConversationProgress
        try:
            progress = ConversationProgress(**raw)
            if not progress.synthesis_eligible:
                return Response(
                    {"error": "synthesis_not_eligible", "reason_codes": progress.reason_codes},
                    status=400,
                )
        except (TypeError, KeyError):
            pass
    return Response({"status": "synthesis_queued"})


@action(detail=True, methods=["post"], url_path="request-evaluation")
def request_evaluation(self, request, pk=None):
    session = self.get_object()
    raw = getattr(session, "conversation_progress", None)
    if raw:
        from backend.apps.hugo.domain.conversation_profile import ConversationProgress
        try:
            progress = ConversationProgress(**raw)
            if not progress.evaluation_eligible:
                return Response(
                    {"error": "evaluation_not_eligible", "reason_codes": progress.reason_codes},
                    status=400,
                )
        except (TypeError, KeyError):
            pass
    return Response({"status": "evaluation_queued"})
```

---

## Checklist de sortie du LOT 2

- [ ] Les 9 tests NR LOT 0 restent verts.
- [ ] Les 8 tests LOT 1 restent verts.
- [ ] `engagementUiModel.js` ne contient aucune référence à un champ P0 brut.
- [ ] `HugoProgressPanel` ne lit aucun endpoint autre que `/ui-state`, `/request-synthesis`, `/request-evaluation`.
- [ ] Le bouton Évaluation est masqué (`visible: false`) tant que `evaluation_button_state != "ready"`.
- [ ] Les 3 profils A/B/C vérifiés visuellement en dev.
- [ ] `/request-synthesis` retourne 400 si non-éligible.
- [ ] `/request-evaluation` retourne 400 si non-éligible.
