from __future__ import annotations

from typing import Any

from django.conf import settings

from apps.library.models import RagCitation


def tracing_enabled() -> bool:
    return bool(getattr(settings, "HUGO_DEBUG_TRACING", getattr(settings, "DEBUG", False)))


def compact_rag_selections_for_trace(rag_selections: list) -> list[dict]:
    """Compact RAG rows for persisted traces (prompt + audit)."""
    return [
        {
            "chunk_id": selection.chunk_id,
            "document_id": selection.document_id,
            "document_title": selection.document_title,
            "score": selection.score,
            "reason": selection.reason,
        }
        for selection in rag_selections
    ]


def build_prompt_sources(ctx: Any, rag_selections: list) -> dict:
    """
    Snapshot of what was available in the prompt (référentiel + RAG), not what the model "used".
    """
    ref_name = (getattr(ctx, "referential_name", None) or "").strip() or None
    ref_src = (getattr(ctx, "referential_source_ref", None) or "").strip() or None
    items_focus = list(getattr(ctx, "items_to_focus", None) or [])
    items_cov = list(getattr(ctx, "items_already_covered", None) or [])
    included = bool(ref_name) or bool(ref_src) or bool(items_focus) or bool(items_cov)
    compact = compact_rag_selections_for_trace(rag_selections)
    return {
        "referential": {
            "included": included,
            "referential_name": ref_name,
            "referential_source_ref": ref_src,
            "focus_items_count": len(items_focus),
        },
        "rag": {
            "used": len(rag_selections) > 0,
            "selection_count": len(rag_selections),
            "selections": compact,
        },
    }


def _default_prompt_sources(rag_selections: list) -> dict:
    compact = compact_rag_selections_for_trace(rag_selections)
    return {
        "referential": {
            "included": False,
            "referential_name": None,
            "referential_source_ref": None,
            "focus_items_count": 0,
        },
        "rag": {
            "used": len(rag_selections) > 0,
            "selection_count": len(rag_selections),
            "selections": compact,
        },
    }


def _merge_prompt_sources(prompt_sources: dict | None, rag_selections: list) -> dict:
    if prompt_sources is not None:
        return prompt_sources
    return _default_prompt_sources(rag_selections)


def build_request_trace(
    *,
    provider: str,
    llm_meta: dict,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    resolved_tutor_prompt_id: str | None,
    configured_output_mode: str,
    output_mode: str,
    effective_max_questions_this_turn: int,
    session_phase: str,
    next_session_phase: str,
    requested_phase: str | None,
    manual_phase_override: str | None,
    alignment_meta: dict,
    phase_decision: dict,
    p0_classifier: dict,
    turn_state: dict,
    conversation_decision: dict,
    conversation_profile: str,
    conversation_progress: dict,
    ui_state: dict,
    session_memory: dict,
    focus_criterion_code: str,
    focus_criterion_label: str,
    covered_criteria_codes: list[str],
    rag_selections: list,
    prompt_sources: dict | None = None,
    tutor_prompt_snapshot: dict | None = None,
) -> dict:
    # Toujours persister ce qui est réellement envoyé au fournisseur (audit / vérif POC),
    # même si HUGO_DEBUG_TRACING est faux — le reste reste conditionnel.
    core_llm = {
        "provider": llm_meta.get("provider", provider),
        "model_used": llm_meta.get("model_used"),
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "max_tokens": max_tokens,
        "request_payload": llm_meta.get("request_payload"),
    }
    err = llm_meta.get("error")
    if err:
        core_llm["llm_error"] = err

    ps = _merge_prompt_sources(prompt_sources, rag_selections)
    rag_compact = compact_rag_selections_for_trace(rag_selections)

    tp_fields = {
        "resolved_tutor_prompt_id": resolved_tutor_prompt_id,
        "tutor_prompt_snapshot": tutor_prompt_snapshot or {},
    }

    if not tracing_enabled():
        return {
            **core_llm,
            **tp_fields,
            "configured_output_mode": configured_output_mode,
            "effective_max_questions_this_turn": effective_max_questions_this_turn,
            "session_phase": session_phase,
            "next_session_phase": next_session_phase,
            "p0_classifier": p0_classifier,
            "p0_signals": (turn_state or {}).get("p0", {}),
            "anti_loop": {
                "last_tutorial_move": (turn_state or {}).get("last_tutorial_move", ""),
                "consecutive_clarify_turns": (turn_state or {}).get("consecutive_clarify_turns", 0),
                "sticky_has_concrete_actions": (turn_state or {}).get("sticky_has_concrete_actions", False),
            },
            "turn_state": turn_state,
            "conversation_decision": conversation_decision,
            "conversation_profile": conversation_profile,
            "conversation_progress": conversation_progress,
            "ui_state": ui_state,
            "session_memory": session_memory,
            "rag": rag_compact,
            "prompt_sources": ps,
        }

    return {
        **core_llm,
        **tp_fields,
        "configured_output_mode": configured_output_mode,
        "resolved_output_mode": output_mode,
        "effective_max_questions_this_turn": effective_max_questions_this_turn,
        "session_phase": session_phase,
        "next_session_phase": next_session_phase,
        "requested_session_phase": requested_phase,
        "manual_phase_override": manual_phase_override,
        "indexed_alignment_applied": alignment_meta.get("applied", False),
        "aligned_pairs_count": alignment_meta.get("pairs_count", 0),
        "phase_decision_source": phase_decision.get("source", "state_adapter"),
        "phase_decision_confidence": phase_decision.get("confidence", 0.0),
        "phase_decision_reason": phase_decision.get("reason", ""),
        "phase_decision_fallback_reason": phase_decision.get("fallback_reason", ""),
        "adapter_next_phase": phase_decision.get("adapter_next_phase", ""),
        "phase_classifier_provider": phase_decision.get("classifier_provider", ""),
        "phase_classifier_model": phase_decision.get("classifier_model", ""),
        "phase_classifier_runtime_config": phase_decision.get("runtime_config", {}),
        "phase_classifier_runtime_config_source": phase_decision.get("runtime_config_source", {}),
        "p0_classifier": p0_classifier,
        "p0_signals": (turn_state or {}).get("p0", {}),
        "anti_loop": {
            "last_tutorial_move": (turn_state or {}).get("last_tutorial_move", ""),
            "consecutive_clarify_turns": (turn_state or {}).get("consecutive_clarify_turns", 0),
            "sticky_has_concrete_actions": (turn_state or {}).get("sticky_has_concrete_actions", False),
        },
        "turn_state": turn_state,
        "conversation_decision": conversation_decision,
        "conversation_profile": conversation_profile,
        "conversation_progress": conversation_progress,
        "ui_state": ui_state,
        "session_memory": session_memory,
        "focus_criterion_code": focus_criterion_code,
        "focus_criterion_label": focus_criterion_label,
        "covered_criteria_codes": covered_criteria_codes[:5],
        "criterion_focus_source": "context_uncovered_priority",
        "rag": rag_compact,
        "prompt_sources": ps,
    }


