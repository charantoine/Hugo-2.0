from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Optional

from django.conf import settings

from apps.hugo.domain.schemas import ConversationDecision, TurnState
from apps.hugo.domain.schemas import (
    SESSION_PHASE_DEEPENING,
    SESSION_PHASE_EXPLORATION,
    SESSION_PHASE_OPENING,
    SESSION_PHASE_POTENTIAL_CLOSURE,
    normalize_session_phase,
)
from apps.hugo.llm_client import complete_with_provider
from apps.hugo.models import HugoSession, TutorPrompt

PHASE_ORDER = [
    SESSION_PHASE_OPENING,
    SESSION_PHASE_EXPLORATION,
    SESSION_PHASE_DEEPENING,
    SESSION_PHASE_POTENTIAL_CLOSURE,
]
PHASE_INDEX = {phase: idx for idx, phase in enumerate(PHASE_ORDER)}

PHASE_CLASSIFIER_PRESETS = {
    "safe": {
        "phase_classifier_enabled": True,
        "phase_classifier_min_confidence": 0.75,
        "phase_classifier_max_tokens": 24,
        "phase_classifier_max_input_chars": 500,
    },
    "balanced": {
        "phase_classifier_enabled": True,
        "phase_classifier_min_confidence": 0.60,
        "phase_classifier_max_tokens": 48,
        "phase_classifier_max_input_chars": 700,
    },
    "aggressive": {
        "phase_classifier_enabled": True,
        "phase_classifier_min_confidence": 0.45,
        "phase_classifier_max_tokens": 64,
        "phase_classifier_max_input_chars": 900,
    },
}


@dataclass
class PhaseDecision:
    next_phase: str
    source: str
    confidence: float
    reason: str
    fallback_reason: str = ""
    classifier_provider: str = ""
    classifier_model: str = ""
    runtime_config: dict[str, Any] | None = None
    runtime_config_source: dict[str, Any] | None = None
    adapter_next_phase: str = ""


def _normalize_phase(value: Any) -> Optional[str]:
    phase = normalize_session_phase(value, default="")
    return phase if phase in PHASE_INDEX else None


def _is_transition_allowed(current_phase: str, candidate_phase: str) -> bool:
    current_idx = PHASE_INDEX.get(current_phase)
    candidate_idx = PHASE_INDEX.get(candidate_phase)
    if current_idx is None or candidate_idx is None:
        return False
    # FSM guardrail: stay or +1 only.
    return candidate_idx in {current_idx, current_idx + 1}


def _resolve_provider(session: HugoSession) -> str:
    group = getattr(session, "group", None)
    if group and getattr(group, "llm_backend", None):
        return str(group.llm_backend).lower()
    return str(getattr(settings, "LLM_PROVIDER_DEFAULT", "ollama")).lower()


def _coerce_positive_int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except Exception:
        return default
    return parsed if parsed > 0 else default


def _coerce_confidence(value: Any, default: float) -> float:
    try:
        parsed = float(value)
    except Exception:
        return default
    if parsed < 0 or parsed > 1:
        return default
    return parsed


def _pick_cascade_value(
    session: HugoSession,
    field_name: str,
    setting_name: str,
    setting_default: Any,
) -> tuple[Any, str]:
    session_value = getattr(session, field_name, None)
    if session_value is not None:
        return session_value, "session"
    group = getattr(session, "group", None)
    group_value = getattr(group, field_name, None) if group else None
    if group_value is not None:
        return group_value, "group"
    return getattr(settings, setting_name, setting_default), "settings"


