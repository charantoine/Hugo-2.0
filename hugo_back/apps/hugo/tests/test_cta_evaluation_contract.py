import json
import re

import pytest

from apps.hugo.models import EvaluationPolicy, HugoSession


EVALUATION_READY_STATUSES = {
    "eligible",
    "blocked_missing_data",
    "blocked_min_turns_not_reached",
    "blocked_context_incomplete",
    "blocked_other",
}

P0_PATTERN = re.compile(
    r"episode_clarity|cognitive_load|interaction_risk|problem_salience|reflection_phase|turn_state|\bp0\b",
    re.IGNORECASE,
)


@pytest.mark.django_db
def test_ui_state_exposes_cta_evaluation_contract(api_client, learner_user, organisation, group):
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        conversation_progress={
            "session_id": str("placeholder"),
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
            "missing_for_next_level": ["Nommer une action concrète déjà réalisée."],
            "reason_codes": ["evaluation_blocked_maturity"],
        },
    )
    session.conversation_progress["session_id"] = str(session.id)
    session.save(update_fields=["conversation_progress"])

    api_client.force_authenticate(user=learner_user)
    response = api_client.get(f"/hugo/sessions/{session.id}/ui-state/")

    assert response.status_code == 200
    cta = response.data["cta_evaluation"]
    assert cta["evaluation_ready_status"] in EVALUATION_READY_STATUSES
    assert isinstance(cta["blocking_reasons"], list)
    assert cta["ui"]["show_evaluation_button"] is True
    assert "request_evaluation" in cta["endpoints"]
    assert cta["last_evaluation"]["status"] in {"none", "in_progress", "completed", "failed"}
    serialized = json.dumps(cta, ensure_ascii=False)
    assert not P0_PATTERN.search(serialized)
    for reason in cta["blocking_reasons"]:
        assert isinstance(reason, str)
        assert not P0_PATTERN.search(reason)