def build_response_trace(
    *,
    provider: str,
    llm_meta: dict,
    rag_selections: list,
    assistant_text_before_guardrails: str = "",
    prompt_sources: dict | None = None,
) -> dict:
    core = {
        "provider": llm_meta.get("provider", provider),
        "model_used": llm_meta.get("model_used"),
        "assistant_text_before_guardrails": assistant_text_before_guardrails,
        "raw_response": llm_meta.get("raw_response"),
    }
    err = llm_meta.get("error")
    if err:
        core["llm_error"] = err

    ps = _merge_prompt_sources(prompt_sources, rag_selections)
    rag_compact = compact_rag_selections_for_trace(rag_selections)

    if not tracing_enabled():
        return {
            **core,
            "rag": rag_compact,
            "prompt_sources": ps,
        }
    return {
        **core,
        "rag": rag_compact,
        "prompt_sources": ps,
    }


def persist_rag_citations(*, organisation_id, assistant_message, rag_selections: list) -> None:
    for selection in rag_selections:
        RagCitation.objects.create(
            organisation_id=organisation_id,
            message=assistant_message,
            document_id=selection.document_id,
            chunk_id=selection.chunk_id,
            score=selection.score,
            meta={
                "reason": selection.reason,
                **(selection.meta or {}),
            },
        )


def build_turn_review_payload(*, session, learner_message, assistant_message, rag_citations) -> dict:
    learner_payload = learner_message.llm_request_payload or {}
    return {
        "pilotage": {
            "conversation_profile": learner_payload.get("conversation_profile", "reflective_afest"),
            "conversation_progress": learner_payload.get("conversation_progress", {}),
            "ui_state": learner_payload.get("ui_state", {}),
            "session_memory": learner_payload.get("session_memory", {}),
        },
        "session": {
            "id": str(session.id),
            "learner_id": str(session.learner_id),
            "group_id": str(session.group_id) if session.group_id else None,
            "current_phase": session.current_phase,
            "manual_phase_override": session.manual_phase_override,
        },
        "learner_message": {
            "id": str(learner_message.id),
            "role": learner_message.role,
            "content": learner_message.content,
            "created_at": learner_message.created_at.isoformat(),
            "llm_request_payload": learner_payload,
        },
        "assistant_message": {
            "id": str(assistant_message.id),
            "role": assistant_message.role,
            "content": assistant_message.content,
            "created_at": assistant_message.created_at.isoformat(),
            "llm_response_payload": assistant_message.llm_response_payload,
        },
        "rag_citations": [
            {
                "id": str(citation.id),
                "document_id": str(citation.document_id),
                "chunk_id": str(citation.chunk_id),
                "score": citation.score,
                "meta": citation.meta,
            }
            for citation in rag_citations
        ],
    }
