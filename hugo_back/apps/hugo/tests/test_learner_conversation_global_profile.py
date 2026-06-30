"""Tests for LearnerConversationGlobalProfile model, API and runtime resolution."""
import pytest
from rest_framework import status

from apps.accounts.models import Role
from apps.hugo.domain.conversation_profile import ConversationPosture
from apps.hugo.models import (
    EvaluationPromptProfile,
    HugoSession,
    LearnerConversationGlobalProfile,
    TutorConductProfile,
    TutorPrompt,
)
from apps.hugo.services.context_builder import _resolve_tutor_prompt
from apps.hugo.services.conduct_profile_resolver import resolve_conduct_profile
from apps.hugo.services.learner_profile_resolver import (
    resolve_evaluation_profile_code,
    resolve_learner_conversation_global_profile,
)


@pytest.fixture
def admin_client(api_client, organisation):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    admin = User.objects.create_user(
        username="learner_profile_admin",
        email="learner_profile_admin@test.local",
        password="pass",
        organisation=organisation,
        role=Role.ORGADMIN,
        is_staff=True,
    )
    api_client.force_authenticate(user=admin)
    return api_client


@pytest.fixture
def session(db, organisation, group, learner_user):
    return HugoSession.objects.create(
        organisation=organisation,
        group=group,
        learner=learner_user,
    )


@pytest.fixture
def diagnostic_prompt(organisation):
    return TutorPrompt.objects.create(
        organisation=organisation,
        code="diag-prompt",
        name="Diag prompt",
        system_template="sys diag",
        user_template="user diag",
        conversation_profile=ConversationPosture.DIAGNOSTIC.value,
        is_active=True,
    )


@pytest.fixture
def reflective_prompt(organisation):
    return TutorPrompt.objects.create(
        organisation=organisation,
        code="refl-prompt",
        name="Refl prompt",
        system_template="sys refl",
        user_template="user refl",
        conversation_profile=ConversationPosture.REFLECTIVE_AFEST.value,
        is_active=True,
    )


@pytest.fixture
def global_profile(organisation, diagnostic_prompt, reflective_prompt):
    return LearnerConversationGlobalProfile.objects.create(
        organisation=organisation,
        name="Profil AFEST standard",
        status=LearnerConversationGlobalProfile.Status.ACTIVE,
        is_default=True,
        diagnostic_tutor_prompt=diagnostic_prompt,
        reflective_tutor_prompt=reflective_prompt,
    )


@pytest.mark.django_db
def test_global_profile_api_crud(admin_client, organisation, diagnostic_prompt):
    create_resp = admin_client.post(
        "/hugo/learner-conversation-profiles/",
        {
            "name": "Mon profil",
            "description": "Test",
            "status": "active",
            "is_default": True,
            "diagnostic_tutor_prompt_id": str(diagnostic_prompt.id),
        },
        format="json",
    )
    assert create_resp.status_code == status.HTTP_201_CREATED, create_resp.content
    profile_id = create_resp.data["id"]
    assert create_resp.data["name"] == "Mon profil"
    assert str(create_resp.data["diagnostic_tutor_prompt"]) == str(diagnostic_prompt.id)

    list_resp = admin_client.get("/hugo/learner-conversation-profiles/")
    assert list_resp.status_code == status.HTTP_200_OK
    assert any(item["id"] == profile_id for item in list_resp.data)

    patch_resp = admin_client.patch(
        f"/hugo/learner-conversation-profiles/{profile_id}/",
        {"description": "Updated"},
        format="json",
    )
    assert patch_resp.status_code == status.HTTP_200_OK
    assert patch_resp.data["description"] == "Updated"

    assert LearnerConversationGlobalProfile.objects.filter(
        organisation=organisation, is_default=True
    ).count() == 1


