"""Tests: document origin stamping and trainer reliability RAG scoring."""
from __future__ import annotations

from types import SimpleNamespace

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role, User
from apps.hugo.domain.schemas import ConversationDecision, TurnState
from apps.hugo.services.rag_support import select_rag_chunks
from apps.library.document_meta import (
    RELIABILITY_SCORE_BOOST,
    TRAINER_ORIGIN_BOOST,
    prepare_document_meta_for_create,
    score_document_meta_boost,
)
from apps.library.models import Document, DocumentChunk, GroupDocument
from apps.library.tests.rag_test_helpers import COMMON_CHUNK_TEXT, rag_teaching_plan, rag_turn_state
from apps.referentials.models import Group


class DocumentOriginStampingTests(TestCase):
    def setUp(self):
        self.organisation = Organisation.objects.create(name="Org Origin")
        self.trainer = User.objects.create_user(
            username="trainer_origin",
            password="pass",
            organisation=self.organisation,
            role=Role.TRAINER,
        )
        self.admin = User.objects.create_user(
            username="admin_origin",
            password="pass",
            organisation=self.organisation,
            role=Role.ORGADMIN,
        )
        self.client = APIClient()

    def test_trainer_create_stamps_origin_trainer(self):
        self.client.force_authenticate(user=self.trainer)
        response = self.client.post(
            reverse("document_list_create"),
            {
                "title": "Cours formateur",
                "source_text": "procedure tableau",
                "meta": {
                    "conversation_role": "reference_course",
                    "origin": "admin",
                    "trainer_reliability": "4",
                },
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.data["meta"]["origin"], "trainer")
        self.assertEqual(response.data["meta"]["trainer_reliability"], "4")

    def test_orgadmin_create_stamps_origin_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse("document_list_create"),
            {"title": "Doc admin", "source_text": "texte", "meta": {"origin": "trainer"}},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["meta"]["origin"], "admin")

    def test_patch_preserves_origin(self):
        self.client.force_authenticate(user=self.trainer)
        create = self.client.post(
            reverse("document_list_create"),
            {"title": "Patch origin", "source_text": "x"},
            format="json",
        )
        doc_id = create.data["id"]
        patch = self.client.patch(
            reverse("document_detail", kwargs={"document_id": doc_id}),
            {"meta": {"origin": "admin", "trainer_reliability": "2"}},
            format="json",
        )
        self.assertEqual(patch.status_code, 200)
        self.assertEqual(patch.data["meta"]["origin"], "trainer")
        self.assertEqual(patch.data["meta"]["trainer_reliability"], "2")

    def test_prepare_document_meta_for_create_unit(self):
        meta = prepare_document_meta_for_create(self.trainer, {"origin": "admin"})
        self.assertEqual(meta["origin"], "trainer")
        self.assertEqual(meta["trainer_reliability"], "3")


class TrainerReliabilityScoringTests(TestCase):
    def test_trainer_origin_outranks_admin_with_same_role(self):
        base = 2.0
        trainer_score, _ = score_document_meta_boost(
            {
                "origin": "trainer",
                "trainer_reliability": "3",
                "conversation_role": "support",
            },
            "reflective_afest",
        )
        admin_score, _ = score_document_meta_boost(
            {"origin": "admin", "conversation_role": "support"},
            "reflective_afest",
        )
        self.assertGreater(trainer_score, admin_score)
        self.assertGreaterEqual(trainer_score - admin_score, TRAINER_ORIGIN_BOOST)

    def test_reliability_ordering_for_trainer_docs(self):
        scores = []
        for level in ("1", "2", "3", "4"):
            boost, _ = score_document_meta_boost(
                {"origin": "trainer", "trainer_reliability": level, "conversation_role": "other"},
                "reflective_afest",
            )
            scores.append((level, boost))
        self.assertEqual([level for level, _ in scores], ["1", "2", "3", "4"])
        self.assertTrue(scores[0][1] < scores[1][1] < scores[2][1] < scores[3][1])
        self.assertEqual(
            scores[3][1] - scores[0][1],
            RELIABILITY_SCORE_BOOST["4"] - RELIABILITY_SCORE_BOOST["1"],
        )


class TrainerOriginRagIntegrationTests(TestCase):
    def setUp(self):
        self.organisation = Organisation.objects.create(name="Org Origin RAG")
        self.group = Group.objects.create(organisation=self.organisation, name="G Origin")

    def _decision(self):
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

    def test_trainer_doc_wins_over_admin_when_rag_active(self):
        trainer_doc = Document.objects.create(
            organisation=self.organisation,
            title="Poly formateur",
            meta={
                "origin": "trainer",
                "trainer_reliability": "4",
                "conversation_role": "support",
                "visibility": "learner_citable",
            },
        )
        admin_doc = Document.objects.create(
            organisation=self.organisation,
            title="Poly admin",
            meta={
                "origin": "admin",
                "conversation_role": "reference_course",
                "visibility": "learner_citable",
            },
        )
        for doc in (trainer_doc, admin_doc):
            GroupDocument.objects.create(
                organisation=self.organisation,
                group=self.group,
                document=doc,
                status=GroupDocument.Status.ACTIVE,
            )
            DocumentChunk.objects.create(
                document=doc,
                content=COMMON_CHUNK_TEXT,
                meta={"document_meta": dict(doc.meta or {})},
            )

        session = SimpleNamespace(organisation_id=self.organisation.id, group_id=self.group.id)
        selections = select_rag_chunks(
            session=session,
            learner_text="procedure tableau electrique consignation verification norme nf",
            teaching_plan=rag_teaching_plan(),
            turn_state=rag_turn_state(),
            conversation_decision=self._decision(),
            limit=5,
        )
        self.assertTrue(selections)
        self.assertEqual(selections[0].document_id, str(trainer_doc.id))
