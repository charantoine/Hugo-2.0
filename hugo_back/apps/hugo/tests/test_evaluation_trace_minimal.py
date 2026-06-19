"""EvaluationTrace pivot minimal — schéma, mapping, cohérence trace_rich_v1 / export."""
import json

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role
from apps.hugo.models import Evidence, HugoSession, LearnerEvaluationRecord, Trace
from apps.hugo.services.evaluation_trace_pivot import (
    PIVOT_SCHEMA,
    build_evaluation_trace_pivot,
    enrich_trace_payload_with_pivot,
)
from apps.referentials.models import Group


@pytest.fixture
def pivot_setup(db):
    user_model = get_user_model()
    org = Organisation.objects.create(name="Org Pivot")
    learner = user_model.objects.create_user(
        username="learner_pivot",
        password="pass",
        organisation=org,
        role=Role.LEARNER,
    )
    admin = user_model.objects.create_user(
        username="admin_pivot",
        password="pass",
        organisation=org,
        role=Role.ORGADMIN,
    )
    group = Group.objects.create(organisation=org, name="G Pivot")
    session = HugoSession.objects.create(
        organisation=org,
        learner=learner,
        group=group,
    )
    record = LearnerEvaluationRecord.objects.create(
        organisation=org,
        session=session,
        learner=learner,
        group=group,
        overall_status=LearnerEvaluationRecord.OverallStatus.COMPLETE,
        trigger_maturity="green",
        items=[{"criterion_code": "C1", "status": "covered"}],
        recap_text="Récap test pivot.",
        evaluation_profile_used="default",
        shared_with_tutor=True,
    )
    trace = Trace.objects.create(
        organisation=org,
        session=session,
        payload_structured={"session_id": str(session.id)},
    )
    evidence = Evidence.objects.create(
        organisation=org,
        trace=trace,
        session=session,
        file_path="/media/evidence/test.jpg",
        meta={"kind": "photo", "caption": "Preuve test"},
    )
    return {
        "org": org,
        "learner": learner,
        "admin": admin,
        "group": group,
        "session": session,
        "record": record,
        "trace": trace,
        "evidence": evidence,
    }


@pytest.mark.django_db
def test_build_evaluation_trace_pivot_nominal(pivot_setup):
    pivot = build_evaluation_trace_pivot(pivot_setup["session"], trace=pivot_setup["trace"])

    assert pivot["schema"] == PIVOT_SCHEMA
    assert pivot["session_id"] == str(pivot_setup["session"].id)
    assert pivot["organisation_id"] == str(pivot_setup["org"].id)
    assert pivot["learner_id"] == str(pivot_setup["learner"].id)
    assert pivot["group_id"] == str(pivot_setup["group"].id)

    record = pivot["evaluation_record"]
    assert record["record_id"] == str(pivot_setup["record"].id)
    assert record["overall_status"] == "complete"
    assert record["trigger_maturity"] == "green"
    assert record["items_count"] == 1

    trace = pivot["trace"]
    assert trace["trace_id"] == str(pivot_setup["trace"].id)
    assert trace["criterion_assessments"] == []

    evidence = pivot["evidence"]
    assert len(evidence) == 1
    assert evidence[0]["evidence_id"] == str(pivot_setup["evidence"].id)
    assert evidence[0]["trace_id"] == str(pivot_setup["trace"].id)

    assert "certification_disclaimer" in pivot


@pytest.mark.django_db
def test_generate_trace_includes_pivot(pivot_setup):
    client = APIClient()
    client.force_authenticate(user=pivot_setup["learner"])
    response = client.post(
        f"/hugo/sessions/{pivot_setup['session'].id}/generate-trace/",
        {},
        format="json",
    )
    assert response.status_code == 201
    body = response.json()
    assert "evaluation_trace_pivot_v1" in body
    pivot = body["evaluation_trace_pivot_v1"]
    assert pivot["schema"] == PIVOT_SCHEMA
    assert pivot["session_id"] == str(pivot_setup["session"].id)
    assert pivot["evaluation_record"]["record_id"] == str(pivot_setup["record"].id)


@pytest.mark.django_db
def test_export_json_includes_evaluation_trace_pivot(pivot_setup):
    payload = enrich_trace_payload_with_pivot(
        pivot_setup["session"],
        pivot_setup["trace"].payload_structured,
        trace=pivot_setup["trace"],
    )
    pivot_setup["trace"].payload_structured = payload
    pivot_setup["trace"].save(update_fields=["payload_structured"])

    client = APIClient()
    client.force_authenticate(user=pivot_setup["admin"])
    response = client.post("/exports/run/", {"format": "json"}, format="json")
    assert response.status_code == 200

    export_payload = json.loads(response.content.decode("utf-8"))
    assert export_payload["schema"] == "trace_rich_v1"
    by_trace = {row["trace_id"]: row for row in export_payload["traces"]}
    trace_row = by_trace[str(pivot_setup["trace"].id)]
    assert "evaluation_trace_pivot_v1" in trace_row
    pivot = trace_row["evaluation_trace_pivot_v1"]
    assert pivot["schema"] == PIVOT_SCHEMA
    assert pivot["evaluation_record"]["record_id"] == str(pivot_setup["record"].id)
    assert pivot["evidence"][0]["evidence_id"] == str(pivot_setup["evidence"].id)
