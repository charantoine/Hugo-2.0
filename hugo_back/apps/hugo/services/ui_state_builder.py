from __future__ import annotations

from typing import Any, Optional

from apps.hugo.domain.conversation_profile import (
    ConversationPosture,
    ConversationProgress as ContractConversationProgress,
    SessionMaturityLevel,
    UIState as ContractUIState,
)
from apps.hugo.domain.posture_transitions import can_transition
from apps.hugo.domain.schemas import ConversationProgress, SessionMemorySummary, UiState
from apps.hugo.services.cta_ui_state import (
    build_cta_evaluation,
    build_cta_synthesis,
    legacy_button_states_from_cta,
)

SCENE_STEPS = [
    {
        "id": "raconter",
        "label": "Raconter",
        "hint": "Poser calmement la situation vécue.",
    },
    {
        "id": "comprendre",
        "label": "Comprendre",
        "hint": "Repérer ce qui bloque ou ce qui compte vraiment.",
    },
    {
        "id": "decider",
        "label": "Décider",
        "hint": "Choisir une prochaine action réaliste.",
    },
    {
        "id": "retenir",
        "label": "Retenir",
        "hint": "Transformer l'expérience en apprentissage clair.",
    },
    {
        "id": "transmettre",
        "label": "Transmettre",
        "hint": "Préparer un mini-bilan partageable.",
    },
]

PROFILE_LABELS = {
    "diagnostic": "Diagnostic",
    "reflective_afest": "Réflexif AFEST",
    "knowledge_review": "Savoirs / révision",
}

LEARNER_DISPLAY_PROFILE_VALUES = frozenset({"youth", "adult", "professional"})


def normalize_learner_display_profile(value: str | None) -> str:
    normalized = str(value or "professional").strip().lower()
    return normalized if normalized in LEARNER_DISPLAY_PROFILE_VALUES else "professional"


def resolve_learner_display_profile_for_session(*, request, session=None) -> str:
    explicit = None
    if hasattr(request, "data") and isinstance(getattr(request, "data", None), dict):
        explicit = request.data.get("learner_display_profile")
    explicit = explicit or request.query_params.get("learner_display_profile")
    if explicit not in (None, ""):
        return normalize_learner_display_profile(explicit)

    group_value = None
    org_value = None
    if session is not None:
        group = getattr(session, "group", None)
        if group is not None:
            group_value = getattr(group, "learner_display_profile", None)
        organisation = getattr(session, "organisation", None)
        if organisation is not None:
            org_value = getattr(organisation, "default_learner_display_profile", None)

    return normalize_learner_display_profile(group_value or org_value or "professional")


def _build_conversation_mode(progress: ContractConversationProgress) -> dict[str, Any]:
    posture = progress.posture
    allowed_posture_transitions: list[dict[str, Any]] = []
    can_switch = False
    for target in ConversationPosture:
        if target == posture:
            continue
        allowed, warning = can_transition(posture, target, progress.overall_maturity)
        allowed_posture_transitions.append(
            {
                "code": target.value,
                "label": PROFILE_LABELS.get(target.value, target.value),
                "allowed": allowed,
                "warning": warning or None,
            }
        )
        if allowed:
            can_switch = True
    switch_warning = None
    if posture == ConversationPosture.KNOWLEDGE_REVIEW:
        _, warning = can_transition(
            posture,
            ConversationPosture.REFLECTIVE_AFEST,
            progress.overall_maturity,
        )
        switch_warning = warning or None
    switch_locked_reason = None
    if not can_switch:
        switch_locked_reason = (
            "Le changement de mode n’est pas disponible dans le contexte actuel de la séance."
        )
    return {
        "code": posture.value,
        "label": PROFILE_LABELS.get(posture.value, posture.value),
        "can_switch": can_switch,
        "switch_warning": switch_warning,
        "allowed_posture_transitions": allowed_posture_transitions,
        "switch_locked_reason": switch_locked_reason,
    }


def _resolve_priority_branch_label(progress: ContractConversationProgress) -> str | None:
    if progress.priority_branch_id:
        for branch in progress.active_branches:
            if branch.branch_id == progress.priority_branch_id:
                return branch.theme_label or branch.objective_label or None
    for branch in progress.active_branches:
        if branch.is_active:
            return branch.theme_label or branch.objective_label or None
    return None


