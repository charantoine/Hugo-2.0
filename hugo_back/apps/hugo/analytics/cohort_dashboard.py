from __future__ import annotations

from datetime import timedelta

from django.db.models import Avg, Count, Q
from django.utils import timezone

from apps.hugo.models import ConversationQualitySignal, LearnerThemeMemory, TrainerKnowledgeItem


def get_cohort_metrics(organisation_id: str, days: int = 30) -> dict:
    since = timezone.now() - timedelta(days=days)
    queryset = ConversationQualitySignal.objects.filter(
        organisation_id=organisation_id,
        created_at__gte=since,
    )
    total = queryset.count()
    if total == 0:
        return {"total_sessions": 0}

    avg_branches = queryset.aggregate(value=Avg("active_branches_max"))["value"] or 0
    stuck_red = queryset.filter(final_maturity="red").count()
    forced_reflective_red = queryset.filter(
        posture="reflective_afest",
        final_maturity="red",
        synthesis_requested=True,
    ).count()
    knowledge_sessions = queryset.filter(posture="knowledge_review").count()
    knowledge_single_branch = queryset.filter(
        posture="knowledge_review",
        active_branches_max__lte=1,
    ).count()
    false_eval = queryset.filter(evaluation_requested=True, evaluation_was_eligible=False).count()
    eval_total = queryset.filter(evaluation_requested=True).count()
    switched = queryset.filter(posture_switches__gt=0).count()
    provisional = TrainerKnowledgeItem.objects.filter(
        organisation_id=organisation_id,
        status="derived_provisional",
    ).count()
    total_knowledge = TrainerKnowledgeItem.objects.filter(organisation_id=organisation_id).count()

    return {
        "total_sessions": total,
        "avg_branches_per_session": round(avg_branches, 2),
        "pct_stuck_red": round(stuck_red / total, 2),
        "pct_forced_reflective_red": round(forced_reflective_red / total, 2),
        "pct_knowledge_single_branch": round(knowledge_single_branch / knowledge_sessions, 2) if knowledge_sessions else 1.0,
        "false_evaluation_rate": round(false_eval / eval_total, 2) if eval_total else 0.0,
        "posture_switch_mid_session": round(switched / total, 2),
        "provisional_criteria_unvalidated": round(provisional / total_knowledge, 2) if total_knowledge else 0.0,
        "alert_dispersion": avg_branches > 2.5,
        "alert_stuck_red": (stuck_red / total) > 0.40,
        "alert_forced_reflective_red": (forced_reflective_red / total) > 0.20,
        "alert_false_eval": (false_eval / eval_total) > 0.10 if eval_total else False,
    }


def get_per_learner_progress(organisation_id: str, learner_id: str) -> list[dict]:
    records = LearnerThemeMemory.objects.filter(
        organisation_id=organisation_id,
        learner_id=learner_id,
    ).order_by("-updated_at")
    return [
        {
            "theme": record.theme_key,
            "status": record.knowledge_status,
            "stabilised": len(record.stabilised_points or []),
            "open": len(record.open_loops or []),
            "difficulties": len(record.persistent_difficulties or []),
            "last_session": str(record.last_conversation_id) if record.last_conversation_id else "",
        }
        for record in records
    ]
