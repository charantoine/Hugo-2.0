"""D2-M07 — pack pytest confidentialité multi-rôles (oracles B1, D1, G3, F1)."""
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
    "p0_debug",
}

LLM_ANALYSIS_TOKENS = (
    "conversationturnllmanalysis",
    "conversationllmanalysis",
    "llm_analysis",
)


@pytest.mark.django_db
def test_b1_01_timeline_hides_private_verbatim(db):
    """B1-01 — pas de verbatim privé pour TUTOR si share_verbatim=false."""
    client = APIClient()
    org = Organisation.objects.create(name="Org B1 D2M07")
    user_model = get_user_model()
    tutor = user_model.objects.create_user(
        username="tutor_d2m07_b1",
        password="pass",
        organisation=org,
        role=Role.TUTOR,
    )
    learner = user_model.objects.create_user(
        username="learner_d2m07_b1",
        password="pass",
        organisation=org,
        role=Role.LEARNER,
    )
    group = Group.objects.create(organisation=org, name="G B1 D2M07")
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
        content="SECRET_VERBATIM_D2M07_B1",
    )

    client.force_authenticate(user=tutor)
    response = client.get(f"/dashboard/groups/{group.id}/learners/{learner.id}/timeline/")

    assert response.status_code == 200
    session_payload = response.data["sessions"][0]
    assert session_payload["share_verbatim"] is False
    assert session_payload["messages"] == []
    assert session_payload["first_learner_message"] == ""
    assert "SECRET_VERBATIM_D2M07_B1" not in json.dumps(response.data)


@pytest.mark.django_db
def test_b1_02_timeline_exposes_pilotage_not_p0_debug(db):
    """B1-02 — agrégat pilotage sans P0 brut ni p0_debug."""
    client = APIClient()
    org = Organisation.objects.create(name="Org B1-02 D2M07")
    user_model = get_user_model()
    tutor = user_model.objects.create_user(
        username="tutor_d2m07_b102",
        password="pass",
        organisation=org,
        role=Role.TUTOR,
    )
    learner = user_model.objects.create_user(
        username="learner_d2m07_b102",
        password="pass",
        organisation=org,
        role=Role.LEARNER,
    )
    group = Group.objects.create(organisation=org, name="G B1-02")
    for user in (tutor, learner):
        GroupMembership.objects.create(organisation=org, group=group, user=user)
    TutorLearnerLink.objects.create(
        organisation=org, group=group, tutor=tutor, learner=learner
    )
    session = HugoSession.objects.create(
        organisation=org,
        group=group,
        learner=learner,
        share_verbatim=True,
    )
    learner_msg = HugoMessage.objects.create(
        organisation=org,
        session=session,
        role=HugoMessage.Role.LEARNER,
        content="Merci, je clos.",
        llm_request_payload={
            "turn_state": {
                "covered_points": ["cause", "action"],
                "remaining_open_points": [],
                "learner_help_request": "none",
                "closure_signal": "explicit",
                "loop_risk": "low",
            },
            "conversation_decision": {
                "pedagogical_move": "assist",
                "primary_intent": "acknowledge_close",
            },
            "system_prompt": "SECRET_PROMPT_MUST_NOT_APPEAR",
        },
    )

    client.force_authenticate(user=tutor)
    response = client.get(f"/dashboard/groups/{group.id}/learners/{learner.id}/timeline/")

    assert response.status_code == 200
    session_payload = response.data["sessions"][0]
    msg = next(m for m in session_payload["messages"] if m["id"] == str(learner_msg.id))
    assert "pilotage" in msg
    assert "p0_debug" not in msg
    assert "turn_state" not in msg
    assert "system_prompt" not in msg
    pilotage = msg["pilotage"]
    assert pilotage["decision_move"] == "assist"
    assert pilotage["closure_signal"] == "explicit"
    serialized = json.dumps(msg, ensure_ascii=False).lower()
    assert "secret_prompt" not in serialized


@pytest.mark.django_db
def test_d1_02_g3_02_evidence_bundle_scoped_to_caller_organisation(db):
    """D1-02 / G3-02 — traces.json limité à l'organisation appelante."""
    client = APIClient()
    user_model = get_user_model()
    org_a = Organisation.objects.create(name="Org A D2M07")
    org_b = Organisation.objects.create(name="Org B D2M07")
    admin_a = user_model.objects.create_user(
        username="admin_a_d2m07",
        password="pass",
        organisation=org_a,
        role=Role.ORGADMIN,
    )
    learner_a = user_model.objects.create_user(
        username="learner_a_d2m07",
        password="pass",
        organisation=org_a,
        role=Role.LEARNER,
    )
    learner_b = user_model.objects.create_user(
        username="learner_b_d2m07",
        password="pass",
        organisation=org_b,
        role=Role.LEARNER,
    )
    group_a = Group.objects.create(organisation=org_a, name="GA D2M07")
    group_b = Group.objects.create(organisation=org_b, name="GB D2M07")
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


@pytest.mark.django_db
def test_g3_01_learner_cannot_access_other_org_ui_state(db):
    """G3-01 — isolation tenant sur GET /ui-state/."""
    user_model = get_user_model()
    org_a = Organisation.objects.create(name="Org A G3 D2M07")
    org_b = Organisation.objects.create(name="Org B G3 D2M07")
    learner_a = user_model.objects.create_user(
        username="learner_a_g3_d2m07",
        password="pass",
        organisation=org_a,
        role=Role.LEARNER,
    )
    learner_b = user_model.objects.create_user(
        username="learner_b_g3_d2m07",
        password="pass",
        organisation=org_b,
        role=Role.LEARNER,
    )
    group_b = Group.objects.create(organisation=org_b, name="GB G3")
    session_b = HugoSession.objects.create(
        organisation=org_b,
        learner=learner_b,
        group=group_b,
    )

    client = APIClient()
    client.force_authenticate(user=learner_a)
    response = client.get(f"/hugo/sessions/{session_b.id}/ui-state/")

    assert response.status_code == 404


