"""Tests: document source_text, indexation chunks, liaison groupe, RAG Hugo."""
from types import SimpleNamespace

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role, User
from apps.hugo.services.rag_support import select_rag_chunks
from apps.hugo.domain.schemas import TurnState, ConversationDecision
from apps.library.models import Document, DocumentChunk
from apps.referentials.models import Group, GroupMembership, TutorLearnerLink


def _turn_state(**kwargs):
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
    }
    defaults.update(kwargs)
    return TurnState(**defaults)


def _decision():
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


class LibraryIngestionIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.organisation = Organisation.objects.create(name="Org Lib")
        self.group = Group.objects.create(organisation=self.organisation, name="G Lib")
        self.admin = User.objects.create_user(
            username="orgadmin_lib",
            password="pass",
            organisation=self.organisation,
            role=Role.ORGADMIN,
        )

    def test_create_index_link_and_rag_selects_chunks(self):
        self.client.force_authenticate(user=self.admin)
        create_url = reverse("document_list_create")
        r = self.client.post(
            create_url,
            {"title": "Tableau electrique", "source_text": "procedure tableau schéma unifilaire circuits prises eclairage verification avant mise sous tension " * 5},
            format="json",
        )
        self.assertEqual(r.status_code, 201, r.content)
        doc_id = r.data["id"]

        index_url = reverse("document_index", kwargs={"document_id": doc_id})
        r2 = self.client.post(index_url, {}, format="json")
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.data["quality_flag"], "OK")
        self.assertGreater(r2.data["chunks_count"], 0)

        doc = Document.objects.get(id=doc_id)
        self.assertEqual(DocumentChunk.objects.filter(document=doc).count(), doc.chunks_count)

        lib_url = reverse("group_library", kwargs={"group_id": self.group.id})
        r3 = self.client.post(lib_url, {"document_id": doc_id}, format="json")
        self.assertEqual(r3.status_code, 201)
        self.assertEqual(r3.data["document_title"], "Tableau electrique")

        session = SimpleNamespace(
            organisation_id=self.organisation.id,
            group_id=self.group.id,
        )
        learner_text = "je dois verifier le tableau electrique avant la mise sous tension procedure"
        tp = SimpleNamespace(rag_mode="supporting")
        selections = select_rag_chunks(
            session=session,
            learner_text=learner_text,
            teaching_plan=tp,
            turn_state=_turn_state(),
            conversation_decision=_decision(),
            limit=5,
        )
        self.assertTrue(len(selections) > 0)
        self.assertEqual(selections[0].document_id, str(doc_id))

    def test_index_clears_previous_chunks_on_reindex(self):
        self.client.force_authenticate(user=self.admin)
        doc = Document.objects.create(
            organisation=self.organisation,
            title="Reindex",
            source_text="aaa " * 200,
        )
        DocumentChunk.objects.create(document=doc, content="old", meta={})
        self.assertEqual(doc.chunks.count(), 1)

        index_url = reverse("document_index", kwargs={"document_id": doc.id})
        r = self.client.post(index_url, {}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertGreater(r.data["chunks_count"], 0)
        contents = list(DocumentChunk.objects.filter(document=doc).values_list("content", flat=True))
        self.assertFalse(any(c == "old" for c in contents))

    def test_learner_cannot_create_document(self):
        learner = User.objects.create_user(
            username="learner_lib",
            password="pass",
            organisation=self.organisation,
            role=Role.LEARNER,
        )
        self.client.force_authenticate(user=learner)
        r = self.client.post(reverse("document_list_create"), {"title": "X", "source_text": "y"}, format="json")
        self.assertEqual(r.status_code, 403)

    def test_learner_without_group_access_cannot_read_library(self):
        learner = User.objects.create_user(
            username="learner_lib_iso",
            password="pass",
            organisation=self.organisation,
            role=Role.LEARNER,
        )
        self.client.force_authenticate(user=learner)
        lib_url = reverse("group_library", kwargs={"group_id": self.group.id})
        r = self.client.get(lib_url)
        self.assertEqual(r.status_code, 403)

    def test_tutor_via_link_can_list_and_read_linked_documents(self):
        self.client.force_authenticate(user=self.admin)
        create_url = reverse("document_list_create")
        r = self.client.post(
            create_url,
            {"title": "Doc tuteur", "source_text": "Texte pour le tuteur."},
            format="json",
        )
        self.assertEqual(r.status_code, 201)
        doc_id = r.data["id"]
        lib_url = reverse("group_library", kwargs={"group_id": self.group.id})
        self.client.post(lib_url, {"document_id": doc_id}, format="json")

        tutor = User.objects.create_user(
            username="tutor_lib",
            password="pass",
            organisation=self.organisation,
            role=Role.TUTOR,
        )
        learner_u = User.objects.create_user(
            username="learner_for_tutor",
            password="pass",
            organisation=self.organisation,
            role=Role.LEARNER,
        )
        TutorLearnerLink.objects.create(
            organisation=self.organisation,
            group=self.group,
            tutor=tutor,
            learner=learner_u,
        )
        self.client.force_authenticate(user=tutor)
        r_list = self.client.get(lib_url)
        self.assertEqual(r_list.status_code, 200)
        items = r_list.data.get("items") or []
        self.assertEqual(len(items), 1)
        content_url = reverse(
            "group_library_document_content",
            kwargs={"group_id": self.group.id, "document_id": doc_id},
        )
        r_content = self.client.get(content_url)
        self.assertEqual(r_content.status_code, 200)
        self.assertIn("Texte pour le tuteur", r_content.data["source_text"])

    def test_trainer_can_create_document_without_being_group_member(self):
        trainer = User.objects.create_user(
            username="trainer_lib",
            password="pass",
            organisation=self.organisation,
            role=Role.TRAINER,
        )
        self.client.force_authenticate(user=trainer)
        r = self.client.post(
            reverse("document_list_create"),
            {"title": "Doc formateur", "source_text": "contenu"},
            format="json",
        )
        self.assertEqual(r.status_code, 201, r.content)

    def test_learner_can_list_and_read_linked_documents(self):
        self.client.force_authenticate(user=self.admin)
        create_url = reverse("document_list_create")
        r = self.client.post(
            create_url,
            {"title": "Doc visible", "source_text": "Contenu markdown ou texte pour l’apprenant."},
            format="json",
        )
        self.assertEqual(r.status_code, 201)
        doc_id = r.data["id"]
        lib_url = reverse("group_library", kwargs={"group_id": self.group.id})
        r_link = self.client.post(lib_url, {"document_id": doc_id}, format="json")
        self.assertEqual(r_link.status_code, 201)

        learner = User.objects.create_user(
            username="learner_lib_read",
            password="pass",
            organisation=self.organisation,
            role=Role.LEARNER,
        )
        GroupMembership.objects.create(
            organisation=self.organisation,
            group=self.group,
            user=learner,
        )
        self.client.force_authenticate(user=learner)
        r_list = self.client.get(lib_url)
        self.assertEqual(r_list.status_code, 200)
        items = r_list.data.get("items") or []
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["document_id"], doc_id)

        content_url = reverse(
            "group_library_document_content",
            kwargs={"group_id": self.group.id, "document_id": doc_id},
        )
        r_content = self.client.get(content_url)
        self.assertEqual(r_content.status_code, 200)
        self.assertEqual(r_content.data["title"], "Doc visible")
        self.assertIn("Contenu markdown", r_content.data["source_text"])
