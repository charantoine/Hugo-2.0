from __future__ import annotations

from apps.hugo.domain.schemas import TeachingPlan
from apps.hugo.domain.turn_state_v17 import TurnStateV17
from apps.hugo.domain.conversation_decision_v17 import ConversationDecisionV17


def _derive_regulation_targets_v17(decision: ConversationDecisionV17) -> dict[str, float]:
    move = decision.pedagogical_move
    if move in {"assist", "clarify", "repair", "pace"}:
        return {"task": 0.65, "reasoning": 0.2, "metacognition": 0.15}
    if move in {"analyze", "micro_explain"}:
        return {"task": 0.2, "reasoning": 0.65, "metacognition": 0.15}
    if move in {"project", "consolidate", "recap", "evaluation", "close"}:
        return {"task": 0.4, "reasoning": 0.15, "metacognition": 0.45}
    return {"task": 0.3, "reasoning": 0.4, "metacognition": 0.3}


def build_teaching_plan_v17(
    state: TurnStateV17,
    decision: ConversationDecisionV17,
    session_phase: str,
) -> TeachingPlan:
    next_phase = state.session_phase
    if decision.response_mode == "closure" or state.closure_eligible:
        next_phase = "potential_closure"
    elif decision.pedagogical_move == "analyze":
        next_phase = "deepening"
    elif state.episode_clarity == "low" or not state.has_concrete_actions:
        next_phase = "exploration"

    ui_focus = {
        "assist": "Aider brièvement puis relancer avec mesure",
        "reflect": "Faire progresser un seul objectif de réflexion",
        "recap": "Consolider en mini-bilan continu",
        "evaluation": "Consolider avec compétences plausibles",
        "closure": "Clore sans rouvrir un nouveau chantier",
    }.get(decision.response_mode, "Faire progresser la scène")

    return TeachingPlan(
        conversation_profile=str((decision.metadata or {}).get("conversation_profile") or "reflective_afest"),
        session_phase=session_phase or state.session_phase,
        focus_competence={},
        learning_stage="intermediate",
        expected_level_now="participe",
        current_level="structured" if state.reflective_minimum_reached else "intermediate",
        coverage_status=state.coverage_status,
        regulation_targets=_derive_regulation_targets_v17(decision),
        open_action_items=[],
        critical_mistakes=[],
        coach_questions_candidates=[],
        rag_mode="supporting" if state.safety_or_quality_risk_level in {"medium", "high"} and decision.pedagogical_move == "analyze" else "none",
        ui_focus_label=ui_focus,
        max_questions_this_turn=decision.target_question_count,
        next_session_phase=next_phase,
        primary_intent=decision.primary_intent,
        pedagogical_move=decision.pedagogical_move,
        question_style=decision.question_style,
        should_recap=decision.should_recap,
        should_encourage=decision.should_encourage,
        should_reframe=decision.should_reframe,
        should_close=decision.should_close,
        response_constraints=list(decision.response_constraints or []),
        phase_source="state_v17",
    )


def apply_v17_decision_to_teaching_plan(
    legacy_plan: TeachingPlan,
    state: TurnStateV17,
    decision: ConversationDecisionV17,
    session_phase: str,
) -> TeachingPlan:
    v17_plan = build_teaching_plan_v17(state, decision, session_phase)
    legacy_plan.coverage_status = v17_plan.coverage_status
    legacy_plan.regulation_targets = v17_plan.regulation_targets
    legacy_plan.rag_mode = v17_plan.rag_mode
    legacy_plan.ui_focus_label = v17_plan.ui_focus_label
    legacy_plan.max_questions_this_turn = decision.target_question_count
    legacy_plan.next_session_phase = v17_plan.next_session_phase
    legacy_plan.primary_intent = decision.primary_intent
    legacy_plan.pedagogical_move = decision.pedagogical_move
    legacy_plan.question_style = decision.question_style
    legacy_plan.should_recap = decision.should_recap
    legacy_plan.should_encourage = decision.should_encourage
    legacy_plan.should_reframe = decision.should_reframe
    legacy_plan.should_close = decision.should_close
    legacy_plan.response_constraints = list(decision.response_constraints or [])
    legacy_plan.phase_source = "state_v17"
    return legacy_plan
