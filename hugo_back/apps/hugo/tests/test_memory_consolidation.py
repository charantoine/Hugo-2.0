import pytest

from apps.hugo.domain.conversation_profile import ConversationBranch, ConversationPosture, ConversationProgress, KnowledgeItemStatus, SessionMaturityLevel
from apps.hugo.models import HugoSession, LearnerThemeMemory
from apps.hugo.services.memory_consolidator import consolidate_session


@pytest.mark.django_db
def test_memory_consolidation_creates_theme_memory(organisation, learner_user, group):
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
    )
    progress = ConversationProgress(
        session_id=str(session.id),
        posture=ConversationPosture.REFLECTIVE_AFEST,
        active_branches=[
            ConversationBranch(
                branch_id="b1",
                theme_label="Sécuriser le tableau",
                objective_label="Identifier la cause",
                exploration_level=SessionMaturityLevel.GREEN,
            )
        ],
        active_branches_count=1,
        overall_maturity=SessionMaturityLevel.GREEN,
    )

    records = consolidate_session(session, progress)

    assert len(records) == 1
    record = LearnerThemeMemory.objects.get()
    assert record.theme_key == "Sécuriser le tableau"
    assert "Identifier la cause" in record.stabilised_points


@pytest.mark.django_db
def test_memory_consolidation_never_auto_validates_provisional_status(organisation, learner_user, group):
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
    )
    memory = LearnerThemeMemory.objects.create(
        organisation=organisation,
        learner=learner_user,
        theme_key="Diagnostic moteur",
        knowledge_status=KnowledgeItemStatus.DERIVED_PROVISIONAL.value,
    )
    progress = ConversationProgress(
        session_id=str(session.id),
        posture=ConversationPosture.DIAGNOSTIC,
        active_branches=[
            ConversationBranch(
                branch_id="b1",
                theme_label="Diagnostic moteur",
                objective_label="Clarifier le symptôme",
                exploration_level=SessionMaturityLevel.GREEN,
            )
        ],
        active_branches_count=1,
        overall_maturity=SessionMaturityLevel.GREEN,
    )

    consolidate_session(session, progress)
    memory.refresh_from_db()

    assert memory.knowledge_status == KnowledgeItemStatus.DERIVED_PROVISIONAL.value
