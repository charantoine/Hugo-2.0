import pytest

from apps.hugo.analytics.cohort_dashboard import get_cohort_metrics
from apps.hugo.domain.conversation_profile import ConversationPosture, ConversationProgress, SessionMaturityLevel
from apps.hugo.models import HugoSession, TrainerKnowledgeItem
from apps.hugo.services.quality_tracker import record_session_signal


@pytest.mark.django_db
def test_record_session_signal_persists_quality_snapshot(organisation, learner_user, group):
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        posture="reflective_afest",
        analytics_state={
            "posture_switch_count": 1,
            "synthesis_requested": True,
            "evaluation_requested": False,
            "dispersion_turns": 2,
            "stuck_red_turns": 3,
            "active_branches_max": 2,
        },
    )
    progress = ConversationProgress(
        session_id=str(session.id),
        posture=ConversationPosture.REFLECTIVE_AFEST,
        active_branches_count=2,
        overall_maturity=SessionMaturityLevel.ORANGE,
        evaluation_eligible=False,
    )

    signal = record_session_signal(session, progress, turn_count=4)

    assert signal.total_turns == 4
    assert signal.posture_switches == 1
    assert signal.dispersion_turns == 2


@pytest.mark.django_db
def test_cohort_metrics_surface_provisional_alerts(organisation, learner_user, group):
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
        posture="knowledge_review",
        analytics_state={
            "posture_switch_count": 0,
            "synthesis_requested": False,
            "evaluation_requested": True,
            "dispersion_turns": 0,
            "stuck_red_turns": 1,
            "active_branches_max": 2,
        },
    )
    progress = ConversationProgress(
        session_id=str(session.id),
        posture=ConversationPosture.KNOWLEDGE_REVIEW,
        active_branches_count=2,
        overall_maturity=SessionMaturityLevel.RED,
        evaluation_eligible=False,
    )
    record_session_signal(session, progress, turn_count=3)
    TrainerKnowledgeItem.objects.create(
        organisation=organisation,
        content="Critère provisoire",
        status="derived_provisional",
    )

    metrics = get_cohort_metrics(str(organisation.id), days=30)

    assert metrics["total_sessions"] == 1
    assert metrics["false_evaluation_rate"] == 1.0
    assert metrics["provisional_criteria_unvalidated"] == 1.0
