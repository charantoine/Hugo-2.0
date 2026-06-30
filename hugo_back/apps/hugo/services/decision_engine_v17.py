from __future__ import annotations

import re

from apps.hugo.domain.schemas import (
    CONVERSATION_PROFILE_DIAGNOSTIC,
    CONVERSATION_PROFILE_KNOWLEDGE_REVIEW,
    CONVERSATION_PROFILE_REFLECTIVE_AFEST,
    normalize_conversation_profile,
)
from apps.hugo.domain.conversation_decision_v17 import ConversationDecisionV17
from apps.hugo.domain.turn_state_v17 import TurnStateV17
from apps.hugo.services.apply_speech_act_overrides import apply_speech_act_overrides
from apps.hugo.services.state_reconciler_v17 import compute_maturity_flags


def _normalize_topic(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def is_redundant_question_candidate(
    candidate_question: str,
    covered_points: list[str],
    remaining_open_points: list[str],
    last_tutorial_move: str,
    blocked_question_topics: list[str] | None = None,
) -> bool:
    clean = _normalize_topic(candidate_question)
    if not clean:
        return False
    blocked = {_normalize_topic(topic) for topic in (blocked_question_topics or []) if _normalize_topic(topic)}
    covered = {_normalize_topic(topic) for topic in (covered_points or []) if _normalize_topic(topic)}
    remaining = {_normalize_topic(topic) for topic in (remaining_open_points or []) if _normalize_topic(topic)}
    if any(topic and topic in clean for topic in blocked):
        return True
    if any(topic and topic in clean for topic in covered if topic not in remaining):
        return True
    if last_tutorial_move in {"clarify", "elicit_action"} and "décrire" in clean:
        return True
    return False


def _build_decision(
    *,
    primary_intent: str,
    pedagogical_move: str,
    response_mode: str,
    target_question_count: int,
    state: TurnStateV17,
    reason_codes: list[str],
    response_constraints: list[str] | None = None,
    metadata: dict | None = None,
    should_close: bool = False,
    should_recap: bool = False,
    should_explain_briefly: bool = False,
    should_acknowledge_repetition: bool = False,
    should_acknowledge_closure: bool = False,
    conversation_profile: str = CONVERSATION_PROFILE_REFLECTIVE_AFEST,
) -> ConversationDecisionV17:
    response_constraints = list(response_constraints or [])
    metadata = dict(metadata or {})
    target_question_count = max(0, min(int(target_question_count), 2))
    response_constraints = list(
        dict.fromkeys(
            ["one_regulation_objective"]
            + response_constraints
            + [f"response_mode:{response_mode}", f"target_question_count:{target_question_count}"]
        )
    )
    number_of_questions = target_question_count
    question_style = "no_question" if target_question_count <= 0 else ("double_same_goal" if target_question_count >= 2 else "simple_open")
    blocked_topics = list(dict.fromkeys(list(state.covered_points or [])))
    decision = ConversationDecisionV17(
        primary_intent=primary_intent,
        pedagogical_move=pedagogical_move,
        response_mode=response_mode,
        target_question_count=target_question_count,
        number_of_questions=number_of_questions,
        question_style=question_style,
        question_bundling_allowed=target_question_count >= 2,
        micro_explanation_allowed=should_explain_briefly,
        should_explain_briefly=should_explain_briefly,
        should_recap=should_recap,
        should_encourage=state.need_encouragement,
        should_reframe=state.needs_reframe,
        should_close=should_close,
        should_acknowledge_repetition=should_acknowledge_repetition,
        should_acknowledge_closure=should_acknowledge_closure,
        blocked_question_topics=blocked_topics,
        response_constraints=response_constraints,
        reason_codes=list(dict.fromkeys(reason_codes)),
        metadata={
            "contract_version": "1.7",
            "conversation_profile": normalize_conversation_profile(conversation_profile),
            "coverage_status": state.coverage_status,
            "requested_output": state.requested_output,
            "last_learner_act": state.last_learner_act,
            "learner_speech_act": state.learner_speech_act,
            "loop_risk": state.loop_risk,
            "covered_points": list(state.covered_points or []),
            "remaining_open_points": list(state.remaining_open_points or []),
            **metadata,
        },
        effective_max_questions_this_turn=target_question_count,
    )
    return decision


def decide_conversation_v17(
    state: TurnStateV17,
    conversation_profile: str = CONVERSATION_PROFILE_REFLECTIVE_AFEST,
) -> ConversationDecisionV17:
    profile = normalize_conversation_profile(conversation_profile)
    flags = compute_maturity_flags(state)
    speech_act = apply_speech_act_overrides(state)

    if speech_act.get("primary_intent"):
        metadata = dict(speech_act.get("metadata") or {})
        metadata["speech_act_first"] = True
        return _build_decision(
            primary_intent=speech_act["primary_intent"],
            pedagogical_move=speech_act["pedagogical_move"],
            response_mode=speech_act["response_mode"],
            target_question_count=speech_act["target_question_count"],
            state=state,
            reason_codes=list(speech_act.get("reason_codes") or []),
            response_constraints=list(speech_act.get("response_constraints") or []),
            metadata=metadata,
            should_close=speech_act["response_mode"] == "closure",
            should_recap=speech_act["response_mode"] in {"recap", "evaluation"},
            should_explain_briefly=speech_act["response_mode"] == "assist",
            should_acknowledge_repetition=state.repetition_signal == "explicit",
            should_acknowledge_closure=state.closure_signal == "explicit",
            conversation_profile=profile,
        )

    if state.safety_or_quality_risk_level in {"medium", "high"}:
        return _build_decision(
            primary_intent="deepen_analysis",
            pedagogical_move="analyze",
            response_mode="reflect",
            target_question_count=1,
            state=state,
            reason_codes=[f"safety_priority_{state.safety_or_quality_risk_level}"],
            response_constraints=["anchor_to_referential_criterion"],
            metadata={"safety_priority": True},
            should_explain_briefly=state.cognitive_load != "high",
            conversation_profile=profile,
        )

    if profile == CONVERSATION_PROFILE_DIAGNOSTIC and (
        state.learner_help_request != "none"
        or state.episode_clarity == "low"
        or state.last_learner_act in {"ask_help", "signal_confusion"}
    ):
        return _build_decision(
            primary_intent="diagnostic_help" if state.learner_help_request != "none" else "clarify_scene",
            pedagogical_move="assist" if state.learner_help_request != "none" else "clarify",
            response_mode="assist" if state.learner_help_request != "none" else "reflect",
            target_question_count=1,
            state=state,
            reason_codes=["diagnostic_profile_priority"],
            response_constraints=["diagnostic_posture", "single_micro_objective"],
            should_explain_briefly=True,
            conversation_profile=profile,
        )

    if profile == CONVERSATION_PROFILE_KNOWLEDGE_REVIEW and state.available_material in {"medium", "high"}:
        return _build_decision(
            primary_intent="stabilize_knowledge",
            pedagogical_move="assist" if state.learner_help_request != "none" else "reformulate",
            response_mode="assist",
            target_question_count=0 if state.cognitive_load == "high" else 1,
            state=state,
            reason_codes=["knowledge_review_profile"],
            response_constraints=["anchor_to_known_rule", "keep_explanation_short"],
            should_explain_briefly=True,
            should_recap=state.need_recap,
            conversation_profile=profile,
        )

    if state.repetition_signal == "explicit" or state.loop_risk == "high":
        if flags["closure_eligible"]:
            return _build_decision(
                primary_intent="close_safely",
                pedagogical_move="close",
                response_mode="closure",
                target_question_count=0,
                state=state,
                reason_codes=["repetition_then_close"],
                response_constraints=["no_question_final", "respect_explicit_closure"],
                metadata={"loop_breaker": True},
                should_close=True,
                should_acknowledge_repetition=True,
                conversation_profile=profile,
            )
        return _build_decision(
            primary_intent="repair_interaction",
            pedagogical_move="repair",
            response_mode="reflect",
            target_question_count=0,
            state=state,
            reason_codes=["repetition_loop_priority"],
            response_constraints=["acknowledge_repetition_briefly", "no_question_final"],
            metadata={"loop_breaker": True},
            should_acknowledge_repetition=True,
            conversation_profile=profile,
        )

    if flags["recap_evaluation_offer_pending"]:
        return _build_decision(
            primary_intent="produce_recap",
            pedagogical_move="consolidate",
            response_mode="reflect",
            target_question_count=1,
            state=state,
            reason_codes=["maturity_pivot_offer_pending"],
            response_constraints=["offer_recap_pivot_once", "short_question_only"],
            metadata={
                "offer_recap_evaluation": True,
                "offer_deferred": False,
                "evaluation_kind": "recap_with_competencies" if flags["evaluation_eligible"] else "",
            },
            conversation_profile=profile,
        )

    if state.reflection_phase == "analysis" and state.has_concrete_actions and state.intervention_necessity != "none":
        target = 2 if state.episode_clarity == "high" and state.reflective_depth == "high" and state.overquestion_risk == "low" else 1
        return _build_decision(
            primary_intent="deepen_analysis",
            pedagogical_move="analyze",
            response_mode="reflect",
            target_question_count=target,
            state=state,
            reason_codes=["analysis_opportunity"],
            response_constraints=["single_micro_objective"],
            should_explain_briefly=state.cognitive_load != "high" and state.interaction_risk != "high",
            conversation_profile=profile,
        )

    if state.reflection_phase == "projection" and state.intervention_necessity != "none":
        target = 2 if state.episode_clarity == "high" and state.loop_risk == "low" else 1
        return _build_decision(
            primary_intent="support_projection",
            pedagogical_move="project",
            response_mode="reflect",
            target_question_count=target,
            state=state,
            reason_codes=["projection_opportunity"],
            conversation_profile=profile,
        )

    if flags["closure_eligible"]:
        return _build_decision(
            primary_intent="close_safely",
            pedagogical_move="close",
            response_mode="closure",
            target_question_count=0,
            state=state,
            reason_codes=["closure_eligible"],
            response_constraints=["no_question_final"],
            should_close=True,
            should_acknowledge_closure=state.closure_signal != "none",
            conversation_profile=profile,
        )

    if state.episode_clarity == "low" or not state.has_concrete_actions:
        return _build_decision(
            primary_intent="clarify_scene",
            pedagogical_move="clarify",
            response_mode="reflect",
            target_question_count=1,
            state=state,
            reason_codes=["clarify_scene_priority"],
            response_constraints=["clarification_turn"],
            conversation_profile=profile,
        )

    if state.problem_salience == "none" and state.reflection_phase == "description":
        return _build_decision(
            primary_intent="surface_problem",
            pedagogical_move="reformulate",
            response_mode="reflect",
            target_question_count=1,
            state=state,
            reason_codes=["surface_problem_fallback"],
            response_constraints=["no_new_front"],
            conversation_profile=profile,
        )

    return _build_decision(
        primary_intent="clarify_scene" if state.intervention_necessity != "none" else "produce_recap",
        pedagogical_move="reformulate",
        response_mode="reflect",
        target_question_count=1 if state.intervention_necessity != "none" else 0,
        state=state,
        reason_codes=["default_reflect_fallback"],
        response_constraints=["no_new_front"],
        conversation_profile=profile,
    )
