import pytest
from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from apps.hugo.models import HugoMessage, HugoSession, TutorPrompt
from apps.hugo.services.hugo_orchestrator import build_hugo_turn
from apps.hugo.services.context_builder import build_hugo_context


@pytest.mark.django_db
def test_build_hugo_turn_uses_tutorprompt_and_teaching_plan(django_user_model, organisation, group):
    learner = django_user_model.objects.create(username="learner_addendum", organisation=organisation)
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner,
        group=group,
        phase_classifier_enabled=False,
    )
    tutor_prompt = TutorPrompt.objects.create(
        organisation=organisation,
        code="afest_default_v2",
        name="AFEST default v2",
        prompt_type=TutorPrompt.PromptType.AFEST_HUGO,
        is_default=True,
        system_template="{base_system_intro}\nPhase: {session_phase}\nFocus: {focus_competence}",
        user_template="[{ui_focus_label}] {situation_content}",
    )
    session.tutor_prompt = tutor_prompt
    session.save()

    user_input = {"content": "Je décris une situation de test.", "session_phase": "exploration"}
    turn = build_hugo_turn(session, user_input)

    assert "Phase: exploration" in turn.system_prompt
    assert "Je décris une situation de test." in turn.user_prompt
    assert turn.turn_state is not None
    assert turn.conversation_decision is not None


@pytest.mark.django_db
@patch("apps.hugo.views_sessions.complete_with_provider")
def test_message_endpoint_respects_tutorprompt_flow(complete_mock, api_client: APIClient, django_user_model, organisation, group):
    learner = django_user_model.objects.create_user(
        username="learner_api",
        password="pass",
        organisation=organisation,
    )
    tutor_prompt = TutorPrompt.objects.create(
        organisation=organisation,
        code="afest_default_v2",
        name="AFEST default v2",
        prompt_type=TutorPrompt.PromptType.AFEST_HUGO,
        is_default=True,
        system_template="{base_system_intro}\nPhase: {session_phase}",
        user_template="{situation_content}",
    )
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner,
        group=group,
        tutor_prompt=tutor_prompt,
        phase_classifier_enabled=False,
    )

    complete_mock.return_value = ("Que s'est-il passé en premier ?", {"provider": "ollama", "model_used": "mistral"})
    api_client.force_authenticate(user=learner)
    url = reverse("message_list_create", kwargs={"session_id": str(session.id)})
    response = api_client.post(url, {"content": "Situation via API"}, format="json")

    assert response.status_code == 200
    assert response.data["assistant_display_variants"]["default_variant"] == "short"
    assert response.data["phase_decision_source"] in {"state_adapter", "fallback_rules", "llm_classifier"}
    assert "turn_state" in response.data
    assert "conversation_decision" in response.data


