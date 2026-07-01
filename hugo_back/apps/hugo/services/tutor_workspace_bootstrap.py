"""Données seed pour les profils espace tuteur P1 (baseline B)."""
from __future__ import annotations

from apps.hugo.domain.conversation_profile import ConversationPosture
from apps.hugo.models import LearnerConversationGlobalProfile, TutorConductProfile, TutorPrompt, PersonaConversationProfile

TUTOR_WORKSPACE_PROFILE_CODES = (
    "tutor_workspace_prep",
    "tutor_workspace_diagnostic",
    "tutor_workspace_coreflex",
    "tutor_workspace_journal",
)

PROFILE_PRIMARY_POSTURE = {
    "tutor_workspace_prep": ConversationPosture.REFLECTIVE_AFEST.value,
    "tutor_workspace_diagnostic": ConversationPosture.DIAGNOSTIC.value,
    "tutor_workspace_coreflex": ConversationPosture.REFLECTIVE_AFEST.value,
    "tutor_workspace_journal": ConversationPosture.KNOWLEDGE_REVIEW.value,
}

PROMPT_SPECS = {
    "tutor_workspace_prep": {
        "name": "Tuteur — Préparer l'entretien",
        "posture": ConversationPosture.REFLECTIVE_AFEST.value,
        "max_questions": 2,
        "system_template": (
            "Tu aides un tuteur professionnel à se préparer AVANT un entretien avec un apprenant. "
            "Tu ne parles jamais à l'apprenant. "
            "Avant toute piste, invite le tuteur à dire ce qu'il a déjà observé. "
            "Formule des hypothèses prudentes, jamais de verdict. "
            "Termine par une prochaine étape concrète.\n"
            "Contexte : {tutor_context_block}\n"
            "{referential_block}"
        ),
        "user_template": "Situation à préparer :\n{situation_content}",
    },
    "tutor_workspace_diagnostic": {
        "name": "Tuteur — Diagnostic prudent",
        "posture": ConversationPosture.DIAGNOSTIC.value,
        "max_questions": 3,
        "system_template": (
            "Tu aides un tuteur à formuler des hypothèses sur une difficulté apprenante, "
            "sans poser de diagnostic définitif. "
            "Distingue compréhension, conceptualisation et engagement. "
            "N'utilise pas de verbatim non partagé. "
            "Propose des questions de confirmation.\n"
            "Contexte : {tutor_context_block}\n"
            "{referential_block}"
        ),
        "user_template": "Signaux ou situation :\n{situation_content}",
    },
    "tutor_workspace_coreflex": {
        "name": "Tuteur — Co-réflexion assistée",
        "posture": ConversationPosture.REFLECTIVE_AFEST.value,
        "max_questions": 3,
        "system_template": (
            "Tu proposes au tuteur des questions ouvertes, reformulations et relances "
            "qu'il pourra utiliser avec l'apprenant plus tard. "
            "Tu ne te substitues pas au tuteur et ne rédiges pas le dialogue apprenant. "
            "Favorise l'autonomie de l'apprenant.\n"
            "Contexte : {tutor_context_block}\n"
            "{referential_block}"
        ),
        "user_template": "Besoin d'accompagnement :\n{situation_content}",
    },
    "tutor_workspace_journal": {
        "name": "Tuteur — Journal de séance",
        "posture": ConversationPosture.KNOWLEDGE_REVIEW.value,
        "max_questions": 1,
        "system_template": (
            "Tu aides un tuteur à rédiger une synthèse structurée et non jugeante "
            "d'un point de suivi ou d'une séance. "
            "Pas de verdict certificatif. "
            "Structure : faits observables, interprétation prudente, suites.\n"
            "Contexte : {tutor_context_block}\n"
            "{referential_block}"
        ),
        "user_template": "Éléments à synthétiser :\n{situation_content}",
    },
}

