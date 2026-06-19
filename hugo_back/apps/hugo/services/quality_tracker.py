from __future__ import annotations

from apps.hugo.domain.conversation_profile import ConversationProgress, SessionMaturityLevel
from apps.hugo.models import ConversationQualitySignal, HugoMessage


def record_session_signal(session, progress: ConversationProgress, turn_count: int = 0) -> ConversationQualitySignal:
    analytics_state = getattr(session, "analytics_state", {}) or {}
    learner_turns = turn_count or HugoMessage.objects.filter(
        session_id=session.id,
        role=HugoMessage.Role.LEARNER,
    ).count()
    signal, _ = ConversationQualitySignal.objects.update_or_create(
        session=session,
        defaults={
            "organisation_id": session.organisation_id,
            "learner_id": session.learner_id,
            "posture": getattr(session, "posture", "") or progress.posture.value,
            "total_turns": learner_turns,
            "active_branches_max": max(
                int(analytics_state.get("active_branches_max", 0) or 0),
                int(progress.active_branches_count or 0),
            ),
            "final_maturity": progress.overall_maturity.value,
            "posture_switches": int(analytics_state.get("posture_switch_count", 0) or 0),
            "synthesis_requested": bool(analytics_state.get("synthesis_requested", False)),
            "evaluation_requested": bool(analytics_state.get("evaluation_requested", False)),
            "evaluation_was_eligible": bool(progress.evaluation_eligible),
            "dispersion_turns": int(analytics_state.get("dispersion_turns", 0) or 0),
            "stuck_red_turns": int(analytics_state.get("stuck_red_turns", 0) or 0),
        },
    )
    return signal


def update_session_analytics(session, progress: ConversationProgress) -> None:
    analytics_state = dict(getattr(session, "analytics_state", {}) or {})
    analytics_state["active_branches_max"] = max(
        int(analytics_state.get("active_branches_max", 0) or 0),
        int(progress.active_branches_count or 0),
    )
    if progress.dispersion_risk:
        analytics_state["dispersion_turns"] = int(analytics_state.get("dispersion_turns", 0) or 0) + 1
    if progress.overall_maturity == SessionMaturityLevel.RED:
        analytics_state["stuck_red_turns"] = int(analytics_state.get("stuck_red_turns", 0) or 0) + 1
    session.analytics_state = analytics_state
