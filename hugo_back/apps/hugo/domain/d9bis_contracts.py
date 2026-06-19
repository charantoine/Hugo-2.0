"""
D9bis — contrats artefacts analytiques LLM (domaines 80/100).

Backend analytics technique : jamais UIState, jamais exports métier standard.
"""
from __future__ import annotations

from typing import Any, TypedDict

D9BIS_SCHEMA_VERSION = "d9bis_v1"
D9BIS_EXPORT_SCOPE = "debug_superadmin_only"

# Champs interdits dans les payloads D9bis persistés ou exportés.
D9BIS_FORBIDDEN_KEYS = frozenset(
    {
        "content",
        "verbatim",
        "llm_request_payload",
        "llm_response_payload",
        "turn_state",
        "conversation_decision",
        "p0_debug",
        "episode_clarity",
        "cognitive_load",
        "interaction_risk",
        "problem_salience",
        "affect_valence",
        "reflection_phase",
        "has_concrete_actions",
    }
)


class ConversationTurnLLMAnalysisContract(TypedDict, total=False):
    """Analyse dérivée d'un tour apprenant — sans verbatim."""

    turn_analysis_id: str
    session_id: str
    message_id: str
    organisation_id: str
    analysis_version: str
    turn_index: int
    quality_signals: dict[str, Any]
    pedagogical_tags: list[str]
    created_at: str


class ConversationLLMAnalysisContract(TypedDict, total=False):
    """Agrégat analytique session — export QA/ops SUPERADMIN."""

    session_analysis_id: str
    session_id: str
    organisation_id: str
    analysis_version: str
    turn_analyses_count: int
    summary_metrics: dict[str, Any]
    export_scope: str
    generated_at: str


def assert_d9bis_payload_clean(payload: dict[str, Any]) -> None:
    """Raise ValueError if forbidden keys appear in a D9bis export dict."""
    lowered = str(payload).lower()
    for key in D9BIS_FORBIDDEN_KEYS:
        if key in lowered:
            raise ValueError(f"D9bis payload contains forbidden key: {key}")
