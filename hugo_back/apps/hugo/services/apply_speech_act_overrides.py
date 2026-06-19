from __future__ import annotations

from typing import Any

from apps.hugo.domain.turn_state_v17 import TurnStateV17


def apply_speech_act_overrides(
    state: TurnStateV17,
) -> dict[str, Any]:
    last_act = str(state.last_learner_act or "none")
    overrides: dict[str, Any] = {
        "primary_intent": None,
        "pedagogical_move": None,
        "response_mode": None,
        "target_question_count": None,
        "number_of_questions": None,
        "response_constraints": [],
        "reason_codes": [],
        "metadata": {},
    }

    if last_act in {"ask_help", "ask_priority", "signal_confusion"}:
        overrides.update(
            {
                "primary_intent": "diagnostic_help",
                "pedagogical_move": "assist",
                "response_mode": "assist",
                "target_question_count": 0 if state.loop_risk == "high" else 1,
                "number_of_questions": 0 if state.loop_risk == "high" else 1,
            }
        )
        overrides["response_constraints"] = ["brief_help_first", "one_regulation_objective"]
        overrides["reason_codes"] = ["speech_act_help_priority"]
        overrides["metadata"] = {"speech_act_override": "help"}
        return overrides

    if last_act == "ask_recap":
        overrides.update(
            {
                "primary_intent": "produce_recap",
                "pedagogical_move": "recap",
                "response_mode": "recap",
                "target_question_count": 0,
                "number_of_questions": 0,
            }
        )
        overrides["response_constraints"] = ["continuous_text_only", "no_question_final", "one_regulation_objective"]
        overrides["reason_codes"] = ["speech_act_recap_priority"]
        overrides["metadata"] = {"speech_act_override": "recap", "audience": "learner"}
        return overrides

    if last_act == "ask_report_for_tutor":
        overrides.update(
            {
                "primary_intent": "produce_recap",
                "pedagogical_move": "recap",
                "response_mode": "recap",
                "target_question_count": 0,
                "number_of_questions": 0,
            }
        )
        overrides["response_constraints"] = ["continuous_text_only", "no_question_final", "one_regulation_objective"]
        overrides["reason_codes"] = ["speech_act_report_priority"]
        overrides["metadata"] = {"speech_act_override": "report", "audience": "tutor"}
        return overrides

    if last_act == "ask_competencies":
        overrides.update(
            {
                "primary_intent": "elicit_competencies",
                "pedagogical_move": "evaluation",
                "response_mode": "evaluation",
                "target_question_count": 0,
                "number_of_questions": 0,
            }
        )
        overrides["response_constraints"] = ["continuous_text_only", "no_question_final", "one_regulation_objective"]
        overrides["reason_codes"] = ["speech_act_competencies_priority"]
        overrides["metadata"] = {
            "speech_act_override": "competencies",
            "evaluation_kind": "recap_with_competencies",
        }
        return overrides

    if last_act == "signal_closure":
        overrides.update(
            {
                "primary_intent": "close_safely",
                "pedagogical_move": "close",
                "response_mode": "closure",
                "target_question_count": 0,
                "number_of_questions": 0,
            }
        )
        overrides["response_constraints"] = ["respect_explicit_closure", "no_question_final", "one_regulation_objective"]
        overrides["reason_codes"] = ["speech_act_closure_priority"]
        overrides["metadata"] = {"speech_act_override": "closure"}
        return overrides

    if last_act == "signal_repetition":
        overrides["reason_codes"] = ["speech_act_repetition_signal"]
        overrides["response_constraints"] = ["acknowledge_repetition_briefly"]
        overrides["metadata"] = {"speech_act_override": "repetition"}
        return overrides

    if last_act == "negotiate_next_step":
        overrides["reason_codes"] = ["speech_act_next_step"]
        overrides["metadata"] = {"speech_act_override": "next_step"}
        return overrides

    overrides["reason_codes"] = ["speech_act_no_override"]
    return overrides
