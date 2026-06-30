"""Tests for learner_conversation_profile on HugoSession API (PR-B1)."""
import pytest
from rest_framework import status

from apps.hugo.domain.conversation_profile import ConversationPosture
from apps.hugo.models import HugoSession, LearnerConversationGlobalProfile, TutorPrompt
from apps.referentials.models import GroupMembership


@pytest.fixture
def learner_client(api_client, learner_user, group, organisation):
    GroupMembership.objects.get_or_create(
        organisation=organisation,
        group=group,
        user=learner_user,
    )
    api_client.force_authenticate(user=learner_user)
    return api_client


@pytest.fixture
def session(db, organisation, group, learner_user):
    return HugoSession.objects.create(
        organisation=organisation,
        group=group,
        learner=learner_user,
    )


@pytest.fixture
def active_profile(organisation, reflective_prompt):
    return LearnerConversationGlobalProfile.objects.create(
        organisation=organisation,
        name="Profil actif test",
        status=LearnerConversationGlobalProfile.Status.ACTIVE,
        is_default=True,
        reflective_tutor_prompt=reflective_prompt,
    )


@pytest.fixture
def reflective_prompt(organisation):
    return TutorPrompt.objects.create(
        organisation=organisation,
        code="refl-api",
        name="Refl API",
        system_template="sys",
        user_template="usr",
        conversation_profile=ConversationPosture.REFLECTIVE_AFEST.value,
        is_active=True,
    )


@pytest.mark.django_db
def test_session_create_inherits_group_default_profile(learner_client, group, active_profile):
    group.default_learner_conversation_profile = active_profile
    group.save(update_fields=["default_learner_conversation_profile"])

    response = learner_client.post("/hugo/sessions/", {"group": str(group.id)}, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["learner_conversation_profile"]["id"] == str(active_profile.id)
    assert data["resolved_conversation_profile_id"] == str(active_profile.id)


@pytest.mark.django_db
def test_session_create_explicit_profile_id(learner_client, group, active_profile):
    response = learner_client.post(
        "/hugo/sessions/",
        {
            "group": str(group.id),
            "learner_conversation_profile_id": str(active_profile.id),
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["learner_conversation_profile"]["id"] == str(active_profile.id)


@pytest.mark.django_db
def test_session_create_rejects_inactive_profile(learner_client, group, organisation, reflective_prompt):
    draft = LearnerConversationGlobalProfile.objects.create(
        organisation=organisation,
        name="Draft",
        status=LearnerConversationGlobalProfile.Status.DRAFT,
        reflective_tutor_prompt=reflective_prompt,
    )
    response = learner_client.post(
        "/hugo/sessions/",
        {
            "group": str(group.id),
            "learner_conversation_profile_id": str(draft.id),
        },
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_session_create_tutor_prompt_deprecated_when_profile_set(
    learner_client, group, active_profile, reflective_prompt
):
    group.default_learner_conversation_profile = active_profile
    group.save(update_fields=["default_learner_conversation_profile"])

    response = learner_client.post(
        "/hugo/sessions/",
        {
            "group": str(group.id),
            "tutor_prompt_id": str(reflective_prompt.id),
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["learner_conversation_profile"]["id"] == str(active_profile.id)
    assert data["tutor_prompt"] is None
    assert "deprecated_tutor_prompt_id_ignored" in (data.get("deprecation_warnings") or [])

    session = HugoSession.objects.get(id=data["id"])
    assert session.tutor_prompt_id is None
    assert session.learner_conversation_profile_id == active_profile.id


@pytest.mark.django_db
def test_session_get_exposes_legacy_tutor_prompt(learner_client, session, reflective_prompt):
    session.tutor_prompt = reflective_prompt
    session.save(update_fields=["tutor_prompt"])

    response = learner_client.get(f"/hugo/sessions/{session.id}/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["tutor_prompt"]["code"] == reflective_prompt.code
    assert data.get("learner_conversation_profile") is None