@pytest.mark.django_db
def test_global_profile_rejects_wrong_posture_prompt(admin_client, organisation, reflective_prompt):
    resp = admin_client.post(
        "/hugo/learner-conversation-profiles/",
        {
            "name": "Bad slot",
            "diagnostic_tutor_prompt_id": str(reflective_prompt.id),
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_resolve_tutor_prompt_from_global_profile(session, global_profile, diagnostic_prompt):
    session.group.default_learner_conversation_profile = global_profile
    session.group.save(update_fields=["default_learner_conversation_profile"])

    resolved = _resolve_tutor_prompt(session, posture=ConversationPosture.DIAGNOSTIC.value)
    assert resolved is not None
    assert resolved.id == diagnostic_prompt.id


@pytest.mark.django_db
def test_resolve_tutor_prompt_legacy_fallback_when_no_global_profile(session, organisation):
    legacy = TutorPrompt.objects.create(
        organisation=organisation,
        code="legacy-default",
        name="Legacy",
        system_template="sys",
        user_template="user",
        is_default=True,
        is_active=True,
    )
    resolved = _resolve_tutor_prompt(session)
    assert resolved is not None
    assert resolved.id == legacy.id


@pytest.mark.django_db
def test_session_explicit_tutor_prompt_overrides_global(session, global_profile, diagnostic_prompt, organisation):
    other = TutorPrompt.objects.create(
        organisation=organisation,
        code="session-override",
        name="Override",
        system_template="sys",
        user_template="user",
        conversation_profile=ConversationPosture.DIAGNOSTIC.value,
        is_active=True,
    )
    session.tutor_prompt = other
    session.learner_conversation_profile = global_profile
    session.save(update_fields=["tutor_prompt", "learner_conversation_profile"])

    resolved = _resolve_tutor_prompt(session, posture=ConversationPosture.DIAGNOSTIC.value)
    assert resolved.id == other.id


@pytest.mark.django_db
def test_resolve_conduct_from_global_profile_slot(session, organisation, global_profile):
    conduct = TutorConductProfile.objects.create(
        organisation=organisation,
        posture=ConversationPosture.DIAGNOSTIC.value,
        system_template="conduct diag custom",
        is_active=True,
    )
    global_profile.diagnostic_conduct_profile = conduct
    global_profile.save(update_fields=["diagnostic_conduct_profile"])
    session.learner_conversation_profile = global_profile
    session.save(update_fields=["learner_conversation_profile"])

    result = resolve_conduct_profile(ConversationPosture.DIAGNOSTIC, organisation, session=session)
    assert "conduct diag custom" in result["system_template"]


@pytest.mark.django_db
def test_resolve_evaluation_profile_code_from_global(session, organisation, global_profile):
    eval_profile = EvaluationPromptProfile.objects.create(
        organisation=organisation,
        code="custom_eval",
        label="Custom",
        prompt_frame="frame",
        prompt_judgement_guide="judge",
        prompt_output_guide="output",
    )
    global_profile.evaluation_prompt_profile = eval_profile
    global_profile.save(update_fields=["evaluation_prompt_profile"])
    session.learner_conversation_profile = global_profile
    session.save(update_fields=["learner_conversation_profile"])

    code = resolve_evaluation_profile_code(session, policy_code="", is_early_trigger=False)
    assert code == "custom_eval"


@pytest.mark.django_db
def test_group_default_learner_profile_cross_org_rejected(db):
    from apps.accounts.models import Organisation, Role, User
    from apps.referentials.models import Group
    from rest_framework.test import APIClient

    org_a = Organisation.objects.create(name="Org iso A")
    org_b = Organisation.objects.create(name="Org iso B")
    orgadmin_a = User.objects.create_user(
        username="orgadmin_iso_a",
        password="testpass",
        organisation=org_a,
        role=Role.ORGADMIN,
    )
    group_a = Group.objects.create(organisation=org_a, name="Group A")
    profile_b = LearnerConversationGlobalProfile.objects.create(
        organisation=org_b,
        name="Profil B",
        status=LearnerConversationGlobalProfile.Status.ACTIVE,
    )
    api_client = APIClient()
    api_client.force_authenticate(user=orgadmin_a)
    resp = api_client.patch(
        f"/groups/{group_a.id}/",
        {"default_learner_conversation_profile": str(profile_b.id)},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_legacy_template_suggests_existing_slots(admin_client, organisation, diagnostic_prompt, reflective_prompt):
    TutorConductProfile.objects.create(
        organisation=organisation,
        posture=ConversationPosture.DIAGNOSTIC.value,
        system_template="conduct diag",
        is_active=True,
    )
    EvaluationPromptProfile.objects.create(
        organisation=organisation,
        code="default",
        label="Default eval",
        prompt_frame="f",
        prompt_judgement_guide="j",
        prompt_output_guide="o",
    )
    resp = admin_client.get("/hugo/learner-conversation-profiles/legacy-template/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["has_legacy_data"] is True
    assert resp.data["diagnostic_tutor_prompt_id"] == str(diagnostic_prompt.id)
    assert resp.data["reflective_tutor_prompt_id"] == str(reflective_prompt.id)
    assert resp.data["evaluation_prompt_profile_id"]


@pytest.mark.django_db
def test_legacy_template_does_not_cross_assign_default_prompt(admin_client, organisation):
    """Default prompt for one posture must not prefill another posture slot."""
    diagnostic_default = TutorPrompt.objects.create(
        organisation=organisation,
        code="diag-mk1",
        name="diagnostic Mk1",
        system_template="sys diag",
        user_template="user diag",
        conversation_profile=ConversationPosture.DIAGNOSTIC.value,
        is_default=True,
        is_active=True,
    )
    resp = admin_client.get("/hugo/learner-conversation-profiles/legacy-template/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["diagnostic_tutor_prompt_id"] == str(diagnostic_default.id)
    assert resp.data["reflective_tutor_prompt_id"] is None
    assert resp.data["knowledge_review_tutor_prompt_id"] is None


@pytest.mark.django_db
def test_create_profile_from_legacy_suggestions(admin_client, organisation, diagnostic_prompt, reflective_prompt):
    reflective_conduct = TutorConductProfile.objects.create(
        organisation=organisation,
        posture=ConversationPosture.REFLECTIVE_AFEST.value,
        system_template="conduct refl",
        is_active=True,
    )
    template = admin_client.get("/hugo/learner-conversation-profiles/legacy-template/").data
    create_resp = admin_client.post(
        "/hugo/learner-conversation-profiles/",
        {
            "name": "Profil assemblé legacy",
            "description": template.get("description_suggestion", ""),
            "status": "active",
            "diagnostic_tutor_prompt_id": template["diagnostic_tutor_prompt_id"],
            "reflective_tutor_prompt_id": template["reflective_tutor_prompt_id"],
            "reflective_conduct_profile_id": str(reflective_conduct.id),
        },
        format="json",
    )
    assert create_resp.status_code == status.HTTP_201_CREATED, create_resp.content
    profile_id = create_resp.data["id"]
    profile = LearnerConversationGlobalProfile.objects.get(id=profile_id)
    assert profile.diagnostic_tutor_prompt_id == diagnostic_prompt.id
    assert profile.reflective_conduct_profile_id == reflective_conduct.id


@pytest.mark.django_db
def test_legacy_template_requires_orgadmin(api_client, learner_user):
    api_client.force_authenticate(user=learner_user)
    resp = api_client.get("/hugo/learner-conversation-profiles/legacy-template/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_resolve_learner_profile_priority_session_over_group(session, global_profile, organisation):
    group_profile = LearnerConversationGlobalProfile.objects.create(
        organisation=organisation,
        name="Group profile",
        status=LearnerConversationGlobalProfile.Status.ACTIVE,
    )
    session_profile = LearnerConversationGlobalProfile.objects.create(
        organisation=organisation,
        name="Session profile",
        status=LearnerConversationGlobalProfile.Status.ACTIVE,
    )
    session.group.default_learner_conversation_profile = group_profile
    session.group.save(update_fields=["default_learner_conversation_profile"])
    session.learner_conversation_profile = session_profile
    session.save(update_fields=["learner_conversation_profile"])

    resolved = resolve_learner_conversation_global_profile(session)
    assert resolved.id == session_profile.id
