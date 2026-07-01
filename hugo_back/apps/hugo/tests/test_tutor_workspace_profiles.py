"""Tests bootstrap profils espace tuteur P1."""
import pytest

from apps.accounts.models import Organisation
from apps.hugo.domain.conversation_profile import ConversationPosture
from apps.hugo.services.tutor_workspace_bootstrap import (
    PROFILE_PRIMARY_POSTURE,
    TUTOR_WORKSPACE_PROFILE_CODES,
    ensure_tutor_workspace_profiles,
)


@pytest.mark.django_db
def test_ensure_tutor_workspace_profiles_creates_four_active_profiles():
    org = Organisation.objects.create(name="Org Tutor Workspace Test")
    profiles = ensure_tutor_workspace_profiles(org)

    assert set(profiles.keys()) == set(TUTOR_WORKSPACE_PROFILE_CODES)
    for code, profile in profiles.items():
        assert profile.status == "active"
        posture = PROFILE_PRIMARY_POSTURE[code]
        prompt = profile.get_tutor_prompt_for_posture(posture)
        conduct = profile.get_conduct_profile_for_posture(posture)
        assert prompt is not None
        assert prompt.code == code
        assert conduct is not None
        assert conduct.forbidden_moves


@pytest.mark.django_db
def test_tutor_workspace_prep_resolves_reflective_prompt():
    org = Organisation.objects.create(name="Org Tutor Prep")
    profiles = ensure_tutor_workspace_profiles(org)
    profile = profiles["tutor_workspace_prep"]
    prompt = profile.get_tutor_prompt_for_posture(ConversationPosture.REFLECTIVE_AFEST.value)
    assert prompt is not None
    assert "tuteur" in prompt.system_template.lower()


@pytest.mark.django_db
def test_ensure_tutor_workspace_profiles_idempotent():
    org = Organisation.objects.create(name="Org Tutor Idempotent")
    first = ensure_tutor_workspace_profiles(org)
    second = ensure_tutor_workspace_profiles(org)
    for code in TUTOR_WORKSPACE_PROFILE_CODES:
        assert str(first[code].id) == str(second[code].id)
