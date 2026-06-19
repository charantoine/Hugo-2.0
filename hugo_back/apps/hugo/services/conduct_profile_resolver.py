from __future__ import annotations

from apps.hugo.domain.conversation_profile import ConversationPosture
from apps.hugo.domain.tutor_profiles import get_profile
from apps.hugo.models import TutorConductProfile


def _to_conduct_dict(profile: TutorConductProfile, posture: ConversationPosture) -> dict:
    static = get_profile(posture)
    return {
        "posture": posture.value,
        "system_template": profile.system_template,
        "user_template": profile.user_template or None,
        "max_questions_per_turn": profile.max_questions_per_turn or static["max_questions_per_turn"],
        "forbidden_moves": profile.forbidden_moves or static["forbidden_moves"],
        "allowed_moves": profile.allowed_moves or static["allowed_moves"],
        "closure_policy": profile.closure_policy or static["closure_policy"],
        "description": profile.description or static["description"],
    }


def resolve_conduct_profile(posture: ConversationPosture, organisation=None) -> dict:
    organisation_id = getattr(organisation, "id", organisation)
    if organisation_id:
        profile = (
            TutorConductProfile.objects.filter(
                organisation_id=organisation_id,
                posture=posture.value,
                is_active=True,
            )
            .order_by("-updated_at")
            .first()
        )
        if profile is not None:
            return _to_conduct_dict(profile, posture)

    profile = (
        TutorConductProfile.objects.filter(
            organisation__isnull=True,
            posture=posture.value,
            is_active=True,
        )
        .order_by("-updated_at")
        .first()
    )
    if profile is not None:
        return _to_conduct_dict(profile, posture)

    return get_profile(posture)
