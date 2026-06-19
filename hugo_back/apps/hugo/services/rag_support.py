from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Optional

from apps.library.models import DocumentChunk, GroupDocument
from apps.hugo.domain.schemas import normalize_conversation_profile


@dataclass
class RagSelection:
    chunk_id: str
    document_id: str
    document_title: str
    content: str
    score: float
    reason: str
    meta: dict[str, Any]

    def prompt_snippet(self) -> str:
        title = self.document_title.strip() or "Document"
        return f"{title} | score={self.score:.2f} | extrait={self.content}"


def _tokenize(text: str) -> set[str]:
    raw_tokens = re.findall(r"[a-zA-ZÀ-ÿ0-9_]+", str(text or "").lower())
    return {token for token in raw_tokens if len(token) >= 3}


def _priority_terms(turn_state: Any) -> set[str]:
    if not turn_state:
        return set()
    terms = set()
    if getattr(turn_state, "interaction_risk", "") == "high":
        terms.update({"securite", "sécurité", "procedure", "procédure"})
    if getattr(turn_state, "cognitive_load", "") == "high":
        terms.update({"checklist", "etape", "étape"})
    if getattr(turn_state, "problem_salience", "") == "high":
        terms.update({"qualite", "qualité", "controle", "contrôle"})
    if getattr(turn_state, "safety_or_quality_risk_level", "") in {"medium", "high"}:
        terms.update({"norme", "conformite", "conformité", "protection", "consignation"})
    return terms


def _build_query_terms(learner_text: str, teaching_plan: Any, turn_state: Any, conversation_decision: Any) -> set[str]:
    query_terms = set()
    query_terms.update(_tokenize(learner_text))
    query_terms.update(_tokenize(getattr(turn_state, "conversation_goal", "")))
    query_terms.update(_tokenize(getattr(conversation_decision, "pedagogical_move", "")))
    focus = getattr(teaching_plan, "focus_competence", {}) or {}
    query_terms.update(_tokenize(focus.get("label", "")))
    query_terms.update(_tokenize(focus.get("criterion_label", "")))
    query_terms.update(_tokenize(focus.get("primary_task_code", "")))
    query_terms.update(_tokenize(focus.get("primary_task_label", "")))
    query_terms.update(_tokenize(focus.get("activity_code", "")))
    query_terms.update(_tokenize(focus.get("activity_label", "")))
    query_terms.update(_priority_terms(turn_state))
    return query_terms


def should_use_rag(
    teaching_plan: Any,
    conversation_decision: Any,
    turn_state: Optional[Any] = None,
    conversation_profile: str = "reflective_afest",
) -> bool:
    if not teaching_plan or getattr(teaching_plan, "rag_mode", "none") == "none":
        return False
    if not conversation_decision:
        return False
    profile = normalize_conversation_profile(conversation_profile)
    move = str(getattr(conversation_decision, "pedagogical_move", "") or "")
    metadata = getattr(conversation_decision, "metadata", {}) or {}
    risk_meta = str(metadata.get("safety_or_quality_risk_level") or "").lower()
    ts_risk = str(getattr(turn_state, "safety_or_quality_risk_level", "") or "").lower() if turn_state else ""
    interaction_high = getattr(turn_state, "interaction_risk", "") == "high" if turn_state else False
    help_explicit = getattr(turn_state, "learner_help_request", "") == "explicit" if turn_state else False
    if profile == "knowledge_review":
        return move in {"assist", "analyze", "reformulate", "project"} or getattr(turn_state, "available_material", "") in {"medium", "high"}
    if profile == "diagnostic":
        return help_explicit or move in {"assist", "analyze", "contrast_gently"} or ts_risk in {"medium", "high"}
    if move not in {"analyze", "contrast_gently"}:
        return False
    if risk_meta in {"medium", "high"}:
        return True
    if ts_risk in {"medium", "high"}:
        return True
    if interaction_high:
        return True
    return False


