"""D9bis — tests d'absence artefacts analytiques LLM sur surfaces métier."""
import io
import json
import zipfile

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role
from apps.hugo.domain.d9bis_contracts import D9BIS_EXPORT_SCOPE, D9BIS_SCHEMA_VERSION
from apps.hugo.models import HugoSession, Trace
from apps.referentials.models import Group

LLM_ANALYSIS_TOKENS = (
    "conversationturnllmanalysis",
    "conversationllmanalysis",
    "llm_analysis",
    "d9bis_contract",
    "turn_analyses",
)


@pytest.fixture
def d9bis_setup(db):
    user_model = get_user_model()
    org = Organisation.objects.create(name="Org D9bis")
    learner = user_model.objects.create_user(
        username="learner_d9bis",
        password="pass",
        organisation=org,
        role=Role.LEARNER,
    )
    admin = user_model.objects.create_user(
        username="admin_d9bis",
        password="pass",
        organisation=org,
        role=Role.ORGADMIN,
    )
    group = Group.objects.create(organisation=org, name="G D9bis")
    session = HugoSession.objects.create(organisation=org, learner=learner, group=group)
    Trace.objects.create(
        organisation=org,
        session=session,
        payload_structured={"session_id": str(session.id)},
    )
    return {"org": org, "learner": learner, "admin": admin, "group": group, "session": session}


@pytest.mark.django_db
def test_d9bis_contracts_schema_version():
    """Contrats D9bis — version et scope export technique."""
    assert D9BIS_SCHEMA_VERSION == "d9bis_v1"
    assert D9BIS_EXPORT_SCOPE == "debug_superadmin_only"


@pytest.mark.django_db
def test_ui_state_has_no_llm_analysis_fields(d9bis_setup):
    session = d9bis_setup["session"]
    session.conversation_progress = {
        "session_id": str(session.id),
        "posture": "reflective_afest",
        "active_branches": [],
        "active_branches_count": 0,
        "overall_maturity": "red",
        "synthesis_eligible": False,
        "evaluation_eligible": False,
        "missing_for_next_level": [],
        "reason_codes": [],
    }
    session.save(update_fields=["conversation_progress"])

    client = APIClient()
    client.force_authenticate(user=d9bis_setup["learner"])
    response = client.get(f"/hugo/sessions/{session.id}/ui-state/")
    assert response.status_code == 200
    serialized = json.dumps(response.data, ensure_ascii=False).lower()
    for token in LLM_ANALYSIS_TOKENS:
        assert token not in serialized


@pytest.mark.django_db
def test_export_run_has_no_llm_analysis(d9bis_setup):
    client = APIClient()
    client.force_authenticate(user=d9bis_setup["admin"])
    response = client.post("/exports/run/", {"format": "json"}, format="json")
    assert response.status_code == 200
    serialized = response.content.decode("utf-8").lower()
    for token in LLM_ANALYSIS_TOKENS:
        assert token not in serialized


@pytest.mark.django_db
def test_evidence_bundle_has_no_llm_analysis(d9bis_setup):
    client = APIClient()
    client.force_authenticate(user=d9bis_setup["admin"])
    response = client.post("/quality/qualiopi/evidence-bundle/", {}, format="json")
    assert response.status_code == 200
    zf = zipfile.ZipFile(io.BytesIO(response.content))
    bundle_text = " ".join(
        zf.read(name).decode("utf-8", errors="ignore").lower() for name in zf.namelist()
    )
    for token in LLM_ANALYSIS_TOKENS:
        assert token not in bundle_text


@pytest.mark.django_db
def test_observability_endpoint_has_no_llm_analysis(d9bis_setup):
    client = APIClient()
    client.force_authenticate(user=d9bis_setup["admin"])
    response = client.get(f"/internal/hugo/sessions/{d9bis_setup['session'].id}/observability/")
    assert response.status_code == 200
    serialized = json.dumps(response.data, ensure_ascii=False).lower()
    for token in LLM_ANALYSIS_TOKENS:
        assert token not in serialized
