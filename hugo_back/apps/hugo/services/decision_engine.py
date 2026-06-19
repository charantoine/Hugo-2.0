from __future__ import annotations

from apps.hugo.domain.schemas import ConversationDecision, TurnState


def decide_conversation(state: TurnState) -> ConversationDecision:
    reason_codes: list[str] = []
    response_constraints: list[str] = ["one_regulation_objective"]

    primary_intent = "stabilize_without_reopening"
    pedagogical_move = "reformulate"
    number_of_questions = 1
    question_style = "simple_open"
    should_explain_briefly = False
    should_recap = False
    should_encourage = False
    should_reframe = False
    should_close = False

    protected_mode = state.cognitive_load == "high" or state.interaction_risk == "high"
    clarify_frontier_reached = (
        state.last_tutorial_move in {"clarify", "elicit_action"}
        and state.consecutive_clarify_turns >= 1
        and state.episode_clarity in {"medium", "high"}
        and state.has_concrete_actions
    )
    explicit_closure_case = (
        state.closure_signal == "explicit"
        and state.safety_or_quality_risk_level != "high"
    )
    explicit_repetition_case = state.repetition_signal == "explicit"
    explicit_help_request_case = state.learner_help_request == "explicit"
    closeable_case = state.can_close_for_now or (
        state.closure_signal == "implicit"
        and state.remaining_open_points in (["need_closure_confirmation"], ["none"])
    )
    analysis_case = (
        state.reflection_phase == "analysis"
        or "cause_hypothesis_named" in state.covered_points
        or "cause_confirmed" in state.covered_points
    ) and state.has_concrete_actions and not clarify_frontier_reached and state.intervention_necessity != "none"
    projection_case = (
        state.reflection_phase == "projection"
        or "future_action_named" in state.covered_points
        or "learning_rule_named" in state.covered_points
    ) and state.intervention_necessity != "none"
    fil_sufficiently_covered = (
        "episode_described" in state.covered_points
        and bool(
            {"cause_hypothesis_named", "cause_confirmed", "future_action_named", "learning_rule_named"}
            & set(state.covered_points)
        )
    )

    if protected_mode:
        number_of_questions = 1
        question_style = "single_safe"
        pedagogical_move = "pace" if state.cognitive_load == "high" else "repair"
        should_explain_briefly = False
        response_constraints.extend(
            [
                "single_question_only",
                "simple_wording_only",
                "no_question_stacking",
                "no_micro_explanation",
            ]
        )
        if state.cognitive_load == "high":
            reason_codes.append("cognitive_load_high")
        if state.interaction_risk == "high":
            reason_codes.append("interaction_risk_high")
        primary_intent = "protect_and_continue"
    elif explicit_closure_case:
        primary_intent = "close_safely"
        pedagogical_move = "close"
        number_of_questions = 0
        question_style = "no_question"
        should_close = True
        response_constraints.extend(["respect_explicit_closure", "no_question_final"])
        reason_codes.append("explicit_closure")
    elif explicit_repetition_case:
        primary_intent = "repair_repetition"
        pedagogical_move = "close" if closeable_case else "repair"
        number_of_questions = 0 if pedagogical_move == "close" else 1
        question_style = "no_question" if number_of_questions == 0 else "simple_open"
        response_constraints.extend(
            [
                "acknowledge_repetition_briefly",
                "do_not_repeat_covered_point",
            ]
        )
        reason_codes.append("explicit_repetition")
    elif explicit_help_request_case:
        primary_intent = "provide_brief_help"
        pedagogical_move = "assist"
        number_of_questions = 1
        question_style = "simple_open"
        should_explain_briefly = True
        response_constraints.extend(
            [
                "brief_help_first",
                "validation_before_question",
            ]
        )
        reason_codes.append("explicit_help_request")
    elif state.safety_or_quality_risk_level in {"medium", "high"}:
        primary_intent = "secure_and_analyze"
        pedagogical_move = "analyze"
        reason_codes.append(f"safety_or_quality_risk_{state.safety_or_quality_risk_level}")
        response_constraints.append("anchor_to_referential_criterion")
        if state.technical_criterion_focus == "none":
            response_constraints.append("ask_for_criterion_explicitation")
            reason_codes.append("criterion_focus_missing")
        if state.tech_representation_level == "explicit":
            response_constraints.append("allow_practice_reference_comparison")
            reason_codes.append("technical_reference_comparison_allowed")
    elif state.contradiction_status == "suspected" and state.episode_clarity in {"medium", "high"}:
        primary_intent = "check_contradiction"
        pedagogical_move = "contrast_gently"
        reason_codes.append("contradiction_suspected")
    elif closeable_case:
        primary_intent = "close_safely"
        pedagogical_move = "close"
        should_close = True
        number_of_questions = 1 if "need_closure_confirmation" in state.remaining_open_points else 0
        question_style = "simple_open" if number_of_questions else "no_question"
        reason_codes.append("closure_eligible")
        if number_of_questions == 0:
            response_constraints.append("no_question_final")
    elif clarify_frontier_reached:
        primary_intent = "exit_clarification_loop"
        pedagogical_move = "analyze" if state.problem_salience in {"low", "high"} else "reformulate"
        reason_codes.append("anti_loop_clarify_limit")
        response_constraints.extend(
            [
                "do_not_repeat_action_clarification",
                "anchor_on_existing_actions",
            ]
        )
    elif analysis_case:
        primary_intent = "deepen_analysis"
        pedagogical_move = "analyze"
        reason_codes.append("analysis_ready")
    elif projection_case:
        primary_intent = "support_projection"
        pedagogical_move = "project"
        reason_codes.append("projection_ready")
    elif state.episode_clarity == "low":
        primary_intent = "clarify_episode"
        pedagogical_move = "clarify"
        reason_codes.append("episode_clarity_low")
    elif not state.has_concrete_actions:
        primary_intent = "elicit_concrete_action"
        pedagogical_move = "elicit_action"
        reason_codes.append("missing_concrete_actions")
    elif (
        state.problem_salience == "none"
        and state.reflection_phase == "description"
        and state.learner_help_request == "none"
        and state.repetition_signal == "none"
        and state.closure_signal == "none"
        and not fil_sufficiently_covered
        and (
            not state.remaining_open_points
            or "missing_problem_identification" in state.remaining_open_points
        )
    ):
        primary_intent = "surface_problem"
        pedagogical_move = "problematize"
        reason_codes.append("problem_salience_none")
    elif state.intervention_necessity == "none":
        primary_intent = "stabilize_without_reopening"
        pedagogical_move = "reformulate"
        reason_codes.append("intervention_not_necessary")
    else:
        primary_intent = "stabilize_description"
        pedagogical_move = "reformulate"
        reason_codes.append("description_mode")

    if not protected_mode and pedagogical_move not in {"close", "repair", "pace", "assist"}:
        if (
            state.need_encouragement
            and state.self_efficacy_signal == "low"
            and state.episode_clarity in {"medium", "high"}
            and state.has_concrete_actions
        ):
            primary_intent = "restore_confidence"
            pedagogical_move = "reassure"
            reason_codes.append("confidence_support")
            response_constraints.append("validation_before_question")
        same_micro_objective = primary_intent in {"deepen_analysis", "support_projection", "secure_and_analyze"}
        problematize_can_double = (
            pedagogical_move == "problematize"
            and state.has_concrete_actions
            and state.episode_clarity in {"medium", "high"}
            and state.loop_risk == "low"
        )
        if (
            same_micro_objective and state.episode_clarity == "high" and state.reflective_depth == "high"
        ) or problematize_can_double:
            number_of_questions = 2
            question_style = "double_same_goal"
            response_constraints.append("two_questions_same_micro_goal_max")
            reason_codes.append("double_question_allowed")
            if problematize_can_double and not same_micro_objective:
                reason_codes.append("problematize_double_question_allowed")
        else:
            number_of_questions = 1
            question_style = "simple_open"
            response_constraints.append("single_question_default")
    elif pedagogical_move in {"repair", "pace"} and not protected_mode:
        if explicit_repetition_case or state.loop_risk == "high":
            number_of_questions = 0
            question_style = "no_question"
            response_constraints.append("no_question_final")
        else:
            number_of_questions = 1
            question_style = "simple_open"
    elif pedagogical_move == "assist":
        number_of_questions = 1 if state.loop_risk != "high" else 0
        question_style = "simple_open" if number_of_questions else "no_question"
        if number_of_questions == 0:
            response_constraints.append("no_question_final")

    if pedagogical_move != "assist":
        should_explain_briefly = (
            state.zpd_estimate == "in"
            and state.reflective_depth in {"medium", "high"}
            and state.epistemic_balance != "learner_more_expert"
            and state.cognitive_load != "high"
            and state.interaction_risk != "high"
        )
    if should_explain_briefly:
        response_constraints.append("micro_explanation_one_sentence_max")
        reason_codes.append("micro_explanation_allowed")

    should_recap = state.need_recap and state.cognitive_load != "high"
    should_encourage = state.need_encouragement
    should_reframe = state.need_reframing and pedagogical_move not in {"repair", "pace"}
    should_close = should_close or (pedagogical_move == "close" and (state.can_close_for_now or state.closure_signal != "none"))

    if should_recap:
        reason_codes.append("recap_needed")
    if should_encourage:
        reason_codes.append("encouragement_needed")
    if should_reframe:
        reason_codes.append("reframing_needed")
    if should_close:
        response_constraints.append("closure_must_be_natural")
    if pedagogical_move == "reformulate":
        response_constraints.append("no_new_front")
    if pedagogical_move in {"clarify", "elicit_action"}:
        response_constraints.append("clarification_turn")
    if pedagogical_move == "assist":
        response_constraints.append("assist_briefly")

    response_constraints.append(f"question_style:{question_style}")
    response_constraints.append(f"question_count:{number_of_questions}")

    return ConversationDecision(
        primary_intent=primary_intent,
        pedagogical_move=pedagogical_move,
        number_of_questions=number_of_questions,
        question_style=question_style,
        should_explain_briefly=should_explain_briefly,
        should_recap=should_recap,
        should_encourage=should_encourage,
        should_reframe=should_reframe,
        should_close=should_close,
        response_constraints=response_constraints,
        reason_codes=reason_codes,
        metadata={
            "conversation_goal": state.conversation_goal,
            "current_phase": state.current_phase,
            "available_material": state.available_material,
            "last_tutorial_move": state.last_tutorial_move,
            "consecutive_clarify_turns": state.consecutive_clarify_turns,
            "sticky_has_concrete_actions": state.sticky_has_concrete_actions,
            "tech_representation_level": state.tech_representation_level,
            "technical_criterion_focus": state.technical_criterion_focus,
            "safety_or_quality_risk_level": state.safety_or_quality_risk_level,
            "covered_points": state.covered_points,
            "remaining_open_points": state.remaining_open_points,
            "learner_help_request": state.learner_help_request,
            "closure_signal": state.closure_signal,
            "repetition_signal": state.repetition_signal,
            "loop_risk": state.loop_risk,
            "assistant_meta_leak_risk": state.assistant_meta_leak_risk,
        },
    )
