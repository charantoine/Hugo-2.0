from __future__ import annotations

from typing import Any, Optional

from apps.hugo.domain.conversation_profile import ConversationPosture
from apps.hugo.domain.schemas import normalize_conversation_profile

PROFILE_LABELS = {
    ConversationPosture.DIAGNOSTIC.value: "Diagnostic",
    ConversationPosture.REFLECTIVE_AFEST.value: "Réflexif AFEST",
    ConversationPosture.KNOWLEDGE_REVIEW.value: "Savoirs / révision",
}


def conversation_profile_label(profile: str) -> str:
    normalized = normalize_conversation_profile(profile)
    return PROFILE_LABELS.get(normalized, PROFILE_LABELS[ConversationPosture.REFLECTIVE_AFEST.value])


def resolve_conversation_profile(
    *,
    session: Any,
    tutor_prompt: Optional[Any],
    learner_content: str,
    turn_state: Optional[Any] = None,
    speech_act_result: Optional[Any] = None,
) -> str:
    override = normalize_conversation_profile(getattr(session, "conversation_profile_override", ""))
    if getattr(session, "conversation_profile_override", None):
        return override

    prompt_profile = normalize_conversation_profile(getattr(tutor_prompt, "conversation_profile", ""))
    if getattr(tutor_prompt, "conversation_profile", None):
        return prompt_profile

    speech_act = str(getattr(speech_act_result, "learner_speech_act", "") or "").strip().lower()
    text = str(learner_content or "").lower()
    if speech_act in {"ask_help", "ask_priority", "signal_confusion"}:
        return ConversationPosture.DIAGNOSTIC.value
    if any(token in text for token in ["cours", "révision", "revision", "methode", "méthode", "règle", "regle", "savoir"]):
        return ConversationPosture.KNOWLEDGE_REVIEW.value
    if turn_state and (
        getattr(turn_state, "episode_clarity", "") == "low"
        or getattr(turn_state, "learner_help_request", "") == "explicit"
    ):
        return ConversationPosture.DIAGNOSTIC.value
    return ConversationPosture.REFLECTIVE_AFEST.value
