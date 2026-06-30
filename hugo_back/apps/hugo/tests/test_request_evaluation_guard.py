import pytest

from apps.hugo.models import EvaluationPolicy, HugoSession


@pytest.mark.django_db
def test_request_evaluation_rejects_when_not_eligible_and_early_trigger_disabled(
    api_client,
    learner_user,
    organisation,
    group,
):
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
            "reason_codes": ["evaluation_blocked_maturity"],
        },
    )
    session.conversation_progress["session_id"] = str(session.id)
    session.save(update_fields=["conversation_progress"])

    policy, _ = EvaluationPolicy.objects.get_or_create(
        organisation=organisation,
        group=group,
        defaults={"allow_early_trigger": True},
    )
    policy.allow_early_trigger = False
    policy.save(update_fields=["allow_early_trigger", "updated_at"])

    api_client.force_authenticate(user=learner_user)
    response = api_client.post(f"/hugo/sessions/{session.id}/request-evaluation/", {}, format="json")

    assert response.status_code == 400
    assert response.data["error"] == "evaluation_not_eligible"
    assert isinstance(response.data["blocking_reasons"], list)
    assert len(response.data["blocking_reasons"]) >= 1
    assert "episode_clarity" not in " ".join(response.data["blocking_reasons"]).lower()


@pytest.mark.django_db
def test_request_evaluation_allows_early_trigger_when_policy_enabled(
    api_client,
    learner_user,
    organisation,
    group,
):
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
            "missing_for_next_level": ["Nommer une action concrète."],
            "reason_codes": ["evaluation_blocked_maturity"],
        },
    )
    session.conversation_progress["session_id"] = str(session.id)
    session.save(update_fields=["conversation_progress"])

    policy, _ = EvaluationPolicy.objects.get_or_create(
        organisation=organisation,
        group=group,
        defaults={"allow_early_trigger": True},
    )
    policy.allow_early_trigger = True
    policy.save(update_fields=["allow_early_trigger", "updated_at"])

    api_client.force_authenticate(user=learner_user)
    response = api_client.post(f"/hugo/sessions/{session.id}/request-evaluation/", {}, format="json")

    assert response.status_code == 200
    assert response.data["status"] == "evaluation_ready"
