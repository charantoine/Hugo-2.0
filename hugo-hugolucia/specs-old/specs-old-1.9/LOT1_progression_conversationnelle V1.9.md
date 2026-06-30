# LOT 1 — Moteur de progression conversationnelle

**Durée estimée :** 3–4 jours  
**Risque :** faible — additif, aucun champ P0 modifié  
**Dépendance :** LOT 0 checklist verte à 100 %

---

## Objectif

Calculer, à chaque tour utile, l'avancement global de la conversation par rapport aux objectifs
d'apprentissage visés, indépendamment du tour courant.
Stocker ce calcul dans `HugoSession.conversation_progress` (JSONB posé au LOT 0).
Brancher les stubs d'endpoints LOT 0 sur ce moteur.

---

## Règle de sécurité du lot

- `decision_engine_v17.py`, `turnstate_v17.py`, `hugo_orchestrator.py`,
  `prompt_renderer.py` : **lecture seule** (on lit leurs sorties, on n'y écrit pas).
- `ConversationProgressCalculator` s'exécute **après** `decide_conversation`,
  en aval dans la chaîne orchestrateur.
- `ConversationPosture`, `SessionMaturityLevel` importés depuis `conversation_profile.py`.

---

## `backend/apps/hugo/services/conversation_progress_calculator.py`

```python
from __future__ import annotations
from dataclasses import asdict
from typing import Optional

from backend.apps.hugo.domain.conversation_profile import (
    ConversationBranch, ConversationPosture, ConversationProgress,
    SessionMaturityLevel, UIState,
)
from backend.apps.hugo.domain.reason_codes import (
    RC_DISPERSION_RISK, RC_EVALUATION_BLOCKED_COGNITIVE_LOAD,
    RC_EVALUATION_BLOCKED_INTERACTION_RISK, RC_EVALUATION_BLOCKED_MATURITY,
    RC_EVALUATION_ELIGIBLE, RC_LOOP_RISK_HIGH, RC_NO_CAUSE_NAMED,
    RC_NO_CONCRETE_ACTIONS, RC_NO_TRANSFER_RULE, RC_NOT_ENOUGH_DESCRIPTION,
    RC_SYNTHESIS_BLOCKED_MATURITY, RC_SYNTHESIS_ELIGIBLE,
)
from backend.apps.hugo.domain.tutor_profiles import MAX_ACTIVE_BRANCHES

MAX_ACTIVE_BRANCHES_LIMIT = MAX_ACTIVE_BRANCHES  # = 3


def deserialize_conversation_progress(raw: dict | None) -> Optional[ConversationProgress]:
    """
    Reconstruit ConversationProgress depuis le JSONB stocké en base.
    Recast explicite :
    - posture -> ConversationPosture
    - overall_maturity -> SessionMaturityLevel
    - active_branches[*].exploration_level -> SessionMaturityLevel
    """
    if not raw:
        return None

    try:
        branches = [
            ConversationBranch(
                branch_id=b["branch_id"],
                theme_label=b["theme_label"],
                objective_label=b["objective_label"],
                referential_item_id=b.get("referential_item_id"),
                exploration_level=SessionMaturityLevel(b.get("exploration_level", "red")),
                is_active=b.get("is_active", True),
                reason_codes=b.get("reason_codes", []),
            )
            for b in raw.get("active_branches", [])
        ]

        return ConversationProgress(
            session_id=raw["session_id"],
            posture=ConversationPosture(raw.get("posture", "reflective_afest")),
            active_branches=branches,
            active_branches_count=raw.get(
                "active_branches_count",
                len([b for b in branches if b.is_active]),
            ),
            priority_branch_id=raw.get("priority_branch_id"),
            dispersion_risk=raw.get("dispersion_risk", False),
            overall_maturity=SessionMaturityLevel(raw.get("overall_maturity", "red")),
            synthesis_eligible=raw.get("synthesis_eligible", False),
            evaluation_eligible=raw.get("evaluation_eligible", False),
            missing_for_next_level=raw.get("missing_for_next_level", []),
            reason_codes=raw.get("reason_codes", []),
        )
    except (KeyError, TypeError, ValueError):
        return None


class ConversationProgressCalculator:
    """
    Calcule ConversationProgress à partir de :
    - TurnState courant (lecture seule — available_material est un champ réel de TurnState)
    - ConversationDecision courante (lecture seule)
    - ConversationProgress précédent (JSONB, peut être None)
    - Posture de session

    Ne modifie aucun champ P0. S'exécute après decide_conversation.
    """

    def __init__(self, posture: ConversationPosture = ConversationPosture.REFLECTIVE_AFEST):
        self.posture = posture

    def update(
        self,
        session_id: str,
        turn_state: object,
        decision: object,
        previous_progress: Optional[ConversationProgress] = None,
    ) -> ConversationProgress:
        prev = previous_progress or ConversationProgress(
            session_id=session_id, posture=self.posture,
        )
        branches = self._update_branches(turn_state, decision, prev.active_branches)
        dispersion = len([b for b in branches if b.is_active]) > MAX_ACTIVE_BRANCHES_LIMIT
        priority_id = self._elect_priority_branch(branches)
        overall = self._compute_overall_maturity(branches)
        reason_codes = self._compute_reason_codes(turn_state, decision, overall, dispersion)
        synthesis_eligible, eval_eligible = self._compute_eligibility(
            overall, turn_state, decision,
        )
        return ConversationProgress(
            session_id=session_id,
            posture=self.posture,
            active_branches=branches,
            active_branches_count=len([b for b in branches if b.is_active]),
            priority_branch_id=priority_id,
            dispersion_risk=dispersion,
            overall_maturity=overall,
            synthesis_eligible=synthesis_eligible,
            evaluation_eligible=eval_eligible,
            missing_for_next_level=self._missing_for_next(overall, turn_state),
            reason_codes=reason_codes,
        )

    def _update_branches(self, turn_state, decision, previous_branches: list) -> list:
        branches = list(previous_branches)
        theme = getattr(turn_state, "conversation_goal", "") or ""
        objective = getattr(turn_state, "current_phase", "") or ""
        if theme and objective:
            existing = next(
                (b for b in branches if b.theme_label == theme and b.objective_label == objective),
                None,
            )
            if existing is None and sum(1 for b in branches if b.is_active) < MAX_ACTIVE_BRANCHES_LIMIT:
                from uuid import uuid4
                branches.append(ConversationBranch(
                    branch_id=str(uuid4()), theme_label=theme,
                    objective_label=objective,
                    exploration_level=SessionMaturityLevel.RED, is_active=True,
                ))
                existing = branches[-1]
            if existing:
                new_level = self._branch_maturity(turn_state, decision)
                if existing.exploration_level != SessionMaturityLevel.GREEN:
                    existing.exploration_level = new_level
        return branches

    def _branch_maturity(self, turn_state, decision) -> SessionMaturityLevel:
        covered = set(getattr(turn_state, "covered_points", []) or [])
        remaining = set(getattr(turn_state, "remaining_open_points", []) or [])
        if self.posture == ConversationPosture.REFLECTIVE_AFEST:
            return self._branch_maturity_reflective(covered, remaining)
        elif self.posture == ConversationPosture.DIAGNOSTIC:
            return self._branch_maturity_diagnostic(covered, remaining)
        return self._branch_maturity_knowledge(covered, remaining)

    def _branch_maturity_reflective(self, covered, remaining) -> SessionMaturityLevel:
        """GREEN réflexif AFEST exige future_action_named + learning_rule_named (transfert explicite)."""
        has_transfer = "future_action_named" in covered and "learning_rule_named" in covered
        has_cause = "cause_hypothesis_named" in covered or "cause_confirmed" in covered
        has_description = "episode_described" in covered and "concrete_actions_described" in covered
        if has_description and has_cause and has_transfer and not remaining:
            return SessionMaturityLevel.GREEN
        if has_description and (has_cause or "problem_named" in covered):
            return SessionMaturityLevel.ORANGE
        return SessionMaturityLevel.RED

    def _branch_maturity_diagnostic(self, covered, remaining) -> SessionMaturityLevel:
        if "concrete_actions_described" in covered and "problem_named" in covered and not remaining:
            return SessionMaturityLevel.GREEN
        if "concrete_actions_described" in covered or "problem_named" in covered:
            return SessionMaturityLevel.ORANGE
        return SessionMaturityLevel.RED

    def _branch_maturity_knowledge(self, covered, remaining) -> SessionMaturityLevel:
        if not remaining and "episode_described" in covered:
            return SessionMaturityLevel.GREEN
        if "episode_described" in covered:
            return SessionMaturityLevel.ORANGE
        return SessionMaturityLevel.RED

    def _elect_priority_branch(self, branches: list) -> Optional[str]:
        active = [b for b in branches if b.is_active]
        order = {SessionMaturityLevel.ORANGE: 2, SessionMaturityLevel.RED: 1, SessionMaturityLevel.GREEN: 0}
        non_green = [b for b in active if b.exploration_level != SessionMaturityLevel.GREEN]
        if non_green:
            return max(non_green, key=lambda b: order.get(b.exploration_level, 0)).branch_id
        return active[0].branch_id if active else None

    def _compute_overall_maturity(self, branches) -> SessionMaturityLevel:
        active = [b for b in branches if b.is_active]
        if not active:
            return SessionMaturityLevel.RED
        levels = [b.exploration_level for b in active]
        if all(l == SessionMaturityLevel.GREEN for l in levels):
            return SessionMaturityLevel.GREEN
        if any(l in (SessionMaturityLevel.GREEN, SessionMaturityLevel.ORANGE) for l in levels):
            return SessionMaturityLevel.ORANGE
        return SessionMaturityLevel.RED

    def _compute_eligibility(self, overall, turn_state, decision) -> tuple:
        cog_load = getattr(turn_state, "cognitive_load", "low") or "low"
        interaction_risk = getattr(turn_state, "interaction_risk", "low") or "low"
        loop_risk = getattr(turn_state, "loop_risk", "low") or "low"
        synthesis_eligible = overall in (SessionMaturityLevel.ORANGE, SessionMaturityLevel.GREEN)
        eval_eligible = (
            overall == SessionMaturityLevel.GREEN
            and cog_load != "high"
            and interaction_risk != "high"
            and loop_risk != "high"
        )
        return synthesis_eligible, eval_eligible

    def _compute_reason_codes(self, turn_state, decision, overall, dispersion) -> list:
        codes = []
        covered = set(getattr(turn_state, "covered_points", []) or [])
        cog_load = getattr(turn_state, "cognitive_load", "low") or "low"
        interaction_risk = getattr(turn_state, "interaction_risk", "low") or "low"
        loop_risk = getattr(turn_state, "loop_risk", "low") or "low"
        if "episode_described" not in covered: codes.append(RC_NOT_ENOUGH_DESCRIPTION)
        if "concrete_actions_described" not in covered: codes.append(RC_NO_CONCRETE_ACTIONS)
        if "cause_hypothesis_named" not in covered and "cause_confirmed" not in covered:
            codes.append(RC_NO_CAUSE_NAMED)
        if "learning_rule_named" not in covered: codes.append(RC_NO_TRANSFER_RULE)
        if loop_risk == "high": codes.append(RC_LOOP_RISK_HIGH)
        if dispersion: codes.append(RC_DISPERSION_RISK)
        if overall in (SessionMaturityLevel.ORANGE, SessionMaturityLevel.GREEN):
            codes.append(RC_SYNTHESIS_ELIGIBLE)
        else:
            codes.append(RC_SYNTHESIS_BLOCKED_MATURITY)
        if overall == SessionMaturityLevel.GREEN:
            codes.append(RC_EVALUATION_ELIGIBLE)
        else:
            codes.append(RC_EVALUATION_BLOCKED_MATURITY)
        if cog_load == "high": codes.append(RC_EVALUATION_BLOCKED_COGNITIVE_LOAD)
        if interaction_risk == "high": codes.append(RC_EVALUATION_BLOCKED_INTERACTION_RISK)
        return codes

    def _missing_for_next(self, overall, turn_state) -> list:
        covered = set(getattr(turn_state, "covered_points", []) or [])
        if overall == SessionMaturityLevel.GREEN:
            return []
        missing = []
        if "episode_described" not in covered: missing.append("Décrire la situation")
        if "concrete_actions_described" not in covered: missing.append("Décrire les actions concrètes")
        if "problem_named" not in covered: missing.append("Nommer le problème")
        if overall == SessionMaturityLevel.ORANGE:
            if "future_action_named" not in covered: missing.append("Formuler une action future")
            if "learning_rule_named" not in covered: missing.append("Formuler une règle de transfert")
        return missing


def build_ui_state_from_progress(
    progress: ConversationProgress,
    gamification_profile: str = "B",
) -> UIState:
    """
    Construit UIState depuis ConversationProgress.
    Ne lit JAMAIS un champ P0 directement.
    NR-07 vérifie que UIState ne contient aucun champ P0 interdit.
    """
    maturity = progress.overall_maturity
    active = [b for b in progress.active_branches if b.is_active]
    total = max(len(active), 1)
    covered_count = sum(1 for b in active if b.exploration_level != SessionMaturityLevel.RED)
    scene_progress = covered_count / total

    priority = next((b for b in active if b.branch_id == progress.priority_branch_id), None)
    quest_label = priority.objective_label if priority else "Démarrer la conversation"
    level_map = {SessionMaturityLevel.RED: 0.0, SessionMaturityLevel.ORANGE: 0.5, SessionMaturityLevel.GREEN: 1.0}
    quest_progress = level_map.get(priority.exploration_level, 0.0) if priority else 0.0

    synthesis_state = (
        "ready" if progress.synthesis_eligible and maturity == SessionMaturityLevel.GREEN
        else "possible" if progress.synthesis_eligible
        else "locked"
    )
    eval_state = "ready" if progress.evaluation_eligible else "locked"

    scene_label_map = {
        SessionMaturityLevel.RED: "Raconter",
        SessionMaturityLevel.ORANGE: "Explorer",
        SessionMaturityLevel.GREEN: "Synthétiser",
    }

    return UIState(
        scene_label=scene_label_map.get(maturity, "Raconter"),
        scene_progress=round(scene_progress, 2),
        active_quest_label=quest_label,
        quest_progress=round(quest_progress, 2),
        maturity_color=maturity,
        synthesis_button_state=synthesis_state,
        evaluation_button_state=eval_state,
        persistent_objects=[],
        gamification_profile=gamification_profile,
    )
```

---

## Patch orchestrateur (additif LOT 1)

Dans `hugo_orchestrator.py`, **après** l'appel à `decide_conversation` :

```python
# LOT 1 — mise à jour progression conversationnelle (lecture seule sur turn_state + decision)
from backend.apps.hugo.domain.conversation_profile import ConversationProgress, ConversationPosture
from backend.apps.hugo.services.conversation_progress_calculator import (
    ConversationProgressCalculator, build_ui_state_from_progress,
)
import dataclasses

posture_value = getattr(session, "posture", "reflective_afest") or "reflective_afest"
try:
    posture = ConversationPosture(posture_value)
except ValueError:
    posture = ConversationPosture.REFLECTIVE_AFEST

from backend.apps.hugo.services.conversation_progress_calculator import (
    ConversationProgressCalculator,
    build_ui_state_from_progress,
    deserialize_conversation_progress,
)

previous_json = getattr(session, "conversation_progress", None)
previous_progress = deserialize_conversation_progress(previous_json)

calculator = ConversationProgressCalculator(posture=posture)
progress = calculator.update(
    session_id=str(session.id),
    turn_state=turn_state,
    decision=decision,
    previous_progress=previous_progress,
)
session.conversation_progress = dataclasses.asdict(progress)
session.save(update_fields=["conversation_progress"])
```

---

## Patch endpoints (remplacement stubs LOT 0)

```python
# backend/apps/hugo/views/sessions.py

import dataclasses
from backend.apps.hugo.services.conversation_progress_calculator import (
    build_ui_state_from_progress,
    deserialize_conversation_progress,
)

@action(detail=True, methods=["get"], url_path="progress")
def get_progress(self, request, pk=None):
    session = self.get_object()
    raw = getattr(session, "conversation_progress", None)
    if not raw:
        return Response({"status": "no_progress_yet", "session_id": str(session.id)})

    progress = deserialize_conversation_progress(raw)
    if progress is None:
        return Response({"error": "invalid_conversation_progress_payload"}, status=500)

    return Response(dataclasses.asdict(progress))

@action(detail=True, methods=["get"], url_path="ui-state")
def get_ui_state(self, request, pk=None):
    session = self.get_object()
    raw = getattr(session, "conversation_progress", None)

    profile = request.query_params.get("gamification_profile", "B")
    if profile not in ("A", "B", "C"):
        profile = "B"

    if not raw:
        return Response({
            "scene_label": "Raconter",
            "scene_progress": 0.0,
            "active_quest_label": "Démarrer la conversation",
            "quest_progress": 0.0,
            "maturity_color": "red",
            "synthesis_button_state": "locked",
            "evaluation_button_state": "locked",
            "persistent_objects": [],
            "gamification_profile": profile,
        })

    progress = deserialize_conversation_progress(raw)
    if progress is None:
        return Response({"error": "invalid_conversation_progress_payload"}, status=500)

    return Response(dataclasses.asdict(build_ui_state_from_progress(
        progress,
        gamification_profile=profile,
    )))
```

---

## Tests du LOT 1 (`test_conversation_progress.py` — 8 tests)

```python
import pytest
from backend.apps.hugo.domain.conversation_profile import (
    ConversationPosture, SessionMaturityLevel, ConversationProgress, ConversationBranch,
)
from backend.apps.hugo.services.conversation_progress_calculator import (
    ConversationProgressCalculator, build_ui_state_from_progress,
)

class FakeTurnState:
    def __init__(self, **kw):
        self.covered_points = kw.get("covered_points", [])
        self.remaining_open_points = kw.get("remaining_open_points", [])
        self.cognitive_load = kw.get("cognitive_load", "low")
        self.interaction_risk = kw.get("interaction_risk", "low")
        self.loop_risk = kw.get("loop_risk", "low")
        self.conversation_goal = kw.get("conversation_goal", "situation_travail")
        self.current_phase = kw.get("current_phase", "exploration")
        self.available_material = kw.get("available_material", "sufficient")  # champ réel TurnState

class FakeDecision:
    def __init__(self, **kw):
        self.pedagogical_move = kw.get("pedagogical_move", "analyze")
        self.number_of_questions = kw.get("number_of_questions", 1)

def calc(posture=ConversationPosture.REFLECTIVE_AFEST):
    return ConversationProgressCalculator(posture=posture)

def test_initial_is_red():
    p = calc().update("s1", FakeTurnState(), FakeDecision())
    assert p.overall_maturity == SessionMaturityLevel.RED

def test_orange_on_description_and_problem():
    ts = FakeTurnState(covered_points=["episode_described", "concrete_actions_described", "problem_named"])
    p = calc().update("s1", ts, FakeDecision())
    assert p.overall_maturity == SessionMaturityLevel.ORANGE

def test_green_requires_transfer_in_reflective():
    ts = FakeTurnState(covered_points=[
        "episode_described", "concrete_actions_described", "problem_named",
        "cause_hypothesis_named", "future_action_named", "learning_rule_named",
    ], remaining_open_points=[])
    p = calc().update("s1", ts, FakeDecision())
    assert p.overall_maturity == SessionMaturityLevel.GREEN

def test_green_branch_does_not_regress():
    ts_green = FakeTurnState(covered_points=[
        "episode_described", "concrete_actions_described", "problem_named",
        "cause_hypothesis_named", "future_action_named", "learning_rule_named",
    ], remaining_open_points=[])
    p_green = calc().update("s1", ts_green, FakeDecision())
    assert p_green.overall_maturity == SessionMaturityLevel.GREEN
    p_after = calc().update("s1", FakeTurnState(covered_points=["episode_described"]),
                            FakeDecision(), previous_progress=p_green)
    green_branch = next((b for b in p_after.active_branches
                        if b.exploration_level == SessionMaturityLevel.GREEN), None)
    assert green_branch is not None, "Branche GREEN a régressé — interdit"

def test_max_3_branches():
    prev = ConversationProgress(
        session_id="s1", posture=ConversationPosture.REFLECTIVE_AFEST,
        active_branches=[
            ConversationBranch(branch_id=f"b{i}", theme_label=f"t{i}",
                               objective_label=f"o{i}", is_active=True)
            for i in range(3)
        ],
    )
    ts = FakeTurnState(conversation_goal="nouveau_theme", current_phase="nouvelle_phase")
    p = calc().update("s1", ts, FakeDecision(), previous_progress=prev)
    assert sum(1 for b in p.active_branches if b.is_active) <= 3

def test_synthesis_eligible_from_orange():
    ts = FakeTurnState(covered_points=["episode_described", "concrete_actions_described", "problem_named"])
    p = calc().update("s1", ts, FakeDecision())
    assert p.synthesis_eligible is True
    assert p.evaluation_eligible is False

def test_evaluation_eligible_only_green():
    ts = FakeTurnState(covered_points=[
        "episode_described", "concrete_actions_described", "problem_named",
        "cause_hypothesis_named", "future_action_named", "learning_rule_named",
    ], remaining_open_points=[], cognitive_load="low", interaction_risk="low")
    p = calc().update("s1", ts, FakeDecision())
    assert p.evaluation_eligible is True

def test_ui_state_no_p0_fields():
    import dataclasses
    from backend.apps.hugo.domain.conversation_profile import UIState
    p = calc().update("s1", FakeTurnState(), FakeDecision())
    ui = build_ui_state_from_progress(p)
    forbidden = {
        "has_concrete_actions", "episode_clarity", "problem_salience",
        "reflection_phase", "affect_valence", "cognitive_load", "interaction_risk",
        "session_phase", "session_maturity", "evidence_strength",
        "covered_points", "remaining_open_points", "loop_risk",
    }
    ui_fields = {f.name for f in dataclasses.fields(UIState)}
    overlap = ui_fields & forbidden
    assert not overlap, f"UIState expose des champs interdits : {overlap}"
    
    def test_deserialize_conversation_progress_from_json():
    from backend.apps.hugo.services.conversation_progress_calculator import deserialize_conversation_progress

    raw = {
        "session_id": "s1",
        "posture": "reflective_afest",
        "active_branches": [{
            "branch_id": "b1",
            "theme_label": "theme_a",
            "objective_label": "objective_a",
            "referential_item_id": None,
            "exploration_level": "orange",
            "is_active": True,
            "reason_codes": [],
        }],
        "active_branches_count": 1,
        "priority_branch_id": "b1",
        "dispersion_risk": False,
        "overall_maturity": "orange",
        "synthesis_eligible": True,
        "evaluation_eligible": False,
        "missing_for_next_level": ["Formuler une action future"],
        "reason_codes": ["synthesiseligible"],
    }

    progress = deserialize_conversation_progress(raw)

    assert progress is not None
    assert progress.posture == ConversationPosture.REFLECTIVE_AFEST
    assert progress.overall_maturity == SessionMaturityLevel.ORANGE
    assert progress.active_branches[0].exploration_level == SessionMaturityLevel.ORANGE
    
    def test_ui_state_invalid_gamification_profile_falls_back_to_b(api_client, session):
    response = api_client.get(f"/api/hugo/sessions/{session.id}/ui-state/?gamification_profile=Z")
    assert response.status_code == 200
    assert response.data["gamification_profile"] == "B"
```

---

## Checklist de sortie du LOT 1

- [ ] Les 9 tests NR LOT 0 restent verts.
- [ ] Les 8 tests `test_conversation_progress.py` passent.
- [ ] `conversation_progress` mis à jour en JSONB après chaque tour.
- [ ] Endpoint `/progress` retourne ConversationProgress sérialisé.
- [ ] Endpoint `/ui-state` retourne UIState sans champ P0 brut.
- [ ] Aucune modification dans les fichiers P0.
- [ ] `available_material` accédé en lecture seule depuis TurnState (champ existant confirmé).