CONDUCT_SPECS = {
    ConversationPosture.REFLECTIVE_AFEST.value: {
        "description": "Conduite espace tuteur — réflexif",
        "max_questions_per_turn": 3,
        "forbidden_moves": [
            "prescrire_conduite_apprenant",
            "verdict_competence",
            "reponse_directe_apprenant",
            "citer_verbatim_non_partage",
        ],
        "closure_policy": "open_next_step",
    },
    ConversationPosture.DIAGNOSTIC.value: {
        "description": "Conduite espace tuteur — diagnostic",
        "max_questions_per_turn": 3,
        "forbidden_moves": [
            "verdict",
            "label_pathologique",
            "citer_verbatim_non_partage",
        ],
        "closure_policy": "hypothesis_check",
    },
    ConversationPosture.KNOWLEDGE_REVIEW.value: {
        "description": "Conduite espace tuteur — documentation",
        "max_questions_per_turn": 1,
        "forbidden_moves": [
            "jugement_moral",
            "partage_auto_apprenant",
            "verbatim_brut",
        ],
        "closure_policy": "summarize_actions",
    },
}


def ensure_tutor_workspace_profiles(organisation) -> dict[str, LearnerConversationGlobalProfile]:
    """Crée ou met à jour les 4 profils globaux tuteur P1 pour une organisation."""
    conduct_by_posture: dict[str, TutorConductProfile] = {}
    for posture, spec in CONDUCT_SPECS.items():
        conduct, _ = TutorConductProfile.objects.update_or_create(
            organisation=organisation,
            posture=posture,
            defaults={
                "system_template": f"Conduite tuteur workspace ({posture})",
                "user_template": "",
                "description": spec["description"],
                "max_questions_per_turn": spec["max_questions_per_turn"],
                "forbidden_moves": spec["forbidden_moves"],
                "closure_policy": spec["closure_policy"],
                "is_active": True,
            },
        )
        conduct_by_posture[posture] = conduct

    prompts: dict[str, TutorPrompt] = {}
    for code, spec in PROMPT_SPECS.items():
        prompt, _ = TutorPrompt.objects.update_or_create(
            organisation=organisation,
            code=code,
            defaults={
                "name": spec["name"],
                "system_template": spec["system_template"],
                "user_template": spec["user_template"],
                "conversation_profile": spec["posture"],
                "max_questions_per_turn": spec["max_questions"],
                "persona_scope": TutorPrompt.PersonaScope.TUTOR,
                "is_active": True,
            },
        )
        prompts[code] = prompt

    from apps.hugo.models import PersonaConversationProfile

    profiles: dict[str, LearnerConversationGlobalProfile] = {}
    for code in TUTOR_WORKSPACE_PROFILE_CODES:
        primary_posture = PROFILE_PRIMARY_POSTURE[code]
        prompt = prompts[code]
        conduct = conduct_by_posture[primary_posture]
        slot_prompt = {
            ConversationPosture.DIAGNOSTIC.value: "diagnostic_tutor_prompt",
            ConversationPosture.REFLECTIVE_AFEST.value: "reflective_tutor_prompt",
            ConversationPosture.KNOWLEDGE_REVIEW.value: "knowledge_review_tutor_prompt",
        }[primary_posture]
        slot_conduct = {
            ConversationPosture.DIAGNOSTIC.value: "diagnostic_conduct_profile",
            ConversationPosture.REFLECTIVE_AFEST.value: "reflective_conduct_profile",
            ConversationPosture.KNOWLEDGE_REVIEW.value: "knowledge_review_conduct_profile",
        }[primary_posture]
        profile, _ = LearnerConversationGlobalProfile.objects.update_or_create(
            organisation=organisation,
            name=code,
            defaults={
                "description": PROMPT_SPECS[code]["name"],
                "status": LearnerConversationGlobalProfile.Status.ACTIVE,
                "is_default": False,
                slot_prompt: prompt,
                slot_conduct: conduct,
            },
        )
        profiles[code] = profile

        PersonaConversationProfile.objects.update_or_create(
            organisation=organisation,
            persona=PersonaConversationProfile.Persona.TUTOR,
            code=code,
            defaults={
                "name": PROMPT_SPECS[code]["name"],
                "description": PROMPT_SPECS[code]["name"],
                "status": PersonaConversationProfile.Status.ACTIVE,
                "is_default": code == "tutor_workspace_prep",
                "tutor_prompt": prompt,
            },
        )

    return profiles
