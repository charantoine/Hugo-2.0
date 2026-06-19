import json

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.hugo.domain.schemas import SessionMemoryContract
from apps.hugo.models import HugoMessage, HugoSession, LearnerThemeMemory, TutorPrompt
from apps.hugo.services.hugo_orchestrator import build_hugo_turn
from apps.hugo.services.session_memory import build_session_memory, build_session_memory_contract


VERBATIM_MARKER = "VERBATIM_LEARNER_SECRET_CONTENT_9f3a2b1c"


@pytest.mark.django_db
def test_session_memory_contract_has_required_fields(organisation, learner_user, group):
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
    )
    contract = build_session_memory_contract(session=session)

    payload = contract.to_dict()
    assert payload["session_id"] == str(session.id)
    assert payload["updated_at"]
    assert payload["memory_scope"] == "intra_conversation"
    assert isinstance(payload["facts_confirmed"], list)
    assert isinstance(payload["open_points"], list)
    assert isinstance(payload["pending_actions"], list)
    assert SessionMemoryContract(**payload).memory_scope == "intra_conversation"


@pytest.mark.django_db
def test_session_memory_contract_excludes_verbatim_content(organisation, learner_user, group):
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
                "covered_points": ["episode_described"],
                "remaining_open_points": ["next_step_unclear"],
            }
        },
    )

    contract = build_session_memory_contract(session=session)
    serialized = json.dumps(contract.to_dict())

    assert VERBATIM_MARKER not in serialized
    assert "episode_described" in serialized


@pytest.mark.django_db
def test_build_session_memory_filters_messages_to_current_session_only(organisation, learner_user, group):
    session_a = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
    )
    session_b = HugoSession.objects.create(
        organisation=organisation,
        learner=learner_user,
        group=group,
    )
    HugoMessage.objects.create(
        organisation=organisation,
        session=session_b,
        role=HugoMessage.Role.LEARNER,
        content="ancien fil",
        llm_request_payload={
            "turn_state": {
                "covered_points": ["cross_session_point"],
                "remaining_open_points": ["cross_session_open"],
            }
        },
    )
    HugoMessage.objects.create(
        organisation=organisation,
        session=session_a,
        role=HugoMessage.Role.LEARNER,
        content="fil courant",
        llm_request_payload={
            "turn_state": {
                "covered_points": ["current_session_point"],
                "remaining_open_points": ["current_session_open"],
            }
        },
    )

    summary = build_session_memory(session_a)
    contract = summary.contract
    assert contract is not None
    assert "cross_session_point" not in contract.facts_confirmed
    assert "cross_session_open" not in contract.open_points
    assert "current_session_point" in contract.facts_confirmed
    assert "current_session_open" in contract.open_points
    assert summary.sessions_considered == 1


@pytest.mark.django_db
def test_build_hugo_turn_attaches_session_memory_contract(django_user_model, organisation, group):
    learner = django_user_model.objects.create(username="learner_contract", organisation=organisation)
    tutor_prompt = TutorPrompt.objects.create(
        organisation=organisation,
        code="afest_contract",
        name="AFEST contract",
        prompt_type=TutorPrompt.PromptType.AFEST_HUGO,
        is_default=True,
        system_template="{base_system_intro}",
        user_template="{situation_content}",
    )
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner,
        group=group,
        tutor_prompt=tutor_prompt,
        phase_classifier_enabled=False,
        p0_classifier_enabled=False,
    )

    turn = build_hugo_turn(session, {"content": "Je décris une situation concrète sur le terrain."})

    assert turn.session_memory is not None
    assert turn.session_memory.contract is not None
    assert turn.session_memory.contract.session_id == str(session.id)
    assert turn.session_memory.contract.memory_scope == "intra_conversation"
    assert turn.session_memory.to_dict()["session_memory"]["memory_scope"] == "intra_conversation"


@pytest.mark.django_db
def test_memory_summary_endpoint_exposes_session_and_theme_blocks(
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
    LearnerThemeMemory.objects.create(
        organisation=organisation,
        learner=learner_user,
        theme_key="Sécurité électrique",
        stabilised_points=["Couper l'alimentation avant intervention"],
        open_loops=["Vérifier la mise à la terre"],
        persistent_difficulties=[],
        knowledge_status="derived_provisional",
        last_conversation=session,
    )

    api_client.force_authenticate(user=learner_user)
    url = reverse("session_memory_summary", kwargs={"session_id": str(session.id)})
    response = api_client.get(url)

    assert response.status_code == 200
    assert "session_memory" in response.data
    assert "theme_memories" in response.data
    assert response.data["session_memory"]["session_id"] == str(session.id)
    assert response.data["session_memory"]["memory_scope"] == "intra_conversation"
    assert len(response.data["theme_memories"]) == 1
    assert response.data["theme_memories"][0]["theme_key"] == "Sécurité électrique"
    assert VERBATIM_MARKER not in json.dumps(response.data)
