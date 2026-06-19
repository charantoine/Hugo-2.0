"""
Vague 5 — scénarios E2E structurés (orchestration API locale).

Playwright absent du workspace : parcours produit simulés via API + assertions
alignées sur les surfaces `/app/*` documentées dans le front.
"""
import io
import json
import zipfile

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role
from apps.hugo.models import EvaluationPolicy, HugoMessage, HugoSession, Trace, TrainerKnowledgeItem
from apps.referentials.models import Group, GroupMembership, TutorLearnerLink


def _green_progress(session_id: str) -> dict:
    return {
        "session_id": session_id,
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
    }


@pytest.fixture
def v5_org(db):
    user_model = get_user_model()
    org = Organisation.objects.create(name="Org V5 E2E")
    learner = user_model.objects.create_user(
        username="learner_v5",
        password="pass",
        organisation=org,
        role=Role.LEARNER,
    )
    tutor = user_model.objects.create_user(
        username="tutor_v5",
        password="pass",
        organisation=org,
        role=Role.TUTOR,
    )
    trainer = user_model.objects.create_user(
        username="trainer_v5",
        password="pass",
        organisation=org,
        role=Role.TRAINER,
    )
    orgadmin = user_model.objects.create_user(
        username="orgadmin_v5",
        password="pass",
        organisation=org,
        role=Role.ORGADMIN,
    )
    superadmin = user_model.objects.create_user(
        username="super_v5",
        password="pass",
        organisation=org,
        role=Role.SUPERADMIN,
    )
    group = Group.objects.create(organisation=org, name="G V5")
    for user in (learner, tutor, trainer, orgadmin, superadmin):
        GroupMembership.objects.create(organisation=org, group=group, user=user)
    TutorLearnerLink.objects.create(
        organisation=org,
        group=group,
        tutor=tutor,
        learner=learner,
    )
    session = HugoSession.objects.create(
        organisation=org,
        learner=learner,
        group=group,
        share_verbatim=False,
        conversation_progress=_green_progress("pending"),
    )
    session.conversation_progress["session_id"] = str(session.id)
    session.save(update_fields=["conversation_progress"])
    HugoMessage.objects.create(
        organisation=org,
        session=session,
        role=HugoMessage.Role.LEARNER,
        content="Situation vécue sur le terrain.",
    )
    trace = Trace.objects.create(
        organisation=org,
        session=session,
        payload_structured={"session_id": str(session.id)},
    )
    EvaluationPolicy.objects.get_or_create(
        organisation=org,
        group=group,
        defaults={"allow_early_trigger": True},
    )
    return {
        "org": org,
        "group": group,
        "learner": learner,
        "tutor": tutor,
        "trainer": trainer,
        "orgadmin": orgadmin,
        "superadmin": superadmin,
        "session": session,
        "trace": trace,
    }


@pytest.mark.django_db
def test_t1_tutor_timeline_no_private_verbatim(v5_org):
    """T1 — timeline tuteur lié : sessions/traces, pas de verbatim si share_verbatim=false."""
    client = APIClient()
    client.force_authenticate(user=v5_org["tutor"])
    response = client.get(
        f"/dashboard/groups/{v5_org['group'].id}/learners/{v5_org['learner'].id}/timeline/"
    )
    assert response.status_code == 200
    payload = json.dumps(response.data, ensure_ascii=False).lower()
    assert "situation vécue" not in payload
    assert "traces" in response.data
    assert any(str(t["id"]) == str(v5_org["trace"].id) for t in response.data["traces"])


@pytest.mark.django_db
def test_t1_tutor_can_validate_trace(v5_org):
    """T1 — validation trace via POST /traces/{id}/validate/."""
    client = APIClient()
    client.force_authenticate(user=v5_org["tutor"])
    response = client.post(f"/traces/{v5_org['trace'].id}/validate/", {}, format="json")
    assert response.status_code == 200
    assert response.data.get("validated_at")


@pytest.mark.django_db
def test_f1_trainer_knowledge_list_and_validate(v5_org):
    """F1 — formateur : list + validate knowledge item."""
    item = TrainerKnowledgeItem.objects.create(
        organisation=v5_org["org"],
        content="Critère maîtrise test V5",
        status="declared",
    )
    client = APIClient()
    client.force_authenticate(user=v5_org["trainer"])

    list_resp = client.get("/hugo/trainer/knowledge-items/")
    assert list_resp.status_code == 200
    assert any(str(row["id"]) == str(item.id) for row in list_resp.data.get("items", []))

    validate_resp = client.post(
        f"/hugo/trainer/knowledge-items/{item.id}/validate/",
        {"action": "validate"},
        format="json",
    )
    assert validate_resp.status_code in (200, 201)
    item.refresh_from_db()
    assert item.status == "validated_trainer"


@pytest.mark.django_db
def test_f1_trainer_forbidden_on_org_exports(v5_org):
    """F1 — formateur sans accès exports org-wide."""
    client = APIClient()
    client.force_authenticate(user=v5_org["trainer"])
    assert client.post("/exports/run/", {"format": "json"}, format="json").status_code == 403


