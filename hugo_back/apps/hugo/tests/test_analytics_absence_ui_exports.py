"""Tests d'absence analytics LLM / D9bis sur surfaces métier."""
import io
import json
import zipfile

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role
from apps.hugo.models import HugoMessage, HugoSession, Trace
from apps.hugo.services.d9bis_analytics import build_or_refresh_d9bis_for_session
from apps.referentials.models import Group

FORBIDDEN_IN_METIER_SURFACES = (
    "d9bis_session_export",
    "turn_analyses_count",
    "quality_signals",
    "pedagogical_tags",
    "conversation_summary_v1",
    "turn_analysis_id",
    "session_analysis_id",
    "llm_request_payload",
    "llm_response_payload",
)


@pytest.fixture
def analytics_absence_setup(db):
    user_model = get_user_model()
    org = Organisation.objects.create(name="Org Absence")
    superadmin = user_model.objects.create_user(
        username="super_absence",
        password="pass",
        organisation=org,
        role=Role.SUPERADMIN,
    )
    orgadmin = user_model.objects.create_user(
        username="orgadmin_absence",
        password="pass",
        organisation=org,
        role=Role.ORGADMIN,
    )
    learner = user_model.objects.create_user(
        username="learner_absence",
        password="pass",
        organisation=org,
        role=Role.LEARNER,
    )
    group = Group.objects.create(organisation=org, name="G Absence")
    session = HugoSession.objects.create(
        organisation=org,
        learner=learner,
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
    HugoMessage.objects.create(
        organisation=org,
        session=session,
        role=HugoMessage.Role.LEARNER,
        content="Message test absence analytics.",
    )
    Trace.objects.create(
        organisation=org,
        session=session,
        payload_structured={"session_id": str(session.id)},
    )
    build_or_refresh_d9bis_for_session(session)
    return {
        "org": org,
        "superadmin": superadmin,
        "orgadmin": orgadmin,
        "learner": learner,
        "session": session,
    }


def _assert_no_forbidden_tokens(serialized: str) -> None:
    lowered = serialized.lower()
    for token in FORBIDDEN_IN_METIER_SURFACES:
        assert token not in lowered


@pytest.mark.django_db
def test_ui_state_has_no_d9bis_fields(analytics_absence_setup):
    client = APIClient()
    client.force_authenticate(user=analytics_absence_setup["learner"])
    response = client.get(f"/hugo/sessions/{analytics_absence_setup['session'].id}/ui-state/")
    assert response.status_code == 200
    _assert_no_forbidden_tokens(json.dumps(response.data, ensure_ascii=False))


@pytest.mark.django_db
def test_export_run_json_has_no_d9bis(analytics_absence_setup):
    client = APIClient()
    client.force_authenticate(user=analytics_absence_setup["orgadmin"])
    response = client.post("/exports/run/", {"format": "json"}, format="json")
    assert response.status_code == 200
    _assert_no_forbidden_tokens(response.content.decode("utf-8"))


@pytest.mark.django_db
def test_export_run_csv_has_no_d9bis(analytics_absence_setup):
    client = APIClient()
    client.force_authenticate(user=analytics_absence_setup["orgadmin"])
    response = client.post("/exports/run/", {"format": "csv"}, format="json")
    assert response.status_code == 200
    _assert_no_forbidden_tokens(response.content.decode("utf-8"))


@pytest.mark.django_db
def test_evidence_bundle_has_no_d9bis(analytics_absence_setup):
    client = APIClient()
    client.force_authenticate(user=analytics_absence_setup["orgadmin"])
    response = client.post("/quality/qualiopi/evidence-bundle/", {}, format="json")
    assert response.status_code == 200
    zf = zipfile.ZipFile(io.BytesIO(response.content))
    bundle_text = " ".join(
        zf.read(name).decode("utf-8", errors="ignore") for name in zf.namelist()
    )
    _assert_no_forbidden_tokens(bundle_text)


@pytest.mark.django_db
def test_generate_trace_has_no_d9bis(analytics_absence_setup):
    client = APIClient()
    client.force_authenticate(user=analytics_absence_setup["learner"])
    response = client.post(
        f"/hugo/sessions/{analytics_absence_setup['session'].id}/generate-trace/",
        {},
        format="json",
    )
    assert response.status_code == 201
    _assert_no_forbidden_tokens(json.dumps(response.json(), ensure_ascii=False))


@pytest.mark.django_db
def test_base_observability_has_no_d9bis(analytics_absence_setup):
    client = APIClient()
    client.force_authenticate(user=analytics_absence_setup["orgadmin"])
    response = client.get(
        f"/internal/hugo/sessions/{analytics_absence_setup['session'].id}/observability/"
    )
    assert response.status_code == 200
    _assert_no_forbidden_tokens(json.dumps(response.data, ensure_ascii=False))


@pytest.mark.django_db
def test_d9bis_export_accessible_superadmin_only(analytics_absence_setup):
    session_id = analytics_absence_setup["session"].id
    client = APIClient()

    client.force_authenticate(user=analytics_absence_setup["orgadmin"])
    assert client.get(f"/internal/hugo/sessions/{session_id}/d9bis/export/").status_code == 403

    client.force_authenticate(user=analytics_absence_setup["superadmin"])
    export_resp = client.get(f"/internal/hugo/sessions/{session_id}/d9bis/export/")
    assert export_resp.status_code == 200
    assert export_resp.data["schema"] == "d9bis_session_export_v1"
