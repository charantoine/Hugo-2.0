from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.test import SimpleTestCase
from django.urls import reverse

from apps.hugo.domain.schemas import TurnState
from apps.hugo.models import HugoMessage, HugoSession, TutorPrompt
from apps.hugo.services.decision_engine import decide_conversation
from apps.hugo.services.hugo_orchestrator import build_hugo_turn
from apps.hugo.services.turn_state_analyzer import analyze_turn_state


def _session_stub(message_count: int = 0, current_phase: str = "exploration"):
    class _MessagesManager(list):
        def count(self):
            return len(self)

        def filter(self, **kwargs):
            role = kwargs.get("role")
            if role is None:
                return self
            return _MessagesManager([message for message in self if getattr(message, "role", None) == role])

        def order_by(self, *_args, **_kwargs):
            return self

    return SimpleNamespace(
        current_phase=current_phase,
        messages=_MessagesManager([SimpleNamespace(role="ASSISTANT") for _ in range(message_count)]),
    )


def _ctx_stub(summary: str | None = None, traces: list[str] | None = None, docs: list[str] | None = None):
    return SimpleNamespace(
        learner_summary=summary,
        recent_traces_info=traces or [],
        class_documents=docs or [],
    )


def _state(**overrides):
    base = TurnState(
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
        setattr(base, key, value)
    return base


class TurnStateAnalyzerTests(SimpleTestCase):
    def test_episode_clarity_low_is_detected(self):
        state = analyze_turn_state(
            session=_session_stub(),
            user_input={"content": "Je ne sais pas trop, c'etait vague."},
            ctx=_ctx_stub(),
        )
        self.assertEqual(state.episode_clarity, "low")
        self.assertFalse(state.has_concrete_actions)

    def test_cognitive_load_high_is_detected(self):
        state = analyze_turn_state(
            session=_session_stub(),
            user_input={"content": "Je suis perdu, il y en a trop et c'est trop complique."},
            ctx=_ctx_stub(),
        )
        self.assertEqual(state.cognitive_load, "high")

    def test_interaction_risk_high_is_detected(self):
        state = analyze_turn_state(
            session=_session_stub(),
            user_input={"content": "J'en ai marre, ca m'enerve et laisse tomber."},
            ctx=_ctx_stub(),
        )
        self.assertEqual(state.interaction_risk, "high")

    def test_missing_actions_with_clear_context_prioritizes_action(self):
        state = analyze_turn_state(
            session=_session_stub(),
            user_input={
                "content": "Sur le chantier avec le client, le contexte etait clair, puis ensuite la procedure generale a ete rappelee."
            },
            ctx=_ctx_stub(),
        )
        self.assertEqual(state.episode_clarity, "medium")
        self.assertFalse(state.has_concrete_actions)

    def test_sticky_actions_and_previous_clarify_are_recovered_from_history(self):
        previous_payload = {
            "turn_state": {"has_concrete_actions": True},
            "conversation_decision": {"pedagogical_move": "clarify"},
        }
        session = _session_stub()
        session.messages.append(
            SimpleNamespace(role="LEARNER", llm_request_payload=previous_payload)
        )

        state = analyze_turn_state(
            session=session,
            user_input={"content": "Sur le chantier avec le client, puis ensuite j'ai observe la panne."},
            ctx=_ctx_stub(),
        )

        self.assertTrue(state.has_concrete_actions)
        self.assertEqual(state.last_tutorial_move, "clarify")
        self.assertEqual(state.consecutive_clarify_turns, 1)

    def test_help_repetition_and_closure_signals_are_detected(self):
        state = analyze_turn_state(
            session=_session_stub(),
            user_input={"content": "Je sais pas, aide moi, on tourne en rond et j'ai fini."},
            ctx=_ctx_stub(),
        )
        self.assertEqual(state.learner_help_request, "explicit")
        self.assertEqual(state.repetition_signal, "explicit")
        self.assertEqual(state.closure_signal, "explicit")
        self.assertEqual(state.loop_risk, "high")

    def test_covered_points_and_remaining_open_points_follow_thread_coverage(self):
        state = analyze_turn_state(
            session=_session_stub(),
            user_input={
                "content": (
                    "J'ai remplace le bouton, puis j'ai vu que le probleme venait d'un fil desserre. "
                    "La prochaine fois je verifierai le serrage avant remise en service."
                )
            },
            ctx=_ctx_stub(),
        )
        self.assertIn("episode_described", state.covered_points)
        self.assertIn("concrete_actions_described", state.covered_points)
        self.assertIn("cause_confirmed", state.covered_points)
        self.assertIn("future_action_named", state.covered_points)
        self.assertNotIn("missing_episode_details", state.remaining_open_points)


class DecisionEngineTests(SimpleTestCase):
    def test_high_cognitive_load_forces_single_question(self):
        decision = decide_conversation(_state(cognitive_load="high"))
        self.assertEqual(decision.number_of_questions, 1)
        self.assertEqual(decision.question_style, "single_safe")
        self.assertFalse(decision.should_explain_briefly)

    def test_high_interaction_risk_forces_single_question(self):
        decision = decide_conversation(_state(interaction_risk="high"))
        self.assertEqual(decision.number_of_questions, 1)
        self.assertEqual(decision.question_style, "single_safe")

    def test_micro_explanation_allowed_only_when_conditions_match(self):
        decision = decide_conversation(_state(reflective_depth="medium", zpd_estimate="in"))
        self.assertTrue(decision.should_explain_briefly)

    def test_micro_explanation_blocked_when_zpd_beyond(self):
        decision = decide_conversation(_state(zpd_estimate="beyond"))
        self.assertFalse(decision.should_explain_briefly)

    def test_two_questions_max_only_for_same_micro_goal(self):
        decision = decide_conversation(_state())
        self.assertEqual(decision.number_of_questions, 2)

    def test_explicit_help_request_prefers_assist(self):
        decision = decide_conversation(
            _state(
                learner_help_request="explicit",
                problem_salience="none",
                reflection_phase="description",
            )
        )
        self.assertEqual(decision.pedagogical_move, "assist")
        self.assertEqual(decision.number_of_questions, 1)
        self.assertTrue(decision.should_explain_briefly)

    def test_explicit_closure_uses_zero_question_close(self):
        decision = decide_conversation(
            _state(
                closure_signal="explicit",
                safety_or_quality_risk_level="low",
                can_close_for_now=True,
            )
        )
        self.assertEqual(decision.pedagogical_move, "close")
        self.assertEqual(decision.number_of_questions, 0)
        self.assertTrue(decision.should_close)
        self.assertIn("no_question_final", decision.response_constraints)

    def test_explicit_repetition_does_not_reopen_problem(self):
        decision = decide_conversation(
            _state(
                repetition_signal="explicit",
                loop_risk="high",
                problem_salience="none",
                reflection_phase="description",
            )
        )
        self.assertIn(decision.pedagogical_move, {"repair", "close"})
        self.assertNotEqual(decision.pedagogical_move, "problematize")
        self.assertEqual(decision.number_of_questions, 0)

    def test_problematize_can_use_two_questions_when_episode_is_usable(self):
        decision = decide_conversation(
            _state(
                problem_salience="none",
                reflection_phase="description",
                episode_clarity="medium",
                has_concrete_actions=True,
            )
        )
        self.assertEqual(decision.primary_intent, "surface_problem")
        self.assertEqual(decision.pedagogical_move, "problematize")
        self.assertEqual(decision.number_of_questions, 2)
        self.assertEqual(decision.question_style, "double_same_goal")
        self.assertIn("problematize_double_question_allowed", decision.reason_codes)

    def test_problematize_stays_single_question_under_protection(self):
        decision = decide_conversation(
            _state(
                problem_salience="none",
                reflection_phase="description",
                episode_clarity="medium",
                has_concrete_actions=True,
                cognitive_load="high",
            )
        )
        self.assertEqual(decision.number_of_questions, 1)
        self.assertEqual(decision.question_style, "single_safe")

    def test_problematize_is_blocked_when_thread_is_already_covered(self):
        decision = decide_conversation(
            _state(
                problem_salience="none",
                reflection_phase="description",
                covered_points=[
                    "episode_described",
                    "cause_hypothesis_named",
                    "future_action_named",
                ],
                remaining_open_points=["none"],
            )
        )
        self.assertNotEqual(decision.pedagogical_move, "problematize")

    def test_missing_actions_prioritizes_action_move(self):
        decision = decide_conversation(_state(has_concrete_actions=False, episode_clarity="medium"))
        self.assertEqual(decision.primary_intent, "elicit_concrete_action")
        self.assertEqual(decision.pedagogical_move, "elicit_action")

    def test_anti_loop_blocks_second_clarification_when_actions_are_known(self):
        decision = decide_conversation(
            _state(
                has_concrete_actions=True,
                episode_clarity="high",
                last_tutorial_move="clarify",
                consecutive_clarify_turns=1,
                problem_salience="high",
            )
        )
        self.assertEqual(decision.primary_intent, "exit_clarification_loop")
        self.assertEqual(decision.pedagogical_move, "analyze")
        self.assertIn("do_not_repeat_action_clarification", decision.response_constraints)

    def test_technical_risk_prioritizes_analysis(self):
        decision = decide_conversation(
            _state(
                safety_or_quality_risk_level="high",
                technical_criterion_focus="none",
                tech_representation_level="explicit",
            )
        )
        self.assertEqual(decision.primary_intent, "secure_and_analyze")
        self.assertEqual(decision.pedagogical_move, "analyze")
        self.assertIn("anchor_to_referential_criterion", decision.response_constraints)

    def test_closure_allowed_when_state_is_mature(self):
        decision = decide_conversation(
            _state(
                session_phase="potential_closure",
                current_phase="potential_closure",
                session_maturity="high",
                evidence_strength="high",
                can_close_for_now=True,
            )
        )
        self.assertTrue(decision.should_close)

    def test_closure_blocked_when_state_not_ready(self):
        decision = decide_conversation(
            _state(
                session_phase="potential_closure",
                current_phase="potential_closure",
                session_maturity="medium",
                evidence_strength="medium",
                can_close_for_now=False,
            )
        )
        self.assertFalse(decision.should_close)


@pytest.mark.django_db
def test_build_hugo_turn_exposes_turn_state_and_decision(django_user_model, organisation, group):
    learner = django_user_model.objects.create(username="learner_turn_state", organisation=organisation)
    tutor_prompt = TutorPrompt.objects.create(
        organisation=organisation,
        code="afest_p0",
        name="AFEST P0",
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
        {"content": "J'ai choisi ce controle parce que la panne etait critique sur le chantier."},
    )

    assert turn.turn_state is not None
    assert turn.conversation_decision is not None
    assert "Décision tutorale locale" in turn.system_prompt


@pytest.mark.django_db
@patch("apps.hugo.views_sessions.complete_with_provider")
def test_message_pipeline_persists_turn_state_and_decision(
    complete_mock, api_client, django_user_model, organisation, group
):
    learner = django_user_model.objects.create_user(
        username="learner_pipeline",
        password="pass",
        organisation=organisation,
    )
    tutor_prompt = TutorPrompt.objects.create(
        organisation=organisation,
        code="afest_pipeline",
        name="AFEST pipeline",
        prompt_type=TutorPrompt.PromptType.AFEST_HUGO,
        is_default=True,
        system_template="{base_system_intro}\n{response_constraints_block}",
        user_template="{situation_content}",
        max_questions_per_turn=2,
    )
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner,
        group=group,
        tutor_prompt=tutor_prompt,
        phase_classifier_enabled=False,
    )
    complete_mock.return_value = (
        "1. Qu'as-tu fait en premier ?\n2. Pourquoi ce choix ?",
        {"provider": "ollama", "model_used": "mistral", "request_payload": {"mock": True}},
    )

    api_client.force_authenticate(user=learner)
    url = reverse("message_list_create", kwargs={"session_id": str(session.id)})
    response = api_client.post(
        url,
        {"content": "J'ai verifie le tableau puis j'ai choisi ce controle parce que le risque etait eleve."},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["conversation_decision"]["number_of_questions"] in {1, 2}

    learner_msg = HugoMessage.objects.filter(session=session, role=HugoMessage.Role.LEARNER).latest("created_at")
    assistant_msg = HugoMessage.objects.filter(session=session, role=HugoMessage.Role.ASSISTANT).latest("created_at")

    assert "turn_state" in learner_msg.llm_request_payload
    assert "conversation_decision" in learner_msg.llm_request_payload
    assert assistant_msg.llm_response_payload["provider"] == "ollama"
    assert assistant_msg.assistant_display_variants["short"] == assistant_msg.content
    assert assistant_msg.assistant_display_variants["default_variant"] == "short"


@pytest.mark.django_db
@patch("apps.hugo.views_sessions.complete_with_provider")
def test_message_pipeline_closure_and_meta_leak_end_with_safe_no_question_reply(
    complete_mock, api_client, django_user_model, organisation, group
):
    learner = django_user_model.objects.create_user(
        username="learner_closure_safe",
        password="pass",
        organisation=organisation,
    )
    tutor_prompt = TutorPrompt.objects.create(
        organisation=organisation,
        code="afest_closure_safe",
        name="AFEST closure safe",
        prompt_type=TutorPrompt.PromptType.AFEST_HUGO,
        is_default=True,
        system_template="{base_system_intro}",
        user_template="{situation_content}",
        output_format_mode=TutorPrompt.OutputFormatMode.REFLECTION_BLOCK,
        max_questions_per_turn=2,
    )
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner,
        group=group,
        tutor_prompt=tutor_prompt,
        phase_classifier_enabled=False,
    )
    complete_mock.return_value = (
        "Je vois que vous me demandez de rebondir sur le dernier message de l'apprenant.",
        {"provider": "ollama", "model_used": "mistral", "request_payload": {"mock": True}},
    )
    api_client.force_authenticate(user=learner)
    url = reverse("message_list_create", kwargs={"session_id": str(session.id)})
    response = api_client.post(url, {"content": "Non, j'ai fini."}, format="json")

    assert response.status_code == 200
    assert response.data["content"] == "D'accord, on peut s'arrêter ici."
    assert response.data["conversation_decision"]["number_of_questions"] == 0
