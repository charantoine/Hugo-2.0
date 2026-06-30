from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional
from django.conf import settings

from apps.hugo.domain.conversation_profile import ConversationPosture
from apps.hugo.domain.schemas import (
    ConversationDecision,
    ConversationProgress,
    LearnerStateSlice,
    LearningStage,
    PedagogicalProfile,
    CompetenceBrief,
    SessionMemorySummary,
    TurnState,
    UiState,
    normalize_session_phase,
)
from apps.hugo.models import HugoSession, TutorPrompt, LearnerState
from apps.hugo.services.conversation_profile import resolve_conversation_profile
from apps.hugo.services.conversation_progress_calculator import build_conversation_progress_contract
from apps.hugo.services.conversation_progress import build_conversation_progress
from apps.hugo.services.context_builder import build_hugo_context, _resolve_tutor_prompt
from apps.hugo.services.decision_engine import decide_conversation
from apps.hugo.services.phase_decider import decide_next_phase
from apps.hugo.services.p0_classifier import classify_p0_turn_state
from apps.hugo.services.posture_selector import resolve_posture
from apps.hugo.services.quality_tracker import update_session_analytics
from apps.hugo.services.rag_support import select_rag_chunks
from apps.hugo.services.trainer_playbook_resolver import load_trainer_playbook_for_session
from apps.hugo.services.conduct_profile_resolver import resolve_conduct_profile
from apps.hugo.services.teaching_plan_builder import build_teaching_plan
from apps.hugo.services.prompt_renderer import render_with_tutor_prompt
from apps.hugo.services.session_memory import build_session_memory
from apps.hugo.services.tracing import build_prompt_sources
from apps.hugo.services.turn_state_analyzer import analyze_turn_state
from apps.hugo.services.ui_state_builder import build_ui_state


@dataclass
class HugoTurn:
    system_prompt: str
    user_prompt: str
    tutor_prompt: Optional[TutorPrompt]
    teaching_plan: Optional[Any] = None
    effective_phase: str = "exploration"
    next_phase: str = "exploration"
    phase_decision: Optional[dict[str, Any]] = None
    p0_classifier: Optional[dict[str, Any]] = None
    turn_state: Optional[TurnState] = None
    conversation_decision: Optional[ConversationDecision] = None
    rag_selections: Optional[list[Any]] = None
    prompt_sources: Optional[dict] = None
    conversation_profile: str = "reflective_afest"
    conversation_progress: Optional[ConversationProgress] = None
    session_memory: Optional[SessionMemorySummary] = None
    ui_state: Optional[UiState] = None


def _p0_v17_enabled() -> bool:
    return bool(getattr(settings, "HUGO_P0_V17_ENABLED", False))


def _normalize_phase(value: Any) -> Optional[str]:
    phase = normalize_session_phase(value, default="")
    return phase or None


def _resolve_effective_phase(
    session: HugoSession,
    user_input: Dict[str, Any],
) -> str:
    request_phase = _normalize_phase(user_input.get("session_phase"))
    if request_phase:
        return request_phase
    manual_override = _normalize_phase(getattr(session, "manual_phase_override", None))
    if manual_override:
        return manual_override
    current_phase = _normalize_phase(getattr(session, "current_phase", None))
    if current_phase:
        return current_phase
    return HugoSession.SessionPhase.EXPLORATION


def _recent_learner_history(session: HugoSession, limit: int = 6) -> list[str]:
    try:
        rows = session.messages.filter(role="LEARNER").order_by("-created_at")[:limit]
    except Exception:
        return []
    out: list[str] = []
    for row in rows:
        content = str(getattr(row, "content", "") or "").strip()
        if content:
            out.append(content)
    return list(reversed(out))


