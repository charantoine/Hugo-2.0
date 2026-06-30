from __future__ import annotations

from apps.hugo.domain.conversation_profile import ConversationPosture, SessionMaturityLevel

ALLOWED_TRANSITIONS = {
    (ConversationPosture.DIAGNOSTIC, ConversationPosture.REFLECTIVE_AFEST): "always",
    (ConversationPosture.REFLECTIVE_AFEST, ConversationPosture.DIAGNOSTIC): "always",
    (ConversationPosture.KNOWLEDGE_REVIEW, ConversationPosture.REFLECTIVE_AFEST): "orange_or_green",
    (ConversationPosture.REFLECTIVE_AFEST, ConversationPosture.KNOWLEDGE_REVIEW): "always",
}

WARNING_TEXT = (
    "La conversation n'a pas encore suffisamment exploré la situation. "
    "Vous pouvez continuer, mais la synthèse sera moins complète."
)


def can_transition(
    from_posture: ConversationPosture,
    to_posture: ConversationPosture,
    current_maturity: SessionMaturityLevel,
) -> tuple[bool, str]:
    if from_posture == to_posture:
        return True, ""
    condition = ALLOWED_TRANSITIONS.get((from_posture, to_posture))
    if condition is None:
        return False, "transition_not_allowed"
    if condition == "orange_or_green" and current_maturity == SessionMaturityLevel.RED:
        return True, WARNING_TEXT
    return True, ""
