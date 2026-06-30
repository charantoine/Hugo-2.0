from __future__ import annotations

from typing import Any

EVALUATION_PROFILES_STATIC: dict[str, dict[str, Any]] = {
    "default": {
        "name": "default",
        "max_dialogue_turns": 6,
        "prompt_frame": (
            "Tu es en phase d'évaluation réflexive avec l'apprenant. "
            "Tu l'aides à se positionner par rapport aux critères abordés, sans exposer de logique interne."
        ),
        "prompt_judgement_guide": (
            "Pour chaque critère, classe les indices en not_covered, partial, demonstrated ou mastered. "
            "Reste prudent si la conversation ne contient qu'un indice partiel."
        ),
        "prompt_output_guide": (
            "Retourne un JSON avec recap_text, overall_status et items. "
            "Chaque item doit contenir target_item_id, label, positioning_level, evidence_basis, confidence, "
            "missing_evidence, learner_self_position et status."
        ),
        "ask_learner_confirmation": True,
        "human_validation_required": True,
    },
    "early_trigger": {
        "name": "early_trigger",
        "max_dialogue_turns": 4,
        "prompt_frame": (
            "L'apprenant a déclenché l'évaluation avant la maturité recommandée. "
            "L'évaluation sera partielle et doit l'expliciter clairement."
        ),
        "prompt_judgement_guide": (
            "N'invente pas de maîtrise. Si un point n'est pas couvert, marque-le not_covered."
        ),
        "prompt_output_guide": (
            "Retourne un JSON avec overall_status='early_trigger' et un recap_text expliquant que l'évaluation reste partielle."
        ),
        "ask_learner_confirmation": True,
        "human_validation_required": True,
    },
    "diagnostic": {
        "name": "diagnostic",
        "max_dialogue_turns": 5,
        "prompt_frame": (
            "Tu produis une évaluation diagnostique factuelle, non jugeante, orientée vers les points à renforcer."
        ),
        "prompt_judgement_guide": (
            "Sois particulièrement attentif à la compréhension causale, aux procédures et aux transferts possibles."
        ),
        "prompt_output_guide": (
            "Retourne un JSON structuré ; le recap_text doit pointer 2 ou 3 priorités de renforcement."
        ),
        "ask_learner_confirmation": False,
        "human_validation_required": True,
    },
}


def _db_profile_to_dict(db_profile) -> dict[str, Any]:
    return {
        "name": db_profile.code,
        "max_dialogue_turns": db_profile.max_dialogue_turns,
        "prompt_frame": db_profile.prompt_frame,
        "prompt_judgement_guide": db_profile.prompt_judgement_guide,
        "prompt_output_guide": db_profile.prompt_output_guide,
        "ask_learner_confirmation": db_profile.ask_learner_confirmation,
        "human_validation_required": db_profile.human_validation_required,
    }


def get_evaluation_profile(organisation=None, code: str = "default", is_early_trigger: bool = False) -> dict[str, Any]:
    from apps.hugo.models import EvaluationPromptProfile

    effective_code = str(code or "").strip() or ("early_trigger" if is_early_trigger else "default")
    organisation_id = getattr(organisation, "id", organisation)

    if organisation_id:
        db_profile = (
            EvaluationPromptProfile.objects.filter(
                organisation_id=organisation_id,
                code=effective_code,
                is_active=True,
            )
            .order_by("-updated_at")
            .first()
        )
        if db_profile is not None:
            return _db_profile_to_dict(db_profile)

    db_profile = (
        EvaluationPromptProfile.objects.filter(
            organisation__isnull=True,
            code=effective_code,
            is_active=True,
        )
        .order_by("-updated_at")
        .first()
    )
    if db_profile is not None:
        return _db_profile_to_dict(db_profile)

    return EVALUATION_PROFILES_STATIC.get(effective_code, EVALUATION_PROFILES_STATIC["default"])
