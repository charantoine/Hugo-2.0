from types import SimpleNamespace

import pytest

from apps.hugo.domain.schemas import TurnState
from apps.hugo.models import HugoSession, TutorPrompt
from apps.hugo.services.decision_engine import decide_conversation
from apps.hugo.services.hugo_orchestrator import build_hugo_turn
from apps.hugo.services.turn_state_analyzer import analyze_turn_state


def _session_stub(message_count: int = 0, current_phase: str = "exploration"):
    return SimpleNamespace(
        current_phase=current_phase,
        messages=SimpleNamespace(count=lambda: message_count),
    )


def _ctx_stub(summary: str | None = None, traces: list[str] | None = None, docs: list[str] | None = None):
    return SimpleNamespace(
        learner_summary=summary,
        recent_traces_info=traces or [],
        class_documents=docs or [],
    )


def _state(**overrides):
    state = TurnState(
        episode_clarity="high",
        has_concrete_actions=True,
        problem_salience="low",
        reflection_phase="analysis",
        reflective_depth="high",
        self_efficacy_signal="neutral",
        affect_valence="neutral",
        cognitive_load="low",
        interaction_risk="low",
        epistemic_balance="balanced",
        zpd_estimate="in",
        session_phase="deepening",
        session_maturity="medium",
        evidence_strength="high",
        intervention_necessity="high",
        contradiction_status="none",
        concept_clarity="high",
        available_material="high",
        conversation_goal="deepen_analysis",
        current_phase="deepening",
        emotional_state="neutral",
        action_feasibility="high",
        autonomy_level="medium",
        recent_progress="steady",
        need_recap=False,
        need_encouragement=False,
        need_reframing=False,
        can_close_for_now=False,
    )
    for key, value in overrides.items():
        setattr(state, key, value)
    return state


def test_analyzer_detects_support_need_after_successful_action():
    state = analyze_turn_state(
        session=_session_stub(message_count=2),
        user_input={
            "content": (
                "J'ai bien realise le branchement sur le tableau, "
                "mais j'ai besoin d'aide pour expliquer pourquoi j'ai choisi cet ordre."
            )
        },
        ctx=_ctx_stub(),
    )
    assert state.has_concrete_actions is True
    assert state.self_efficacy_signal == "low"
    assert state.need_encouragement is True


def test_decision_engine_uses_reassure_for_low_confidence_with_concrete_action():
    decision = decide_conversation(
        _state(
            episode_clarity="medium",
            has_concrete_actions=True,
            self_efficacy_signal="low",
            need_encouragement=True,
            reflection_phase="description",
            reflective_depth="low",
            problem_salience="low",
        )
    )
    assert decision.pedagogical_move == "reassure"
    assert decision.should_encourage is True
    assert "validation_before_question" in decision.response_constraints


def test_decision_engine_uses_reformulate_when_no_intervention_needed():
    decision = decide_conversation(
        _state(
            intervention_necessity="none",
            problem_salience="low",
            reflection_phase="analysis",
            need_recap=False,
        )
    )
    assert decision.pedagogical_move == "reformulate"
    assert "no_new_front" in decision.response_constraints


def test_analyzer_detects_recent_progress_from_content():
    state = analyze_turn_state(
        session=_session_stub(message_count=5),
        user_input={
            "content": "J'ai progresse sur le diagnostic et maintenant je vois mieux comment verifier avant de remplacer."
        },
        ctx=_ctx_stub(summary=""),
    )
    assert state.recent_progress == "improving"


@pytest.mark.django_db
def test_build_hugo_turn_calibrates_reassure_scenario(django_user_model, organisation, group):
    learner = django_user_model.objects.create(username="learner_calibration", organisation=organisation)
    tutor_prompt = TutorPrompt.objects.create(
        organisation=organisation,
        code="afest_calibration",
        name="AFEST calibration",
        prompt_type=TutorPrompt.PromptType.AFEST_HUGO,
        is_default=True,
        system_template="{base_system_intro}\n{decision_block}",
        user_template="{situation_content}",
    )
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner,
        group=group,
        tutor_prompt=tutor_prompt,
        phase_classifier_enabled=False,
    )

    turn = build_hugo_turn(
        session,
        {
            "content": (
                "J'ai bien realise le branchement, mais j'ai besoin d'aide pour comprendre "
                "si mon ordre de verification etait le bon."
            )
        },
    )

    assert turn.conversation_decision is not None
    assert turn.conversation_decision.pedagogical_move == "reassure"
    assert turn.conversation_decision.should_encourage is True
