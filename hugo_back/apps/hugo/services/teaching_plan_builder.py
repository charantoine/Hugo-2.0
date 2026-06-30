from __future__ import annotations

from typing import Dict, Any
import re

from apps.hugo.domain.schemas import (
    CONVERSATION_PROFILE_DIAGNOSTIC,
    CONVERSATION_PROFILE_KNOWLEDGE_REVIEW,
    ConversationDecision,
    SESSION_PHASE_DEEPENING,
    SESSION_PHASE_EXPLORATION,
    SESSION_PHASE_OPENING,
    SESSION_PHASE_POTENTIAL_CLOSURE,
    LearnerStateSlice,
    LearningStage,
    PedagogicalProfile,
    TeachingPlan,
    TurnState,
    normalize_conversation_profile,
    normalize_session_phase,
)

PHASE_ORDER = [
    SESSION_PHASE_OPENING,
    SESSION_PHASE_EXPLORATION,
    SESSION_PHASE_DEEPENING,
    SESSION_PHASE_POTENTIAL_CLOSURE,
]
PHASE_INDEX = {phase: idx for idx, phase in enumerate(PHASE_ORDER)}


def _normalize_phase(value: Any) -> str:
    return normalize_session_phase(value)


def _contains_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def compute_next_session_phase(current_phase: str, user_input: Dict[str, Any]) -> str:
    """
    Deterministic phase progression for POC:
    opening -> exploration -> deepening -> potential_closure.
    """
    phase = _normalize_phase(current_phase)
    text = str(user_input.get("content", "") or "")

    if phase == SESSION_PHASE_OPENING:
        if text.strip():
            return SESSION_PHASE_EXPLORATION
        return SESSION_PHASE_OPENING

    if phase == SESSION_PHASE_EXPLORATION:
        reasoning_patterns = [
            r"\bparce que\b",
            r"\bj['’]ai (choisi|d[eé]cid[eé]|estim[eé])\b",
            r"\b(crit[eè]re|analyse|raisonnement|cause|cons[eé]quence|arbitrage)\b",
            r"\bje pense que\b",
        ]
        if _contains_any(text, reasoning_patterns):
            return SESSION_PHASE_DEEPENING
        return SESSION_PHASE_EXPLORATION

    if phase == SESSION_PHASE_DEEPENING:
        action_patterns = [
            r"\bje vais\b",
            r"\bprochaine fois\b",
            r"\bplan d['’ ]action\b",
            r"\bje m['’]engage\b",
            r"\b(etape|[eé]tape|checklist|verification|v[eé]rification)\b",
        ]
        if _contains_any(text, action_patterns):
            return SESSION_PHASE_POTENTIAL_CLOSURE
        return SESSION_PHASE_DEEPENING

    return SESSION_PHASE_POTENTIAL_CLOSURE


def _derive_regulation_targets(
    pedagogical_profile: PedagogicalProfile,
    turn_state: TurnState | None,
    conversation_decision: ConversationDecision | None,
    conversation_profile: str,
) -> dict[str, float]:
    if conversation_profile == CONVERSATION_PROFILE_DIAGNOSTIC:
        return {"task": 0.6, "reasoning": 0.3, "metacognition": 0.1}
    if conversation_profile == CONVERSATION_PROFILE_KNOWLEDGE_REVIEW:
        return {"task": 0.25, "reasoning": 0.55, "metacognition": 0.2}
    if not conversation_decision:
        return pedagogical_profile.focus_weights or {
            "task": 0.33,
            "reasoning": 0.34,
            "metacognition": 0.33,
        }

    move = conversation_decision.pedagogical_move
    if move in {"clarify", "elicit_action", "pace", "repair", "reassure", "assist"}:
        return {"task": 0.65, "reasoning": 0.2, "metacognition": 0.15}
    if move == "reformulate":
        return {"task": 0.25, "reasoning": 0.15, "metacognition": 0.6}
    if move in {"analyze", "contrast_gently", "problematize"}:
        return {"task": 0.15, "reasoning": 0.7, "metacognition": 0.15}
    if move in {"project", "close"}:
        return {"task": 0.45, "reasoning": 0.15, "metacognition": 0.4}
    if turn_state and turn_state.need_reframing:
        return {"task": 0.35, "reasoning": 0.25, "metacognition": 0.4}
    return pedagogical_profile.focus_weights or {
        "task": 0.33,
        "reasoning": 0.34,
        "metacognition": 0.33,
    }


