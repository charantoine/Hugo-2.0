"""Unit tests for Document.meta contract and RAG meta scoring."""
from django.test import SimpleTestCase
from rest_framework.exceptions import ValidationError

from apps.hugo.services.rag_support import score_document, select_rag_chunks
from apps.hugo.domain.schemas import TurnState, ConversationDecision
from apps.library.document_meta import score_document_meta_boost, validate_document_meta
from apps.library.models import Document, DocumentChunk, GroupDocument
from apps.accounts.models import Organisation
from apps.referentials.models import Group
from django.test import TestCase
from types import SimpleNamespace


class DocumentMetaValidationTests(SimpleTestCase):
    def test_valid_meta_defaults(self):
        meta = validate_document_meta({})
        self.assertEqual(meta["conversation_role"], "other")
        self.assertEqual(meta["pedagogical_intent"], "explanation")
        self.assertEqual(meta["visibility"], "learner_citable")
        self.assertEqual(meta["trainer_reliability"], "3")

    def test_valid_meta_full(self):
        meta = validate_document_meta(
            {
                "conversation_role": "reference_course",
                "pedagogical_intent": "diagnosis",
                "visibility": "internal_only",
                "trainer_priority": "high",
            }
        )
        self.assertEqual(meta["conversation_role"], "reference_course")

    def test_invalid_conversation_role_raises(self):
        with self.assertRaises(ValidationError):
            validate_document_meta({"conversation_role": "invalid_role"})


class DocumentMetaScoringTests(SimpleTestCase):
    def test_reference_course_outranks_support(self):
        base = 2.0
        ref = score_document({"conversation_role": "reference_course"}, base)
        support = score_document({"conversation_role": "support"}, base)
        plain = score_document({}, base)
        self.assertGreater(ref, support)
        self.assertGreater(support, plain)

    def test_score_document_meta_boost_ordering(self):
        scores = []
        for role in ("reference_course", "support", "other"):
            boost, _ = score_document_meta_boost({"conversation_role": role}, "reflective_afest")
            scores.append((role, boost))
        self.assertEqual([r for r, _ in scores], ["reference_course", "support", "other"])
        self.assertTrue(scores[0][1] > scores[1][1] > scores[2][1])


class RagReferenceCourseIntegrationTests(TestCase):
    def setUp(self):
        self.organisation = Organisation.objects.create(name="Org Meta RAG")
        self.group = Group.objects.create(organisation=self.organisation, name="G Meta")

    def _turn_state(self, **kwargs):
        defaults = {
            "episode_clarity": "medium",
            "has_concrete_actions": True,
            "problem_salience": "high",
            "reflection_phase": "analysis",
            "reflective_depth": "medium",
            "self_efficacy_signal": "neutral",
            "affect_valence": "neutral",
            "cognitive_load": "medium",
            "interaction_risk": "low",
            "epistemic_balance": "balanced",
            "zpd_estimate": "in",
            "session_phase": "exploration",
            "session_maturity": "early",
            "evidence_strength": "medium",
            "intervention_necessity": "low",
            "contradiction_status": "none",
            "concept_clarity": "medium",
            "available_material": "high",
            "conversation_goal": "progress",
            "current_phase": "exploration",
            "emotional_state": "neutral",
            "action_feasibility": "medium",
            "autonomy_level": "medium",
            "recent_progress": "steady",
            "need_recap": False,
            "need_encouragement": False,
            "need_reframing": False,
            "can_close_for_now": False,
            "safety_or_quality_risk_level": "high",
        }
        defaults.update(kwargs)
        return TurnState(**defaults)

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

    def test_reference_course_chunks_rank_first(self):
        shared = "procedure tableau electrique verification mise sous tension schéma "
        ref_doc = Document.objects.create(
            organisation=self.organisation,
            title="Cours référence",
            source_text=shared * 3,
            meta={
                "conversation_role": "reference_course",
                "visibility": "learner_citable",
                "origin": "trainer",
                "trainer_reliability": "4",
            },
        )
        support_doc = Document.objects.create(
            organisation=self.organisation,
            title="Support",
            source_text=shared * 3,
            meta={"conversation_role": "support", "visibility": "learner_citable"},
        )
        for doc in (ref_doc, support_doc):
            GroupDocument.objects.create(
                organisation=self.organisation,
                group=self.group,
                document=doc,
                status=GroupDocument.Status.ACTIVE,
            )
            DocumentChunk.objects.create(
                document=doc,
                content=shared,
                meta={"document_meta": dict(doc.meta or {})},
            )

        session = SimpleNamespace(organisation_id=self.organisation.id, group_id=self.group.id)
        selections = select_rag_chunks(
            session=session,
            learner_text="je dois verifier le tableau electrique procedure mise sous tension",
            teaching_plan=SimpleNamespace(rag_mode="supporting", focus_competence={}),
            turn_state=self._turn_state(safety_or_quality_risk_level="high"),
            conversation_decision=self._decision(),
            limit=3,
        )
        self.assertTrue(selections)
        self.assertEqual(selections[0].document_id, str(ref_doc.id))
