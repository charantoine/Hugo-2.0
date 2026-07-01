"""Résolution persona tuteur/formateur — hors chemin apprenant."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from apps.accounts.models import Role
from apps.hugo.models import LearnerConversationGlobalProfile, PersonaConversationProfile, TutorPrompt
from apps.hugo.services.tutor_workspace_bootstrap import TUTOR_WORKSPACE_PROFILE_CODES

if TYPE_CHECKING:
    from apps.hugo.models import HugoSession


def resolve_session_persona(session) -> Optional[str]:
    """
    Retourne 'tutor', 'trainer' ou None (mode apprenant classique).

    Ne modifie pas les résolveurs apprenant ; détection additive uniquement.
    """
    explicit = getattr(session, "persona_conversation_profile", None)
    if explicit is not None and explicit.status == PersonaConversationProfile.Status.ACTIVE:
        return str(explicit.persona)

    learner_profile = getattr(session, "learner_conversation_profile", None)
    if (
        learner_profile is not None
        and learner_profile.status == LearnerConversationGlobalProfile.Status.ACTIVE
        and learner_profile.name in TUTOR_WORKSPACE_PROFILE_CODES
    ):
        return PersonaConversationProfile.Persona.TUTOR

    learner = getattr(session, "learner", None)
    role = getattr(learner, "role", None)
    if role == Role.TRAINER:
        if learner_profile is None or learner_profile.name in TUTOR_WORKSPACE_PROFILE_CODES:
            return PersonaConversationProfile.Persona.TRAINER
    return None


def is_persona_session(session) -> bool:
    return resolve_session_persona(session) is not None


def resolve_persona_prompt_for_session(session, posture: str | None = None) -> Optional[TutorPrompt]:
    """Résout le TutorPrompt pour une session persona. Retourne None si session apprenant."""
    persona = resolve_session_persona(session)
    if not persona:
        return None

    explicit = getattr(session, "persona_conversation_profile", None)
    if explicit is not None and explicit.status == PersonaConversationProfile.Status.ACTIVE:
        prompt = explicit.tutor_prompt
        if prompt is not None and prompt.is_active:
            return prompt

    if persona == PersonaConversationProfile.Persona.TUTOR:
        from apps.hugo.services.learner_profile_resolver import resolve_tutor_prompt_from_global_profile

        legacy = resolve_tutor_prompt_from_global_profile(session, posture)
        if legacy is not None:
            return legacy

    scope = TutorPrompt.PersonaScope.TUTOR if persona == PersonaConversationProfile.Persona.TUTOR else TutorPrompt.PersonaScope.TRAINER
    org_id = getattr(session, "organisation_id", None)
    if not org_id:
        return None
    default = (
        TutorPrompt.objects.filter(
            organisation_id=org_id,
            persona_scope=scope,
            is_active=True,
            is_default=True,
        )
        .order_by("created_at")
        .first()
    )
    if default is not None:
        return default
    return (
        TutorPrompt.objects.filter(
            organisation_id=org_id,
            persona_scope=scope,
            is_active=True,
        )
        .order_by("created_at")
        .first()
    )


def build_persona_context_block(session, persona: str) -> str:
    """Bloc texte injecté dans {tutor_context_block} / {persona_context_block}."""
    lines = [f"Mode conversation : {persona}"]
    learner = getattr(session, "learner", None)
    if learner is not None:
        lines.append(f"Interlocuteur : {getattr(learner, 'username', '')} ({getattr(learner, 'role', '')})")
    group = getattr(session, "group", None)
    if group is not None:
        lines.append(f"Groupe : {getattr(group, 'name', '')}")
    profile = getattr(session, "persona_conversation_profile", None)
    if profile is not None:
        lines.append(f"Profil persona : {profile.name} ({profile.code})")
    legacy = getattr(session, "learner_conversation_profile", None)
    if legacy is not None and legacy.name in TUTOR_WORKSPACE_PROFILE_CODES:
        lines.append(f"Profil workspace (legacy) : {legacy.name}")
    return "\n".join(lines)
