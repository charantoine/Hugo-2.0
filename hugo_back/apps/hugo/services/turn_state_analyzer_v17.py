from __future__ import annotations

from types import SimpleNamespace

from apps.hugo.domain.turn_state_v17 import TurnStateV17, from_legacy_turn_state
from apps.hugo.services.turn_state_analyzer import analyze_turn_state


def analyze_turn_state_v17(
    context,
    learner_message: str,
    requested_phase: str | None = None,
) -> TurnStateV17:
    """
    Stateless compatibility wrapper for the 1.7 contract.

    The production runtime still relies on the legacy session-aware analyzer and then
    reconciles the result into `TurnStateV17`. This wrapper exists to expose the target
    1.7 signature without breaking the current pipeline.
    """
    session_stub = SimpleNamespace(messages=SimpleNamespace(count=lambda: 0))
    legacy_state = analyze_turn_state(
        session=session_stub,
        user_input={"content": learner_message, "session_phase": requested_phase or ""},
        ctx=context,
    )
    return from_legacy_turn_state(legacy_state)
