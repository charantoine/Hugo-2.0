"""D2-M06 + D2-M11 — pack pytest exports & analytics (E3/E4, absence D9bis)."""
import io
import json
import zipfile

import pytest
from django.apps import apps
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role
from apps.hugo.domain.schemas import P0_CORE_FIELDS, P0_LLM_FIELDS
from apps.hugo.models import HugoSession, LearnerEvaluationRecord, Trace
from apps.referentials.models import Group

EVIDENCE_BUNDLE_TRACE_KEYS = {
    "trace_id",
    "session_id",
    "learner_id",
    "validated_at",
    "created_at",
}

P0_FORBIDDEN_IN_EXPORTS = set(P0_CORE_FIELDS) | set(P0_LLM_FIELDS) | {
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

TURN_REVIEW_MARKER = "turn_review_secret_marker_d2m06"


def _bundle_zip(client):
    response = client.post("/quality/qualiopi/evidence-bundle/", {}, format="json")
    assert response.status_code == 200
    return zipfile.ZipFile(io.BytesIO(response.content))


def _bundle_text(zf):
    return " ".join(
        zf.read(name).decode("utf-8", errors="ignore").lower() for name in zf.namelist()
    )


def _export_run_json(client, **body):
    response = client.post("/exports/run/", body or {"format": "json"}, format="json")
    assert response.status_code == 200
    return json.loads(response.content.decode("utf-8"))


@pytest.fixture
def export_org_setup(db):
    user_model = get_user_model()
    org_a = Organisation.objects.create(name="Org D2M06 A")
    org_b = Organisation.objects.create(name="Org D2M06 B")
    admin_a = user_model.objects.create_user(
        username="admin_d2m06_a",
        password="pass",
        organisation=org_a,
        role=Role.ORGADMIN,
    )
    admin_b = user_model.objects.create_user(
        username="admin_d2m06_b",
        password="pass",
        organisation=org_b,
        role=Role.ORGADMIN,
    )
    learner_a = user_model.objects.create_user(
        username="learner_d2m06_a",
        password="pass",
        organisation=org_a,
        role=Role.LEARNER,
    )
    learner_b = user_model.objects.create_user(
        username="learner_d2m06_b",
        password="pass",
        organisation=org_b,
        role=Role.LEARNER,
    )
    group_a = Group.objects.create(organisation=org_a, name="G D2M06 A")
    group_b = Group.objects.create(organisation=org_b, name="G D2M06 B")
    session_a = HugoSession.objects.create(
        organisation=org_a,
        learner=learner_a,
        group=group_a,
    )
    session_b = HugoSession.objects.create(
        organisation=org_b,
        learner=learner_b,
        group=group_b,
    )
    trace_a = Trace.objects.create(
        organisation=org_a,
        session=session_a,
        payload_structured={
            "session_id": str(session_a.id),
            "turn_state": "secret-p0",
            "episode_clarity": 0.9,
        },
    )
    trace_b = Trace.objects.create(
        organisation=org_b,
        session=session_b,
        payload_structured={"session_id": str(session_b.id), "secret": True},
    )
    client = APIClient()
    client.force_authenticate(user=admin_a)
    return {
        "client": client,
        "org_a": org_a,
        "org_b": org_b,
        "admin_a": admin_a,
        "admin_b": admin_b,
        "learner_a": learner_a,
        "learner_b": learner_b,
        "group_a": group_a,
        "group_b": group_b,
        "session_a": session_a,
        "session_b": session_b,
        "trace_a": trace_a,
        "trace_b": trace_b,
    }


# --- Bloc 1 : EvidenceBundle (E3) ---


@pytest.mark.django_db
def test_evidence_bundle_traces_json_shape(export_org_setup):
    """D2-M11 E3 — traces.json : clés métadonnées autorisées uniquement."""
    zf = _bundle_zip(export_org_setup["client"])
    traces = json.loads(zf.read("traces.json"))
    assert traces
    for row in traces:
        assert set(row.keys()) == EVIDENCE_BUNDLE_TRACE_KEYS


@pytest.mark.django_db
def test_evidence_bundle_no_payload_structured(export_org_setup):
    """E3 non-fuite — pas de payload_structured dans le ZIP."""
    zf = _bundle_zip(export_org_setup["client"])
    bundle_text = _bundle_text(zf)
    assert "payload_structured" not in bundle_text
    traces = json.loads(zf.read("traces.json"))
    for row in traces:
        assert "payload_structured" not in row


@pytest.mark.django_db
def test_evidence_bundle_no_p0_tokens(export_org_setup):
    """Confidentialité E3 — P0 persisté en DB mais absent du bundle."""
    zf = _bundle_zip(export_org_setup["client"])
    bundle_text = _bundle_text(zf)
    for token in P0_FORBIDDEN_IN_EXPORTS:
        assert token not in bundle_text


# --- Bloc 2 : ExportRun (E4) ---


@pytest.mark.django_db
def test_export_run_json_includes_payload_structured(export_org_setup):
    """E4 — trace_rich_v1 inclut payload_structured."""
    payload = _export_run_json(export_org_setup["client"])
    assert payload["schema"] == "trace_rich_v1"
    by_id = {item["trace_id"]: item for item in payload["traces"]}
    trace_row = by_id[str(export_org_setup["trace_a"].id)]
    assert "payload_structured" in trace_row
    assert trace_row["payload_structured"]["session_id"] == str(export_org_setup["session_a"].id)


@pytest.mark.django_db
def test_export_run_json_no_llm_analysis(export_org_setup):
    """F1-02 / D9bis — ExportRun sans artefact LLM analysis."""
    payload = _export_run_json(export_org_setup["client"])
    serialized = json.dumps(payload, ensure_ascii=False).lower()
    for token in LLM_ANALYSIS_TOKENS:
        assert token not in serialized


@pytest.mark.django_db
def test_export_run_json_no_p0_in_standard_trace(export_org_setup):
    """E4 garde-fou — squelette generate-trace sans P0 dans l'export."""
    client = APIClient()
    client.force_authenticate(user=export_org_setup["learner_a"])
    gen = client.post(
        f"/hugo/sessions/{export_org_setup['session_a'].id}/generate-trace/",
        {},
        format="json",
    )
    assert gen.status_code == 201

    client.force_authenticate(user=export_org_setup["admin_a"])
    payload = _export_run_json(client)
    by_id = {item["trace_id"]: item for item in payload["traces"]}
    generated_id = str(gen.json()["id"])
    assert generated_id in by_id

    generated_payload = json.dumps(
        by_id[generated_id]["payload_structured"],
        ensure_ascii=False,
    ).lower()
    for token in P0_FORBIDDEN_IN_EXPORTS:
        assert token not in generated_payload


@pytest.mark.django_db
def test_export_run_cross_tenant(export_org_setup):
    """G3-02 — isolation tenant sur ExportRun."""
    client = APIClient()
    client.force_authenticate(user=export_org_setup["admin_b"])
    payload = _export_run_json(client)
    trace_ids = {item["trace_id"] for item in payload["traces"]}
    assert str(export_org_setup["trace_b"].id) in trace_ids
    assert str(export_org_setup["trace_a"].id) not in trace_ids


@pytest.mark.django_db
def test_evidence_bundle_cross_tenant(export_org_setup):
    """G3-02 — isolation tenant sur EvidenceBundle (ENC-CODE-05)."""
    client = APIClient()
    client.force_authenticate(user=export_org_setup["admin_b"])
    zf = _bundle_zip(client)
    bundle_text = _bundle_text(zf)
    assert str(export_org_setup["trace_b"].id) in bundle_text
    assert str(export_org_setup["trace_a"].id) not in bundle_text


@pytest.mark.django_db
def test_learner_forbidden_on_evidence_bundle(export_org_setup):
    """Matrice rôles E3 — LEARNER ne déclenche pas EvidenceBundle."""
    client = APIClient()
    client.force_authenticate(user=export_org_setup["learner_a"])
    response = client.post("/quality/qualiopi/evidence-bundle/", {}, format="json")
    assert response.status_code == 403


@pytest.mark.django_db
def test_learner_forbidden_on_export_run(export_org_setup):
    """Matrice rôles E4 — LEARNER ne déclenche pas ExportRun."""
    client = APIClient()
    client.force_authenticate(user=export_org_setup["learner_a"])
    response = client.post("/exports/run/", {"format": "json"}, format="json")
    assert response.status_code == 403


@pytest.mark.django_db
def test_trainer_eval_export_only_shared_records(db):
    """E2 — export formateur : uniquement records shared_with_tutor=true."""
    client = APIClient()
    user_model = get_user_model()
    org = Organisation.objects.create(name="Org E2 D2M11")
    trainer = user_model.objects.create_user(
        username="trainer_e2_d2m11",
        password="pass",
        organisation=org,
        role=Role.TRAINER,
    )
    learner = user_model.objects.create_user(
        username="learner_e2_d2m11",
        password="pass",
        organisation=org,
        role=Role.LEARNER,
    )
    group = Group.objects.create(organisation=org, name="G E2")
    session_shared = HugoSession.objects.create(
        organisation=org,
        learner=learner,
        group=group,
    )
    session_private = HugoSession.objects.create(
        organisation=org,
        learner=learner,
        group=group,
    )
    shared = LearnerEvaluationRecord.objects.create(
        organisation=org,
        session=session_shared,
        learner=learner,
        group=group,
        shared_with_tutor=True,
        recap_text="shared-recap-marker",
    )
    LearnerEvaluationRecord.objects.create(
        organisation=org,
        session=session_private,
        learner=learner,
        group=group,
        shared_with_tutor=False,
        recap_text="private-recap-marker",
    )

    client.force_authenticate(user=trainer)
    response = client.get("/hugo/trainer/evaluation-records/export/?format=json")
    assert response.status_code == 200
    payload = response.json()
    session_ids = {row["session_id"] for row in payload["records"]}
    assert str(session_shared.id) in session_ids
    assert str(session_private.id) not in session_ids
    serialized = json.dumps(payload, ensure_ascii=False)
    assert "shared-recap-marker" in serialized
    assert "private-recap-marker" not in serialized


# --- Bloc 3 : absence D9bis / frontière E5 ---


@pytest.mark.django_db
def test_d9bis_models_registered_but_not_in_metier_exports(export_org_setup):
    """D2-M06 — modèles D9bis présents mais absents des exports métier E3/E4."""
    registered = {
        model._meta.model_name.lower()
        for model in apps.get_models()
        if model._meta.app_label in {"hugo", "exports", "quality"}
    }
    assert "conversationturnllmanalysis" in registered
    assert "conversationllmanalysis" in registered

    payload = _export_run_json(export_org_setup["client"])
    serialized = json.dumps(payload, ensure_ascii=False).lower()
    for token in LLM_ANALYSIS_TOKENS:
        assert token not in serialized


@pytest.mark.django_db
def test_turn_review_not_in_bundle_or_export_run(export_org_setup, db):
    """Frontière E5/E6 — contenu turn-review (debug) absent des exports E3/E4."""
    from apps.hugo.models import HugoMessage

    HugoMessage.objects.create(
        organisation=export_org_setup["org_a"],
        session=export_org_setup["session_a"],
        role=HugoMessage.Role.LEARNER,
        content="visible user turn",
        llm_request_payload={TURN_REVIEW_MARKER: True, "turn_state": "debug-only"},
    )

    zf = _bundle_zip(export_org_setup["client"])
    assert TURN_REVIEW_MARKER.lower() not in _bundle_text(zf)

    payload = _export_run_json(export_org_setup["client"])
    export_text = json.dumps(payload, ensure_ascii=False).lower()
    assert TURN_REVIEW_MARKER.lower() not in export_text
    for token in ("llm_request_payload", "llm_response_payload"):
        assert token not in export_text


@pytest.mark.django_db
def test_d9bis_absent_in_ui_state(api_client, learner_user, organisation, group):
    """D1-06 / D9bis — UIState sans champs LLM analysis dédiés."""
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
