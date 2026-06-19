"""Tasks: recalc learner_state after trace validation."""
from celery import shared_task
from django.db import transaction


@shared_task
def recalc_learner_state(learner_id, group_id, organisation_id):
    """Update learner_state cache (skills_matrix, summary)."""
    from .models import LearnerState, Trace
    with transaction.atomic():
        LearnerState.objects.update_or_create(
            organisation_id=organisation_id,
            learner_id=learner_id,
            group_id=group_id,
            defaults={
                "skills_matrix": {},
                "missing_coverage": [],
                "open_action_items": [],
                "summary": "",
            },
        )
