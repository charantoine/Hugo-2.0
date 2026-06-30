"""Observabilité avancée v1 — agrégats techniques multi-session, SUPERADMIN only."""
from __future__ import annotations

from datetime import date
from typing import Any

from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone

from apps.hugo.models import ConversationQualitySignal, HugoMessage, HugoSession


def _parse_optional_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(str(value))


def build_conversation_summary(
    organisation_id,
    *,
    group_id: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> dict[str, Any]:
    sessions = HugoSession.objects.filter(organisation_id=organisation_id)
    if group_id:
        sessions = sessions.filter(group_id=group_id)
    if from_date:
        sessions = sessions.filter(created_at__date__gte=from_date)
    if to_date:
        sessions = sessions.filter(created_at__date__lte=to_date)

    session_ids = list(sessions.values_list("id", flat=True))
    sessions_count = len(session_ids)

    message_stats = HugoMessage.objects.filter(session_id__in=session_ids).aggregate(
        learner_turns=Count("id", filter=Q(role=HugoMessage.Role.LEARNER)),
        assistant_turns=Count("id", filter=Q(role=HugoMessage.Role.ASSISTANT)),
    )

    quality_qs = ConversationQualitySignal.objects.filter(session_id__in=session_ids)
    quality_agg = quality_qs.aggregate(
        avg_turns=Avg("total_turns"),
        synthesis_requested_count=Count("id", filter=Q(synthesis_requested=True)),
        evaluation_requested_count=Count("id", filter=Q(evaluation_requested=True)),
        evaluation_eligible_count=Count("id", filter=Q(evaluation_was_eligible=True)),
        total_dispersion=Sum("dispersion_turns"),
        total_stuck_red=Sum("stuck_red_turns"),
    )

    maturity_distribution: dict[str, int] = {}
    posture_distribution: dict[str, int] = {}
    for row in quality_qs.values("final_maturity", "posture"):
        maturity = row.get("final_maturity") or "unknown"
        posture = row.get("posture") or "unknown"
        maturity_distribution[maturity] = maturity_distribution.get(maturity, 0) + 1
        posture_distribution[posture] = posture_distribution.get(posture, 0) + 1

    cta_blocked_synthesis = 0
    cta_blocked_evaluation = 0
    posture_switches = 0
    for session in sessions.only("analytics_state"):
        analytics = dict(getattr(session, "analytics_state", {}) or {})
        cta_blocked_synthesis += int(analytics.get("cta_synthesis_blocked_count", 0) or 0)
        cta_blocked_evaluation += int(analytics.get("cta_evaluation_blocked_count", 0) or 0)
        posture_switches += int(analytics.get("posture_switch_count", 0) or 0)

    duration_samples = []
    for session in sessions.prefetch_related("messages")[:500]:
        msgs = list(session.messages.order_by("created_at").values_list("created_at", flat=True))
        if len(msgs) >= 2:
            duration_samples.append((msgs[-1] - msgs[0]).total_seconds())

    avg_duration_seconds = (
        sum(duration_samples) / len(duration_samples) if duration_samples else None
    )

    learner_turns = int(message_stats.get("learner_turns") or 0)
    assistant_turns = int(message_stats.get("assistant_turns") or 0)

    return {
        "schema": "conversation_summary_v1",
        "generated_at": timezone.now().isoformat(),
        "organisation_id": str(organisation_id),
        "filters": {
            "group_id": str(group_id) if group_id else None,
            "from_date": from_date.isoformat() if from_date else None,
            "to_date": to_date.isoformat() if to_date else None,
        },
        "sessions_count": sessions_count,
        "turn_metrics": {
            "learner_turns_total": learner_turns,
            "assistant_turns_total": assistant_turns,
            "avg_learner_turns_per_session": (
                round(learner_turns / sessions_count, 2) if sessions_count else 0
            ),
            "avg_duration_seconds": round(avg_duration_seconds, 2) if avg_duration_seconds else None,
        },
        "cta_metrics": {
            "synthesis_requested_sessions": int(quality_agg.get("synthesis_requested_count") or 0),
            "evaluation_requested_sessions": int(quality_agg.get("evaluation_requested_count") or 0),
            "evaluation_eligible_sessions": int(quality_agg.get("evaluation_eligible_count") or 0),
            "synthesis_blocked_total": cta_blocked_synthesis,
            "evaluation_blocked_total": cta_blocked_evaluation,
        },
        "posture_metrics": {
            "posture_switch_total": posture_switches,
            "posture_distribution": posture_distribution,
        },
        "quality_metrics": {
            "maturity_distribution": maturity_distribution,
            "avg_total_turns": round(float(quality_agg.get("avg_turns") or 0), 2),
            "dispersion_turns_total": int(quality_agg.get("total_dispersion") or 0),
            "stuck_red_turns_total": int(quality_agg.get("total_stuck_red") or 0),
        },
        "scope": "superadmin_technical_only",
    }
