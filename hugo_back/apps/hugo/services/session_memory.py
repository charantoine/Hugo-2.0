from __future__ import annotations

from typing import Any, Iterable, Optional

from django.utils import timezone

from apps.hugo.domain.schemas import SessionMemoryContract, SessionMemorySummary
from apps.hugo.models import HugoMessage, HugoSession, Trace


def _to_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _unique(items: Iterable[str], limit: int = 6) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = str(item).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
        if len(result) >= limit:
            break
    return result


def _session_learner_messages(
    session: HugoSession,
    *,
    max_messages: int = 6,
    messages: Optional[list[HugoMessage]] = None,
) -> list[HugoMessage]:
    if messages is not None:
        return list(messages)
    return list(
        HugoMessage.objects.filter(
            organisation_id=session.organisation_id,
            session_id=session.id,
            role=HugoMessage.Role.LEARNER,
        )
        .exclude(llm_request_payload={})
        .order_by("-created_at")[:max_messages]
    )


def _collect_turn_state_points(messages: list[HugoMessage]) -> tuple[list[str], list[str]]:
    covered_points: list[str] = []
    carry_over_points: list[str] = []
    for message in messages:
        payload = message.llm_request_payload or {}
        turn_state = payload.get("turn_state") if isinstance(payload.get("turn_state"), dict) else {}
        covered_points.extend(_to_list(turn_state.get("covered_points")))
        carry_over_points.extend(_to_list(turn_state.get("remaining_open_points")))
    return covered_points, carry_over_points


def _resolve_progress_field(conversation_progress: Any, field_name: str, default: str = "") -> str:
    if conversation_progress is None:
        return default
    if isinstance(conversation_progress, dict):
        return str(conversation_progress.get(field_name) or default).strip()
    return str(getattr(conversation_progress, field_name, "") or default).strip()


def _resolve_progress_list(conversation_progress: Any, field_name: str) -> list[str]:
    if conversation_progress is None:
        return []
    if isinstance(conversation_progress, dict):
        return _to_list(conversation_progress.get(field_name))
    return _to_list(getattr(conversation_progress, field_name, []))


def _resolve_turn_state_list(turn_state: Any, field_name: str) -> list[str]:
    if turn_state is None:
        return []
    if isinstance(turn_state, dict):
        return _to_list(turn_state.get(field_name))
    return _to_list(getattr(turn_state, field_name, []))


def build_session_memory_contract(
    *,
    session: HugoSession,
    turn_state: Any = None,
    conversation_progress: Any = None,
    messages: Optional[list[HugoMessage]] = None,
    max_messages: int = 6,
) -> SessionMemoryContract:
    """
    Build the governed intra-conversation memory contract for the current session thread.
    """
    session_messages = _session_learner_messages(session, max_messages=max_messages, messages=messages)
    payload_covered, payload_open = _collect_turn_state_points(session_messages)

    facts_confirmed = _unique(
        _resolve_turn_state_list(turn_state, "covered_points")
        + _resolve_progress_list(conversation_progress, "covered_points")
        + payload_covered
    )
    open_points = _unique(
        _resolve_turn_state_list(turn_state, "remaining_open_points")
        + _resolve_progress_list(conversation_progress, "remaining_open_points")
        + payload_open
    )

    goal_items = _resolve_turn_state_list(turn_state, "conversation_goal")
    theme = (
        _resolve_progress_field(conversation_progress, "branch_label")
        or _resolve_progress_field(conversation_progress, "conversation_profile")
        or (goal_items[0] if goal_items else "")
    )
    learning_objective = _resolve_progress_field(conversation_progress, "active_objective")

    pending_actions: list[str] = []
    next_action = _resolve_progress_field(conversation_progress, "next_recommended_action")
    if next_action:
        pending_actions.append(next_action)
    # TODO(lot1): enrich pending_actions from explicit learner commitments when available.

    updated_at = session.updated_at.isoformat() if getattr(session, "updated_at", None) else timezone.now().isoformat()

    return SessionMemoryContract(
        session_id=str(session.id),
        updated_at=updated_at,
        theme=theme,
        learning_objective=learning_objective,
        facts_confirmed=facts_confirmed,
        open_points=open_points,
        pending_actions=_unique(pending_actions, limit=5),
        memory_scope="intra_conversation",
    )


def build_session_memory(
    session: HugoSession,
    *,
    turn_state: Any = None,
    conversation_progress: Any = None,
    messages: Optional[list[HugoMessage]] = None,
    max_messages: int = 6,
) -> SessionMemorySummary:
    session_messages = _session_learner_messages(session, max_messages=max_messages, messages=messages)
    covered_points, carry_over_points = _collect_turn_state_points(session_messages)

    contract = build_session_memory_contract(
        session=session,
        turn_state=turn_state,
        conversation_progress=conversation_progress,
        messages=session_messages,
        max_messages=max_messages,
    )

    if contract.theme:
        summary = contract.theme
    elif carry_over_points:
        summary = "Continuer sur les points ouverts du fil courant sans repartir de zéro."
    elif covered_points:
        summary = "Capitaliser sur les repères déjà stabilisés dans ce fil."
    else:
        summary = "Fil en cours : repartir des repères structurés disponibles dans cette session."

    validated_traces_count = Trace.objects.filter(
        organisation_id=session.organisation_id,
        session_id=session.id,
        validated_at__isnull=False,
    ).count()

    return SessionMemorySummary(
        summary=summary,
        active_themes=_unique(covered_points),
        carry_over_points=_unique(carry_over_points),
        open_action_items=list(contract.pending_actions),
        last_session_at=None,
        sessions_considered=1 if session_messages else 0,
        validated_traces_count=validated_traces_count,
        contract=contract,
    )