def _build_focus_candidates_from_context(ctx) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for item in ctx.items_to_focus:
        uncovered = [c for c in item.criteria if c.coverage_status != "covered"]
        if not uncovered:
            continue
        primary = sorted(uncovered, key=lambda c: c.order_index)[0]
        candidates.append(
            {
                "item_id": item.id,
                "label": item.title,
                "item_code": item.code,
                "block_code": item.block_code,
                "block_label": item.block_label,
                "criterion_id": primary.id,
                "criterion_code": primary.code,
                "criterion_label": primary.label,
                "covered_criteria_codes": item.covered_criteria_codes,
                "coach_questions": item.coach_questions,
                "common_mistakes": item.common_mistakes,
                "example_situations": item.example_situations,
                "example_evidence": item.example_evidence,
                "linked_documents": item.linked_documents,
                "tasks": item.tasks,
                "primary_task_code": item.tasks[0]["task_code"] if item.tasks else "",
                "primary_task_label": item.tasks[0]["task_label"] if item.tasks else "",
                "activity_code": item.tasks[0]["activity_code"] if item.tasks else "",
                "activity_label": item.tasks[0]["activity_label"] if item.tasks else "",
            }
        )
    return candidates


def _build_minimal_learner_state_slice(session: HugoSession, ctx) -> LearnerStateSlice:
    """
    Minimal implementation derived from existing LearnerState, without changing schema.
    """
    ls = (
        LearnerState.objects.filter(
            organisation_id=session.organisation_id,
            learner_id=session.learner_id,
        )
        .order_by("-updated_at")
        .first()
    )
    learner_id = str(session.learner_id)
    group_id = str(session.group_id) if session.group_id else None

    return LearnerStateSlice(
        learner_id=learner_id,
        group_id=group_id,
        focus_candidates=_build_focus_candidates_from_context(ctx),
        open_action_items=list((ls.open_action_items or []) if ls else []),
        signals={},
    )


def _build_minimal_learning_stage(session: HugoSession) -> LearningStage:
    """
    Placeholder learning stage; can be refined later.
    """
    group_id = str(session.group_id) if session.group_id else ""
    return LearningStage(
        group_id=group_id,
        item_id="",
        stage="intermediate",
        expected_level_now="participe",
        final_target_level="maîtrise",
        priority="medium",
        intermediate_objective_label="",
    )


def _build_minimal_pedagogical_profile(session: HugoSession) -> PedagogicalProfile:
    """
    Minimal pedagogical profile; future versions may consume hugo_config and overlays.
    """
    group_id = str(session.group_id) if session.group_id else ""
    return PedagogicalProfile(
        group_id=group_id,
        item_id="",
        focus_weights={"task": 0.3, "reasoning": 0.5, "metacognition": 0.2},
        directive_level="balanced",
        risk_sensitivity="normal",
        coach_questions_typed=[],
        critical_mistakes=[],
        exemplar_situations=[],
    )


def _build_minimal_competence_brief() -> CompetenceBrief:
    """
    Minimal competence brief; can be populated from referentials later.
    """
    return CompetenceBrief(
        item_id="",
        label="",
        key_criteria=[],
        expected_evidence=[],
        critical_mistakes=[],
        typical_situations=[],
        preferred_coach_questions=[],
    )


