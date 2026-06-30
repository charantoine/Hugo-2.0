"""Contract and validation for Document.meta (trainer library / RAG)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from rest_framework.exceptions import ValidationError

CONVERSATION_ROLES = frozenset(
    {
        "reference_course",
        "support",
        "context",
        "example",
        "technical_point",
        "other",
    }
)
PEDAGOGICAL_INTENTS = frozenset(
    {
        "diagnosis",
        "explanation",
        "practice_support",
        "contextualization",
    }
)
VISIBILITY_VALUES = frozenset({"learner_citable", "internal_only"})
ORIGIN_VALUES = frozenset({"trainer", "admin", "import", "unknown"})
TRAINER_RELIABILITY_VALUES = frozenset({"1", "2", "3", "4"})
DEFAULT_TRAINER_RELIABILITY = "3"
DEFAULT_DOCUMENT_ORIGIN = "unknown"

# Scoring boosts (applied only inside score_document_meta_boost when RAG is already active).
TRAINER_ORIGIN_BOOST = 2.0
RELIABILITY_SCORE_BOOST: dict[str, float] = {
    "1": -0.5,
    "2": 0.0,
    "3": 0.75,
    "4": 1.5,
}

# Legacy keys still accepted in meta (admin UI)
LEGACY_KNOWLEDGE_TYPES = frozenset(
    {
        "knowledge",
        "diagnostic",
        "revision",
        "mistake_pattern",
        "reflection",
        "evidence",
        "mastery_criteria",
        "safety",
        "checklist",
    }
)


@dataclass(frozen=True)
class DocumentMetaContract:
    """Normalized trainer document metadata stored in Document.meta."""

    conversation_role: str = "other"
    pedagogical_intent: str = "explanation"
    visibility: str = "learner_citable"
    trainer_priority: str = "normal"
    intended_profiles: tuple[str, ...] = ()
    pedagogical_intent_note: str = ""
    knowledge_type: str = ""

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "conversation_role": self.conversation_role,
            "pedagogical_intent": self.pedagogical_intent,
            "visibility": self.visibility,
            "trainer_priority": self.trainer_priority,
        }
        if self.intended_profiles:
            out["intended_profiles"] = list(self.intended_profiles)
        if self.pedagogical_intent_note:
            out["pedagogical_intent_note"] = self.pedagogical_intent_note
        if self.knowledge_type:
            out["knowledge_type"] = self.knowledge_type
        return out


def _normalize_profiles(value: Any) -> tuple[str, ...]:
    if not value:
        return ()
    if isinstance(value, str):
        parts = [p.strip() for p in value.split(",") if p.strip()]
        return tuple(parts)
    if isinstance(value, (list, tuple)):
        return tuple(str(p).strip() for p in value if str(p).strip())
    raise ValidationError({"meta": "intended_profiles must be a list or comma-separated string."})


def validate_document_meta(meta: dict[str, Any] | None, *, allow_origin: bool = True) -> dict[str, Any]:
    """
    Validate and normalize Document.meta. Unknown keys are preserved.
    Raises rest_framework.ValidationError on invalid enum values.
    When allow_origin=False, any client-supplied origin is ignored (not copied).
    """
    raw = dict(meta or {})
    normalized = dict(raw)

    role = str(raw.get("conversation_role") or "other").strip().lower()
    if role not in CONVERSATION_ROLES:
        raise ValidationError(
            {"meta": f"conversation_role must be one of: {', '.join(sorted(CONVERSATION_ROLES))}."}
        )
    normalized["conversation_role"] = role

    intent = str(raw.get("pedagogical_intent") or "explanation").strip().lower()
    if intent not in PEDAGOGICAL_INTENTS:
        raise ValidationError(
            {"meta": f"pedagogical_intent must be one of: {', '.join(sorted(PEDAGOGICAL_INTENTS))}."}
        )
    normalized["pedagogical_intent"] = intent

    visibility = str(raw.get("visibility") or "learner_citable").strip().lower()
    if visibility not in VISIBILITY_VALUES:
        raise ValidationError(
            {"meta": f"visibility must be one of: {', '.join(sorted(VISIBILITY_VALUES))}."}
        )
    normalized["visibility"] = visibility

    priority = str(raw.get("trainer_priority") or "normal").strip().lower()
    if priority not in {"normal", "high"}:
        raise ValidationError({"meta": "trainer_priority must be 'normal' or 'high'."})
    normalized["trainer_priority"] = priority

    if "intended_profiles" in raw:
        normalized["intended_profiles"] = list(_normalize_profiles(raw.get("intended_profiles")))

    note = raw.get("pedagogical_intent_note")
    if note is not None:
        normalized["pedagogical_intent_note"] = str(note).strip()[:4000]

    kt = raw.get("knowledge_type")
    if kt is not None and str(kt).strip():
        kt_norm = str(kt).strip().lower()
        if kt_norm not in LEGACY_KNOWLEDGE_TYPES:
            raise ValidationError({"meta": f"Unknown knowledge_type: {kt_norm}"})
        normalized["knowledge_type"] = kt_norm

    reliability = str(raw.get("trainer_reliability") or DEFAULT_TRAINER_RELIABILITY).strip()
    if reliability not in TRAINER_RELIABILITY_VALUES:
        raise ValidationError(
            {"meta": f"trainer_reliability must be one of: {', '.join(sorted(TRAINER_RELIABILITY_VALUES))}."}
        )
    normalized["trainer_reliability"] = reliability

    if allow_origin and "origin" in raw:
        origin = str(raw.get("origin") or DEFAULT_DOCUMENT_ORIGIN).strip().lower()
        if origin not in ORIGIN_VALUES:
            raise ValidationError(
                {"meta": f"origin must be one of: {', '.join(sorted(ORIGIN_VALUES))}."}
            )
        normalized["origin"] = origin

    return normalized


def prepare_document_meta_for_create(user, meta: dict[str, Any] | None) -> dict[str, Any]:
    """Validate client meta, strip forged origin, stamp server-side origin from user role."""
    from apps.accounts.models import Role

    raw = dict(meta or {})
    raw.pop("origin", None)
    normalized = validate_document_meta(raw, allow_origin=False)
    role = getattr(user, "role", None)
    normalized["origin"] = "trainer" if role == Role.TRAINER else "admin"
    return normalized


def prepare_document_meta_for_update(existing_meta: dict[str, Any] | None, patch_meta: dict[str, Any] | None) -> dict[str, Any]:
    """Merge meta patch while preserving immutable server-stamped origin."""
    existing = dict(existing_meta or {})
    patch = dict(patch_meta or {})
    patch.pop("origin", None)
    merged = {**existing, **patch}
    normalized = validate_document_meta(merged, allow_origin=True)
    if existing.get("origin"):
        normalized["origin"] = existing["origin"]
    elif "origin" in normalized:
        pass
    else:
        normalized["origin"] = DEFAULT_DOCUMENT_ORIGIN
    return normalized


def score_document_meta_boost(document_meta: dict[str, Any] | None, conversation_profile: str) -> tuple[float, list[str]]:
    """
    Additional RAG score from document meta (on top of lexical overlap).
    Mirrors and extends rag_support._score_document_meta.
    """
    meta = dict(document_meta or {})
    score = 0.0
    reasons: list[str] = []
    profile = str(conversation_profile or "").strip().lower()

    role = str(meta.get("conversation_role") or "").lower()
    if role == "reference_course":
        score += 2.5
        reasons.append("reference_course")
    elif role == "support":
        score += 1.0
        reasons.append("support")
    elif role == "technical_point":
        score += 1.2
        reasons.append("technical_point")
    elif role == "context":
        score += 0.5
        reasons.append("context")

    intent = str(meta.get("pedagogical_intent") or "").lower()
    if intent == "diagnosis" and profile == "diagnostic":
        score += 0.75
        reasons.append("intent_diagnosis")

    intended_profiles = [
        str(item).strip().lower()
        for item in (meta.get("intended_profiles") or [])
        if str(item).strip()
    ]
    if profile and profile in intended_profiles:
        score += 2.0
        reasons.append("profile_match")

    knowledge_type = str(meta.get("knowledge_type") or "").lower()
    trainer_priority = str(meta.get("trainer_priority") or "").lower()
    if trainer_priority == "high":
        score += 1.5
        reasons.append("trainer_priority")
    if profile == "diagnostic" and knowledge_type in {"diagnostic", "safety", "mistake_pattern"}:
        score += 1.5
        reasons.append("diagnostic_doc")
    if profile == "knowledge_review" and knowledge_type in {"knowledge", "revision", "checklist"}:
        score += 1.5
        reasons.append("knowledge_doc")
    if profile == "reflective_afest" and knowledge_type in {"reflection", "evidence", "mastery_criteria"}:
        score += 1.0
        reasons.append("reflective_doc")
    for key in ("mastery_criteria", "common_mistakes", "reasoning_points"):
        if meta.get(key):
            score += 0.5
            reasons.append(key)

    origin = str(meta.get("origin") or "").lower()
    if origin == "trainer":
        score += TRAINER_ORIGIN_BOOST
        reasons.append("trainer_origin")
        reliability = str(meta.get("trainer_reliability") or DEFAULT_TRAINER_RELIABILITY)
        rel_boost = RELIABILITY_SCORE_BOOST.get(reliability, RELIABILITY_SCORE_BOOST[DEFAULT_TRAINER_RELIABILITY])
        score += rel_boost
        reasons.append(f"reliability_{reliability}")

    return score, reasons
