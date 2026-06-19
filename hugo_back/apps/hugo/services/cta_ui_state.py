from __future__ import annotations

from typing import Any, Optional

from apps.hugo.domain.conversation_profile import ConversationProgress, SessionMaturityLevel
from apps.hugo.models import LearnerEvaluationRecord
from apps.hugo.services.evaluation_blocking_reasons import (
    build_synthesis_blocking_reasons,
    resolve_evaluation_ready_status,
    resolve_synthesis_ready_status,
)
from apps.hugo.services.evaluation_service import get_or_create_policy, resolve_evaluation_readiness


def _session_endpoint(session_id: str, suffix: str) -> str:
    return f"/hugo/sessions/{session_id}/{suffix}"


def _resolve_last_evaluation(session) -> dict[str, Any]:
    record = (
        LearnerEvaluationRecord.objects.filter(session_id=session.id)
        .order_by("-updated_at")
        .first()
    )
    if record is None:
        return {"status": "none", "completed_at": None}
    return {
        "status": "completed",
        "completed_at": record.updated_at.isoformat() if record.updated_at else None,
    }


def _legacy_synthesis_button_state(status: str) -> str:
    if status == "eligible":
        return "ready"
    if status == "blocked_context_incomplete":
        return "possible"
    return "locked"


def _legacy_evaluation_button_state(status: str, *, evaluation_eligible: bool) -> str:
    if status != "eligible":
        return "locked"
    return "ready" if evaluation_eligible else "possible"


def build_cta_synthesis(session, progress: ConversationProgress) -> dict[str, Any]:
    session_id = str(progress.session_id or session.id)
    status, blocking_reasons = resolve_synthesis_ready_status(progress)
    disabled = status != "eligible"
    helper_text = blocking_reasons[0] if disabled and blocking_reasons else None
    return {
        "synthesis_ready_status": status,
        "blocking_reasons": blocking_reasons,
        "endpoints": {
            "request_synthesis": _session_endpoint(session_id, "request-synthesis/"),
        },
        "ui": {
            "show_synthesis_button": True,
            "button_label": "Obtenir une synthèse" if status == "eligible" else "Synthèse indisponible",
            "button_disabled": disabled,
            "helper_text": helper_text,
        },
    }


def build_cta_evaluation(session, progress: ConversationProgress) -> dict[str, Any]:
    session_id = str(progress.session_id or session.id)
    policy = get_or_create_policy(session.organisation, session.group)
    readiness = resolve_evaluation_readiness(progress)
    status, blocking_reasons = resolve_evaluation_ready_status(
        progress,
        allow_early_trigger=bool(policy.allow_early_trigger),
    )
    disabled = status != "eligible"
    helper_text: Optional[str] = None
    if not disabled and not progress.evaluation_eligible and readiness.get("message"):
        helper_text = str(readiness["message"])
    elif disabled and blocking_reasons:
        helper_text = blocking_reasons[0]
    elif not disabled and readiness.get("message"):
        helper_text = str(readiness["message"])

    advisory = status == "eligible" and not progress.evaluation_eligible
    if status == "eligible" and progress.evaluation_eligible:
        button_label = "Demander une évaluation"
    elif status == "eligible":
        button_label = "Évaluation possible"
        if not helper_text:
            helper_text = (
                "Vous pouvez demander une évaluation, mais nous vous conseillons "
                "de poursuivre la conversation pour enrichir le fil."
            )
    else:
        button_label = "Évaluation indisponible"

    return {
        "evaluation_ready_status": status,
        "blocking_reasons": blocking_reasons,
        "endpoints": {
            "request_evaluation": _session_endpoint(session_id, "request-evaluation/"),
            "finalize_evaluation": _session_endpoint(session_id, "finalize-evaluation/"),
            "evaluation_readiness": _session_endpoint(session_id, "evaluation-readiness/"),
        },
        "ui": {
            "show_evaluation_button": True,
            "button_label": button_label,
            "button_disabled": disabled,
            "helper_text": helper_text,
            "advisory": advisory,
        },
        "last_evaluation": _resolve_last_evaluation(session),
    }


def legacy_button_states_from_cta(
    *,
    progress: ConversationProgress,
    cta_synthesis: dict[str, Any],
    cta_evaluation: dict[str, Any],
) -> tuple[str, str, str, Optional[str]]:
    synthesis_state = _legacy_synthesis_button_state(str(cta_synthesis.get("synthesis_ready_status") or ""))
    evaluation_state = _legacy_evaluation_button_state(
        str(cta_evaluation.get("evaluation_ready_status") or ""),
        evaluation_eligible=bool(progress.evaluation_eligible),
    )
    readiness = resolve_evaluation_readiness(progress)
    trigger_state = str(readiness.get("trigger_state") or "red")
    trigger_message = readiness.get("message")
    if cta_evaluation.get("ui", {}).get("helper_text"):
        trigger_message = cta_evaluation["ui"]["helper_text"]
    return synthesis_state, evaluation_state, trigger_state, trigger_message
