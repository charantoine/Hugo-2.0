from __future__ import annotations

from typing import Any

from apps.hugo.domain.conversation_profile import ConversationPosture
from apps.hugo.models import EvaluationPromptProfile, TutorConductProfile, TutorPrompt

POSTURE_SLOTS = (
    ("diagnostic", ConversationPosture.DIAGNOSTIC.value),
    ("reflective", ConversationPosture.REFLECTIVE_AFEST.value),
    ("knowledge_review", ConversationPosture.KNOWLEDGE_REVIEW.value),
)


def _pick_tutor_prompt(organisation_id, posture: str) -> TutorPrompt | None:
    return (
        TutorPrompt.objects.filter(
            organisation_id=organisation_id,
            conversation_profile=posture,
            is_active=True,
        )
        .order_by("-is_default", "-updated_at")
        .first()
    )


def _pick_conduct_profile(organisation_id, posture: str) -> TutorConductProfile | None:
    return (
        TutorConductProfile.objects.filter(
            organisation_id=organisation_id,
            posture=posture,
            is_active=True,
        )
        .order_by("-updated_at")
        .first()
    )


def _pick_evaluation_prompt_profile(organisation_id) -> EvaluationPromptProfile | None:
    profile = (
        EvaluationPromptProfile.objects.filter(
            organisation_id=organisation_id,
            code="default",
            is_active=True,
        )
        .order_by("-updated_at")
        .first()
    )
    if profile is not None:
        return profile
    return (
        EvaluationPromptProfile.objects.filter(
            organisation_id=organisation_id,
            is_active=True,
        )
        .order_by("-updated_at")
        .first()
    )


def build_legacy_profile_suggestions(organisation_id) -> dict[str, Any]:
    """
    Suggest slot FK values from legacy per-posture configuration for the organisation.
    Does not mutate any data — used to prefill admin create forms.
    """
    suggestions: dict[str, Any] = {
        "name_suggestion": "Profil global (legacy)",
        "description_suggestion": "Assemblé automatiquement à partir des modes conversationnels existants.",
    }
    filled_slots = 0

    for slot_prefix, posture in POSTURE_SLOTS:
        prompt = _pick_tutor_prompt(organisation_id, posture)
        conduct = _pick_conduct_profile(organisation_id, posture)
        prompt_key = f"{slot_prefix}_tutor_prompt_id"
        conduct_key = f"{slot_prefix}_conduct_profile_id"
        suggestions[prompt_key] = str(prompt.id) if prompt else None
        suggestions[conduct_key] = str(conduct.id) if conduct else None
        if prompt or conduct:
            filled_slots += 1

    eval_profile = _pick_evaluation_prompt_profile(organisation_id)
    suggestions["evaluation_prompt_profile_id"] = str(eval_profile.id) if eval_profile else None
    if eval_profile:
        filled_slots += 1

    suggestions["filled_slots"] = filled_slots
    suggestions["has_legacy_data"] = filled_slots > 0
    return suggestions
