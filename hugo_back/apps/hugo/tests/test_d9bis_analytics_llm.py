"""D9bis analytics LLM — structure, invariants, multi-tenant."""
import json

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role
from apps.hugo.domain.d9bis_contracts import D9BIS_FORBIDDEN_KEYS, D9BIS_SCHEMA_VERSION
from apps.hugo.domain.schemas import P0_CORE_FIELDS, P0_LLM_FIELDS
from apps.hugo.models import ConversationLLMAnalysis, ConversationTurnLLMAnalysis, HugoMessage, HugoSession
from apps.hugo.services.d9bis_analytics import (
    build_or_refresh_d9bis_for_session,
    serialize_session_analysis,
)
from apps.referentials.models import Group


@pytest.fixture
def d9bis_analytics_setup(db):
    user_model = get_user_model()
    org_a = Organisation.objects.create(name="Org D9bis A")
    org_b = Organisation.objects.create(name="Org D9bis B")
    super_a = user_model.objects.create_user(
        username="super_d9bis_a",
        password="pass",
        organisation=org_a,
        role=Role.SUPERADMIN,
    )
    orgadmin_a = user_model.objects.create_user(
        username="orgadmin_d9bis_a",
        password="pass",
        organisation=org_a,
        role=Role.ORGADMIN,
    )
    learner_a = user_model.objects.create_user(
        username="learner_d9bis_a",
        password="pass",
        organisation=org_a,
        role=Role.LEARNER,
    )
    learner_b = user_model.objects.create_user(
        username="learner_d9bis_b",
        password="pass",
        organisation=org_b,
        role=Role.LEARNER,
    )
    group_a = Group.objects.create(organisation=org_a, name="G D9bis A")
    session_a = HugoSession.objects.create(
        organisation=org_a,
        learner=learner_a,
        group=group_a,
        posture="reflective_afest",
        conversation_progress={
            "session_id": "pending",
            "posture": "reflective_afest",
            "active_branches_count": 1,
            "overall_maturity": "orange",
            "synthesis_eligible": True,
            "evaluation_eligible": False,
            "reason_codes": ["evaluation_blocked_maturity"],
        },
        analytics_state={"cta_evaluation_blocked_count": 2},
    )
    session_a.conversation_progress["session_id"] = str(session_a.id)
    session_a.save(update_fields=["conversation_progress"])

    HugoMessage.objects.create(
        organisation=org_a,
        session=session_a,
        role=HugoMessage.Role.LEARNER,
        content="J'ai vécu une situation complexe sur le chantier avec mon équipe.",
        llm_request_payload={
            "conversation_progress": {"overall_maturity": "orange", "episode_clarity": 0.9},
            "turn_state": {"secret": True},
        },
    )
    HugoMessage.objects.create(
        organisation=org_a,
        session=session_a,
        role=HugoMessage.Role.ASSISTANT,
        content="Réponse assistant — ne doit pas être stockée D9bis.",
    )

    session_b = HugoSession.objects.create(organisation=org_b, learner=learner_b, group=Group.objects.create(organisation=org_b, name="G B"))

    return {
        "org_a": org_a,
        "org_b": org_b,
        "super_a": super_a,
        "orgadmin_a": orgadmin_a,
        "learner_a": learner_a,
        "session_a": session_a,
        "session_b": session_b,
    }


@pytest.mark.django_db
def test_build_d9bis_creates_turn_and_session_analyses(d9bis_analytics_setup):
    aggregate = build_or_refresh_d9bis_for_session(d9bis_analytics_setup["session_a"])

    assert aggregate.analysis_version == D9BIS_SCHEMA_VERSION
    assert aggregate.turn_analyses_count == 1
    assert ConversationTurnLLMAnalysis.objects.filter(session=aggregate.session).count() == 1

    turn = ConversationTurnLLMAnalysis.objects.get(session=aggregate.session)
    assert turn.quality_signals["learner_char_length_bucket"] in {"short", "medium", "long"}
    assert "episode_clarity" not in turn.quality_signals
    assert turn.pedagogical_tags


@pytest.mark.django_db
def test_d9bis_export_has_no_verbatim_or_p0(d9bis_analytics_setup):
    aggregate = build_or_refresh_d9bis_for_session(d9bis_analytics_setup["session_a"])
    payload = serialize_session_analysis(aggregate)

    serialized = json.dumps(payload, ensure_ascii=False).lower()
    assert "j'ai vécu" not in serialized
    assert "réponse assistant" not in serialized
    for field in set(P0_CORE_FIELDS) | set(P0_LLM_FIELDS) | set(D9BIS_FORBIDDEN_KEYS):
        assert field not in serialized


@pytest.mark.django_db
def test_d9bis_endpoints_superadmin_only(d9bis_analytics_setup):
    session_id = d9bis_analytics_setup["session_a"].id
    client = APIClient()

    client.force_authenticate(user=d9bis_analytics_setup["orgadmin_a"])
    assert client.post(f"/internal/hugo/sessions/{session_id}/d9bis/build/", {}, format="json").status_code == 403
    assert client.get(f"/internal/hugo/sessions/{session_id}/d9bis/export/").status_code == 403

    client.force_authenticate(user=d9bis_analytics_setup["super_a"])
    build_resp = client.post(f"/internal/hugo/sessions/{session_id}/d9bis/build/", {}, format="json")
    assert build_resp.status_code == 201
    export_resp = client.get(f"/internal/hugo/sessions/{session_id}/d9bis/export/")
    assert export_resp.status_code == 200
    assert export_resp.data["schema"] == "d9bis_session_export_v1"
    assert export_resp.data["turn_analyses_count"] == 1


@pytest.mark.django_db
def test_d9bis_cross_tenant_isolation(d9bis_analytics_setup):
    build_or_refresh_d9bis_for_session(d9bis_analytics_setup["session_a"])
    build_or_refresh_d9bis_for_session(d9bis_analytics_setup["session_b"])

    client = APIClient()
    client.force_authenticate(user=d9bis_analytics_setup["super_a"])
    export_a = client.get(
        f"/internal/hugo/sessions/{d9bis_analytics_setup['session_a'].id}/d9bis/export/"
    )
    assert export_a.status_code == 200
    assert export_a.data["organisation_id"] == str(d9bis_analytics_setup["org_a"].id)

    export_b_attempt = client.get(
        f"/internal/hugo/sessions/{d9bis_analytics_setup['session_b'].id}/d9bis/export/"
    )
    assert export_b_attempt.status_code == 404

    assert ConversationLLMAnalysis.objects.filter(
        organisation=d9bis_analytics_setup["org_a"]
    ).count() == 1
    assert ConversationLLMAnalysis.objects.filter(
        organisation=d9bis_analytics_setup["org_b"]
    ).count() == 1