def _build_scene_progress(progress: ConversationProgress) -> dict[str, Any]:
    return {
        "current_step_index": progress.stage_index,
        "current_step": SCENE_STEPS[progress.stage_index],
        "percent": progress.percent,
        "steps": [
            {
                **step,
                "state": "done" if index < progress.stage_index else ("current" if index == progress.stage_index else "locked"),
            }
            for index, step in enumerate(SCENE_STEPS)
        ],
        "covered_points": list(progress.covered_points or []),
        "remaining_open_points": list(progress.remaining_open_points or []),
    }


def _build_quest_cards(progress: ConversationProgress) -> list[dict[str, Any]]:
    quests: list[dict[str, Any]] = []
    for index, point in enumerate(list(progress.remaining_open_points or [])[:3]):
        quests.append(
            {
                "id": f"carry-{index}",
                "title": "Faire avancer la scène" if index else progress.active_objective,
                "description": point,
                "status": "next",
            }
        )
    if len(quests) < 3 and progress.stage_index < 2:
        quests.append(
            {
                "id": "clarify-scene",
                "title": "Clarifier la situation",
                "description": "Donner un fait concret ou une vérification déjà réalisée pour stabiliser le diagnostic.",
                "status": "next",
            }
        )
    if len(quests) < 3 and progress.stage_index < 4:
        quests.append(
            {
                "id": "next-step",
                "title": "Préparer la suite",
                "description": progress.next_recommended_action,
                "status": "next",
            }
        )
    if len(quests) < 3 and progress.can_summarize:
        quests.append(
            {
                "id": "mini-bilan",
                "title": "Préparer le mini-bilan",
                "description": "Transformer ce qui est déjà clair en synthèse courte et partageable.",
                "status": "next",
            }
        )
    return quests[:3]


def _build_persistent_objects(
    progress: ConversationProgress,
    memory: SessionMemorySummary,
    traces_count: int,
    evidence_count: int,
) -> list[dict[str, Any]]:
    return [
        {
            "id": "trace-ready",
            "kind": "trace",
            "title": "Trace prête à relire" if progress.can_summarize else "Trace en préparation",
            "description": (
                "La scène est assez mûre pour produire une trace utile."
                if progress.can_summarize
                else "La scène progresse ; la trace sera plus robuste quand l'objectif actif sera stabilisé."
            ),
            "status": "ready" if progress.can_summarize else "building",
            "meta": f"{traces_count} trace(s)" if traces_count else "Encore en construction",
        },
        {
            "id": "session-memory",
            "kind": "memory",
            "title": "Mémoire de parcours",
            "description": memory.summary,
            "status": "visible" if (memory.active_themes or memory.open_action_items) else "building",
            "meta": memory.memory_scope,
        },
        {
            "id": "progress-capsule",
            "kind": "capsule",
            "title": "Capsule de progrès",
            "description": (
                "Un progrès réutilisable est déjà visible dans cette scène."
                if progress.stage_index >= 3
                else "La capsule apparaîtra dès qu’un vrai pas en avant sera suffisamment stabilisé."
            ),
            "status": "ready" if progress.stage_index >= 3 else "building",
            "meta": f"{evidence_count} preuve(s)" if evidence_count else progress.current_step_label,
        },
    ]


def _build_symbolic_rewards(progress: ConversationProgress, learner_turns_count: int) -> list[dict[str, Any]]:
    return [
        {
            "id": "badge-scene",
            "kind": "badge",
            "label": "Premier pas",
            "description": "Débloqué dès que la scène est vraiment lancée.",
            "unlocked": learner_turns_count > 0,
        },
        {
            "id": "theme-scene",
            "kind": "theme",
            "label": "Thème Horizon" if progress.stage_index >= 2 else "Thème Élan",
            "description": "Un thème léger, aligné sur la progression réelle.",
            "unlocked": progress.stage_index >= 1,
        },
        {
            "id": "avatar-hugo",
            "kind": "avatar",
            "label": "Hugo Focus" if progress.stage_index >= 3 else "Hugo Complice",
            "description": "Une variation symbolique sans effet sur le moteur.",
            "unlocked": progress.stage_index >= 3,
        },
    ]