def _select_focus_candidate(
    learner_slice: LearnerStateSlice,
    conversation_decision: ConversationDecision | None,
) -> dict[str, Any] | None:
    if not learner_slice.focus_candidates:
        return None
    if not conversation_decision:
        return learner_slice.focus_candidates[0]

    move = conversation_decision.pedagogical_move

    def score(candidate: dict[str, Any]) -> tuple[int, int, int, str]:
        coach_questions = list(candidate.get("coach_questions") or [])
        common_mistakes = list(candidate.get("common_mistakes") or [])
        example_evidence = list(candidate.get("example_evidence") or [])
        example_situations = list(candidate.get("example_situations") or [])
        uncovered = len(candidate.get("covered_criteria_codes") or [])
        if move in {"analyze", "contrast_gently", "problematize"}:
            return (len(common_mistakes), len(coach_questions), len(example_situations), str(candidate.get("label") or ""))
        if move in {"elicit_action", "project"}:
            return (len(example_evidence), len(example_situations), len(coach_questions), str(candidate.get("label") or ""))
        return (len(coach_questions), len(example_situations), -uncovered, str(candidate.get("label") or ""))

    return sorted(learner_slice.focus_candidates, key=score, reverse=True)[0]


def _derive_ui_focus_label(
    turn_state: TurnState | None,
    conversation_decision: ConversationDecision | None,
    user_input: Dict[str, Any],
    conversation_profile: str,
) -> str:
    if user_input.get("ui_focus_label"):
        return str(user_input["ui_focus_label"])
    if conversation_profile == CONVERSATION_PROFILE_DIAGNOSTIC:
        return "Isoler le point qui bloque vraiment"
    if conversation_profile == CONVERSATION_PROFILE_KNOWLEDGE_REVIEW:
        return "Stabiliser le repère ou la méthode utile"
    if not turn_state or not conversation_decision:
        return "Comprendre comment tu as décidé"
    move = conversation_decision.pedagogical_move
    labels = {
        "clarify": "Clarifier la situation vécue",
        "elicit_action": "Faire émerger l'action réelle",
        "problematize": "Faire apparaître le point à analyser",
        "analyze": "Approfondir le raisonnement de l'apprenant",
        "contrast_gently": "Vérifier un possible décalage",
        "project": "Préparer la prochaine action",
        "close": "Consolider et conclure sans bloquer",
        "pace": "Alléger la charge du tour",
        "repair": "Protéger la relation et rester simple",
        "assist": "Aider brièvement avant de relancer",
        "reassure": "Rassurer et consolider la confiance",
        "reformulate": "Stabiliser sans ouvrir un nouveau front",
    }
    return labels.get(move, "Comprendre comment tu as décidé")


def _derive_coverage_status(
    user_input: Dict[str, Any],
    turn_state: TurnState | None,
) -> str:
    explicit_status = str(user_input.get("coverage_status") or "").strip()
    if explicit_status:
        return explicit_status
    if not turn_state:
        return "ok"
    if turn_state.closure_signal == "explicit" or turn_state.remaining_open_points == ["none"]:
        return "covered"
    if turn_state.episode_clarity == "low":
        return "needs_clarification"
    if not turn_state.has_concrete_actions:
        return "action_missing"
    if turn_state.evidence_strength == "low":
        return "fragile"
    return "ok"


def _derive_rag_mode(
    user_input: Dict[str, Any],
    turn_state: TurnState | None,
    conversation_decision: ConversationDecision | None,
    conversation_profile: str,
) -> str:
    explicit_mode = str(user_input.get("rag_mode") or "").strip()
    if explicit_mode:
        return explicit_mode
    if not turn_state or not conversation_decision:
        return "none"
    if conversation_profile == CONVERSATION_PROFILE_KNOWLEDGE_REVIEW and turn_state.available_material in {"medium", "high"}:
        return "supporting"
    if conversation_profile == CONVERSATION_PROFILE_DIAGNOSTIC and turn_state.learner_help_request == "explicit":
        return "supporting"
    if (
        turn_state.available_material in {"medium", "high"}
        and turn_state.safety_or_quality_risk_level in {"medium", "high"}
        and conversation_decision.pedagogical_move in {"analyze", "contrast_gently"}
    ):
        return "supporting"
    content = str(user_input.get("content") or "").lower()
    if (
        turn_state.safety_or_quality_risk_level == "high"
        and conversation_decision.pedagogical_move == "analyze"
        and any(term in content for term in ["procedure", "procédure", "checklist", "securite", "sécurité"])
    ):
        return "supporting"
    return "none"


def _derive_next_phase_from_state(
    current_phase: str,
    user_input: Dict[str, Any],
    turn_state: TurnState | None,
    conversation_decision: ConversationDecision | None,
) -> str:
    if not turn_state or not conversation_decision:
        return compute_next_session_phase(current_phase, user_input)
    if conversation_decision.should_close or turn_state.closure_signal == "explicit" or turn_state.can_close_for_now:
        return SESSION_PHASE_POTENTIAL_CLOSURE
    if turn_state.episode_clarity == "low" or not turn_state.has_concrete_actions:
        return SESSION_PHASE_EXPLORATION
    if turn_state.reflection_phase == "analysis":
        return SESSION_PHASE_DEEPENING
    if turn_state.reflection_phase == "projection" and turn_state.evidence_strength in {"medium", "high"}:
        return SESSION_PHASE_POTENTIAL_CLOSURE
    return compute_next_session_phase(current_phase, user_input)


