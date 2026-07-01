"""Seed profil persona formateur par défaut (baseline B)."""
from __future__ import annotations

from apps.hugo.models import PersonaConversationProfile, TutorPrompt

TRAINER_DEFAULT_CODE = "trainer_chat_default"

TRAINER_DEFAULT_TEMPLATES = {
    "name": "Formateur — chat métier",
    "system_template": (
        "Tu accompagnes un formateur dans un échange métier (explicitation, arbitrage, gouvernance documentaire). "
        "Tu ne parles pas à l'apprenant. "
        "Reste factuel, cite les sources disponibles, propose des formulations structurées.\n"
        "Contexte : {persona_context_block}\n"
        "{referential_block}"
    ),
    "user_template": "Situation ou question :\n{situation_content}",
}


def ensure_trainer_persona_profile(organisation) -> PersonaConversationProfile:
    prompt, _ = TutorPrompt.objects.update_or_create(
        organisation=organisation,
        prompt_type=TutorPrompt.PromptType.AFEST_HUGO,
        code=TRAINER_DEFAULT_CODE,
        defaults={
            "name": TRAINER_DEFAULT_TEMPLATES["name"],
            "system_template": TRAINER_DEFAULT_TEMPLATES["system_template"],
            "user_template": TRAINER_DEFAULT_TEMPLATES["user_template"],
            "persona_scope": TutorPrompt.PersonaScope.TRAINER,
            "is_default": True,
            "is_active": True,
        },
    )
    profile, _ = PersonaConversationProfile.objects.update_or_create(
        organisation=organisation,
        persona=PersonaConversationProfile.Persona.TRAINER,
        code=TRAINER_DEFAULT_CODE,
        defaults={
            "name": TRAINER_DEFAULT_TEMPLATES["name"],
            "description": "Profil chat formateur par défaut",
            "status": PersonaConversationProfile.Status.ACTIVE,
            "is_default": True,
            "tutor_prompt": prompt,
        },
    )
    return profile