@pytest.mark.django_db
def test_g3_01_orgadmin_cannot_access_other_org_ui_state(db):
    """G3-01 — ORGADMIN ne lit pas ui-state d'une session hors tenant."""
    user_model = get_user_model()
    org_a = Organisation.objects.create(name="Org A Admin G3")
    org_b = Organisation.objects.create(name="Org B Admin G3")
    admin_a = user_model.objects.create_user(
        username="admin_a_g3_d2m07",
        password="pass",
        organisation=org_a,
        role=Role.ORGADMIN,
    )
    learner_b = user_model.objects.create_user(
        username="learner_b_g3_d2m07",
        password="pass",
        organisation=org_b,
        role=Role.LEARNER,
    )
    group_b = Group.objects.create(organisation=org_b, name="GB Admin G3")
    session_b = HugoSession.objects.create(
        organisation=org_b,
        learner=learner_b,
        group=group_b,
    )

    client = APIClient()
    client.force_authenticate(user=admin_a)
    response = client.get(f"/hugo/sessions/{session_b.id}/ui-state/")

    assert response.status_code == 404


@pytest.mark.django_db
def test_g3_03_d1_04_orgadmin_has_no_export_md_endpoint(api_client, learner_user, organisation, group):
    """G3-03 / D1-04 — pas d'endpoint export-md accessible à ORGADMIN."""
    user_model = get_user_model()
    orgadmin = user_model.objects.create_user(
        username="orgadmin_export_md",
        password="pass",
        organisation=organisation,
        role=Role.ORGADMIN,
    )
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
    )

    api_client.force_authenticate(user=orgadmin)
    response = api_client.get(f"/hugo/sessions/{session.id}/debug/export-md/")

    assert response.status_code == 404


@pytest.mark.django_db
def test_d1_06_ui_state_has_no_llm_analysis_fields(api_client, learner_user, organisation, group):
    """D1-06 — UIState produit sans artefact LLM analysis (D9bis)."""
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
    serialized = json.dumps(response.data, ensure_ascii=False).lower()
    for token in LLM_ANALYSIS_TOKENS:
        assert token not in serialized


@pytest.mark.django_db
def test_f1_02_evidence_bundle_has_no_llm_analysis_artifact(db):
    """F1-02 — bundle Qualiopi sans export ConversationTurnLLMAnalysis."""
    client = APIClient()
    user_model = get_user_model()
    org = Organisation.objects.create(name="Org F1-02")
    admin = user_model.objects.create_user(
        username="admin_f1_02",
        password="pass",
        organisation=org,
        role=Role.ORGADMIN,
    )
    learner = user_model.objects.create_user(
        username="learner_f1_02",
        password="pass",
        organisation=org,
        role=Role.LEARNER,
    )
    group = Group.objects.create(organisation=org, name="G F1-02")
    session = HugoSession.objects.create(organisation=org, learner=learner, group=group)
    Trace.objects.create(organisation=org, session=session, payload_structured={})

    client.force_authenticate(user=admin)
    response = client.post("/quality/qualiopi/evidence-bundle/", {}, format="json")

    assert response.status_code == 200
    zf = zipfile.ZipFile(io.BytesIO(response.content))
    names = set(zf.namelist())
    assert not any("llm_analysis" in name.lower() for name in names)
    bundle_text = " ".join(zf.read(name).decode("utf-8", errors="ignore").lower() for name in names)
    for token in LLM_ANALYSIS_TOKENS:
        assert token not in bundle_text


@pytest.mark.django_db
def test_f1_03_unlinked_tutor_timeline_forbidden(db):
    """F1-03 — tuteur non lié : timeline refusée (403)."""
    client = APIClient()
    org = Organisation.objects.create(name="Org F1-03")
    user_model = get_user_model()
    tutor = user_model.objects.create_user(
        username="tutor_f1_03",
        password="pass",
        organisation=org,
        role=Role.TUTOR,
    )
    learner_linked = user_model.objects.create_user(
        username="learner_linked_f1_03",
        password="pass",
        organisation=org,
        role=Role.LEARNER,
    )
    learner_unlinked = user_model.objects.create_user(
        username="learner_unlinked_f1_03",
        password="pass",
        organisation=org,
        role=Role.LEARNER,
    )
    group = Group.objects.create(organisation=org, name="G F1-03")
    for user in (tutor, learner_linked, learner_unlinked):
        GroupMembership.objects.create(organisation=org, group=group, user=user)
    TutorLearnerLink.objects.create(
        organisation=org, group=group, tutor=tutor, learner=learner_linked
    )

    client.force_authenticate(user=tutor)
    response = client.get(
        f"/dashboard/groups/{group.id}/learners/{learner_unlinked.id}/timeline/"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_inv01_ui_state_surface_has_no_p0_fields(api_client, learner_user, organisation, group):
    """INV-01 — rappel : UIState sans champs P0 (garde-fou lot confidentialité)."""
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
    assert set(response.data.keys()).isdisjoint(P0_FORBIDDEN_IN_UI)