@pytest.mark.django_db
@override_settings(HUGO_DEBUG_TRACING=True)
@patch("apps.hugo.views_sessions.complete_with_provider")
def test_message_endpoint_keeps_reflection_block_layout_when_cap_is_one(
    complete_mock, api_client: APIClient, django_user_model, organisation, group
):
    learner = django_user_model.objects.create_user(
        username="learner_reflection_guardrail",
        password="pass",
        organisation=organisation,
    )
    tutor_prompt = TutorPrompt.objects.create(
        organisation=organisation,
        code="afest_reflection_guardrail",
        name="AFEST reflection guardrail",
        prompt_type=TutorPrompt.PromptType.AFEST_HUGO,
        is_default=True,
        system_template="{base_system_intro}\nPhase: {session_phase}",
        user_template="{situation_content}",
        output_format_mode=TutorPrompt.OutputFormatMode.REFLECTION_BLOCK,
        max_questions_per_turn=3,
    )
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner,
        group=group,
        tutor_prompt=tutor_prompt,
        phase_classifier_enabled=False,
    )

    complete_mock.return_value = (
        "C'est toujours un choc quand un gros court-circuit arrive.\n"
        "Peux-tu me dire ce qui t'a fait penser qu'il fallait changer cette prise ?\n"
        "Qu'as-tu verifie avant de couper l'alimentation pour la remplacer ?",
        {"provider": "ollama", "model_used": "mistral"},
    )
    api_client.force_authenticate(user=learner)
    url = reverse("message_list_create", kwargs={"session_id": str(session.id)})
    response = api_client.post(url, {"content": "j'ai change une prise et ca a tout fait sauter !"}, format="json")

    assert response.status_code == 200
    assert response.data["content"].startswith("C'est toujours un choc quand un gros court-circuit arrive.")
    assert "1. Peux-tu me dire ce qui t'a fait penser qu'il fallait changer cette prise ?" in response.data["content"]
    assert "2. Qu'as-tu verifie avant de couper l'alimentation pour la remplacer ?" in response.data["content"]
    assert response.data["assistant_display_variants"]["short"] == response.data["content"]
    assert response.data["assistant_display_variants"]["long"].startswith("C'est toujours un choc quand un gros court-circuit arrive.")

    learner_msg = HugoMessage.objects.filter(session=session, role=HugoMessage.Role.LEARNER).latest("created_at")
    assistant_msg = HugoMessage.objects.filter(session=session, role=HugoMessage.Role.ASSISTANT).latest("created_at")
    assert learner_msg.llm_request_payload["resolved_output_mode"] == TutorPrompt.OutputFormatMode.REFLECTION_BLOCK
    assert learner_msg.llm_request_payload["effective_max_questions_this_turn"] == 2
    assert assistant_msg.assistant_display_variants["short"] == assistant_msg.content
    assert assistant_msg.assistant_display_variants["default_variant"] == "short"

    messages_response = api_client.get(url)
    assert messages_response.status_code == 200
    last_message = messages_response.data["messages"][-1]
    assert last_message["assistant_display_variants"]["short"] == assistant_msg.content
    assert "long" in last_message["assistant_display_variants"]


@pytest.mark.django_db
@override_settings(HUGO_DEBUG_TRACING=False)
@patch("apps.hugo.views_sessions.complete_with_provider")
def test_message_endpoint_persists_tutor_prompt_snapshot_when_tracing_disabled(
    complete_mock, api_client: APIClient, django_user_model, organisation, group
):
    learner = django_user_model.objects.create_user(
        username="learner_snapshot_tp",
        password="pass",
        organisation=organisation,
    )
    tutor_prompt = TutorPrompt.objects.create(
        organisation=organisation,
        code="snapshot_tp",
        name="Snapshot TP",
        prompt_type=TutorPrompt.PromptType.AFEST_HUGO,
        is_default=True,
        system_template="{base_system_intro}\nSNAP",
        user_template="{situation_content}",
        output_format_mode=TutorPrompt.OutputFormatMode.REFLECTION_BLOCK,
        max_questions_per_turn=2,
        max_tokens=200,
    )
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner,
        group=group,
        tutor_prompt=tutor_prompt,
        phase_classifier_enabled=False,
    )

    complete_mock.return_value = ("Réponse courte.", {"provider": "ollama", "model_used": "mistral"})
    api_client.force_authenticate(user=learner)
    url = reverse("message_list_create", kwargs={"session_id": str(session.id)})
    response = api_client.post(url, {"content": "Test snapshot"}, format="json")

    assert response.status_code == 200
    learner_msg = HugoMessage.objects.filter(session=session, role=HugoMessage.Role.LEARNER).latest("created_at")
    payload = learner_msg.llm_request_payload
    assert payload["resolved_tutor_prompt_id"] == str(tutor_prompt.id)
    assert "resolved_output_mode" not in payload
    snap = payload["tutor_prompt_snapshot"]
    assert snap["code"] == "snapshot_tp"
    assert snap["output_format_mode"] == TutorPrompt.OutputFormatMode.REFLECTION_BLOCK
    assert snap["max_questions_per_turn"] == 2
    assert snap["max_tokens"] == 200
    assert snap["system_template"] == "{base_system_intro}\nSNAP"
    assert snap["user_template"] == "{situation_content}"