def build_teaching_plan(
    learner_slice: LearnerStateSlice,
    learning_stage: LearningStage,
    pedagogical_profile: PedagogicalProfile,
    user_input: Dict[str, Any],
    max_questions_per_turn: int,
    conversation_profile: str = "reflective_afest",
    turn_state: TurnState | None = None,
    conversation_decision: ConversationDecision | None = None,
) -> TeachingPlan:
    """
    Build a compact TeachingPlan as described in the addendum.

    This first implementation is intentionally simple and deterministic; it can be
    enriched later without changing the external contract.
    """
    # Focus competence: pick first candidate if any, otherwise derive from learning_stage.
    selected_focus = _select_focus_candidate(learner_slice, conversation_decision)
    if selected_focus:
        focus = selected_focus
        focus_competence = {
            "item_id": focus.get("item_id"),
            "label": focus.get("label"),
            "item_code": focus.get("item_code"),
            "block_code": focus.get("block_code"),
            "block_label": focus.get("block_label"),
            "criterion_id": focus.get("criterion_id"),
            "criterion_code": focus.get("criterion_code"),
            "criterion_label": focus.get("criterion_label"),
            "covered_criteria_codes": focus.get("covered_criteria_codes", []),
            "coach_questions": focus.get("coach_questions", []),
            "common_mistakes": focus.get("common_mistakes", []),
            "example_situations": focus.get("example_situations", []),
            "example_evidence": focus.get("example_evidence", []),
            "linked_documents": focus.get("linked_documents", []),
            "tasks": focus.get("tasks", []),
            "primary_task_code": focus.get("primary_task_code", ""),
            "primary_task_label": focus.get("primary_task_label", ""),
            "activity_code": focus.get("activity_code", ""),
            "activity_label": focus.get("activity_label", ""),
        }
    else:
        focus_competence = {
            "item_id": learning_stage.item_id,
            "label": "",
        }

    normalized_profile = normalize_conversation_profile(conversation_profile)
    regulation_targets = _derive_regulation_targets(
        pedagogical_profile=pedagogical_profile,
        turn_state=turn_state,
        conversation_decision=conversation_decision,
        conversation_profile=normalized_profile,
    )

    open_action_items = [
        item.get("label") if isinstance(item, dict) else str(item)
        for item in learner_slice.open_action_items
    ]

    coach_candidates = [
        q.get("label")
        for q in (pedagogical_profile.coach_questions_typed or [])
        if isinstance(q, dict) and q.get("label")
    ]
    overlay_coach_questions = [
        str(question).strip()
        for question in (focus_competence.get("coach_questions") or [])
        if str(question).strip()
    ]
    if overlay_coach_questions:
        coach_candidates = overlay_coach_questions[:3] + coach_candidates
    critical_mistakes = list(pedagogical_profile.critical_mistakes or [])
    overlay_common_mistakes = [
        str(item).strip()
        for item in (focus_competence.get("common_mistakes") or [])
        if str(item).strip()
    ]
    if overlay_common_mistakes:
        critical_mistakes = overlay_common_mistakes[:3] + critical_mistakes

    ui_focus_label = _derive_ui_focus_label(turn_state, conversation_decision, user_input, normalized_profile)
    session_phase = turn_state.session_phase if turn_state else _normalize_phase(user_input.get("session_phase", "exploration"))
    next_session_phase = _derive_next_phase_from_state(
        current_phase=session_phase,
        user_input=user_input,
        turn_state=turn_state,
        conversation_decision=conversation_decision,
    )
    current_level = user_input.get("current_level", learning_stage.stage)
    if turn_state:
        if turn_state.concept_clarity == "low":
            current_level = "emergent"
        elif turn_state.concept_clarity == "medium":
            current_level = "intermediate"
        elif turn_state.concept_clarity == "high":
            current_level = "structured"

    return TeachingPlan(
        conversation_profile=normalized_profile,
        session_phase=session_phase,
        focus_competence=focus_competence,
        learning_stage=learning_stage.stage,
        expected_level_now=learning_stage.expected_level_now,
        current_level=current_level,
        coverage_status=_derive_coverage_status(user_input, turn_state),
        regulation_targets=regulation_targets,
        open_action_items=open_action_items,
        critical_mistakes=critical_mistakes,
        coach_questions_candidates=coach_candidates,
        rag_mode=_derive_rag_mode(user_input, turn_state, conversation_decision, normalized_profile),
        ui_focus_label=ui_focus_label,
        max_questions_this_turn=max_questions_per_turn,
        next_session_phase=next_session_phase,
        primary_intent=conversation_decision.primary_intent if conversation_decision else "",
        pedagogical_move=conversation_decision.pedagogical_move if conversation_decision else "",
        question_style=conversation_decision.question_style if conversation_decision else "simple_open",
        should_recap=conversation_decision.should_recap if conversation_decision else False,
        should_encourage=conversation_decision.should_encourage if conversation_decision else False,
        should_reframe=conversation_decision.should_reframe if conversation_decision else False,
        should_close=conversation_decision.should_close if conversation_decision else False,
        response_constraints=list(conversation_decision.response_constraints) if conversation_decision else [],
        phase_source="state_adapter" if turn_state else "deterministic_rules",
    )

