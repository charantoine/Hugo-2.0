from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from apps.hugo.domain.turn_state_v17 import TurnStateV17


@dataclass
class P0RuntimeConfig:
    p0_classifier_enabled: bool = False
    p0_classifier_min_confidence: float = 0.6
    p0_classifier_max_tokens: int = 180
    p0_classifier_max_input_chars: int = 900
    source_by_field: dict[str, Any] = field(default_factory=dict)


def classify_p0_turn_state_v17(
    state: TurnStateV17,
    context,
    config: P0RuntimeConfig,
) -> TurnStateV17:
    """
    1.7-compatible classifier contract.

    The current runtime still delegates real provider calls to the legacy P0 classifier.
    This function preserves the target signature and guarantees the state contract while
    leaving business-safe override logic in the existing pipeline.
    """
    state.debug_signals.source_by_field = dict(config.source_by_field or state.source_by_field)
    if not config.p0_classifier_enabled:
        state.debug_signals.reason_trace = list(dict.fromkeys(list(state.reason_trace) + ["p0_v17_classifier_disabled"]))
        return state
    state.debug_signals.reason_trace = list(dict.fromkeys(list(state.reason_trace) + ["p0_v17_classifier_passthrough"]))
    return state
