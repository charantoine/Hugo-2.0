from __future__ import annotations

from typing import Optional

from apps.hugo.domain.conversation_profile import ConversationPosture

DEFAULT_POSTURE = ConversationPosture.REFLECTIVE_AFEST

DIAGNOSTIC_SIGNALS = {"diagnostic", "problème", "probleme", "analyser", "comprendre"}
KNOWLEDGE_SIGNALS = {"réviser", "reviser", "leçon", "lecon", "cours", "apprendre", "mémoriser", "memoriser", "quiz"}


def resolve_posture(session, user_message: str = "", explicit_posture: Optional[str] = None) -> ConversationPosture:
    if explicit_posture:
        try:
            return ConversationPosture(str(explicit_posture).strip().lower())
        except ValueError:
            pass

    stored = getattr(session, "posture", None) or getattr(session, "conversation_profile_override", None)
    if stored:
        try:
            return ConversationPosture(str(stored).strip().lower())
        except ValueError:
            pass

    message = str(user_message or "").lower()
    if any(signal in message for signal in DIAGNOSTIC_SIGNALS):
        return ConversationPosture.DIAGNOSTIC
    if any(signal in message for signal in KNOWLEDGE_SIGNALS):
        return ConversationPosture.KNOWLEDGE_REVIEW
    return DEFAULT_POSTURE
