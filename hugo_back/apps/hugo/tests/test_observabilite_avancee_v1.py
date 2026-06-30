"""Observabilité avancée v1 — agrégats et permissions SUPERADMIN."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role
from apps.hugo.models import ConversationQualitySignal, HugoMessage, HugoSession
from apps.hugo.services.observability_advanced_v1 import build_conversation_summary
from apps.referentials.models import Group


@pytest.fixture
def obs_adv_setup(db):
    user_model = get_user_model()
    org = Organisation.objects.create(name="Org Obs Adv")
    superadmin = user_model.objects.create_user(
        username="super_obs_adv",
        password="pass",
        organisation=org,
        role=Role.SUPERADMIN,
    )
    orgadmin = user_model.objects.create_user(
        username="orgadmin_obs_adv",
        password="pass",
        organisation=org,
        role=Role.ORGADMIN,
    )
    learner = user_model.objects.create_user(
        username="learner_obs_adv",
        password="pass",
        organisation=org,
        role=Role.LEARNER,
    )
    group = Group.objects.create(organisation=org, name="G Obs Adv")
    session = HugoSession.objects.create(
        organisation=org,
        learner=learner,
        group=group,
        posture="reflective_afest",
        analytics_state={
            "cta_synthesis_blocked_count": 1,
            "cta_evaluation_blocked_count": 2,
            "posture_switch_count": 1,
            "synthesis_requested": True,
        },
    )
    HugoMessage.objects.create(
        organisation=org,
        session=session,
        role=HugoMessage.Role.LEARNER,
        content="Tour 1",
    )
    HugoMessage.objects.create(
        organisation=org,
        session=session,
        role=HugoMessage.Role.ASSISTANT,
        content="Réponse",
    )
    ConversationQualitySignal.objects.create(
        session=session,
        organisation=org,
        learner=learner,
        posture="reflective_afest",
        total_turns=1,
        final_maturity="orange",
        synthesis_requested=True,
        evaluation_requested=False,
        evaluation_was_eligible=False,
    )
    return {
        "org": org,
        "superadmin": superadmin,
        "orgadmin": orgadmin,
        "group": group,
        "session": session,
    }


@pytest.mark.django_db
def test_conversation_summary_payload(obs_adv_setup):
    summary = build_conversation_summary(
        organisation_id=obs_adv_setup["org"].id,
        group_id=str(obs_adv_setup["group"].id),
    )
    assert summary["schema"] == "conversation_summary_v1"
    assert summary["sessions_count"] == 1
    assert summary["turn_metrics"]["learner_turns_total"] == 1
    assert summary["cta_metrics"]["synthesis_blocked_total"] == 1
    assert summary["cta_metrics"]["evaluation_blocked_total"] == 2
    assert summary["scope"] == "superadmin_technical_only"


@pytest.mark.django_db
def test_conversation_summary_endpoint_superadmin_only(obs_adv_setup):
    client = APIClient()

    client.force_authenticate(user=obs_adv_setup["orgadmin"])
    forbidden = client.get("/internal/hugo/analytics/conversation-summary/")
    assert forbidden.status_code == 403

    client.force_authenticate(user=obs_adv_setup["superadmin"])
    allowed = client.get("/internal/hugo/analytics/conversation-summary/")
    assert allowed.status_code == 200
    assert allowed.data["schema"] == "conversation_summary_v1"
    assert allowed.data["sessions_count"] >= 1


@pytest.mark.django_db
def test_session_observability_still_orgadmin(obs_adv_setup):
    """Observabilité de base v1 reste accessible ORGADMIN (non D9bis)."""
    client = APIClient()
    client.force_authenticate(user=obs_adv_setup["orgadmin"])
    response = client.get(
        f"/internal/hugo/sessions/{obs_adv_setup['session'].id}/observability/"
    )
    assert response.status_code == 200
    assert response.data["schema"] == "session_observability_v1"
