"""D9bis — analytics LLM dérivées, sans verbatim ni P0."""
from __future__ import annotations

from typing import Any

from django.utils import timezone

from apps.hugo.domain.d9bis_contracts import (
    D9BIS_EXPORT_SCOPE,
    D9BIS_SCHEMA_VERSION,
    assert_d9bis_payload_clean,
)
from apps.hugo.domain.schemas import P0_CORE_FIELDS, P0_LLM_FIELDS
from apps.hugo.models import (
    ConversationLLMAnalysis,
    ConversationTurnLLMAnalysis,
    HugoMessage,
    HugoSession,
)

_P0_FORBIDDEN = set(P0_CORE_FIELDS) | set(P0_LLM_FIELDS)


def _char_length_bucket(length: int) -> str:
    if length <= 80:
        return "short"
    if length <= 280:
        return "medium"
    return "long"


def _extract_progress_derivatives(session: HugoSession) -> dict[str, Any]:
    progress = session.conversation_progress if isinstance(session.conversation_progress, dict) else {}
    reason_codes = progress.get("reason_codes") or []
    return {
        "overall_maturity": progress.get("overall_maturity"),
        "active_branches_count": int(progress.get("active_branches_count", 0) or 0),
        "synthesis_eligible": bool(progress.get("synthesis_eligible")),
        "evaluation_eligible": bool(progress.get("evaluation_eligible")),
        "reason_codes_count": len(reason_codes) if isinstance(reason_codes, list) else 0,
        "posture": progress.get("posture") or getattr(session, "posture", ""),
    }


def _build_turn_quality_signals(
    session: HugoSession,
    message: HugoMessage,
    turn_index: int,
) -> dict[str, Any]:
    progress_derivatives = _extract_progress_derivatives(session)
    signals = {
        "turn_index": turn_index,
        "learner_char_length_bucket": _char_length_bucket(len(message.content or "")),
        **progress_derivatives,
    }
    for forbidden in _P0_FORBIDDEN:
        signals.pop(forbidden, None)
    return signals


def _derive_pedagogical_tags(session: HugoSession, turn_index: int) -> list[str]:
    progress = session.conversation_progress if isinstance(session.conversation_progress, dict) else {}
    tags: list[str] = []
    maturity = progress.get("overall_maturity")
    if maturity:
        tags.append(f"maturity:{maturity}")
    if progress.get("synthesis_eligible"):
        tags.append("synthesis_eligible")
    if progress.get("evaluation_eligible"):
        tags.append("evaluation_eligible")
    if turn_index == 1:
        tags.append("opening_turn")
    return tags[:10]


def build_or_refresh_d9bis_for_session(session: HugoSession) -> ConversationLLMAnalysis:
    """Persist derived turn analyses and session aggregate — no verbatim stored."""
    learner_messages = list(
        session.messages.filter(role=HugoMessage.Role.LEARNER).order_by("created_at")
    )
    ConversationTurnLLMAnalysis.objects.filter(session=session).delete()

    turn_rows: list[ConversationTurnLLMAnalysis] = []
    for index, message in enumerate(learner_messages, start=1):
        quality_signals = _build_turn_quality_signals(session, message, index)
        pedagogical_tags = _derive_pedagogical_tags(session, index)
        row = ConversationTurnLLMAnalysis.objects.create(
            organisation_id=session.organisation_id,
            session=session,
            learner_message=message,
            turn_index=index,
            analysis_version=D9BIS_SCHEMA_VERSION,
            quality_signals=quality_signals,
            pedagogical_tags=pedagogical_tags,
        )
        turn_rows.append(row)

    analytics = dict(getattr(session, "analytics_state", {}) or {})
    summary_metrics = {
        "learner_turns": len(turn_rows),
        "assistant_turns": session.messages.filter(role=HugoMessage.Role.ASSISTANT).count(),
        "cta_synthesis_blocked": int(analytics.get("cta_synthesis_blocked_count", 0) or 0),
        "cta_evaluation_blocked": int(analytics.get("cta_evaluation_blocked_count", 0) or 0),
        "synthesis_requested": bool(analytics.get("synthesis_requested")),
        "evaluation_requested": bool(analytics.get("evaluation_requested")),
        "posture_switch_count": int(analytics.get("posture_switch_count", 0) or 0),
        "final_maturity": _extract_progress_derivatives(session).get("overall_maturity"),
    }

    aggregate, _ = ConversationLLMAnalysis.objects.update_or_create(
        session=session,
        defaults={
            "organisation_id": session.organisation_id,
            "analysis_version": D9BIS_SCHEMA_VERSION,
            "turn_analyses_count": len(turn_rows),
            "summary_metrics": summary_metrics,
            "export_scope": D9BIS_EXPORT_SCOPE,
        },
    )
    return aggregate


def serialize_turn_analysis(row: ConversationTurnLLMAnalysis) -> dict[str, Any]:
    payload = {
        "turn_analysis_id": str(row.id),
        "session_id": str(row.session_id),
        "message_id": str(row.learner_message_id),
        "organisation_id": str(row.organisation_id),
        "analysis_version": row.analysis_version,
        "turn_index": row.turn_index,
        "quality_signals": row.quality_signals or {},
        "pedagogical_tags": list(row.pedagogical_tags or []),
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }
    assert_d9bis_payload_clean(payload)
    return payload


def serialize_session_analysis(
    aggregate: ConversationLLMAnalysis,
    *,
    include_turns: bool = True,
) -> dict[str, Any]:
    turn_analyses = []
    if include_turns:
        for row in ConversationTurnLLMAnalysis.objects.filter(session_id=aggregate.session_id).order_by("turn_index"):
            turn_analyses.append(serialize_turn_analysis(row))

    payload = {
        "schema": "d9bis_session_export_v1",
        "session_analysis_id": str(aggregate.id),
        "session_id": str(aggregate.session_id),
        "organisation_id": str(aggregate.organisation_id),
        "analysis_version": aggregate.analysis_version,
        "turn_analyses_count": aggregate.turn_analyses_count,
        "summary_metrics": aggregate.summary_metrics or {},
        "turn_analyses": turn_analyses,
        "export_scope": aggregate.export_scope,
        "generated_at": timezone.now().isoformat(),
        "disclaimer": "Export technique QA/ops — données dérivées, non montrables produit.",
    }
    assert_d9bis_payload_clean(payload)
    return payload
