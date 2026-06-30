"""Tests for evaluation config admin API (Phase 1 Super Admin alignment)."""
import pytest
from rest_framework.test import APIClient

from apps.accounts.models import Role
from apps.hugo.models import EvaluationPolicy, EvaluationPromptProfile


@pytest.fixture
def admin_client(api_client, organisation):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    admin = User.objects.create_user(
        username="eval_admin",
        email="eval_admin@test.local",
        password="pass",
        organisation=organisation,
        role=Role.ORGADMIN,
        is_staff=True,
    )
    api_client.force_authenticate(user=admin)
    return api_client, admin


def test_evaluation_prompt_profile_crud(admin_client, organisation):
    client, admin = admin_client
    create_resp = client.post(
        "/hugo/evaluation-prompt-profiles/",
        {
            "code": "default",
            "label": "Profil default org",
            "is_active": True,
            "prompt_frame": "Frame test",
            "prompt_judgement_guide": "Guide test",
            "prompt_output_guide": "Output test",
            "max_dialogue_turns": 6,
            "ask_learner_confirmation": True,
            "human_validation_required": True,
        },
        format="json",
    )
    assert create_resp.status_code == 201, create_resp.content
    profile_id = create_resp.data["id"]
    assert EvaluationPromptProfile.objects.filter(id=profile_id, organisation=organisation).exists()

    list_resp = client.get("/hugo/evaluation-prompt-profiles/")
    assert list_resp.status_code == 200
    codes = [item["code"] for item in list_resp.data]
    assert "default" in codes

    patch_resp = client.patch(
        f"/hugo/evaluation-prompt-profiles/{profile_id}/",
        {"label": "Profil mis à jour"},
        format="json",
    )
    assert patch_resp.status_code == 200
    assert patch_resp.data["label"] == "Profil mis à jour"
    assert patch_resp.data["updated_by"] == admin.username


def test_evaluation_policy_crud(admin_client, organisation):
    client, _admin = admin_client
    create_resp = client.post(
        "/hugo/evaluation-policies/",
        {
            "share_with_tutor": True,
            "tutor_validation_required": False,
            "allow_early_trigger": True,
            "early_trigger_warning": "Évaluation partielle.",
            "trainer_directives": "",
            "evaluation_profile_code": "default",
        },
        format="json",
    )
    assert create_resp.status_code == 201, create_resp.content
    policy_id = create_resp.data["id"]
    assert EvaluationPolicy.objects.filter(id=policy_id, organisation=organisation).exists()

    get_resp = client.get(f"/hugo/evaluation-policies/{policy_id}/")
    assert get_resp.status_code == 200
    assert get_resp.data["evaluation_profile_code"] == "default"


def test_evaluation_config_requires_orgadmin(api_client, learner_user):
    api_client.force_authenticate(user=learner_user)
    resp = api_client.get("/hugo/evaluation-prompt-profiles/")
    assert resp.status_code == 403