def resolve_classifier_runtime_config(session: HugoSession) -> tuple[dict[str, Any], dict[str, Any]]:
    enabled_raw, enabled_src = _pick_cascade_value(
        session,
        "phase_classifier_enabled",
        "HUGO_PHASE_CLASSIFIER_ENABLED",
        True,
    )
    max_tokens_raw, max_tokens_src = _pick_cascade_value(
        session,
        "phase_classifier_max_tokens",
        "HUGO_PHASE_CLASSIFIER_MAX_TOKENS",
        PHASE_CLASSIFIER_PRESETS["balanced"]["phase_classifier_max_tokens"],
    )
    min_conf_raw, min_conf_src = _pick_cascade_value(
        session,
        "phase_classifier_min_confidence",
        "HUGO_PHASE_CLASSIFIER_MIN_CONFIDENCE",
        PHASE_CLASSIFIER_PRESETS["balanced"]["phase_classifier_min_confidence"],
    )
    max_input_chars_raw, max_input_chars_src = _pick_cascade_value(
        session,
        "phase_classifier_max_input_chars",
        "HUGO_PHASE_CLASSIFIER_MAX_INPUT_CHARS",
        PHASE_CLASSIFIER_PRESETS["balanced"]["phase_classifier_max_input_chars"],
    )

    runtime_config = {
        "phase_classifier_enabled": bool(enabled_raw),
        "phase_classifier_max_tokens": _coerce_positive_int(
            max_tokens_raw,
            PHASE_CLASSIFIER_PRESETS["balanced"]["phase_classifier_max_tokens"],
        ),
        "phase_classifier_min_confidence": _coerce_confidence(
            min_conf_raw,
            PHASE_CLASSIFIER_PRESETS["balanced"]["phase_classifier_min_confidence"],
        ),
        "phase_classifier_max_input_chars": _coerce_positive_int(
            max_input_chars_raw,
            PHASE_CLASSIFIER_PRESETS["balanced"]["phase_classifier_max_input_chars"],
        ),
    }
    source_by_field = {
        "phase_classifier_enabled": enabled_src,
        "phase_classifier_max_tokens": max_tokens_src,
        "phase_classifier_min_confidence": min_conf_src,
        "phase_classifier_max_input_chars": max_input_chars_src,
    }
    unique_sources = {src for src in source_by_field.values()}
    source_by_field["effective"] = unique_sources.pop() if len(unique_sources) == 1 else "mixed"
    return runtime_config, source_by_field


def _extract_json_object(text: str) -> Optional[dict]:
    body = (text or "").strip()
    if not body:
        return None
    try:
        parsed = json.loads(body)
        return parsed if isinstance(parsed, dict) else None
    except Exception:
        pass
    match = re.search(r"\{.*\}", body, flags=re.DOTALL)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
        return parsed if isinstance(parsed, dict) else None
    except Exception:
        return None


def _derive_adapter_phase(
    current_phase: str,
    deterministic_next_phase: str,
    turn_state: TurnState | None = None,
    conversation_decision: ConversationDecision | None = None,
) -> tuple[str, str]:
    normalized_current = _normalize_phase(current_phase) or SESSION_PHASE_EXPLORATION
    normalized_fallback = _normalize_phase(deterministic_next_phase) or normalized_current
    if not turn_state or not conversation_decision:
        return normalized_fallback, "deterministic_plan"
    if conversation_decision.should_close or turn_state.closure_signal == "explicit" or turn_state.can_close_for_now:
        return SESSION_PHASE_POTENTIAL_CLOSURE, "decision_close"
    if turn_state.episode_clarity == "low" or not turn_state.has_concrete_actions:
        return SESSION_PHASE_EXPLORATION, "decision_exploration"
    if conversation_decision.pedagogical_move in {"analyze", "contrast_gently"}:
        return SESSION_PHASE_DEEPENING, "decision_deepening"
    if conversation_decision.pedagogical_move == "project":
        return SESSION_PHASE_POTENTIAL_CLOSURE, "decision_projection"
    return normalized_fallback, "deterministic_plan"


