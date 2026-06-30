"""Observabilité de base (domaine 80) — signaux techniques, non exposés UIState apprenant."""
from __future__ import annotations

from typing import Any

from apps.hugo.models import ConversationQualitySignal, HugoMessage, HugoSession


def increment_session_analytics_counter(session: HugoSession, key: str) -> None:
    state = dict(getattr(session, "analytics_state", {}) or {})
    state[key] = int(state.get(key, 0) or 0) + 1
    session.analytics_state = state
    session.save(update_fields=["analytics_state", "updated_at"])


def build_session_observability_snapshot(session: HugoSession) -> dict[str, Any]:
    analytics = dict(getattr(session, "analytics_state", {}) or {})
    learner_turns = HugoMessage.objects.filter(
        session_id=session.id,
        role=HugoMessage.Role.LEARNER,
    ).count()
    assistant_turns = HugoMessage.objects.filter(
        session_id=session.id,
        role=HugoMessage.Role.ASSISTANT,
    ).count()

    quality: ConversationQualitySignal | None = None
    try:
        quality = session.quality_signal
    except ConversationQualitySignal.DoesNotExist:
        quality = None

    return {
        "schema": "session_observability_v1",
        "session_id": str(session.id),
        "organisation_id": str(session.organisation_id),
        "learner_id": str(session.learner_id),
        "turn_counts": {
            "learner": learner_turns,
            "assistant": assistant_turns,
            "total": learner_turns + assistant_turns,
        },
        "cta_counters": {
            "synthesis_requested": bool(analytics.get("synthesis_requested")),
            "evaluation_requested": bool(analytics.get("evaluation_requested")),
            "synthesis_blocked": int(analytics.get("cta_synthesis_blocked_count", 0) or 0),
            "evaluation_blocked": int(analytics.get("cta_evaluation_blocked_count", 0) or 0),
        },
        "analytics_state": {
            "posture_switch_count": int(analytics.get("posture_switch_count", 0) or 0),
            "dispersion_turns": int(analytics.get("dispersion_turns", 0) or 0),
            "stuck_red_turns": int(analytics.get("stuck_red_turns", 0) or 0),
            "active_branches_max": int(analytics.get("active_branches_max", 0) or 0),
        },
        "quality_signal": (
            {
                "total_turns": quality.total_turns,
                "final_maturity": quality.final_maturity,
                "evaluation_was_eligible": quality.evaluation_was_eligible,
                "synthesis_requested": quality.synthesis_requested,
                "evaluation_requested": quality.evaluation_requested,
            }
            if quality
            else None
        ),
        "scope": "admin_debug_only",
    }