def build_ui_state(
    *,
    progress: ConversationProgress,
    session_memory: SessionMemorySummary,
    conversation_decision: Any,
    turn_state: Any,
    rag_selections: Optional[list[Any]] = None,
    traces_count: int = 0,
    evidence_count: int = 0,
    learner_turns_count: int = 0,
    gamification_profile: str = "B",
) -> UiState:
    rag_items = [
        {
            "document_id": selection.document_id,
            "title": selection.document_title,
            "reason": selection.reason,
            "score": round(float(selection.score), 2),
        }
        for selection in list(rag_selections or [])[:3]
    ]
    return UiState(
        header_badges=[
            {"id": "profile", "label": "Posture", "value": PROFILE_LABELS.get(progress.conversation_profile, progress.conversation_profile)},
            {"id": "objective", "label": "Objectif", "value": progress.active_objective},
            {"id": "branch", "label": "Fil actif", "value": progress.branch_label},
        ],
        scene_progress=_build_scene_progress(progress),
        quest_cards=_build_quest_cards(progress),
        persistent_objects=_build_persistent_objects(progress, session_memory, traces_count, evidence_count),
        symbolic_rewards=_build_symbolic_rewards(progress, learner_turns_count),
        supporting_documents=rag_items,
        session_memory=session_memory.to_dict(),
        tutor_signals={
            "current_phase": progress.tutor_signal_summary.get("current_phase", ""),
            "can_close_for_now": progress.closure_eligible,
            "closure_signal": str(getattr(turn_state, "closure_signal", "") or "none"),
            "recent_progress": str(getattr(turn_state, "recent_progress", "") or ""),
            "decision_move": str(getattr(conversation_decision, "pedagogical_move", "") or ""),
            "conversation_profile": progress.conversation_profile,
            "active_objective": progress.active_objective,
            "reason_codes": list(progress.reason_codes or []),
        },
        ui_visibility_flags={
            "frontend_mode": "engagement",
            "engagement_ui_enabled": True,
            "scene_progress_enabled": True,
            "persistent_objects_enabled": True,
            "symbolic_rewards_enabled": True,
            "documents_panel_enabled": True,
            "session_memory_enabled": True,
        },
        gamification_profile={
            "code": gamification_profile,
            "title": "Profil engagement",
        },
    )


def build_contract_ui_state(
    *,
    session,
    progress: ContractConversationProgress,
    gamification_profile: str = "B",
    learner_display_profile: str = "professional",
) -> ContractUIState:
    maturity = progress.overall_maturity
    if maturity == SessionMaturityLevel.GREEN:
        scene_label = "Synthétiser"
        scene_progress = 1.0
    elif maturity == SessionMaturityLevel.ORANGE:
        scene_label = "Explorer"
        scene_progress = 0.65
    else:
        scene_label = "Raconter"
        scene_progress = 0.25 if progress.active_branches_count else 0.0

    active_quest_label = (
        progress.missing_for_next_level[0]
        if progress.missing_for_next_level
        else ("Faire une synthèse" if progress.synthesis_eligible else "Poursuivre la conversation")
    )
    quest_progress = min(1.0, progress.active_branches_count / 3) if progress.active_branches_count else 0.0

    persistent_objects = [
        {
            "id": f"branch-{branch.branch_id}",
            "kind": "branch",
            "label": branch.theme_label or "Fil actif",
            "status": branch.exploration_level.value,
        }
        for branch in progress.active_branches[:3]
    ]

    cta_synthesis = build_cta_synthesis(session, progress)
    cta_evaluation = build_cta_evaluation(session, progress)
    synthesis_button_state, evaluation_button_state, evaluation_trigger_state, evaluation_trigger_message = (
        legacy_button_states_from_cta(
            progress=progress,
            cta_synthesis=cta_synthesis,
            cta_evaluation=cta_evaluation,
        )
    )

    return ContractUIState(
        scene_label=scene_label,
        scene_progress=scene_progress,
        active_quest_label=active_quest_label,
        quest_progress=quest_progress,
        maturity_color=maturity,
        synthesis_button_state=synthesis_button_state,
        evaluation_button_state=evaluation_button_state,
        evaluation_trigger_state=evaluation_trigger_state,
        evaluation_trigger_message=evaluation_trigger_message,
        persistent_objects=persistent_objects,
        gamification_profile=gamification_profile if gamification_profile in {"A", "B", "C"} else "B",
        conversation_mode=_build_conversation_mode(progress),
        learner_display_profile=normalize_learner_display_profile(learner_display_profile),
        cta_evaluation=cta_evaluation,
        cta_synthesis=cta_synthesis,
        dispersion_risk=bool(progress.dispersion_risk),
        priority_branch_label=_resolve_priority_branch_label(progress),
    )
