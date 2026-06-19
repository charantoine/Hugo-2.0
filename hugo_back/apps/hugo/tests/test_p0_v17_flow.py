from types import SimpleNamespace

import pytest
from django.test import SimpleTestCase, override_settings

from apps.hugo.domain.schemas import TurnState
from apps.hugo.models import HugoSession, TutorPrompt
from apps.hugo.services.decision_engine_v17 import decide_conversation_v17, is_redundant_question_candidate
from apps.hugo.services.learner_speech_act_classifier import classify_learner_speech_act
from apps.hugo.services.output_guardrails_v17 import apply_output_guardrails_v17
from apps.hugo.services.prompt_renderer_v17 import TutorPromptProfile
from apps.hugo.services.state_reconciler_v17 import reconcile_turn_state_v17


def _legacy_state(**overrides):
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
        action_feasibility="medium",
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


class P0V17UnitTests(SimpleTestCase):
    def test_speech_act_classifier_detects_report_for_tutor(self):
        result = classify_learner_speech_act("Peux-tu me faire un texte pour le formateur ?")
        self.assertEqual(result.learner_speech_act, "ask_report_for_tutor")
        self.assertEqual(result.last_learner_act, "ask_report_for_tutor")
        self.assertEqual(result.requested_output, "report_for_tutor")

    def test_reconcile_turn_state_v17_aligns_help_request_with_speech_act(self):
        state = reconcile_turn_state_v17(
            legacy_state=_legacy_state(learner_help_request="none"),
            speech_act_result=classify_learner_speech_act("Tu peux m'aider à comprendre ?"),
            p0_classifier={"source": "heuristic", "source_by_field": {}},
            recent_history=[],
        )
        self.assertEqual(state.learner_help_request, "explicit")
        self.assertTrue(state.needs_diagnostic_help)

    def test_decide_conversation_v17_prioritizes_explicit_help(self):
        state = reconcile_turn_state_v17(
            legacy_state=_legacy_state(reflection_phase="analysis", covered_points=["episode_described", "cause_hypothesis_named"]),
            speech_act_result=classify_learner_speech_act("Tu peux m'aider, je ne sais pas par quoi commencer ?"),
            p0_classifier={"source": "heuristic", "source_by_field": {}},
            recent_history=[],
        )
        decision = decide_conversation_v17(state)
        self.assertEqual(decision.response_mode, "assist")
        self.assertEqual(decision.primary_intent, "diagnostic_help")
        self.assertLessEqual(decision.number_of_questions, 1)
        self.assertEqual(decision.metadata.get("conversation_profile"), "reflective_afest")

    def test_decide_conversation_v17_honors_diagnostic_profile(self):
        state = reconcile_turn_state_v17(
            legacy_state=_legacy_state(episode_clarity="low", has_concrete_actions=False, reflection_phase="description"),
            speech_act_result=classify_learner_speech_act("Je suis perdu, je ne comprends pas ce qui bloque."),
            p0_classifier={"source": "heuristic", "source_by_field": {}},
            recent_history=[],
        )
        decision = decide_conversation_v17(state, conversation_profile="diagnostic")
        self.assertEqual(decision.metadata.get("conversation_profile"), "diagnostic")
        self.assertIn(decision.pedagogical_move, {"assist", "clarify"})

    def test_decide_conversation_v17_honors_knowledge_review_profile(self):
        state = reconcile_turn_state_v17(
            legacy_state=_legacy_state(available_material="high", learner_help_request="explicit"),
            speech_act_result=classify_learner_speech_act("Tu peux me rappeler la méthode à suivre ?"),
            p0_classifier={"source": "heuristic", "source_by_field": {}},
            recent_history=[],
        )
        decision = decide_conversation_v17(state, conversation_profile="knowledge_review")
        self.assertEqual(decision.metadata.get("conversation_profile"), "knowledge_review")
        self.assertEqual(decision.response_mode, "assist")

    def test_is_redundant_question_candidate_blocks_covered_topic(self):
        redundant = is_redundant_question_candidate(
            "Peux-tu redécrire l'episode_described ?",
            covered_points=["episode_described"],
            remaining_open_points=["missing_future_action"],
            last_tutorial_move="clarify",
        )
        self.assertTrue(redundant)

    def test_output_guardrails_v17_closure_returns_non_question_text(self):
        state = reconcile_turn_state_v17(
            legacy_state=_legacy_state(closure_signal="explicit", can_close_for_now=True),
            speech_act_result=classify_learner_speech_act("C'est bon, on a fini."),
            p0_classifier={"source": "heuristic", "source_by_field": {}},
            recent_history=[],
        )
        decision = decide_conversation_v17(state)
        profile = TutorPromptProfile(
            session=SimpleNamespace(),
            tutor_prompt=None,
            teaching_plan=None,
            competence_brief=None,
            learner_message="C'est bon, on a fini.",
            context=None,
            rag_chunks=[],
        )
        reply = apply_output_guardrails_v17("1. Veux-tu continuer ?\n2. Que retiens-tu ?", decision, profile)
        self.assertNotIn("?", reply)


