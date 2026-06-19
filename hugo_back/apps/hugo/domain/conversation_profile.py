from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Optional


class ConversationPosture(str, Enum):
    """Canonical posture source of truth for Hugo conversation flows."""

    DIAGNOSTIC = "diagnostic"
    REFLECTIVE_AFEST = "reflective_afest"
    KNOWLEDGE_REVIEW = "knowledge_review"


class SessionMaturityLevel(str, Enum):
    """Conversation maturity label exposed to product-safe consumers."""

    RED = "red"
    ORANGE = "orange"
    GREEN = "green"


class KnowledgeItemStatus(str, Enum):
    """Canonical trainer knowledge lifecycle."""

    DECLARED = "declared"
    DERIVED_PROVISIONAL = "derived_provisional"
    VALIDATED_TRAINER = "validated_trainer"


class LearnerDisplayProfile(str, Enum):
    """Product display profile for learner UI (same UIState, different rendering)."""

    YOUTH = "youth"
    ADULT = "adult"
    PROFESSIONAL = "professional"


@dataclass
class ConversationBranch:
    branch_id: str = ""
    theme_label: str = ""
    objective_label: str = ""
    referential_item_id: Optional[str] = None
    exploration_level: SessionMaturityLevel = SessionMaturityLevel.RED
    is_active: bool = True
    reason_codes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["exploration_level"] = self.exploration_level.value
        return payload


@dataclass
class ConversationProgress:
    session_id: str = ""
    posture: ConversationPosture = ConversationPosture.REFLECTIVE_AFEST
    active_branches: list[ConversationBranch] = field(default_factory=list)
    active_branches_count: int = 0
    priority_branch_id: Optional[str] = None
    dispersion_risk: bool = False
    overall_maturity: SessionMaturityLevel = SessionMaturityLevel.RED
    synthesis_eligible: bool = False
    evaluation_eligible: bool = False
    missing_for_next_level: list[str] = field(default_factory=list)
    reason_codes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "posture": self.posture.value,
            "active_branches": [branch.to_dict() for branch in self.active_branches],
            "active_branches_count": self.active_branches_count,
            "priority_branch_id": self.priority_branch_id,
            "dispersion_risk": self.dispersion_risk,
            "overall_maturity": self.overall_maturity.value,
            "synthesis_eligible": self.synthesis_eligible,
            "evaluation_eligible": self.evaluation_eligible,
            "missing_for_next_level": list(self.missing_for_next_level or []),
            "reason_codes": list(self.reason_codes or []),
        }


@dataclass
class UIState:
    """
    Product-safe UI contract.

    This object must not expose raw P0 fields. Only derived/product labels belong here.
    """

    scene_label: str = "Raconter"
    scene_progress: float = 0.0
    active_quest_label: str = "Démarrer la conversation"
    quest_progress: float = 0.0
    maturity_color: SessionMaturityLevel = SessionMaturityLevel.RED
    synthesis_button_state: str = "locked"
    evaluation_button_state: str = "locked"
    evaluation_trigger_state: str = "red"
    evaluation_trigger_message: Optional[str] = None
    persistent_objects: list[dict[str, Any]] = field(default_factory=list)
    gamification_profile: str = "B"
    conversation_mode: dict[str, Any] = field(default_factory=dict)
    learner_display_profile: str = LearnerDisplayProfile.PROFESSIONAL.value
    cta_evaluation: dict[str, Any] = field(default_factory=dict)
    cta_synthesis: dict[str, Any] = field(default_factory=dict)
    dispersion_risk: bool = False
    priority_branch_label: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["maturity_color"] = self.maturity_color.value
        if payload.get("conversation_mode", {}).get("switch_warning") in ("", None):
            payload["conversation_mode"]["switch_warning"] = None
        return payload


def deserialize_conversation_progress(raw: Optional[dict[str, Any]]) -> Optional[ConversationProgress]:
    if not raw:
        return None
    try:
        branches = [
            ConversationBranch(
                branch_id=str(item.get("branch_id") or ""),
                theme_label=str(item.get("theme_label") or ""),
                objective_label=str(item.get("objective_label") or ""),
                referential_item_id=str(item.get("referential_item_id")) if item.get("referential_item_id") is not None else None,
                exploration_level=SessionMaturityLevel(item.get("exploration_level", SessionMaturityLevel.RED.value)),
                is_active=bool(item.get("is_active", True)),
                reason_codes=[str(code) for code in list(item.get("reason_codes") or []) if str(code).strip()],
            )
            for item in list(raw.get("active_branches") or [])
            if isinstance(item, dict)
        ]
        return ConversationProgress(
            session_id=str(raw.get("session_id") or ""),
            posture=ConversationPosture(raw.get("posture", ConversationPosture.REFLECTIVE_AFEST.value)),
            active_branches=branches,
            active_branches_count=int(raw.get("active_branches_count", len([branch for branch in branches if branch.is_active])) or 0),
            priority_branch_id=str(raw.get("priority_branch_id")) if raw.get("priority_branch_id") else None,
            dispersion_risk=bool(raw.get("dispersion_risk", False)),
            overall_maturity=SessionMaturityLevel(raw.get("overall_maturity", SessionMaturityLevel.RED.value)),
            synthesis_eligible=bool(raw.get("synthesis_eligible", False)),
            evaluation_eligible=bool(raw.get("evaluation_eligible", False)),
            missing_for_next_level=[
                str(item)
                for item in list(raw.get("missing_for_next_level") or [])
                if str(item).strip()
            ],
            reason_codes=[str(code) for code in list(raw.get("reason_codes") or []) if str(code).strip()],
        )
    except (TypeError, ValueError):
        return None


def deserialize_ui_state(raw: Optional[dict[str, Any]]) -> Optional[UIState]:
    if not raw:
        return None
    try:
        return UIState(
            scene_label=str(raw.get("scene_label") or "Raconter"),
            scene_progress=float(raw.get("scene_progress", 0.0) or 0.0),
            active_quest_label=str(raw.get("active_quest_label") or "Démarrer la conversation"),
            quest_progress=float(raw.get("quest_progress", 0.0) or 0.0),
            maturity_color=SessionMaturityLevel(raw.get("maturity_color", SessionMaturityLevel.RED.value)),
            synthesis_button_state=str(raw.get("synthesis_button_state") or "locked"),
            evaluation_button_state=str(raw.get("evaluation_button_state") or "locked"),
            evaluation_trigger_state=str(raw.get("evaluation_trigger_state") or "red"),
            evaluation_trigger_message=(
                str(raw.get("evaluation_trigger_message")).strip()
                if raw.get("evaluation_trigger_message") not in (None, "")
                else None
            ),
            persistent_objects=[
                item
                for item in list(raw.get("persistent_objects") or [])
                if isinstance(item, dict)
            ],
            gamification_profile=str(raw.get("gamification_profile") or "B"),
            conversation_mode=(
                dict(raw.get("conversation_mode"))
                if isinstance(raw.get("conversation_mode"), dict)
                else {}
            ),
            learner_display_profile=str(
                raw.get("learner_display_profile") or LearnerDisplayProfile.PROFESSIONAL.value
            ),
        )
    except (TypeError, ValueError):
        return None
