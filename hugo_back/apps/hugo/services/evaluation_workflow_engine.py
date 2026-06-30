from __future__ import annotations

from dataclasses import dataclass, field

from apps.hugo.domain.conversation_profile import ConversationProgress, SessionMaturityLevel


@dataclass
class EvaluationContext:
    session_id: str
    conversation_evidence: list[dict] = field(default_factory=list)
    referential_items: list[dict] = field(default_factory=list)
    trainer_knowledge_items: list[dict] = field(default_factory=list)
    trainer_directives: str = ""
    maturity_at_trigger: SessionMaturityLevel = SessionMaturityLevel.RED
    is_early_trigger: bool = False


def assemble_evaluation_context(
    *,
    session,
    progress: ConversationProgress,
    policy,
    referential_items: list[dict],
    trainer_knowledge_items: list[dict],
) -> EvaluationContext:
    evidence: list[dict] = []
    for branch in list(progress.active_branches or []):
        evidence.append(
            {
                "branch_id": branch.branch_id,
                "theme": branch.theme_label,
                "objective": branch.objective_label,
                "maturity": branch.exploration_level.value,
                "reason_codes": list(branch.reason_codes or []),
                "referential_item_id": branch.referential_item_id or "",
            }
        )

    return EvaluationContext(
        session_id=str(session.id),
        conversation_evidence=evidence,
        referential_items=list(referential_items or []),
        trainer_knowledge_items=list(trainer_knowledge_items or []),
        trainer_directives=str(getattr(policy, "trainer_directives", "") or "").strip(),
        maturity_at_trigger=progress.overall_maturity,
        is_early_trigger=progress.overall_maturity != SessionMaturityLevel.GREEN,
    )
