from __future__ import annotations

from typing import TYPE_CHECKING

from apps.hugo.domain.conversation_profile import ConversationPosture
from apps.hugo.models import LearnerConversationGlobalProfile, TutorPrompt

if TYPE_CHECKING:
    from apps.hugo.models import HugoSession, TutorConductProfile


def resolve_learner_conversation_global_profile(session) -> LearnerConversationGlobalProfile | None:
    """
    Resolve the active global learner profile for a session.

    Priority:
    - explicit session.learner_conversation_profile (active status),
    - group.default_learner_conversation_profile (active status),
    - organisation default profile (is_default=True, active status).
    """
    explicit = getattr(session, "learner_conversation_profile", None)
    if explicit is not None and explicit.status == LearnerConversationGlobalProfile.Status.ACTIVE:
        return explicit

    group = getattr(session, "group", None)
    group_profile = getattr(group, "default_learner_conversation_profile", None) if group else None
    if group_profile is not None and group_profile.status == LearnerConversationGlobalProfile.Status.ACTIVE:
        return group_profile

    org_id = getattr(session, "organisation_id", None)
    if org_id:
        org_default = (
            LearnerConversationGlobalProfile.objects.filter(
                organisation_id=org_id,
                is_default=True,
                status=LearnerConversationGlobalProfile.Status.ACTIVE,
            )
            .order_by("-updated_at")
            .first()
        )
        if org_default is not None:
            return org_default
    return None


def resolve_tutor_prompt_from_global_profile(
    session,
    posture: str | ConversationPosture | None = None,
) -> TutorPrompt | None:
    profile = resolve_learner_conversation_global_profile(session)
    if profile is None:
        return None
    posture_value = posture.value if isinstance(posture, ConversationPosture) else str(posture or "")
    if not posture_value:
        posture_value = (
            getattr(session, "posture", None)
            or getattr(session, "conversation_profile_override", None)
            or ConversationPosture.REFLECTIVE_AFEST.value
        )
    return profile.get_tutor_prompt_for_posture(posture_value)


def resolve_conduct_profile_from_global_profile(
    session,
    posture: str | ConversationPosture,
) -> TutorConductProfile | None:
    profile = resolve_learner_conversation_global_profile(session)
    if profile is None:
        return None
    posture_value = posture.value if isinstance(posture, ConversationPosture) else str(posture)
    return profile.get_conduct_profile_for_posture(posture_value)


def resolve_evaluation_profile_code(session, *, policy_code: str, is_early_trigger: bool) -> str:
    """
    Prefer evaluation prompt profile code from global learner profile when set.
    Falls back to policy / early-trigger logic unchanged.
    """
    profile = resolve_learner_conversation_global_profile(session)
    if profile is not None and profile.evaluation_prompt_profile_id:
        code = str(profile.evaluation_prompt_profile.code or "").strip()
        if code:
            return code
    if policy_code:
        return policy_code
    return "early_trigger" if is_early_trigger else "default"
