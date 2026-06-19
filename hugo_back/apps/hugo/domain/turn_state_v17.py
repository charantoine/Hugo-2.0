from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from apps.hugo.domain.schemas import TurnState


@dataclass
class CoreSignalsV17:
    episode_clarity: str = "low"
    has_concrete_actions: bool = False
    problem_salience: str = "none"
    reflection_phase: str = "description"
    affect_valence: str = "neutral"
    cognitive_load: str = "low"
    interaction_risk: str = "low"
    reflective_depth: str = "low"
    evidence_strength: str = "low"
    session_phase: str = "exploration"
    session_maturity: str = "low"
    need_recap: bool = False
    need_encouragement: bool = False
    can_close_for_now: bool = False
    conversation_goal: str = "clarify_scene"


@dataclass
class DerivedSignalsV17:
    requested_output: str = "none"
    coverage_status: str = "ok"
    reopen_risk: str = "low"
    overquestion_risk: str = "low"
    reflective_minimum_reached: bool = False
    needs_diagnostic_help: bool = False
    needs_reframe: bool = False
    needs_recap: bool = False
    needs_competency_elicitation: bool = False
    recap_eligible: bool = False
    recap_evaluation_eligible: bool = False
    evaluation_eligible: bool = False
    closure_eligible: bool = False
    recap_evaluation_offer_pending: bool = False
    available_material: str = "low"
    contradiction_status: str = "none"
    current_phase: str = "exploration"
    intervention_necessity: str = "low"


@dataclass
class ConversationSignalsV17:
    learner_speech_act: str = "describe_situation"
    last_learner_act: str = "none"
    learner_help_request: str = "none"
    closure_signal: str = "none"
    repetition_signal: str = "none"
    covered_points: List[str] = field(default_factory=list)
    remaining_open_points: List[str] = field(default_factory=list)
    loop_risk: str = "low"
    last_tutorial_move: str = ""
    consecutive_clarify_turns: int = 0
    sticky_has_concrete_actions: bool = False
    tech_representation_level: str = "implicit"
    technical_criterion_focus: str = "none"
    safety_or_quality_risk_level: str = "low"


@dataclass
class DebugSignalsV17:
    debug_signals: Dict[str, Any] = field(default_factory=dict)
    source_by_field: Dict[str, Any] = field(default_factory=dict)
    override_fields: List[str] = field(default_factory=list)
    reason_trace: List[str] = field(default_factory=list)
    legacy_snapshot: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TurnStateV17:
    core_signals: CoreSignalsV17 = field(default_factory=CoreSignalsV17)
    derived_signals: DerivedSignalsV17 = field(default_factory=DerivedSignalsV17)
    conversation_signals: ConversationSignalsV17 = field(default_factory=ConversationSignalsV17)
    debug_signals: DebugSignalsV17 = field(default_factory=DebugSignalsV17)

    def __getattr__(self, name: str) -> Any:
        for block in (
            self.core_signals,
            self.derived_signals,
            self.conversation_signals,
            self.debug_signals,
        ):
            if hasattr(block, name):
                return getattr(block, name)
        raise AttributeError(name)

    def flat_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        payload.update(asdict(self.core_signals))
        payload.update(asdict(self.derived_signals))
        payload.update(asdict(self.conversation_signals))
        payload.update(asdict(self.debug_signals))
        payload["core_signals"] = asdict(self.core_signals)
        payload["derived_signals"] = asdict(self.derived_signals)
        payload["conversation_signals"] = asdict(self.conversation_signals)
        payload["debug_signals_block"] = asdict(self.debug_signals)
        return payload

    def to_dict(self) -> Dict[str, Any]:
        return self.flat_dict()


def compute_v17_coverage_status(state: TurnStateV17) -> str:
    if state.closure_signal == "explicit" or state.remaining_open_points in (["none"], []):
        return "covered"
    if state.episode_clarity == "low":
        return "needs_clarification"
    if not state.has_concrete_actions:
        return "action_missing"
    if state.evidence_strength == "low":
        return "fragile"
    return "ok"


