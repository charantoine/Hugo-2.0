"""Shared fixtures for library RAG integration tests."""
from __future__ import annotations

from types import SimpleNamespace

from apps.hugo.domain.schemas import ConversationDecision, TurnState


def rag_turn_state(**overrides):
    defaults = {
        "episode_clarity": "medium",
        "has_concrete_actions": True,
        "problem_salience": "high",
        "reflection_phase": "analysis",
        "reflective_depth": "medium",
        "self_efficacy_signal": "neutral",
        "affect_valence": "neutral",
        "cognitive_load": "medium",
        "interaction_risk": "low",
        "epistemic_balance": "balanced",
        "zpd_estimate": "in",
        "session_phase": "exploration",
        "session_maturity": "early",
        "evidence_strength": "medium",
        "intervention_necessity": "low",
        "contradiction_status": "none",
        "concept_clarity": "medium",
        "available_material": "high",
        "conversation_goal": "progress",
        "current_phase": "exploration",
        "emotional_state": "neutral",
        "action_feasibility": "medium",
        "autonomy_level": "medium",
        "recent_progress": "steady",
        "need_recap": False,
        "need_encouragement": False,
        "need_reframing": False,
        "can_close_for_now": False,
        "safety_or_quality_risk_level": "high",
    }
    defaults.update(overrides)
    return TurnState(**defaults)


def rag_conversation_decision(**overrides):
    defaults = {
        "primary_intent": "guide",
        "pedagogical_move": "analyze",
        "number_of_questions": 1,
        "question_style": "open",
        "should_explain_briefly": False,
        "should_recap": False,
        "should_encourage": False,
        "should_reframe": False,
        "should_close": False,
        "response_constraints": [],
        "reason_codes": [],
        "metadata": {},
    }
    defaults.update(overrides)
    return ConversationDecision(**defaults)


def rag_teaching_plan():
    return SimpleNamespace(rag_mode="supporting", focus_competence={})


def rag_session(organisation_id, group_id):
    return SimpleNamespace(organisation_id=organisation_id, group_id=group_id)


COMMON_CHUNK_TEXT = (
    "procedure tableau electrique consignation verification mise sous tension "
    "schema unifilaire circuits prises eclairage norme nf c15-100 "
)
