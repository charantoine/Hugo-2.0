"""End-to-end API test: learner message → rag_citations with reference_course priority."""
from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role, User
from apps.hugo.models import HugoMessage, HugoSession, TutorPrompt
from apps.library.models import Document, DocumentChunk, GroupDocument, RagCitation
from apps.library.tests.rag_test_helpers import COMMON_CHUNK_TEXT
from apps.referentials.models import Group


@override_settings(HUGO_DEBUG_TRACING=True)
class RagCitationsEndToEndTests(TestCase):
    @patch("apps.hugo.views_sessions.complete_with_provider")
    def test_message_post_returns_reference_course_rag_citation(self, complete_mock):
        organisation = Organisation.objects.create(name="Org RAG E2E")
        group = Group.objects.create(organisation=organisation, name="G RAG")
        learner = User.objects.create_user(
            username="learner_rag_e2e",
            password="pass",
            organisation=organisation,
            role=Role.LEARNER,
        )
        tutor_prompt = TutorPrompt.objects.create(
            organisation=organisation,
            code="afest_rag_e2e",
            name="AFEST RAG E2E",
            prompt_type=TutorPrompt.PromptType.AFEST_HUGO,
            is_default=True,
            system_template="{base_system_intro}\n{documents_block}",
            user_template="{situation_content}",
            max_questions_per_turn=2,
        )
        session = HugoSession.objects.create(
            organisation=organisation,
            learner=learner,
            group=group,
            tutor_prompt=tutor_prompt,
            phase_classifier_enabled=False,
        )

        ref_title = "Poly Reference Consignation E2E"
        ref_doc = Document.objects.create(
            organisation=organisation,
            title=ref_title,
            meta={"conversation_role": "reference_course", "visibility": "learner_citable"},
        )
        support_doc = Document.objects.create(
            organisation=organisation,
            title="Support generique",
            meta={"conversation_role": "support", "visibility": "learner_citable"},
        )
        for doc in (ref_doc, support_doc):
            GroupDocument.objects.create(
                organisation=organisation,
                group=group,
                document=doc,
                status=GroupDocument.Status.ACTIVE,
            )
            DocumentChunk.objects.create(
                document=doc,
                content=COMMON_CHUNK_TEXT,
                meta={"document_meta": dict(doc.meta or {})},
            )

        complete_mock.return_value = (
            "Qu'as-tu verifie sur la consignation du tableau ?",
            {
                "provider": "ollama",
                "model_used": "mistral",
                "request_payload": {"mock": True},
                "raw_response": {"ok": True},
            },
        )

        client = APIClient()
        client.force_authenticate(user=learner)
        url = reverse("message_list_create", kwargs={"session_id": str(session.id)})
        response = client.post(
            url,
            {
                "content": (
                    "Je dois verifier la procedure de consignation et la checklist securite "
                    "sur le tableau electrique avant mise sous tension norme nf c15-100."
                ),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200, response.content)
        citations = response.data.get("rag_citations") or []
        self.assertTrue(citations, "Expected rag_citations in API response")

        titles = [str(c.get("document_title") or "") for c in citations]
        self.assertTrue(
            any(ref_title in t for t in titles),
            f"Expected reference_course title in citations, got {titles}",
        )

        assistant_msg = HugoMessage.objects.filter(
            session=session,
            role=HugoMessage.Role.ASSISTANT,
        ).latest("created_at")
        self.assertTrue(RagCitation.objects.filter(message=assistant_msg).exists())

        learner_msg = HugoMessage.objects.filter(
            session=session,
            role=HugoMessage.Role.LEARNER,
        ).latest("created_at")
        self.assertIn("rag", learner_msg.llm_request_payload)
        rag_payload = learner_msg.llm_request_payload.get("rag")
        if isinstance(rag_payload, list) and rag_payload:
            rag_titles = [str(item.get("document_title") or "") for item in rag_payload]
            self.assertIn(ref_title, rag_titles)
        elif isinstance(rag_payload, dict):
            rag_titles = [
                sel.get("document_title", "")
                for sel in (rag_payload.get("selections") or [])
            ]
            if rag_titles:
                self.assertIn(ref_title, rag_titles)
