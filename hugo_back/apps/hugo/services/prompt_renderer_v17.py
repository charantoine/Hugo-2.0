from __future__ import annotations

from dataclasses import dataclass

from apps.hugo.domain.conversation_decision_v17 import ConversationDecisionV17, to_legacy_conversation_decision
from apps.hugo.domain.turn_state_v17 import TurnStateV17, to_legacy_turn_state
from apps.hugo.services.prompt_renderer import render_with_tutor_prompt


@dataclass
class TutorPromptProfile:
    session: object
    tutor_prompt: object | None
    teaching_plan: object | None
    competence_brief: object | None
    learner_message: str
    context: object
    rag_chunks: list[str] | None = None


@dataclass
class RenderedPrompt:
    system_prompt: str
    user_prompt: str


def _v17_guidance_block(state: TurnStateV17, decision: ConversationDecisionV17) -> str:
    conversation_profile = str((decision.metadata or {}).get("conversation_profile") or "reflective_afest")
    lines = [
        "Directives P0 1.7 :",
        f"- conversation_profile : {conversation_profile}",
        f"- response_mode : {decision.response_mode}",
        f"- target_question_count : {decision.target_question_count}",
        f"- coverage_status : {state.coverage_status}",
        f"- learner_speech_act : {state.learner_speech_act}",
        f"- last_learner_act : {state.last_learner_act}",
    ]
    if decision.blocked_question_topics:
        lines.append("- blocked_question_topics : " + ", ".join(decision.blocked_question_topics[:6]))
    if decision.response_mode in {"recap", "evaluation", "closure"}:
        lines.append("- Réponds en texte continu, sans liste, sans checklist et sans rouvrir un nouveau chantier.")
    if decision.target_question_count <= 0:
        lines.append("- Ne pose aucune question finale.")
    if decision.response_mode == "evaluation":
        lines.append("- Si tu mentionnes des compétences, reste prudent et non scolaire.")
    if decision.response_mode == "assist":
        lines.append("- Donne une aide courte, concrète, puis au plus une relance cohérente.")
    return "\n".join(lines)


def render_tutor_prompt_v17(
    context,
    state: TurnStateV17,
    decision: ConversationDecisionV17,
    profile: TutorPromptProfile,
) -> RenderedPrompt:
    legacy_state = to_legacy_turn_state(state)
    legacy_decision = to_legacy_conversation_decision(decision)
    if profile.tutor_prompt:
        rendered = render_with_tutor_prompt(
            tutor_prompt=profile.tutor_prompt,
            session=profile.session,
            ctx=context,
            content=profile.learner_message,
            teaching_plan=profile.teaching_plan,
            competence_brief=profile.competence_brief,
            turn_state=legacy_state,
            conversation_decision=legacy_decision,
            rag_chunks=list(profile.rag_chunks or []),
        )
        system_prompt = rendered.system_prompt + "\n\n" + _v17_guidance_block(state, decision)
        user_prompt = rendered.user_prompt
        return RenderedPrompt(system_prompt=system_prompt, user_prompt=user_prompt)

    from apps.hugo.services.context_builder import _build_afest_prompts_legacy

    system_prompt, user_prompt = _build_afest_prompts_legacy(
        profile.session,
        profile.learner_message,
        context,
        session_phase=state.session_phase,
        max_questions=decision.target_question_count,
    )
    system_prompt += "\n\n" + _v17_guidance_block(state, decision)
    return RenderedPrompt(system_prompt=system_prompt, user_prompt=user_prompt)
