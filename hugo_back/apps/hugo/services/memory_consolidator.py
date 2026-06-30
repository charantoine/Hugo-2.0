from __future__ import annotations

from typing import Optional

from apps.hugo.domain.conversation_profile import ConversationProgress, KnowledgeItemStatus
from apps.hugo.models import LearnerThemeMemory


def normalize_knowledge_status(raw_value: Optional[str]) -> KnowledgeItemStatus:
    try:
        return KnowledgeItemStatus(raw_value or KnowledgeItemStatus.DECLARED.value)
    except ValueError:
        return KnowledgeItemStatus.DECLARED


def consolidate_session(session, progress: ConversationProgress) -> list[LearnerThemeMemory]:
    updated_records: list[LearnerThemeMemory] = []
    for branch in progress.active_branches:
        record, _ = LearnerThemeMemory.objects.get_or_create(
            organisation_id=session.organisation_id,
            learner_id=session.learner_id,
            theme_key=branch.theme_label or "Progression de séance",
        )
        if branch.referential_item_id:
            record.referential_item_id = branch.referential_item_id

        stabilised = set(record.stabilised_points or [])
        open_loops = set(record.open_loops or [])
        difficulties = set(record.persistent_difficulties or [])

        if branch.exploration_level.value == "green":
            stabilised.add(branch.objective_label or branch.theme_label)
            open_loops.discard(branch.objective_label or branch.theme_label)
            difficulties.discard(branch.objective_label or branch.theme_label)
        elif branch.exploration_level.value == "orange":
            open_loops.add(branch.objective_label or branch.theme_label)
        else:
            difficulties.add(branch.objective_label or branch.theme_label)

        for code in branch.reason_codes or []:
            open_loops.add(code)
            stabilised.discard(code)

        current_status = normalize_knowledge_status(record.knowledge_status)
        if current_status == KnowledgeItemStatus.DERIVED_PROVISIONAL:
            next_status = KnowledgeItemStatus.DERIVED_PROVISIONAL
        else:
            next_status = current_status

        record.stabilised_points = sorted(stabilised)
        record.open_loops = sorted(open_loops)
        record.persistent_difficulties = sorted(difficulties)
        record.knowledge_status = next_status.value
        record.last_conversation = session
        record.save()
        updated_records.append(record)

    return updated_records
