import pytest

from apps.hugo.models import HugoSession


SYNTHESIS_READY_STATUSES = {
    "eligible",
    "blocked_not_enough_content",
    "blocked_context_incomplete",
}


@pytest.mark.django_db
def test_ui_state_cta_synthesis_matches_progress_eligibility(api_client, learner_user, organisation, group):
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        conversation_progress={
            "session_id": "pending",
            "posture": "reflective_afest",
            "active_branches": [
                {
                    "branch_id": "branch-1",
                    "theme_label": "Incident tableau",
                    "objective_label": "Clarifier la cause",
                    "exploration_level": "orange",
                    "is_active": True,
                    "reason_codes": [],
                }
            ],
            "active_branches_count": 1,
            "overall_maturity": "orange",
            "synthesis_eligible": True,
            "evaluation_eligible": False,
            "missing_for_next_level": [],
            "reason_codes": ["synthesis_eligible"],
        },
    )
    session.conversation_progress["session_id"] = str(session.id)
    session.save(update_fields=["conversation_progress"])

    api_client.force_authenticate(user=learner_user)
    response = api_client.get(f"/hugo/sessions/{session.id}/ui-state/")
    cta = response.data["cta_synthesis"]

    assert cta["synthesis_ready_status"] in SYNTHESIS_READY_STATUSES
    assert cta["synthesis_ready_status"] == "eligible"
    assert cta["ui"]["button_disabled"] is False
    assert cta["endpoints"]["request_synthesis"].endswith("/request-synthesis/")


@pytest.mark.django_db
def test_ui_state_cta_synthesis_blocked_when_not_eligible(api_client, learner_user, organisation, group):
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        conversation_progress={
            "session_id": "pending",
            "posture": "reflective_afest",
            "active_branches": [],
            "active_branches_count": 0,
            "overall_maturity": "red",
            "synthesis_eligible": False,
            "evaluation_eligible": False,
            "missing_for_next_level": ["Décrire la situation vécue."],
            "reason_codes": ["synthesis_blocked_maturity"],
        },
    )
    session.conversation_progress["session_id"] = str(session.id)
    session.save(update_fields=["conversation_progress"])

    api_client.force_authenticate(user=learner_user)
    response = api_client.get(f"/hugo/sessions/{session.id}/ui-state/")
    cta = response.data["cta_synthesis"]

    assert cta["synthesis_ready_status"] == "blocked_not_enough_content"
    assert cta["ui"]["button_disabled"] is True
    assert len(cta["blocking_reasons"]) >= 1
