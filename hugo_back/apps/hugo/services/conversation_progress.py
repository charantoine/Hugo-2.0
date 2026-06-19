from __future__ import annotations

from typing import Any

from apps.hugo.domain.schemas import ConversationProgress, normalize_conversation_profile

SCENE_STEPS = [
    {"id": "raconter", "label": "Raconter"},
    {"id": "comprendre", "label": "Comprendre"},
    {"id": "decider", "label": "Décider"},
    {"id": "retenir", "label": "Retenir"},
    {"id": "transmettre", "label": "Transmettre"},
]


def _normalize_token(value: Any) -> str:
    return str(value or "").strip().lower()


def _score_signal(value: Any) -> int:
    normalized = _normalize_token(value)
    if normalized in {"high", "élevé", "eleve", "strong", "fort", "ready", "covered", "true"}:
        return 2
    if normalized in {"medium", "moyen", "moderate", "ok", "partial"}:
        return 1
    return 0


def _to_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _derive_stage_index(turn_state: Any, traces_count: int) -> int:
    if not turn_state:
        return 0
    covered_points = _to_list(getattr(turn_state, "covered_points", []))
    remaining_open_points = _to_list(getattr(turn_state, "remaining_open_points", []))

    stage_index = 0
    if _score_signal(getattr(turn_state, "episode_clarity", "")) > 0 or covered_points:
        stage_index = max(stage_index, 1)
    if bool(getattr(turn_state, "has_concrete_actions", False)):
        stage_index = max(stage_index, 2)
    if (
        _score_signal(getattr(turn_state, "reflective_depth", "")) > 0
        or _score_signal(getattr(turn_state, "recent_progress", "")) > 0
        or _score_signal(getattr(turn_state, "evidence_strength", "")) > 0
    ):
        stage_index = max(stage_index, 3)
    if (
        traces_count > 0
        or bool(getattr(turn_state, "can_close_for_now", False))
        or _normalize_token(getattr(turn_state, "closure_signal", "")) == "explicit"
        or (remaining_open_points == [] and stage_index >= 2)
    ):
        stage_index = max(stage_index, 4)
    return min(stage_index, len(SCENE_STEPS) - 1)


def _maturity_label(stage_index: int) -> str:
    return ["starting", "exploring", "acting", "consolidating", "closing"][stage_index]


def build_conversation_progress(
    *,
    session: Any,
    turn_state: Any,
    conversation_decision: Any,
    teaching_plan: Any,
    conversation_profile: str,
    rag_selections: list[Any] | None = None,
    traces_count: int = 0,
) -> ConversationProgress:
    profile = normalize_conversation_profile(conversation_profile)
    covered_points = _to_list(getattr(turn_state, "covered_points", []))
    remaining_open_points = _to_list(getattr(turn_state, "remaining_open_points", []))
    stage_index = _derive_stage_index(turn_state, traces_count)
    current_step = SCENE_STEPS[stage_index]
    meaningful_progress = bool(covered_points or remaining_open_points or traces_count or getattr(turn_state, "episode_clarity", ""))
    percent = 0 if not meaningful_progress and stage_index == 0 else round(((stage_index + 1) / len(SCENE_STEPS)) * 100)

    focus_competence = getattr(teaching_plan, "focus_competence", {}) or {}
    branch_label = (
        str(focus_competence.get("label") or "").strip()
        or str(getattr(turn_state, "conversation_goal", "") or "").strip()
        or "Progression de séance"
    )
    branch_key = (
        str(focus_competence.get("criterion_code") or "").strip()
        or str(focus_competence.get("item_code") or "").strip()
        or str(getattr(turn_state, "conversation_goal", "") or "").strip()
        or "session"
    )
    active_objective = (
        str(getattr(teaching_plan, "ui_focus_label", "") or "").strip()
        or str(getattr(conversation_decision, "primary_intent", "") or "").strip()
        or "Faire progresser la séance"
    )
    closure_eligible = bool(
        getattr(conversation_decision, "should_close", False)
        or getattr(turn_state, "can_close_for_now", False)
        or _normalize_token(getattr(turn_state, "closure_signal", "")) == "explicit"
    )
    can_summarize = bool(
        closure_eligible
        or getattr(conversation_decision, "should_recap", False)
        or getattr(turn_state, "need_recap", False)
    )
    decision_metadata = getattr(conversation_decision, "metadata", {}) or {}
    evaluation_eligible = bool(
        decision_metadata.get("evaluation_kind")
        or decision_metadata.get("offer_recap_evaluation")
        or _normalize_token(getattr(turn_state, "technical_criterion_focus", "")) not in {"", "none"}
    )
    rag_allowed = str(getattr(teaching_plan, "rag_mode", "none") or "none") != "none"
    tutor_signal_summary = {
        "current_phase": str(getattr(session, "current_phase", "") or getattr(turn_state, "session_phase", "")),
        "decision_move": str(getattr(conversation_decision, "pedagogical_move", "") or ""),
        "question_style": str(getattr(conversation_decision, "question_style", "") or ""),
        "loop_risk": str(getattr(turn_state, "loop_risk", "") or "low"),
        "cognitive_load": str(getattr(turn_state, "cognitive_load", "") or "low"),
        "coverage_status": str(getattr(teaching_plan, "coverage_status", "") or ""),
    }

    return ConversationProgress(
        conversation_profile=profile,
        branch_key=branch_key or "session",
        branch_label=branch_label,
        active_objective=active_objective,
        stage_index=stage_index,
        current_step_id=current_step["id"],
        current_step_label=current_step["label"],
        percent=percent,
        maturity=_maturity_label(stage_index),
        can_summarize=can_summarize,
        evaluation_eligible=evaluation_eligible,
        closure_eligible=closure_eligible,
        rag_allowed=rag_allowed,
        supported_by_documents=bool(rag_selections),
        covered_points=covered_points[:6],
        remaining_open_points=remaining_open_points[:6],
        reason_codes=list(getattr(conversation_decision, "reason_codes", []) or [])[:6],
        next_recommended_action=(remaining_open_points[0] if remaining_open_points else active_objective),
        tutor_signal_summary=tutor_signal_summary,
    )
