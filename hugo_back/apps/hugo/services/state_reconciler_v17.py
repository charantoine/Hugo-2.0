from __future__ import annotations

from typing import Any

from apps.hugo.domain.turn_state_v17 import TurnStateV17, from_legacy_turn_state
from apps.hugo.services.learner_speech_act_classifier import LearnerSpeechActResult


def compute_maturity_flags(state: TurnStateV17) -> dict[str, bool]:
    covered = set(state.covered_points or [])
    reflective_minimum_reached = (
        "episode_described" in covered
        and bool({"cause_hypothesis_named", "cause_confirmed"} & covered)
        and bool({"future_action_named", "learning_rule_named"} & covered)
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
        or (
            reflective_minimum_reached
            and state.loop_risk != "high"
            and state.interaction_risk != "high"
            and state.safety_or_quality_risk_level != "high"
        )
    )
    recap_eligible = bool(
        reflective_minimum_reached
        or state.need_recap
        or state.remaining_open_points in (["need_closure_confirmation"], ["none"])
    )
    evaluation_eligible = bool(
        recap_evaluation_eligible
        and state.available_material in {"medium", "high"}
        and state.technical_criterion_focus != "none"
    )
    recap_offer_already_done = bool((state.debug_signals.debug_signals or {}).get("recap_evaluation_offer_proposed"))
    return {
        "reflective_minimum_reached": reflective_minimum_reached,
        "recap_eligible": recap_eligible,
        "recap_evaluation_eligible": recap_evaluation_eligible,
        "evaluation_eligible": evaluation_eligible,
        "closure_eligible": closure_eligible,
        "recap_evaluation_offer_pending": recap_evaluation_eligible and not recap_offer_already_done,
    }


def reconcile_turn_state_v17(
    *,
    legacy_state: Any,
    speech_act_result: LearnerSpeechActResult | None = None,
    p0_classifier: dict[str, Any] | None = None,
    recent_history: list[str] | None = None,
) -> TurnStateV17:
    state = legacy_state if isinstance(legacy_state, TurnStateV17) else from_legacy_turn_state(legacy_state)
    speech = speech_act_result or LearnerSpeechActResult(
        learner_speech_act="describe_situation",
        last_learner_act="none",
        requested_output="none",
    )
    state.conversation_signals.learner_speech_act = speech.learner_speech_act
    state.conversation_signals.last_learner_act = speech.last_learner_act
    if speech.requested_output != "none":
        state.derived_signals.requested_output = speech.requested_output
    if speech.last_learner_act in {"ask_help", "ask_priority"} and state.learner_help_request == "none":
        state.conversation_signals.learner_help_request = "explicit"
    if speech.last_learner_act == "signal_closure" and state.closure_signal == "none":
        state.conversation_signals.closure_signal = "explicit"
    if speech.last_learner_act == "signal_repetition" and state.repetition_signal == "none":
        state.conversation_signals.repetition_signal = "explicit"

    flags = compute_maturity_flags(state)
    state.derived_signals.reflective_minimum_reached = flags["reflective_minimum_reached"]
    state.derived_signals.recap_eligible = flags["recap_eligible"]
    state.derived_signals.recap_evaluation_eligible = flags["recap_evaluation_eligible"]
    state.derived_signals.evaluation_eligible = flags["evaluation_eligible"]
    state.derived_signals.closure_eligible = flags["closure_eligible"]
    state.derived_signals.recap_evaluation_offer_pending = flags["recap_evaluation_offer_pending"]
    state.derived_signals.needs_recap = state.need_recap or state.derived_signals.recap_eligible
    state.derived_signals.needs_reframe = state.problem_salience == "none" and state.reflection_phase == "description"
    state.derived_signals.needs_diagnostic_help = (
        state.learner_help_request != "none"
        or speech.last_learner_act in {"ask_help", "ask_priority", "signal_confusion"}
    )
    state.derived_signals.needs_competency_elicitation = (
        state.evaluation_eligible and state.technical_criterion_focus == "none"
    )
    if state.closure_signal == "explicit":
        state.derived_signals.requested_output = "closure"
    elif speech.requested_output != "none":
        state.derived_signals.requested_output = speech.requested_output

    if state.repetition_signal == "explicit":
        state.conversation_signals.loop_risk = "high"
    elif state.loop_risk == "low" and state.consecutive_clarify_turns >= 1 and state.episode_clarity in {"medium", "high"}:
        state.conversation_signals.loop_risk = "medium"

    state.derived_signals.reopen_risk = (
        "high" if state.closure_signal != "none" else "medium" if state.repetition_signal != "none" else "low"
    )
    state.derived_signals.overquestion_risk = (
        "high" if state.loop_risk == "high" else "medium" if state.reflective_depth == "high" else "low"
    )
    if state.remaining_open_points == ["none"] or state.closure_signal == "explicit":
        state.derived_signals.coverage_status = "covered"
    elif not state.has_concrete_actions:
        state.derived_signals.coverage_status = "action_missing"
    elif state.episode_clarity == "low":
        state.derived_signals.coverage_status = "needs_clarification"
    else:
        state.derived_signals.coverage_status = "ok"

    debug = dict(state.debug_signals.debug_signals or {})
    debug["speech_act"] = speech.learner_speech_act
    debug["last_learner_act"] = speech.last_learner_act
    debug["recent_history_size"] = len(recent_history or [])
    if p0_classifier:
        debug["p0_classifier_source"] = p0_classifier.get("source", "")
        debug["p0_classifier_confidence"] = p0_classifier.get("confidence", 0.0)
        state.debug_signals.source_by_field = dict(p0_classifier.get("source_by_field") or state.source_by_field)
        if p0_classifier.get("source") == "llm_classifier":
            state.debug_signals.override_fields = sorted(
                [
                    key
                    for key, value in (p0_classifier.get("source_by_field") or {}).items()
                    if value == "llm_classifier"
                ]
            )
    state.debug_signals.debug_signals = debug
    state.debug_signals.reason_trace = list(dict.fromkeys(list(state.reason_trace) + list(speech.reason_codes)))
    return state