def decide_next_phase(
    session: HugoSession,
    tutor_prompt: TutorPrompt | None,
    current_phase: str,
    user_input: dict[str, Any],
    deterministic_next_phase: str,
    turn_state: TurnState | None = None,
    conversation_decision: ConversationDecision | None = None,
) -> PhaseDecision:
    runtime_config, runtime_config_source = resolve_classifier_runtime_config(session)
    classifier_enabled = bool(runtime_config["phase_classifier_enabled"])
    normalized_current = _normalize_phase(current_phase) or HugoSession.SessionPhase.EXPLORATION
    adapter_next_phase, adapter_reason = _derive_adapter_phase(
        current_phase=normalized_current,
        deterministic_next_phase=deterministic_next_phase,
        turn_state=turn_state,
        conversation_decision=conversation_decision,
    )
    provider = _resolve_provider(session)
    if not classifier_enabled:
        return PhaseDecision(
            next_phase=adapter_next_phase,
            source="state_adapter",
            confidence=1.0,
            reason=adapter_reason,
            fallback_reason="classifier_desactive",
            runtime_config=runtime_config,
            runtime_config_source=runtime_config_source,
            adapter_next_phase=adapter_next_phase,
        )

    classifier_input = str(user_input.get("content", "") or "").strip()
    max_input_chars = int(runtime_config["phase_classifier_max_input_chars"])
    if not classifier_input:
        return PhaseDecision(
            next_phase=adapter_next_phase,
            source="state_adapter",
            confidence=1.0,
            reason=adapter_reason,
            fallback_reason="input_vide",
            runtime_config=runtime_config,
            runtime_config_source=runtime_config_source,
            adapter_next_phase=adapter_next_phase,
        )

    system_prompt = (
        "Tu es un classifieur de phase pedagogique. "
        "Tu dois repondre uniquement en JSON strict: "
        '{"phase":"opening|exploration|deepening|potential_closure","confidence":0.0,"reason":"court"}. '
        "Aucune explication hors JSON."
    )
    user_prompt = (
        f'phase_actuelle="{normalized_current}"\n'
        f'phase_adaptee="{adapter_next_phase}"\n'
        f'input_apprenant="{classifier_input[:max_input_chars]}"\n'
        f'couverture="{str(user_input.get("coverage_status", "ok"))[:50]}"\n'
        "Choisis la phase suivante la plus appropriee."
    )
    max_tokens = int(runtime_config["phase_classifier_max_tokens"])
    min_conf = float(runtime_config["phase_classifier_min_confidence"])

    text, meta = complete_with_provider(
        prompt=user_prompt,
        system=system_prompt,
        max_tokens=max_tokens,
        provider=provider,
        tutor_prompt=tutor_prompt,
    )
    parsed = _extract_json_object(text)
    if not parsed:
        return PhaseDecision(
            next_phase=adapter_next_phase,
            source="state_adapter",
            confidence=1.0,
            reason=adapter_reason,
            fallback_reason="parse_invalide",
            classifier_provider=provider,
            classifier_model=str(meta.get("model_used") or ""),
            runtime_config=runtime_config,
            runtime_config_source=runtime_config_source,
            adapter_next_phase=adapter_next_phase,
        )

    candidate = _normalize_phase(parsed.get("phase"))
    if not candidate:
        return PhaseDecision(
            next_phase=adapter_next_phase,
            source="state_adapter",
            confidence=1.0,
            reason=adapter_reason,
            fallback_reason="phase_invalide",
            classifier_provider=provider,
            classifier_model=str(meta.get("model_used") or ""),
            runtime_config=runtime_config,
            runtime_config_source=runtime_config_source,
            adapter_next_phase=adapter_next_phase,
        )

    try:
        confidence = float(parsed.get("confidence", 0.0))
    except Exception:
        confidence = 0.0
    reason = str(parsed.get("reason", "") or "").strip()[:140]

    if not _is_transition_allowed(normalized_current, candidate):
        return PhaseDecision(
            next_phase=adapter_next_phase,
            source="state_adapter",
            confidence=1.0,
            reason=adapter_reason,
            fallback_reason="transition_non_autorisee",
            classifier_provider=provider,
            classifier_model=str(meta.get("model_used") or ""),
            runtime_config=runtime_config,
            runtime_config_source=runtime_config_source,
            adapter_next_phase=adapter_next_phase,
        )
    if confidence < min_conf:
        return PhaseDecision(
            next_phase=adapter_next_phase,
            source="state_adapter",
            confidence=1.0,
            reason=adapter_reason,
            fallback_reason="confiance_trop_faible",
            classifier_provider=provider,
            classifier_model=str(meta.get("model_used") or ""),
            runtime_config=runtime_config,
            runtime_config_source=runtime_config_source,
            adapter_next_phase=adapter_next_phase,
        )

    if turn_state and turn_state.closure_signal == "explicit" and candidate != SESSION_PHASE_POTENTIAL_CLOSURE:
        return PhaseDecision(
            next_phase=adapter_next_phase,
            source="state_adapter",
            confidence=1.0,
            reason=adapter_reason,
            fallback_reason="explicit_closure_priority",
            classifier_provider=provider,
            classifier_model=str(meta.get("model_used") or ""),
            runtime_config=runtime_config,
            runtime_config_source=runtime_config_source,
            adapter_next_phase=adapter_next_phase,
        )

    if (
        turn_state
        and conversation_decision
        and (turn_state.cognitive_load == "high" or turn_state.interaction_risk == "high")
        and candidate != adapter_next_phase
    ):
        return PhaseDecision(
            next_phase=adapter_next_phase,
            source="state_adapter",
            confidence=1.0,
            reason=adapter_reason,
            fallback_reason="state_priority_high_risk",
            classifier_provider=provider,
            classifier_model=str(meta.get("model_used") or ""),
            runtime_config=runtime_config,
            runtime_config_source=runtime_config_source,
            adapter_next_phase=adapter_next_phase,
        )

    return PhaseDecision(
        next_phase=candidate,
        source="llm_classifier",
        confidence=confidence,
        reason=reason or "decision_llm",
        classifier_provider=provider,
        classifier_model=str(meta.get("model_used") or ""),
        runtime_config=runtime_config,
        runtime_config_source=runtime_config_source,
        adapter_next_phase=adapter_next_phase,
    )
