"""Load validated trainer playbook items for Hugo conversation prompts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from apps.hugo.domain.conversation_profile import KnowledgeItemStatus
from apps.hugo.models import TrainerKnowledgeItem

PLAYBOOK_CONTENT_TYPES = frozenset(
    {
        "frequent_error",
        "reasoning_chain",
        "reference_rule",
        "procedure",
        "mastery_criterion",
        "technical_point",
    }
)


@dataclass
class TrainerPlaybook:
    """Structured playbook ready for system-prompt injection (internal directives)."""

    block_text: str = ""
    items: list[dict[str, Any]] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not self.block_text.strip()


def _item_in_group_scope(item_meta: dict[str, Any], group_id: str | None) -> bool:
    scope = item_meta.get("scope_group_ids") or item_meta.get("group_ids") or []
    if not scope:
        return True
    if not group_id:
        return False
    normalized = {str(g).strip() for g in scope if str(g).strip()}
    return str(group_id) in normalized


def _format_playbook_item(item: TrainerKnowledgeItem) -> str:
    meta = dict(item.meta or {})
    situation = str(meta.get("situation_cue") or "").strip()
    desired = str(meta.get("desired_response") or "").strip()
    lines = [f"- [{item.content_type}] {item.content.strip()}"]
    if situation:
        lines.append(f"  Situation : {situation}")
    if desired:
        lines.append(f"  Réaction attendue : {desired}")
    return "\n".join(lines)


def load_trainer_playbook_for_session(session: Any) -> TrainerPlaybook:
    """
    Return validated trainer knowledge items scoped to the session organisation/group.
    Only items with status validated_trainer are injected (internal system block).
    """
    organisation_id = getattr(session, "organisation_id", None)
    if not organisation_id:
        return TrainerPlaybook()

    group_id = str(getattr(session, "group_id", "") or "") or None
    qs = (
        TrainerKnowledgeItem.objects.filter(
            organisation_id=organisation_id,
            status=KnowledgeItemStatus.VALIDATED_TRAINER.value,
        )
        .order_by("-updated_at")[:40]
    )

    selected: list[dict[str, Any]] = []
    formatted_lines: list[str] = []
    for item in qs:
        meta = dict(item.meta or {})
        visibility = str(meta.get("visibility") or "internal_only").strip().lower()
        if visibility not in {"internal_only", "learner_citable"}:
            visibility = "internal_only"
        if not _item_in_group_scope(meta, group_id):
            continue
        if item.content_type not in PLAYBOOK_CONTENT_TYPES and not meta.get("situation_cue"):
            continue
        selected.append(
            {
                "id": str(item.id),
                "content_type": item.content_type,
                "content": item.content,
                "meta": meta,
                "visibility": visibility,
            }
        )
        formatted_lines.append(_format_playbook_item(item))

    if not formatted_lines:
        return TrainerPlaybook()

    block = (
        "Consignes formateur (bloc interne — ne pas reciter mot pour mot a l'apprenant) :\n"
        + "\n".join(formatted_lines)
    )
    return TrainerPlaybook(block_text=block, items=selected)
