"""Tests for LearnerConversationGlobalProfile completeness (PR-B3)."""
import pytest
from rest_framework import status

from apps.accounts.models import Role
from apps.hugo.domain.conversation_profile import ConversationPosture
from apps.hugo.models import LearnerConversationGlobalProfile, TutorPrompt


@pytest.fixture
def admin_client(api_client, organisation):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    admin = User.objects.create_user(
        username="completeness_admin",
        email="completeness_admin@test.local",
        password="pass",
        organisation=organisation,
        role=Role.ORGADMIN,
        is_staff=True,
    )
    api_client.force_authenticate(user=admin)
    return api_client


@pytest.fixture
def diagnostic_prompt(organisation):
    return TutorPrompt.objects.create(
        organisation=organisation,
        code="diag-comp",
        name="Diag",
        system_template="sys",
        user_template="usr",
        conversation_profile=ConversationPosture.DIAGNOSTIC.value,
        is_active=True,
    )


@pytest.fixture
def reflective_prompt(organisation):
    return TutorPrompt.objects.create(
        organisation=organisation,
        code="refl-comp",
        name="Refl",
        system_template="sys",
        user_template="usr",
        conversation_profile=ConversationPosture.REFLECTIVE_AFEST.value,
        is_active=True,
    )


@pytest.fixture
def global_profile(organisation, diagnostic_prompt, reflective_prompt):
    return LearnerConversationGlobalProfile.objects.create(
        organisation=organisation,
        name="Profil completude",
        status=LearnerConversationGlobalProfile.Status.ACTIVE,
        diagnostic_tutor_prompt=diagnostic_prompt,
        reflective_tutor_prompt=reflective_prompt,
    )


@pytest.mark.django_db
def test_profile_completeness_empty(global_profile):
    from apps.hugo.services.profile_completeness import compute_profile_completeness

    payload = compute_profile_completeness(global_profile)
    assert payload["total"] == 7
    assert payload["filled"] >= 2
    assert "score" in payload
    assert isinstance(payload["missing_slots"], list)
    assert isinstance(payload["warnings"], list)


@pytest.mark.django_db
def test_profile_completeness_api_list(admin_client, global_profile):
    response = admin_client.get("/hugo/learner-conversation-profiles/")
    assert response.status_code == status.HTTP_200_OK
    row = next(item for item in response.json() if item["id"] == str(global_profile.id))
    assert "completeness" in row
    assert row["completeness"]["total"] == 7
    assert "missing_slots" in row
    assert "warnings" in row
