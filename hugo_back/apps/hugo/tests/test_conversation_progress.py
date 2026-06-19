from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.test import SimpleTestCase

from apps.hugo.domain.conversation_profile import ConversationPosture, SessionMaturityLevel
from apps.hugo.models import HugoMessage, HugoSession
from apps.hugo.services.conversation_progress_calculator import (
    ConversationProgressCalculator,
    build_conversation_progress_contract,
)
from apps.hugo.services.synthesis_service import generate_synthesis


class ConversationProgressCalculatorTests(SimpleTestCase):
    def test_reflective_progress_reaches_green_when_transfer_is_present(self):
        turn_state = SimpleNamespace(
            conversation_goal="Pose d'une prise",
            current_phase="exploration",
            covered_points=[
                "problem_named",
                "cause_hypothesis_named",
                "future_action_named",
                "learning_rule_named",
            ],
            remaining_open_points=[],
            episode_clarity="high",
            has_concrete_actions=True,
            loop_risk="low",
            cognitive_load="low",
            interaction_risk="low",
        )
        decision = SimpleNamespace()
        progress = build_conversation_progress_contract(
            session_id="session-1",
            turn_state=turn_state,
            decision=decision,
            posture=ConversationPosture.REFLECTIVE_AFEST,
        )
        self.assertEqual(progress.overall_maturity, SessionMaturityLevel.GREEN)
        self.assertTrue(progress.synthesis_eligible)
        self.assertTrue(progress.evaluation_eligible)

    def test_knowledge_review_clamps_to_one_active_branch(self):
        calculator = ConversationProgressCalculator(posture=ConversationPosture.KNOWLEDGE_REVIEW)
        previous = build_conversation_progress_contract(
            session_id="session-1",
            turn_state=SimpleNamespace(
                conversation_goal="Réviser Ohm",
                current_phase="exploration",
                covered_points=[],
                remaining_open_points=["Définir la formule"],
                episode_clarity="medium",
                has_concrete_actions=False,
                loop_risk="low",
                cognitive_load="low",
                interaction_risk="low",
            ),
            decision=SimpleNamespace(),
            posture=ConversationPosture.KNOWLEDGE_REVIEW,
        )
        updated = calculator.update(
            session_id="session-1",
            turn_state=SimpleNamespace(
                conversation_goal="Réviser Kirchhoff",
                current_phase="exploration",
                covered_points=[],
                remaining_open_points=["Comparer les lois"],
                episode_clarity="medium",
                has_concrete_actions=False,
                loop_risk="low",
                cognitive_load="low",
                interaction_risk="low",
            ),
            decision=SimpleNamespace(),
            previous_progress=previous,
        )
        self.assertEqual(updated.active_branches_count, 1)


@pytest.mark.django_db
def test_progress_and_ui_state_endpoints_return_contract(api_client, learner_user, organisation, group):
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        posture="diagnostic",
        conversation_progress={
            "session_id": "s1",
            "posture": "diagnostic",
            "active_branches": [
                {
                    "branch_id": "branch-1",
                    "theme_label": "Incident tableau",
                    "objective_label": "exploration",
                    "exploration_level": "orange",
                    "is_active": True,
                    "reason_codes": ["no_concrete_actions"],
                }
            ],
            "active_branches_count": 1,
            "overall_maturity": "orange",
            "synthesis_eligible": True,
            "evaluation_eligible": False,
            "missing_for_next_level": ["Nommer l'action suivante."],
            "reason_codes": ["synthesis_eligible"],
        },
    )
    api_client.force_authenticate(user=learner_user)

    progress_response = api_client.get(f"/hugo/sessions/{session.id}/progress/")
    ui_state_response = api_client.get(f"/hugo/sessions/{session.id}/ui-state/?gamification_profile=C")

    assert progress_response.status_code == 200
    assert progress_response.data["posture"] == "diagnostic"
    assert progress_response.data["overall_maturity"] == "orange"
    assert ui_state_response.status_code == 200
    assert ui_state_response.data["scene_label"] == "Explorer"
    assert ui_state_response.data["gamification_profile"] == "C"


