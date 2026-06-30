from types import SimpleNamespace

import pytest
from django.test import SimpleTestCase

from apps.hugo.domain.conversation_profile import ConversationPosture, SessionMaturityLevel
from apps.hugo.domain.posture_transitions import can_transition
from apps.hugo.models import HugoSession, TutorConductProfile
from apps.hugo.services.posture_selector import resolve_posture
from apps.hugo.services.conduct_profile_resolver import resolve_conduct_profile
from apps.hugo.services.prompt_renderer import render_with_tutor_prompt
from apps.hugo.services.context_builder import HugoContext


class PostureSelectorTests(SimpleTestCase):
    def test_resolve_posture_prefers_explicit_override(self):
        session = SimpleNamespace(posture="", conversation_profile_override="")
        posture = resolve_posture(session, user_message="Je veux réviser", explicit_posture="diagnostic")
        self.assertEqual(posture, ConversationPosture.DIAGNOSTIC)

    def test_transition_warns_when_switching_from_red_knowledge_to_reflective(self):
        allowed, warning = can_transition(
            ConversationPosture.KNOWLEDGE_REVIEW,
            ConversationPosture.REFLECTIVE_AFEST,
            SessionMaturityLevel.RED,
        )
        self.assertTrue(allowed)
        self.assertIn("suffisamment exploré", warning)

    def test_prompt_renderer_injects_posture_block(self):
        tutor_prompt = SimpleNamespace(
            system_template="{base_system_intro}",
            user_template="{situation_content}",
        )
        session = SimpleNamespace(organisation_id="org", id="session")
        ctx = HugoContext(
            referential_name="",
            referential_source_ref="",
            items_to_focus=[],
            items_already_covered=[],
            learner_summary="",
            recent_traces_info=[],
            class_documents=[],
        )
        turn_state = SimpleNamespace(
            current_phase="exploration",
            episode_clarity="medium",
            has_concrete_actions=False,
            cognitive_load="low",
            interaction_risk="low",
            safety_or_quality_risk_level="low",
            technical_criterion_focus="none",
            tech_representation_level="implicit",
            last_tutorial_move="",
            consecutive_clarify_turns=0,
            conversation_goal="Comprendre",
            covered_points=[],
            remaining_open_points=["Nommer l'action"],
            learner_help_request="none",
            closure_signal="none",
            repetition_signal="none",
            loop_risk="low",
            assistant_meta_leak_risk="low",
            posture_constraints={
                "posture": "diagnostic",
                "max_questions_per_turn": 2,
                "forbidden_moves": ["project"],
                "description": "Diagnostic guidé.",
            },
            to_dict=lambda: {},
        )
        decision = SimpleNamespace(
            primary_intent="clarify",
            pedagogical_move="clarify",
            number_of_questions=1,
            question_style="simple_open",
            should_explain_briefly=False,
            should_recap=False,
            should_encourage=False,
            should_reframe=False,
            should_close=False,
            response_constraints=[],
            to_dict=lambda: {},
        )
        rendered = render_with_tutor_prompt(
            tutor_prompt=tutor_prompt,
            session=session,
            ctx=ctx,
            content="Mon disjoncteur saute.",
            turn_state=turn_state,
            conversation_decision=decision,
        )
        self.assertIn("Bloc posture", rendered.system_prompt)
        self.assertIn("diagnostic", rendered.system_prompt)


@pytest.mark.django_db
def test_set_posture_endpoint_updates_session(api_client, learner_user, organisation, group):
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        posture="reflective_afest",
        conversation_progress={
            "session_id": "s1",
            "posture": "reflective_afest",
            "overall_maturity": "orange",
            "active_branches": [],
            "active_branches_count": 0,
        },
    )
    api_client.force_authenticate(user=learner_user)
    response = api_client.post(
        f"/hugo/sessions/{session.id}/set-posture/",
        {"posture": "diagnostic"},
        format="json",
    )
    session.refresh_from_db()
    assert response.status_code == 200
    assert session.posture == "diagnostic"
    assert session.conversation_profile_override == "diagnostic"


@pytest.mark.django_db
def test_conduct_profile_prefers_organisation_override(organisation):
    TutorConductProfile.objects.create(
        organisation=organisation,
        posture="reflective_afest",
        system_template="Custom {posture}",
        max_questions_per_turn=1,
        forbidden_moves=["project"],
    )

    result = resolve_conduct_profile(ConversationPosture.REFLECTIVE_AFEST, organisation)

    assert result["system_template"] == "Custom {posture}"
    assert result["max_questions_per_turn"] == 1
    assert result["forbidden_moves"] == ["project"]


@pytest.mark.django_db
def test_conduct_profile_falls_back_to_static_when_missing(organisation):
    result = resolve_conduct_profile(ConversationPosture.KNOWLEDGE_REVIEW, organisation)

    assert result["posture"] == ConversationPosture.KNOWLEDGE_REVIEW
    assert "max_questions_per_turn" in result