def from_legacy_turn_state(state: TurnState) -> TurnStateV17:
    covered_points = list(getattr(state, "covered_points", []) or [])
    remaining_open_points = list(getattr(state, "remaining_open_points", []) or [])
    reflective_minimum_reached = (
        "episode_described" in covered_points
        and bool({"cause_hypothesis_named", "cause_confirmed"} & set(covered_points))
        and bool({"future_action_named", "learning_rule_named"} & set(covered_points))
    )
    recap_evaluation_eligible = (
        state.episode_clarity == "high"
        and (state.has_concrete_actions or state.sticky_has_concrete_actions)
        and state.evidence_strength in {"medium", "high"}
        and state.cognitive_load != "high"
        and state.safety_or_quality_risk_level != "high"
    )
    closure_eligible = bool(
        state.closure_signal == "explicit"
        or state.can_close_for_now
        or (reflective_minimum_reached and state.loop_risk != "high" and state.interaction_risk != "high")
    )
    requested_output = "none"
    coverage_status = "covered" if state.remaining_open_points == ["none"] else "ok"
    if state.closure_signal != "none":
        requested_output = "closure"
    core = CoreSignalsV17(
        episode_clarity=state.episode_clarity,
        has_concrete_actions=state.has_concrete_actions,
        problem_salience=state.problem_salience,
        reflection_phase=state.reflection_phase,
        affect_valence=state.affect_valence,
        cognitive_load=state.cognitive_load,
        interaction_risk=state.interaction_risk,
        reflective_depth=state.reflective_depth,
        evidence_strength=state.evidence_strength,
        session_phase=state.session_phase,
        session_maturity=state.session_maturity,
        need_recap=state.need_recap,
        need_encouragement=state.need_encouragement,
        can_close_for_now=state.can_close_for_now,
        conversation_goal=state.conversation_goal,
    )
    derived = DerivedSignalsV17(
        requested_output=requested_output,
        coverage_status=coverage_status,
        reopen_risk="high" if state.closure_signal != "none" else ("medium" if state.repetition_signal != "none" else "low"),
        overquestion_risk="high" if state.loop_risk == "high" else ("medium" if state.reflective_depth == "high" else "low"),
        reflective_minimum_reached=reflective_minimum_reached,
        needs_diagnostic_help=state.learner_help_request != "none",
        needs_reframe=state.need_reframing,
        needs_recap=state.need_recap,
        needs_competency_elicitation=recap_evaluation_eligible and state.technical_criterion_focus == "none",
        recap_eligible=state.need_recap or reflective_minimum_reached,
        recap_evaluation_eligible=recap_evaluation_eligible,
        evaluation_eligible=recap_evaluation_eligible and state.available_material in {"medium", "high"},
        closure_eligible=closure_eligible,
        recap_evaluation_offer_pending=recap_evaluation_eligible,
        available_material=state.available_material,
        contradiction_status=state.contradiction_status,
        current_phase=state.current_phase,
        intervention_necessity=state.intervention_necessity,
    )
    conv = ConversationSignalsV17(
        learner_speech_act="signal_closure" if state.closure_signal == "explicit" else "describe_situation",
        last_learner_act="signal_closure" if state.closure_signal == "explicit" else "signal_repetition" if state.repetition_signal == "explicit" else "ask_help" if state.learner_help_request == "explicit" else "none",
        learner_help_request=state.learner_help_request,
        closure_signal=state.closure_signal,
        repetition_signal=state.repetition_signal,
        covered_points=covered_points,
        remaining_open_points=remaining_open_points,
        loop_risk=state.loop_risk,
        last_tutorial_move=state.last_tutorial_move,
        consecutive_clarify_turns=state.consecutive_clarify_turns,
        sticky_has_concrete_actions=state.sticky_has_concrete_actions,
        tech_representation_level=state.tech_representation_level,
        technical_criterion_focus=state.technical_criterion_focus,
        safety_or_quality_risk_level=state.safety_or_quality_risk_level,
    )
    debug = DebugSignalsV17(
        debug_signals=dict(state.debug_signals or {}),
        source_by_field={field_name: "legacy" for field_name in core.__dict__.keys()},
        override_fields=[],
        reason_trace=["legacy_adapter"],
        legacy_snapshot=state.to_dict(),
    )
    v17 = TurnStateV17(
        core_signals=core,
        derived_signals=derived,
        conversation_signals=conv,
        debug_signals=debug,
    )
    v17.derived_signals.coverage_status = compute_v17_coverage_status(v17)
    return v17


