"""C9-OPS-03 — Smoke API memory-summary for LEARNER (cluster 10).

Verifies GET /hugo/sessions/{id}/memory-summary/ returns governed intra-conversation
payload without raw learner verbatim.
"""
import json

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.hugo.models import HugoMessage, HugoSession, LearnerThemeMemory

VERBATIM_MARKER = "SMOKE_MEMORY_SUMMARY_VERBATIM_DO_NOT_EXPOSE"


@pytest.mark.django_db
def test_memory_summary_smoke_learner_no_verbatim(
    api_client: APIClient,
    learner_user,
    organisation,
    group,
):
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
    )
    HugoMessage.objects.create(
        organisation=organisation,
        session=session,
        role=HugoMessage.Role.LEARNER,
        content=VERBATIM_MARKER,
        llm_request_payload={
            "turn_state": {
                "covered_points": ["smoke_fact_confirmed"],
                "remaining_open_points": ["smoke_open_point"],
            }
        },
    )
    LearnerThemeMemory.objects.create(
        organisation=organisation,
        learner=learner_user,
        theme_key="Smoke theme",
        stabilised_points=["structured point only"],
        open_loops=[],
        persistent_difficulties=[],
        knowledge_status="derived_provisional",
        last_conversation=session,
    )

    api_client.force_authenticate(user=learner_user)
    url = reverse("session_memory_summary", kwargs={"session_id": str(session.id)})
    response = api_client.get(url)

    assert response.status_code == 200
    body = response.data
    assert body["session_memory"]["memory_scope"] == "intra_conversation"
    assert body["session_memory"]["session_id"] == str(session.id)
    assert "smoke_fact_confirmed" in json.dumps(body["session_memory"])
    assert VERBATIM_MARKER not in json.dumps(body)
    assert "theme_memories" in body
    assert len(body["theme_memories"]) >= 1
    assert body["theme_memories"][0]["theme_key"] == "Smoke theme"
    assert VERBATIM_MARKER not in json.dumps(body["theme_memories"])