@pytest.mark.django_db
@override_settings(HUGO_P0_V17_ENABLED=True)
def test_build_hugo_turn_uses_v17_for_explicit_report_request(django_user_model, organisation, group):
    learner = django_user_model.objects.create(username="learner_v17", organisation=organisation)
    tutor_prompt = TutorPrompt.objects.create(
        organisation=organisation,
        code="afest_v17",
        name="AFEST v17",
        prompt_type=TutorPrompt.PromptType.AFEST_HUGO,
        is_default=True,
        system_template="{base_system_intro}\n{thread_guidance_block}",
        user_template="{situation_content}",
    )
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner,
        group=group,
        tutor_prompt=tutor_prompt,
        phase_classifier_enabled=False,
        p0_classifier_enabled=False,
    )

    from apps.hugo.services.hugo_orchestrator import build_hugo_turn

    turn = build_hugo_turn(
        session,
        {"content": "Peux-tu me faire un texte pour le tuteur sur ce que j'ai appris ?"},
    )

    assert turn.conversation_decision is not None
    assert turn.conversation_decision.number_of_questions == 0
    assert turn.conversation_decision.metadata.get("contract_version") == "1.7"
    assert turn.conversation_decision.metadata.get("response_mode") == "recap"
    assert turn.conversation_decision.metadata.get("audience") == "tutor"
    assert "Directives P0 1.7" in turn.system_prompt


@pytest.mark.django_db
@override_settings(HUGO_P0_V17_ENABLED=True)
def test_build_hugo_turn_exposes_ui_state_progress_and_memory(django_user_model, organisation, group):
    learner = django_user_model.objects.create(username="learner_ui_state", organisation=organisation)
    tutor_prompt = TutorPrompt.objects.create(
        organisation=organisation,
        code="knowledge_v17",
        name="Knowledge v17",
        prompt_type=TutorPrompt.PromptType.AFEST_HUGO,
        is_default=True,
        conversation_profile="knowledge_review",
        system_template="{base_system_intro}\n{thread_guidance_block}",
        user_template="{situation_content}",
    )
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner,
        group=group,
        tutor_prompt=tutor_prompt,
        phase_classifier_enabled=False,
        p0_classifier_enabled=False,
    )

    from apps.hugo.services.hugo_orchestrator import build_hugo_turn

    turn = build_hugo_turn(
        session,
        {"content": "Peux-tu me rappeler la checklist utile avant de remettre sous tension ?"},
    )

    assert turn.conversation_profile == "knowledge_review"
    assert turn.conversation_progress is not None
    assert turn.ui_state is not None
    assert turn.session_memory is not None
    assert turn.ui_state.supporting_documents == []
    assert turn.ui_state.tutor_signals["conversation_profile"] == "knowledge_review"
    assert turn.session_memory.memory_scope == "governed_structured"
