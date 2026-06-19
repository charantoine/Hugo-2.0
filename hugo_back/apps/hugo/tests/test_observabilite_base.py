"""Observabilité de base (domaine 80) — signaux techniques, non exposés UIState apprenant."""
import json

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role
from apps.hugo.models import EvaluationPolicy, HugoMessage, HugoSession
from apps.hugo.services.session_observability import build_session_observability_snapshot
from apps.referentials.models import Group


def _red_progress(session_id: str) -> dict:
    return {
        "session_id": session_id,
        "posture": "reflective_afest",
        "active_branches": [],
        "active_branches_count": 0,
        "overall_maturity": "red",
        "synthesis_eligible": False,
        "evaluation_eligible": False,
        "missing_for_next_level": ["Décrire la situation vécue."],
        "reason_codes": ["evaluation_blocked_maturity"],
    }


@pytest.mark.django_db
def test_cta_blocked_counters_increment(api_client, learner_user, organisation, group):
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        conversation_progress=_red_progress("pending"),
    )
    session.conversation_progress["session_id"] = str(session.id)
    session.save(update_fields=["conversation_progress"])

    EvaluationPolicy.objects.get_or_create(
        organisation=organisation,
        group=group,
        defaults={"allow_early_trigger": False},
    )

    api_client.force_authenticate(user=learner_user)
    eval_resp = api_client.post(f"/hugo/sessions/{session.id}/request-evaluation/", {}, format="json")
    synth_resp = api_client.post(f"/hugo/sessions/{session.id}/request-synthesis/", {}, format="json")
    assert eval_resp.status_code == 400
    assert synth_resp.status_code == 400

    session.refresh_from_db()
    analytics = session.analytics_state or {}
    assert analytics.get("cta_evaluation_blocked_count") == 1
    assert analytics.get("cta_synthesis_blocked_count") == 1


@pytest.mark.django_db
def test_observability_snapshot_turn_counts(db):
    user_model = get_user_model()
    org = Organisation.objects.create(name="Org Obs")
    learner = user_model.objects.create_user(
        username="learner_obs",
        password="pass",
        organisation=org,
        role=Role.LEARNER,
    )
    group = Group.objects.create(organisation=org, name="G Obs")
    session = HugoSession.objects.create(organisation=org, learner=learner, group=group)
    HugoMessage.objects.create(
        session=session,
        organisation=org,
        role=HugoMessage.Role.LEARNER,
        content="Bonjour",
    )
    HugoMessage.objects.create(
        session=session,
        organisation=org,
        role=HugoMessage.Role.ASSISTANT,
        content="Réponse",
    )

    snapshot = build_session_observability_snapshot(session)
    assert snapshot["schema"] == "session_observability_v1"
    assert snapshot["turn_counts"]["learner"] == 1
    assert snapshot["turn_counts"]["assistant"] == 1
    assert snapshot["scope"] == "admin_debug_only"


@pytest.mark.django_db
def test_observability_endpoint_admin_only(api_client, learner_user, organisation, group):
    user_model = get_user_model()
    admin = user_model.objects.create_user(
        username="admin_obs",
        password="pass",
        organisation=organisation,
        role=Role.ORGADMIN,
    )
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
    )

    api_client.force_authenticate(user=learner_user)
    forbidden = api_client.get(f"/internal/hugo/sessions/{session.id}/observability/")
    assert forbidden.status_code == 403

    api_client.force_authenticate(user=admin)
    allowed = api_client.get(f"/internal/hugo/sessions/{session.id}/observability/")
    assert allowed.status_code == 200
    assert allowed.data["schema"] == "session_observability_v1"


@pytest.mark.django_db
def test_ui_state_does_not_expose_observability(api_client, learner_user, organisation, group):
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        analytics_state={
            "cta_evaluation_blocked_count": 3,
            "cta_synthesis_blocked_count": 2,
        },
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
    for token in (
        "session_observability",
        "cta_evaluation_blocked_count",
        "cta_synthesis_blocked_count",
        "admin_debug_only",
    ):
        assert token not in serialized
