from __future__ import annotations

from apps.hugo.domain.conversation_profile import ConversationPosture

MAX_ACTIVE_BRANCHES = 3

TUTOR_PROFILES = {
    ConversationPosture.REFLECTIVE_AFEST: {
        "posture": ConversationPosture.REFLECTIVE_AFEST,
        "max_branches": MAX_ACTIVE_BRANCHES,
        "synthesis_requires": "orange_or_green",
        "evaluation_requires": "green",
        "green_requires_transfer": True,
        "max_questions_per_turn": 2,
        "allowed_moves": [
            "clarify",
            "elicit_action",
            "problematize",
            "analyze",
            "contrast_gently",
            "project",
            "reassure",
            "close",
            "assist",
        ],
        "forbidden_moves": [],
        "closure_policy": "explicit_or_green",
        "description": "Entretien réflexif AFEST.",
    },
    ConversationPosture.DIAGNOSTIC: {
        "posture": ConversationPosture.DIAGNOSTIC,
        "max_branches": MAX_ACTIVE_BRANCHES,
        "synthesis_requires": "orange_or_green",
        "evaluation_requires": "green",
        "green_requires_transfer": False,
        "max_questions_per_turn": 2,
        "allowed_moves": [
            "clarify",
            "elicit_action",
            "problematize",
            "analyze",
            "contrast_gently",
            "reassure",
            "close",
            "assist",
        ],
        "forbidden_moves": ["project"],
        "closure_policy": "explicit_or_green",
        "description": "Diagnostic guidé.",
    },
    ConversationPosture.KNOWLEDGE_REVIEW: {
        "posture": ConversationPosture.KNOWLEDGE_REVIEW,
        "max_branches": 1,
        "synthesis_requires": "orange_or_green",
        "evaluation_requires": "green",
        "green_requires_transfer": False,
        "max_questions_per_turn": 1,
        "allowed_moves": ["clarify", "analyze", "contrast_gently", "reassure", "close", "assist"],
        "forbidden_moves": ["elicit_action", "project"],
        "closure_policy": "explicit_or_green",
        "description": "Révision ou bûchage ciblé.",
    },
}


def get_profile(posture: ConversationPosture) -> dict:
    return TUTOR_PROFILES.get(posture, TUTOR_PROFILES[ConversationPosture.REFLECTIVE_AFEST])


def get_profile_stub(posture: ConversationPosture) -> dict:
    return get_profile(posture)
