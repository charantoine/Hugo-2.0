from __future__ import annotations

from typing import Any

from apps.hugo.models import LearnerConversationGlobalProfile, TutorConductProfile, TutorPrompt

POSTURE_SLOTS: tuple[tuple[str, str, str, str], ...] = (
    ("diagnostic", "diagnostic_tutor_prompt", "diagnostic_conduct_profile", "Diagnostic"),
    ("reflective_afest", "reflective_tutor_prompt", "reflective_conduct_profile", "Réflexif"),
    ("knowledge_review", "knowledge_review_tutor_prompt", "knowledge_review_conduct_profile", "Bûchage"),
)


def _is_active_prompt(prompt: TutorPrompt | None) -> bool:
    return prompt is not None and bool(prompt.is_active)


def _is_active_conduct(profile: TutorConductProfile | None) -> bool:
    return profile is not None and bool(profile.is_active)


def compute_profile_completeness(profile: LearnerConversationGlobalProfile) -> dict[str, Any]:
    """
    Summarise how complete a global learner profile is for admin / learner surfaces.

    Scoring (7 parts): 3 posture prompts + 3 posture conduct + 1 evaluation bundle.
    Evaluation counts as filled when evaluation_prompt_profile OR evaluation_policy is set.
    """
    missing_slots: list[str] = []
    warnings: list[str] = []
    filled = 0
    total = 7

    for _posture, prompt_field, conduct_field, label in POSTURE_SLOTS:
        prompt = getattr(profile, prompt_field, None)
        conduct = getattr(profile, conduct_field, None)
        if _is_active_prompt(prompt):
            filled += 1
        else:
            missing_slots.append(prompt_field)
        if _is_active_conduct(conduct):
            filled += 1
        else:
            warnings.append(f"{label} : profil de conduite absent (repli org / système).")
        if prompt is not None and not prompt.is_active:
            warnings.append(f"{label} : TutorPrompt lié mais inactif.")
        if conduct is not None and not conduct.is_active:
            warnings.append(f"{label} : profil de conduite lié mais inactif.")

    eval_prompt = getattr(profile, "evaluation_prompt_profile", None)
    eval_policy = getattr(profile, "evaluation_policy", None)
    if eval_prompt is not None or eval_policy is not None:
        filled += 1
    else:
        missing_slots.append("evaluation")
        warnings.append("Évaluation : aucun profil ni politique org liée (repli get_or_create).")

    score = round(filled / total, 2) if total else 0.0
    return {
        "filled": filled,
        "total": total,
        "score": score,
        "missing_slots": missing_slots,
        "warnings": warnings,
    }