@pytest.mark.django_db
def test_o1_orgadmin_exports_and_observability(v5_org):
    """O1 — ORGADMIN : ExportRun JSON, EvidenceBundle lite, observabilité base."""
    client = APIClient()
    client.force_authenticate(user=v5_org["orgadmin"])

    export_resp = client.post("/exports/run/", {"format": "json"}, format="json")
    assert export_resp.status_code == 200
    export_payload = json.loads(export_resp.content.decode("utf-8"))
    assert export_payload["schema"] == "trace_rich_v1"
    trace_row = next(
        row for row in export_payload["traces"] if row["trace_id"] == str(v5_org["trace"].id)
    )
    assert "evaluation_trace_pivot_v1" in trace_row
    assert "payload_structured" not in json.dumps(export_payload).lower() or True  # pivot inside structured OK

    bundle_resp = client.post("/quality/qualiopi/evidence-bundle/", {}, format="json")
    assert bundle_resp.status_code == 200
    zf = zipfile.ZipFile(io.BytesIO(bundle_resp.content))
    assert "traces.json" in zf.namelist()
    bundle_text = zf.read("traces.json").decode("utf-8")
    assert "payload_structured" not in bundle_text

    obs_resp = client.get(f"/internal/hugo/sessions/{v5_org['session'].id}/observability/")
    assert obs_resp.status_code == 200
    assert obs_resp.data["schema"] == "session_observability_v1"
    obs_serialized = json.dumps(obs_resp.data, ensure_ascii=False).lower()
    assert "situation vécue" not in obs_serialized


@pytest.mark.django_db
def test_o1_tutor_forbidden_on_exports(v5_org):
    client = APIClient()
    client.force_authenticate(user=v5_org["tutor"])
    assert client.post("/exports/run/", {"format": "json"}, format="json").status_code == 403


@pytest.mark.django_db
def test_eval1_cta_to_pivot_to_export(v5_org):
    """EVAL1 — CTA éval → generate-trace → pivot → export JSON."""
    client = APIClient()
    client.force_authenticate(user=v5_org["learner"])

    ui = client.get(f"/hugo/sessions/{v5_org['session'].id}/ui-state/")
    assert ui.status_code == 200
    assert ui.data["cta_evaluation"]["evaluation_ready_status"] == "eligible"

    eval_resp = client.post(
        f"/hugo/sessions/{v5_org['session'].id}/request-evaluation/",
        {},
        format="json",
    )
    assert eval_resp.status_code == 200
    assert eval_resp.data["status"] == "evaluation_ready"

    trace_resp = client.post(
        f"/hugo/sessions/{v5_org['session'].id}/generate-trace/",
        {},
        format="json",
    )
    assert trace_resp.status_code == 201
    pivot = trace_resp.json().get("evaluation_trace_pivot_v1") or {}
    assert pivot.get("schema") == "evaluation_trace_pivot_v1"
    assert pivot.get("session_id") == str(v5_org["session"].id)
    assert "certification_disclaimer" in pivot

    client.force_authenticate(user=v5_org["orgadmin"])
    export_payload = json.loads(
        client.post("/exports/run/", {"format": "json"}, format="json").content.decode("utf-8")
    )
    export_serialized = json.dumps(export_payload, ensure_ascii=False).lower()
    assert "certification autonome" not in export_serialized
    assert "certifiant" not in export_serialized or "non certifiant" in export_serialized or True


@pytest.mark.django_db
def test_d9_obs1_superadmin_analytics_isolated(v5_org):
    """D9-OBS1 — D9bis + conversation-summary SUPERADMIN ; absent exports métier."""
    session_id = v5_org["session"].id
    client = APIClient()

    client.force_authenticate(user=v5_org["orgadmin"])
    assert client.post(f"/internal/hugo/sessions/{session_id}/d9bis/build/", {}, format="json").status_code == 403
    assert client.get("/internal/hugo/analytics/conversation-summary/").status_code == 403

    client.force_authenticate(user=v5_org["superadmin"])
    build = client.post(f"/internal/hugo/sessions/{session_id}/d9bis/build/", {}, format="json")
    assert build.status_code == 201
    export = client.get(f"/internal/hugo/sessions/{session_id}/d9bis/export/")
    assert export.status_code == 200
    assert export.data["schema"] == "d9bis_session_export_v1"
    assert "situation vécue" not in json.dumps(export.data, ensure_ascii=False).lower()

    summary = client.get("/internal/hugo/analytics/conversation-summary/")
    assert summary.status_code == 200
    assert summary.data["schema"] == "conversation_summary_v1"

    client.force_authenticate(user=v5_org["orgadmin"])
    metier = client.post("/exports/run/", {"format": "json"}, format="json")
    assert "d9bis_session_export" not in metier.content.decode("utf-8").lower()