def to_legacy_turn_state(state: TurnStateV17) -> TurnState:
    snapshot = dict(state.legacy_snapshot or {})
    base: Dict[str, Any] = {
        "episode_clarity": "low",
        "has_concrete_actions": False,
        "problem_salience": "none",
        "reflection_phase": "description",
        "reflective_depth": "low",
        "self_efficacy_signal": "neutral",
        "affect_valence": "neutral",
        "cognitive_load": "low",
        "interaction_risk": "low",
        "epistemic_balance": "balanced",
        "zpd_estimate": "in",
        "session_phase": "exploration",
        "session_maturity": "low",
        "evidence_strength": "low",
        "intervention_necessity": "low",
        "contradiction_status": "none",
        "concept_clarity": "medium",
        "available_material": "low",
        "conversation_goal": "clarify_scene",
        "current_phase": "exploration",
        "emotional_state": "neutral",
        "action_feasibility": "medium",
        "autonomy_level": "medium",
        "recent_progress": "steady",
        "need_recap": False,
        "need_encouragement": False,
        "need_reframing": False,
        "can_close_for_now": False,
        "last_tutorial_move": "",
        "consecutive_clarify_turns": 0,
        "sticky_has_concrete_actions": False,
        "tech_representation_level": "implicit",
        "technical_criterion_focus": "none",
        "safety_or_quality_risk_level": "low",
        "covered_points": [],
        "remaining_open_points": [],
        "learner_help_request": "none",
        "closure_signal": "none",
        "repetition_signal": "none",
        "loop_risk": "low",
        "assistant_meta_leak_risk": "low",
        "debug_signals": {},
    }
    for key, value in snapshot.items():
        if key in base:
            base[key] = value
    base.update(
        {
            "episode_clarity": state.episode_clarity,
            "has_concrete_actions": state.has_concrete_actions,
            "problem_salience": state.problem_salience,
            "reflection_phase": state.reflection_phase,
            "reflective_depth": state.reflective_depth,
            "affect_valence": state.affect_valence,
            "cognitive_load": state.cognitive_load,
            "interaction_risk": state.interaction_risk,
            "session_phase": state.session_phase,
            "session_maturity": state.session_maturity,
            "evidence_strength": state.evidence_strength,
            "intervention_necessity": state.intervention_necessity,
            "contradiction_status": state.contradiction_status,
            "available_material": state.available_material,
            "conversation_goal": state.conversation_goal,
            "current_phase": state.current_phase or state.session_phase,
            "need_recap": state.need_recap,
            "need_encouragement": state.need_encouragement,
            "need_reframing": state.needs_reframe,
            "can_close_for_now": state.can_close_for_now or state.closure_eligible,
            "last_tutorial_move": state.last_tutorial_move,
            "consecutive_clarify_turns": state.consecutive_clarify_turns,
            "sticky_has_concrete_actions": state.sticky_has_concrete_actions,
            "tech_representation_level": state.tech_representation_level,
            "technical_criterion_focus": state.technical_criterion_focus,
            "safety_or_quality_risk_level": state.safety_or_quality_risk_level,
            "covered_points": list(state.covered_points),
            "remaining_open_points": list(state.remaining_open_points),
            "learner_help_request": state.learner_help_request,
            "closure_signal": state.closure_signal,
            "repetition_signal": state.repetition_signal,
            "loop_risk": state.loop_risk,
            "debug_signals": {
                **dict(base.get("debug_signals") or {}),
                **dict(state.debug_signals.debug_signals or {}),
                "source_by_field": dict(state.source_by_field or {}),
                "override_fields": list(state.override_fields or []),
                "reason_trace": list(state.reason_trace or []),
                "coverage_status_v17": state.coverage_status,
                "requested_output_v17": state.requested_output,
                "recap_evaluation_eligible_v17": state.recap_evaluation_eligible,
            },
        }
    )
    return TurnState(**base)
