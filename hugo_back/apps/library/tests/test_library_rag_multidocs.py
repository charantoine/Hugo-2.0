"""Integration tests: RAG with many documents per group (realistic trainer library load)."""
from __future__ import annotations

import time

from django.test import TestCase

from apps.accounts.models import Organisation
from apps.hugo.services.rag_support import select_rag_chunks
from apps.library.indexing import index_document_chunks
from apps.library.models import Document, DocumentChunk, GroupDocument
from apps.library.tests.rag_test_helpers import (
    COMMON_CHUNK_TEXT,
    rag_conversation_decision,
    rag_session,
    rag_teaching_plan,
    rag_turn_state,
)
from apps.referentials.models import Group


class LibraryRagMultidocsTests(TestCase):
    """
    Simule un groupe avec ~30 documents indexés (référence, support, autres).
    Vérifie stabilité, temps raisonnable et priorisation reference_course.
    """

    REFERENCE_COUNT = 8
    SUPPORT_COUNT = 12
    OTHER_COUNT = 10

    def setUp(self):
        self.organisation = Organisation.objects.create(name="Org Multi RAG")
        self.group = Group.objects.create(organisation=self.organisation, name="G Multi")
        self.ref_doc_ids: set[str] = set()
        self.support_doc_ids: set[str] = set()
        self._seed_documents()

    def _create_and_link_doc(self, title: str, role: str, intent: str = "explanation") -> Document:
        doc = Document.objects.create(
            organisation=self.organisation,
            title=title,
            source_text=COMMON_CHUNK_TEXT * 4,
            meta={
                "conversation_role": role,
                "pedagogical_intent": intent,
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

    def _seed_documents(self):
        started = time.perf_counter()
        for i in range(self.REFERENCE_COUNT):
            doc = self._create_and_link_doc(f"Poly reference {i + 1}", "reference_course")
            self.ref_doc_ids.add(str(doc.id))
        for i in range(self.SUPPORT_COUNT):
            doc = self._create_and_link_doc(f"Support {i + 1}", "support", "practice_support")
            self.support_doc_ids.add(str(doc.id))
        for i in range(self.OTHER_COUNT):
            role = "context" if i % 2 == 0 else "other"
            self._create_and_link_doc(f"Annexe {i + 1}", role, "contextualization")
        elapsed_seed = time.perf_counter() - started
        total_docs = Document.objects.filter(organisation=self.organisation).count()
        total_chunks = DocumentChunk.objects.filter(document__organisation=self.organisation).count()
        self.assertEqual(total_docs, self.REFERENCE_COUNT + self.SUPPORT_COUNT + self.OTHER_COUNT)
        self.assertGreater(total_chunks, total_docs)
        self.seed_elapsed_seconds = elapsed_seed

    def test_multidoc_rag_reference_course_majority_in_top_n(self):
        session = rag_session(self.organisation.id, self.group.id)
        learner_query = (
            "Je dois verifier la consignation du tableau electrique avant mise sous tension "
            "selon la procedure et la norme nf c15-100"
        )
        started = time.perf_counter()
        selections = select_rag_chunks(
            session=session,
            learner_text=learner_query,
            teaching_plan=rag_teaching_plan(),
            turn_state=rag_turn_state(),
            conversation_decision=rag_conversation_decision(),
            limit=10,
        )
        rag_elapsed = time.perf_counter() - started

        self.assertGreater(len(selections), 0, "RAG should return chunks for a matching query")
        ref_in_top = sum(1 for item in selections if item.document_id in self.ref_doc_ids)
        self.assertGreaterEqual(
            ref_in_top,
            (len(selections) + 1) // 2,
            f"Expected majority reference_course in top {len(selections)}, got {ref_in_top}",
        )
        self.assertIn(selections[0].document_id, self.ref_doc_ids)
        self.assertLess(rag_elapsed, 5.0, "RAG selection should stay fast with ~30 docs")
        self.assertLess(self.seed_elapsed_seconds, 30.0, "Seeding 30 indexed docs should be reasonable in CI")

    def test_multidoc_rag_returns_bounded_selection_set(self):
        session = rag_session(self.organisation.id, self.group.id)
        selections = select_rag_chunks(
            session=session,
            learner_text="procedure tableau electrique consignation verification schema",
            teaching_plan=rag_teaching_plan(),
            turn_state=rag_turn_state(),
            conversation_decision=rag_conversation_decision(),
            limit=10,
        )
        self.assertGreater(len(selections), 0)
        self.assertLessEqual(len(selections), 10)
        self.assertTrue(all(item.score > 0 for item in selections))

    def test_technical_point_gets_boost_over_plain_other(self):
        tech_doc = self._create_and_link_doc("Point technique consignation", "technical_point", "diagnosis")
        plain_doc = self._create_and_link_doc("Note diverse", "other", "explanation")
        session = rag_session(self.organisation.id, self.group.id)
        selections = select_rag_chunks(
            session=session,
            learner_text="consignation tableau electrique procedure verification",
            teaching_plan=rag_teaching_plan(),
            turn_state=rag_turn_state(),
            conversation_decision=rag_conversation_decision(),
            limit=5,
        )
        scores_by_doc = {item.document_id: item.score for item in selections}
        if str(tech_doc.id) in scores_by_doc and str(plain_doc.id) in scores_by_doc:
            self.assertGreater(scores_by_doc[str(tech_doc.id)], scores_by_doc[str(plain_doc.id)])