@pytest.mark.django_db
def test_synthesis_and_evaluation_endpoints_return_generated_payloads(api_client, learner_user, organisation, group):
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        posture="diagnostic",
        conversation_progress={
            "session_id": "s2",
            "posture": "diagnostic",
            "active_branches": [
                {
                    "branch_id": "branch-1",
                    "theme_label": "Incident tableau",
                    "objective_label": "exploration",
                    "exploration_level": "green",
                    "is_active": True,
                    "reason_codes": ["ready_for_synthesis"],
                }
            ],
            "active_branches_count": 1,
            "overall_maturity": "green",
            "synthesis_eligible": True,
            "evaluation_eligible": True,
            "missing_for_next_level": [],
            "reason_codes": ["ready_for_synthesis", "ready_for_evaluation"],
        },
    )
    HugoMessage.objects.create(
        organisation=organisation,
        session=session,
        role=HugoMessage.Role.LEARNER,
        content="J'ai maintenant une vision claire de ce qui s'est passé.",
    )
    api_client.force_authenticate(user=learner_user)

    synthesis_response = api_client.post(
        f"/hugo/sessions/{session.id}/request-synthesis/",
        {"gamification_profile": "A"},
        format="json",
    )
    evaluation_response = api_client.post(
        f"/hugo/sessions/{session.id}/request-evaluation/",
        {"gamification_profile": "A"},
        format="json",
    )

    assert synthesis_response.status_code == 200
    assert synthesis_response.data["status"] == "synthesis_ready"
    assert "Synthèse de la scène" == synthesis_response.data["synthesis"]["title"]
    assert synthesis_response.data["ui_state"]["gamification_profile"] == "A"

    assert evaluation_response.status_code == 200
    assert evaluation_response.data["status"] == "evaluation_ready"
    assert evaluation_response.data["evaluation"]["competence_items"][0]["label"] == "Incident tableau"
    assert evaluation_response.data["ui_state"]["scene_label"] == "Synthétiser"


@pytest.mark.django_db
def test_synthesis_endpoint_rejects_when_progress_not_eligible(api_client, learner_user, organisation, group):
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        posture="diagnostic",
        conversation_progress={
            "session_id": "s3",
            "posture": "diagnostic",
            "active_branches": [],
            "active_branches_count": 0,
            "overall_maturity": "red",
            "synthesis_eligible": False,
            "evaluation_eligible": False,
            "missing_for_next_level": ["Décrire la situation"],
            "reason_codes": ["needs_more_context"],
        },
    )
    api_client.force_authenticate(user=learner_user)

    response = api_client.post(f"/hugo/sessions/{session.id}/request-synthesis/", {}, format="json")

    assert response.status_code == 400
    assert response.data["error"] == "synthesis_not_eligible"
    assert response.data["reason_codes"] == ["needs_more_context"]


@pytest.mark.django_db
@patch("apps.hugo.services.synthesis_service.complete_with_provider")
def test_generate_synthesis_prefers_llm_output_when_available(complete_mock, organisation, learner_user, group):
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        posture="reflective_afest",
    )
    HugoMessage.objects.create(
        organisation=organisation,
        session=session,
        role=HugoMessage.Role.LEARNER,
        content="J'ai identifié la cause probable et la prochaine vérification à faire.",
    )
    progress = build_conversation_progress_contract(
        session_id=str(session.id),
        turn_state=SimpleNamespace(
            conversation_goal="Incident tableau",
            current_phase="exploration",
            covered_points=["problem_named", "cause_hypothesis_named", "future_action_named"],
            remaining_open_points=[],
            episode_clarity="high",
            has_concrete_actions=True,
            loop_risk="low",
            cognitive_load="low",
            interaction_risk="low",
        ),
        decision=SimpleNamespace(),
        posture=ConversationPosture.REFLECTIVE_AFEST,
    )
    complete_mock.return_value = (
        "Tu as clarifié l'incident et identifié une prochaine vérification concrète.",
        {"provider": "ollama", "model_used": "mistral"},
    )

    synthesis = generate_synthesis(session, progress)

    assert synthesis["source"] == "llm"
    assert synthesis["text"] == "Tu as clarifié l'incident et identifié une prochaine vérification concrète."
    assert synthesis["llm_meta"]["model_used"] == "mistral"


@pytest.mark.django_db
@patch("apps.hugo.services.synthesis_service.complete_with_provider")
def test_generate_synthesis_falls_back_when_llm_returns_empty(complete_mock, organisation, learner_user, group):
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        posture="diagnostic",
    )
    progress = build_conversation_progress_contract(
        session_id=str(session.id),
        turn_state=SimpleNamespace(
            conversation_goal="Diagnostic moteur",
            current_phase="exploration",
            covered_points=["problem_named"],
            remaining_open_points=["Confirmer la cause"],
            episode_clarity="medium",
            has_concrete_actions=True,
            loop_risk="low",
            cognitive_load="low",
            interaction_risk="low",
        ),
        decision=SimpleNamespace(),
        posture=ConversationPosture.DIAGNOSTIC,
    )
    complete_mock.return_value = ("", {"provider": "ollama", "error": "timeout"})

    synthesis = generate_synthesis(session, progress)

    assert synthesis["source"] == "fallback"
    assert "mini-bilan" in synthesis["text"]
    assert synthesis["llm_meta"]["error"] == "timeout"