def _score_focus_alignment(haystack: str, focus: dict[str, Any]) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []
    criterion_code = str(focus.get("criterion_code", "") or "").lower()
    criterion_label = str(focus.get("criterion_label", "") or "").lower()
    primary_task_code = str(focus.get("primary_task_code", "") or "").lower()
    primary_task_label = str(focus.get("primary_task_label", "") or "").lower()
    activity_code = str(focus.get("activity_code", "") or "").lower()
    activity_label = str(focus.get("activity_label", "") or "").lower()
    if criterion_code and criterion_code in haystack:
        score += 2.5
        reasons.append("criterion_code")
    if primary_task_code and primary_task_code in haystack:
        score += 2.0
        reasons.append("task_code")
    if activity_code and activity_code in haystack:
        score += 1.5
        reasons.append("activity_code")
    for label, bonus, reason in (
        (criterion_label, 1.5, "criterion_label"),
        (primary_task_label, 1.2, "task_label"),
        (activity_label, 1.0, "activity_label"),
    ):
        tokens = [token for token in _tokenize(label) if len(token) >= 5]
        if tokens and any(token in haystack for token in tokens[:4]):
            score += bonus
            reasons.append(reason)
    return score, reasons


def _score_document_meta(chunk: Any, profile: str) -> tuple[float, list[str]]:
    meta = dict(getattr(chunk, "meta", {}) or {})
    document_meta = dict(meta.get("document_meta") or {})
    score = 0.0
    reasons: list[str] = []
    intended_profiles = [
        str(item).strip().lower()
        for item in (document_meta.get("intended_profiles") or [])
        if str(item).strip()
    ]
    if profile in intended_profiles:
        score += 2.0
        reasons.append("profile_match")
    knowledge_type = str(document_meta.get("knowledge_type") or "").lower()
    trainer_priority = str(document_meta.get("trainer_priority") or "").lower()
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
        if document_meta.get(key):
            score += 0.5
            reasons.append(key)
    return score, reasons


def select_rag_chunks(
    session: Any,
    learner_text: str,
    teaching_plan: Any,
    turn_state: Any,
    conversation_decision: Any,
    conversation_profile: str = "reflective_afest",
    limit: int = 3,
) -> list[RagSelection]:
    if not getattr(session, "group_id", None):
        return []
    profile = normalize_conversation_profile(conversation_profile)
    if not should_use_rag(teaching_plan, conversation_decision, turn_state, profile):
        return []

    document_ids = list(
        GroupDocument.objects.filter(
            organisation_id=session.organisation_id,
            group_id=session.group_id,
            status=GroupDocument.Status.ACTIVE,
        ).values_list("document_id", flat=True)
    )
    if not document_ids:
        return []

    query_terms = _build_query_terms(learner_text, teaching_plan, turn_state, conversation_decision)
    if not query_terms:
        return []

    selections: list[RagSelection] = []
    focus = getattr(teaching_plan, "focus_competence", {}) or {}
    chunks = (
        DocumentChunk.objects.filter(document_id__in=document_ids)
        .select_related("document")
        .order_by("created_at")
    )
    for chunk in chunks:
        content = " ".join(str(chunk.content or "").split()).strip()
        if not content:
            continue
        haystack = " ".join(
            [
                content.lower(),
                str(getattr(chunk.document, "title", "") or "").lower(),
                str(getattr(chunk, "meta", {}) or "").lower(),
            ]
        )
        overlap = sum(1 for term in query_terms if term in haystack)
        if overlap <= 0:
            continue
        score = float(overlap)
        reason_tokens = ["lexical_overlap"]
        focus_score, focus_reasons = _score_focus_alignment(haystack, focus)
        score += focus_score
        reason_tokens.extend(focus_reasons)
        meta_score, meta_reasons = _score_document_meta(chunk, profile)
        score += meta_score
        reason_tokens.extend(meta_reasons)
        if any(priority in haystack for priority in ["procedure", "procédure", "securite", "sécurité", "checklist"]):
            score += 1.5
            reason_tokens.append("priority_document")
        selections.append(
            RagSelection(
                chunk_id=str(chunk.id),
                document_id=str(chunk.document_id),
                document_title=str(getattr(chunk.document, "title", "") or ""),
                content=content[:320],
                score=score,
                reason="+".join(reason_tokens[:3]),
                meta={
                    "chunk_meta": getattr(chunk, "meta", {}) or {},
                    "matched_terms": sorted(term for term in query_terms if term in haystack)[:8],
                    "focus_match": focus_reasons[:4],
                },
            )
        )

    selections.sort(key=lambda item: (-item.score, item.document_title, item.chunk_id))
    return selections[:limit]
