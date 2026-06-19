"""Cluster 3 — oracles prioritaires (validation courte personae A1/B1/D1)."""
import io
import json
import zipfile

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role
from apps.hugo.domain.schemas import P0_CORE_FIELDS, P0_LLM_FIELDS
from apps.hugo.models import HugoMessage, HugoSession, Trace
from apps.referentials.models import Group, GroupMembership, TutorLearnerLink


P0_FORBIDDEN_IN_UI = set(P0_CORE_FIELDS) | set(P0_LLM_FIELDS) | {
    "turn_state",
    "conversation_decision",
    "episode_clarity",
    "cognitive_load",
    "interaction_risk",
}


@pytest.mark.django_db
def test_inv01_ui_state_response_has_no_p0_fields(api_client, learner_user, organisation, group):
    """INV-01 — contrat GET /ui-state/ sans champs P0."""
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
            "missing_for_next_level": [],
            "reason_codes": [],
        },
    )
    session.conversation_progress["session_id"] = str(session.id)
    session.save(update_fields=["conversation_progress"])

    api_client.force_authenticate(user=learner_user)
    response = api_client.get(f"/hugo/sessions/{session.id}/ui-state/")

    assert response.status_code == 200
    payload_keys = set(response.data.keys())
    assert payload_keys.isdisjoint(P0_FORBIDDEN_IN_UI)
    serialized = json.dumps(response.data, ensure_ascii=False).lower()
    for token in ("turn_state", "episode_clarity", "cognitive_load", "interaction_risk"):
        assert token not in serialized


@pytest.mark.django_db
def test_a1_04_cta_evaluation_eligible_when_progress_green(api_client, learner_user, organisation, group):
    """A1-04 — CTA évaluation alignée sur maturité GREEN + evaluation_eligible."""
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        conversation_progress={
            "session_id": "pending",
            "posture": "reflective_afest",
            "active_branches": [
                {
                    "branch_id": "b1",
                    "theme_label": "Situation",
                    "objective_label": "clôture",
                    "exploration_level": "green",
                    "is_active": True,
                    "reason_codes": [],
                }
            ],
            "active_branches_count": 1,
            "overall_maturity": "green",
            "synthesis_eligible": True,
            "evaluation_eligible": True,
            "missing_for_next_level": [],
            "reason_codes": ["evaluation_eligible"],
        },
    )
    session.conversation_progress["session_id"] = str(session.id)
    session.save(update_fields=["conversation_progress"])

    api_client.force_authenticate(user=learner_user)
    response = api_client.get(f"/hugo/sessions/{session.id}/ui-state/")
    cta = response.data["cta_evaluation"]

    assert response.status_code == 200
    assert cta["evaluation_ready_status"] == "eligible"
    assert cta["ui"]["button_disabled"] is False
    assert "Demander une évaluation" in cta["ui"]["button_label"]


@pytest.mark.django_db
def test_b1_01_timeline_hides_messages_when_share_verbatim_false(db):
    """B1-01 — tuteur lié ne voit pas les messages si share_verbatim=false."""
    client = APIClient()
    org = Organisation.objects.create(name="Org B1")
    user_model = get_user_model()
    tutor = user_model.objects.create_user(
        username="tutor_b1",
        password="pass",
        organisation=org,
        role=Role.TUTOR,
    )
    learner = user_model.objects.create_user(
        username="learner_b1",
        password="pass",
        organisation=org,
        role=Role.LEARNER,
    )
    group = Group.objects.create(organisation=org, name="G B1")
    for user in (tutor, learner):
        GroupMembership.objects.create(organisation=org, group=group, user=user)
    TutorLearnerLink.objects.create(
        organisation=org, group=group, tutor=tutor, learner=learner
    )
    session = HugoSession.objects.create(
        organisation=org,
        group=group,
        learner=learner,
        share_verbatim=False,
    )
    HugoMessage.objects.create(
        organisation=org,
        session=session,
        role=HugoMessage.Role.LEARNER,
        content="SECRET_VERBATIM_B1_ORACLE",
    )

    client.force_authenticate(user=tutor)
    response = client.get(f"/dashboard/groups/{group.id}/learners/{learner.id}/timeline/")

    assert response.status_code == 200
    session_payload = response.data["sessions"][0]
    assert session_payload["share_verbatim"] is False
    assert session_payload["messages"] == []
    assert session_payload["first_learner_message"] == ""
    assert "SECRET_VERBATIM_B1_ORACLE" not in json.dumps(response.data)


@pytest.mark.django_db
def test_g3_01_learner_cannot_access_other_org_session(api_client, db):
    """G3-01 — isolation tenant sur GET /ui-state/ (session autre org)."""
    user_model = get_user_model()
    org_a = Organisation.objects.create(name="Org A G3")
    org_b = Organisation.objects.create(name="Org B G3")
    learner_a = user_model.objects.create_user(
        username="learner_a_g3",
        password="pass",
        organisation=org_a,
        role=Role.LEARNER,
    )
    learner_b = user_model.objects.create_user(
        username="learner_b_g3",
        password="pass",
        organisation=org_b,
        role=Role.LEARNER,
    )
    group_b = Group.objects.create(organisation=org_b, name="G B")
    session_b = HugoSession.objects.create(
        organisation=org_b,
        learner=learner_b,
        group=group_b,
    )

    api_client.force_authenticate(user=learner_a)
    response = api_client.get(f"/hugo/sessions/{session_b.id}/ui-state/")

    assert response.status_code == 404


@pytest.mark.django_db
def test_d1_02_evidence_bundle_scoped_to_organisation(db):
    """D1-02 — bundle Qualiopi ne contient que les traces de l'organisation appelante."""
    client = APIClient()
    user_model = get_user_model()
    org_a = Organisation.objects.create(name="Org A D1")
    org_b = Organisation.objects.create(name="Org B D1")
    admin_a = user_model.objects.create_user(
        username="admin_a_d1",
        password="pass",
        organisation=org_a,
        role=Role.ORGADMIN,
    )
    learner_a = user_model.objects.create_user(
        username="learner_a_d1",
        password="pass",
        organisation=org_a,
        role=Role.LEARNER,
    )
    learner_b = user_model.objects.create_user(
        username="learner_b_d1",
        password="pass",
        organisation=org_b,
        role=Role.LEARNER,
    )
    group_a = Group.objects.create(organisation=org_a, name="GA")
    group_b = Group.objects.create(organisation=org_b, name="GB")
    session_a = HugoSession.objects.create(organisation=org_a, learner=learner_a, group=group_a)
    session_b = HugoSession.objects.create(organisation=org_b, learner=learner_b, group=group_b)
    trace_a = Trace.objects.create(organisation=org_a, session=session_a, payload_structured={})
    trace_b = Trace.objects.create(organisation=org_b, session=session_b, payload_structured={})

    client.force_authenticate(user=admin_a)
    response = client.post("/quality/qualiopi/evidence-bundle/", {}, format="json")

    assert response.status_code == 200
    zf = zipfile.ZipFile(io.BytesIO(response.content))
    traces = json.loads(zf.read("traces.json"))
    trace_ids = {row["trace_id"] for row in traces}
    assert str(trace_a.id) in trace_ids
    assert str(trace_b.id) not in trace_ids
