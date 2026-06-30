"""Reliability scoring, RAG citations, and reindex behaviour after meta PATCH."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role, User
from apps.hugo.domain.schemas import ConversationDecision
from apps.hugo.models import HugoMessage, HugoSession, TutorPrompt
from apps.hugo.services.rag_support import select_rag_chunks
from apps.library.indexing import index_document_chunks
from apps.library.models import Document, DocumentChunk, GroupDocument
from apps.library.tests.rag_test_helpers import COMMON_CHUNK_TEXT, rag_teaching_plan, rag_turn_state
from apps.referentials.models import Group


def _rag_decision():
    return ConversationDecision(
        primary_intent="guide",
        pedagogical_move="analyze",
        number_of_questions=1,
        question_style="open",
        should_explain_briefly=False,
        should_recap=False,
        should_encourage=False,
        should_reframe=False,
        should_close=False,
        response_constraints=[],
        reason_codes=[],
        metadata={},
    )


class ReliabilityRagSelectionTests(TestCase):
    def setUp(self):
        self.organisation = Organisation.objects.create(name="Org Rel RAG")
        self.group = Group.objects.create(organisation=self.organisation, name="G Rel")
        self.session = SimpleNamespace(
            organisation_id=self.organisation.id,
            group_id=self.group.id,
        )

    def _link_indexed_doc(self, title: str, reliability: str) -> Document:
        doc = Document.objects.create(
            organisation=self.organisation,
            title=title,
            source_text=COMMON_CHUNK_TEXT,
            meta={
                "origin": "trainer",
                "trainer_reliability": reliability,
                "conversation_role": "support",
                "visibility": "learner_citable",
            },
        )
        index_document_chunks(doc, chunk_size=400, overlap=40)
        GroupDocument.objects.create(
            organisation=self.organisation,
            group=self.group,
            document=doc,
            status=GroupDocument.Status.ACTIVE,
        )
        return doc

    def test_high_reliability_trainer_doc_ranks_above_low(self):
        low = self._link_indexed_doc("Brouillon formateur", "1")
        high = self._link_indexed_doc("Reference formateur", "4")
        selections = select_rag_chunks(
            session=self.session,
            learner_text="procedure tableau electrique consignation verification norme nf checklist securite",
            teaching_plan=rag_teaching_plan(),
            turn_state=rag_turn_state(),
            conversation_decision=_rag_decision(),
            limit=5,
        )
        self.assertGreaterEqual(len(selections), 2)
        self.assertEqual(selections[0].document_id, str(high.id))
        scores = {str(s.document_id): s.score for s in selections}
        self.assertGreater(scores[str(high.id)], scores[str(low.id)])

    def test_draft_reliability_still_selectable_but_not_first_among_peers(self):
        draft = self._link_indexed_doc("Draft only", "1")
        star4 = self._link_indexed_doc("Star four", "4")
        selections = select_rag_chunks(
            session=self.session,
            learner_text="procedure tableau electrique consignation verification",
            teaching_plan=rag_teaching_plan(),
            turn_state=rag_turn_state(),
            conversation_decision=_rag_decision(),
            limit=3,
        )
        ids = [s.document_id for s in selections]
        self.assertIn(str(draft.id), ids)
        self.assertEqual(ids[0], str(star4.id))


class ReliabilityReindexBehaviourTests(TestCase):
    def setUp(self):
        self.organisation = Organisation.objects.create(name="Org Reindex")
        self.group = Group.objects.create(organisation=self.organisation, name="G Reindex")
        self.trainer = User.objects.create_user(
            username="trainer_reindex",
            password="pass",
            organisation=self.organisation,
            role=Role.TRAINER,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.trainer)
        self.session = SimpleNamespace(
            organisation_id=self.organisation.id,
            group_id=self.group.id,
        )

    def _rag_top_doc_id(self, doc: Document) -> str | None:
        GroupDocument.objects.get_or_create(
            organisation=self.organisation,
            group=self.group,
            document=doc,
            defaults={"status": GroupDocument.Status.ACTIVE},
        )
        selections = select_rag_chunks(
            session=self.session,
            learner_text="procedure tableau electrique consignation verification norme",
            teaching_plan=rag_teaching_plan(),
            turn_state=rag_turn_state(),
            conversation_decision=_rag_decision(),
            limit=3,
        )
        return selections[0].document_id if selections else None

    def test_patch_reliability_without_reindex_keeps_stale_chunk_meta(self):
        doc = Document.objects.create(
            organisation=self.organisation,
            title="Stale meta test",
            source_text=COMMON_CHUNK_TEXT,
            meta={
                "origin": "trainer",
                "trainer_reliability": "2",
                "conversation_role": "support",
                "visibility": "learner_citable",
            },
        )
        index_document_chunks(doc)
        chunk = DocumentChunk.objects.filter(document=doc).first()
        self.assertEqual(chunk.meta["document_meta"]["trainer_reliability"], "2")

        patch = self.client.patch(
            reverse("document_detail", kwargs={"document_id": doc.id}),
            {"meta": {"trainer_reliability": "4"}},
            format="json",
        )
        self.assertEqual(patch.status_code, 200)
        doc.refresh_from_db()
        self.assertEqual(doc.meta["trainer_reliability"], "4")

        chunk.refresh_from_db()
        self.assertEqual(
            chunk.meta["document_meta"]["trainer_reliability"],
            "2",
            "Chunk meta is snapshot-at-index; PATCH alone must not update it",
        )

    def test_reindex_after_patch_propagates_reliability_to_chunks(self):
        doc = Document.objects.create(
            organisation=self.organisation,
            title="Reindex test",
            source_text=COMMON_CHUNK_TEXT,
            meta={
                "origin": "trainer",
                "trainer_reliability": "2",
                "conversation_role": "support",
                "visibility": "learner_citable",
            },
        )
        index_document_chunks(doc)
        self.client.patch(
            reverse("document_detail", kwargs={"document_id": doc.id}),
            {"meta": {"trainer_reliability": "4"}},
            format="json",
        )
        reindex = self.client.post(reverse("document_index", kwargs={"document_id": doc.id}), {}, format="json")
        self.assertEqual(reindex.status_code, 200)

        chunk = DocumentChunk.objects.filter(document=doc).first()
        self.assertEqual(chunk.meta["document_meta"]["trainer_reliability"], "4")

    def test_reindex_changes_rag_ranking_between_two_similar_docs(self):
        doc_low = Document.objects.create(
            organisation=self.organisation,
            title="Doc low rel",
            source_text=COMMON_CHUNK_TEXT,
            meta={
                "origin": "trainer",
                "trainer_reliability": "4",
                "conversation_role": "support",
                "visibility": "learner_citable",
            },
        )
        doc_high = Document.objects.create(
            organisation=self.organisation,
            title="Doc high rel",
            source_text=COMMON_CHUNK_TEXT,
            meta={
                "origin": "trainer",
                "trainer_reliability": "2",
                "conversation_role": "support",
                "visibility": "learner_citable",
            },
        )
        for doc in (doc_low, doc_high):
            index_document_chunks(doc)
            GroupDocument.objects.create(
                organisation=self.organisation,
                group=self.group,
                document=doc,
                status=GroupDocument.Status.ACTIVE,
            )

        self.assertEqual(self._rag_top_doc_id(doc_low), str(doc_low.id))

        self.client.patch(
            reverse("document_detail", kwargs={"document_id": doc_high.id}),
            {"meta": {"trainer_reliability": "4"}},
            format="json",
        )
        # Without reindex: ranking unchanged
        self.assertEqual(self._rag_top_doc_id(doc_low), str(doc_low.id))

        self.client.post(reverse("document_index", kwargs={"document_id": doc_high.id}), {}, format="json")
        top_after = self._rag_top_doc_id(doc_high)
        self.assertEqual(top_after, str(doc_high.id))


@override_settings(HUGO_DEBUG_TRACING=True)
class ReliabilityRagCitationsApiTests(TestCase):
    @patch("apps.hugo.views_sessions.complete_with_provider")
    def test_message_rag_citations_prefer_high_reliability_trainer_doc(self, complete_mock):
        organisation = Organisation.objects.create(name="Org Rel API")
        group = Group.objects.create(organisation=organisation, name="G Rel API")
        learner = User.objects.create_user(
            username="learner_rel_api",
            password="pass",
            organisation=organisation,
            role=Role.LEARNER,
        )
        tutor_prompt = TutorPrompt.objects.create(
            organisation=organisation,
            code="rel_rag",
            name="Rel RAG",
            prompt_type=TutorPrompt.PromptType.AFEST_HUGO,
            is_default=True,
            system_template="{base_system_intro}\n{documents_block}",
            user_template="{situation_content}",
        )
        session = HugoSession.objects.create(
            organisation=organisation,
            learner=learner,
            group=group,
            tutor_prompt=tutor_prompt,
            phase_classifier_enabled=False,
        )
        title_low = "Formateur brouillon **"
        title_high = "Formateur reference ****"
        for title, rel in ((title_low, "1"), (title_high, "4")):
            doc = Document.objects.create(
                organisation=organisation,
                title=title,
                meta={
                    "origin": "trainer",
                    "trainer_reliability": rel,
                    "conversation_role": "support",
                    "visibility": "learner_citable",
                },
            )
            DocumentChunk.objects.create(
                document=doc,
                content=COMMON_CHUNK_TEXT,
                meta={"document_meta": dict(doc.meta or {})},
            )
            GroupDocument.objects.create(
                organisation=organisation,
                group=group,
                document=doc,
                status=GroupDocument.Status.ACTIVE,
            )

        complete_mock.return_value = (
            "Qu'as-tu verifie ?",
            {"provider": "ollama", "model_used": "mistral", "request_payload": {}},
        )
        client = APIClient()
        client.force_authenticate(user=learner)
        response = client.post(
            reverse("message_list_create", kwargs={"session_id": str(session.id)}),
            {
                "content": (
                    "Je dois verifier la procedure de consignation et la checklist securite "
                    "sur le tableau electrique norme nf c15-100."
                ),
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        citations = response.data.get("rag_citations") or []
        self.assertGreaterEqual(len(citations), 2)
        scores_by_title = {c.get("document_title"): c.get("score") for c in citations}
        self.assertIn(title_low, scores_by_title)
        self.assertIn(title_high, scores_by_title)
        self.assertGreater(
            float(scores_by_title[title_high]),
            float(scores_by_title[title_low]),
            "High trainer_reliability must score above draft in RAG selections",
        )

        assistant = HugoMessage.objects.filter(session=session, role=HugoMessage.Role.ASSISTANT).latest("created_at")
        top_citation = assistant.rag_citations.select_related("document").order_by("-score").first()
        self.assertEqual(top_citation.document.title, title_high)
