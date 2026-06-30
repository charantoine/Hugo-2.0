"""Message pipeline: validated TrainerKnowledgeItem → playbook block in LLM system prompt."""
from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role, User
from apps.hugo.domain.conversation_profile import KnowledgeItemStatus
from apps.hugo.models import HugoMessage, HugoSession, TrainerKnowledgeItem, TutorPrompt
from apps.referentials.models import Group


@override_settings(HUGO_DEBUG_TRACING=True)
class TrainerPlaybookPromptPipelineTests(TestCase):
    @patch("apps.hugo.views_sessions.complete_with_provider")
    def test_message_system_prompt_includes_validated_playbook_directive(self, complete_mock):
        organisation = Organisation.objects.create(name="Org Playbook Prompt")
        group = Group.objects.create(organisation=organisation, name="G Playbook")
        learner = User.objects.create_user(
            username="learner_playbook_prompt",
            password="pass",
            organisation=organisation,
            role=Role.LEARNER,
        )
        TrainerKnowledgeItem.objects.create(
            organisation=organisation,
            content="Toujours rappeler la consignation avant toute intervention.",
            content_type="frequent_error",
            status=KnowledgeItemStatus.VALIDATED_TRAINER.value,
            meta={
                "situation_cue": "oubli de consignation",
                "desired_response": "rappeler la procedure de consignation sans culpabiliser",
                "visibility": "internal_only",
            },
        )
        tutor_prompt = TutorPrompt.objects.create(
            organisation=organisation,
            code="afest_playbook",
            name="AFEST Playbook",
            prompt_type=TutorPrompt.PromptType.AFEST_HUGO,
            is_default=True,
            system_template="{base_system_intro}\n{documents_block}",
            user_template="{situation_content}",
            max_questions_per_turn=1,
        )
        session = HugoSession.objects.create(
            organisation=organisation,
            learner=learner,
            group=group,
            tutor_prompt=tutor_prompt,
            phase_classifier_enabled=False,
        )

        complete_mock.return_value = (
            "As-tu bien consigné avant d'intervenir ?",
            {"provider": "ollama", "model_used": "mistral", "request_payload": {"mock": True}},
        )

        client = APIClient()
        client.force_authenticate(user=learner)
        url = reverse("message_list_create", kwargs={"session_id": str(session.id)})
        response = client.post(
            url,
            {"content": "J'ai oublié la consignation sur le tableau, que faire ?"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)

        learner_msg = HugoMessage.objects.filter(
            session=session,
            role=HugoMessage.Role.LEARNER,
        ).latest("created_at")
        system_prompt = str(learner_msg.llm_request_payload.get("system_prompt") or "")
        self.assertIn("Consignes formateur", system_prompt)
        self.assertIn("consignation", system_prompt.lower())
        self.assertIn("frequent_error", system_prompt)
