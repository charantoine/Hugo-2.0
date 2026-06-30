from __future__ import annotations

import logging

from apps.hugo.models import HugoSession, LearnerConversationGlobalProfile

logger = logging.getLogger(__name__)


def apply_session_profile_defaults(
    *,
    validated_data: dict,
    organisation_id,
    tutor_prompt_deprecated: bool = False,
) -> dict:
    """
    Resolve learner_conversation_profile on session create.

    Priority for explicit profile on create:
    - payload learner_conversation_profile
    - group.default_learner_conversation_profile (if active)
    """
    group = validated_data.get("group")
    profile = validated_data.get("learner_conversation_profile")

    if profile is None and group is not None:
        group_default = getattr(group, "default_learner_conversation_profile", None)
        if (
            group_default is not None
            and group_default.status == LearnerConversationGlobalProfile.Status.ACTIVE
        ):
            profile = group_default
            validated_data["learner_conversation_profile"] = profile

    if tutor_prompt_deprecated and validated_data.get("tutor_prompt") is not None:
        if profile is not None:
            logger.warning(
                "deprecated_tutor_prompt_id_ignored session will use learner_conversation_profile=%s",
                profile.id,
            )
            validated_data.pop("tutor_prompt", None)
        else:
            logger.warning("deprecated_tutor_prompt_id_on_session_create")

    if profile is not None:
        if profile.status != LearnerConversationGlobalProfile.Status.ACTIVE:
            raise ValueError("inactive_learner_conversation_profile")
        if organisation_id and str(profile.organisation_id) != str(organisation_id):
            raise ValueError("profile_org_mismatch")

    return validated_data