def build_hugo_turn(session: HugoSession, user_input: Dict[str, Any]) -> HugoTurn:
    """
    High-level orchestrator building a single Hugo turn.

    Returns a structured turn payload with rendered prompts and planning metadata.
    """
    ctx = build_hugo_context(session)

    content = user_input.get("content", "")
    resolved_posture = resolve_posture(
        session=session,
        user_message=content,
        explicit_posture=user_input.get("posture"),
    )
    tutor_prompt: Optional[TutorPrompt] = _resolve_tutor_prompt(session, posture=resolved_posture.value)
    learner_slice = _build_minimal_learner_state_slice(session, ctx)
    learning_stage = _build_minimal_learning_stage(session)
    pedagogical_profile = _build_minimal_pedagogical_profile(session)
    competence_brief = _build_minimal_competence_brief()
    max_questions_per_turn = (
        tutor_prompt.max_questions_per_turn
        if tutor_prompt and tutor_prompt.max_questions_per_turn
        else 1
    )
    effective_phase = _resolve_effective_phase(session, user_input)
    posture_profile = resolve_conduct_profile(resolved_posture, session.organisation, session=session)
    max_questions_per_turn = min(max_questions_per_turn, int(posture_profile.get("max_questions_per_turn", 1) or 1))
    user_input_for_plan = dict(user_input)
    user_input_for_plan["session_phase"] = effective_phase
    heuristic_turn_state = analyze_turn_state(session=session, user_input=user_input_for_plan, ctx=ctx)
    p0_classifier_result = classify_p0_turn_state(
        session=session,
        tutor_prompt=tutor_prompt,
        user_input=user_input_for_plan,
        ctx=ctx,
        heuristic_state=heuristic_turn_state,
    )
    turn_state = p0_classifier_result.turn_state
    v17_state = None
    v17_decision = None
    speech_act_result = None
    conversation_profile = resolve_conversation_profile(
        session=session,
        tutor_prompt=tutor_prompt,
        learner_content=content,
        turn_state=turn_state,
    )
    conversation_profile = resolved_posture.value or conversation_profile
    turn_state.posture_constraints = {
        "posture": resolved_posture.value,
        "max_questions_per_turn": posture_profile.get("max_questions_per_turn", 1),
        "forbidden_moves": list(posture_profile.get("forbidden_moves", [])),
        "description": posture_profile.get("description", ""),
    }
    if _p0_v17_enabled():
        from apps.hugo.domain.conversation_decision_v17 import to_legacy_conversation_decision
        from apps.hugo.domain.turn_state_v17 import to_legacy_turn_state
        from apps.hugo.services.decision_engine_v17 import decide_conversation_v17
        from apps.hugo.services.learner_speech_act_classifier import classify_learner_speech_act
        from apps.hugo.services.state_reconciler_v17 import reconcile_turn_state_v17

        recent_history = _recent_learner_history(session)
        speech_act_result = classify_learner_speech_act(content, recent_history)
        v17_state = reconcile_turn_state_v17(
            legacy_state=turn_state,
            speech_act_result=speech_act_result,
            p0_classifier=p0_classifier_result.to_dict(),
            recent_history=recent_history,
        )
        conversation_profile = resolve_conversation_profile(
            session=session,
            tutor_prompt=tutor_prompt,
            learner_content=content,
            turn_state=v17_state,
            speech_act_result=speech_act_result,
        )
        conversation_profile = resolved_posture.value or conversation_profile
        v17_decision = decide_conversation_v17(v17_state, conversation_profile=conversation_profile)
        bounded_question_count = max(0, min(max_questions_per_turn, v17_decision.target_question_count))
        v17_decision.effective_max_questions_this_turn = bounded_question_count
        v17_decision.target_question_count = bounded_question_count
        v17_decision.number_of_questions = min(v17_decision.number_of_questions, bounded_question_count)
        turn_state = to_legacy_turn_state(v17_state)
        conversation_decision = to_legacy_conversation_decision(v17_decision)
    else:
        conversation_decision = decide_conversation(turn_state)
        conversation_decision.metadata = {
            **dict(conversation_decision.metadata or {}),
            "conversation_profile": conversation_profile,
        }
        bounded_question_count = max(
            0,
            min(max_questions_per_turn, conversation_decision.number_of_questions),
        )

    teaching_plan = build_teaching_plan(
        learner_slice=learner_slice,
        learning_stage=learning_stage,
        pedagogical_profile=pedagogical_profile,
        user_input=user_input_for_plan,
        max_questions_per_turn=bounded_question_count,
        conversation_profile=conversation_profile,
        turn_state=turn_state,
        conversation_decision=conversation_decision,
    )
    if _p0_v17_enabled() and v17_state and v17_decision:
        from apps.hugo.services.teaching_plan_builder_v17 import apply_v17_decision_to_teaching_plan

        teaching_plan = apply_v17_decision_to_teaching_plan(
            teaching_plan,
            v17_state,
            v17_decision,
            effective_phase,
        )
    phase_decision = decide_next_phase(
        session=session,
        tutor_prompt=tutor_prompt,
        current_phase=turn_state.session_phase,
        user_input=user_input_for_plan,
        deterministic_next_phase=teaching_plan.next_session_phase or teaching_plan.session_phase,
        turn_state=turn_state,
        conversation_decision=conversation_decision,
    )
    teaching_plan.next_session_phase = phase_decision.next_phase
    teaching_plan.session_phase = turn_state.session_phase
    teaching_plan.max_questions_this_turn = bounded_question_count
    teaching_plan.phase_source = phase_decision.source
    rag_selections = select_rag_chunks(
        session=session,
        learner_text=content,
        teaching_plan=teaching_plan,
        turn_state=turn_state,
        conversation_decision=conversation_decision,
        conversation_profile=conversation_profile,
    )
    trainer_playbook = load_trainer_playbook_for_session(session)
    trainer_playbook_block = trainer_playbook.block_text if not trainer_playbook.is_empty() else ""
    traces_count = session.traces.count()
    evidence_count = session.evidence.count()
    learner_turns_count = session.messages.filter(role="LEARNER").count()
    conversation_progress = build_conversation_progress(
        session=session,
        turn_state=turn_state,
        conversation_decision=conversation_decision,
        teaching_plan=teaching_plan,
        conversation_profile=conversation_profile,
        rag_selections=rag_selections,
        traces_count=traces_count,
    )
    session_memory = build_session_memory(
        session,
        turn_state=turn_state,
        conversation_progress=conversation_progress,
    )
    contract_progress = build_conversation_progress_contract(
        session_id=str(session.id),
        turn_state=turn_state,
        decision=conversation_decision,
        posture=resolved_posture,
        previous_progress_raw=session.conversation_progress,
    )
    analytics_state = dict(getattr(session, "analytics_state", {}) or {})
    if getattr(session, "posture", "") and session.posture != resolved_posture.value:
        analytics_state["posture_switch_count"] = int(analytics_state.get("posture_switch_count", 0) or 0) + 1
    session.analytics_state = analytics_state
    session.posture = resolved_posture.value
    session.conversation_progress = contract_progress.to_dict()
    update_session_analytics(session, contract_progress)
    session.save(update_fields=["posture", "conversation_progress", "analytics_state", "updated_at"])
    ui_state = build_ui_state(
        progress=conversation_progress,
        session_memory=session_memory,
        conversation_decision=conversation_decision,
        turn_state=turn_state,
        rag_selections=rag_selections,
        traces_count=traces_count,
        evidence_count=evidence_count,
        learner_turns_count=learner_turns_count,
        gamification_profile=str((getattr(tutor_prompt, "metadata", {}) or {}).get("gamification_profile") or "B"),
    )
    prompt_sources = build_prompt_sources(ctx, rag_selections)

    if _p0_v17_enabled() and v17_state and v17_decision:
        from apps.hugo.services.prompt_renderer_v17 import TutorPromptProfile, render_tutor_prompt_v17

        profile = TutorPromptProfile(
            session=session,
            tutor_prompt=tutor_prompt,
            teaching_plan=teaching_plan,
            competence_brief=competence_brief,
            learner_message=content,
            context=ctx,
            rag_chunks=[selection.prompt_snippet() for selection in rag_selections],
            trainer_playbook_block=trainer_playbook_block,
        )
        rendered_v17 = render_tutor_prompt_v17(
            context=ctx,
            state=v17_state,
            decision=v17_decision,
            profile=profile,
        )
        return HugoTurn(
            system_prompt=rendered_v17.system_prompt,
            user_prompt=rendered_v17.user_prompt,
            tutor_prompt=tutor_prompt,
            teaching_plan=teaching_plan,
            effective_phase=turn_state.session_phase,
            next_phase=phase_decision.next_phase,
            phase_decision={
                "source": phase_decision.source,
                "confidence": phase_decision.confidence,
                "reason": phase_decision.reason,
                "fallback_reason": phase_decision.fallback_reason,
                "classifier_provider": phase_decision.classifier_provider,
                "classifier_model": phase_decision.classifier_model,
                "runtime_config": phase_decision.runtime_config or {},
                "runtime_config_source": phase_decision.runtime_config_source or {},
                "adapter_next_phase": phase_decision.adapter_next_phase,
            },
            p0_classifier={**p0_classifier_result.to_dict(), "contract_version": "1.7"},
            turn_state=turn_state,
            conversation_decision=conversation_decision,
            rag_selections=rag_selections,
            prompt_sources=prompt_sources,
            conversation_profile=conversation_profile,
            conversation_progress=conversation_progress,
            session_memory=session_memory,
            ui_state=ui_state,
        )

    if not tutor_prompt:
        # Fallback to legacy behaviour via context_builder.
        from apps.hugo.services.context_builder import _build_afest_prompts_legacy

        system_prompt, user_prompt = _build_afest_prompts_legacy(
            session,
            content,
            ctx,
            session_phase=turn_state.session_phase,
            max_questions=bounded_question_count,
        )
        system_prompt += (
            "\n\nEtat conversationnel synthétique:\n"
            f"- phase: {turn_state.session_phase}\n"
            f"- clarity: {turn_state.episode_clarity}\n"
            f"- move: {conversation_decision.pedagogical_move}\n"
            f"- questions_max: {bounded_question_count}"
        )
        return HugoTurn(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            tutor_prompt=None,
            teaching_plan=teaching_plan,
            effective_phase=turn_state.session_phase,
            next_phase=phase_decision.next_phase,
            phase_decision={
                "source": phase_decision.source,
                "confidence": phase_decision.confidence,
                "reason": phase_decision.reason,
                "fallback_reason": phase_decision.fallback_reason,
                "classifier_provider": phase_decision.classifier_provider,
                "classifier_model": phase_decision.classifier_model,
                "runtime_config": phase_decision.runtime_config or {},
                "runtime_config_source": phase_decision.runtime_config_source or {},
                "adapter_next_phase": phase_decision.adapter_next_phase,
            },
            p0_classifier=p0_classifier_result.to_dict(),
            turn_state=turn_state,
            conversation_decision=conversation_decision,
            rag_selections=rag_selections,
            prompt_sources=prompt_sources,
            conversation_profile=conversation_profile,
            conversation_progress=conversation_progress,
            session_memory=session_memory,
            ui_state=ui_state,
        )

    rendered = render_with_tutor_prompt(
        tutor_prompt=tutor_prompt,
        session=session,
        ctx=ctx,
        content=content,
        teaching_plan=teaching_plan,
        competence_brief=competence_brief,
        turn_state=turn_state,
        conversation_decision=conversation_decision,
        rag_chunks=[selection.prompt_snippet() for selection in rag_selections],
        trainer_playbook_block=trainer_playbook_block,
    )
    return HugoTurn(
        system_prompt=rendered.system_prompt,
        user_prompt=rendered.user_prompt,
        tutor_prompt=tutor_prompt,
        teaching_plan=teaching_plan,
        effective_phase=turn_state.session_phase,
        next_phase=phase_decision.next_phase,
        phase_decision={
            "source": phase_decision.source,
            "confidence": phase_decision.confidence,
            "reason": phase_decision.reason,
            "fallback_reason": phase_decision.fallback_reason,
            "classifier_provider": phase_decision.classifier_provider,
            "classifier_model": phase_decision.classifier_model,
            "runtime_config": phase_decision.runtime_config or {},
            "runtime_config_source": phase_decision.runtime_config_source or {},
            "adapter_next_phase": phase_decision.adapter_next_phase,
        },
        p0_classifier=p0_classifier_result.to_dict(),
        turn_state=turn_state,
        conversation_decision=conversation_decision,
        rag_selections=rag_selections,
        prompt_sources=prompt_sources,
        conversation_profile=conversation_profile,
        conversation_progress=conversation_progress,
        session_memory=session_memory,
        ui_state=ui_state,
    )

